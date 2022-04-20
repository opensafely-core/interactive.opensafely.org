from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import AnalysisRequestForm


def index(request):
    return render(request, "index.html")


# This view only exists to support testing that logging in and out actually work, and
# should be removed once we have a real view to test with.
@login_required
def protected(request):
    return render(request, "index.html")


@login_required
def new_analysis_request(request):
    if request.method == "POST":
        form = AnalysisRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Request submitted successfully")
            return redirect(reverse("home"))
    else:
        form = AnalysisRequestForm()

    return render(request, "interactive/new_analysis_request.html", {"form": form})


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
