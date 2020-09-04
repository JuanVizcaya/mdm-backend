# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from usuarios.models import Usuario
from django.urls import reverse

from secrets import token_hex
# import locale

# locale.setlocale(locale.LC_ALL,'Spanish_US.1252')

def files_path(instance, filename):
    return 'media/catalogos/{}/{}'.format(instance.filesId, filename)

class UploadFiles(models.Model):
    class Meta:
        verbose_name = 'Catalogo cargado'
        verbose_name_plural = 'Cargas de catálogos'
    
    filesId = models.CharField(verbose_name='Id de carga',max_length=32,default='',unique=True)
    filesType = models.CharField(max_length=15, verbose_name='Tipo de Catálogo', choices=(('entidades','entidades'),('municipios','municipios'),('localidades','localidades')))
    filesVersion = models.DateField(verbose_name='Versión')
    uploadedDate = models.DateTimeField(verbose_name='Fecha de carga',default=timezone.now)
    author = models.ForeignKey(Usuario,verbose_name='Autor',on_delete=models.PROTECT, default=None)
    status = models.CharField(verbose_name='Estatus',max_length=80,default='Inicial')
    statusDesc = models.CharField(max_length=254,default='Carga inicial')
    processStep = models.CharField(max_length=80,default='-')
    stepNumber = models.DecimalField(verbose_name='Número de paso',max_digits=3,decimal_places=1,default=0)
    activo = models.BooleanField(verbose_name='Proceso activo',default=False)
    buttons = models.CharField(verbose_name='Botones Activos',max_length=20,default='')
    nextStep = models.CharField(verbose_name='En Proceso', max_length=80, default='')
    catLoad = models.FileField(verbose_name='Catalogo',upload_to=files_path)
    eqvLoad = models.FileField(verbose_name='Tabla de Equivalencias',upload_to=files_path)
    actLoad = models.FileField(verbose_name='Registro de Actualización',upload_to=files_path)
    catTable = models.CharField(verbose_name='Temporal del Catálogo', max_length=80, default='-')
    eqvTable = models.CharField(verbose_name='Temporal de la Tabla de Equivalencia', max_length=80, default='-')
    actTable = models.CharField(verbose_name='Temporal del Registro de Actualización', max_length=80, default='-')
    
    def save(self, *args, **kwargs):
        if not self.filesId:
            token = token_hex(16)
            self.filesId = token
        super(UploadFiles, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.filesVersion} - {self.filesType} ({self.filesId})'

class UploadFilesTrack(models.Model):
    class Meta:
        verbose_name = 'Tack completo'
        verbose_name_plural = 'Todos los tracks'
    UploadFiles = models.ForeignKey(UploadFiles, on_delete=models.CASCADE)
    stepNumber = models.DecimalField(verbose_name='Número de paso',max_digits=3,decimal_places=1)
    startTime = models.DateTimeField(verbose_name='Hora de inicio')
    endTime = models.DateTimeField(verbose_name='Hora de fin',null=True, blank=True)
    status = models.CharField(verbose_name='Estatus',max_length=80)
    statusDesc = models.CharField(verbose_name='Descripción del estatus',max_length=254)
    processStep = models.CharField(verbose_name='Paso',max_length=80)
    activo = models.BooleanField(verbose_name='Proceso activo',default=False)
    buttons = models.CharField(verbose_name='Botones Activos',max_length=20,default='')
    nextStep = models.CharField(verbose_name='En Proceso', max_length=80, default='')
    
    def __str__(self):
        return f'Id : {self.UploadFiles.filesId} - paso: {self.stepNumber}'

# class FilesTypes(models.Model):
#     abr = models.CharField(max_length=10)
#     name = models.CharField(max_length=50)

class LastVersion(models.Model):
    class Meta:
        verbose_name = 'Último periodo cargado'
        verbose_name_plural = 'Versiones vigentes'
    filesType = models.CharField(max_length=15, verbose_name='Tipo de Catálogo', choices=(('entidades','entidades'),('municipios','municipios'),('localidades','localidades')))
    filesVersion = models.DateField(verbose_name='Versión')
    uploadedDate = models.DateTimeField(verbose_name='Fecha de carga',default=timezone.now)
    author = models.ForeignKey(Usuario,on_delete=models.PROTECT)

    def __str__(self):
        return self.filesType

class FileMovements(models.Model):
    class Meta:
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos por carga'
    UploadFiles = models.ForeignKey(UploadFiles, on_delete=models.CASCADE)
    cgo_act = models.CharField(verbose_name='Código de actualización',max_length=2)
    descgo_act = models.CharField(verbose_name='Descripción del código de actualización',max_length=110)
    mov_cant = models.IntegerField(verbose_name='Cantidad')
    move_type = models.CharField(verbose_name='Tipo de movimiento (Alta/Baja)', max_length=5, choices=(('alta','alta'),('baja','baja'),('ambas','ambas')), default='ambas')

class MovTypes(models.Model):
    class Meta:
        verbose_name = 'Tipo de movimiento'
        verbose_name_plural = 'Tipos de movimientos'
    filesType = models.CharField(max_length=15, verbose_name='Tipo de Catálogo', choices=(('entidades','entidades'),('municipios','municipios'),('localidades','localidades')))
    cgo_act = models.CharField(verbose_name='Código de actualización',max_length=2)
    descgo_act = models.CharField(verbose_name='Descripción del código de actualización',max_length=110)
    move_type = models.CharField(verbose_name='Tipo de movimiento (Alta/Baja)', max_length=5, choices=(('alta','alta'),('baja','baja'),('ambas','ambas')), default='ambas')
    author = models.ForeignKey(Usuario,on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.filesType} - {self.descgo_act} ({self.cgo_act})'
