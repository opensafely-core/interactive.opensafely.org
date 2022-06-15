import django.contrib.auth.admin  # noqa: F401
import django.contrib.auth.models  # noqa: F401
from django.contrib import admin, auth
from django.http import HttpResponseRedirect
from django.utils import timezone

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


@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    change_form_template = "admin/registration_review_form.html"
    list_display = ["full_name", "email", "job_title", "organisation", "review_status"]

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return []  # pragma: no cover

        return [
            "full_name",
            "email",
            "job_title",
            "organisation",
            "review_status",
            "reviewed_at",
            "reviewed_by",
        ]

    def response_change(self, request, obj):
        if "_approve-request" in request.POST:
            obj.review(
                request.user, timezone.now(), RegistrationRequest.ReviewStatus.APPROVED
            )
            obj.save()
            self.message_user(
                request, f"The request for {obj.full_name} has been approved"
            )
            return HttpResponseRedirect(".")
        elif "_deny-request" in request.POST:
            obj.review(
                request.user, timezone.now(), RegistrationRequest.ReviewStatus.DENIED
            )
            obj.save()
            self.message_user(
                request, f"The request for {obj.full_name} has been denied"
            )
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)


@admin.register(AnalysisRequest)
class AnalysisRequestAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "codelist_slug", "start_date", "end_date"]
