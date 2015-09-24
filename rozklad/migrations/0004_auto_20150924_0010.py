# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rozklad', '0003_room'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discipline',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.TextField()),
                ('full_name', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='building',
            name='number',
            field=models.IntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='room',
            unique_together=set([('name', 'building')]),
        ),
    ]
