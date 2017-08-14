from sea.extensions import AbstractExtension
import celery


class Celery(celery.Celery, AbstractExtension):

    def init_app(self, app):
        self.config_from_object(app.config.get('CELERY'))
