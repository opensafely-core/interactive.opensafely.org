from datetime import datetime

from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone

from interactive.models import RegistrationRequest, User

from ..factories import RegistrationRequestFactory


def test_registration_request_response_change_loads_successfully(client, admin_user):
    client.force_login(admin_user)
    request = RegistrationRequestFactory()
    response = client.get(
        reverse("admin:interactive_registrationrequest_change", args=(request.id,))
    )
    assert response.status_code == 200


def test_registration_request_response_change_approved(client, admin_user):
    client.force_login(admin_user)
    request = RegistrationRequestFactory()
    response = client.post(
        reverse("admin:interactive_registrationrequest_change", args=(request.id,)),
        {"_approve-request": True},
        follow=True,
    )
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "has been approved" in str(messages[0])

    saved_request = RegistrationRequest.objects.last()
    assert saved_request.review_status == RegistrationRequest.ReviewStatus.APPROVED
    assert saved_request.reviewed_by == admin_user
    assert saved_request.reviewed_at is not None

    new_user = User.objects.get(email=request.email)
    assert new_user.name == request.full_name
    assert not new_user.is_staff
    assert new_user.is_active


def test_registration_request_response_change_denied(client, admin_user):
    client.force_login(admin_user)
    request = RegistrationRequestFactory()
    response = client.post(
        reverse("admin:interactive_registrationrequest_change", args=(request.id,)),
        {"_deny-request": True},
        follow=True,
    )
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "has been denied" in str(messages[0])

    saved_request = RegistrationRequest.objects.last()
    assert saved_request.review_status == RegistrationRequest.ReviewStatus.DENIED
    assert saved_request.reviewed_by == admin_user
    assert saved_request.reviewed_at is not None


def test_registration_request_response_change_save_does_nothing(client, admin_user):
    client.force_login(admin_user)
    request = RegistrationRequestFactory()
    response = client.post(
        reverse("admin:interactive_registrationrequest_change", args=(request.id,)),
        {},
        follow=True,
    )

    assert response.status_code == 200
    saved_request = RegistrationRequest.objects.last()
    assert saved_request.review_status is None


def test_registration_request_render_change_form_edit_adds_review_status_approved(
    client, admin_user
):
    client.force_login(admin_user)
    request = RegistrationRequestFactory()
    request.review(
        admin_user,
        datetime(2022, 1, 1, tzinfo=timezone.utc),
        RegistrationRequest.ReviewStatus.APPROVED,
    )
    request.save()

    response = client.get(
        reverse("admin:interactive_registrationrequest_change", args=(request.id,))
    )

    assert response.status_code == 200
    assert response.context["is_approved"]


def test_registration_request_render_change_form_edit_adds_review_status_denied(
    client, admin_user
):
    client.force_login(admin_user)
    request = RegistrationRequestFactory()
    request.review(
        admin_user,
        datetime(2022, 1, 1, tzinfo=timezone.utc),
        RegistrationRequest.ReviewStatus.DENIED,
    )
    request.save()

    response = client.get(
        reverse("admin:interactive_registrationrequest_change", args=(request.id,))
    )

    assert response.status_code == 200
    assert not response.context["is_approved"]


def test_registration_request_render_change_form_new_request_not_permitted(
    client, admin_user
):
    client.force_login(admin_user)

    response = client.get(reverse("admin:interactive_registrationrequest_add"))

    assert response.status_code == 403
