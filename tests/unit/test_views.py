from django.test.client import RequestFactory
from django.urls import reverse

from interactive import views
from interactive.models import AnalysisRequest

from .assertions import assert_difference, assert_no_difference


def test_index(client):
    response = client.get(reverse("home"))
    assert response.status_code == 200


def test_login_success(client, user, mock_codelists_response):
    response = client.post(
        reverse("login"), {"username": "alice", "password": "password"}, follow=True
    )
    assert b"You have successfully logged in" in response.content
    assert_logged_in(client, user)


def test_login_failure_wrong_username(client, user):
    response = client.post(
        reverse("login"), {"username": "malice", "password": "password"}, follow=True
    )
    assert b"Please enter a correct username and password" in response.content
    assert_not_logged_in(client, user)


def test_login_failure_wrong_password(client, user):
    response = client.post(
        reverse("login"), {"username": "alice", "password": "wordpass"}, follow=True
    )
    assert b"Please enter a correct username and password" in response.content
    assert_not_logged_in(client, user)


def test_logout(client, user):
    client.force_login(user)
    response = client.get(reverse("logout"), follow=True)
    assert b"You have successfully logged out" in response.content
    assert_not_logged_in(client, user)


def test_new_analysis_request_get(client, user, mock_codelists_response):
    client.force_login(user)
    response = client.get(reverse("new_analysis_request"))
    assert response.status_code == 200


def test_new_analysis_request_get_not_logged_in(client, user):
    response = client.get(reverse("new_analysis_request"))
    assert response.status_code == 302


def test_new_analysis_request_post_success(client, user):
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
    assert b"Request submitted successfully" in response.content


def test_new_analysis_request_post_failure(client, user):
    client.force_login(user)
    with assert_no_difference(AnalysisRequest.objects.count):
        response = client.post(
            reverse("new_analysis_request"),
            {"title": "", "codelist": "opensafely/systolic-blood-pressure-qof"},
        )
    assert b"This field is required" in response.content


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
