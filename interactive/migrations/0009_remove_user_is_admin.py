# Generated by Django 4.0.4 on 2022-05-04 09:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("interactive", "0008_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="is_admin",
        ),
    ]