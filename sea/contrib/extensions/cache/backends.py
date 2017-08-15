import abc
import pickle
import time


class BaseBackend(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get(self, key):
        raise NotImplementedError

    @abc.abstractmethod
    def get_many(self, keys):
        raise NotImplementedError

    @abc.abstractmethod
    def set(self, key, value, ttl=None):
        raise NotImplementedError

    @abc.abstractmethod
    def set_many(self, mapping):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, key):
        raise NotImplementedError

    @abc.abstractmethod
    def delete_many(self, keys):
        raise NotImplementedError

    @abc.abstractmethod
    def expire(self, key, seconds):
        raise NotImplementedError

    @abc.abstractmethod
    def expireat(self, key, timestamp):
        raise NotImplementedError

    @abc.abstractmethod
    def clear(self):
        raise NotImplementedError


class Redis(BaseBackend):

    def __init__(self, *args, **kwargs):
        import redis
        self._client = redis.StrictRedis(*args, **kwargs)

    def get(self, key):
        return self._client.get(key)

    def get_many(self, keys):
        return self._client.mget(keys)

    def set(self, key, value, ttl=None):
        return self._client.set(key, value, ex=ttl)

    def set_many(self, mapping):
        return self._client.mset(mapping)

    def delete(self, key):
        return self._client.delete(key)

    def delete_many(self, keys):
        return self._client.delete(keys)

    def expire(self, key, seconds):
        return self._client.expire(key, seconds)

    def expireat(self, key, timestamp):
        return self._client.expireat(key, int(timestamp))

    def clear(self):
        return self._client.flushdb()


class Simple(BaseBackend):

    def __init__(self, threshold=500, default_ttl=600):
        self._cache = {}
        self.threshold = threshold
        self.default_ttl = default_ttl

    def _ttl2expire(self, ttl):
        if ttl is None:
            ttl = self.default_ttl
        now = int(time.time())
        return now + ttl

    def _expired(self, ts):
        now = int(time.time())
        return now > ts

    def _prune(self):
        toremove = []
        for k, (exp, v) in self._cache.items():
            if self._expired(exp):
                toremove.append(k)
        for k in toremove:
            self._cache.pop(k, None)
        return len(self._cache)

    def get(self, key):
        exp, v = self._cache.get(key, (None, None))
        if exp is None:
            return None
        if self._expired(exp):
            self._cache.pop(key)
            return None
        return pickle.loads(v)

    def get_many(self, keys):
        return [self.get(k) for k in keys]

    def set(self, key, value, ttl=None):
        if len(self._cache) >= self.threshold \
                and self._prune() >= self.threshold:
            return False
        self._cache[key] = (
            self._ttl2expire(ttl), pickle.dumps(
                value, pickle.HIGHEST_PROTOCOL))
        return True

    def set_many(self, mapping):
        for k, v in mapping.items():
            self.set(k, v)
        return True

    def delete(self, key):
        try:
            self._cache.pop(key)
            return 1
        except KeyError:
            pass
        return 0

    def delete_many(self, keys):
        return sum([self.delete(k) for k in keys])

    def expire(self, key, seconds):
        try:
            exp, v = self._cache[key]
        except KeyError:
            return 0
        self._cache[key] = (self._ttl2expire(seconds), v)
        return 1

    def expireat(self, key, timestamp):
        try:
            exp, v = self._cache[key]
        except KeyError:
            return 0
        self._cache[key] = (timestamp, v)
        return 1

    def clear(self):
        return self._cache.clear()
