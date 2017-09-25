import grpc

from sea.servicer import ServicerMeta, params_required, extract_params
from sea import exceptions
from sea.pb2 import default_pb2


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

        @params_required('username', 'password')
        def need_params(self, request, context):
            return 'Yeah'

    logstream.truncate(0)
    logstream.seek(0)

    servicer = HelloServicer()

    request = app
    context = HelloContext()
    ret = servicer.return_error(request, context)
    assert isinstance(ret, default_pb2.Empty)
    assert context.code is grpc.StatusCode.INVALID_ARGUMENT
    assert context.details == 'error'

    request = app
    request.password = 'password'
    context = HelloContext()
    ret = servicer.need_params(request, context)
    assert isinstance(ret, default_pb2.Empty)
    assert context.code is grpc.StatusCode.INVALID_ARGUMENT
    assert 'username' in context.details
    assert 'password' not in context.details
    request.username = 'username'
    ret = servicer.need_params(request, context)
    assert ret == 'Yeah'

    p = logstream.tell()
    assert p > 0
    content = logstream.getvalue()
    assert 'HelloServicer.return_error' in content

    ret = servicer.return_normal(None, context)
    assert ret == 'Got it!'

    assert logstream.tell() > p


def test_extract_params(app):
    o = app
    o.x = 1
    o.y = 2
    assert extract_params(o, ['x', 'y']) == {'x': 1, 'y': 2}
