# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-23 03:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('odoo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VolumePricesLine',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('price', models.FloatField(verbose_name='Price')),
            ],
            options={
                'db_table': 'volume_prices_line',
                'managed': False,
            },
        ),
    ]
