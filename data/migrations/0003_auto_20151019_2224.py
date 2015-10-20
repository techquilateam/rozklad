# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_auto_20151019_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='degree',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='first_name',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='middle_name',
            field=models.TextField(blank=True),
        ),
    ]
