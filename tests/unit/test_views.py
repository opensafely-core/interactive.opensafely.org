import timeflake
from django.contrib.messages import get_messages
from django.urls import reverse

from interactive import views
from interactive.models import AnalysisRequest, RegistrationRequest
from tests.factories import AnalysisRequestFactory, UserFactory

from .assertions import assert_difference, assert_no_difference


def test_index(client):
    response = client.get(reverse("home"))
    assert response.status_code == 200


def test_about(client):
    response = client.get(reverse("about"))
    assert response.status_code == 200


def test_login_success(client):
    user = UserFactory()

    response = client.post(
        reverse("login"),
        {"username": user.email, "password": "password!"},
        follow=True,
    )

    # check that our post-login configuration is correct
    assert response.redirect_chain == [("/", 302)]

    # check our success message has been rendered
    assert b"You have successfully logged in" in response.content


def test_login_failure_wrong_username(client):
    response = client.post(
        reverse("login"),
        {"username": "malice@test.com", "password": "password!"},
        follow=True,
    )
    assert b"Please enter a correct email address and password" in response.content
    assert_not_logged_in(client)


def test_login_failure_wrong_password(client):
    user = UserFactory()

    response = client.post(
        reverse("login"),
        {"username": user.email, "password": "wordpass"},
        follow=True,
    )
    assert b"Please enter a correct email address and password" in response.content
    assert_not_logged_in(client)


def test_logout(client):
    user = UserFactory()

    client.force_login(user)
    response = client.post(reverse("logout"), follow=True)
    assert b"You have successfully logged out" in response.content
    assert_not_logged_in(client)


def test_register_interest_get(client):
    response = client.get(reverse("register_interest"))
    assert response.status_code == 200


def test_register_interest_post_success(client, get_slack_messages):
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

    messages = get_slack_messages()
    assert len(messages) == 1
    assert "alice@test.com" in messages[-1]["text"]
    assert "Unit test" in messages[-1]["text"]


def test_register_interest_post_failure_returns_unsaved_form(client, slack_messages):
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


def test_new_analysis_request_get(client, codelists):
    user = UserFactory()

    client.force_login(user)
    response = client.get(reverse("new_analysis_request"))
    assert response.status_code == 200


def test_new_analysis_request_get_not_logged_in(client):
    response = client.get(reverse("new_analysis_request"))
    assert response.status_code == 302


def test_new_analysis_request_post_returns_unsaved_form(
    client, slack_messages, codelists
):
    user = UserFactory()

    client.force_login(user)
    with assert_no_difference(AnalysisRequest.objects.count):
        response = client.post(
            reverse("new_analysis_request"),
            {"title": "", "codelist": "opensafely/systolic-blood-pressure-qof"},
        )

    assert b"Submit" in response.content
    assert slack_messages == []


def test_request_analysis_done_returns_template(client):
    user = UserFactory()
    client.force_login(user)

    response = client.get(reverse("request_analysis_done"))

    assert response.status_code == 200


def test_new_analysis_request_post_not_logged_in(client):
    response = client.post(reverse("new_analysis_request"))
    assert response.status_code == 302


def test_analysis_request_output(client, monkeypatch):
    user = UserFactory()

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


def test_analysis_request_output_not_logged_in(client):
    pk = timeflake.random()
    response = client.get(reverse("request_analysis_output", kwargs={"pk": pk}))
    assert response.status_code == 302


def test_analysis_request_output_not_authorised(client):
    user = UserFactory()

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


def test_analysis_request_email_user_not_authorised(client):
    user = UserFactory()

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


def test_bad_request(rf):
    request = rf.get("/")
    response = views.bad_request(request)
    assert response.status_code == 400
    assert "Bad request" in response.rendered_content


def test_permission_denied(rf):
    request = rf.get("/")
    response = views.permission_denied(request)
    assert response.status_code == 403
    assert "Permission denied" in response.rendered_content


def test_page_not_found(rf):
    request = rf.get("/")
    response = views.page_not_found(request)
    assert response.status_code == 404
    assert "Page not found" in response.rendered_content


def test_server_error(rf):
    request = rf.get("/")
    response = views.server_error(request)
    assert response.status_code == 500
    assert "Server error" in response.rendered_content


def test_csrf_failure(client):
    client.handler.enforce_csrf_checks = True
    response = client.post(reverse("home"), {})
    assert response.status_code == 400
    assert "CSRF Failed" in response.rendered_content


def assert_not_logged_in(client):
    response = client.get(reverse("request_analysis_done"))
    assert response.status_code == 302
