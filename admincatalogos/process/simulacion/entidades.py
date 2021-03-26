# -*- coding: utf-8 -*-
import sys
from pandas import isna
import json

from catalogos.models import Tmp_Cat_Entidades, Cat_Entidades, Hist_Entidades
from ...models import MovTypes
from catalogos.processing.fields import toConcatenate, model_fields

from .utilities import readTemp, getCatActual, checkFirstLoad

__all__ = ['simulacion']

def getFeatures(loadType):
    return {
        'entidades':
            {
                'cat_model': Cat_Entidades,
                'hist_model': Hist_Entidades,
                'tmp_model': Tmp_Cat_Entidades,
                'cve_ag': 'cve_ent', 'cve_ori': 'cveent_ori', 'cve_act': 'cveent_act',
                'fields': ['nom_ent', 'abr_ent', 'p_total', 'v_total', 'p_mas', 'p_fem'],
                'eqvFields': ['cveent_ori', 'noment_ori', 'cveent_act', 'noment_act', 'fecha_act', 'cgo_act', 'descgo_act', 'filesId'],
                'cgo_alta': ('*', 'U'),
                'cgo_baja': ('P',)
            },
        'municipios':
            {
                'cgo_alta': ('*', 'M'),
                'cgo_baja': ('P',)
            },
        'localidades':
            {
                'cgo_alta': ('*', 'B'),
                'cgo_baja': ('T', 'R', 'C')
            }
    }[loadType]

# OBJETO DE SIMULACIÓN
class Sim_Ent(object):
    def __init__(self, load):
        self.load = load
        self.movsCat = MovTypes.objects.filter(filesType=self.load.filesType)
        self.moves = {}
        self.cve_ag = 'cve_ent'
        self.catFields = ['nom_ent', 'abr_ent', 'p_total', 'v_total', 'p_mas', 'p_fem']
        self.activas = Cat_Entidades.objects.filter(es_activa=True)
        self.dfs, self.keepFields, self.equivs = readTemp(self.load, 'cvent_ori', 'cveent_act')
        self.catActual = getCatActual(self.load.filesType)
        self.firstLoad = checkFirstLoad(self.load.filesType)
        self.newMoves = {'altas': [], 'bajas': [], 'cambios': []}
        self.errors = []

    def getAltasAndMovs(self):
        # try:
        join = self.dfs['cat'].join(self.catActual.set_index(self.cve_ag), on=self.cve_ag, rsuffix='_')
        filtCgoNa = isna(join['cgo_act'])
        altas = join[filtCgoNa][self.keepFields]
        altas['nuevo_reg'] = True
        self.moves['altas'] = {m[self.cve_ag]:m for m in altas.to_dict('records')}

        # OBTIENE MOVIMIENTOS TODO: Revisar en segunda carga
        notNaMoves = join[~filtCgoNa]
        for field in [f for f in self.keepFields if not f in (self.cve_ag, 'filesId')]:
            filt = (join[field] != join[f'{field}_'])
            fieldMoves = notNaMoves[filt][self.keepFields]
            fieldMoves['nuevo_reg'] = False
            fieldMoves['field'] = field
            if not fieldMoves.empty:
                self.moves['cambios'] = {m[self.cve_ag]:m for m in fieldMoves.to_dict('records')}
        # except:
        #     errors.append('error al obtener los movimientos')
        if self.errors:
            return {'valid': False, 'errors': self.errors, 'status': 'en la obtención de altas'}
        return {'valid': True, 'errors': self.errors, 'status': 'Obtención de altas correcta'}

    def getBajas(self):
        # try:
        join = self.catActual.join(self.dfs['cat'].set_index(self.cve_ag), on=self.cve_ag, rsuffix='_')
        # OBTIENE BAJAS
        filt = isna(join['filesId'])
        bajas = join[filt][self.keepFields]
        bajas['nuevo_reg'] = False
        self.moves['bajas'] = {m[cve_ag]:m for m in bajas.to_dict('records')}
        # except:
        #     self.errors.append('error al obtener los movimientos')
        if self.errors:
            return {'valid': False, 'errors': self.errors, 'status': 'en la obtención de bajas'}
        return {'valid': True, 'errors': self.errors, 'status': 'Obtención de bajas correcta'}

    def makeMovesInegi(self, cgos_alta, cgos_baja):
        # try:
        # === MOVIMIENTOS EN REGISTRO DE ACTUALIZACIÓN ===
        for idx, row in self.dfs['act'].iterrows():
            cve_mov = row[self.cve_ag]
            moveType = self.movsCat.get(cgo_act=row['cgo_act'])
            # CASO ALTAS
            if moveType.cgo_act in cgos_alta:
                newMove = self.newAltaInegi(moveType, row)
                self.newMoves['altas'].append(newMove)
            # CASO BAJAS
            elif moveType.cgo_act in cgos_baja:
                newMove = self.newBajaInegi(moveType, row)
                self.newMoves['bajas'].append(newMove)
            # CASO CAMBIOS
            else:
                newMove = self.newMoveInegi(moveType, row)
                self.newMoves['cambios'].append(newMove)
        # except:
        #     self.errors.append('error al crea los movimientos INEGI')
        if self.errors:
            return {'valid': False, 'errors': self.errors, 'status': 'en la creación de movimientos inegi'}
        return {'valid': True, 'errors': self.errors, 'status': 'Creación de movimientos inegi correcta'}
                
    def get_rec_activo(self, cve_mov):
        try:
            recActual = self.activas.objects.get(cve_ent=cve_mov)
        except:
            raise f'No se encontró la clave {cve_mov} en el catálogo actual'
        return recActual

    def newMoveInegi(self, moveType, row):
        cve_mov = row[self.cve_ag]
        newMoveInegi = {}

        recActivo = self.get_rec_activo(cve_mov)

        if not cve_mov in self.moves['cambios'].keys():
            raise f'Error, no se encontro {newMoveInegi[cve_ag]} en los movimientos (cambios).'
        self.moves['cambios'][cve_mov]['hecho'] = True
        # CASO CAMBIO DE NOMBRE
        if moveType.cgo_act == 'W':
            if not cve_mov in self.equivs['ori'].keys():
                raise f'No se encontró la clave {cve_mov} en la tabla de equivalencias'
            rowEqv = self.equivs['ori'][cve_mov]
            newMoveInegi['es_activa'] = True
            newMoveInegi[self.cve_ag] = recActivo[self.cve_ag] #FIXME: No sé si aplica
            newMoveInegi['nom_ent'] = rowEqv['noment_act']
            newMoveInegi['abr_ent'] = row['abr_ent']
            newMoveInegi['p_total'] = row['p_total']
        
        newMoveInegi['carga'] = self.load
        newMoveInegi['ent'] = recActivo
        newMoveInegi['snap_id'] = recActivo.snap_id + 1
        newMoveInegi['nuevo_reg'] = False
        newMoveInegi['fecha_act'] = row['fecha_act']
        newMoveInegi['mov_inegi'] = True
        newMoveInegi['cgo_act'] = moveType.cgo_act
        newMoveInegi['descgo_act'] = moveType.descgo_act

    # TODO: Revisar correcto funcionamiento en 2da carga
    def newBajaInegi(self, moveType, row):
        cve_mov = row[self.cve_ag]
        newMoveInegi = {}
        recActual = self.get_rec_activo(cve_mov)

        if not cve_mov in self.moves['bajas'].keys():
            raise f'Error, no se encontró {newMoveInegi[cve_ag]} en el catálogo cargado.'
        self.moves['bajas'][cve_mov]['hecho'] = True

        for field in self.catFields:
            newMoveInegi[field] = recActual[field]
        
        newMoveInegi['carga'] = self.load
        newMoveInegi['ent'] = recActual
        newMoveInegi['snap_id'] = recActual.snap_id + 1
        newMoveInegi['nuevo_reg'] = False
        newMoveInegi['fecha_act'] = row['fecha_act']
        newMoveInegi['es_activa'] = False
        newMoveInegi['mov_inegi'] = True
        newMoveInegi[self.cve_ag] = recActual[self.cve_ag] #FIXME: No sé si aplica
        newMoveInegi['cgo_act'] = moveType.cgo_act
        newMoveInegi['descgo_act'] = moveType.descgo_act
        
        return newMoveInegi

    def newAltaInegi(self, moveType, row):
        newMoveInegi = {}
        recInCat = self.dfs['cat'].loc[self.dfs['cat'][self.cve_ag] == row[self.cve_ag]]
        if len(recInCat) == 0:
            raise f"Error, no existe {row[self.cve_ag]} en el catálogo cargado"
        elif len(recInCat) == 1:
            recInCat = recInCat.to_dict('records')[0]
            cve_mov = recInCat[self.cve_ag]
            # EXISTE EN ALTAS ENCONTRADAS
            if not cve_mov in self.moves['altas'].keys():
                raise f'Error, no se encontro {newMoveInegi[cve_ag]} en los movimientos (altas).'
            self.moves['altas'][cve_mov]['hecho'] = True
            
            # TODO: get_padre() PARA MUNICIPIOS Y LOCALIDADES

            for field in self.catFields:
                newMoveInegi[field] = recInCat[field]
            newMoveInegi['carga'] = self.load
            newMoveInegi['snap_id'] = 1
            newMoveInegi['nuevo_reg'] = True
            newMoveInegi['fecha_act'] = row['fecha_act']
            newMoveInegi['es_activa'] = True
            newMoveInegi['mov_inegi'] = True
            newMoveInegi[self.cve_ag] = recInCat[self.cve_ag]
            newMoveInegi['cgo_act'] = moveType.cgo_act
            newMoveInegi['descgo_act'] = moveType.descgo_act
        else:
            raise f"Error, existe más de un registro con {row[self.cve_ag]} en catálogo cargado"
        return newMoveInegi
    
    #TODO: Movimientos no contenidos en el registro de actualizacion
    def makeMovesDAE(self):
        # ALTAS
        if self.moves.get('altas'):
            movesNotRegistered = [mv for mv in self.moves['altas'].values() if not mv.get('hecho')]
            moveType = self.movsCat.get(cgo_act='NU')
            for move in movesNotRegistered:
                newMove = self.newDAEMove('altas', move, moveType)
                self.newMoves['altas'].append(newMove)
        # BAJAS
        if self.moves.get('bajas'):
            movesNotRegistered = [mv for mv in self.moves['bajas'].values() if not mv.get('hecho')]
            if movesNotRegistered:
                self.errors.append(f'Hay bajas no registradas')
        # MOVIMIENTOS
        if self.moves.get('cambios'):
            movesNotRegistered = [mv for mv in self.moves['cambios'].values() if not mv.get('hecho')]
            if movesNotRegistered:
                self.errors.append(f'Hay moviemientos no registrados')
        if self.errors:
            return {'valid': False, 'errors': self.errors, 'status': 'en la creación de movimientos dae'}
        return {'valid': True, 'errors': self.errors, 'status': 'Creación de movimientos dae correcta'}
            
    def newDAEMove(self, _type, move, moveType):
        newMove = {}
        if _type == 'altas':
            for field in self.catFields:
                newMove[field] = move[field]
            newMove['carga'] = self.load
            newMove['snap_id'] = 1
            newMove['nuevo_reg'] = True
            newMove['fecha_act'] = self.load.filesVersion
            newMove['es_activa'] = True
            newMove['mov_inegi'] = False
            newMove[self.cve_ag] = move[self.cve_ag]
            newMove['cgo_act'] = moveType.cgo_act
            newMove['descgo_act'] = moveType.descgo_act
        return newMove
    
    def saveNewMoves(self):
        # try:
        count = 0
        for move_type in self.newMoves:
            for move in self.newMoves[move_type]:
                Tmp_Cat_Entidades.objects.create(**move)
                count += 1
        # except:
        #     self.errors.append('error al salvar los nuevos movimientos')
        if self.errors:
            return {'valid': False, 'errors': self.errors, 'status': 'en el salvado de registros temporales'}
        return {'valid': True, 'errors': self.errors, 'status': 'Salvado de registros temporales correcto'}
