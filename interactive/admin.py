import django.contrib.auth.admin  # noqa: F401
import django.contrib.auth.models  # noqa: F401
from django.contrib import admin, auth

# the module name is app_name.models
from interactive.models import AnalysisRequest, RegistrationRequest, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ["name", "email"]
    list_display = ["name", "email"]
    search_fields = ["email", "name"]


# Remove standard admin
# admin.site.unregister(auth.models.User)
admin.site.unregister(auth.models.Group)

# Register your models to admin site, then you can add, edit, delete and search your models in Django admin site.
admin.site.register(RegistrationRequest)


@admin.register(AnalysisRequest)
class AnalysisRequestAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "codelist_slug", "start_date", "end_date"]
