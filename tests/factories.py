import factory
import timeflake

from interactive.models import (
    END_DATE,
    START_DATE,
    AnalysisRequest,
    RegistrationRequest,
    User,
)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user-{n}@example.com")
    name = factory.Sequence(lambda n: f"user-{n}")
    password = factory.PostGenerationMethodCall("set_password", "password!")
    is_active = True


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
