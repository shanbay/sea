from sea import create_app
from sea.contrib.extensions import consul


def test_consul():
    c = consul.Consul()
    assert c._client is None
    c.init_app(create_app('./tests/wd'))
    assert isinstance(c._client, consul.consul.Consul)
