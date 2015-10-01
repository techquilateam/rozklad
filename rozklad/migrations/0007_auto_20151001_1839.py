# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rozklad', '0006_lesson'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='type',
            field=models.IntegerField(null=True, choices=[(0, 'lecture'), (1, 'practical'), (2, 'laboratory')]),
        ),
    ]
