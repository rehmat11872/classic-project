# Generated by Django 2.2.10 on 2021-02-14 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainings', '0003_auto_20210214_1254'),
    ]

    operations = [
        migrations.AddField(
            model_name='roleapplication',
            name='accreditation_duration_month',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='roleapplication',
            name='accreditation_duration_year',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
