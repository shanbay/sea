import logging
import os.path
import sys
from unittest import mock

import pytest

from sea import app, exceptions


def test_baseapp(caplog):

    root_path = './tests/wd'
    sys.path.append(root_path)
    sys.path.append(os.path.join(root_path, 'protos'))

    _app = app.BaseApp(root_path, env='testing')
    assert not _app.debug
    assert not _app.testing

    from configs import testing

    os.environ["SEA_DEBUG"] = "true"
    _app = app.BaseApp(root_path, env='testing')
    _app.config.from_object(testing)
    assert _app.config["PORT"] == 4000
    os.environ["PORT"] = "4001"
    _app.config.load_config_from_env()
    assert _app.config["PORT"] == 4001
    assert _app.debug
    assert _app.testing
    os.environ["SEA_MIDDLEWARES"] = "sea.middleware.BaseMiddleware,sea.middleware.ServiceLogMiddleware,"
    _app.load_middlewares()

    assert len(_app.middlewares) == 4

    with mock.patch('sea._app', new=_app):
        from app import extensions, servicers

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
        _app._register_extension('pwx', extensions.pwx)
        _app._register_extension('pwx', extensions.pwx)
    _app._extensions = {}
    _app.load_extensions_in_module(extensions)
    ext = _app.extensions.pwx
    assert ext is extensions.pwx

    with caplog.at_level(logging.DEBUG):
        _app.logger.debug('test')
        assert caplog.text
