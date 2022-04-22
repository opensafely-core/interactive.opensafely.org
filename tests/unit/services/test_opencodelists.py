import pytest
import requests

from services import opencodelists


class MockErrorResponse:
    def __init__(*args, **kwargs):
        pass

    def raise_for_status(self):
        raise Exception()


@pytest.fixture
def mock_response_raises(monkeypatch):
    monkeypatch.setattr(requests, "get", MockErrorResponse)


def test_fetch_returns_codelists(mock_response):
    expected_codelist = (
        "opensafely/systolic-blood-pressure-qof",
        "Systolic blood pressure QoF",
    )
    assert expected_codelist in opencodelists.fetch()


def test_fetch_raises_on_error(mock_response_raises):
    with pytest.raises(Exception):
        opencodelists.fetch()
