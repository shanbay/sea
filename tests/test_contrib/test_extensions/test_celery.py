from sea import create_app
from sea.contrib.extensions import celery


def test_celery():
    c = celery.Celery()
    c.init_app(create_app('./tests/wd'))
    assert c.conf.broker_url == 'redis://localhost:6379/2'
