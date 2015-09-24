# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rozklad', '0005_teacher'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6')])),
                ('day', models.IntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday')])),
                ('week', models.IntegerField(choices=[(1, 'Week 1'), (2, 'Week 2')])),
                ('type', models.IntegerField(choices=[(0, 'lecture'), (1, 'practical'), (2, 'laboratory')])),
                ('discipline', models.ForeignKey(to='rozklad.Discipline')),
                ('groups', models.ManyToManyField(to='rozklad.Group')),
                ('rooms', models.ManyToManyField(blank=True, to='rozklad.Room')),
                ('teachers', models.ManyToManyField(blank=True, to='rozklad.Teacher')),
            ],
        ),
    ]
