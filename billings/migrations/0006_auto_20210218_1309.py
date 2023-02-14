# Generated by Django 2.2.10 on 2021-02-18 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billings', '0005_auto_20210213_2159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claimapplication',
            name='state_from',
            field=models.CharField(choices=[('MELAKA', 'MELAKA'), ('JOHOR', 'JOHOR'), ('NEGERI SEMBILAN', 'NEGERI SEMBILAN'), ('PAHANG', 'PAHANG'), ('TERENGGANU', 'TERENGGANU'), ('KELANTAN', 'KELANTAN'), ('PERAK', 'PERAK'), ('PERLIS', 'PERLIS'), ('KEDAH', 'KEDAH'), ('SELANGOR', 'SELANGOR'), ('WILAYAH PERSEKUTUAN KUALA LUMPUR', 'WP KUALA LUMPUR'), ('WILAYAH PERSEKUTUAN LABUAN', 'WP LABUAN'), ('WILAYAH PERSEKUTUAN PUTRAJAYA', 'WP PUTRAJAYA'), ('SABAH', 'SABAH'), ('SARAWAK', 'SARAWAK'), ('PULAU PINANG', 'PULAU PINANG')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='claimapplication',
            name='state_to',
            field=models.CharField(choices=[('MELAKA', 'MELAKA'), ('JOHOR', 'JOHOR'), ('NEGERI SEMBILAN', 'NEGERI SEMBILAN'), ('PAHANG', 'PAHANG'), ('TERENGGANU', 'TERENGGANU'), ('KELANTAN', 'KELANTAN'), ('PERAK', 'PERAK'), ('PERLIS', 'PERLIS'), ('KEDAH', 'KEDAH'), ('SELANGOR', 'SELANGOR'), ('WILAYAH PERSEKUTUAN KUALA LUMPUR', 'WP KUALA LUMPUR'), ('WILAYAH PERSEKUTUAN LABUAN', 'WP LABUAN'), ('WILAYAH PERSEKUTUAN PUTRAJAYA', 'WP PUTRAJAYA'), ('SABAH', 'SABAH'), ('SARAWAK', 'SARAWAK'), ('PULAU PINANG', 'PULAU PINANG')], max_length=50, null=True),
        ),
    ]