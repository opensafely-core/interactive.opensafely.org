import pytest
import requests

from services import opencodelists


TEST_CODELISTS = [
    {
        "name": "Assessment instruments and outcome measures for long covid",
        "versions": [
            {
                "full_slug": "opensafely/assessment-instruments-and-outcome-measures-for-long-covid/version"
            }
        ],
    },
    {
        "name": "Systolic blood pressure QoF",
        "versions": [{"full_slug": "opensafely/systolic-blood-pressure-qof/version"}],
    },
    {
        "name": "Chronic Cardiac Disease (SNOMED)",
        "versions": [
            {"full_slug": "opensafely/chronic-cardiac-disease-snomed/version"}
        ],
    },
]


@pytest.fixture
def codelists(responses):
    responses.add(
        method="GET",
        url=opencodelists.LIST_URL,
        json={"codelists": TEST_CODELISTS},
    )


@pytest.fixture
def add_codelist_response(responses):
    def add(slug, body=None, **kwargs):
        responses.add(
            method="GET",
            url=f"https://www.opencodelists.org/codelist/{slug}/download.csv",
            body=body,
            **kwargs,
        )

    return add


def test_fetch_returns_codelists(codelists):
    expected_codelist = (
        "opensafely/systolic-blood-pressure-qof/version",
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


def test_get_codelist(add_codelist_response):
    add_codelist_response("org/codelist", "1\n2\n3")
    codelist = opencodelists.get_codelist("org/codelist")
    assert codelist == "1\n2\n3"


def test_get_codelist_error(add_codelist_response):
    slug = "org/codelist"
    add_codelist_response(slug, status=500)

    with pytest.raises(requests.HTTPError):
        opencodelists.get_codelist(slug)
