import sys

from celery.__main__ import main as celerymain

from sea.cli import jobm


def celery(argv, app):
    sys.argv = (
        ["celery"] + argv + ["-A", "app.extensions:{app}".format(app=app)]
    )
    return celerymain()


@jobm.job("async_task", proxy=True, help="invoke celery cmds for async tasks")
def async_task(argv):
    return celery(argv, "async_task")


@jobm.job("bus", proxy=True, help="invoke celery cmds for bus")
def bus(argv):
    return celery(argv, "bus")
