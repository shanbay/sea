from . import celery as CELERY
from . import orator as ORATOR

CACHE_BACKEND = 'Redis'

MIDDLEWARES = [
    'sea.middleware.ServiceLogMiddleware',
    'sea.middleware.RpcErrorMiddleware'
]
