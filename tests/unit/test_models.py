from datetime import date

import pytest

from interactive.models import (
    AnalysisRequest,
    RegistrationRequest,
    User,
    date_of_last_extract,
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


def test_user_string_repr():
    user = User()
    user.email = "alice@test.com"
    assert str(user) == "alice@test.com"


def test_analysis_request_string_repr():
    analysis = AnalysisRequest()
    analysis.title = "Analysis title"
    analysis.codelist = "Test Codelist"
    assert str(analysis) == "Analysis title (Test Codelist)"


def test_register_interest_string_repr():
    request = RegistrationRequest()
    request.full_name = "Alice"
    request.email = "alice@test.com"
    request.organisation = "The Bennett Institute"
    request.job_title = "Tester"
    assert str(request) == "Alice (alice@test.com), Tester at The Bennett Institute"


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
