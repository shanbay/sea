middleware
=================

sea 的中间件需要在配置文件中进行注册::

    MIDDLEWARES = [
        'sea.middleware.ServiceLogMiddleware',
        'sea.middleware.RpcErrorMiddleware'
    ]

Default middleware
^^^^^^^^^^^^^^^^^^^

sea 默认提供了如下几个 middleware

* RpcErrorMiddleware 拦截 ``RpcException`` 及其子类异常，并将异常信息添加至 gPRC context。

* ServiceLogMiddleware 日志记录中间件

* GuardMiddleware 拦截业务逻辑中的所有异常，并将异常信息添加至 gRPC context，``code`` 赋值为 ``grpc.StatusCode.INTERNAL`` 返回 ``default_pb2.Empty()`` (*此中间件内置于 sea 中*)

Custom middleware
^^^^^^^^^^^^^^^^^^

通过继承 ``sea.middleware.BaseMiddleware`` 并重写 ``__call__`` 方法来自定义中间件
