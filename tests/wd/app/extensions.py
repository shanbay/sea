from cachext.exts import Cache
from peeweext.sea import Peeweext
from sea.contrib.extensions.celery import Celery

cache = Cache()
pwx = Peeweext()
celeryapp = Celery()
