import os
import sys
import inspect

from sea.app import Sea
from sea.extensions import AbstractExtension
from sea.utils import import_string

__version__ = '0.3.0'
_app = None


def _load_servicers(target):
    from app import servicers as _servicers
    for _, _servicer in inspect.getmembers(_servicers, inspect.isclass):
        if _servicer.__name__.endswith('Servicer'):
            target.register_servicer(_servicer)


def _load_extensions(target):
    from app import extensions as _extensions
    for _ext_name in dir(_extensions):
        _ext = getattr(_extensions, _ext_name)
        if isinstance(_ext, AbstractExtension):
            target.register_extension(_ext_name, _ext)


def create_app(root_path, app_class=Sea):
    sys.path.append(root_path)
    sys.path.append(os.path.join(root_path, 'protos'))

    env = os.environ.get('SEA_ENV', 'development')
    config = import_string('configs.{}'.format(env))

    global _app
    if _app is not None:
        return _app
    _app = app_class(root_path)
    _app.config.from_object(config)

    _load_servicers(_app)
    _load_extensions(_app)

    return _app


def current_app():
    global _app
    return _app
