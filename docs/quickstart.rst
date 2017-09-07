QuickStart
==========

let's create a project named helloworld::

    sea new helloworld

It will generate following driectories and files automaticlly::

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


create ``protos/helloworld.proto`` like this::

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


run this command ``sea generate -I ./protos helloworld.proto``, protos dir will be added two files::

    protos
    ├── helloworld_pb2_grpc.py
    ├── helloworld_pb2.py
    └── helloworld.proto

overwrite ``app/servicer.py`` like following::

    import helloworld_pb2
    import helloworld_pb2_grpc

    from sea.servicer import ServicerMeta


    class HelloworldServicer(helloworld_pb2_grpc.GreeterServicer, metaclass=ServicerMeta):

        def SayHello(self, request, context):
            return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)

run ``sea server --host address``, host argument is your publish host, in order for the client to find you

Then create the client::

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

run this script. if successful, you will see::

    Greeter client received: Hello, you!
