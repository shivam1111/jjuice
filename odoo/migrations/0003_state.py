# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-03-23 07:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('odoo', '0002_volumepricesline'),
    ]

    operations = [
        migrations.CreateModel(
            name='State',
            fields=[
                ('name', models.CharField(max_length=60, verbose_name='Name')),
                ('code', models.CharField(max_length=3, verbose_name='Name')),
                ('id', models.IntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'res_country_state',
                'managed': False,
            },
        ),
    ]
