import elasticsearch

from sea.extensions import AbstractExtension


class Elasticsearch(AbstractExtension):

    def __init__(self):
        self._client = None

    def init_app(self, app):
        opts = app.config.get_namespace('ELASTICSEARCH_')
        self._client = elasticsearch.Elasticsearch(**opts)

    def __getattr__(self, name):
        return getattr(self._client, name)
