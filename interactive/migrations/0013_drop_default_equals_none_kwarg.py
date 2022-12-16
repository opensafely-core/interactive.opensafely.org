# Generated by Django 4.1.4 on 2022-12-14 14:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("interactive", "0012_drop_all_blank_kwargs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="analysisrequest",
            name="complete_email_sent_at",
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name="registrationrequest",
            name="review_status",
            field=models.TextField(
                choices=[("Approved", "Approved"), ("Denied", "Denied")], null=True
            ),
        ),
        migrations.AlterField(
            model_name="registrationrequest",
            name="reviewed_at",
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name="registrationrequest",
            name="reviewed_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
