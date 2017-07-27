import os
import importlib
import inspect

from sea.app import Sea
from sea.extensions import AbstractExtension

_app = None


def create_app(root_path, app_class=Sea):
    env = os.environ.get('SEA_ENV', 'development')
    config = importlib.import_module('app.configs.{}'.format(env))

    global _app
    if _app is not None:
        return _app
    _app = app_class(root_path)
    _app.config.from_object(config.Config)

    from app import servicers as _servicers
    for _, _servicer in inspect.getmembers(_servicers, inspect.isclass):
        if _servicer.__name__.endswith('Servicer'):
            _app.register_servicer(_servicer)

    from app import extensions as _extensions
    for _ext in dir(_extensions):
        _ext = getattr(_extensions, _ext)
        if isinstance(_ext, AbstractExtension):
            _ext.init_app(_app)

    return _app


def current_app():
    global _app
    return _app
