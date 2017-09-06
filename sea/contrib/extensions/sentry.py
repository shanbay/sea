import logging
import raven
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler

from sea.extensions import AbstractExtension


class Sentry(AbstractExtension):

    def init_app(self, app):
        dsn = app.config.get('SENTRY_DSN')
        if dsn:
            client = raven.Client(dsn)
            handler = SentryHandler(client)
            handler.setLevel(logging.ERROR)
            setup_logging(handler)
            try:
                from raven.contrib.celery import (
                    register_signal, register_logger_signal)
                register_logger_signal(client)
                register_signal(client)
            except ImportError:
                pass
