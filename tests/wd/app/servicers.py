import helloworld_pb2
import helloworld_pb2_grpc

from sea.servicer import MetaServicer


class GreeterServicer(helloworld_pb2_grpc.GreeterServicer, metaclass=MetaServicer):

    DEFAULT_MSG_CLASS = helloworld_pb2.HelloReply

    def SayHello(self, request, context):
        return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)
