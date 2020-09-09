from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import UploadFiles, UploadFilesTrack
from django.utils import timezone

@receiver(post_save, sender=UploadFiles)
def new_load(sender, instance, created=False, **kwargs):
    if created:
        UploadFilesTrack.objects.create(
            UploadFiles = instance,
            stepNumber = 1,
            startTime = timezone.now(),
            endTime = timezone.now(),
            status = 'Nueva carga',
            statusDesc = '-',
            processStep = 'Cargado'
        )

@receiver(post_save, sender=UploadFilesTrack)
def upload_status(sender, instance, **kwargs):
    instance.UploadFiles.status = instance.status
    instance.UploadFiles.statusDesc = instance.statusDesc
    instance.UploadFiles.processStep = instance.processStep
    instance.UploadFiles.activo = instance.activo
    instance.UploadFiles.buttons = instance.buttons
    instance.UploadFiles.nextStep = instance.nextStep
    instance.UploadFiles.stepNumber = instance.stepNumber
    instance.UploadFiles.save()

@receiver(pre_delete, sender=UploadFiles)
def clear_temps(sender, instance, **kwargs):
    from pandas.io import sql
    from django.conf import settings
    from sqlalchemy import create_engine
    from shutil import rmtree
    from os.path import abspath, dirname, exists, join
    from os import getcwd
    
    engine = create_engine(f'postgresql://{settings.TEMP_FILES_USER}:{settings.TEMP_FILES_PASS}@{settings.TEMP_FILES_HOST}:{settings.TEMP_FILES_PORT}/{settings.TEMP_FILES_DBNAME}')

    if instance.catTable == f'tmp_cat_{instance.filesId}':
        sql.execute(f'DROP TABLE IF EXISTS {instance.catTable}', engine)
    elif instance.catTable == f'dq_tmp_{instance.filesType}_cat':
        sql.execute(f'DELETE FROM {instance.catTable} WHERE "filesId" = \'{instance.filesId}\'', engine)

    if instance.eqvTable == f'tmp_eqv_{instance.filesId}':
        sql.execute(f'DROP TABLE IF EXISTS {instance.eqvTable}', engine)
    elif instance.eqvTable == f'dq_tmp_{instance.filesType}_eqv':
        sql.execute(f'DELETE FROM {instance.eqvTable} WHERE "filesId" = \'{instance.filesId}\'', engine)

    if instance.actTable == f'tmp_act_{instance.filesId}':
        sql.execute(f'DROP TABLE IF EXISTS {instance.actTable}', engine)
    elif instance.actTable == f'dq_tmp_{instance.filesType}_act':
        sql.execute(f'DELETE FROM {instance.actTable} WHERE "filesId" = \'{instance.filesId}\'', engine)
    
    delPath = f'media/catalogos/{instance.filesId}'
    if exists(delPath):
        rmtree(delPath)
