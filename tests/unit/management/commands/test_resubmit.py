import pytest
import timeflake
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError

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
    workspace_repo, add_codelist_response, slack_messages, submit_job_request
):
    analysis_request = AnalysisRequestFactory()
    add_codelist_response(analysis_request.codelist_slug, "1\n2\n3")
    call_command("resubmit", str(analysis_request.id))
