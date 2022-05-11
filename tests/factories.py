import factory
import timeflake

from interactive.models import AnalysisRequest, User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user-{n}@example.com")
    name = factory.Sequence(lambda n: f"user-{n}")
    password = factory.PostGenerationMethodCall("set_password", "password!")


class AnalysisRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AnalysisRequest

    id = timeflake.random()  # noqa: A003
    user = factory.SubFactory("tests.factories.UserFactory")
    title = factory.Sequence(lambda n: f"Analysis Request {n}")
    start_date = factory.Faker("date")
    end_date = factory.Faker("date")