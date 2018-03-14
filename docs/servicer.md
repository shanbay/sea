# GRPC Servicer

Servicer 是对 grpc proto 中定义的 service 的实现

### 定义 `proto`

参考 [GRPC](https://grpc.io/) 和 [protobuf](https://developers.google.com/protocol-buffers/)

假设我们定义如下`proto`

`/path/to/proto/hello.proto`

```proto3
service Greeter {
  rpc SayHello (HelloRequest) returns (HelloReply) {}
}

message HelloRequest {
  string name = 1;
}

message HelloReply {
  string message = 1;
}
```

### 根据 `proto` 编译出 `py` 文件

在项目根目录中运行：

```
$ sea g -I/path/to/proto/ hello.proto
```

会生成两个文件 `protos/hello_pb2.py` 和 `protos/hello_pb2_grpc.py`


### 实现 service

`app/servicer.py`

```python
from sea.servicer import ServicerMeta
import hello_pb2
import hello_pb2_grpc

class Greeter(hello_pb2_grpc.GreeterServicer, metaclass=ServicerMeta):

  def SayHello(self, request, context):
    return hello_pb2.HelloReply(message='Hello, %s!' % request.name)
```

**注意点** 需要指定 metaclass 为 `sea.servicer.ServicerMeta`

### 运行

在项目根目录中运行：

```
$ sea s
```

就可以提供 grpc 服务了
