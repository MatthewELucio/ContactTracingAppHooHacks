# Generated by Django 5.1.7 on 2025-03-30 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0004_alter_physicalreport_disease'),
    ]

    operations = [
        migrations.AlterField(
            model_name='physicalreport',
            name='disease',
            field=models.CharField(choices=[], max_length=100),
        ),
    ]
