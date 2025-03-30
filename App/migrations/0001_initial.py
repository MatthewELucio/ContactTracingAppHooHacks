# Generated by Django 5.1.7 on 2025-03-30 04:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AirborneReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("symptoms", models.CharField(max_length=255)),
                ("symptoms_appeared_date", models.DateTimeField()),
                ("diagnosis_date", models.DateTimeField(blank=True, null=True)),
                (
                    "illness",
                    models.CharField(
                        choices=[
                            ("cc", "Commonn Cold"),
                            ("flu", "Influenza (Flu)"),
                            ("other", "Other"),
                        ],
                        max_length=100,
                    ),
                ),
                ("was_diagnosed", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Disease",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "disease_type",
                    models.CharField(
                        choices=[("air", "Air"), ("physical", "Physical")],
                        help_text="Type of disease (air or physical)",
                        max_length=20,
                    ),
                ),
                ("learn_link", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="PhysicalReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("symptoms_appeared_date", models.DateTimeField()),
                ("diagnosis_date", models.DateTimeField(blank=True, null=True)),
                ("symptoms", models.TextField()),
                (
                    "illness",
                    models.CharField(
                        choices=[
                            ("mono", "Mono"),
                            ("hfm", "Hand-Foot-Mouth Disease"),
                            ("other", "Other"),
                        ],
                        max_length=100,
                    ),
                ),
                ("was_diagnosed", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Infection",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("infected_at", models.DateTimeField(auto_now_add=True)),
                (
                    "disease",
                    models.ForeignKey(
                        help_text="The disease associated with this infection",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="infections",
                        to="App.disease",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="The user who is infected",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="infections",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LocationHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
                ("recorded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="location_histories",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RelevantLocation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="relevant_locations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
