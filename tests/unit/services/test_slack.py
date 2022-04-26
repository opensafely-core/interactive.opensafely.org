from slack_sdk.errors import SlackApiError

from services import slack


def test_post(mocker):
    mock = mocker.patch("services.slack.client", autospec=True)

    slack.post("text", "channel")

    mock.chat_postMessage.assert_called_once_with(channel="channel", text="text")


def test_post_error(mocker):
    mock = mocker.patch("services.slack.client", autospec=True)

    mock.chat_postMessage.side_effect = SlackApiError(
        message="an error", response={"error": "an error occurred"}
    )

    slack.post("text", "channel")

    mock.chat_postMessage.assert_called_once_with(channel="channel", text="text")


def test_link_with_only_url():
    assert slack.link("https://localhost") == "<https://localhost>"


def test_link_with_url_and_text():
    assert (
        slack.link("https://localhost", "some text") == "<https://localhost|some text>"
    )


def test_link_with_relative_url():
    assert slack.link("/analysis-request") == "<http://localhost:8000/analysis-request>"
