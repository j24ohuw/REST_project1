# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-13 02:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snippets', '0004_stock_error'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock',
            name='error',
        ),
    ]