import {{ project }}_pb2
import {{ project }}_pb2_grpc

from sea.servicer import ServicerMeta


class GreeterServicer({{ project }}_pb2_grpc.GreeterServicer, metaclass=ServicerMeta):

    DEFAULT_MSG_CLASS = {{ project }}_pb2.EmptyReply
