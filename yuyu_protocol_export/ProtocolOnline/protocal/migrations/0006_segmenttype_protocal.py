# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-01 10:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('protocal', '0005_auto_20170801_1833'),
    ]

    operations = [
        migrations.AddField(
            model_name='segmenttype',
            name='protocal',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='protocal.Protocal'),
        ),
    ]
