# Generated by Django 2.2 on 2021-08-02 03:52

import core.helpers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.AlterField(
            model_name='qlassicreporting',
            name='report_file',
            field=models.FileField(blank=True, null=True, upload_to=core.helpers.PathAndRename('assessment/report/'), verbose_name='Report File'),
        ),
    ]
