# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnregisteredVKUserTimetablePermissions',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('vk_user_id', models.IntegerField()),
                ('groups', models.ManyToManyField(to='data.Group')),
                ('teachers', models.ManyToManyField(to='data.Teacher')),
            ],
        ),
    ]
