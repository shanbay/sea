import mock
from sea.contrib.extensions.celery import AsyncTask, Bus
from sea.contrib.extensions.celery.cmd import async_task, bus


def test_celery(app):
    AsyncTask().init_app(app)
    Bus().init_app(app)
    with mock.patch("sea.contrib.extensions.celery.cmd.celerymain"):
        async_task(["worker"])
        bus(["worker"])
    # assert c.conf.broker_url == 'redis://localhost:6379/2'
