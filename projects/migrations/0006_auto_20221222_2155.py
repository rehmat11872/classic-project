# Generated by Django 2.2.10 on 2022-12-22 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_projectinfo_project_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectinfo',
            name='project_status',
        ),
        migrations.AddField(
            model_name='contractor',
            name='project_status',
            field=models.CharField(choices=[('reviewed', 'Reviewed'), ('verified', 'Verified'), ('rejected', 'Rejected'), ('is_being_assessed', 'is being assessed'), ('completed', 'Completed')], max_length=50, null=True),
        ),
    ]