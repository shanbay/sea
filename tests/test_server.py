import os
import signal
from unittest import mock

from sea.server import Server
from sea.register import ConsulRegister


def test_server(app):
    s = Server(app, '127.0.0.1')

    assert isinstance(s.register, ConsulRegister)
    assert not s._stopped

    with mock.patch('time.sleep', new=lambda s: os.kill(os.getpid(), signal.SIGINT)):
        assert s.run()
        assert s._stopped
