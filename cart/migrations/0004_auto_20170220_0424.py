# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-20 04:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_cartitem_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartitem',
            old_name='user',
            new_name='user_id',
        ),
    ]
