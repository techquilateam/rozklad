# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rozklad', '0009_auto_20151004_0359'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='building',
            options={'ordering': ('id',)},
        ),
        migrations.AlterModelOptions(
            name='discipline',
            options={'ordering': ('id',)},
        ),
        migrations.AlterModelOptions(
            name='group',
            options={'ordering': ('id',)},
        ),
        migrations.AlterModelOptions(
            name='lesson',
            options={'ordering': ('id',)},
        ),
        migrations.AlterModelOptions(
            name='room',
            options={'ordering': ('id',)},
        ),
        migrations.AlterModelOptions(
            name='teacher',
            options={'ordering': ('id',)},
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='moderators',
        ),
    ]
