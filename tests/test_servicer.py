import grpc

from sea.servicer import ServicerMeta
from sea import exceptions
from sea.pb2 import default_pb2


class HelloContext():

    def __init__(self):
        self.code = None
        self.details = None

    def set_code(self, code):
        self.code = code

    def set_details(self, details):
        self.details = details


class HelloServicer(metaclass=ServicerMeta):

    def return_error(self, request, context):
        raise exceptions.BadRequestException('error')

    def return_normal(self, request, context):
        return 'Got it!'


def test_meta_servicer(app):
    servicer = HelloServicer()
    context = HelloContext()
    ret = servicer.return_error(None, context)
    assert isinstance(ret, default_pb2.Empty)
    assert context.code is grpc.StatusCode.INVALID_ARGUMENT
    assert context.details == 'error'

    ret = servicer.return_normal(None, context)
    assert ret == 'Got it!'
