from django.urls import path
from .views import RegisterAPI

from rest_framework.authtoken.views import ObtainAuthToken

app_name = 'usuarios'

urlpatterns = [
    path('registrar', RegisterAPI.as_view(), name='register'),
    path('entrar', ObtainAuthToken.as_view(), name='login'),
]