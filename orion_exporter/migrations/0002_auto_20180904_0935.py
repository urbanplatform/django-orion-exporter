# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-04 09:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orion_exporter', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orionservicepath',
            name='name',
            field=models.CharField(max_length=255, verbose_name=b'Service Path'),
        ),
    ]
