# Generated by Django 4.0.4 on 2022-05-13 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("interactive", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="analysisrequest",
            name="commit_sha",
            field=models.CharField(
                max_length=40, null=True, verbose_name="Repo commit"
            ),
        ),
    ]
