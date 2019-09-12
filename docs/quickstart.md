# 快速入门

- - -

让我们来创建第一个项目 helloworld:

```
$ sea new --skip-peewee --skip-cache --skip-async_task --skip-bus --skip-sentry helloworld
```

这条命令会自动生成以下目录及文件:
```
.
├── app
│   ├── extensions.py
│   ├── __init__.py
│   └── servicers.py
├── configs
│   ├── default
│   │   ├── __init__.py
│   ├── development.py
│   ├── __init__.py
│   └── testing.py
├── jobs
│   └── __init__.py
├── protos
├── requirements.txt
└── tests
    └── __init__.py
```

> 关于项目结构的更多说明，请参照文档[项目结构](structure)

创建 `/path/to/protos/helloworld.proto` 文件:

```
syntax = "proto3";

package helloworld;

// The greeting service definition.
service Greeter {
  // Sends a greeting
  rpc SayHello (HelloRequest) returns (HelloReply) {}
}

// The request message containing the user's name.
message HelloRequest {
  string name = 1;
}

// The response message containing the greetings
message HelloReply {
  string message = 1;
}
```

> 关于proto语法的更多说明，请参照文档[protocol-buffers](https://developers.google.com/protocol-buffers/docs/overview)

运行

```
$ sea generate -I /path/to/protos/ helloworld.proto
```

protos 目录下会生成 proto 文件对应的 Python 版本 这条命令的第一个参数是 proto 文件所在的目录，第二个参数是 proto 文件的名字:

```
protos
├── helloworld_pb2_grpc.py
└── helloworld_pb2.py
```

使用下面的内容重写 app/servicer.py:

```python
import helloworld_pb2
import helloworld_pb2_grpc

from sea.servicer import ServicerMeta


class HelloworldServicer(helloworld_pb2_grpc.GreeterServicer, metaclass=ServicerMeta):

    def SayHello(self, request, context):
        return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)
```

运行
```
sea server
```

然后创建 client:

```python
import grpc

import helloworld_pb2
import helloworld_pb2_grpc


def run():
  channel = grpc.insecure_channel('localhost:6000')
  stub = helloworld_pb2_grpc.GreeterStub(channel)
  response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
  print("Greeter client received: " + response.message)


if __name__ == '__main__':
  run()
```

运行这段代码，你会发现成功地收到 server 端的 echo

```
Greeter client received: Hello, you!
```
