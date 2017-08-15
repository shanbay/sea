from sea.extensions import AbstractExtension
import orator


class Orator(AbstractExtension):

    def __init__(self):
        self._client = None

    def init_app(self, app):
        conf_m = app.config.get('ORATOR')
        self._client = orator.DatabaseManager(conf_m.DATABASES)
        orator.Model.set_connection_resolver(self._client)

    def __getattr__(self, name):
        return getattr(self._client, name)
