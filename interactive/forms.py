from django.forms import modelform_factory

from .models import AnalysisRequest


AnalysisRequestForm = modelform_factory(AnalysisRequest, fields=["title"])
