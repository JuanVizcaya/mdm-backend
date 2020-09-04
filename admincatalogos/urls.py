from django.urls import path
from .views import UploadFilesAPI, FilesStatusAPI, ValidaCifrasAPI, SeguimientoAPI

app_name = 'admdata'

urlpatterns = [
    path('upload', UploadFilesAPI.as_view(), name='upload'),
    path('listloads', FilesStatusAPI.as_view(), name='listloads'),
    path('seguimiento', SeguimientoAPI.as_view(), name='seguimiento'),
    path('validacifras', ValidaCifrasAPI.as_view(), name='validacifras'),
]
