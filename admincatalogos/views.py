# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
import json

from .models import UploadFiles, FileMovements, VersionesLocalidades
from .process.validacioncarga import validacionDeCarga
from .process.validacioncifras import validacionDeCifras
from .process.dq.dq import dq_process
from .process.simulacion.simulacion import sim_process
from .serializers import (
    UploadFilesSerializer, UploadFilesListSerializer,
    FileMovementsSerializer, VersionesLocalidadesSerializer,
    TmpEntidadesDataSerializer
)

from catalogos.models import Tmp_Cat_Entidades

# WEBSERVICE LISTA DE CARGAS POR TIPO DE CATÁLOGO
class FilesStatusAPI(APIView):
    def get(self, request):
        if not 'catalogo' in request.query_params:
            return Response({'statusRequest': 'error', 'error': 'Parámetros insuficientes', 'catalogo': 'Parámetro requerido'}, status=status.HTTP_400_BAD_REQUEST)
        filesType = request.query_params.get('catalogo')
        if not filesType in ('entidades', 'municipios', 'localidades'):
            return Response({'statusRequest': 'error', 'error': 'opciones permitidas: entidades, municipios, localidades'}, status=status.HTTP_400_BAD_REQUEST)
        qs = UploadFiles.objects.filter(filesType = filesType)
        serializedData = UploadFilesListSerializer(qs, many=True)
        return Response({'count': len(serializedData.data),'statusRequest': 'ok', 'data': serializedData.data}, status=status.HTTP_200_OK)

# WEBSERVICE DE CARGA Y VALIDACIÓN
class UploadFilesAPI(APIView):
    def post(self, request):
        serializedData = UploadFilesSerializer(data=request.data)
        responseData = {}
        if serializedData.is_valid():
            filesLoad = serializedData.save(author=request.user)
            serializedResponse = UploadFilesSerializer(filesLoad)
            resultadoValidacion = validacionDeCarga(filesLoad)
            resultadoValidacion['data'] = serializedResponse.data
            return Response(resultadoValidacion, status=status.HTTP_200_OK)

        else:
            responseData = serializedData.errors
            return Response(responseData, status=status.HTTP_400_BAD_REQUEST)

class SeguimientoAPI(APIView):
    """ ENDPOINT INFO SEGUIMIENTO DE CARGA """
    def get(self, request):
        # CARD - SEGUIMIENTO
        if not 'idcarga' in request.query_params:
            return Response(
                {
                    'statusRequest': 'error',
                    'error': 'Parámetros insuficientes',
                    'idcarga': 'Parámetro requerido'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        idcarga = request.query_params.get('idcarga')
        try:
            load = UploadFiles.objects.get(filesId = idcarga)
        except UploadFiles.DoesNotExist:
            return Response(
                {
                    'statusRequest': 'error',
                    'error': 'Id de carga inválido',
                    'idcarga': idcarga
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.user != load.author:
            return Response(
                {
                    'statusRequest': 'error',
                    'error': 'No tienes permisos sufucientes'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        seguimientoSerializedData = UploadFilesListSerializer(load)
        
        # CARD - RESULTADOS
        qsResultados = FileMovements.objects.filter(UploadFiles = load)
        if not qsResultados:
            dataResultados = None
        else:
            dataResultados = FileMovementsSerializer(qsResultados, many=True).data

        # CARD - DATOS
        dataDatosExists = False
        if Tmp_Cat_Entidades.objects.filter(carga=load).exists():
            dataDatosExists = True
        
        return Response(
            {
                'statusRequest': 'ok',
                'dataSeguimiento': seguimientoSerializedData.data,
                'dataResultados': dataResultados,
                'dataDatosExists': dataDatosExists
            },
            status=status.HTTP_200_OK
        )


# TODO: C - CONSTRUIR CARD DATOS SERVICE
class CardDatosAPI(APIView):
    def get(self, request):
        if not 'idcarga' in request.query_params:
            return Response({'statusRequest': 'error', 'error': 'Parámetros insuficientes', 'idcarga': 'Parámetro requerido'}, status=status.HTTP_400_BAD_REQUEST)
        idcarga = request.query_params.get('idcarga')
        try:
            carga = UploadFiles.objects.get(filesId = idcarga)
        except UploadFiles.DoesNotExist:
            return Response({'statusRequest': 'error',  'error': 'Id de carga inválido', 'idcarga': idcarga}, status=status.HTTP_400_BAD_REQUEST)
        if request.user != carga.author:
            return Response({'statusRequest': 'error', 'error': 'No tienes permisos sufucientes'}, status=status.HTTP_401_UNAUTHORIZED)
        
        qs = Tmp_Cat_Entidades.objects.filter(carga=carga)
        if not qs.exists():
            return Response(
                {'statusRequest': 'error', 'error': 'No existen movimientos para esta carga'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TmpEntidadesDataSerializer(qs, many=True)
        return Response(
            {'statusRequest': 'ok', 'data': serializer.data}
        )

# WEBSERVICE PASO 2 - VALIDACIÓN DE CIFRAS
class ValidaCifrasAPI(APIView):
    def get(self, request):
        if not 'idcarga' in request.query_params:
            return Response({'statusRequest': 'error', 'error': 'Parámetros insuficientes', 'idcarga': 'Parámetro requerido'}, status=status.HTTP_400_BAD_REQUEST)
        idcarga = request.query_params.get('idcarga')
        try:
            carga = UploadFiles.objects.get(filesId = idcarga)
        except UploadFiles.DoesNotExist:
            return Response({'statusRequest': 'error',  'error': 'Id de carga inválido', 'idcarga': idcarga}, status=status.HTTP_400_BAD_REQUEST)
        if request.user != carga.author:
            return Response({'statusRequest': 'error', 'error': 'No tienes permisos sufucientes'}, status=status.HTTP_401_UNAUTHORIZED)
        if carga.stepNumber != 5:
            return Response({'statusRequest': 'error', 'error': 'Este proceso no puede ejecutarse en la carga'}, status=status.HTTP_401_UNAUTHORIZED)
        serializedResponse = UploadFilesListSerializer(carga)
        resultadoValidacion = validacionDeCifras(carga)
        resultadoValidacion['data'] = serializedResponse.data
        
        return Response({'statusRequest': 'ok', 'data': resultadoValidacion}, status=status.HTTP_200_OK)

class DQAPI(APIView):
    def get(self, request):
        if not 'idcarga' in request.query_params:
            return Response({'statusRequest': 'error', 'error': 'Parámetros insuficientes', 'idcarga': 'Parámetro requerido'}, status=status.HTTP_400_BAD_REQUEST)
        idcarga = request.query_params.get('idcarga')
        try:
            carga = UploadFiles.objects.get(filesId = idcarga)
        except UploadFiles.DoesNotExist:
            return Response({'statusRequest': 'error',  'error': 'Id de carga inválido', 'idcarga': idcarga}, status=status.HTTP_400_BAD_REQUEST)
        if request.user != carga.author:
            return Response({'statusRequest': 'error', 'error': 'No tienes permisos sufucientes'}, status=status.HTTP_401_UNAUTHORIZED)
        if carga.stepNumber != 9:
            return Response({'statusRequest': 'error', 'error': 'Este proceso no puede ejecutarse en la carga'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializedResponse = UploadFilesListSerializer(carga)
        resultadoDQ = dq_process(carga)
        resultadoDQ['data'] = serializedResponse.data
        
        return Response({'statusRequest': 'ok', 'data': resultadoDQ}, status=status.HTTP_200_OK)

class SimulacionAPI(APIView):
    def get(self, request):
        if not 'idcarga' in request.query_params:
            return Response({'statusRequest': 'error', 'error': 'Parámetros insuficientes', 'idcarga': 'Parámetro requerido'}, status=status.HTTP_400_BAD_REQUEST)
        idcarga = request.query_params.get('idcarga')
        try:
            carga = UploadFiles.objects.get(filesId = idcarga)
        except UploadFiles.DoesNotExist:
            return Response({'statusRequest': 'error',  'error': 'Id de carga inválido', 'idcarga': idcarga}, status=status.HTTP_400_BAD_REQUEST)
        if request.user != carga.author:
            return Response({'statusRequest': 'error', 'error': 'No tienes permisos sufucientes'}, status=status.HTTP_401_UNAUTHORIZED)
        if carga.stepNumber != 14:
            return Response({'statusRequest': 'error', 'error': 'Este proceso no puede ejecutarse en la carga'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializedResponse = UploadFilesListSerializer(carga)
        resultadoSimulacion = sim_process(carga)
        resultadoSimulacion['data'] = serializedResponse.data
        
        return Response({'statusRequest': 'ok', 'data': resultadoSimulacion}, status=status.HTTP_200_OK)


class VersionesLocalidadesAPI(APIView):
    def get(self, request):
        cargas = VersionesLocalidades.objects.filter(tipo = 'localidades')
        serializedResponse = VersionesLocalidadesSerializer(cargas, many=True)
        
        return Response({'tipo': 'get', 'statusRequest': 'ok', 'data': serializedResponse.data}, status=status.HTTP_200_OK)

    def post(self, request):
        cargas = VersionesLocalidades.objects.filter(tipo = 'localidades')
        serializedResponse = VersionesLocalidadesSerializer(cargas, many=True)
        
        return Response({'tipo': 'post','statusRequest': 'ok', 'data': serializedResponse.data}, status=status.HTTP_200_OK)

class VersionesLocalidadesTKNAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if not 'tipo' in request.query_params:
            return Response({'statusRequest': 'error', 'error': 'Parámetros insuficientes', 'tipo': 'Parámetro requerido'}, status=status.HTTP_400_BAD_REQUEST)
        tipo = request.query_params.get('tipo')
        if not tipo in ('entidades', 'municipios', 'localidades'):
            return Response({'statusRequest': 'error', 'error': 'Parámetros inválido, se aceptan (entidades, municipios, localidades)', 'tipo_enviado': tipo}, status=status.HTTP_400_BAD_REQUEST)
        tipo = request.query_params.get('tipo')
        try:
            cargas = VersionesLocalidades.objects.filter(tipo = tipo)
        except VersionesLocalidades.DoesNotExist:
            return Response({'statusRequest': 'error',  'error': 'Tipo inválido, se aceptan "entidades", "municipios" o "localidades"', 'tipo_enviado': tipo}, status=status.HTTP_400_BAD_REQUEST)
        
        serializedResponse = VersionesLocalidadesSerializer(cargas, many=True)
        
        return Response({'tipo': 'get', 'statusRequest': 'ok', 'data': serializedResponse.data}, status=status.HTTP_200_OK)

    def post(self, request):
        if not 'tipo' in request.query_params:
            return Response({'statusRequest': 'error', 'error': 'Parámetros insuficientes', 'tipo': 'Parámetro requerido'}, status=status.HTTP_400_BAD_REQUEST)
        tipo = request.query_params.get('tipo')
        try:
            cargas = VersionesLocalidades.objects.filter(tipo = tipo)
        except VersionesLocalidades.DoesNotExist:
            return Response({'statusRequest': 'error',  'error': 'Tipo inválido, se aceptan "entidades", "municipios" o "localidades"', 'tipo_enviado': tipo}, status=status.HTTP_400_BAD_REQUEST)
        
        serializedResponse = VersionesLocalidadesSerializer(cargas, many=True)
        
        return Response({'tipo': 'get', 'statusRequest': 'ok', 'data': serializedResponse.data}, status=status.HTTP_200_OK)