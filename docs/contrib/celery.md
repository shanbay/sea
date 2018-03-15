# Celery

## Quick Start

config 里

```python
CELERY_BROKER_URL = 'redis://redis:5672/8'

CELERY_IMPORTS = ['app.tasks']
```

`app/extensions.py`

```python
from sea.contrib.extensions.celery import Celery

celeryapp = Celery()
```

`app/tasks.py`

```python
from app.extensions import celeryapp

@celeryapp.task
def task1(arg1, arg2):
    pass
```

```python
from app.tasks import task1

task1.delay(arg1=1, arg2=2)
```

## 配置

具体配置见[celery 文档](http://docs.celeryproject.org/en/v4.1.0/userguide/configuration.html)

配置的格式为：

`CELERY_{Upper(lowcase_setting_name)}`，其中 lowcase_setting_name 为文档中小写配置名，转化为大写。例如

`imports` => `CELERY_IMPORTS`
`accept_content` => `CELERY_ACCEPT_CONTENT`
`broker_url` => `CELERY_BROKER_URL`
`task_acks_late` => `CELERY_TASK_ACKS_LATE`

## 运行

`sea celery`，会自动设置 `-A` 参数，并调用原生 `celery`。例如：

`sea celery worker` => `celery worker -A 'app.extensions:celeryapp'`
