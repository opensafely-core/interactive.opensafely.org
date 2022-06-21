# Generated by Django 4.0.5 on 2022-06-20 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("interactive", "0008_registrationrequest_review_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="job_title",
            field=models.CharField(
                blank=True, default="", max_length=100, verbose_name="Job title"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="organisation",
            field=models.CharField(
                blank=True, default="", max_length=100, verbose_name="Organisation"
            ),
        ),
    ]
