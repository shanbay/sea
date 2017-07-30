from sea.extensions.consul import Consul as OriginConsul


class MockAgent:
    class MockService:
        def register(self, name, address, port, check=None):
            self.name = name
            self.address = address,
            self.port = port
            self.check = check
            return True

        def deregister(self, name):
            self.name = None
            return True

    def __init__(self):
        self.service = self.MockService()


class MockCatalog:

    def __init__(self, agent):
        self.agent = agent

    def service(self, name):
        service = self.agent.service
        if service.name == name:
            return ('2791405', [{
                    'Address': service.address,
                    'CreateIndex': 2791238,
                    'ModifyIndex': 2791405,
                    'Node': 'nd1',
                    'ServiceAddress': service.address,
                    'ServiceEnableTagOverride': False,
                    'ServiceID': name,
                    'ServiceName': name,
                    'ServicePort': service.port,
                    'ServiceTags': []
                    }])
        else:
            return ('2791405', [])


class MockConsulClient:

    def __init__(self, **kwargs):
        self.agent = MockAgent()
        self.catalog = MockCatalog(self.agent)
        self.dc = 'consul'


class Consul(OriginConsul):

    def init_app(self, app):
        opts = app.config.get_namespace('CONSUL_')
        self._client = MockConsulClient(**opts)
