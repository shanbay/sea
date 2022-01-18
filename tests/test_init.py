import sea
from sea.signals import post_ready
from unittest.mock import Mock


def test_app():
    mock_func = Mock(spec={})
    post_ready.connect(mock_func)

    assert not sea.current_app
    app = sea.create_app('./tests/wd')
    assert app == sea.current_app
    assert sea.create_app('./tests/wd') is app
    assert app.testing
    mock_func.assert_called_with(app)

    from configs import default
    from app.servicers import GreeterServicer, helloworld_pb2_grpc
    from app.extensions import pwx

    assert app.config.get('CACHE_BACKEND') == default.CACHE_BACKEND
    servicer = app.servicers['GreeterServicer']
    assert servicer == (
        helloworld_pb2_grpc.add_GreeterServicer_to_server, GreeterServicer)
    extension = app.extensions.pwx
    assert extension is pwx
