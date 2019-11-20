import os
import sys

from celery.__main__ import main as celerymain

from sea import create_app
from sea.cli import jobm
from sea.utils import import_string


def celery(argv, app):
    if argv[0] == "inspect":
        config_name = os.environ.get("SEA_ENV")
        config = import_string('configs.{}'.format(config_name))
        celeryapp = import_string(
            "sea.contrib.extensions.celery.empty_celeryapp.capp")
        celeryapp.config_from_object(
            config, namespace="{}_".format(app).upper())
        sys.argv = (
            ["celery"] + argv + ["-A",
                                 "sea.contrib.extensions.celery.empty_celeryapp.capp".format(app=app)]
        )
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
