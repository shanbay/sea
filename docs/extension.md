# 扩展

sea 提供了扩展的机制，方便集成外部服务。

### 使用扩展

1. 在 `app/extensions.py` 里初始化一个所需要的扩展的实例，如：

```python
from peeweext import Peeweext

pw = Peeweext()
```

2. 在代码中其他地方使用该扩展，只需要从 `app.extensions` 中 import 刚刚初始化的实例，如：

```python
from app.extensions import pw

pw.somethed()
```

### 编写扩展

定义一个扩展类，实现`init_app` 方法，该方法接受一个参数 `app`

在sea初始化的过程中，会将 `current_app` 作为 `app` 参数传入给 `init_app`

例如，实现一个简单的 `Redis` 扩展

```python
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

```

该 Redis 扩展会根据 `REDIS_` 开头的config初始化 `redis.StrictRedis` 对象。

在使用中，调用该扩展的任何其他方法，会转发给 `redis.StrictRedis` 对象。所以在使用中，使用该扩展的实例和使用`redis.StrictRedis`实例没有区别。
