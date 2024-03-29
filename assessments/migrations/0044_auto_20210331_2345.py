# Generated by Django 2.2.10 on 2021-03-31 15:45

import core.helpers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0043_auto_20210331_2307'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='qlassicreporting',
            name='qaa_number',
        ),
        migrations.AddField(
            model_name='qlassicreporting',
            name='approved_by',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='qlassicreporting',
            name='approved_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='qlassicreporting',
            name='qr_file',
            field=models.ImageField(blank=True, null=True, upload_to=core.helpers.PathAndRename('assessment/qr/'), verbose_name='QR File'),
        ),
        migrations.AddField(
            model_name='qlassicreporting',
            name='reviewed_by',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='qlassicreporting',
            name='reviewed_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='qlassicreporting',
            name='verified_by',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='qlassicreporting',
            name='verified_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
