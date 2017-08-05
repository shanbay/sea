from sea.extensions import AbstractExtension
import orator


class Orator(AbstractExtension):

    def __init__(self):
        self._client = None

    def init_app(self, app):
        self._client = orator.DatabaseManager(app.config.get('ORATOR'))

    def __getattr__(self, name):
        return getattr(self._client, name)
