# Generated by Django 2.2.10 on 2021-04-26 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0049_suggestedassessor_prev_acception'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qlassicassessmentapplication',
            name='ccd_point',
            field=models.FloatField(default=20, null=True, verbose_name='CCD Point'),
        ),
    ]