import inspect
import os
import signal
import threading
from unittest import mock

from sea.signals import server_started, server_stopped


def test_thread_server(app, logstream):
    from sea.server.threading import Server

    s = Server(app)
    assert not s._stopped

    def log_started(s):
        app.logger.warning("started!")

    def log_stopped(s):
        app.logger.warning("stopped!")

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


def test_multiprocessing_server(app, logstream):
    from sea.server.multiprocessing import Server

    s = Server(app)
    assert not s._stopped

    def log_started(s):
        app.logger.warning("started!")

    def log_stopped(s):
        app.logger.warning("stopped!")

    def _mocked(*args, **kwargs):
        curframe = inspect.currentframe()
        caller_name = inspect.getouterframes(curframe, 2)[1][3]
        if caller_name == "run":
            os.kill(os.getpid(), signal.SIGINT)

    server_started.connect(log_started)
    server_stopped.connect(log_stopped)

    with mock.patch("time.sleep", new=_mocked):
        assert s.run()
        process_num = os.open("ps ax | grep sea | grep -v grep | wc -l")
        print(process_num)
        assert s._stopped

    content = logstream.getvalue()
    assert "started!" in content and "stopped!" in content
