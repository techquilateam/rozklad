# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('number', models.IntegerField(unique=True)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
            options={
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Discipline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.TextField(unique=True)),
                ('full_name', models.TextField(unique=True)),
            ],
            options={
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=20, unique=True)),
                ('okr', models.IntegerField(choices=[(0, 'bachelor'), (1, 'magister'), (2, 'specialist')])),
                ('type', models.IntegerField(choices=[(0, 'daily'), (1, 'extramural')])),
            ],
            options={
                'ordering': ('id',),
                'permissions': (('edit_group_timetable', 'Edit Group Timetable'),),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('number', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6')])),
                ('day', models.IntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday')])),
                ('week', models.IntegerField(choices=[(1, 'Week 1'), (2, 'Week 2')])),
                ('type', models.IntegerField(null=True, choices=[(0, 'lecture'), (1, 'practical'), (2, 'laboratory')])),
                ('discipline', models.ForeignKey(to='data.Discipline')),
                ('groups', models.ManyToManyField(to='data.Group')),
            ],
            options={
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=10)),
                ('building', models.ForeignKey(to='data.Building')),
            ],
            options={
                'ordering': ('id',),
                'permissions': (('edit_room_timetable', 'Edit Room Timetable'),),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('last_name', models.TextField()),
                ('first_name', models.TextField(blank=True)),
                ('middle_name', models.TextField(blank=True)),
                ('degree', models.TextField(blank=True)),
            ],
            options={
                'ordering': ('id',),
                'permissions': (('edit_teacher_timetable', 'Edit Teacher Timetable'),),
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='teacher',
            unique_together=set([('last_name', 'first_name', 'middle_name', 'degree')]),
        ),
        migrations.AddField(
            model_name='lesson',
            name='rooms',
            field=models.ManyToManyField(to='data.Room', blank=True),
        ),
        migrations.AddField(
            model_name='lesson',
            name='teachers',
            field=models.ManyToManyField(to='data.Teacher', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='room',
            unique_together=set([('name', 'building')]),
        ),
    ]
