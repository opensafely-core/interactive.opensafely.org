# Generated by Django 4.1.4 on 2022-12-15 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("interactive", "0014_require_all_created_at_fields_are_filled"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="is_staff",
            field=models.BooleanField(
                default=False,
                help_text="Designates whether the user can log into the staff area.",
                verbose_name="staff status",
            ),
        ),
    ]
