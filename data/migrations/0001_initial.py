# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(unique=True)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('moderators', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Discipline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
                ('full_name', models.TextField(unique=True)),
                ('moderators', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=20)),
                ('okr', models.IntegerField(choices=[(0, 'bachelor'), (1, 'magister'), (2, 'specialist')])),
                ('type', models.IntegerField(choices=[(0, 'daily'), (1, 'extramural')])),
                ('moderators', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6')])),
                ('day', models.IntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday')])),
                ('week', models.IntegerField(choices=[(1, 'Week 1'), (2, 'Week 2')])),
                ('type', models.IntegerField(null=True, choices=[(0, 'lecture'), (1, 'practical'), (2, 'laboratory')])),
                ('discipline', models.ForeignKey(to='data.Discipline')),
                ('groups', models.ManyToManyField(to='data.Group')),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('building', models.ForeignKey(to='data.Building')),
                ('moderators', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.TextField()),
                ('first_name', models.TextField()),
                ('middle_name', models.TextField()),
                ('degree', models.TextField()),
                ('moderators', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ('id',),
            },
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
            name='teacher',
            unique_together=set([('last_name', 'first_name', 'middle_name', 'degree')]),
        ),
        migrations.AlterUniqueTogether(
            name='room',
            unique_together=set([('name', 'building')]),
        ),
    ]
