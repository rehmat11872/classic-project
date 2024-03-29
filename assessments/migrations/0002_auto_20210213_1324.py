# Generated by Django 2.2.10 on 2021-02-13 05:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('assessments', '0001_initial'),
        ('projects', '0001_initial'),
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trainings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='workcompletionform',
            name='assessor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.Assessor'),
        ),
        migrations.AddField(
            model_name='workcompletionform',
            name='qaa',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='assessments.QlassicAssessmentApplication'),
        ),
        migrations.AddField(
            model_name='supportingdocuments',
            name='jt',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='trainings.JoinedTraining'),
        ),
        migrations.AddField(
            model_name='supportingdocuments',
            name='qaa',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='assessments.QlassicAssessmentApplication'),
        ),
        migrations.AddField(
            model_name='supportingdocuments',
            name='ra',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='trainings.RoleApplication'),
        ),
        migrations.AddField(
            model_name='suggestedassessor',
            name='assessor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.Assessor'),
        ),
        migrations.AddField(
            model_name='suggestedassessor',
            name='qaa',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='assessments.QlassicAssessmentApplication'),
        ),
        migrations.AddField(
            model_name='subcomponentresultdocument',
            name='sub_component_result',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='assessments.SubComponentResult'),
        ),
        migrations.AddField(
            model_name='subcomponentresult',
            name='assessment_data',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='assessments.AssessmentData'),
        ),
        migrations.AddField(
            model_name='subcomponentresult',
            name='sub_component',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='assessments.SubComponent'),
        ),
        migrations.AddField(
            model_name='subcomponent',
            name='component',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='assessments.Component'),
        ),
        migrations.AddField(
            model_name='siteattendance',
            name='qaa',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='assessments.QlassicAssessmentApplication'),
        ),
        migrations.AddField(
            model_name='qlassicreporting',
            name='ad',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='assessments.AssessmentData'),
        ),
        migrations.AddField(
            model_name='qlassicreporting',
            name='qaa',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='assessments.QlassicAssessmentApplication'),
        ),
        migrations.AddField(
            model_name='qlassicassessmentapplication',
            name='pi',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.ProjectInfo'),
        ),
        migrations.AddField(
            model_name='qlassicassessmentapplication',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='element',
            name='sub_component',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='assessments.SubComponent'),
        ),
        migrations.AddField(
            model_name='defectgroupresult',
            name='assessment_data',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='assessments.AssessmentData'),
        ),
        migrations.AddField(
            model_name='defectgroupresult',
            name='defect_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='assessments.DefectGroup'),
        ),
        migrations.AddField(
            model_name='defectgroup',
            name='element',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='assessments.Element'),
        ),
        migrations.AddField(
            model_name='assignedassessor',
            name='ad',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='assessments.AssessmentData'),
        ),
        migrations.AddField(
            model_name='assignedassessor',
            name='assessor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.Assessor'),
        ),
        migrations.AddField(
            model_name='assessmentdata',
            name='assessor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.Assessor'),
        ),
        migrations.AddField(
            model_name='assessmentdata',
            name='qaa',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='assessments.QlassicAssessmentApplication'),
        ),
        migrations.AddField(
            model_name='assessmentdata',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
