import pytest
import requests

from services import opencodelists


def test_fetch_returns_codelists(mock_codelists_response):
    expected_codelist = (
        "opensafely/systolic-blood-pressure-qof",
        "Systolic blood pressure QoF",
    )
    assert expected_codelist in opencodelists.fetch()


def test_fetch_raises_http_error_on_endpoint_exception(mock_response_raises):
    with pytest.raises(requests.HTTPError):
        opencodelists.fetch()
