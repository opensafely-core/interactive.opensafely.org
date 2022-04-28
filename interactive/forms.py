from django import forms

from .models import END_DATE, START_DATE, AnalysisRequest, RegistrationRequest


class RegistrationRequestForm(forms.ModelForm):
    class Meta:
        model = RegistrationRequest
        fields = ["full_name", "email", "organisation", "job_title"]


class AnalysisRequestForm(forms.ModelForm):
    class Meta:
        model = AnalysisRequest
        fields = ["title", "codelist"]

    def __init__(self, *args, **kwargs):
        codelists = kwargs.pop("codelists", None)
        super().__init__(*args, **kwargs)
        if codelists:
            self.fields["codelist"] = forms.ChoiceField(choices=codelists)

    def save(self, user):
        self.instance.start_date = START_DATE
        self.instance.end_date = END_DATE
        self.instance.user = user
        super().save()
