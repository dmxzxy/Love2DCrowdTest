# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-08 06:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('protocal', '0010_auto_20170804_1240'),
    ]

    operations = [
        migrations.AddField(
            model_name='customtypesegment',
            name='namespace',
            field=models.CharField(default='name', max_length=100, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='enmusegment',
            name='namespace',
            field=models.CharField(default='name', max_length=100, unique=True),
            preserve_default=False,
        ),
    ]