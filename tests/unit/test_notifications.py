from interactive import notifications


def test_notify_analysis_request_submitted(mocker):
    mock = mocker.patch("interactive.notifications.slack", autospec=True)
    notifications.notify_analysis_request_submitted("A title", "codelist", "username")
    mock.post.assert_called_once()


def test_notify_register_interest_submitted(mocker):
    mock = mocker.patch("interactive.notifications.slack", autospec=True)
    notifications.notify_register_interest_submitted(
        "Alice", "job title", "org name", "email"
    )
    mock.post.assert_called_once()
