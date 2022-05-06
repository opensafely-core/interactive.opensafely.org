from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.shortcuts import redirect, render
from environs import Env

from services import opencodelists

from .forms import AnalysisRequestForm, RegistrationRequestForm
from .models import END_DATE, START_DATE
from .notifications import (
    notify_analysis_request_submitted,
    notify_registration_request_submitted,
)


env = Env()


def index(request):
    return render(request, "index.html")


def register_interest(request):
    if request.method == "POST":
        form = RegistrationRequestForm(request.POST)
        if form.is_valid():
            form.save()
            notify_registration_request_submitted(
                form.instance.full_name,
                form.instance.job_title,
                form.instance.organisation,
                form.instance.email,
            )
            return redirect("register_interest_done")
    else:
        form = RegistrationRequestForm()
    return render(request, "interactive/register_interest.html", {"form": form})


def register_interest_done(request):
    return render(request, "interactive/register_interest_done.html")


@login_required
def new_analysis_request(request):
    codelists = [("", "---")] + opencodelists.fetch()
    if request.method == "POST":
        form = AnalysisRequestForm(request.POST, codelists=codelists)
        if form.is_valid():
            form.save(user=request.user)
            notify_analysis_request_submitted(
                form.instance.title, form.instance.codelist, request.user.email
            )
            return redirect("request_analysis_done")
    else:
        form = AnalysisRequestForm(codelists=codelists)

    ctx = {
        "form": form,
        "start_date": START_DATE,
        "end_date": END_DATE,
    }
    return render(request, "interactive/new_analysis_request.html", ctx)


@login_required
def new_analysis_request_done(request):
    return render(request, "interactive/new_analysis_request_done.html")


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
    return render(
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
    return render(
        request,
        "error.html",
        status=403,
        context={
            "error_code": "403",
            "error_name": "Permission denied",
            "error_message": "You do not have access to this page.",
        },
    )


def page_not_found(request, exception=None):
    return render(
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
    return render(
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
    return render(
        request,
        "error.html",
        status=400,
        context={
            "error_code": "CSRF",
            "error_name": "CSRF Failed",
            "error_message": "The form was not able to submit.",
        },
    )
