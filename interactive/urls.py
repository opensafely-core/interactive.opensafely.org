"""interactive URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from interactive import views


password_reset_urls = [
    path("", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path(
        "done",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "complete",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]

request_analysis_urls = [
    path("", views.new_analysis_request, name="new_analysis_request"),
    path(
        "done",
        views.new_analysis_request_done,
        name="request_analysis_done",
    ),
    path(
        "<str:pk>/output",
        views.analysis_request_output,
        name="request_analysis_output",
    ),
    path(
        "<str:pk>/email",
        views.analysis_request_email,
        name="request_analysis_email",
    ),
]

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("about", TemplateView.as_view(template_name="about.html"), name="about"),
    path(
        "register-interest/", views.RegisterInterest.as_view(), name="register_interest"
    ),
    path(
        "register-interest/done",
        TemplateView.as_view(template_name="interactive/register_interest_done.html"),
        name="register_interest_done",
    ),
    path(
        "login/",
        views.LoginView.as_view(redirect_authenticated_user=True),
        name="login",
    ),
    path(
        "logout/",
        views.LogoutView.as_view(),
        name="logout",
    ),
    path("request-analysis/", include(request_analysis_urls)),
    path("password-reset/", include(password_reset_urls)),
    path("staff/", include("staff.urls", namespace="staff")),
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + "favicon.ico")),
    path("robots.txt", RedirectView.as_view(url=settings.STATIC_URL + "robots.txt")),
    path("__debug__/", include("debug_toolbar.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = views.bad_request
handler403 = views.permission_denied
handler404 = views.page_not_found
handler500 = views.server_error

# Allow the error pages to be previewed when running in debug mode
if settings.DEBUG:
    urlpatterns += (  # pragma: no cover
        path("400", views.bad_request, name="bad_request"),
        path("403", views.permission_denied, name="permission_denied"),
        path("404", views.page_not_found, name="page_not_found"),
        path("500", views.server_error, name="server_error"),
    )
