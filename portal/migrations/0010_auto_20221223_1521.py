# Generated by Django 2.2.10 on 2022-12-23 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0009_updateinformation_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='updateinformation',
            name='update_logo',
            field=models.ImageField(blank=True, null=True, upload_to='update_logo'),
        ),
    ]
