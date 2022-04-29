from django.contrib import admin

# the module name is app_name.models
from interactive.models import AnalysisRequest, RegistrationRequest


# Register your models to admin site, then you can add, edit, delete and search your models in Django admin site.
admin.site.register(RegistrationRequest)
admin.site.register(AnalysisRequest)
