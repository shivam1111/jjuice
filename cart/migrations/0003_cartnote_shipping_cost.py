# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-03-30 07:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_cartnote'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartnote',
            name='shipping_cost',
            field=models.FloatField(default=0.0, verbose_name='Shipping Cost'),
        ),
    ]