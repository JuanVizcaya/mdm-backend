# -*- coding: utf-8 -*-
import sys
from django.conf import settings
from sqlalchemy import create_engine
from pandas import read_sql, isna
import json

from ..utilities import process_data
from ..tracking import Tracking
from .entidades import Sim_Ent

__all__ = ['sim_process']

def getSimObject(loadType):
    return {
        'entidades': Sim_Ent,
    }[loadType]

# FUNCIÓN PRINCIPAL
def sim_process(filesLoad):
    pData = process_data('simulacion')
    SIM = getSimObject(filesLoad.filesType)
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
