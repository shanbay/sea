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

    from app.servicers import GreeterServicer, helloworld_pb2_grpc
    from app.extensions import consul

    _app.register_servicer(GreeterServicer)
    assert 'GreeterServicer' in _app.servicers
    servicer = _app.servicers['GreeterServicer']
    assert isinstance(servicer, tuple)
    assert servicer == (helloworld_pb2_grpc.add_GreeterServicer_to_server, GreeterServicer)
    with pytest.raises(exceptions.ConfigException):
        _app.register_servicer(GreeterServicer)

    _app.register_extension('consul', consul)
    ext = _app.extensions['consul']
    assert ext is consul
    with pytest.raises(exceptions.ConfigException):
        _app.register_extension('consul', consul)
