import logging
import raven
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler


class Sentry:

    def init_app(self, app):
        dsn = app.config.get('SENTRY_DSN')
        if dsn:
            config = app.config.get_namespace('SENTRY_')
            self.client = raven.Client(**config)
            handler = SentryHandler(self.client)
            handler.setLevel(logging.ERROR)
            setup_logging(handler)
            try:
                from raven.contrib.celery import (
                    register_signal, register_logger_signal)
                register_logger_signal(self.client)
                register_signal(self.client)
            except ImportError:
                pass
