from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .notifications import send_welcome_email


START_DATE = "2020-01-01"
END_DATE = "2021-12-31"


class UserManager(BaseUserManager):
    """
    Custom User Model Manager

    This builds on top Django's BaseUserManager to add the methods required to
    make createsuperuser work.
    """

    def create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The Email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and save an Admin with the given email and password."""
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    objects = UserManager()

    name = models.CharField(max_length=100)
    email = models.EmailField(
        verbose_name="email address",
        max_length=100,
        unique=True,
        error_messages={"unique": "A user with this email address already exists."},
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def __str__(self):
        return self.email


class RegistrationRequest(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="Full name")
    email = models.CharField(max_length=100, verbose_name="Email")
    organisation = models.CharField(max_length=100, verbose_name="Organisation")
    job_title = models.CharField(max_length=100, verbose_name="Job title")

    def __str__(self) -> str:
        return (
            f"{self.full_name} ({self.email}), {self.job_title} at {self.organisation}"
        )


class AnalysisRequest(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    title = models.CharField(max_length=100, verbose_name="Analysis title")
    codelist = models.CharField(max_length=255, verbose_name="Codelist")
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self) -> str:
        return f"{self.title} ({self.codelist})"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def send_email(sender, instance, created, **kwargs):
    if not created:
        return

    send_welcome_email(instance.name, instance.email)
