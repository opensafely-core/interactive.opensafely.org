"""
Django settings for interactive project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
import re
from pathlib import Path

from environs import Env, EnvError

from services import sentry
from services.logging import logging_config_dict


env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
try:
    SECRET_KEY = env.str("SECRET_KEY")
except EnvError:
    raise Exception(
        "SECRET_KEY environment variable not found. Have the environment variables been set correctly?"
    )

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", False)

BASE_URL = env.str("BASE_URL", default="http://localhost:8000")

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "interactive",
    "whitenoise.runserver_nostatic",
    "anymail",
    "django.contrib.staticfiles",
    "django_extensions",
    "django_vite",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "interactive.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "interactive.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": env.dj_db_url(
        "DATABASE_URL", "postgres://user:pass@localhost:5432/interactive"
    )
}

# Use our custom user class
AUTH_USER_MODEL = "interactive.User"

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Logging
LOGGING = logging_config_dict

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "assets", "dist"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"

DJANGO_VITE_ASSETS_PATH = "/static/bundle/"
DJANGO_VITE_STATIC_URL_PREFIX = "bundle"
DJANGO_VITE_DEV_MODE = env.bool("DJANGO_VITE_DEV_MODE", default=False)
DJANGO_VITE_MANIFEST_PATH = os.path.join(
    BASE_DIR, "staticfiles", "bundle", "manifest.json"
)

# Vite generates files with 8 hash digits
# http://whitenoise.evans.io/en/stable/django.html#WHITENOISE_IMMUTABLE_FILE_TEST


def immutable_file_test(path, url):
    # Match filename with 12 hex digits before the extension
    # e.g. app.db8f2edc0c8a.js
    return re.match(r"^.+\.[0-9a-f]{8,12}\..+$", url)


WHITENOISE_IMMUTABLE_FILE_TEST = immutable_file_test

# Insert Whitenoise Middleware.
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = (
    "br",
    "bz2",
    "css.map",
    "flv",
    "gif",
    "gz",
    "ico",
    "jpeg",
    "jpg",
    "js.map",
    "json",
    "map",
    "png",
    "svg",
    "swf",
    "tbz",
    "tgz",
    "webmanifest",
    "webp",
    "woff",
    "woff2",
    "xz",
    "zip",
)

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
LOGIN_URL = "/login"

# Security
# https://docs.djangoproject.com/en/4.0/ref/settings/#core-settings
# https://docs.djangoproject.com/en/4.0/ref/settings/#sessions
CSRF_COOKIE_SECURE = not DEBUG
CSRF_FAILURE_VIEW = "interactive.views.csrf_failure"
CSRF_TRUSTED_ORIGINS = [BASE_URL]
SESSION_COOKIE_SECURE = not DEBUG

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR / "sent_emails"

# THIRD PARTY SETTINGS

sentry.initialise_sentry()

# Anymail
ANYMAIL = {
    "MAILGUN_API_KEY": env.str("MAILGUN_API_KEY", default=None),
    "MAILGUN_API_URL": "https://api.eu.mailgun.net/v3",
    "MAILGUN_SENDER_DOMAIN": "mg.interactive.opensafely.org",
}
EMAIL_BACKEND = env.str(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = "OpenSAFELY Interactive <noreply@mg.interactive.opensafely.org>"
SERVER_EMAIL = "OpenSAFELY Interactive <noreply@mg.interactive.opensafely.org>"


# Application settings
GITHUB_TOKEN = env.str("GITHUB_TOKEN")
