from django import forms

from .models import AnalysisRequest


class AnalysisRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        codelists = kwargs.pop("codelists", None)
        super().__init__(*args, **kwargs)
        if codelists:
            self.fields["codelist"] = forms.ChoiceField(choices=codelists)

    class Meta:
        model = AnalysisRequest
        fields = ["title", "codelist"]
