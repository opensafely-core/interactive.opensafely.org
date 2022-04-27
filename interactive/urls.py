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
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
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

urlpatterns = [
    path("", views.index, name="home"),
    path("request-analysis/", views.new_analysis_request, name="new_analysis_request"),
    path("admin/", admin.site.urls),
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
    path("password-reset/", include(password_reset_urls)),
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + "favicon.ico")),
    path("robots.txt", RedirectView.as_view(url=settings.STATIC_URL + "robots.txt")),
]

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
