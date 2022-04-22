from django.db import models


class AnalysisRequest(models.Model):

    title = models.CharField(max_length=100)
    codelist = models.CharField(max_length=255)
