# Generated by Django 3.0.4 on 2020-09-18 03:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admincatalogos', '0011_versioneslocalidades'),
    ]

    operations = [
        migrations.AddField(
            model_name='versioneslocalidades',
            name='vigente',
            field=models.BooleanField(default=False, verbose_name='Vigente'),
        ),
    ]
