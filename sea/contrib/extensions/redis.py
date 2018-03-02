import redis


class Redis:

    def __init__(self):
        self._client = None

    def init_app(self, app):
        opts = app.config.get_namespace('REDIS_')
        self._pool = redis.ConnectionPool(**opts)
        self._client = redis.StrictRedis(connection_pool=self._pool)

    def __getattr__(self, name):
        return getattr(self._client, name)
