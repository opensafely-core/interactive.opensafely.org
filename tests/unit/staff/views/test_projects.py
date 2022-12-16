import pytest
from django.conf import settings
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import Http404

from interactive.models import Project
from interactive.utils import set_from_qs
from staff.views.projects import (
    ProjectCreate,
    ProjectDetail,
    ProjectEdit,
    ProjectList,
    ProjectRemoveMember,
)

from ....factories import (
    OrgFactory,
    ProjectFactory,
    ProjectMembershipFactory,
    UserFactory,
)


def test_projectcreate_get_success(rf, staff_user):
    project = ProjectFactory()

    request = rf.get("/")
    request.user = staff_user

    response = ProjectCreate.as_view()(request, slug=project.slug)

    assert response.status_code == 200


def test_projectcreate_post_success(rf, staff_user):
    org = OrgFactory()

    assert not Project.objects.exists()

    data = {
        "org": org.pk,
        "name": "new-name",
        "number": 42,
        "purpose": "The project purpose",
        "summary": "The project summary",
        "application_url": "http://example.com",
    }
    request = rf.post("/", data)
    request.user = staff_user

    response = ProjectCreate.as_view()(request)

    assert response.status_code == 302, response.context_data["form"].errors

    project = Project.objects.first()
    assert response.url == project.get_staff_url()
    assert project.created_by == staff_user
    assert project.name == "new-name"
    assert project.org == org
    assert project.number == 42
    assert project.purpose == "The project purpose"
    assert project.summary == "The project summary"
    assert project.application_url == "http://example.com"


def test_projectcreate_unauthorized(rf):
    request = rf.get("/")
    request.user = UserFactory()

    response = ProjectCreate.as_view()(request)

    assert response.status_code == 302
    assert response.url == f"{settings.LOGIN_URL}?next=/"


def test_projectdetail_get_success(rf, staff_user):
    project = ProjectFactory()

    request = rf.get("/")
    request.user = staff_user

    response = ProjectDetail.as_view()(request, slug=project.slug)

    assert response.status_code == 200


def test_projectdetail_post_success(rf, staff_user):
    project = ProjectFactory()

    user1 = UserFactory()
    user2 = UserFactory()

    request = rf.post("/", {"users": [str(user1.pk), str(user2.pk)]})
    request.user = staff_user

    response = ProjectDetail.as_view()(request, slug=project.slug)

    assert response.status_code == 302
    assert response.url == project.get_staff_url()

    assert set_from_qs(project.members.all()) == {user1.pk, user2.pk}


def test_projectedetail_unauthorized(rf):
    project = ProjectFactory()

    request = rf.get("/")
    request.user = UserFactory()

    response = ProjectDetail.as_view()(request, slug=project.slug)

    assert response.status_code == 302
    assert response.url == f"{settings.LOGIN_URL}?next=/"


def test_projectedit_get_success(rf, staff_user):
    project = ProjectFactory()

    request = rf.get("/")
    request.user = staff_user

    response = ProjectEdit.as_view()(request, slug=project.slug)

    assert response.status_code == 200


def test_projectedit_get_unauthorized(rf):
    project = ProjectFactory()

    request = rf.get("/")
    request.user = UserFactory()

    response = ProjectEdit.as_view()(request, slug=project.slug)

    assert response.status_code == 302
    assert response.url == f"{settings.LOGIN_URL}?next=/"


def test_projectedit_post_success(rf, staff_user):
    old_org = OrgFactory()
    original = ProjectFactory(org=old_org, name="test", number=123)

    new_org = OrgFactory()

    data = {
        "name": "New Name",
        "slug": "new-name",
        "number": 456,
        "org": str(new_org.pk),
        "status": Project.Statuses.COMPLETED_AWAITING,
        "status_description": "",
    }
    request = rf.post("/", data)
    request.user = staff_user

    response = ProjectEdit.as_view()(request, slug=original.slug)

    assert response.status_code == 302, response.context_data["form"].errors

    updated = Project.objects.get(pk=original.pk)
    assert response.url == updated.get_staff_url()
    assert updated.name == "New Name"
    assert updated.slug == "new-name"
    assert updated.number == 456
    assert updated.org == new_org
    assert updated.updated_by == staff_user


def test_projectedit_post_success_when_not_changing_org_or_slug(rf, staff_user):
    project = ProjectFactory(name="Test", slug="test", number=123)

    data = {
        "name": "Test",
        "slug": "test",
        "number": 456,
        "org": str(project.org.pk),
        "status": Project.Statuses.POSTPONED,
        "status_description": "",
    }
    request = rf.post("/", data)
    request.user = staff_user

    response = ProjectEdit.as_view()(request, slug=project.slug)

    assert response.status_code == 302, response.context_data["form"].errors

    project.refresh_from_db()
    assert response.url == project.get_staff_url()
    assert project.name == "Test"
    assert project.slug == "test"
    assert project.number == 456


def test_projectedit_post_unauthorized(rf):
    project = ProjectFactory()

    request = rf.post("/")
    request.user = UserFactory()

    response = ProjectEdit.as_view()(request, slug=project.slug)

    assert response.status_code == 302
    assert response.url == f"{settings.LOGIN_URL}?next=/"


def test_projectedit_post_unknown_project(rf, staff_user):
    request = rf.post("/")
    request.user = staff_user

    with pytest.raises(Http404):
        ProjectEdit.as_view()(request, slug="")


def test_projectlist_filter_by_org(rf, staff_user):
    project = ProjectFactory()
    ProjectFactory.create_batch(2)

    request = rf.get(f"/?org={project.org.slug}")
    request.user = staff_user

    response = ProjectList.as_view()(request)

    assert len(response.context_data["project_list"]) == 1


def test_projectlist_find_by_username(rf, staff_user):
    ProjectFactory(name="ben")
    ProjectFactory(name="benjamin")
    ProjectFactory(name="seb")

    request = rf.get("/?q=ben")
    request.user = staff_user

    response = ProjectList.as_view()(request)

    assert response.status_code == 200

    assert len(response.context_data["project_list"]) == 2


def test_projectlist_success(rf, staff_user):
    ProjectFactory.create_batch(5)

    request = rf.get("/")
    request.user = staff_user

    response = ProjectList.as_view()(request)

    assert response.status_code == 200
    assert len(response.context_data["project_list"])


def test_projectlist_unauthorized(rf):
    project = ProjectFactory()

    request = rf.post("/")
    request.user = UserFactory()

    response = ProjectList.as_view()(
        request, org_slug=project.org.slug, project_slug=project.slug
    )

    assert response.status_code == 302
    assert response.url == f"{settings.LOGIN_URL}?next=/"


def test_projectremovemember_success(rf, staff_user):
    project = ProjectFactory()
    user = UserFactory()

    ProjectMembershipFactory(project=project, user=user)

    request = rf.post("/", {"email": user.email})
    request.user = staff_user

    # set up messages framework
    request.session = "session"
    messages = FallbackStorage(request)
    request._messages = messages

    response = ProjectRemoveMember.as_view()(request, slug=project.slug)

    assert response.status_code == 302
    assert response.url == project.get_staff_url()

    project.refresh_from_db()
    assert user not in project.members.all()

    # check we have a message for the user
    messages = list(messages)
    assert len(messages) == 1
    assert str(messages[0]) == f"Removed {user.email} from {project.title}"


def test_projectremovemember_unauthorized(rf):
    request = rf.post("/")
    request.user = UserFactory()

    response = ProjectRemoveMember.as_view()(request)

    assert response.status_code == 302
    assert response.url == f"{settings.LOGIN_URL}?next=/"


def test_projectremovemember_unknown_project(rf, staff_user):
    request = rf.post("/")
    request.user = staff_user

    with pytest.raises(Http404):
        ProjectRemoveMember.as_view()(request, slug="test")


def test_projectremovemember_unknown_member(rf, staff_user):
    project = ProjectFactory()

    assert project.memberships.count() == 0

    request = rf.post("/", {"email": "test"})
    request.user = staff_user

    # set up messages framework
    request.session = "session"
    messages = FallbackStorage(request)
    request._messages = messages

    response = ProjectRemoveMember.as_view()(request, slug=project.slug)

    assert response.status_code == 302
    assert response.url == project.get_staff_url()

    project.refresh_from_db()
    assert project.memberships.count() == 0
