# Generated by Django 2.2.10 on 2021-04-21 00:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0048_auto_20210408_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='suggestedassessor',
            name='prev_acception',
            field=models.CharField(blank=True, choices=[('accept', 'Accept'), ('reject', 'Reject'), ('pending', 'Wait For Respond')], max_length=10, null=True),
        ),
    ]