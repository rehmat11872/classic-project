# Generated by Django 2.2.10 on 2021-02-14 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='qia_eligible',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
