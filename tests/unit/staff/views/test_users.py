import pytest
from django.conf import settings
from django.http import Http404

from interactive.utils import set_from_qs
from staff.views.users import UserDetail, UserList

from ....factories import AnalysisRequestFactory, UserFactory


def test_userdetail_get_success(rf, staff_user):
    user = UserFactory()
    AnalysisRequestFactory(user=user)

    request = rf.get("/")
    request.user = staff_user

    response = UserDetail.as_view()(request, pk=user.pk)

    assert response.status_code == 200

    assert set_from_qs(response.context_data["analysis_requests"]) == set_from_qs(
        user.analysisrequest_set.all()
    )
    assert response.context_data["user"] == user


def test_userdetail_post_success(rf, staff_user):
    user = UserFactory(
        name="Ben",
        email="example@example.com",
        organisation="Bennett",
        job_title="Professor",
        is_staff=False,
        is_active=False,
    )

    data = {
        "name": "test",
        "email": "test@example.com",
        "organisation": "test",
        "job_title": "test",
        "is_active": False,
        "is_staff": True,
    }
    request = rf.post("/", data)
    request.user = staff_user

    response = UserDetail.as_view()(request, pk=user.pk)

    assert response.status_code == 302, response.context_data["form"].errors
    assert response.url == user.get_staff_url()

    user.refresh_from_db()
    assert user.email == "test@example.com"
    assert user.name == "test"
    assert user.is_staff
    assert not user.is_active


def test_userdetail_with_unknown_user(rf, staff_user):
    request = rf.get("/")
    request.user = staff_user

    with pytest.raises(Http404):
        UserDetail.as_view()(request, pk="unknown")


def test_userdetail_without_staff_user(rf):
    user = UserFactory()

    request = rf.get("/")
    request.user = UserFactory()

    response = UserDetail.as_view()(request, pk=user.pk)

    assert response.status_code == 302
    assert response.url == f"{settings.LOGIN_URL}?next=/"


def test_userlist_find_by_username(rf, staff_user):
    UserFactory(name="ben")
    UserFactory(name="ben g")
    UserFactory(name="seb")

    request = rf.get("/?q=ben")
    request.user = staff_user

    response = UserList.as_view()(request)

    assert response.status_code == 200

    assert len(response.context_data["object_list"]) == 2


def test_userlist_success(rf, staff_user):
    UserFactory.create_batch(5)

    request = rf.get("/")
    request.user = staff_user

    response = UserList.as_view()(request)

    assert response.status_code == 200
    # the staff_user fixture creates a User object as well as the 5 we
    # created in the batch call above
    assert len(response.context_data["object_list"]) == 6
