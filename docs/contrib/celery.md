# Celery

## Quick Start

config 里

```python
# 异步任务
ASYNC_TASK_BROKER_URL = 'redis://redis:5672/8'
ASYNC_TASK_IMPORTS = ['app.tasks']

# bus 消息
BUS_BROKER_URL = 'redis://redis:5672/8'
BUS_IMPORTS = ['app.buses']
```

`app/extensions.py`

```python
from sea.contrib.extensions.celery import AsyncTask, Bus

async_task = AsyncTask()
bus = Bus()
```

`app/async_tasks.py`

```python
from app.extensions import async_task

@async_task.task
def task1(arg1, arg2):
    pass
```

```python
from app.tasks import task1

task1.delay(arg1=1, arg2=2)
```

`app/buses.py`

```python
from app.extensions import bus

# 接收其他项目发出的 bus 消息
@bus.task(name="buses.message.create")
def handle_message(**kwargs):
    print(kwargs)

# 发 bus 消息给其他项目
@bus.task(name="buses.to.others")
def send_bus(**kwargs):
    pass
```

## 配置

具体配置见[celery 文档](http://docs.celeryproject.org/en/v4.1.0/userguide/configuration.html)

配置的格式为：

`ASYNC_TASK/BUS_{Upper(lowcase_setting_name)}`，其中 lowcase_setting_name 为文档中小写配置名，转化为大写。例如

`imports` => `ASYNC_TASK/BUS_IMPORTS`
`accept_content` => `ASYNC_TASK/BUS_ACCEPT_CONTENT`
`broker_url` => `ASYNC_TASK/BUS_BROKER_URL`
`task_acks_late` => `ASYNC_TASK/BUS_TASK_ACKS_LATE`

## 运行

`sea async_task/bus`，会自动设置 `-A` 参数，并调用原生 `celery`。例如：

`sea celery async_task` => `celery worker -A 'app.extensions:async_task'`
`sea celery bus` => `celery worker -A 'app.extensions:bus'`
