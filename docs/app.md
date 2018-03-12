# App

每个`Sea`项目都有一个 app，它是定义在 `app/__init__.py` 中的 `App` 类的实例。
`App` 是 `sea.app.BaseApp` 的子类。

## 获取当前 app

在项目代码中，可以通过 `sea.current_app` 来获得当前 app

## class sea.app.BaseApp

`config_class` (class):

> app 使用的 config 类， 默认为 `sea.config.Config`。可以通过继承扩展 Config

`debug` (instance):

> 是否打开了 debug，默认为 False

`testing` (instance):

> 是否为测试，默认为 False

`tz` (instance):

> 时区，默认为 'UTC'

`logger` (instance):

> `logging.Logger` 的实例，用于打日志。
> 例如： `app.logger.info('Hello')`

`extensions` (instance):

> 当前项目的所有扩展，例如在`extensions.py` 中如果定义了 `cache = Cache()`，那么就可以利用 `app.extensions.cache` 来使用该 cache 扩展

`middlewares` (instance):

> 当前项目所有的 middlewares。按照顺序为“由内到外”排列
