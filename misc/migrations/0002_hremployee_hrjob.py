# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-24 12:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('misc', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HrEmployee',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('work_email', models.EmailField(max_length=254, verbose_name='Work Email')),
                ('name_related', models.CharField(blank=True, max_length=100, verbose_name='Name')),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('write_date', models.DateTimeField(auto_now=True)),
                ('write_uid', models.IntegerField(verbose_name='Write UID')),
                ('create_uid', models.IntegerField(verbose_name='Write UID')),
                ('publish', models.NullBooleanField(verbose_name='Publish on Website')),
                ('image_medium', models.BinaryField(verbose_name='Image')),
                ('image', models.BinaryField(verbose_name='Image')),
            ],
            options={
                'db_table': 'hr_employee',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='HrJob',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100, verbose_name='Name')),
                ('state', models.CharField(choices=[('open', 'Recruitment Closed'), ('recruit', 'Recruitment Open')], max_length=50, verbose_name='State')),
            ],
            options={
                'db_table': 'hr_job',
                'managed': False,
            },
        ),
    ]
