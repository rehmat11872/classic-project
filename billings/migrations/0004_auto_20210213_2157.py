# Generated by Django 2.2.10 on 2021-02-13 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billings', '0003_auto_20210213_1324'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
