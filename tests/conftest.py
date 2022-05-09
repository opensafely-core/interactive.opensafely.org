import pytest

from interactive.models import User


# include some fixtures from submodules
pytest_plugins = ["tests.unit.services.test_opencodelists"]


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def user():
    return User.objects.create_user(
        email="alice@test.com", password="password", name="Alice"
    )
