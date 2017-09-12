from sea.contrib.extensions import redis


def test_redis(app):
    r = redis.Redis()
    assert r._client is None
    r.init_app(app)
    assert isinstance(r._client, redis.redis.StrictRedis)
    assert r.ping()
