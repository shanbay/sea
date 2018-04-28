# Sentry

在 1.4.1 版本添加支持。

## Quick Start

在项目依赖中添加 `raven`，并在项目配置中设置：

```python
SENTRY_DSN = "https://username:token@sentry.io/1"
```

`app/extensions.py` 中添加 Sentry 扩展：

```python
from sea.contrib.extensions.sentry import Sentry


sentry = Sentry()
```

即可使用 Sentry 的事件追踪功能。

## 高级配置

在项目配置中定义以 `SENTRY_` 开头的变量，即可配置 Sentry 客户端

配置格式为：

`SENTRY_{Upper(lowcase_setting_name)}`，其中 lowcase_setting_name 为客户端配置项，需转化为大写。例：

`dsn` => `SENTRY_DSN`
`environment` => `SENTRY_ENVRIONMENT`

具体客户端配置，见 [Sentry Python client 文档](https://docs.sentry.io/clients/python/advanced/#client-arguments).
