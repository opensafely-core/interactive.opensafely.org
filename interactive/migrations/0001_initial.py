import datetime

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("auth", "0002_alter_permission_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "email",
                    models.EmailField(
                        error_messages={
                            "unique": "A user with this email address already exists."
                        },
                        max_length=100,
                        unique=True,
                        verbose_name="email address",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("is_superuser", models.BooleanField(default=False)),
                ("is_staff", models.BooleanField(default=False)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="AnalysisRequest",
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
                (
                    "title",
                    models.CharField(max_length=100, verbose_name="Analysis title"),
                ),
                ("codelist", models.CharField(max_length=255, verbose_name="Codelist")),
                (
                    "end_date",
                    models.DateField(
                        default=datetime.datetime(
                            2022, 4, 26, 10, 16, 51, 91902, tzinfo=utc
                        )
                    ),
                ),
                (
                    "start_date",
                    models.DateField(
                        default=datetime.datetime(
                            2022, 4, 26, 10, 16, 59, 800702, tzinfo=utc
                        )
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        default=1,
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RegistrationRequest",
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
                (
                    "full_name",
                    models.CharField(max_length=100, verbose_name="Full name"),
                ),
                ("email", models.CharField(max_length=100, verbose_name="Email")),
                (
                    "organisation",
                    models.CharField(max_length=100, verbose_name="Organisation"),
                ),
                (
                    "job_title",
                    models.CharField(max_length=100, verbose_name="Job title"),
                ),
            ],
        ),
    ]
