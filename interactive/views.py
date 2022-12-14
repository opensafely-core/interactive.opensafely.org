from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.generic import FormView

from services import jobserver, opencodelists

from .emails import send_analysis_request_email
from .forms import AnalysisRequestForm, RegistrationRequestForm
from .models import END_DATE, START_DATE, AnalysisRequest
from .notifications import notify_registration_request_submitted


class RegisterInterest(FormView):
    form_class = RegistrationRequestForm
    template_name = "interactive/register_interest.html"

    def form_valid(self, form):
        form.save()
        notify_registration_request_submitted(
            form.instance.full_name,
            form.instance.job_title,
            form.instance.organisation,
            form.instance.email,
        )
        return redirect("register_interest_done")


@login_required
def new_analysis_request(request):
    codelists = opencodelists.fetch()

    def codelists_to_choices(codelists):
        yield ("", "---")
        for codelist in codelists:
            yield (codelist["slug"], codelist["name"])

    codelist_choices = list(codelists_to_choices(codelists))

    form = AnalysisRequestForm(codelists=codelist_choices)

    ctx = {
        "form": form,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "codelists": codelists,
    }
    return TemplateResponse(request, "interactive/new_analysis_request.html", ctx)


@login_required
def new_analysis_request_done(request):
    return TemplateResponse(request, "interactive/new_analysis_request_done.html")


@login_required
def analysis_request_output(request, pk):
    analysis_request = AnalysisRequest.objects.get(pk=pk)
    if not analysis_request.visible_to(request.user):
        raise PermissionDenied

    context = {"analysis": analysis_request}
    if outputs := jobserver.fetch_release(str(analysis_request.id)):
        context.update(outputs)

    return TemplateResponse(
        request,
        "interactive/analysis_request_output.html",
        context,
    )


@login_required
def analysis_request_email(request, pk):
    if not request.user.is_staff:
        return permission_denied(request)

    analysis_request = get_object_or_404(AnalysisRequest, pk=pk)
    send_analysis_request_email(analysis_request.created_by.email, analysis_request)

    analysis_request.complete_email_sent_at = timezone.now()
    analysis_request.save()

    messages.success(request, f"Email sent to {analysis_request.created_by.email}")
    return redirect("request_analysis_output", pk)


#
# Authentication
#
class LoginView(DjangoLoginView):
    def form_valid(self, form):
        messages.success(
            self.request, "You have successfully logged in.", extra_tags="autohide"
        )
        return super().form_valid(form)


class LogoutView(DjangoLogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(
            request, "You have successfully logged out.", extra_tags="autohide"
        )
        return super().dispatch(request, *args, **kwargs)


#
# Error pages
#
def bad_request(request, exception=None):
    return TemplateResponse(
        request,
        "error.html",
        status=400,
        context={
            "error_code": "400",
            "error_name": "Bad request",
            "error_message": "An error has occurred displaying this page.",
        },
    )


def permission_denied(request, exception=None):
    return TemplateResponse(
        request,
        "error.html",
        status=403,
        context={
            "error_code": "403",
            "error_name": "Permission denied",
            "error_message": "You do not have permission to access this page.",
        },
    )


def page_not_found(request, exception=None):
    return TemplateResponse(
        request,
        "error.html",
        status=404,
        context={
            "error_code": "404",
            "error_name": "Page not found",
            "error_message": "Please check the URL in the address bar.",
        },
    )


def server_error(request):
    return TemplateResponse(
        request,
        "error.html",
        status=500,
        context={
            "error_code": "500",
            "error_name": "Server error",
            "error_message": "An error has occurred displaying this page.",
        },
    )


def csrf_failure(request, reason=""):
    return TemplateResponse(
        request,
        "error.html",
        status=400,
        context={
            "error_code": "CSRF",
            "error_name": "CSRF Failed",
            "error_message": "The form was not able to submit.",
        },
    )
