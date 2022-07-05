from django import forms

from .models import RegistrationRequest


class RegistrationRequestForm(forms.ModelForm):
    class Meta:
        model = RegistrationRequest
        fields = ["full_name", "email", "organisation", "job_title"]


class AnalysisRequestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        codelists = kwargs.pop("codelists")

        super().__init__(*args, **kwargs)

        self.fields["codelist_slug"] = forms.ChoiceField(choices=codelists)
