# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0003_project_clone_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coreuser',
            name='user_mobile',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='coreuser',
            name='user_token',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
