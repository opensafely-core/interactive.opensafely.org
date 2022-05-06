from django.test.client import RequestFactory
from django.urls import reverse

from interactive import views
from interactive.models import AnalysisRequest, RegistrationRequest

from .assertions import assert_difference, assert_no_difference


def test_index(client):
    response = client.get(reverse("home"))
    assert response.status_code == 200


def test_login_success(client, user):
    response = client.post(
        reverse("login"),
        {"username": "alice@test.com", "password": "password"},
        follow=True,
    )
    assert b"You have successfully logged in" in response.content
    assert_logged_in(client, user)


def test_login_failure_wrong_username(client, user):
    response = client.post(
        reverse("login"), {"username": "malice", "password": "password"}, follow=True
    )
    assert b"Please enter a correct email address and password" in response.content
    assert_not_logged_in(client, user)


def test_login_failure_wrong_password(client, user):
    response = client.post(
        reverse("login"),
        {"username": "alice@test.com", "password": "wordpass"},
        follow=True,
    )
    assert b"Please enter a correct email address and password" in response.content
    assert_not_logged_in(client, user)


def test_logout(client, user):
    client.force_login(user)
    response = client.get(reverse("logout"), follow=True)
    assert b"You have successfully logged out" in response.content
    assert_not_logged_in(client, user)


def test_register_interest_get(client):
    response = client.get(reverse("register_interest"))
    assert response.status_code == 200


def test_register_interest_post_success(client, user, mocker):
    mocker.patch(
        "interactive.views.notify_registration_request_submitted", autospec=True
    )
    with assert_difference(RegistrationRequest.objects.count, expected_difference=1):
        response = client.post(
            reverse("register_interest"),
            {
                "full_name": "Alice",
                "job_title": "Software engineer",
                "email": "alice@test.com",
                "organisation": "Unit test",
            },
            follow=True,
        )
    assert b"Your registration is being processed" in response.content

    request = RegistrationRequest.objects.last()
    assert request.full_name == "Alice"


def test_register_interest_post_success_calls_notify(client, user, mocker):
    mock_notify = mocker.patch(
        "interactive.views.notify_registration_request_submitted", autospec=True
    )

    client.post(
        reverse("register_interest"),
        {
            "full_name": "Alice",
            "job_title": "Software engineer",
            "email": "alice@test.com",
            "organisation": "Unit test",
        },
        follow=True,
    )

    mock_notify.assert_called_once()


def test_register_interest_post_failure_returns_unsaved_form(client, user):
    with assert_no_difference(RegistrationRequest.objects.count):
        response = client.post(
            reverse("register_interest"),
            {
                "full_name": "Alice",
                "email": "",
            },
        )

    assert b"Register your interest" in response.content
    assert b"Submit" in response.content


def test_register_interest_post_failure_doesnt_call_notify(client, user, mocker):
    mock_notify = mocker.patch(
        "interactive.views.notify_registration_request_submitted", autospec=True
    )

    client.post(
        reverse("register_interest"),
        {
            "full_name": "Alice",
            "email": "",
        },
    )

    mock_notify.assert_not_called()


def test_new_analysis_request_get(client, user):
    client.force_login(user)
    response = client.get(reverse("new_analysis_request"))
    assert response.status_code == 200


def test_new_analysis_request_get_not_logged_in(client):
    response = client.get(reverse("new_analysis_request"))
    assert response.status_code == 302


def test_new_analysis_request_post_success(client, user, mocker):
    mocker.patch("interactive.views.notify_analysis_request_submitted", autospec=True)
    client.force_login(user)
    with assert_difference(AnalysisRequest.objects.count, expected_difference=1):
        response = client.post(
            reverse("new_analysis_request"),
            {
                "title": "An Analysis",
                "codelist": "opensafely/systolic-blood-pressure-qof",
            },
            follow=True,
        )
    assert b"Your request is being processed" in response.content

    request = AnalysisRequest.objects.last()
    assert request.user == user
    assert request.title == "An Analysis"
    assert request.codelist == "opensafely/systolic-blood-pressure-qof"
    assert str(request.start_date) == "2020-01-01"
    assert str(request.end_date) == "2021-12-31"


def test_new_analysis_request_post_success_calls_notify(client, user, mocker):
    mock_notify = mocker.patch(
        "interactive.views.notify_analysis_request_submitted", autospec=True
    )

    client.force_login(user)
    client.post(
        reverse("new_analysis_request"),
        {
            "title": "An Analysis",
            "codelist": "opensafely/systolic-blood-pressure-qof",
        },
        follow=True,
    )

    mock_notify.assert_called_once()


def test_new_analysis_request_post_failure_returns_unsaved_form(client, user):
    client.force_login(user)
    with assert_no_difference(AnalysisRequest.objects.count):
        response = client.post(
            reverse("new_analysis_request"),
            {"title": "", "codelist": "opensafely/systolic-blood-pressure-qof"},
        )

    assert b"Analysis title" in response.content
    assert b"Submit" in response.content


def test_new_analysis_request_post_failure_with_invalid_codelist(client, user):
    client.force_login(user)
    with assert_no_difference(AnalysisRequest.objects.count):
        response = client.post(
            reverse("new_analysis_request"),
            {"title": "Sneaky study", "codelist": "sneaky-user/my-codelist"},
        )

    assert b"Analysis title" in response.content
    assert b"Submit" in response.content


def test_new_analysis_request_post_failure_doesnt_call_notify(client, user, mocker):
    mock_notify = mocker.patch(
        "interactive.views.notify_analysis_request_submitted", autospec=True
    )

    client.force_login(user)
    client.post(
        reverse("new_analysis_request"),
        {"title": "", "codelist": "opensafely/systolic-blood-pressure-qof"},
    )

    mock_notify.assert_not_called()


def test_new_analysis_request_post_not_logged_in(client, user):
    response = client.post(reverse("new_analysis_request"))
    assert response.status_code == 302


def test_bad_request():
    factory = RequestFactory()
    request = factory.get("/")
    response = views.bad_request(request)
    assert response.status_code == 400
    assert b"Bad request" in response.content


def test_permission_denied():
    factory = RequestFactory()
    request = factory.get("/")
    response = views.permission_denied(request)
    assert response.status_code == 403
    assert b"Permission denied" in response.content


def test_page_not_found():
    factory = RequestFactory()
    request = factory.get("/")
    response = views.page_not_found(request)
    assert response.status_code == 404
    assert b"Page not found" in response.content


def test_server_error():
    factory = RequestFactory()
    request = factory.get("/")
    response = views.server_error(request)
    assert response.status_code == 500
    assert b"Server error" in response.content


def test_csrf_failure(client):
    client.handler.enforce_csrf_checks = True
    response = client.post(reverse("home"), {})
    assert response.status_code == 400
    assert b"CSRF Failed" in response.content


def assert_logged_in(client, user):
    response = client.get(reverse("new_analysis_request"))
    assert response.status_code == 200


def assert_not_logged_in(client, user):
    response = client.get(reverse("new_analysis_request"))
    assert response.status_code == 302
