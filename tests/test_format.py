from sea.format import msg2dict, stream2dict
from tests.wd.protos import helloworld_pb2

def test_msg2dict(app):
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