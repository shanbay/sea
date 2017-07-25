import os
import os.path
import inspect
import importlib

from sea.config import Config, ConfigAttribute
from sea.datatypes import ImmutableDict


class Sea:
    config_class = Config
    debug = ConfigAttribute('DEBUG')
    testing = ConfigAttribute('TESTING')
    default_config = ImmutableDict({
        'DEBUG': False,
        'TESTING': False
    })

    def __init__(self, root_path, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root_path = root_path
        self.config = self.config_class(root_path, self.default_config)
        self.error_handler_spec = {}
        self.servicers = {}
        self.extensions = {}

    def register_servicer(self, servicer):
        name = servicer.__name__
        if name in self.servicers:
            return
        add_func = self._get_servicer_add_func(servicer)
        self.servicers[name] = (add_func, servicer)

    def _get_servicer_add_func(self, servicer):
        for b in servicer.__bases__:
            if b.__name__ == servicer.__name__:
                m = inspect.getmodule(b)
                return getattr(m, 'add_{}_to_server'.format(b.__name__))


def create_app(app_class=Sea):
    env = os.environ.get('SEA_ENV', 'development')
    config = importlib.import_module('app.configs.{}'.format(env))

    _app = app_class(os.path.abspath(os.getcwd()))
    _app.config.from_object(config.Config)

    from app import servicers as _servicers
    for _, _servicer in inspect.getmembers(_servicers, inspect.isclass):
        if _servicer.__name__.endswith('Servicer'):
            _app.register_servicer(_servicer)

    from app import extensions as _extensions
    for _ext in dir(_extensions):
        _ext = getattr(_extensions, _ext)
        _ext.init_app(_app)

    return _app
