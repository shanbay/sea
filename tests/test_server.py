import os
import signal
import threading
from unittest import mock

from sea.server import Server
from sea.signals import server_started, server_stopped


def test_server(app, logstream):
    s = Server(app)
    assert not s._stopped

    def log_started(s):
        app.logger.warn('started!')

    def log_stopped(s):
        app.logger.warn('stopped!')

    server_started.connect(log_started)
    server_stopped.connect(log_stopped)

    with mock.patch('time.sleep', new=lambda s: os.kill(os.getpid(), signal.SIGINT)):
        assert s.run()
        assert threading.active_count() > 1
        assert s._stopped

    content = logstream.getvalue()
    assert 'started!' in content and 'stopped!' in content
