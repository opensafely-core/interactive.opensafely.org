import pytest
import requests

from services import opencodelists


@pytest.fixture
def codelists(responses):
    responses.add(
        method="GET",
        url=opencodelists.LIST_URL,
        json={
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
        },
    )


def test_fetch_returns_codelists(codelists):
    expected_codelist = (
        "opensafely/systolic-blood-pressure-qof",
        "Systolic blood pressure QoF",
    )
    assert expected_codelist in opencodelists.fetch()


def test_fetch_raises_http_error_on_endpoint_exception(responses):
    responses.add(
        method="GET",
        url=opencodelists.LIST_URL,
        status=500,
    )

    with pytest.raises(requests.HTTPError):
        opencodelists.fetch()
