# Generated by Django 2.2.10 on 2021-03-31 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0040_auto_20210331_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='qlassicassessmentapplication',
            name='ccd_point',
            field=models.FloatField(blank=True, null=True, verbose_name='CCD Point'),
        ),
    ]