import inspect
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
        app.logger.warn("started!")

    def log_stopped(s):
        app.logger.warn("stopped!")

    def _mocked(*args, **kwargs):
        curframe = inspect.currentframe()
        caller_name = inspect.getouterframes(curframe, 2)[1][3]
        if caller_name == "run":
            os.kill(os.getpid(), signal.SIGINT)

    server_started.connect(log_started)
    server_stopped.connect(log_stopped)

    with mock.patch("time.sleep", new=_mocked):
        assert s.run()
        assert threading.active_count() > 1
        assert s._stopped

    content = logstream.getvalue()
    assert "started!" in content and "stopped!" in content
