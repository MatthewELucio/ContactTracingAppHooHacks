# Generated by Django 5.1.7 on 2025-03-30 03:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0005_notification'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='physicalreport',
            name='diagnosis_date',
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
        migrations.RemoveField(
            model_name='physicalreport',
            name='was_diagnosed',
        ),
        migrations.AddField(
            model_name='physicalreport',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='physical_reports', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='physicalreport',
            name='illness',
            field=models.CharField(max_length=100),
        ),
        migrations.CreateModel(
            name='ReportPerson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='persons', to='App.physicalreport')),
            ],
        ),
    ]
