from interactive import notifications
from tests.factories import AnalysisRequestFactory


def test_notify_analysis_request_submitted(mocker):
    mock = mocker.patch("interactive.notifications.slack", autospec=True)
    analysis_request = AnalysisRequestFactory()
    notifications.notify_analysis_request_submitted(analysis_request, "username")
    mock.post.assert_called_once()


def test_notify_register_interest_submitted(mocker):
    mock = mocker.patch("interactive.notifications.slack", autospec=True)
    notifications.notify_registration_request_submitted(
        "Alice", "job title", "org name", "email"
    )
    mock.post.assert_called_once()
