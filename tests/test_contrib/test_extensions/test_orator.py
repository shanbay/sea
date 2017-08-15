from unittest import mock

from sea import create_app
from sea.contrib.extensions import orator


def test_orator():
    c = orator.Orator()
    assert c._client is None
    c.init_app(create_app('./tests/wd'))
    assert isinstance(c._client, orator.orator.DatabaseManager)
    with mock.patch.object(c._client, 'connection') as mocked:
        c.connection()
        mocked.assert_called_once_with()
