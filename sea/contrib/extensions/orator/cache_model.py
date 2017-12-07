from orator.orm import model
from sea import current_app
from sea.contrib.extensions import cache as cache_ext
from sea.contrib.extensions.cache import default_key


def _related_caches_key(cls, pk):
    return 'related_caches.{}.{}.{}'.format(cls.__module__, cls.__name__, pk)


def _model_caches_key(cache_version):

    def wrapper(f, *args, **kwargs):
        return '{}.{}'.format(cache_version, default_key(f, *args, **kwargs))

    return wrapper


def _register_to_related_caches(f, pk, cls, *args, **kwargs):
    cache = current_app.extensions.cache
    key = cache._backend.trans_key(_related_caches_key(cls, pk))
    redis = cache._backend._client
    cached_key = cache._backend.trans_key(
        f.make_cache_key(cls, *args, **kwargs))
    redis.sadd(key, cached_key)
    redis.expire(key, cache._backend.default_ttl)
    return True


def _find_register(f, ins, cls, *args, **kwargs):
    return _register_to_related_caches(f, args[0], cls, *args, **kwargs)


def _find_by_register(f, ins, cls, *args, **kwargs):
    if ins is None or ins is cache_ext.CacheNone:
        return True
    return _register_to_related_caches(f, getattr(ins, ins.__primary_key__),
                                       cls, *args, **kwargs)


def _bulk_register_to_related_caches(cls, key_model_map):
    cache = current_app.extensions.cache
    redis = cache._backend._client
    for cached_key, ins in key_model_map.items():
        key = cache._backend.trans_key(
            _related_caches_key(cls, getattr(ins, ins.__primary_key__)))
        cached_key = cache._backend.trans_key(cached_key)
        redis.sadd(key, cached_key)
        redis.expire(key, cache._backend.default_ttl)
    return True


def _clear_related_caches(instance):
    cache = current_app.extensions.cache
    key = cache._backend.trans_key(
        _related_caches_key(instance.__class__,
                            getattr(instance, instance.__primary_key__)))
    redis = cache._backend._client
    related_caches = redis.smembers(key)
    if related_caches:
        redis.delete(*related_caches)
    return True


def _pk_is_list(cls, pk, *args, **kwargs):
    return isinstance(pk, list)


class ModelMeta(model.MetaModel):

    def __new__(mcls, name, bases, kws):
        max_find_many_cache = kws.get('__max_find_many_cache__', 10)

        cache_version = kws.get('__cache_version__', '1.0')

        @classmethod
        @cache_ext.cached(fallbacked=_find_register,
                          cache_key=_model_caches_key(cache_version),
                          unless=_pk_is_list, cache_none=True)
        def find(cls, pk, columns=None):
            if isinstance(pk, list) and pk and len(pk) <= max_find_many_cache:
                cache = current_app.extensions.cache
                keymap = {i: find.__func__.make_cache_key(cls, i) for i in pk}
                rv = cache.get_many(keymap.values())
                models = dict(zip(pk, rv))
                misspks = [
                    i for i, m in models.items()
                    if m is None]
                models = {
                    k: m for k, m in models.items()
                    if not (m is cache_ext.CacheNone or m is None)}
                if not misspks:
                    return cls().new_collection(models.values())
                missed = super(cls, cls).find(misspks, columns)
                missed = {getattr(m, m.__primary_key__): m for m in missed}
                models.update(missed)
                key_model_map = {keymap[i]: m for i, m in missed.items()}
                cache.set_many(key_model_map)
                _bulk_register_to_related_caches(cls, key_model_map)
                return cls().new_collection(list(models.values()))
            return super(cls, cls).find(pk, columns)

        @classmethod
        @cache_ext.cached(fallbacked=_find_by_register,
                          cache_key=_model_caches_key(cache_version),
                          cache_none=True)
        def find_by(cls, name, val, columns=None):
            return super(cls, cls).find_by(name, val, columns)

        kws.update({
            'find': find,
            'find_by': find_by,
            '__cache_version__': cache_version,
        })
        return super().__new__(mcls, name, bases, kws)

    def __init__(cls, name, bases, kws):
        super().__init__(name, bases, kws)
        cls.saved(_clear_related_caches)
        cls.deleted(_clear_related_caches)
