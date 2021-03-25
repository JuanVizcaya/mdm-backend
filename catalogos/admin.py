from django.contrib import admin
from .models import Tmp_Cat_Entidades, Cat_Entidades


@admin.register(Cat_Entidades)
class CatEntidadesAdmin(admin.ModelAdmin):
    list_display = ('cve_ent','descgo_act','fecha_reg','es_activa')
    search_fields = ('cve_ent',)


@admin.register(Tmp_Cat_Entidades)
class TmpCatEntidadesAdmin(admin.ModelAdmin):
    list_display = ('cve_ent', 'carga', 'descgo_act',
                    'fecha_act','es_activa', 'mov_inegi')
    search_fields = ('cve_ent', 'ent')
    autocomplete_fields = ('ent',)
