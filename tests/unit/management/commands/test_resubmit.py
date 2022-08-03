from datetime import timedelta
from io import StringIO

import pytest
import timeflake
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone

from tests.factories import AnalysisRequest, AnalysisRequestFactory


def test_resubmit_error():
    with pytest.raises(CommandError) as exc:
        call_command("resubmit", "invalid")

    assert isinstance(exc.value.__cause__, ValidationError)

    rid = timeflake.random()
    with pytest.raises(CommandError) as exc:
        call_command("resubmit", str(rid))

    assert isinstance(exc.value.__cause__, AnalysisRequest.DoesNotExist)


def test_resubmit_success(
    workspace_repo,
    add_codelist_response,
    slack_messages,
    submit_job_request,
    create_output_checker_issue,
):
    analysis_request = AnalysisRequestFactory()
    add_codelist_response(analysis_request.codelist_slug, "1\n2\n3")
    call_command("resubmit", str(analysis_request.id))


def test_resubmit_success_uuid(
    workspace_repo,
    add_codelist_response,
    slack_messages,
    submit_job_request,
    create_output_checker_issue,
):
    analysis_request = AnalysisRequestFactory()
    add_codelist_response(analysis_request.codelist_slug, "1\n2\n3")
    call_command("resubmit", str(analysis_request.id.uuid))


def test_resubmit_success_since(
    workspace_repo,
    add_codelist_response,
    slack_messages,
    submit_job_request,
    create_output_checker_issue,
):

    since = timezone.now()
    analysis_request1 = AnalysisRequestFactory(
        created_at=since - timedelta(days=1), commit_sha=None, codelist_slug="first"
    )
    analysis_request2 = AnalysisRequestFactory(
        created_at=since + timedelta(days=1), commit_sha=None, codelist_slug="second"
    )

    # only 2nd request should be run, so only that codelist should be fetched
    add_codelist_response(analysis_request2.codelist_slug, "1\n2\n3")
    stdout = StringIO()
    call_command("resubmit", since=since.strftime("%Y-%m-%d"), stdout=stdout)

    output = stdout.getvalue()
    assert str(analysis_request1.id) not in output
    assert str(analysis_request2.id) in output


def test_resubmit_success_since_none_valid(
    workspace_repo,
    add_codelist_response,
    slack_messages,
):

    since = timezone.now()
    stdout = StringIO()
    call_command("resubmit", since=since.strftime("%Y-%m-%d"), stdout=stdout)

    output = stdout.getvalue()
    assert "No AnalysisRequests found since" in output
