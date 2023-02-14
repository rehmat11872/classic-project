# Generated by Django 2.2.10 on 2021-03-15 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0011_auto_20210309_1515'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='component',
            name='weightage',
        ),
        migrations.AddField(
            model_name='component',
            name='weightage_a',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True, verbose_name='Weightage A'),
        ),
        migrations.AddField(
            model_name='component',
            name='weightage_b',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True, verbose_name='Weightage B'),
        ),
        migrations.AddField(
            model_name='component',
            name='weightage_c',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True, verbose_name='Weightage C'),
        ),
        migrations.AddField(
            model_name='component',
            name='weightage_d',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True, verbose_name='Weightage D'),
        ),
        migrations.AlterField(
            model_name='component',
            name='type',
            field=models.IntegerField(choices=[(1, 'Type 1'), (2, 'Type 2')], default=1, null=True),
        ),
        migrations.AlterField(
            model_name='element',
            name='weightage',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True, verbose_name='Weightage (%)'),
        ),
        migrations.AlterField(
            model_name='subcomponent',
            name='type',
            field=models.IntegerField(choices=[(0, 'No Type'), (2, 'Type 2'), (3, 'Type 3')], default=3, null=True),
        ),
    ]