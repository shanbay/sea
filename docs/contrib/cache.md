# Cache

## TL;DR;

`configs/default/cache.py`

```python
CACHE_BACKEND = 'Redis'
CACHE_HOST = 'localhost'
```

`app/extensions`

```python
from sea.contrib.extensions.cache import Cache
cache = Cache()
```

`testcode.py`

```python
from app.extensions import cache

count = 1

@cache.cached
def query():
    count += 1
    return count
```

```sh
$ sea c
>>> welcome to sea console

In [1]: import testcode

In [2]: testcode.query()
Out[2]: 2

In [3]: testcode.query()
Out[3]: 2

In [4]: testcode.query.uncached()
Out[4]: 3
```


## 配置

`CACHE_BACKEND`

> Cache 的实现，目前有：`Simple` 和 `Redis`

`CACHE_PREFIX`

> cache 中 key 的前缀，默认为 `app.name`

`CACHE_DEFAULT_TTL`

> 默认的 ttl， 默认值为 172800


## 接口

在 `app`
