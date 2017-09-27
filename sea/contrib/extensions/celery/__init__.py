import celery

from sea.extensions import AbstractExtension


class Celery(celery.Celery, AbstractExtension):

    def init_app(self, app):
        self.config_from_object(app.config.get_namespace('CELERY_'))
