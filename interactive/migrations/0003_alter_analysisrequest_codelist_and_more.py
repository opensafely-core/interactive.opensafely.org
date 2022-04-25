# Generated by Django 4.0.4 on 2022-04-25 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("interactive", "0002_analysisrequest_codelist"),
    ]

    operations = [
        migrations.AlterField(
            model_name="analysisrequest",
            name="codelist",
            field=models.CharField(max_length=255, verbose_name="Codelist"),
        ),
        migrations.AlterField(
            model_name="analysisrequest",
            name="title",
            field=models.CharField(max_length=100, verbose_name="Analysis title"),
        ),
    ]
