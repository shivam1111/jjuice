# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-06-18 12:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0005_cartitem_checkedout'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartnote',
            name='promotion_code',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Promotion Code'),
        ),
    ]