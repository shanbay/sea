import os
from sea.utils import import_string
from celery import Celery


capp = Celery()


def load_config(app, without_imports=True):
    config_name = os.environ.get("SEA_ENV")
    config = import_string('configs.{}'.format(config_name))
    capp.config_from_object(config, namespace="{}_".format(app).upper())
    if without_imports:
        capp._conf["{}_imports".format(app).upper()] = []
