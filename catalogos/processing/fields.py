from admincatalogos.process import dq_functions as dqf
from django.db.models import CharField, DecimalField, IntegerField, DateField

toConcatenate = {
    'cve_munc': 'cve_ent',
    'cve_locc': 'cve_munc',
    'cve_cab': 'cve_munc',
    'cvemuncori': 'cveent_ori',
    'cvemuncact': 'cveent_act',
    'cveloccori': 'cvemuncori',
    'cveloccact': 'cvemuncact'
}

model_fields = {
    'cve_ent': {'model': CharField(verbose_name='Clave de entidad',max_length=2), 'rules': [dqf.to_str,dqf.remove_spaces,dqf.zfill2]},
    'cve_munc': {'model': CharField(verbose_name='Clave de municipio',max_length=5), 'rules': [dqf.to_str,dqf.remove_spaces,dqf.zfill3,dqf.concatenate]},
    'cve_locc': {'model': CharField(verbose_name='Clave de localidad',max_length=9), 'rules': [dqf.to_str,dqf.remove_spaces,dqf.zfill4,dqf.concatenate]},
    'mapa_loc': {'model': CharField(verbose_name='Clave de localidad para mapa',max_length=9), 'rules': [dqf.delete_field]},
    'cve_cab': {'model': CharField(verbose_name='Clave de la cabecera municipal',max_length=9), 'rules': [dqf.to_str,dqf.remove_spaces,dqf.zfill4,dqf.concatenate]},
    'nom_ent': {'model': CharField(verbose_name='Nombre de entidad',max_length=110), 'rules': [dqf.upper,dqf.strip,dqf.rm_double_spaces,dqf.replace_tilde]},
    'nom_mun': {'model': CharField(verbose_name='Nombre de municipio',max_length=110), 'rules': [dqf.upper,dqf.strip,dqf.rm_double_spaces,dqf.replace_tilde]},
    'nom_loc': {'model': CharField(verbose_name='Nombre de la localidad',max_length=110), 'rules': [dqf.upper,dqf.strip,dqf.rm_double_spaces,dqf.replace_tilde]},
    'nom_cab': {'model': CharField(verbose_name='Nombre de la cabecera municipal',max_length=110), 'rules': [dqf.upper,dqf.strip,dqf.rm_double_spaces,dqf.replace_tilde]},
    'abr_ent': {'model': CharField(verbose_name='Abreviatura de entidad',max_length=16), 'rules': [dqf.upper,dqf.remove_spaces]},
    'ambito': {'model': CharField(verbose_name='Ambito',max_length=1), 'rules': [dqf.upper,dqf.remove_spaces]},
    'latitud': {'model': CharField(verbose_name='Latitud gms',max_length=20), 'rules': [dqf.to_str,dqf.remove_spaces]},
    'longitud': {'model': CharField(verbose_name='Longitud gms',max_length=20), 'rules': [dqf.to_str,dqf.remove_spaces]},
    'lat_dec': {'model': DecimalField(verbose_name='Latitud decimal',max_digits=14,decimal_places=8), 'rules': [dqf.to_float]},
    'lon_dec': {'model': DecimalField(verbose_name='Longitud decimal',max_digits=14,decimal_places=8), 'rules': [dqf.to_float]},
    'altitud': {'model': DecimalField(verbose_name='Altitud',max_digits=11,decimal_places=3), 'rules': [dqf.to_float]},
    'cve_carta': {'model': CharField(verbose_name='Calve carta',max_length=6), 'rules': [dqf.upper,dqf.remove_spaces]},
    'p_total': {'model': IntegerField(verbose_name='Población total'), 'rules': [dqf.to_str,dqf.remove_spaces,dqf.char_to_zero,dqf.to_int]},
    'v_total': {'model': IntegerField(verbose_name='Viviendas totales'), 'rules': [dqf.to_str,dqf.remove_spaces,dqf.char_to_zero,dqf.to_int]},
    'p_mas': {'model': IntegerField(verbose_name='Población masculina'), 'rules': [dqf.to_str,dqf.remove_spaces,dqf.char_to_zero,dqf.to_int]},
    'p_fem': {'model': IntegerField(verbose_name='Población femenina'), 'rules': [dqf.to_str,dqf.remove_spaces,dqf.char_to_zero,dqf.to_int]},
    'cveent_ori': {'model': CharField(verbose_name='Clave de entidad origen',max_length=2), 'rules': [dqf.to_str,dqf.remove_spaces,dqf.zfill2]},
    'cveent_act': {'model': CharField(verbose_name='Clave de entidad actual',max_length=2), 'rules': [dqf.to_str,dqf.remove_spaces,dqf.zfill2]},
    'cvemuncori': {'model': CharField(verbose_name='Clave de municipio origen',max_length=5), 'rules': [dqf.to_str,dqf.remove_spaces,dqf.zfill3,dqf.concatenate]},
    'cvemuncact': {'model': CharField(verbose_name='Clave de municipio actual',max_length=5), 'rules': [dqf.to_str,dqf.remove_spaces,dqf.zfill3,dqf.concatenate]},
    'cveloccori': {'model': CharField(verbose_name='Clave de localidad origen',max_length=9), 'rules': [dqf.to_str,dqf.remove_spaces,dqf.zfill4,dqf.concatenate]},
    'cveloccact': {'model': CharField(verbose_name='Clave de localidad actual',max_length=9), 'rules': [dqf.to_str,dqf.remove_spaces,dqf.zfill4,dqf.concatenate]},
    'noment_ori': {'model': CharField(verbose_name='Nombre de entidad origen',max_length=110), 'rules': [dqf.upper,dqf.strip,dqf.rm_double_spaces,dqf.replace_tilde]},
    'noment_act': {'model': CharField(verbose_name='Nombre de entidad origen',max_length=110), 'rules': [dqf.upper,dqf.strip,dqf.rm_double_spaces,dqf.replace_tilde]},
    'nommun_ori': {'model': CharField(verbose_name='Nombre de municipio origen',max_length=110), 'rules': [dqf.upper,dqf.strip,dqf.rm_double_spaces,dqf.replace_tilde]},
    'nommun_act': {'model': CharField(verbose_name='Nombre de municipio actual',max_length=110), 'rules': [dqf.upper,dqf.strip,dqf.rm_double_spaces,dqf.replace_tilde]},
    'nomloc_ori': {'model': CharField(verbose_name='Nombre de localidad origen',max_length=110), 'rules': [dqf.upper,dqf.strip,dqf.rm_double_spaces,dqf.replace_tilde]},
    'nomloc_act': {'model': CharField(verbose_name='Nombre de localidad actual',max_length=110), 'rules': [dqf.upper,dqf.strip,dqf.rm_double_spaces,dqf.replace_tilde]},
    'ambito_ori': {'model': CharField(verbose_name='Ambito origen',max_length=1), 'rules': [dqf.upper,dqf.remove_spaces]},
    'ambito_act': {'model': CharField(verbose_name='Ambito actual',max_length=1), 'rules': [dqf.upper,dqf.remove_spaces]},
    'fecha_act': {'model': DateField(verbose_name='Fecha de actualización'), 'rules': [dqf.remove_spaces,dqf.to_date]},
    'cgo_act': {'model': CharField(verbose_name='Código de actualización',max_length=2), 'rules': [dqf.upper,dqf.remove_spaces]},
    'descgo_act': {'model': CharField(verbose_name='Descripción del código de actualización',max_length=110), 'rules': [dqf.upper,dqf.strip]},
    'estatus': {'model': CharField(verbose_name='Estatus',max_length=10)}
}