import grpc

from sea.servicer import ServicerMeta, msg2dict, stream2dict
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


def test_msg2dict(app):
    app.name = 'v-name'
    app.msg = 'v-msg'
    ret = msg2dict(app, ['name', 'msg', 'tz'])
    assert ret == {'name': 'v-name', 'msg': 'v-msg', 'tz': 'UTC'}

    request = helloworld_pb2.HelloRequest(name="value")
    ret = msg2dict(request)
    assert ret == {"name": "value"}


def test_stream2dict():
    def stream_generator():
        for i in range(5):
            yield helloworld_pb2.HelloRequest(name=str(i))

    ret = stream2dict(stream_generator())
    for i, part in enumerate(ret):
        assert part == {"name": str(i)}
