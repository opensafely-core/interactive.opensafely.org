import pytest
from django.contrib.auth.models import User


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def user():
    return User.objects.create_user(username="alice", password="password")
