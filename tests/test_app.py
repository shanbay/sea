import pytest
import sys
import os.path

from sea import app, exceptions


def test_sea():
    root_path = './tests/wd'
    sys.path.append(root_path)
    sys.path.append(os.path.join(root_path, 'protos'))

    _app = app.Sea(root_path)
    assert not _app.debug
    assert not _app.testing
    assert _app.extensions == {}
    assert _app.servicers == {}

    class C(object):
        DEBUG = True
        TESTING = True

    _app.config.from_object(C)
    assert _app.debug
    assert _app.testing

    from app import servicers, extensions

    _app.load_servicers_in_module(servicers)
    assert 'GreeterServicer' in _app.servicers
    servicer = _app.servicers['GreeterServicer']
    assert isinstance(servicer, tuple)
    assert servicer == (
        servicers.helloworld_pb2_grpc.add_GreeterServicer_to_server,
        servicers.GreeterServicer)
    with pytest.raises(exceptions.ConfigException):
        _app.register_servicer(servicers.GreeterServicer)

    _app.load_extensions_in_module(extensions)
    ext = _app.extensions['consul']
    assert ext is extensions.consul
    with pytest.raises(exceptions.ConfigException):
        _app.register_extension('consul', extensions.consul)
