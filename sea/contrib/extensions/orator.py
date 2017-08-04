import sys

from sea.extensions import AbstractExtension

try:
    import orator
except ImportError as e:
    print(
        '{}\nyou need run: pip install orator'.format(e),
        file=sys.stderr)
    sys.exit(2)


class Orator(AbstractExtension):

    def __init__(self):
        self._client = None

    def init_app(self, app):
        self._client = orator.DatabaseManager(app.config.get('DATABASES'))

    def __getattr__(self, name):
        return getattr(self._client, name)
