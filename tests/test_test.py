import grpc

from sea.exceptions import BadRequestException
from sea.test.stub import Context, Stub
from sea.servicer import ServicerMeta


def test_stub(app):
    class HelloServicer(metaclass=ServicerMeta):
        def return_error(self, request, context):
            raise BadRequestException()

        def return_normal(self, request, context):
            return context.invocation_metadata()

    stub = Stub(HelloServicer())
    data = {"a": 2}
    res = stub.return_normal(None, metadata=data)
    assert res == data
    assert stub.ctx.invocation_metadata() == data
    res = stub.return_normal(None)
    assert res is None
    assert stub.ctx.code == grpc.StatusCode.OK
    assert stub.ctx.invocation_metadata() is None

    res = stub.return_error(None)
    assert stub.ctx.code == BadRequestException.code
