# Generated by Django 2.2.10 on 2021-03-17 04:21

import core.helpers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0019_auto_20210317_1209'),
    ]

    operations = [
        migrations.AddField(
            model_name='sampleresult',
            name='assessors',
            field=models.CharField(blank=True, max_length=4000, null=True),
        ),
        migrations.AlterField(
            model_name='sampleresult',
            name='photo_1',
            field=models.FileField(blank=True, max_length=500, null=True, upload_to=core.helpers.PathAndRename('qaa/photos')),
        ),
        migrations.AlterField(
            model_name='sampleresult',
            name='photo_2',
            field=models.FileField(blank=True, max_length=500, null=True, upload_to=core.helpers.PathAndRename('qaa/photos')),
        ),
        migrations.AlterField(
            model_name='sampleresult',
            name='photo_3',
            field=models.FileField(blank=True, max_length=500, null=True, upload_to=core.helpers.PathAndRename('qaa/photos')),
        ),
        migrations.AlterField(
            model_name='sampleresult',
            name='photo_4',
            field=models.FileField(blank=True, max_length=500, null=True, upload_to=core.helpers.PathAndRename('qaa/photos')),
        ),
    ]
