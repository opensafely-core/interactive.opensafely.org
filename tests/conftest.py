import os
from collections import namedtuple

import pytest

import services

from .factories import UserFactory


# include some fixtures from submodules
# it might be better to move to a tests.fixtures module at some point
pytest_plugins = [
    "tests.unit.services.test_jobserver",
    "tests.unit.services.test_opencodelists",
    "tests.unit.test_submit",
]


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def admin_user():
    return UserFactory(is_staff=True)


# set these values to have messages generated by tests appear in a test channel
slack_token = os.environ.get("SLACK_BOT_TOKEN")
slack_test_channel = os.environ.get("SLACK_TEST_CHANNEL")

SlackMessage = namedtuple("SlackMessage", ("text", "channel"))


@pytest.fixture
def slack_messages(monkeypatch):
    messages = []

    actual_post = services.slack.post

    def post(text, channel=None):
        messages.append(SlackMessage(text, channel))

        if slack_token and slack_test_channel:  # pragma: no cover
            actual_post(text, slack_test_channel)

    monkeypatch.setattr("services.slack.post", post)
    return messages
