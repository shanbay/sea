from sea.contrib.extensions import elasticsearch


def test_elasticsearch(app):
    e = elasticsearch.Elasticsearch()
    assert e._pool is None
    e.init_app(app)
    assert isinstance(e._client, elasticsearch.elasticsearch.Elasticsearch)
