extenstion
=================

sea 自带了一些扩展，它们位于 ``sea/contrib/extensions/`` 中

cache
^^^^^^

``cache.Cache`` 一个 cache 的代理，它内部维持了一个 ``_backend``，其类型由 config 的 ``CACHE_BACKEND`` 指定。目前 sea 支持以下两种

* Simple: 基于 Python dict 的实现
* Redis: Redis 存储

若想要实现自己的 cache backend 需要继承抽象基类 ``BaseBackend``。

当调用 ``cache.Cache`` 实例的这些 ``'get', 'get_many', 'set', 'set_many', 'delete', 'delete_many', 'expire', 'expireat', 'clear', 'ttl', 'exists'``
 方法时会直接代理到 ``_backend`` 上去。

除此之外，``cache.Cache`` 还提供了 memoization。通过 ``cached`` 装饰器可以缓存函数的执行结果，最好的例子便是元类 ``orator.cache_model.ModelMeta``。

orator
^^^^^^^

``sea.contrib.extensions.orator.cache_model.ModelMeta`` 是一个元类，它可以为你的 model 增加缓存功能::

    from sea.contrib.extensions.orator import cache_model


    class User(Model, metaclass=cache_model.ModelMeta):

        __table__ = 'users' # 数据库对应表名
        __dates__ = ['birth_date', 'death_date'] # 日期字段
        __fillable__ = ['address', 'telephone'] # 允许 mass assignment 的字段

缓存将会存储在 ``config`` 中指定的介质中

celery
^^^^^^^

使用方法和 `celery.Celery` 相同

consul
^^^^^^^

使用 ``config`` 中的 ``CONSUL_`` 开头的变量进行配置，对 ``consul.Consul`` 对象的方法进行代理

redis
^^^^^^

使用 ``config`` 中的 ``REDIS_`` 开头的变量进行配置，对 ``redis.StrictRedis`` 对象的方法进行代理

sentry
^^^^^^^

接入 sentry
