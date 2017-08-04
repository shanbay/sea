from sea import create_app
from sea.contrib.extensions import orator


def test_consul():
    c = orator.Orator()
    assert c._client is None
    c.init_app(create_app('./tests/wd'))
    assert isinstance(c._client, orator.orator.DatabaseManager)
