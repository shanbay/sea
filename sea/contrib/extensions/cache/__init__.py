import functools
import logging

from sea.extensions import AbstractExtension
from . import backends


logger = logging.getLogger(__name__)
DEFAULT_KEY_TYPES = (str, int, float, bool)


def _trans_key(v):
    if isinstance(v, bytes):
        return v.decode()
    if v is None or isinstance(v, DEFAULT_KEY_TYPES):
        return str(v)
    else:
        raise ValueError('only str, int, float, bool can be key')


def default_key(f, *args, **kwargs):
    keys = [_trans_key(v) for v in args]
    keys += sorted(
        ['{}={}'.format(k, _trans_key(v)) for k, v in kwargs.items()])
    return '{}.{}.{}'.format(f.__module__, f.__name__, '.'.join(keys))


class Cache(AbstractExtension):

    PROTO_METHODS = ('get', 'get_many', 'set', 'set_many', 'delete',
                     'delete_many', 'expire', 'expireat', 'clear')

    def __init__(self):
        self._backend = None

    def init_app(self, app):
        self.app = app
        opts = app.config.get_namespace('CACHE_')
        backend_cls = getattr(backends, opts.pop('backend'))
        # default ttl: 60 * 60 * 48
        self.default_ttl = opts.pop('default_ttl', 172800)
        self._backend = backend_cls(**opts)

    def cached(self, ttl=None, cache_key=default_key, unless=None):
        if ttl is None:
            ttl = self.default_ttl

        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                if callable(unless) and unless(*args, **kwargs):
                    return f(*args, **kwargs)
                key = wrapper.make_cache_key(*args, **kwargs)
                rv = self._backend.get(key)
                if rv is None:
                    rv = f(*args, **kwargs)
                    self._backend.set(key, rv, ttl=wrapper.ttl)
                return rv

            def make_cache_key(*args, **kwargs):
                if callable(cache_key):
                    key = cache_key(f, *args, **kwargs)
                else:
                    key = cache_key
                return '{}.{}'.format(self.app.name, key)

            wrapper.uncached = f
            wrapper.ttl = ttl
            wrapper.make_cache_key = make_cache_key

            return wrapper
        return decorator

    def __getattr__(self, name):
        if name in self.PROTO_METHODS:
            return getattr(self._backend, name)
        return super().__getattr__(name)
