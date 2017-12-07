import grpc

from sea.servicer import ServicerMeta
from sea.format import msg2dict, stream2dict
from sea import exceptions
from sea.pb2 import default_pb2
from tests.wd.protos import helloworld_pb2


def test_meta_servicer(app, logstream):

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

    logstream.truncate(0)
    logstream.seek(0)

    servicer = HelloServicer()
    context = HelloContext()
    ret = servicer.return_error(None, context)
    assert isinstance(ret, default_pb2.Empty)
    assert context.code is grpc.StatusCode.INVALID_ARGUMENT
    assert context.details == 'error'

    p = logstream.tell()
    assert p > 0
    content = logstream.getvalue()
    assert 'HelloServicer.return_error' in content

    ret = servicer.return_normal(None, context)
    assert ret == 'Got it!'

    assert logstream.tell() > p
