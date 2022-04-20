from django.urls import reverse


def test_index(client):
    response = client.get(reverse("home"))
    assert response.status_code == 200


def test_login_success(client, user):
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


def test_bad_request(client):
    response = client.get(reverse("bad_request"))
    assert response.status_code == 400
    assert b"Bad request"


def test_permission_denied(client):
    response = client.get(reverse("permission_denied"))
    assert response.status_code == 403
    assert b"Permission denied"


def test_page_not_found(client):
    response = client.get(reverse("page_not_found"))
    assert response.status_code == 404
    assert b"Page not found"


def test_server_error(client):
    response = client.get(reverse("server_error"))
    assert response.status_code == 500
    assert b"Server error"


def test_csrf_failure(client):
    client.handler.enforce_csrf_checks = True
    response = client.post(reverse("home"), {})
    assert response.status_code == 400
    assert b"CSRF Failed"


def assert_logged_in(client, user):
    response = client.get("/protected/")
    assert response.status_code == 200


def assert_not_logged_in(client, user):
    response = client.get("/protected/")
    assert response.status_code == 302
