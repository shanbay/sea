class ConsulRegister:

    def __init__(self, client):

        self.client = client

    def register(self, name, port):
        return self.client.kv.put(name, port)

    def deregister(self, name):
        return self.client.kv.delete(name)

    def get_port(self, name):
        _, data = self.client.kv.get(name)
        if data is None:
            return None
        port = data['Value']
        if isinstance(port, bytes):
            port = port.decode()
        return port
