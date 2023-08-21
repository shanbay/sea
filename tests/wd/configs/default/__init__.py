from .peewee import *
from .async_task import *

CACHE_BACKEND = "Redis"

MIDDLEWARES = [
    "sea.middleware.ServiceLogMiddleware",
    "sea.middleware.RpcErrorMiddleware",
]

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

TIMEZONE = "Asia/Shanghai"
GRPC_GRACE = 0
GRPC_REFLECTION_SERVICES = ["helloworld.Greeter"]
PROMETHEUS_SCRAPE = True
