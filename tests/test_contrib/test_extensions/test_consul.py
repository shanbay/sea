from sea.contrib.extensions import consul


def test_consul(app):
    c = consul.Consul()
    assert c._client is None
    c.init_app(app)
    assert isinstance(c._client, consul.consul.Consul)
