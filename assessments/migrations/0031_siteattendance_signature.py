# Generated by Django 2.2.10 on 2021-03-19 08:57

import core.helpers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0030_auto_20210319_1657'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteattendance',
            name='signature',
            field=models.FileField(blank=True, max_length=500, null=True, upload_to=core.helpers.PathAndRename('qaa/signature')),
        ),
    ]
