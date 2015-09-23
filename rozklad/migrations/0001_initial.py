# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=20)),
                ('okr', models.IntegerField(choices=[(0, 'bachelor'), (1, 'magister'), (2, 'specialist')])),
                ('type', models.IntegerField(choices=[(0, 'daily'), (1, 'extramural')])),
            ],
        ),
    ]
