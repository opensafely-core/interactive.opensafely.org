import pytest
from django.conf import settings
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import Http404

from interactive.models import Org
from interactive.utils import set_from_qs
from staff.views.orgs import OrgCreate, OrgDetail, OrgEdit, OrgList, OrgRemoveMember

from ....factories import OrgFactory, OrgMembershipFactory, UserFactory


def test_orgcreate_get_success(rf, staff_user):
    request = rf.get("/")
    request.user = staff_user

    response = OrgCreate.as_view()(request)

    assert response.status_code == 200


def test_orgcreate_post_success(rf, staff_user):
    request = rf.post("/", {"name": "A New Org"})
    request.user = staff_user

    response = OrgCreate.as_view()(request)

    assert response.status_code == 302

    orgs = Org.objects.all()
    assert len(orgs) == 1

    org = orgs.first()
    assert org.name == "A New Org"
    assert org.created_by == staff_user
    assert response.url == org.get_staff_url()


def test_orgdetail_get_success(rf, staff_user):
    org = OrgFactory()
    UserFactory(email="test@example.com", name="Ben Goldacre")

    request = rf.get("/")
    request.user = staff_user

    response = OrgDetail.as_view()(request, slug=org.slug)

    assert response.status_code == 200
    assert "test@example.com (Ben Goldacre)" in response.rendered_content

    expected = set_from_qs(org.members.all())
    output = set_from_qs(response.context_data["members"])
    assert output == expected


def test_orgdetail_post_success(rf, staff_user):
    org = OrgFactory()

    user1 = UserFactory()
    user2 = UserFactory()

    request = rf.post("/", {"users": [str(user1.pk), str(user2.pk)]})
    request.user = staff_user

    response = OrgDetail.as_view()(request, slug=org.slug)

    assert response.status_code == 302
    assert response.url == org.get_staff_url()

    assert set_from_qs(org.members.all()) == {user1.pk, user2.pk}


def test_orgdetail_post_with_bad_data(rf, staff_user):
    org = OrgFactory()

    request = rf.post("/", {"test": "test"})
    request.user = staff_user

    response = OrgDetail.as_view()(request, slug=org.slug)

    assert response.status_code == 200
    assert response.context_data["form"].errors


def test_orgdetail_unauthorized(rf):
    org = OrgFactory()

    request = rf.get("/")
    request.user = UserFactory()

    response = OrgDetail.as_view()(request, slug=org.slug)

    assert response.status_code == 302
    assert response.url == f"{settings.LOGIN_URL}?next=/"


def test_orgedit_get_success(rf, staff_user):
    org = OrgFactory()

    request = rf.get("/")
    request.user = staff_user

    response = OrgEdit.as_view()(request, slug=org.slug)

    assert response.status_code == 200


def test_orgedit_get_unauthorized(rf):
    org = OrgFactory()

    request = rf.get("/")
    request.user = UserFactory()

    response = OrgEdit.as_view()(request, slug=org.slug)

    assert response.status_code == 302
    assert response.url == f"{settings.LOGIN_URL}?next=/"


def test_orgedit_post_success(rf, staff_user, tmp_path):
    logo = tmp_path / "new_logo.png"
    logo.write_text("test")

    org = OrgFactory()

    data = {"name": "New Name", "slug": "new-name", "logo_file": logo.open()}
    request = rf.post("/", data)
    request.user = staff_user

    response = OrgEdit.as_view()(request, slug=org.slug)

    assert response.status_code == 302, response.context_data["form"].errors

    org.refresh_from_db()
    assert response.url == org.get_staff_url()
    assert org.name == "New Name"
    assert org.slug == "new-name"
    assert org.logo_file


def test_orgedit_post_success_when_not_changing_slug(rf, staff_user, tmp_path):
    logo = tmp_path / "new_logo.png"
    logo.write_text("test")

    org = OrgFactory(slug="slug")

    data = {"name": "New Name", "slug": "slug", "logo_file": logo.open()}
    request = rf.post("/", data)
    request.user = staff_user

    response = OrgEdit.as_view()(request, slug=org.slug)

    assert response.status_code == 302, response.context_data["form"].errors

    org.refresh_from_db()
    assert response.url == org.get_staff_url()
    assert org.name == "New Name"
    assert org.slug == "slug"


def test_orgedit_post_unauthorized(rf):
    org = OrgFactory()

    request = rf.post("/")
    request.user = UserFactory()

    response = OrgEdit.as_view()(request, slug=org.slug)

    assert response.status_code == 302
    assert response.url == f"{settings.LOGIN_URL}?next=/"


def test_orglist_find_by_name(rf, staff_user):
    OrgFactory(name="ben")
    OrgFactory(name="benjamin")
    OrgFactory(name="seb")

    request = rf.get("/?q=ben")
    request.user = staff_user

    response = OrgList.as_view()(request)

    assert response.status_code == 200

    assert len(response.context_data["org_list"]) == 2


def test_orglist_success(rf, staff_user):
    OrgFactory.create_batch(5)

    request = rf.get("/")
    request.user = staff_user

    response = OrgList.as_view()(request)

    assert response.status_code == 200

    assert len(response.context_data["org_list"]) == 5


def test_orglist_unauthorized(rf):
    request = rf.post("/")
    request.user = UserFactory()

    response = OrgList.as_view()(request)

    assert response.status_code == 302
    assert response.url == f"{settings.LOGIN_URL}?next=/"


def test_orgremovemember_success(rf, staff_user):
    org = OrgFactory()
    user = UserFactory()

    OrgMembershipFactory(org=org, user=user)

    request = rf.post("/", {"email": user.email})
    request.user = staff_user

    # set up messages framework
    request.session = "session"
    messages = FallbackStorage(request)
    request._messages = messages

    response = OrgRemoveMember.as_view()(request, slug=org.slug)

    assert response.status_code == 302
    assert response.url == org.get_staff_url()

    org.refresh_from_db()
    assert user not in org.members.all()

    # check we have a message for the user
    messages = list(messages)
    assert len(messages) == 1
    assert str(messages[0]) == f"Removed {user.email} from {org.name}"


def test_orgremovemember_unauthorized(rf):
    request = rf.post("/")
    request.user = UserFactory()

    response = OrgRemoveMember.as_view()(request)

    assert response.status_code == 302
    assert response.url == f"{settings.LOGIN_URL}?next=/"


def test_orgremovemember_unknown_org(rf, staff_user):
    request = rf.post("/")
    request.user = staff_user

    with pytest.raises(Http404):
        OrgRemoveMember.as_view()(request, slug="test")


def test_orgremovemember_unknown_member(rf, staff_user):
    org = OrgFactory()

    assert org.memberships.count() == 0

    request = rf.post("/", {"email": "test"})
    request.user = staff_user

    # set up messages framework
    request.session = "session"
    messages = FallbackStorage(request)
    request._messages = messages

    response = OrgRemoveMember.as_view()(request, slug=org.slug)

    assert response.status_code == 302
    assert response.url == org.get_staff_url()

    org.refresh_from_db()
    assert org.memberships.count() == 0
