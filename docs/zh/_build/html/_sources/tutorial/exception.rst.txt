exception
=================

sea 在 ``sea.exceptions`` 中提供了异常基类 ``RpcException``，他是与中间件 ``sea.middleware.RpcErrorMiddleware`` 配合使用的

此基类主要有以下两个属性

1) ``code`` 必须为 gRPC 定义的 ``code``

* StatusCode.OK
* StatusCode.CANCELLED
* StatusCode.UNKNOWN
* StatusCode.INVALID_ARGUMENT
* StatusCode.DEADLINE_EXCEEDED
* StatusCode.NOT_FOUND
* StatusCode.ALREADY_EXISTS
* StatusCode.PERMISSION_DENIED
* StatusCode.RESOURCE_EXHAUSTED
* StatusCode.FAILED_PRECONDITION
* StatusCode.ABORTED
* StatusCode.OUT_OF_RANGE
* StatusCode.UNIMPLEMENTED
* StatusCode.INTERNAL
* StatusCode.UNAVAILABLE
* StatusCode.DATA_LOSS
* StatusCode.UNAUTHENTICATED

2) ``details`` 异常信息

自定义异常 Example::

    class NotFoundException(RpcException):

        code = grpc.StatusCode.NOT_FOUND
        details = 'Not Found'
