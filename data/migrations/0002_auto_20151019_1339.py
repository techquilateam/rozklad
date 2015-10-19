# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='building',
            name='moderators',
        ),
        migrations.RemoveField(
            model_name='discipline',
            name='moderators',
        ),
        migrations.RemoveField(
            model_name='group',
            name='moderators',
        ),
        migrations.RemoveField(
            model_name='room',
            name='moderators',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='moderators',
        ),
    ]
