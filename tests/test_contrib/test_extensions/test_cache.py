import pytest
import pickle
import time
from unittest import mock

from sea.contrib.extensions import cache
from sea.contrib.extensions.cache import backends


def test_default_key():
    def tmp(a, b=2, c=None):
        return a, b, c

    with pytest.raises(ValueError):
        cache.default_key(tmp, [], b=b'hello')

    key = cache.default_key(tmp, b'hello', b=True, c=None)
    assert key == 'default.{}.{}.{}'.format(tmp.__module__, tmp.__name__, 'hello.b=True.c=None')


def test_cache(app):

    c = cache.Cache()
    assert c._backend is None
    c.init_app(app)
    assert isinstance(c._backend, backends.Redis)


def test_cached(app):
    total = 0
    fallbacked_count = 0

    def true_if_gte_10(num):
        return num >= 10

    def fallbacked(f, rv, *args, **kwargs):
        nonlocal fallbacked_count
        fallbacked_count += 1
        return fallbacked_count

    @cache.cached(unless=true_if_gte_10, fallbacked=fallbacked)
    def incr1(num):
        nonlocal total
        total += num
        return total

    rt = incr1(1)
    assert rt == 1
    assert fallbacked_count == 1
    rt = incr1(1)
    assert rt == 1
    rt = incr1(10)
    assert rt == 11
    assert fallbacked_count == 1

    @cache.cached(cache_key='testkey')
    def incr2(num):
        global total
        total += num
        return total

    c = app.extensions.cache

    with mock.patch.object(c._backend, 'get', return_value=100) as mocked:
        incr2(10)
        mocked.assert_called_once_with('testkey')

    with pytest.raises(AttributeError):
        c.nosuchmethod()

    with mock.patch.object(c._backend, 'set', return_value=True) as mocked:
        c.set('key', 'value')
        mocked.assert_called_once_with('key', 'value')


def test_base_backend():
    c = backends.BaseBackend
    for m in ('get', 'get_many', 'set_many', 'delete', 'delete_many', 'ttl', 'exists'):
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
    c = backends.Redis(prefix='testapp')
    c._client.flushdb()

    assert c.get('key') is None
    assert not c.exists('key')
    assert c.set_many({'ka': 'va', 'kb': 'vb'})
    assert c.get_many(['ka', 'kb', 'nokey']) == ['va', 'vb', None]
    assert c.set('key', 'value', ttl=1)
    assert c.exists('key')
    assert c.get('key') == 'value'
    assert c._client.get('testapp.key') == pickle.dumps('value', pickle.HIGHEST_PROTOCOL)
    assert c.expireat('key', time.time() - 1) == 1
    assert c.expireat('nokey', time.time() - 1) == 0
    assert c.get('key') is None
    assert c.delete('nokey') == 0
    c.set('key', 'value')
    assert c.delete('key') == 1
    assert c.delete_many(['nokey', 'ka']) == 1
    c.set('key', 'value')
    assert c.expire('key', 2) == 1
    ttl = c.ttl('key')
    assert ttl <= 2 and ttl > 0
    assert c.clear()

    c._client.flushdb()


def test_simple_backend():
    c = backends.Simple(threshold=3)
    assert c.get('key') is None
    assert not c.exists('key')
    assert c.set_many({'ka': 'va', 'kb': 'vb'})
    assert c.get_many(['ka', 'kb', 'nokey']) == ['va', 'vb', None]
    assert c.set('key', 'value', ttl=1)
    assert c.exists('key')
    assert c.get('key') == 'value'
    assert not c.set('extra', 'value')
    aminlater = time.time() + 60
    with mock.patch('time.time', new=lambda: aminlater):
        assert c.set('extra', 'value')
    assert c.delete('nokey') == 0
    assert c.delete('extra') == 1
    c.set('key', 'value')
    assert c.delete_many(['extra', 'key']) == 1

    assert c.expire('key', 1) == 0
    c.set('key', 'value')
    assert c.expire('key', 2) == 1
    ttl = c.ttl('key')
    assert ttl <= 2 and ttl > 0
    assert c.ttl('nokey') == -2
    assert c.get('key') == 'value'
    with mock.patch('time.time', new=lambda: aminlater):
        assert c.ttl('key') == -2
        assert c.get('key') is None
    assert c.expireat('nokey', int(time.time())) == 0
    c.set('key', 'value')
    assert c.expireat('key', int(time.time() - 1)) == 1
    assert c.get('key') is None
    c.clear()
    assert len(c._cache) == 0
