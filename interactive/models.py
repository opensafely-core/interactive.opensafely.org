from django.db import models


START_DATE = "2020-01-01"
END_DATE = "2021-12-31"


class RegisterInterest(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="Full name")
    email = models.CharField(max_length=100, verbose_name="Email")
    organisation = models.CharField(max_length=100, verbose_name="Organisation")
    job_title = models.CharField(max_length=100, verbose_name="Job title")


class AnalysisRequest(models.Model):

    user = models.ForeignKey("auth.User", on_delete=models.PROTECT)
    title = models.CharField(max_length=100, verbose_name="Analysis title")
    codelist = models.CharField(max_length=255, verbose_name="Codelist")
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self) -> str:
        return f"{self.title} ({self.codelist})"
