# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-17 21:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0002_position_weight'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='price',
            field=models.FloatField(default=-1),
        ),
    ]
