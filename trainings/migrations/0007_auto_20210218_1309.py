# Generated by Django 2.2.10 on 2021-02-18 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainings', '0006_auto_20210214_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='training',
            name='state',
            field=models.CharField(choices=[('MELAKA', 'MELAKA'), ('JOHOR', 'JOHOR'), ('NEGERI SEMBILAN', 'NEGERI SEMBILAN'), ('PAHANG', 'PAHANG'), ('TERENGGANU', 'TERENGGANU'), ('KELANTAN', 'KELANTAN'), ('PERAK', 'PERAK'), ('PERLIS', 'PERLIS'), ('KEDAH', 'KEDAH'), ('SELANGOR', 'SELANGOR'), ('WILAYAH PERSEKUTUAN KUALA LUMPUR', 'WP KUALA LUMPUR'), ('WILAYAH PERSEKUTUAN LABUAN', 'WP LABUAN'), ('WILAYAH PERSEKUTUAN PUTRAJAYA', 'WP PUTRAJAYA'), ('SABAH', 'SABAH'), ('SARAWAK', 'SARAWAK'), ('PULAU PINANG', 'PULAU PINANG')], max_length=255, null=True),
        ),
    ]
