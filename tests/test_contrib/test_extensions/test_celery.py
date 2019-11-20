import os
import sys
import mock
import importlib
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
        extensions = importlib.import_module("app.extensions")
        celeryapp = extensions.async_task
        assert celeryapp.conf["broker_url"] is None
    else:
        """一起跑（app.extensions已经被初始化）"""
        extensions = importlib.import_module("app.extensions")
        celeryapp = extensions.async_task
        assert celeryapp.conf["broker_url"] == 'redis://localhost:6379/2'

    with mock.patch("sea.contrib.extensions.celery.cmd.celerymain") as mocked:
        async_task("inspect ping -d wd@$HOSTNAME".split())
        assert mocked.called
    assert celeryapp.conf["broker_url"] == "redis://localhost:6379/2"
    assert celeryapp.conf["TASK_DEFAULT_QUEUE"] == "wd.celery"
