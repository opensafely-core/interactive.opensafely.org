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
from django.utils.text import slugify
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
    id = TimeflakePrimaryKeyBinary(  # noqa: A003
        error_messages={"invalid": "Invalid timeflake id"}
    )

    orgs = models.ManyToManyField(
        "Org",
        related_name="members",
        through="OrgMembership",
        through_fields=["user", "org"],
    )
    projects = models.ManyToManyField(
        "Project",
        related_name="members",
        through="ProjectMembership",
        through_fields=["user", "project"],
    )

    name = models.TextField()
    email = models.EmailField(
        verbose_name="email address",
        unique=True,
        error_messages={"unique": "A user with this email address already exists."},
    )
    organisation = models.TextField(verbose_name="Organisation", default="")
    job_title = models.TextField(verbose_name="Job title", default="")

    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into the staff area.",
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

    objects = CustomUserManager()

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

    id = TimeflakePrimaryKeyBinary(  # noqa: A003
        error_messages={"invalid": "Invalid timeflake id"}
    )

    full_name = models.TextField(verbose_name="Full name")
    email = models.TextField(verbose_name="Email")
    organisation = models.TextField(verbose_name="Organisation")
    job_title = models.TextField(verbose_name="Job title")

    reviewed_at = models.DateTimeField(null=True)
    reviewed_by = models.ForeignKey(
        "interactive.User",
        null=True,
        on_delete=models.PROTECT,
        related_name="reviewed_registration_requests",
    )
    review_status = models.TextField(choices=ReviewStatus.choices, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return (
            f"{self.full_name} ({self.email}), {self.job_title} at {self.organisation}"
        )

    def get_staff_url(self):
        return reverse("staff:registration-request-detail", kwargs={"pk": self.pk})


class AnalysisRequest(models.Model):
    id = TimeflakePrimaryKeyBinary(  # noqa: A003
        error_messages={"invalid": "Invalid timeflake id"}
    )

    title = models.TextField(verbose_name="Analysis title")
    codelist_slug = models.TextField(verbose_name="Codelist")
    codelist_name = models.TextField(verbose_name="Codelist")
    start_date = models.DateField()
    end_date = models.DateField()
    commit_sha = models.TextField(verbose_name="Repo commit SHA", null=True)
    complete_email_sent_at = models.DateTimeField(null=True)
    job_request_url = models.TextField(default="")

    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        "interactive.User",
        on_delete=models.PROTECT,
        related_name="analysis_requests",
    )

    def __str__(self) -> str:
        return f"{self.title} ({self.codelist_slug})"

    def visible_to(self, user):
        return self.created_by == user or user.is_staff

    def get_codelist_url(self):
        oc = furl("https://www.opencodelists.org/codelist/")
        return (oc / self.codelist_slug).url

    def get_output_url(self):
        return reverse("request_analysis_output", kwargs={"pk": self.id})

    def get_staff_url(self):
        return reverse("staff:analysis-request-detail", kwargs={"pk": self.pk})

    def get_github_commit_url(self):
        return f"{settings.WORKSPACE_REPO}/tree/{self.id}"


class Org(models.Model):
    """An Organisation using the platform"""

    created_by = models.ForeignKey(
        "User",
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_orgs",
    )

    name = models.TextField(unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(default="", blank=True)
    logo = models.TextField(default="", blank=True)
    logo_file = models.FileField(upload_to="org_logos/", null=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Organisation"

    def __str__(self):
        return self.name

    def get_staff_edit_url(self):
        return reverse("staff:org-edit", kwargs={"slug": self.slug})

    def get_staff_url(self):
        return reverse("staff:org-detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        return super().save(*args, **kwargs)


class OrgMembership(models.Model):
    """Membership of an Organistion for a User"""

    created_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        related_name="created_org_memberships",
        null=True,
    )
    org = models.ForeignKey(
        "Org",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="org_memberships",
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ["org", "user"]

    def __str__(self):
        return f"{self.user.email} | {self.org.name}"


class Project(models.Model):
    class Statuses(models.TextChoices):
        ONGOING = "ongoing", "Ongoing"
        POSTPONED = "postponed", "Postponed"
        RETIRED = "retired", "Retired"

        # we expect these to go away and be replaced with first class support
        # for linking out to papers and reports but for now we need to track
        # them so they're statuses.
        ONGOING_LINKED = "ongoing-and-linked", "Ongoing - paper/report linked"
        COMPLETED_LINKED = "completed-and-linked", "Completed - paper/report linked"
        COMPLETED_AWAITING = (
            "completed-and-awaiting",
            "Completed - awaiting paper/report",
        )

    org = models.ForeignKey(
        "Org",
        on_delete=models.CASCADE,
        related_name="projects",
    )

    name = models.TextField(unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    number = models.IntegerField()

    status = models.TextField(choices=Statuses.choices, default=Statuses.ONGOING)
    status_description = models.TextField(default="", blank=True)

    purpose = models.TextField()
    summary = models.TextField()
    application_url = models.TextField()

    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        "User",
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_projects",
    )

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        "User",
        on_delete=models.PROTECT,
        related_name="projects_updated",
        null=True,
    )

    def __str__(self):
        return f"{self.org.name} | {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        return super().save(*args, **kwargs)

    @property
    def title(self):
        return f"{self.number} - {self.name}"


class ProjectMembership(models.Model):
    """Membership of a Project for a User"""

    created_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        related_name="created_project_memberships",
        null=True,
    )
    project = models.ForeignKey(
        "Project",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ["project", "user"]

    def __str__(self):
        return f"{self.user.email} | {self.project.title}"


@receiver(post_save, sender=User)
def send_email(sender, instance, created, **kwargs):
    if not created:
        return

    send_welcome_email(instance.email, instance)
