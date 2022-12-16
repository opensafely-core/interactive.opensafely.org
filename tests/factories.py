import factory
import timeflake

from interactive.models import (
    END_DATE,
    START_DATE,
    AnalysisRequest,
    Org,
    OrgMembership,
    Project,
    ProjectMembership,
    RegistrationRequest,
    User,
)


class AnalysisRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AnalysisRequest

    id = factory.LazyAttribute(lambda _: timeflake.random())  # noqa: A003
    title = factory.Sequence(lambda n: f"Analysis Request {n}")
    start_date = START_DATE
    end_date = END_DATE
    codelist_name = "Asthma annual review QOF"
    codelist_slug = "opensafely/asthma-annual-review-qof"

    created_by = factory.SubFactory("tests.factories.UserFactory")


class RegistrationRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RegistrationRequest

    id = factory.LazyAttribute(lambda _: timeflake.random())  # noqa: A003


class OrgFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Org

    name = factory.Sequence(lambda n: f"Org-{n}")
    slug = factory.Sequence(lambda n: f"org-{n}")


class OrgMembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrgMembership

    org = factory.SubFactory("tests.factories.OrgFactory")
    user = factory.SubFactory("tests.factories.UserFactory")


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: f"Project {n}")
    slug = factory.Sequence(lambda n: f"project-{n}")
    number = factory.Sequence(lambda n: n)

    org = factory.SubFactory("tests.factories.OrgFactory")


class ProjectMembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectMembership

    project = factory.SubFactory("tests.factories.ProjectFactory")
    user = factory.SubFactory("tests.factories.UserFactory")


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user-{n}@example.com")
    name = factory.Sequence(lambda n: f"user-{n}")
    password = factory.PostGenerationMethodCall("set_password", "password!")
    is_active = True
