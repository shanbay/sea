import consul

from sea.extensions import AbstractExtension


class Consul(AbstractExtension):
    '''
    pip install python-consul
    '''

    def __init__(self):
        self._client = None

    def init_app(self, app):
        opts = app.config.get_namespace('CONSUL_')
        self._client = consul.Consul(**opts)

    def __getattr__(self, name):
        return getattr(self._client, name)
