import os
import sys

from sea.app import Sea
from sea.utils import import_string

__version__ = '0.6.2'
_app = None


def create_app(root_path, app_class=Sea):
    sys.path.append(root_path)
    sys.path.append(os.path.join(root_path, 'protos'))

    env = os.environ.get('SEA_ENV', 'development')
    config = import_string('configs.{}'.format(env))

    global _app
    if _app is not None:
        return _app
    _app = app_class(root_path, env=env)
    _app.config.from_object(config)

    _app.load_middlewares()
    _app.load_extensions_in_module(import_string('app.extensions'))
    _app.load_servicers_in_module(import_string('app.servicers'))

    return _app


def current_app():
    global _app
    return _app
