import elasticsearch

from sea.extensions import AbstractExtension


class Elasticsearch(AbstractExtension):

    def __init__(self):
        self._pool = None

    def init_app(self, app):
        opts = app.config.get_namespace('ELASTICSEARCH_')
        connections = []
        for i in range(10):
            connections.append((elasticsearch.Elasticsearch(), opts))
        self._pool = elasticsearch.ConnectionPool(connections)

    @property
    def _client(self):
        return self._pool.get_connection()

    def __getattr__(self, name):
        return getattr(self._client, name)
