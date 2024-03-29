# Generated by Django 2.2.10 on 2021-02-20 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0005_auto_20210219_2316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qlassicassessmentapplication',
            name='application_status',
            field=models.CharField(blank=True, choices=[('pending', 'Pending'), ('reviewed', 'Reviewed'), ('verified', 'Verified'), ('rejected', 'Rejected'), ('rejected_amendment', 'Rejected (With Amendment)'), ('need_payment', 'Need Payment'), ('paid', 'Paid'), ('assessor_assign', 'Assessor Assigned'), ('confirm', 'Confirm'), ('in_progress', 'In-Progress'), ('completed', 'Completed'), ('approved', 'Approved')], max_length=50, null=True),
        ),
    ]
