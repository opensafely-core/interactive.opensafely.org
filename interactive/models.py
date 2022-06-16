from calendar import WEDNESDAY
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from furl import furl
from timeflake.extensions.django import TimeflakePrimaryKeyBinary

from .emails import send_welcome_email


def date_of_last_extract():
    # The cutoff for TPP's data extract is the Wednesday of the previous week
    # We usually receive the data on a Tuesday, so if today is a Tuesday or
    # Wednesday the cutoff is last Wednesday, otherwise it's the Wednesday before.
    today = date.today()
    offset = (today.weekday() - WEDNESDAY) % 7
    weeks = 1
    if offset == 6:
        weeks = 0
    return today - timedelta(days=offset, weeks=weeks)


START_DATE = "2019-09-01"
END_DATE = date_of_last_extract().strftime("%Y-%m-%d")


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        if not email:
            raise ValueError("The Email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    objects = CustomUserManager()

    id = TimeflakePrimaryKeyBinary()  # noqa: A003
    name = models.CharField(max_length=100)
    email = models.EmailField(
        verbose_name="email address",
        max_length=100,
        unique=True,
        error_messages={"unique": "A user with this email address already exists."},
    )
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text=(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.name

    def __str__(self):
        return self.email

    def get_password_reset_url(self, uid, token):
        return reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})


class RegistrationRequest(models.Model):
    id = TimeflakePrimaryKeyBinary()  # noqa: A003
    full_name = models.CharField(max_length=100, verbose_name="Full name")
    email = models.CharField(max_length=100, verbose_name="Email")
    organisation = models.CharField(max_length=100, verbose_name="Organisation")
    job_title = models.CharField(max_length=100, verbose_name="Job title")

    def __str__(self) -> str:
        return (
            f"{self.full_name} ({self.email}), {self.job_title} at {self.organisation}"
        )


class AnalysisRequest(models.Model):
    id = TimeflakePrimaryKeyBinary()  # noqa: A003
    user = models.ForeignKey("interactive.User", on_delete=models.PROTECT)
    title = models.CharField(max_length=100, verbose_name="Analysis title")
    codelist_slug = models.CharField(max_length=255, verbose_name="Codelist")
    codelist_name = models.CharField(max_length=255, verbose_name="Codelist")
    start_date = models.DateField()
    end_date = models.DateField()
    commit_sha = models.CharField(
        max_length=40, verbose_name="Repo commit SHA", null=True
    )
    complete_email_sent_at = models.DateTimeField(default=None, blank=True, null=True)
    job_request_url = models.TextField(default="")

    def __str__(self) -> str:
        return f"{self.title} ({self.codelist_slug})"

    @property
    def created_by(self):
        return self.user.email

    def visible_to(self, user):
        return self.user == user or user.is_staff

    def get_absolute_url(self):
        # Currently only used by django admin
        return self.get_output_url()  # pragma: no cover

    def get_output_url(self):
        return reverse("request_analysis_output", kwargs={"pk": self.id})


@receiver(post_save, sender=User)
def send_email(sender, instance, created, **kwargs):
    if not created:
        return

    uid = urlsafe_base64_encode(force_bytes(instance.pk))
    token = PasswordResetTokenGenerator().make_token(instance)
    reset_url = furl(settings.BASE_URL) / instance.get_password_reset_url(uid, token)

    context = {
        "name": instance.name,
        "url": reset_url,
    }

    send_welcome_email(instance.email, context)
