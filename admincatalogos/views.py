# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
import json

from .models import UploadFiles, FileMovements
from .serializers import UploadFilesSerializer, UploadFilesListSerializer, FileMovementsSerializer
from .process.validacioncarga import validacionDeCarga
from .process.validacioncifras import validacionDeCifras
from .process.dq import dq


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

# WEBSERVICE INFO SEGUIMIENTO DE CARGA
# TODO: B - TERMINAR DE CONSTRUIR
class SeguimientoAPI(APIView):
    def get(self, request):
        # CARD - SEGUIMIENTO
        if not 'idcarga' in request.query_params:
            return Response({'statusRequest': 'error', 'error': 'Parámetros insuficientes', 'idcarga': 'Parámetro requerido'}, status=status.HTTP_400_BAD_REQUEST)
        idcarga = request.query_params.get('idcarga')
        try:
            qsSeguimiento = UploadFiles.objects.get(filesId = idcarga)
        except UploadFiles.DoesNotExist:
            return Response({'statusRequest': 'error', 'error': 'Id de carga inválido', 'idcarga': idcarga}, status=status.HTTP_400_BAD_REQUEST)
        if request.user != qsSeguimiento.author:
            return Response({'statusRequest': 'error', 'error': 'No tienes permisos sufucientes'}, status=status.HTTP_401_UNAUTHORIZED)
        seguimientoSerializedData = UploadFilesListSerializer(qsSeguimiento)
        
        # CARD - RESULTADOS
        qsResultados = FileMovements.objects.filter(UploadFiles = qsSeguimiento)
        if not qsResultados:
            dataResultados = None
        else:
            dataResultados = FileMovementsSerializer(qsResultados, many=True).data

        # TODO: C - CONSTRUIR CARD DATOS
        # CARD - DATOS
        return Response({'statusRequest': 'ok', 'dataSeguimiento': seguimientoSerializedData.data, 'dataResultados': dataResultados, 'dataDatos': None}, status=status.HTTP_200_OK)

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
        if carga.stepNumber != 5:
            return Response({'statusRequest': 'error', 'error': 'Este proceso no puede ejecutarse en la carga'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializedResponse = UploadFilesListSerializer(carga)
        resultadoDQ = dq(carga)
        
        return Response({'statusRequest': 'ok', 'data': None}, status=status.HTTP_200_OK)
