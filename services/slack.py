import structlog
from django.conf import settings
from environs import Env
from furl import furl
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


logger = structlog.get_logger(__name__)

env = Env()

slack_token = env.str("SLACK_BOT_TOKEN", default="")

client = WebClient(token=slack_token)


def post(text, channel="interactive-requests"):
    if settings.DEBUG:  # pragma: no cover
        return

    try:
        client.chat_postMessage(channel=channel, text=text)
    except SlackApiError:
        # failing to slack is never fatal, but is something we need to take action on
        # so any problems should appear in Sentry
        logger.exception("Failed to notify slack")


def link(url, text=None):
    """Because no one can remember this"""
    if url.startswith("/"):
        base_url = furl(settings.BASE_URL)
        base_url.path = url
        url = base_url.url

    if text is None:
        return f"<{url}>"
    else:
        return f"<{url}|{text}>"
