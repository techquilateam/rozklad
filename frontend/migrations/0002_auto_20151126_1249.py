# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unregisteredvkusertimetablepermissions',
            name='groups',
            field=models.ManyToManyField(to='data.Group', blank=True),
        ),
        migrations.AlterField(
            model_name='unregisteredvkusertimetablepermissions',
            name='teachers',
            field=models.ManyToManyField(to='data.Teacher', blank=True),
        ),
    ]
