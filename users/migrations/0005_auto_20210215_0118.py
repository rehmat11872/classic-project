# Generated by Django 2.2.10 on 2021-02-14 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20210215_0118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='qia_status',
            field=models.CharField(choices=[('', 'Not Eligible'), ('need_review', 'Need Review'), ('need_payment', 'Need Payment'), ('approved', 'Approved')], default='', max_length=50, null=True),
        ),
    ]
