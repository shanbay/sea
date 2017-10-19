import functools
import logging

from sea import current_app
from sea.extensions import AbstractExtension
from . import backends


logger = logging.getLogger(__name__)
DEFAULT_KEY_TYPES = (str, int, float, bool)


def norm_cache_key(v):
    if isinstance(v, type):
        return v.__name__
    if isinstance(v, bytes):
        return v.decode()
    if v is None or isinstance(v, DEFAULT_KEY_TYPES):
        return str(v)
    else:
        raise ValueError('only str, int, float, bool can be key')


def default_key(f, *args, **kwargs):
    keys = [norm_cache_key(v) for v in args]
    keys += sorted(
        ['{}={}'.format(k, norm_cache_key(v)) for k, v in kwargs.items()])
    return 'default.{}.{}.{}'.format(f.__module__, f.__name__, '.'.join(keys))


class CacheNone:
    pass


class Cache(AbstractExtension):

    PROTO_METHODS = ('get', 'get_many', 'set', 'set_many', 'delete',
                     'delete_many', 'expire', 'expireat', 'clear',
                     'ttl', 'exists')

    def __init__(self):
        self._backend = None

    def init_app(self, app):
        opts = app.config.get_namespace('CACHE_').copy()
        backend_cls = getattr(backends, opts.pop('backend'))
        prefix = opts.pop('prefix', app.name)
        # default ttl: 60 * 60 * 48
        self._backend = backend_cls(
            prefix=prefix, default_ttl=opts.pop('default_ttl', 172800),
            **opts)

    def __getattr__(self, name):
        if name in self.PROTO_METHODS:
            return getattr(self._backend, name)
        raise AttributeError


class cached:
    def __init__(self, func=None, ttl=None, cache_key=default_key,
                 unless=None, fallbacked=None, cache_none=False):
        self.ttl = ttl
        self.cache_key = cache_key
        self.unless = unless
        self.fallbacked = fallbacked
        self.cache_none = cache_none
        if func is not None:
            func = self.decorator(func)
        self.func = func

    def __call__(self, *args, **kwargs):
        if self.func is not None:
            return self.func(*args, **kwargs)
        f = args[0]
        return self.decorator(f)

    def decorator(self, f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if callable(self.unless) and self.unless(*args, **kwargs):
                return f(*args, **kwargs)
            cache = current_app.extensions.cache
            key = wrapper.make_cache_key(*args, **kwargs)
            rv = cache.get(key)
            if rv is None:
                rv = f(*args, **kwargs)
                if self.cache_none and rv is None:
                    rv = CacheNone
                if rv is not None:
                    cache.set(key, rv, ttl=wrapper.ttl)
                if callable(self.fallbacked):
                    self.fallbacked(wrapper, rv, *args, **kwargs)
            if self.cache_none and rv is CacheNone:
                return None
            return rv

        def make_cache_key(*args, **kwargs):
            if callable(self.cache_key):
                key = self.cache_key(f, *args, **kwargs)
            else:
                key = self.cache_key
            return key

        wrapper.uncached = f
        wrapper.ttl = self.ttl
        wrapper.make_cache_key = make_cache_key

        return wrapper

    def __getattr__(self, name):
        return getattr(self.func, name)
