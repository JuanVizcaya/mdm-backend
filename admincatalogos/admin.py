from django.contrib import admin
from .models import UploadFiles, UploadFilesTrack, FileMovements, MovTypes, LastVersion, VersionesLocalidades


# Register your models here.
@admin.register(UploadFiles)
class UploadFilesAdmin(admin.ModelAdmin):
    list_display = ('filesType','filesId','filesVersion','author','status','activo')
    search_fields = ['filesId']

@admin.register(UploadFilesTrack)
class UploadFilesTrackAdmin(admin.ModelAdmin):
    list_display = ('UploadFiles','stepNumber','status','processStep','startTime','endTime')
    search_fields = ['UploadFiles.filesId']

@admin.register(FileMovements)
class FileMovementsAdmin(admin.ModelAdmin):
    list_display = ('UploadFiles','cgo_act','descgo_act','mov_cant','move_type')
    search_fields = ['UploadFiles.filesId']

@admin.register(MovTypes)
class MovTypesAdmin(admin.ModelAdmin):
    list_display = ('filesType', 'cgo_act', 'descgo_act', 'move_type')
    search_fields = ['cgo_act']

@admin.register(LastVersion)
class LastVersionAdmin(admin.ModelAdmin):
    list_display = ('filesType', 'filesVersion', 'uploadedDate')
    search_fields = ['filesVersion']

@admin.register(VersionesLocalidades)
class VersionesLocalidadesAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'version', 'fecha_carga', 'num_regs','vigente')
    search_fields = ['version']