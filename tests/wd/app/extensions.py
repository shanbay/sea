from sea.contrib.extensions.cache import Cache
from sea.contrib.extensions.orator import Orator
from sea.contrib.extensions.celery import Celery

cache = Cache()
db = Orator()
celeryapp = Celery()
