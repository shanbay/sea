from unittest import mock
from sea.client import Client
from tests.wd.protos.helloworld_pb2 import GreeterStub, HelloRequest


def test_client(app):
    client = Client(app, 'helloworld', GreeterStub)
    res = client.SayHello(HelloRequest(name='1234'))
    assert isinstance(res, dict)
    assert '1234' in res["message"]
