# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rozklad', '0007_auto_20151001_1839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discipline',
            name='full_name',
            field=models.TextField(unique=True),
        ),
        migrations.AlterField(
            model_name='discipline',
            name='name',
            field=models.TextField(unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='teacher',
            unique_together=set([('last_name', 'first_name', 'middle_name', 'degree')]),
        ),
    ]
