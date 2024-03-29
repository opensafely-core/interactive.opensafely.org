# Generated by Django 4.1.4 on 2022-12-14 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("interactive", "0016_add_error_message_to_all_timeflake_pks"),
    ]

    operations = [
        migrations.AlterField(
            model_name="analysisrequest",
            name="codelist_name",
            field=models.TextField(verbose_name="Codelist"),
        ),
        migrations.AlterField(
            model_name="analysisrequest",
            name="codelist_slug",
            field=models.TextField(verbose_name="Codelist"),
        ),
        migrations.AlterField(
            model_name="analysisrequest",
            name="commit_sha",
            field=models.TextField(null=True, verbose_name="Repo commit SHA"),
        ),
        migrations.AlterField(
            model_name="analysisrequest",
            name="title",
            field=models.TextField(verbose_name="Analysis title"),
        ),
        migrations.AlterField(
            model_name="registrationrequest",
            name="email",
            field=models.TextField(verbose_name="Email"),
        ),
        migrations.AlterField(
            model_name="registrationrequest",
            name="full_name",
            field=models.TextField(verbose_name="Full name"),
        ),
        migrations.AlterField(
            model_name="registrationrequest",
            name="job_title",
            field=models.TextField(verbose_name="Job title"),
        ),
        migrations.AlterField(
            model_name="registrationrequest",
            name="organisation",
            field=models.TextField(verbose_name="Organisation"),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                error_messages={
                    "unique": "A user with this email address already exists."
                },
                max_length=254,
                unique=True,
                verbose_name="email address",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="job_title",
            field=models.TextField(default="", verbose_name="Job title"),
        ),
        migrations.AlterField(
            model_name="user",
            name="name",
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="user",
            name="organisation",
            field=models.TextField(default="", verbose_name="Organisation"),
        ),
    ]
