# Generated by Django 2.2.10 on 2021-03-31 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0044_auto_20210331_2345'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='qlassicreporting',
            name='type_of_report',
        ),
        migrations.AddField(
            model_name='qlassicreporting',
            name='report_type',
            field=models.CharField(choices=[('qlassic_score_letter', 'QLASSIC Score Letter'), ('qlassic_certificate', 'QLASSIC Certificate'), ('qlassic_report', 'QLASSIC Report')], max_length=30, null=True),
        ),
    ]
