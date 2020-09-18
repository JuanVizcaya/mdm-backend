# -*- coding: utf-8 -*-
import sys
from django.conf import settings
from sqlalchemy import create_engine
from pandas import read_sql
from pandas.io import sql
import json

from ..models import LastVersion, MovTypes, FileMovements
from .utilities import process_data
from .tracking import Tracking
from catalogos.processing.fields import toConcatenate, model_fields

pData = process_data('DQ')

# FUNCIÓN PRINCIPAL
def dq(filesLoad):
    track = Tracking(filesLoad, pData['steps'], '10')
    try:
        resultados = {}
        carga = DQ(filesLoad)

        # LIMPIEZA DE CATÁLOGO
        resultados['cat'] = carga.cleanFile('cat')
        if not resultados['cat']['valid']:
            data = {'status': 'Error en limpieza del catálogo', 'statusDesc': json.dumps(resultados['cat']['errors'])}
            track.save_step(error=True, errorData=data)
            return resultados['cat']
        track.save_step(stepNumber='11')

        # LIMPIEZA DE REGISTRO DE ACTUALIZACIÓN
        resultados['act'] = carga.cleanFile('act')
        if not resultados['act']['valid']:
            data = {'status': 'Error en limpieza del registro de actualización', 'statusDesc': json.dumps(resultados['act']['errors'])}
            track.save_step(error=True, errorData=data)
            return resultados['act']
        track.save_step(stepNumber='12')

        # LIMPIEZA DE TABLA DE EQUIVALENCIAS
        resultados['eqv'] = carga.cleanFile('eqv')
        if not resultados['eqv']['valid']:
            data = {'status': 'Error en limpieza de la tabla de equivalencias', 'statusDesc': json.dumps(resultados['eqv']['errors'])}
            track.save_step(error=True, errorData=data)
            return resultados['eqv']
        track.save_step(stepNumber='13')
        
        # GUARDA EN TABLAS TEMPORALES
        resultados['saveTemp'] = carga.saveTemps()
        if not resultados['saveTemp']['valid']:
            data = {'status': 'Error al guardar en tablas temporales', 'statusDesc': json.dumps(resultados['saveTemp']['errors'])}
            track.save_step(error=True, errorData=data)
            return resultados['saveTemp']
        track.save_step(stepNumber='14', lastTrack=True)

        return {'valid': True, 'errors': []}
    except: # GUARDA LA EXCEPCIÓN
        data = {'status': 'Falló la limpieza', 'statusDesc': f'{sys.exc_info()[0]}'}
        track.save_step(error=True, errorData=data)
        return {'valid': False, 'errors': [f'Falló la limpieza: {sys.exc_info()[0]}']}

# OBJETO DE VALIDACIONES
class DQ(object):
    def __init__(self, load):
        self.load = load
        self.loadType = load.filesType
        self.readTemp()

    def readTemp(self):
        self.dfs = {}
        engine = create_engine(f'postgresql://{settings.TEMP_FILES_USER}:{settings.TEMP_FILES_PASS}@{settings.TEMP_FILES_HOST}:{settings.TEMP_FILES_PORT}/{settings.TEMP_FILES_DBNAME}')
        self.dfs['cat'] = read_sql(f'select * from {self.load.catTable}', engine)
        self.dfs['act'] = read_sql(f'select * from {self.load.actTable}', engine)
        self.dfs['eqv'] = read_sql(f'select * from {self.load.eqvTable}', engine)

    def cleanFile(self, tipo):
        errors = []
        try:
            for column in self.dfs[tipo].columns.tolist():
                for rule in model_fields[column]['rules']:
                    if rule.__name__ == 'concatenate':
                        self.dfs[tipo][column] = rule(self.dfs[tipo][toConcatenate[column]], self.dfs[tipo][column])
                    elif rule.__name__ == 'delete_field':
                        self.dfs[tipo] = rule(self.dfs[tipo],self.dfs[tipo][column])
                    else:
                        self.dfs[tipo][column] = rule(self.dfs[tipo][column])

        except:
            errors.append('error al obtener los movimientos')
        if errors:
            return {'valid': False, 'errors': errors, 'status': 'en la limpieza del catálogo'}
        return {'valid': True, 'errors': errors, 'status': 'limpieza de catálogo correcta'}

    def saveTemps(self):
        errors = []
        try:
            engine = create_engine(f'postgresql://{settings.TEMP_FILES_USER}:{settings.TEMP_FILES_PASS}@{settings.TEMP_FILES_HOST}:{settings.TEMP_FILES_PORT}/{settings.TEMP_FILES_DBNAME}')
            for tipo in ['cat','eqv','act']:
                self.dfs[tipo]['filesId'] = self.load.filesId
                self.dfs[tipo].to_sql(f'dq_tmp_{self.loadType}_{tipo}',engine,if_exists='append',index=False, chunksize=10000)
            sql.execute(f'DROP TABLE IF EXISTS {self.load.catTable}', engine)
            self.load.catTable = f'dq_tmp_{self.loadType}_cat'
            sql.execute(f'DROP TABLE IF EXISTS {self.load.eqvTable}', engine)
            self.load.eqvTable = f'dq_tmp_{self.loadType}_eqv'
            sql.execute(f'DROP TABLE IF EXISTS {self.load.actTable}', engine)
            self.load.actTable = f'dq_tmp_{self.loadType}_act'
            self.load.save()
        except:
            errors.append('error al guardar en temporales')
        if errors:
            return {'valid': False, 'errors': errors, 'status': 'error al guardar en temporales'}
        return {'valid': True, 'errors': errors, 'status': 'se guardó en temporales'}