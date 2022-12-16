import pytest
from django.conf import settings
from django.http import Http404

from staff.views.registration_requests import (
    RegistrationRequestDetail,
    RegistrationRequestList,
)

from ....factories import RegistrationRequestFactory, UserFactory


def test_registrationrequestdetail_get_success(rf, staff_user):
    registration_request = RegistrationRequestFactory()

    request = rf.get("/")
    request.user = staff_user

    response = RegistrationRequestDetail.as_view()(request, pk=registration_request.pk)

    assert response.status_code == 200
    assert response.context_data["registration_request"] == registration_request


def test_registrationrequestdetail_with_unknown_registration_request(rf, staff_user):
    request = rf.get("/")
    request.user = staff_user

    with pytest.raises(Http404):
        RegistrationRequestDetail.as_view()(request, pk="unknown")


def test_registrationrequestdetail_without_staff_user(rf):
    user = UserFactory()

    request = rf.get("/")
    request.user = UserFactory()

    response = RegistrationRequestDetail.as_view()(request, pk=user.pk)

    assert response.status_code == 302
    assert response.url == f"{settings.LOGIN_URL}?next=/"


def test_registrationrequestlist_find_by_email(rf, staff_user):
    RegistrationRequestFactory(email="test@example.com")
    RegistrationRequestFactory(email="foo@example.com")
    RegistrationRequestFactory(email="bar@opensafely.org")

    request = rf.get("/?q=example")
    request.user = staff_user

    response = RegistrationRequestList.as_view()(request)

    assert response.status_code == 200
    assert len(response.context_data["object_list"]) == 2


def test_registrationrequestlist_find_by_full_name(rf, staff_user):
    RegistrationRequestFactory(full_name="Ben")
    RegistrationRequestFactory(full_name="Ben Goldacre")
    RegistrationRequestFactory(full_name="Seb Bacon")

    request = rf.get("/?q=ben")
    request.user = staff_user

    response = RegistrationRequestList.as_view()(request)

    assert response.status_code == 200
    assert len(response.context_data["object_list"]) == 2


def test_registrationrequestlist_find_by_job_title(rf, staff_user):
    RegistrationRequestFactory(job_title="Clinical researcher")
    RegistrationRequestFactory(job_title="Software engineer")
    RegistrationRequestFactory(job_title="Healthcare researcher")

    request = rf.get("/?q=research")
    request.user = staff_user

    response = RegistrationRequestList.as_view()(request)

    assert response.status_code == 200
    assert len(response.context_data["object_list"]) == 2


def test_registrationrequestlist_find_by_organisation(rf, staff_user):
    RegistrationRequestFactory(organisation="Bennett Institute")
    RegistrationRequestFactory(organisation="DataLab")
    RegistrationRequestFactory(organisation="NHS England")

    request = rf.get("/?q=bennett")
    request.user = staff_user

    response = RegistrationRequestList.as_view()(request)

    assert response.status_code == 200
    assert len(response.context_data["object_list"]) == 1


def test_registrationrequestlist_success(rf, staff_user):
    RegistrationRequestFactory.create_batch(5)

    request = rf.get("/")
    request.user = staff_user

    response = RegistrationRequestList.as_view()(request)
    assert response.status_code == 200
    assert len(response.context_data["object_list"]) == 5
