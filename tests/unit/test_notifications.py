from interactive import notifications
from tests.factories import AnalysisRequestFactory


def test_notify_analysis_request_submitted(slack_messages):
    analysis_request = AnalysisRequestFactory()

    notifications.notify_analysis_request_submitted(analysis_request, "ticket link")

    msg = slack_messages[-1].text
    assert analysis_request.created_by.email in msg
    assert analysis_request.codelist_name in msg
    assert analysis_request.codelist_slug in msg
    assert analysis_request.title in msg
    assert str(analysis_request.id) in msg
    assert analysis_request.job_request_url in msg
    assert "ticket link" in msg


def test_notify_register_interest_submitted(slack_messages):
    notifications.notify_registration_request_submitted(
        "Alice", "job title", "org name", "email"
    )
    msg = slack_messages[-1].text
    assert "Alice" in msg
    assert "job title" in msg
    assert "org name" in msg
    assert "email" in msg
