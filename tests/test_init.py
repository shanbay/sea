import sea


def test_app():
    sea._app = None
    assert sea.current_app() is None
    app = sea.create_app('./tests/wd')
    assert sea.current_app() is app
    assert sea.create_app('./tests/wd') is app
    assert app.testing

    from app.configs.default import Config
    from app.servicers import GreeterServicer, helloworld_pb2_grpc
    from app.extensions import consul

    assert app.config.get('CACHE_URL') == Config.CACHE_URL
    servicer = app.servicers['GreeterServicer']
    assert servicer == (
        helloworld_pb2_grpc.add_GreeterServicer_to_server, GreeterServicer)
    extension = app.extensions['consul']
    assert extension is consul
