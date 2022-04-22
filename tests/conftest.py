import pytest
import requests
from django.contrib.auth.models import User


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def user():
    return User.objects.create_user(username="alice", password="password")


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")


class MockResponse:
    def __init__(*args, **kwargs):
        pass

    def raise_for_status(self):
        pass

    @staticmethod
    def json():
        response = {
            "codelists": [
                {
                    "full_slug": "opensafely/assessment-instruments-and-outcome-measures-for-long-covid",
                    "name": "Assessment instruments and outcome measures for long covid",
                },
                {
                    "full_slug": "opensafely/systolic-blood-pressure-qof",
                    "name": "Systolic blood pressure QoF",
                },
                {
                    "full_slug": "opensafely/chronic-cardiac-disease-snomed",
                    "name": "Chronic Cardiac Disease (SNOMED)",
                },
            ]
        }
        return response


@pytest.fixture
def mock_response(monkeypatch):
    monkeypatch.setattr(requests, "get", MockResponse)
