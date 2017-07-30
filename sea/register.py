from consul import Check


class ConsulRegister:

    def __init__(self, client):

        self.client = client

    def register(self, name, publish_host, port):
        return self.client.agent.service.register(
            name, address=publish_host, port=port,
            check=Check.tcp(publish_host, port, "10s"))

    def deregister(self, name, publish_host, port):
        return self.client.agent.service.deregister(name)

    def service_url(self, name):
        _, nodes = self.client.catalog.service(name)
        if len(nodes) == 0:
            return None
        port = nodes[0]['ServicePort']
        return '{}.service.{}:{}'.format(name, self.client.dc, port)
