# -*- coding: utf-8 -*-
import sys
from django.conf import settings
from sqlalchemy import create_engine
from pandas import read_sql
import json
from datetime import datetime as dt

from .utilities import process_data
from .tracking import Tracking
from ..models import LastVersion, MovTypes, FileMovements

pData = process_data('validacionDeCifras')

# FUNCIÓN PRINCIPAL
def validacionDeCifras(filesLoad):
    track = Tracking(filesLoad, pData['steps'], '6')
    try:
        resultados = {}
        carga = Validacion(filesLoad)

        # OBTENCIÓN DE MOVIMIENTOS
        resultados['cifras'] = carga.getCifras()
        if not resultados['cifras']['valid']:
            data = {'status': 'Error de validación', 'statusDesc': json.dumps(resultados['cifras']['errors'])}
            track.save_step(error=True, errorData=data)
            return resultados['cifras']
        track.save_step(stepNumber='7')

        # VALIDACIÓN DE CIFRAS
        resultados['validaCifras'] = carga.validaCifras()
        if not resultados['validaCifras']['valid']:
            data = {'status': 'Error de validaCifras', 'statusDesc': json.dumps(resultados['validaCifras']['errors'])}
            track.save_step(error=True, errorData=data)
            return resultados['validaCifras']
        track.save_step(stepNumber='8')
        
        # VALIDACIÓN DE VERSIÓN
        resultados['validaVersion'] = carga.validaCifras()
        if not resultados['validaVersion']['valid']:
            data = {'status': 'Error de validaVersion', 'statusDesc': json.dumps(resultados['validaVersion']['errors'])}
            track.save_step(error=True, errorData=data)
            return resultados['validaVersion']
        track.save_step(stepNumber='9', lastTrack=True)

        return {'valid': True, 'errors': [], 'cifras': carga.cifras}
    except: # GUARDA LA EXCEPCIÓN
        data = {'status': 'Falló la validación', 'statusDesc': f'{sys.exc_info()[0]}'}
        track.save_step(error=True, errorData=data)
        return {'valid': False, 'errors': [f'Falló la validación: {sys.exc_info()[0]}']}

# OBJETO DE VALIDACIONES
class Validacion(object):
    def __init__(self, load):
        self.load = load
        self.loadType = load.filesType
        self.lastVersion = LastVersion.objects.get(filesType = self.loadType)
        self.movsCat = MovTypes.objects.filter(filesType=self.loadType)
        self.cifras = {
            'cat': {'moves':{'totalAltas': 0, 'totalBajas': 0}},
            'act': {'moves':{'totalAltas': 0, 'totalBajas': 0}},
            'eqv': {'moves':{'totalAltas': 0, 'totalBajas': 0}}
        }
        self.checkFirstLoad()
        self.readTemp()
        self.getCgo()

    def checkFirstLoad(self):
        self.firstLoad = True
        if self.lastVersion.filesVersion.year >= 2000:
            self.firstLoad = False

    def getCgo(self):
        self.cgoField = 'CGO_ACT'
        if self.loadType == 'entidades':
            self.cgoField = 'COD_ACT'

    def readTemp(self):
        self.dfs = {}
        engine = create_engine(f'postgresql://{settings.TEMP_FILES_USER}:{settings.TEMP_FILES_PASS}@{settings.TEMP_FILES_HOST}:{settings.TEMP_FILES_PORT}/{settings.TEMP_FILES_DBNAME}')
        self.dfs['cat'] = read_sql(f'select * from {self.load.catTable}', engine)
        self.dfs['act'] = read_sql(f'select * from {self.load.actTable}', engine)
        self.dfs['eqv'] = read_sql(f'select * from {self.load.eqvTable}', engine)

    def getCifras(self):
        errors = []
        try:
            # NÚMERO DE REGISTROS POR ARCHIVO
            self.cifras['cat']['numRecs'] = self.dfs['cat'].shape[0]
            self.cifras['act']['numRecs'] = self.dfs['act'].shape[0]
            self.cifras['eqv']['numRecs'] = self.dfs['eqv'].shape[0]
            # MOVIMIENTOS POR CGO_ACT
            self.cifras['act']['moves']['all'] = self.dfs['act'].groupby(self.cgoField)[[self.cgoField]].count().to_dict()[self.cgoField]
            self.cifras['eqv']['moves']['all'] = self.dfs['eqv'].groupby(self.cgoField)[[self.cgoField]].count().to_dict()[self.cgoField]
            # OBTENCIÓN DE ALTAS Y BAJAS TOTALES
            for tipo in ['act','eqv']:
                for cgo in self.cifras[tipo]['moves']['all'].keys():
                    movType = self.movsCat.get(cgo_act=cgo)
                    numMovs = self.cifras[tipo]['moves']['all'][cgo]
                    if movType.move_type == 'alta':
                        self.cifras[tipo]['moves']['totalAltas'] += numMovs
                    elif movType.move_type == 'baja':
                        self.cifras[tipo]['moves']['totalBajas'] += numMovs
                    elif movType.move_type == 'ambas':
                        self.cifras[tipo]['moves']['totalAltas'] += numMovs
                        self.cifras[tipo]['moves']['totalBajas'] += numMovs
                    # GUARDA MOVIMIENTOS EN FileMovements
                    if tipo == 'act':
                        FileMovements.objects.create(UploadFiles=self.load, cgo_act=cgo, descgo_act=movType.descgo_act, mov_cant=numMovs, move_type=movType.move_type)
            # GUARDA ALTAS TOTALES EN FileMovements
            FileMovements.objects.create(UploadFiles=self.load, cgo_act='AT', descgo_act='ALTAS TOTALES', mov_cant=self.cifras['act']['moves']['totalAltas'], move_type='alta')
            # GUARDA BAJAS TOTALES EN FileMovements
            FileMovements.objects.create(UploadFiles=self.load, cgo_act='BT', descgo_act='BAJAS TOTALES', mov_cant=self.cifras['act']['moves']['totalBajas'], move_type='baja')

            if not self.firstLoad: # TODO: Desarrollar la parte donde lee del catalogo vigente y compara los movimientos con el nuevo para sacar bajas y altas totales
                    # self.cifras['cat']['moves']['totalAltas'] = numMovs
                    # self.cifras['cat']['moves']['totalBajas'] = numMovs
                pass
        except:
            errors.append('error al obtener los movimientos')
        if errors:
            return {'valid': False, 'errors': errors, 'status': 'error al leer los movimientos'}
        return {'valid': True, 'errors': errors, 'status': 'lectura de movimientos correcta'}

    def validaCifras(self):
        errors = []
        if not self.firstLoad:
            # COMPARA TAB EQUIV VS REG ACT
            if self.cifras['act']['moves']['totalAltas'] != self.cifras['eqv']['moves']['totalAltas'] and self.cifras['act']['moves']['totalBajas'] != self.cifras['eqv']['moves']['totalBajas']:
                errors.append(pData['errors']['actVSeqv'])
            if self.cifras['act']['moves']['totalAltas'] != self.cifras['cat']['moves']['totalAltas'] and self.cifras['act']['moves']['totalBajas'] != self.cifras['cat']['moves']['totalBajas']:
                errors.append(pData['errors']['actVScat'])
        if errors:
            return {'valid': False, 'errors': errors, 'status': 'error en validación de cifras'}
        return {'valid': True, 'errors': errors, 'status': 'cifras ok'}
    
    def validaVersion(self):
        errors = []
        try:
            # VALIDA VERSIÓN DADA POR EL USUARIO VS LASTVERSION EN DB QUE SEA SUPERIOR
            if self.load.filesVersion.year < self.lastVersion.filesVersion.year or (self.load.filesVersion.year == self.lastVersion.filesVersion.year and self.load.filesVersion.month < self.lastVersion.filesVersion.month):
                errors.append(f"{pData['errors']['lastVersion']} {self.load.filesVersion.isoformat()}")
            # VALIDA COINCIDENCIA DE FECHAS EN REG ACT CON LO INDICADO EN INPUT
            fechas = self.dfs['act'].groupby('FECHA_ACT')[['FECHA_ACT']].count().index.to_list()
            for fecha in fechas:
                fechaArchivos = dt.strptime(fecha, '%Y-%m-%d').date()
                filesVersion = self.load.filesVersion
                if fechaArchivos.year != filesVersion.year or fechaArchivos.month != filesVersion.month:
                    errors.append(f"{ pData['errors']['actVersion'] } {fecha}")
            # VALIDA COINCIDENCIA DE FECHAS EN REG ACT CON LO INDICADO EN INPUT, EXCEPTO EN PRIMERA CARGA
            if not self.firstLoad:
                fechas = self.dfs['eqv'].groupby('FECHA_ACT')[['FECHA_ACT']].count().index.to_list()
                for fecha in fechas:
                    fechaArchivos = dt.strptime(fecha, '%Y-%m-%d').date()
                    filesVersion = self.load.filesVersion
                    if fechaArchivos.year != filesVersion.year or fechaArchivos.month != filesVersion.month:
                        errors.append(f"{ pData['errors']['eqvVersion'] } {fecha}")
        except:
            errors.append('error al validar los movimientos')
        if errors:
            return {'valid': False, 'errors': errors, 'status': 'error en validación de versión'}
        return {'valid': True, 'errors': errors, 'status': 'versión ok'}