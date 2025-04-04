# Generated by Django 5.1.7 on 2025-03-30 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='physicalreport',
            name='diagnosis_date',
        ),
        migrations.RemoveField(
            model_name='physicalreport',
            name='illness',
        ),
        migrations.RemoveField(
            model_name='physicalreport',
            name='name',
        ),
        migrations.RemoveField(
            model_name='physicalreport',
            name='symptoms',
        ),
        migrations.RemoveField(
            model_name='physicalreport',
            name='symptoms_appeared_date',
        ),
        migrations.AddField(
            model_name='physicalreport',
            name='disease',
            field=models.CharField(choices=[('Mononucleosis (Mono)', 'Mononucleosis (Mono)'), ('HIV & AIDS', 'HIV & AIDS')], default=1, max_length=100),
            preserve_default=False,
        ),
    ]
