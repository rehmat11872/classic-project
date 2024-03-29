# Generated by Django 2.2.10 on 2023-02-13 13:24

import core.helpers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0011_auto_20221223_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='updateinformation',
            name='update_footer_logo',
            field=models.FileField(blank=True, null=True, upload_to=core.helpers.PathAndRename('logo'), validators=[core.helpers.file_size_validator]),
        ),
    ]
