from sea.extensions.consul import Consul as OriginConsul


class MockKv:

    def __init__(self):
        self.v = None

    def put(self, name, value):
        self.v = value
        return True

    def delete(self, name):
        self.v = None
        return True

    def get(self, name):
        if self.v is None:
            return ('2771385', None)
        return ('2771385',
                {
                    'CreateIndex': 2771381,
                    'Flags': 0,
                    'Key': 'testk',
                    'LockIndex': 0,
                    'ModifyIndex': 2771385,
                    'Value': self.v.encode()
                })


class MockConsulClient:

    def __init__(self, **kwargs):
        self.kv = MockKv()


class Consul(OriginConsul):

    def init_app(self, app):
        opts = app.config.get_namespace('CONSUL_')
        self._client = MockConsulClient(**opts)
