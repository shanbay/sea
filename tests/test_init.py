import sea


def test_app():
    assert not sea.current_app
    app = sea.create_app('./tests/wd')
    assert app == sea.current_app
    assert sea.create_app('./tests/wd') is app
    assert app.testing

    from configs import default
    from app.servicers import GreeterServicer, helloworld_pb2_grpc
    from app.extensions import pwx

    assert app.config.get('CACHE_BACKEND') == default.CACHE_BACKEND
    servicer = app.servicers['GreeterServicer']
    assert servicer == (
        helloworld_pb2_grpc.add_GreeterServicer_to_server, GreeterServicer)
    extension = app.extensions.pwx
    assert extension is pwx
