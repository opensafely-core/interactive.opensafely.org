import pytest
from furl import furl

from services import github


@pytest.fixture
def add_github_response(responses):
    def add(path, method="GET", **kwargs):
        responses.add(
            url=str(furl(github.BASE_URL) / path),  # convert furl to str
            method=method,
            **kwargs,
        )

    return add


@pytest.fixture
def create_output_checker_issue(add_github_response):
    add_github_response(
        "repos/ebmdatalab/opensafely-output-review/issues",
        method="POST",
        json={"html_url": "http://example.com/"},
    )


def test_create_issue(create_output_checker_issue):
    output = github.create_issue("abc123", "")

    assert output == "http://example.com/"
