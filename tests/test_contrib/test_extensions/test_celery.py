from sea.contrib.extensions import celery


def test_celery(app):
    c = celery.Celery()
    c.init_app(app)
    # assert c.conf.broker_url == 'redis://localhost:6379/2'
