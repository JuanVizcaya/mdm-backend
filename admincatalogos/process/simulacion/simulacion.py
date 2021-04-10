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

def valid_step(resultados, track):
    if not resultados['valid']:
        data = {'status': resultados['status'], 
                'statusDesc': json.dumps(resultados['errors'])}
        track.save_step(error=True, errorData=data)
        return False
    return True

def sim_process(filesLoad):
    """ FUNCIÓN PRINCIPAL """
    pData = process_data('simulacion')
    simulator = getSimObject(filesLoad.filesType)
    track = Tracking(filesLoad, pData['steps'], '15')
    # try:
    resultados = {}
    carga = simulator(filesLoad)
    # OBTENCIÓN DE ALTAS Y MOVIMIENTOS
    track.save_step(stepNumber='16')
    resultados['altas'] = carga.getAltasAndMovs()
    if not valid_step(resultados['altas'], track):
        return resultados['altas']
    # OBTENCIÓN DE BAJAS
    track.save_step(stepNumber='17')
    resultados['bajas'] = carga.getBajas()
    if not valid_step(resultados['bajas'], track):
        return resultados['bajas']
    # CREACIÓN DE MOVIMIENTOS INEGI
    track.save_step(stepNumber='18')
    resultados['moves_inegi'] = carga.makeMovesInegi(('*', 'U'), ('P',))
    if not valid_step(resultados['moves_inegi'], track):
        return resultados['moves_inegi']
    # CREACIÓN DE MOVIMIENTOS DAE
    track.save_step(stepNumber='19')
    resultados['moves_dae'] = carga.makeMovesDAE()
    if not valid_step(resultados['moves_dae'], track):
        return resultados['moves_dae']
    # SALVADO DE TODOS LOS MOVIMIENTOS
    track.save_step(stepNumber='20')
    resultados['moves_dae'] = carga.saveNewMoves()
    if not valid_step(resultados['moves_dae'], track):
        return resultados['moves_dae']
    track.save_step(stepNumber='21')

    return {'valid': True, 'errors': []}
    # except: # GUARDA LA EXCEPCIÓN
    #     data = {'status': 'Falló la limpieza', 'statusDesc': f'{sys.exc_info()[0]}'}
    #     track.save_step(error=True, errorData=data)
    #     return {'valid': False, 'errors': [f'Falló la limpieza: {sys.exc_info()[0]}']}
