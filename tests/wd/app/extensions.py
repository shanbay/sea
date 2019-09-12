from cachext.exts import Cache
from peeweext.sea import Peeweext
from sea.contrib.extensions.celery import AsyncTask, Bus

cache = Cache()
pwx = Peeweext()
async_task = AsyncTask()
bus = Bus()
