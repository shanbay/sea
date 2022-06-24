import os
import sys
from unittest import mock

from sea import import_string
from sea.contrib.extensions.celery import AsyncTask, Bus
from sea.contrib.extensions.celery.cmd import async_task, bus


def test_celery(app):
    AsyncTask().init_app(app)
    Bus().init_app(app)
    with mock.patch("sea.contrib.extensions.celery.cmd.celerymain"):
        async_task(["worker"])
        bus(["worker"])
    # assert c.conf.broker_url == 'redis://localhost:6379/2'


def test_celery_no_app():
    """需要独立于其他测试的session单独跑一次"""
    root_path = os.path.join(os.path.dirname(__file__).replace(
        '/test_contrib/test_extensions', ''), 'wd')

    if root_path not in sys.path:
        """单独跑"""
        os.environ.setdefault('SEA_ENV', 'testing')
        sys.path.append(root_path)
    celeryapp = import_string(
        "sea.contrib.extensions.celery.empty_celeryapp.capp")
    assert celeryapp.conf["broker_url"] is None

    with mock.patch("sea.contrib.extensions.celery.cmd.celerymain") as mocked:
        async_task("inspect ping -d wd@$HOSTNAME".split())
        assert mocked.called
    assert celeryapp.conf["broker_url"] == "redis://localhost:6379/2"
    assert celeryapp.conf["TASK_DEFAULT_QUEUE"] == "wd.celery"
    assert celeryapp.conf["imports"] == []
    assert celeryapp.conf["IMPORTS"] == []
    assert celeryapp.conf["async_task_imports".upper()] == []
