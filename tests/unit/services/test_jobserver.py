import pytest
import requests
from django.conf import settings

from services import jobserver


@pytest.fixture
def add_jobserver_response(responses):
    def add(path, method="GET", **kwargs):
        responses.add(
            url=str(settings.JOB_SERVER_URL / path),  # convert furl to str
            method=method,
            **kwargs,
        )

    return add


@pytest.fixture
def fetch_release(add_jobserver_response):
    add_jobserver_response(
        jobserver.RELEASES_PATH,
        json={
            "files": [
                {
                    "name": "backend/output/123/deciles_chart_counts_per_week_per_practice.png",
                    "url": "/api/v2/releases/file/6STFP07F15EM",
                },
                {
                    "name": "backend/output/123/event_counts.csv",
                    "url": "/api/v2/releases/file/EK8NRG9A6GKQGJ",
                },
                {
                    "name": "backend/output/123/top_5_code_table.csv",
                    "url": "/api/v2/releases/file/WXC18BDMBTM0M",
                },
            ]
        },
    )


@pytest.fixture
def fetch_deciles_chart(add_jobserver_response):
    add_jobserver_response(
        "/api/v2/releases/file/6STFP07F15EM",
        body=b"abc123",
    )


@pytest.fixture
def fetch_event_counts(add_jobserver_response):
    add_jobserver_response(
        "/api/v2/releases/file/EK8NRG9A6GKQGJ",
        body=b'"Patient count"\n"1000"',
    )


@pytest.fixture
def fetch_most_common_codes(add_jobserver_response):
    add_jobserver_response(
        "/api/v2/releases/file/WXC18BDMBTM0M",
        body=b'"Code","Proportion of codes (%)"\n "72313002","90.23"',
    )


def test_fetch_release_returns_correct_files(
    fetch_release, fetch_deciles_chart, fetch_event_counts, fetch_most_common_codes
):
    analysis_request_id = "123"

    output = jobserver.fetch_release(analysis_request_id)

    assert "deciles_chart" in output
    assert "summary" in output
    assert "Patient count" in output["summary"][0]
    assert "common_codes" in output
    assert "Proportion" in output["common_codes"][0]
    assert "90.23" in output["common_codes"][0]["Proportion"]


def test_fetch_release_handles_missing_column_for_common_codes(
    fetch_release, fetch_deciles_chart, fetch_event_counts, add_jobserver_response
):
    add_jobserver_response(
        "/api/v2/releases/file/WXC18BDMBTM0M",
        body=b'"Code","Missing column"\n "72313002","90.23"',
    )
    analysis_request_id = "123"

    output = jobserver.fetch_release(analysis_request_id)

    assert "common_codes" in output
    assert "Proportion" in output["common_codes"][0]


def test_fetch_release_raises_http_error_on_endpoint_exception(add_jobserver_response):
    analysis_request_id = "123"
    add_jobserver_response(
        jobserver.RELEASES_PATH,
        status=500,
    )

    with pytest.raises(requests.HTTPError):
        jobserver.fetch_release(analysis_request_id)
