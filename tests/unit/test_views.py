import timeflake
from django.contrib.messages import get_messages
from django.test.client import RequestFactory
from django.urls import reverse

from interactive import views
from interactive.models import (
    AnalysisRequest,
    RegistrationRequest,
    date_of_last_extract,
)
from tests.factories import AnalysisRequestFactory

from .assertions import assert_difference, assert_no_difference


def test_index(client):
    response = client.get(reverse("home"))
    assert response.status_code == 200


def test_about(client):
    response = client.get(reverse("about"))
    assert response.status_code == 200


def test_login_success(client, user):
    response = client.post(
        reverse("login"),
        {"username": user.email, "password": "password!"},
        follow=True,
    )
    assert b"You have successfully logged in" in response.content
    assert_logged_in(client, user)


def test_login_failure_wrong_username(client, user):
    response = client.post(
        reverse("login"),
        {"username": "malice@test.com", "password": "password!"},
        follow=True,
    )
    assert b"Please enter a correct email address and password" in response.content
    assert_not_logged_in(client, user)


def test_login_failure_wrong_password(client, user):
    response = client.post(
        reverse("login"),
        {"username": user.email, "password": "wordpass"},
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


def test_register_interest_post_success(client, user, slack_messages):
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
    assert "alice@test.com" in slack_messages[-1].text
    assert "Unit test" in slack_messages[-1].text


def test_register_interest_post_failure_returns_unsaved_form(
    client, user, slack_messages
):
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
    assert slack_messages == []


def test_new_analysis_request_get(client, user, codelists):
    client.force_login(user)
    response = client.get(reverse("new_analysis_request"))
    assert response.status_code == 200


def test_new_analysis_request_get_not_logged_in(client):
    response = client.get(reverse("new_analysis_request"))
    assert response.status_code == 302


def test_new_analysis_request_post_success(
    client,
    user,
    slack_messages,
    codelists,
    add_codelist_response,
    submit_job_request,
    create_output_checker_issue,
    workspace_repo,
):
    client.force_login(user)
    codelist_slug = "opensafely/systolic-blood-pressure-qof/v1"
    codelist_name = "Systolic blood pressure QoF"
    add_codelist_response(codelist_slug, codelist_name)

    response = client.post(
        reverse("new_analysis_request"),
        {"codelist_slug": "opensafely/systolic-blood-pressure-qof/v1"},
        follow=True,
    )
    assert response.status_code == 200

    # success should redirect elsewhere
    assert response.redirect_chain == [
        (reverse("request_analysis_done"), 302)
    ], response.redirect_chain

    assert b"Your request is being processed" in response.content

    # check we created the correct number of AnalysisRequests, if we have more
    # we either a bug in the view or leaky tests (also a bug)
    assert AnalysisRequest.objects.count() == 1

    request = AnalysisRequest.objects.first()
    assert request.user == user
    assert request.title == codelist_name
    assert request.codelist_slug == codelist_slug
    assert request.codelist_name == codelist_name
    assert request.job_request_url == "test-url"
    assert str(request.start_date) == "2019-09-01"
    assert str(request.end_date) == date_of_last_extract().strftime("%Y-%m-%d")

    assert len(slack_messages) == 2
    analysis_msg, output_msg = slack_messages

    assert user.email in analysis_msg.text
    assert "opensafely/systolic-blood-pressure-qof/v1" in analysis_msg.text


def test_new_analysis_request_post_failure_returns_unsaved_form(
    client, user, slack_messages, codelists
):
    client.force_login(user)
    with assert_no_difference(AnalysisRequest.objects.count):
        response = client.post(
            reverse("new_analysis_request"),
            {"title": "", "codelist": "opensafely/systolic-blood-pressure-qof"},
        )

    assert b"Submit" in response.content
    assert slack_messages == []


def test_new_analysis_request_post_failure_with_invalid_codelist(
    client, user, slack_messages, codelists
):
    client.force_login(user)
    with assert_no_difference(AnalysisRequest.objects.count):
        response = client.post(
            reverse("new_analysis_request"),
            {"title": "Sneaky study", "codelist": "sneaky-user/my-codelist"},
        )

    assert b"Submit" in response.content
    assert slack_messages == []


def test_new_analysis_request_post_not_logged_in(client, user):
    response = client.post(reverse("new_analysis_request"))
    assert response.status_code == 302


def test_analysis_request_output(client, user, monkeypatch):
    def release_outputs(analysis_request_id):
        return {"deciles_chart": ""}

    monkeypatch.setattr(views.jobserver, "fetch_release", release_outputs)

    client.force_login(user)
    analysis_request = AnalysisRequestFactory(user=user)

    response = client.get(
        reverse("request_analysis_output", kwargs={"pk": analysis_request.id})
    )

    assert response.status_code == 200
    assert "deciles_chart" in response.context


def test_analysis_request_output_not_logged_in(client, user):
    pk = timeflake.random()
    response = client.get(reverse("request_analysis_output", kwargs={"pk": pk}))
    assert response.status_code == 302


def test_analysis_request_output_not_authorised(client, user):
    client.force_login(user)
    analysis_request = AnalysisRequestFactory()
    response = client.get(
        reverse("request_analysis_output", kwargs={"pk": analysis_request.id})
    )
    assert response.status_code == 403


def test_analysis_request_output_admin_can_view(client, admin_user, monkeypatch):
    monkeypatch.setattr(views.jobserver, "fetch_release", lambda x: {})

    client.force_login(admin_user)
    analysis_request = AnalysisRequestFactory()

    response = client.get(
        reverse("request_analysis_output", kwargs={"pk": analysis_request.id})
    )

    assert response.status_code == 200


def test_analysis_request_email_admin_can_view(client, admin_user):
    client.force_login(admin_user)
    analysis_request = AnalysisRequestFactory()

    response = client.get(
        reverse("request_analysis_email", kwargs={"pk": analysis_request.id})
    )

    assert response.status_code == 302
    assert response.url == reverse(
        "request_analysis_output", kwargs={"pk": analysis_request.id}
    )

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]).startswith("Email sent")


def test_analysis_request_email_user_not_authorised(client, user):
    client.force_login(user)
    analysis_request = AnalysisRequestFactory()

    response = client.get(
        reverse("request_analysis_email", kwargs={"pk": analysis_request.id})
    )

    assert response.status_code == 403
    assert b"Permission denied" in response.content


def test_analysis_request_email_user_not_logged_in(client):
    analysis_request = AnalysisRequestFactory()

    response = client.get(
        reverse("request_analysis_email", kwargs={"pk": analysis_request.id})
    )

    assert response.status_code == 302
    assert response.url.startswith("/login")


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
    response = client.get(reverse("request_analysis_done"))
    assert response.status_code == 200


def assert_not_logged_in(client, user):
    response = client.get(reverse("request_analysis_done"))
    assert response.status_code == 302
