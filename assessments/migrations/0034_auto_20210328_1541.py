# Generated by Django 2.2.10 on 2021-03-28 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0033_auto_20210324_1241'),
    ]

    operations = [
        migrations.AddField(
            model_name='syncresult',
            name='sync_complete',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='qlassicassessmentapplication',
            name='application_status',
            field=models.CharField(blank=True, choices=[('pending', 'Pending'), ('reviewed', 'Reviewed'), ('verified', 'Verified'), ('rejected', 'Rejected'), ('rejected_amendment', 'Rejected (With Amendment)'), ('need_payment', 'Need Payment'), ('assessor_assign', 'Assessor Assigned'), ('confirm', 'Confirm'), ('in_progress', 'In-Progress'), ('completed', 'Completed'), ('approved', 'Approved')], max_length=50, null=True),
        ),
    ]
