# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-15 13:18
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cart_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('write_date', models.DateTimeField(auto_now=True)),
                ('quantity', models.IntegerField(default=1)),
                ('product', models.IntegerField(verbose_name='Product')),
            ],
            options={
                'ordering': ('create_date',),
                'db_table': 'cart_items',
            },
        ),
    ]
