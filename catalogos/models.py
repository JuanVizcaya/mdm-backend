# -*- coding: utf-8 -*-
from django.db import models

from admincatalogos.models import UploadFiles
from .processing.fields import  model_fields

# ===== MODELOS DE ENTIDADES =====

class Cat_Entidades(models.Model):
    class Meta:
        verbose_name = 'Entidades'
        verbose_name_plural = 'Catálogo de entidades'
    snap_id = model_fields['snap_id']['model']
    par_id = model_fields['par_id']['model']
    fecha_ini = model_fields['fecha_ini']['model']
    fecha_fin = model_fields['fecha_fin']['model']
    fecha_reg = model_fields['fecha_reg']['model']
    es_activa = model_fields['es_activa']['model']
    mov_inegi = model_fields['mov_inegi']['model']
    cve_ent = model_fields['cve_ent']['model']
    nom_ent = model_fields['nom_ent']['model']
    abr_ent = model_fields['abr_ent']['model']
    p_total = model_fields['p_total']['model']
    v_total = model_fields['v_total']['model']
    p_mas = model_fields['p_mas']['model']
    p_fem = model_fields['p_fem']['model']
    cgo_act = model_fields['cgo_act']['model']
    descgo_act = model_fields['descgo_act']['model']

class Tmp_Cat_Entidades(models.Model):
    class Meta:
        verbose_name = 'Entidad temporal'
        verbose_name_plural = 'Entidades temporales'
    carga = models.ForeignKey(UploadFiles, on_delete=models.CASCADE)
    ent = models.ForeignKey(Cat_Entidades, on_delete=models.CASCADE, null=True, blank=True)
    snap_id = model_fields['snap_id']['model']
    nuevo_reg = model_fields['nuevo_reg']['model']
    fecha_act = model_fields['fecha_act']['model']
    es_activa = model_fields['es_activa']['model']
    mov_inegi = model_fields['mov_inegi']['model']
    cve_ent = model_fields['cve_ent']['model']
    nom_ent = model_fields['nom_ent']['model']
    abr_ent = model_fields['abr_ent']['model']
    p_total = model_fields['p_total']['model']
    v_total = model_fields['v_total']['model']
    p_mas = model_fields['p_mas']['model']
    p_fem = model_fields['p_fem']['model']
    cgo_act = model_fields['cgo_act']['model']
    descgo_act = model_fields['descgo_act']['model']
    
class Hist_Entidades(models.Model):
    ent = models.ForeignKey(Cat_Entidades,on_delete=models.CASCADE)
    snap_id = model_fields['snap_id']['model']
    fecha_ini = model_fields['fecha_ini']['model']
    fecha_fin = model_fields['fecha_fin']['model']
    fecha_reg = model_fields['fecha_reg']['model']
    es_activa = model_fields['es_activa']['model']
    mov_inegi = model_fields['mov_inegi']['model']
    cve_ent = model_fields['cve_ent']['model']
    nom_ent = model_fields['nom_ent']['model']
    abr_ent = model_fields['abr_ent']['model']
    p_total = model_fields['p_total']['model']
    v_total = model_fields['v_total']['model']
    p_mas = model_fields['p_mas']['model']
    p_fem = model_fields['p_fem']['model']
    cgo_act = model_fields['cgo_act']['model']
    descgo_act = model_fields['descgo_act']['model']
    
# ===== MODELOS DE MUNICIPIOS =====
    
# class Cat_Mun(models.Model):
#     snap_id = model_fields['snap_id']['model']
#     fecha_ini = model_fields['fecha_ini']['model']
#     fecha_fin = model_fields['fecha_fin']['model']
#     es_activa = model_fields['es_activa']['model']
#     mov_inegi = model_fields['mov_inegi']['model']
#     cve_ent = model_fields['cve_ent']['model']
#     nom_ent = model_fields['nom_ent']['model']
#     abr_ent = model_fields['abr_ent']['model']
#     p_total = model_fields['p_total']['model']
#     v_total = model_fields['v_total']['model']
#     p_mas = model_fields['p_mas']['model']
#     p_fem = model_fields['p_fem']['model']
#     estatus = model_fields['estatus']['model']
#     cgo_act = model_fields['cgo_act']['model']
#     descgo_act = model_fields['descgo_act']['model']