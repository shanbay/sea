from sea.test.stub import Context, Stub
from sea.servicer import ServicerMeta


def test_stub(app):
    class HelloServicer(metaclass=ServicerMeta):

        def return_normal(self, request, context):
            return context.invocation_metadata()

    stub = Stub(HelloServicer())
    data = {'a': 1}
    res = stub.return_normal(None, metadata=data)
    assert res == data
    res = stub.return_normal(None)
    assert res is None
