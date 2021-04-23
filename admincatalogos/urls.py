from django.urls import path
from .views import (
    UploadFilesAPI, FilesStatusAPI, ValidaCifrasAPI,
    SeguimientoAPI, DQAPI, VersionesLocalidadesAPI,
    VersionesLocalidadesTKNAPI, SimulacionAPI,
    CardDatosAPI
)

app_name = 'admdata'

urlpatterns = [
    path('upload', UploadFilesAPI.as_view(), name='upload'),
    path('listloads', FilesStatusAPI.as_view(), name='listloads'),
    path('seguimiento', SeguimientoAPI.as_view(), name='seguimiento'),
    path('seguimiento-movs', CardDatosAPI.as_view(), name='seguimiento-movs'),
    path('validacifras', ValidaCifrasAPI.as_view(), name='validacifras'),
    path('dq', DQAPI.as_view(), name='dq'),
    path('simulacion', SimulacionAPI.as_view(), name='simulacion'),
    path('localidades-versiones', VersionesLocalidadesAPI.as_view(), name='localidades-versiones'),
    path('localidades-versiones-tkn', VersionesLocalidadesTKNAPI.as_view(), name='localidades-versiones-tkn'),
]
