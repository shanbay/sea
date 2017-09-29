application
=================

``sea/app.py`` 中的 ``Sea`` 类是 sea 框架的应用主体，他是在 ``sea/__init__.py`` 中的 ``create_app`` 函数被实例化的，并且通过 Python 的模块机制保证全局单例，可以通过 `sea/__init__.py` 的 ``current_app`` 函数获取此 app 对象

你可以通过 app 对象获取许多有用的信息

* app.config 获取配置信息
* app.servicers 获取已注册的 servicers
* app.extensions 获取扩展
* app.middlewares 获取中间件

也可以通过 ``app`` 实例的 ``register_extension``, ``register_servicer`` 等方法进行启动后的动态装载
