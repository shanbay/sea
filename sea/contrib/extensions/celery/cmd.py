import os
import sys

from celery.__main__ import main as celerymain

from sea.cli import jobm
from sea import create_app


def celery(argv, app):
    if argv[0] == "inspect":
        import importlib
        config_name = os.environ.get("SEA_ENV")
        config = importlib.import_module('configs.{}'.format(config_name))
        extensions = importlib.import_module("app.extensions")
        celeryapp = getattr(extensions, app)
        celeryapp.config_from_object(config, namespace=f"{app}_".upper())
    else:
        create_app()
    sys.argv = (
        ["celery"] + argv + ["-A", "app.extensions:{app}".format(app=app)]
    )
    return celerymain()


@jobm.job("async_task", proxy=True, inapp=False,
          help="invoke celery cmds for async tasks")
def async_task(argv):
    return celery(argv, "async_task")


@jobm.job("bus", proxy=True, inapp=False, help="invoke celery cmds for bus")
def bus(argv):
    return celery(argv, "bus")
