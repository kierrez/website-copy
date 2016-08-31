# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-31 13:41
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0008_entry_watch_again'),
    ]

    operations = [
        migrations.AddField(
            model_name='archive',
            name='watch_again_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='entry',
            name='watch_again_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, null=True),
        ),
    ]
