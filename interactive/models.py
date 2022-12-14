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
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
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
    organisation = models.CharField(
        max_length=100, verbose_name="Organisation", default=""
    )
    job_title = models.CharField(max_length=100, verbose_name="Job title", default="")

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

    created_at = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.name

    def __str__(self):
        return self.email

    def get_password_reset_url(self):
        uid = urlsafe_base64_encode(force_bytes(self.pk))
        token = PasswordResetTokenGenerator().make_token(self)

        return reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})

    def get_staff_url(self):
        return reverse("staff:user-detail", kwargs={"pk": self.pk})


class RegistrationRequest(models.Model):
    class ReviewStatus(models.TextChoices):
        APPROVED = "Approved"
        DENIED = "Denied"

    id = TimeflakePrimaryKeyBinary()  # noqa: A003
    full_name = models.CharField(max_length=100, verbose_name="Full name")
    email = models.CharField(max_length=100, verbose_name="Email")
    organisation = models.CharField(max_length=100, verbose_name="Organisation")
    job_title = models.CharField(max_length=100, verbose_name="Job title")

    reviewed_at = models.DateTimeField(null=True)
    reviewed_by = models.ForeignKey(
        "interactive.User",
        null=True,
        on_delete=models.PROTECT,
    )
    review_status = models.TextField(choices=ReviewStatus.choices, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return (
            f"{self.full_name} ({self.email}), {self.job_title} at {self.organisation}"
        )


class AnalysisRequest(models.Model):
    id = TimeflakePrimaryKeyBinary(  # noqa: A003
        error_messages={"invalid": "Invalid timeflake id"}
    )

    user = models.ForeignKey("interactive.User", on_delete=models.PROTECT)
    title = models.CharField(max_length=100, verbose_name="Analysis title")
    codelist_slug = models.CharField(max_length=255, verbose_name="Codelist")
    codelist_name = models.CharField(max_length=255, verbose_name="Codelist")
    start_date = models.DateField()
    end_date = models.DateField()
    commit_sha = models.CharField(
        max_length=40, verbose_name="Repo commit SHA", null=True
    )
    complete_email_sent_at = models.DateTimeField(null=True)
    job_request_url = models.TextField(default="")

    created_at = models.DateTimeField(default=timezone.now)

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

    def get_staff_url(self):
        return reverse("staff:analysis-request-detail", kwargs={"pk": self.pk})

    def get_github_commit_url(self):
        return f"{settings.WORKSPACE_REPO}/tree/{self.id}"


@receiver(post_save, sender=User)
def send_email(sender, instance, created, **kwargs):
    if not created:
        return

    send_welcome_email(instance.email, instance)
