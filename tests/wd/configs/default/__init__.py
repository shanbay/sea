from . import celery as CELERY
from . import orator as ORATOR

CACHE_BACKEND = 'Redis'

MIDDLEWARES = [
    'sea.middleware.ServiceLogMiddleware',
    'sea.middleware.RpcErrorMiddleware'
]

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
