from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
class RegisterAPI(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            usuario = serializer.save()
            data['response'] = 'Usuario registrado exitosamente'
            data['email'] = usuario.email
            data['first_name'] = usuario.first_name
            data['last_name'] = usuario.last_name
            token = Token.objects.get(user=usuario).key
            data['token'] = token
            return Response(data)
        else:
            data = serializer.errors
            return Response(data, status=status.HTTP_400_BAD_REQUEST)