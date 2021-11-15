import sys

from celery.__main__ import main as celerymain

from sea import create_app
from sea.cli import jobm


def celery(argv, app):
    if argv[0] == "inspect":
        from sea.contrib.extensions.celery import empty_celeryapp
        empty_celeryapp.load_config(app)
        sys.argv = (
            ["celery"]
            + ["-A", "sea.contrib.extensions.celery.empty_celeryapp.capp"]
            + argv
        )
    else:
        create_app()
        sys.argv = (
            ["celery"]
            + ["-A", "app.extensions:{app}".format(app=app)]
            + argv
        )
    return celerymain()


@jobm.job("async_task", proxy=True, inapp=False,
          help="invoke celery cmds for async tasks")
def async_task(argv):
    return celery(argv, "async_task")


@jobm.job("bus", proxy=True, inapp=False, help="invoke celery cmds for bus")
def bus(argv):
    return celery(argv, "bus")
