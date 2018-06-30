# 测试

Sea 内建对 pytest 测试框架的支持，

## 编写测试

**fixture**

- `sea.test.fixtures.app`

**测试 grpc 接口**

可以利用 `sea.test.stub.Stub` 来做grpc接口的测试。

例如：

定义如下 grpc servicer

```python
class HelloServicer(metaclass=ServicerMeta):

    def return_error(self, request, context):
        raise BadRequestException()

    def return_normal(self, request, context):
        return context.invocation_metadata()
```

测试以上 servicer

```python
from sea.test.stub import Stub

stub = Stub(HelloServicer())
data = {'a': 2}
res = stub.return_normal(message, metadata=data)

assert stub.ctx.invocation_metadata() == data
assert stub.ctx.code == grpc.StatusCode.OK
```

## 运行测试

```
$ sea test
```
