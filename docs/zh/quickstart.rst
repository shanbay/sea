QuickStart
==========

让我们来创建第一个项目 helloworld::

    sea new helloworld

这条命令会自动生成以下目录及文件::

    .
    ├── app
    │   ├── extensions.py
    │   ├── __init__.py
    │   ├── models.py
    │   ├── servicers.py
    │   └── tasks.py
    ├── configs
    │   ├── default
    │   │   ├── celery.py
    │   │   ├── __init__.py
    │   │   └── orator.py
    │   ├── development
    │   │   └── __init__.py
    │   ├── __init__.py
    │   └── testing
    │       └── __init__.py
    ├── db
    ├── jobs
    │   └── __init__.py
    ├── protos
    ├── requirements.txt
    └── tests
        └── __init__.py

创建 ``protos/helloworld.proto`` 文件::

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

运行 ``sea generate -I . helloworld.proto`` 命令后, ``protos`` 目录下会生成 proto 文件对应的 Python 版本
这条命令的第一个参数是 proto 文件所在的目录，第二个参数是 proto 文件的名字::

    protos
    ├── helloworld_pb2_grpc.py
    └── helloworld_pb2.py

使用下面的内容重写 ``app/servicer.py``::

    import helloworld_pb2
    import helloworld_pb2_grpc

    from sea.servicer import ServicerMeta


    class HelloworldServicer(helloworld_pb2_grpc.GreeterServicer, metaclass=ServicerMeta):

        def SayHello(self, request, context):
            return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)

运行 ``sea server --host 127.0.0.1``，``host`` 参数是你的发布端口，client 可以通过此端口来找到你。这样 server 就已经运行起来了

然后创建 client::

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

运行这段代码，你会发现成功地收到 server 端的 echo

    Greeter client received: Hello, you!
