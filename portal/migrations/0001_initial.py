# Generated by Django 2.2.10 on 2021-02-13 05:24

import core.helpers
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255, null=True)),
                ('announcement', models.TextField(max_length=3000, null=True)),
                ('publish', models.CharField(choices=[('publish', 'Publish'), ('do_not_publish', 'Do not publish')], max_length=50, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(max_length=50, null=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('modified_by', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LetterTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255, null=True)),
                ('template_file', models.FileField(blank=True, null=True, upload_to=core.helpers.PathAndRename('templates'))),
                ('is_active', models.BooleanField(default=True, verbose_name='Use this template now?')),
                ('template_type', models.CharField(choices=[('qlassic_score_letter', 'QLASSIC Score letter'), ('qlassic_certificate', 'QLASSIC Certificate'), ('qlassic_report', 'QLASSIC Report'), ('training_certificate', 'Training Certificate'), ('trainer_interview_letter', 'Trainer Interview Letter'), ('qca_interview_letter', 'QCA Interview Letter'), ('trainer_reject_letter', 'Trainer Reject Letter'), ('qca_reject_letter', 'QCA Reject Letter'), ('attendance_sheet', 'Attendance Sheet'), ('accreditation_letter', 'Accreditation Letter'), ('accreditation_certificate', 'Accreditation Certificate')], max_length=150, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(max_length=50, null=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('modified_by', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LetterTemplateConfiguration',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('slug', models.CharField(max_length=255, null=True)),
                ('value', models.TextField(blank=True, max_length=3000, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(max_length=50, null=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('modified_by', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255, null=True)),
                ('publication', models.TextField(max_length=3000, null=True)),
                ('file', models.FileField(max_length=255, null=True, upload_to=core.helpers.PathAndRename('publications'))),
                ('publish', models.CharField(choices=[('publish', 'Publish'), ('do_not_publish', 'Do not publish')], max_length=50, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(max_length=50, null=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('modified_by', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Training',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name_of_training', models.CharField(max_length=255, null=True, verbose_name='Training Name')),
                ('from_date', models.DateField(null=True, verbose_name='Start Date')),
                ('to_date', models.DateField(null=True, verbose_name='End Date')),
                ('available_seat', models.IntegerField(null=True, verbose_name='Available Seat')),
                ('passing_mark', models.DecimalField(decimal_places=2, max_digits=6, null=True, verbose_name='Passing Mark')),
                ('ccd_point', models.DecimalField(decimal_places=2, max_digits=6, null=True, verbose_name='CCD Point')),
                ('fee', models.DecimalField(decimal_places=2, max_digits=8, null=True, verbose_name='Fees')),
                ('address1', models.CharField(max_length=100, null=True)),
                ('address2', models.CharField(max_length=100, null=True)),
                ('postcode', models.CharField(max_length=10, null=True, verbose_name='Postal code')),
                ('city', models.CharField(max_length=50, null=True)),
                ('state', models.CharField(choices=[('MELAKA', 'MELAKA'), ('JOHOR', 'JOHOR'), ('NEGERI SEMBILAN', 'NEGERI SEMBILAN'), ('PAHANG', 'PAHANG'), ('TERENGGANU', 'TERENGGANU'), ('KELANTAN', 'KELANTAN'), ('PERAK', 'PERAK'), ('PERLIS', 'PERLIS'), ('KEDAH', 'KEDAH'), ('SELANGOR', 'SELANGOR'), ('WILAYAH PERSEKUTUAN KUALA LUMPUR', 'KUALA LUMPUR'), ('SABAH', 'SABAH'), ('SARAWAK', 'SARAWAK'), ('PULAU PINANG', 'PULAU PINANG')], max_length=50, null=True)),
                ('publish', models.BooleanField(default=False, verbose_name='Published?')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(max_length=50, null=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('modified_by', models.CharField(max_length=50, null=True)),
            ],
        ),
    ]
