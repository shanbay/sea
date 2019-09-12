from sea.contrib.extensions.celery import AsyncTask, Bus


def test_celery(app):
    AsyncTask().init_app(app)
    Bus().init_app(app)
    # assert c.conf.broker_url == 'redis://localhost:6379/2'
