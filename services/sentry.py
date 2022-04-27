import sentry_sdk
from environs import Env
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger


env = Env()


def initialise_sentry():

    # ignore the request logging middleware, it creates ungrouped events by default
    # https://docs.sentry.io/platforms/python/guides/logging/#ignoring-a-logger
    ignore_logger("django_structlog.middlewares.request")

    sentry_dsn = env.str("SENTRY_DSN", default=None)
    environment = env.str("SENTRY_ENVIRONMENT", default="localhost")

    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            integrations=[DjangoIntegration()],
            send_default_pii=True,
        )
