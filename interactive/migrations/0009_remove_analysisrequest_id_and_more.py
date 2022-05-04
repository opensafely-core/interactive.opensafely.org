# Generated by Django 4.0.4 on 2022-05-04 08:44

import timeflake.extensions.django
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("interactive", "0008_analysisrequest_uuid_registrationrequest_uuid"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="analysisrequest",
            name="id",
        ),
        migrations.RemoveField(
            model_name="registrationrequest",
            name="id",
        ),
        migrations.AlterField(
            model_name="analysisrequest",
            name="uuid",
            field=timeflake.extensions.django.TimeflakePrimaryKeyBinary(
                serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="registrationrequest",
            name="uuid",
            field=timeflake.extensions.django.TimeflakePrimaryKeyBinary(
                serialize=False
            ),
        ),
    ]
