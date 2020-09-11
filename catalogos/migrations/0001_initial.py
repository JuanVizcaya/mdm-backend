# Generated by Django 3.0.4 on 2020-09-11 03:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('admincatalogos', '0010_auto_20200910_2229'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cat_Ent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cve_ent', models.CharField(max_length=2, verbose_name='Clave de entidad')),
                ('nom_ent', models.CharField(max_length=110, verbose_name='Nombre de entidad')),
                ('abr_ent', models.CharField(max_length=16, verbose_name='Abreviatura de entidad')),
                ('p_total', models.IntegerField(verbose_name='Población total')),
                ('v_total', models.IntegerField(verbose_name='Viviendas totales')),
                ('p_mas', models.IntegerField(verbose_name='Población masculina')),
                ('p_fem', models.IntegerField(verbose_name='Población femenina')),
                ('cgo_act', models.CharField(max_length=2, verbose_name='Código de actualización')),
                ('descgo_act', models.CharField(max_length=110, verbose_name='Descripción del código de actualización')),
                ('snap_id', models.IntegerField(verbose_name='Id snapshot')),
                ('fecha_ini', models.DateField(verbose_name='Fecha de inicio del movimiento')),
                ('fecha_fin', models.DateField(verbose_name='Fecha de fin del movimiento')),
                ('fecha_reg', models.DateField(verbose_name='Fecha registro del movimiento')),
                ('es_activa', models.BooleanField(verbose_name='Es activa')),
                ('mov_inegi', models.BooleanField(verbose_name='Reportado por INEGI')),
            ],
            options={
                'verbose_name': 'Entidades',
                'verbose_name_plural': 'Catálogo de entidades',
            },
        ),
        migrations.CreateModel(
            name='Tmp_Cat_Ent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cve_ent', models.CharField(max_length=2, verbose_name='Clave de entidad')),
                ('nom_ent', models.CharField(max_length=110, verbose_name='Nombre de entidad')),
                ('abr_ent', models.CharField(max_length=16, verbose_name='Abreviatura de entidad')),
                ('p_total', models.IntegerField(verbose_name='Población total')),
                ('v_total', models.IntegerField(verbose_name='Viviendas totales')),
                ('p_mas', models.IntegerField(verbose_name='Población masculina')),
                ('p_fem', models.IntegerField(verbose_name='Población femenina')),
                ('fecha_act', models.DateField(verbose_name='Fecha de actualización')),
                ('cgo_act', models.CharField(max_length=2, verbose_name='Código de actualización')),
                ('descgo_act', models.CharField(max_length=110, verbose_name='Descripción del código de actualización')),
                ('snap_id', models.IntegerField(verbose_name='Id snapshot')),
                ('es_activa', models.BooleanField(verbose_name='Es activa')),
                ('mov_inegi', models.BooleanField(verbose_name='Reportado por INEGI')),
                ('nuevo_reg', models.BooleanField(verbose_name='Primer registro')),
                ('carga', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admincatalogos.UploadFiles')),
                ('ent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogos.Cat_Ent')),
            ],
            options={
                'verbose_name': 'Entidades temporales',
                'verbose_name_plural': 'Catálogo de entidades temporal',
            },
        ),
        migrations.CreateModel(
            name='Hist_Ent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cve_ent', models.CharField(max_length=2, verbose_name='Clave de entidad')),
                ('nom_ent', models.CharField(max_length=110, verbose_name='Nombre de entidad')),
                ('abr_ent', models.CharField(max_length=16, verbose_name='Abreviatura de entidad')),
                ('p_total', models.IntegerField(verbose_name='Población total')),
                ('v_total', models.IntegerField(verbose_name='Viviendas totales')),
                ('p_mas', models.IntegerField(verbose_name='Población masculina')),
                ('p_fem', models.IntegerField(verbose_name='Población femenina')),
                ('cgo_act', models.CharField(max_length=2, verbose_name='Código de actualización')),
                ('descgo_act', models.CharField(max_length=110, verbose_name='Descripción del código de actualización')),
                ('snap_id', models.IntegerField(verbose_name='Id snapshot')),
                ('fecha_ini', models.DateField(verbose_name='Fecha de inicio del movimiento')),
                ('fecha_fin', models.DateField(verbose_name='Fecha de fin del movimiento')),
                ('fecha_reg', models.DateField(verbose_name='Fecha registro del movimiento')),
                ('es_activa', models.BooleanField(verbose_name='Es activa')),
                ('mov_inegi', models.BooleanField(verbose_name='Reportado por INEGI')),
                ('ent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogos.Cat_Ent')),
            ],
        ),
    ]