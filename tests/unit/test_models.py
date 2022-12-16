from datetime import date

import pytest
from django.urls import reverse

from interactive.models import Org, User, date_of_last_extract
from tests.factories import (
    AnalysisRequestFactory,
    OrgFactory,
    OrgMembershipFactory,
    RegistrationRequestFactory,
    UserFactory,
)


def test_user_manager_create_user_successfully():
    user = User.objects.create_user("alice@test.com", "password")
    assert str(user) == "alice@test.com"


def test_user_manager_create_user_missing_email_raises_error():
    with pytest.raises(ValueError):
        User.objects.create_user("", "password")


def test_user_manager_create_superuser_with_correct_permissions():
    user = User.objects.create_superuser("admin@test.com", "password")
    assert user.is_active
    assert user.is_staff
    assert user.is_superuser


def test_user_get_full_name_returns_name():
    user = User.objects.create_user("alice@test.com", "password", name="Alice Test")
    assert user.get_full_name() == "Alice Test"


def test_user_get_staff_url():
    user = UserFactory()

    url = user.get_staff_url()

    assert url == reverse("staff:user-detail", kwargs={"pk": user.pk})


def test_user_string_repr():
    user = User()
    user.email = "alice@test.com"
    assert str(user) == "alice@test.com"


def test_analysis_request_get_codelist_url():
    analysis = AnalysisRequestFactory(codelist_slug="testing/foo")

    url = analysis.get_codelist_url()

    assert url == "https://www.opencodelists.org/codelist/testing/foo"


def test_analysis_request_get_staff_url():
    analysis = AnalysisRequestFactory()

    url = analysis.get_staff_url()

    assert url == reverse("staff:analysis-request-detail", kwargs={"pk": analysis.pk})


def test_analysis_request_string_repr():
    analysis = AnalysisRequestFactory(
        title="Analysis title",
        codelist_slug="Test Codelist",
    )

    assert str(analysis) == "Analysis title (Test Codelist)"


def test_org_slugification():
    # test with the Org model here because the factory sets a slug for us by
    # default and calls save when creating the object so one is set anyway
    org = Org(name="Test Org")
    assert org.slug == ""

    org.save()
    assert org.slug == "test-org"


def test_org_string_repr():
    org = OrgFactory(name="Test Org")

    assert str(org) == "Test Org"


def test_orgmembership_string_repr():
    org = OrgFactory(name="Test Org")
    user = UserFactory(email="test@example.com")
    membership = OrgMembershipFactory(org=org, user=user)

    assert str(membership) == "test@example.com | Test Org"


def test_register_interest_string_repr():
    request = RegistrationRequestFactory(
        full_name="Alice",
        email="alice@test.com",
        organisation="The Bennett Institute",
        job_title="Tester",
    )

    assert str(request) == "Alice (alice@test.com), Tester at The Bennett Institute"


def test_registration_request_get_staff_url():
    registration = RegistrationRequestFactory()

    url = registration.get_staff_url()

    assert url == reverse(
        "staff:registration-request-detail", kwargs={"pk": registration.pk}
    )


def test_date_of_last_extract_sun_to_previous_wed(freezer):
    freezer.move_to("2022-05-15")
    assert date_of_last_extract() == date(2022, 5, 4)


def test_date_of_last_extract_mon_to_previous_wed(freezer):
    freezer.move_to("2022-05-16")
    assert date_of_last_extract() == date(2022, 5, 4)


def test_date_of_last_extract_tues_to_previous_wed(freezer):
    freezer.move_to("2022-05-17")
    assert date_of_last_extract() == date(2022, 5, 11)


def test_date_of_last_extract_wed_to_previous_wed(freezer):
    freezer.move_to("2022-05-18")
    assert date_of_last_extract() == date(2022, 5, 11)


def test_date_of_last_extract_thurs_to_previous_wed(freezer):
    freezer.move_to("2022-05-19")
    assert date_of_last_extract() == date(2022, 5, 11)
