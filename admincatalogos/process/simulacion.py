# -*- coding: utf-8 -*-
import sys
from django.conf import settings
from sqlalchemy import create_engine
from pandas import read_sql, isna
import json

from catalogos.models import Tmp_Cat_Entidades
from ..models import MovTypes, LastVersion
from .utilities import process_data
from .tracking import Tracking
from catalogos.processing.fields import toConcatenate, model_fields

pData = process_data('simulacion')

# FUNCIÓN PRINCIPAL
def simulacion(filesLoad):
    track = Tracking(filesLoad, pData['steps'], '15')
    try:
        resultados = {}
        carga = SIM(filesLoad)

        # OBTENCIÓN DE ALTAS
        track.save_step(stepNumber='16')
        resultados['altas'] = carga.getAltasAndMovs()
        if not resultados['altas']['valid']:
            data = {'status': 'Error en limpieza del catálogo', 'statusDesc': json.dumps(resultados['altas']['errors'])}
            track.save_step(error=True, errorData=data)
            return resultados['altas']
        track.save_step(stepNumber='17', )

        return {'valid': True, 'errors': []}
    except: # GUARDA LA EXCEPCIÓN
        data = {'status': 'Falló la limpieza', 'statusDesc': f'{sys.exc_info()[0]}'}
        track.save_step(error=True, errorData=data)
        return {'valid': False, 'errors': [f'Falló la limpieza: {sys.exc_info()[0]}']}


fieldsByType = {
    'entidades': ['nom_ent', 'abr_ent', 'p_total', 'v_total', 'p_mas', 'p_fem', 'cgo_act', 'descgo_act'],
    'municipios': [],
    'localidades': []
    }

# OBJETO DE SIMULACIÓN
class SIM(object):
    def __init__(self, load):
        self.load = load
        self.loadType = load.filesType
        self.movsCat = MovTypes.objects.filter(filesType=self.loadType)
        self.moves = {}
        self.lastVersion = LastVersion.objects.get(filesType = self.loadType)
        self.cve_ag = {'entidades':'cve_ent','municipios':'cve_munc','localidades':'cve_locc'}[self.loadType]
        self.engine = create_engine(f'postgresql://{settings.TEMP_FILES_USER}:{settings.TEMP_FILES_PASS}@{settings.TEMP_FILES_HOST}:{settings.TEMP_FILES_PORT}/{settings.TEMP_FILES_DBNAME}')
        self.readTemp()
        self.getCatActual()
        self.checkFirstLoad()
        
    def checkFirstLoad(self):
        self.firstLoad = True
        if self.lastVersion.filesVersion.year >= 2000:
            self.firstLoad = False

    def readTemp(self):
        self.dfs = {}
        self.dfs['cat'] = read_sql(f'select * from {self.load.catTable} where "filesId"=\'{self.load.filesId}\'', self.engine)
        self.dfs['act'] = read_sql(f'select * from {self.load.actTable} where "filesId"=\'{self.load.filesId}\'', self.engine)
        self.dfs['eqv'] = read_sql(f'select * from {self.load.eqvTable} where "filesId"=\'{self.load.filesId}\'', self.engine)
        self.keepFields = self.dfs['cat'].columns.values.tolist()

    def getCatActual(self):
        self.catActual = read_sql(f'select * from catalogos_cat_{self.loadType} where es_activa is true', self.engine)

    def getAltasAndMovs(self):
        errors = []
        # try:

        join = self.dfs['cat'].join(self.catActual.set_index(self.cve_ag), on=self.cve_ag, rsuffix='_')
        filtCgoNa = isna(join['cgo_act'])
        altas = join[filtCgoNa][self.keepFields]
        altas['nuevo_reg'] = True
        self.moves['altas'] = altas

        # OBTIENE MOVIMIENTOS TODO: Revisar en segunda carga
        for field in [f for f in self.keepFields if not f in (self.cve_ag, 'filesId')]:
            filt = (not filtCgoNa and join[field] != join[f'{field}_'])
            moves = join[filt][self.keepFields]
            moves['nuevo_reg'] = False
            self.moves[field] = moves

        # except:
        #     errors.append('error al obtener los movimientos')
        if errors:
            return {'valid': False, 'errors': errors, 'status': 'en la obtención de altas'}
        return {'valid': True, 'errors': errors, 'status': 'Obtención de altas correcta'}

    def getBajas(self):
        errors = []
        # try:
        join = self.catActual.join(self.dfs['cat'].set_index(self.cve_ag), on=self.cve_ag, rsuffix='_')
        # OBTIENE BAJAS
        filt = isna(join['p_total'])
        bajas = join[filt][self.keepFields]
        bajas['nuevo_reg'] = False
        self.moves['bajas'] = bajas

        # except:
        #     errors.append('error al obtener los movimientos')
        if errors:
            return {'valid': False, 'errors': errors, 'status': 'en la obtención de bajas'}
        return {'valid': True, 'errors': errors, 'status': 'Obtención de bajas correcta'}
    
    def setMoves(self):
        if self.loadType == 'entidades':
            newMoves = self.getNewMoves(cgo_alta=('*', 'U'), cgo_baja=('P',))
        elif self.loadType == 'municipios':
            newMoves = self.getNewMoves(cgo_alta=('*', 'M'), cgo_baja=('P',))
        elif self.loadType == 'localidades':
            newMoves = self.getNewMoves(cgo_alta=('*', 'B'), cgo_baja=('T', 'R', 'C'))
    
    def getNewMoves(self, cgo_alta, cgo_baja):
        for idx, row in self.dfs['act'].iterrows():
            newMove = {}
            thisMoveType = self.movsCat.get(cgo_act=row['cgo_act'])
            ownFields = fieldsByType[self.loadType]
            # CASO ALTAS
            if thisMoveType.cgo_act in cgo_alta:
                recInCat = self.dfs['cat'].loc[self.dfs['cat'][self.cve_ag] == row[self.cve_ag]]
                if len(recInCat) == 0:
                    raise f"Error, no existe {row[self.cve_ag]} en catalogo"
                elif len(recInCat) == 1:
                    recInCat = recInCat.to_dict('records')[0]
                    
                    for field in ownFields:
                        newMove[field] = recInCat[field]
                    newMove['carga'] = self.load
                    newMove['snap_id'] = 1
                    newMove['nuevo_reg'] = True
                    newMove['fecha_act'] = row['fecha_act']
                    newMove['es_activa'] = True
                    newMove['mov_inegi'] = True
                    newMove[self.cve_ag] = recInCat[self.cve_ag]
                    
                    newMove['cgo_act'] = thisMoveType.cgo_act
                    newMove['descgo_act'] = thisMoveType.descgo_act
                else:
                    raise f"Error, existe más de un registro con {row[self.cve_ag]} en catalogo"
