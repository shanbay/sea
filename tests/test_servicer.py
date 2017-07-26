import grpc

from sea.servicer import MetaServicer
from sea import exceptions


class HelloContext():

    def __init__(self):
        self.code = None
        self.details = None

    def set_code(self, code):
        self.code = code

    def set_details(self, details):
        self.details = details


class HelloServicer(metaclass=MetaServicer):

    DEFAULT_MSG_CLASS = dict

    def return_error(self, request, context):
        raise exceptions.BadRequestException('error')

    def return_normal(self, request, context):
        return 'Got it!'


def test_meta_servicer():
    servicer = HelloServicer()
    context = HelloContext()
    ret = servicer.return_error(None, context)
    assert ret == {}
    assert context.code == grpc.StatusCode.INVALID_ARGUMENT
    assert context.details == 'error'

    ret = servicer.return_normal(None, context)
    assert ret == 'Got it!'
