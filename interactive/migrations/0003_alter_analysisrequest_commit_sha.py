# Generated by Django 4.0.4 on 2022-05-13 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("interactive", "0002_analysisrequest_commit"),
    ]

    operations = [
        migrations.AlterField(
            model_name="analysisrequest",
            name="commit_sha",
            field=models.CharField(
                max_length=40, null=True, verbose_name="Repo commit SHA"
            ),
        ),
    ]
