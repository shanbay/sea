import pytest
import time
from unittest import mock

from sea.contrib.extensions import cache
from sea.contrib.extensions.cache import backends
from sea import create_app, current_app


total = 0


def test_default_key():
    def tmp(a, b=2, c=None):
        return a, b, c

    with pytest.raises(ValueError):
        cache.default_key(tmp, [], b=b'hello')

    key = cache.default_key(tmp, b'hello', b=True, c=None)
    assert key == '{}.{}.{}'.format(tmp.__module__, tmp.__name__, 'hello.b=True.c=None')


def test_cache():
    c = cache.Cache()
    assert c._backend is None
    c.init_app(create_app('./tests/wd'))
    assert isinstance(c._backend, backends.Simple)

    def true_if_gte_10(num):
        return num >= 10

    @c.cached(unless=true_if_gte_10)
    def incr1(num):
        global total
        total += num
        return total

    rt = incr1(1)
    assert rt == 1
    rt = incr1(1)
    assert rt == 1
    rt = incr1(10)
    assert rt == 11

    @c.cached(cache_key='testkey')
    def incr2(num):
        global total
        total += num
        return total

    with mock.patch.object(c._backend, 'get', return_value=100) as mocked:
        incr2(10)
        mocked.assert_called_once_with('{}.{}'.format(current_app().name, 'testkey'))

    with pytest.raises(AttributeError):
        c.nosuchmethod()

    with mock.patch.object(c._backend, 'set', return_value=True) as mocked:
        c.set('key', 'value')
        mocked.assert_called_once_with('key', 'value')


def test_base_backend():
    c = backends.BaseBackend
    for m in ('get', 'get_many', 'set_many', 'delete', 'delete_many'):
        with pytest.raises(NotImplementedError):
            m = getattr(c, m)
            m(mock.Mock(), 'key')

    for m in ('set', 'expire', 'expireat'):
        with pytest.raises(NotImplementedError):
            m = getattr(c, m)
            m(mock.Mock(), 'key', 'value')

    with pytest.raises(NotImplementedError):
        c.clear(mock.Mock())


def test_redis_backend():
    c = backends.Redis()
    with mock.patch.object(c, '_client') as mocked:
        mapping = {
            'get': 'get', 'get_many': 'mget', 'set_many': 'mset',
            'delete': 'delete', 'delete_many': 'delete'
        }
        for k, v in mapping.items():
            getattr(c, k)('key')
            getattr(mocked, v).assert_called_with('key')

        mapping = {
            'expire': 'expire', 'expireat': 'expireat'
        }
        for k, v in mapping.items():
            getattr(c, k)('key', 10)
            getattr(mocked, v).assert_called_with('key', 10)
        c.set('key', 'value')
        mocked.set.assert_called_with('key', 'value', ex=None)
        c.clear()
        mocked.flushdb.assert_called_with()


def test_simple_backend():
    c = backends.Simple(threshold=3)
    assert c.get('key') is None
    assert c.set_many({'ka': 'va', 'kb': 'vb'})
    assert c.get_many(['ka', 'kb', 'nokey']) == ['va', 'vb', None]
    assert c.set('key', 'value', ttl=1)
    assert c.get('key') == 'value'
    assert not c.set('extra', 'value')
    time.sleep(2.1)
    assert c.set('extra', 'value')
    assert c.delete('nokey') == 0
    assert c.delete('extra') == 1
    c.set('key', 'value')
    assert c.delete_many(['extra', 'key']) == 1

    assert c.expire('key', 1) == 0
    c.set('key', 'value')
    assert c.expire('key', 1) == 1
    assert c.get('key') == 'value'
    time.sleep(2.1)
    assert c.get('key') is None
    assert c.expireat('nokey', int(time.time())) == 0
    c.set('key', 'value')
    assert c.expireat('key', int(time.time() - 1)) == 1
    assert c.get('key') is None
    c.clear()
    assert len(c._cache) == 0
