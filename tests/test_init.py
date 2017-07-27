import os

import sea


def test_app():
    assert sea.current_app() is None
    os.environ.setdefault('SEA_ENV', 'testing')
    app = sea.create_app('.')
    assert sea.current_app() is app
    assert sea.create_app(os.getcwd()) is app
    assert app.testing
    from app.configs.default import Config
    from app.servicers import GreeterServicer, helloworld_pb2_grpc
    assert app.config.get('CACHE_URL') == Config.CACHE_URL
    servicer = app.servicers['GreeterServicer']
    assert servicer == (
        helloworld_pb2_grpc.add_GreeterServicer_to_server, GreeterServicer)
