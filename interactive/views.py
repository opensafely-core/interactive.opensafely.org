from django.contrib import messages
from django.contrib.auth.views import LogoutView
from django.shortcuts import render


def index(request):
    return render(request, "index.html")


def bad_request(request, exception=None):
    return render(request, "400.html", status=400)


def permission_denied(request, exception=None):
    return render(request, "403.html", status=403)


def page_not_found(request, exception=None):
    return render(request, "404.html", status=404)


def server_error(request):
    return render(request, "500.html", status=500)


class LogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, "You have successfully logged out.")
        return super().dispatch(request, *args, **kwargs)
