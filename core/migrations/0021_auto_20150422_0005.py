# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_collaboration_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collaboration',
            name='rate',
        ),
        migrations.RemoveField(
            model_name='project',
            name='rate',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='rate',
        ),
    ]
