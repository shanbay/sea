import pytest
import os.path

from sea import app

from app.servicers import GreeterServicer, helloworld_pb2_grpc
from app.extensions import consul


def test_sea():
    _app = app.Sea(os.path.dirname(__file__))
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

    _app.register_servicer(GreeterServicer)
    assert 'GreeterServicer' in _app.servicers
    servicer = _app.servicers['GreeterServicer']
    assert isinstance(servicer, tuple)
    assert servicer == (helloworld_pb2_grpc.add_GreeterServicer_to_server, GreeterServicer)
    with pytest.raises(RuntimeError):
        _app.register_servicer(GreeterServicer)

    _app.register_extension('consul', consul)
    ext = _app.extensions['consul']
    assert ext is consul
