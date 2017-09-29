configuation
=================

sea 支持多种环境配置，``default`` ``development`` ``testing`` 等。你需要将他们置于工程根目录的 ``configs`` 目录下，如下面这样::

    configs
    |-- default
    |   |-- celery.py
    |   |-- __init__.py
    |   |-- orator.py
    |-- development
    |   |-- __init__.py
    |-- __init__.py
    |-- testing
        |-- __init__.py


sea 在启动时会根据环境变量 ``SEA_ENV`` 来决定使用哪份配置文件，就像这样 ``SEA_ENV=testing sea server``。此环境变量的值应当为 ``configs`` 下的某一目录名称。默认是使用 ``development`` 配置。

配置应当以变量的形式给出，变量名需大写 比如 ``CACHE_BACKEND = redis``

sea 会将所有的配置构建成 ``sea.config.Config`` 类的对象，你可以通过 ``Config`` 类的实例的 ``get_namespace`` 方法获取以某一命名空间开头的配置变量

例如在 sea 的 redis 扩展中就是这样获取配置的::

    class Redis(AbstractExtension):

        def init_app(self, app):
            opts = app.config.get_namespace('REDIS_')
            self._pool = redis.ConnectionPool(**opts)
            self._client = redis.StrictRedis(connection_pool=self._pool)

Basic
^^^^^^^

* DEBUG: ``True`` or ``False`` 是否显示调试信息
* TESTING:
* TIMEZONE: 时区 如 ``UTC``


Cache
^^^^^^

* CACHE_BACKEND: 某种缓存系统 如 ``Redis``
* CACHE_PREFIX: 缓存 Key 前缀
* CACHE_HOST: 主机名
* CACHE_DB: 数据库
* CACHE_PORT: 端口号
* CACHE_PASSWORD: 连接密码


gRPC
^^^^^

* GRPC_WORKERS: workers 数量
* GRPC_HOST:
* GRPC_PORT: grpc server 监听端口
* GRPC_LOG_LEVEL: grpc 日志级别
* GRPC_LOG_HANDLER: ``logging.StreamHandler()``
* GRPC_LOG_FORMAT: 日志格式 如 ``'[%(asctime)s %(levelname)s in %(module)s] %(message)s'``

Celery
^^^^^^^

* CELERY_BROKER_URL: 如 ``redis://localhost:6379/1``

* CELERY_TASK_QUEUES::

    {
        'demo.direct': {
            'exchange': 'demo-exchange',
            'exchange_type': 'direct',
            'routing_key': 'demo.direct',
        },
    }

* CELERY_TASK_DEFAULT_QUEUE: 如 'demo.celery'

* CELERY_TASK_ROUTES::

    {
        'app.tasks.*': {
            'queue': CELERY_TASK_DEFAULT_QUEUE,
        },
    }

* CELERY_IMPORTS = ['app.tasks']
