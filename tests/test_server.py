import inspect
import os
import signal
import threading
import time
from unittest import mock
import pytest
import asyncio

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
    # In multiprocessing mode, prometheus dir must be set
    try:
        os.mkdir("/tmp/prometheus_metrics")
        os.environ.setdefault("PROMETHEUS_MULTIPROC_DIR", "/tmp/prometheus_metrics")

        app.config["PROMETHEUS_PORT"] = 9092

        from sea.server.multiprocessing import Server

        s = Server(app)
        assert not s._stopped

        def log_started(s):
            app.logger.warning("started!")

        def log_stopped(s):
            app.logger.warning("stopped!")

        server_started.connect(log_started)
        server_stopped.connect(log_stopped)

        def kill_later(sec):
            time.sleep(sec)
            os.kill(os.getpid(), signal.SIGINT)

        # 3 seconds to wait before killing server
        threading.Thread(target=kill_later, args=[3]).start()

        # with mock.patch("time.sleep", new=_mocked):
        assert s.run()
        assert s._stopped

        content = logstream.getvalue()
        assert "stopped!" in content
    finally:
        os.rmdir("/tmp/prometheus_metrics")


@pytest.mark.asyncio
async def test_asyncio_server(app, logstream):
    from sea.server.asyncio import Server

    s = Server(app)
    assert not s._stopped

    def log_started(s):
        app.logger.warning("started!")

    def log_stopped(s):
        app.logger.warning("stopped!")

    server_started.connect(log_started)
    server_stopped.connect(log_stopped)

    async def stop_server_later(sec):
        await asyncio.sleep(sec)
        await s._stop_handler()
        # server_stopped.send(s)

    # Run the server and stop it after 3 seconds in parallel
    await asyncio.gather(s.run(), stop_server_later(3))

    # asyncio.create_task(stop_server_later(3))

    # await s.run()
    assert s._stopped

    content = logstream.getvalue()
    assert "started!" in content
    # assert "started!" in content and "stopped!" in content
