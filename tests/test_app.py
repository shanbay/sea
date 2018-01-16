import pytest
import sys
import os.path
from unittest import mock

from sea import app, exceptions


def test_baseapp():
    root_path = './tests/wd'
    sys.path.insert(0, root_path)
    sys.path.insert(1, os.path.join(root_path, 'protos'))

    _app = app.BaseApp(root_path, env='testing')
    assert not _app.debug
    assert not _app.testing

    from configs import testing

    _app.config.from_object(testing)
    assert _app.debug
    assert _app.testing
    _app.load_middlewares()

    assert len(_app.middlewares) == 3

    with mock.patch('sea._app', new=_app):
        from app import servicers, extensions

    with pytest.raises(exceptions.ConfigException):
        _app._register_servicer(servicers.GreeterServicer)
        _app._register_servicer(servicers.GreeterServicer)

    _app._servicers = {}
    _app.load_servicers_in_module(servicers)
    assert 'GreeterServicer' in _app.servicers
    servicer = _app.servicers['GreeterServicer']
    assert isinstance(servicer, tuple)
    assert servicer == (
        servicers.helloworld_pb2_grpc.add_GreeterServicer_to_server,
        servicers.GreeterServicer)

    with pytest.raises(exceptions.ConfigException):
        _app._register_extension('db', extensions.db)
        _app._register_extension('db', extensions.db)
    _app._extensions = {}
    _app.load_extensions_in_module(extensions)
    ext = _app.extensions.db
    assert ext is extensions.db

    with mock.patch('sys.stderr') as mocked:
        _app.logger.debug('test')
        assert len(mocked.method_calls) > 0
