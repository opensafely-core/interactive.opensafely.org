from django.db import models


class AnalysisRequest(models.Model):

    title = models.CharField(max_length=100, verbose_name="Analysis title")
    codelist = models.CharField(max_length=255, verbose_name="Codelist")

    def __str__(self) -> str:
        return f"{self.title} ({self.codelist})"
