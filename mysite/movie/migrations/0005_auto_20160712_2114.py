# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-12 19:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0004_auto_20160712_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='rate_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='entry',
            name='release_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='entry',
            name='url_imdb',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='genre',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
