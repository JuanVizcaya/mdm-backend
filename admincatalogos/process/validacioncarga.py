# -*- coding: utf-8 -*-
import sys
from django.conf import settings
from sqlalchemy import create_engine
import pandas as pd
from .utilities import process_data
from .tracking import Tracking
import json

pData = process_data('validacionDeCarga')

def validacionDeCarga(filesLoad):
    track = Tracking(filesLoad, pData['steps'], '2')
    try:
        resultados = {}
        carga = Validacion(filesLoad)

        # VALIDACIÓN DE TIPO
        resultados['tipo'] = carga.tipoArchivos()
        if not resultados['tipo']['valid']:
            data = {'status': 'Error de validación', 'statusDesc': json.dumps(resultados['tipo']['errors'])}
            track.save_step(error=True, errorData=data)
            return resultados['tipo']
        track.save_step(stepNumber='3')

        # VALIDACIÓN DE ESTRUCTURA
        resultados['estructura'] = carga.estructura()
        if not resultados['estructura']['valid']:
            data = {'status': 'Error de estructura', 'statusDesc': json.dumps(resultados['estructura']['errors'])}
            track.save_step(error=True, errorData=data)
            return resultados['estructura']
        track.save_step(stepNumber='4')

        # CREA TABLAS TEMPORALES
        carga.saveTemps()
        track.save_step(stepNumber='5', lastTrack=True)

        return {'valid': True, 'errors': []}
    except: # GUARDA LA EXCEPCIÓN
        data = {'status': 'Falló la validación', 'statusDesc': f'{sys.exc_info()[0]}'}
        track.save_step(error=True, errorData=data)
        return {'valid': False, 'errors': [f'Falló la validación: {sys.exc_info()[0]}']}
        
    
class Validacion(object):
    def __init__(self, load):
        self.load = load
        self.loadType = load.filesType
    
    def tipoArchivos(self):
        errors = []
        self.files = {}
        for tipo ,csv in zip(['cat','eqv','act'], [self.load.catLoad, self.load.eqvLoad, self.load.actLoad]):
            try:
                self.files[tipo] = pd.read_csv(csv, low_memory=False)
            except:
                errors.append(pData[tipo]['readError'])
        if errors:
            return {'valid': False, 'errors': errors, 'status': 'error de tipo de archivo'}
        return {'valid': True, 'errors': errors, 'status': 'tipo de archivos ok'}

    def estructura(self):
        errors = []
        for tipo in ['cat','eqv','act']:
            if self.files[tipo].columns.to_list() != pData[tipo][self.loadType]['fields']:
                errors.append(pData[tipo]['fieldsError'])
        if errors:
            return {'valid': False, 'errors': errors, 'status': 'error de estrctura'}
        return {'valid': True, 'errors': errors, 'status': 'estructura ok'}
    
    def saveTemps(self):
        engine = create_engine(f'postgresql://{settings.TEMP_FILES_USER}:{settings.TEMP_FILES_PASS}@{settings.TEMP_FILES_HOST}:{settings.TEMP_FILES_PORT}/{settings.TEMP_FILES_DBNAME}')
        for tipo in ['cat','eqv','act']:
            # self.files[tipo]['filesId'] = self.load.filesId
            self.files[tipo] = self.files[tipo].rename(columns={ori:act for ori, act in zip(pData[tipo][self.loadType]['fields'], pData[tipo][self.loadType]['newFields'])})
            self.files[tipo].to_sql(f'tmp_{tipo}_{self.load.filesId}',engine,if_exists='replace',index=False, chunksize=10000)
        self.load.catTable = f'tmp_cat_{self.load.filesId}'
        self.load.eqvTable = f'tmp_eqv_{self.load.filesId}'
        self.load.actTable = f'tmp_act_{self.load.filesId}'
        self.load.save()
