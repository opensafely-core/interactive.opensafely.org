from slack_sdk.errors import SlackApiError

from services import slack


def test_post_sends_message(mocker):
    mock = mocker.patch("services.slack.client", autospec=True)

    slack.post("text", "channel")

    mock.chat_postMessage.assert_called_once_with(channel="channel", text="text")


def test_post_error_logs_exception(mocker):
    mock_logger = mocker.patch("services.slack.logger.exception")
    mock_client = mocker.patch("services.slack.client", autospec=True)
    mock_client.chat_postMessage.side_effect = SlackApiError(
        message="an error", response={"error": "an error occurred"}
    )

    slack.post("text", "channel")

    mock_logger.assert_called_once()


def test_link_with_only_url():
    assert slack.link("https://localhost") == "<https://localhost>"


def test_link_with_url_and_text():
    assert (
        slack.link("https://localhost", "some text") == "<https://localhost|some text>"
    )


def test_link_with_relative_url():
    assert slack.link("/analysis-request") == "<http://localhost:8000/analysis-request>"
