import sys

from sea.extensions import AbstractExtension

try:
    import consul
except ImportError as e:
    print(
        '{}\nyou need run: pip install python-consul'.format(e),
        file=sys.stderr)
    sys.exit(2)


class Consul(AbstractExtension):

    def __init__(self):
        self._client = None

    def init_app(self, app):
        opts = app.config.get_namespace('CONSUL_')
        self._client = consul.Consul(**opts)

    def __getattr__(self, name):
        return getattr(self._client, name)
