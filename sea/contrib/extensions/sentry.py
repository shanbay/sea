import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations import DidNotEnable


class Sentry:

    def init_app(self, app):
        dsn = app.config.get('SENTRY_DSN')
        if dsn:
            config = app.config.get_namespace('SENTRY_')
            sentry_logging = LoggingIntegration()
            integrations = [sentry_logging]

            try:
                from sentry_sdk.integrations.celery import CeleryIntegration

                integrations.append(CeleryIntegration())
            except DidNotEnable:
                pass

            sentry_sdk.init(**config, integrations=integrations)
