import orator
import pendulum

from sea.extensions import AbstractExtension
from sea import current_app


class Orator(AbstractExtension):

    def __init__(self):
        self._dbmanager = None

    def init_app(self, app):
        self._dbmanager = orator.DatabaseManager(
            app.config.get('DATABASES'))
        orator.Model.set_connection_resolver(self._dbmanager)

    def __getattr__(self, name):
        return getattr(self._dbmanager, name)


class Model(orator.Model):

    def as_datetime(self, value):
        rt = super().as_datetime(value)
        if isinstance(rt, pendulum.pendulum.Pendulum):
            rt = rt.in_timezone(current_app.tz)
        return rt
