import inspect
import os.path

from sea.config import Config, ConfigAttribute
from sea.datatypes import ImmutableDict
from sea.register import ConsulRegister
from sea import exceptions


class Sea:
    config_class = Config
    debug = ConfigAttribute('DEBUG')
    testing = ConfigAttribute('TESTING')
    default_config = ImmutableDict({
        'DEBUG': False,
        'TESTING': False,
        'GRPC_WORKERS': 3,
        'GRPC_HOST': '[::]',
        'GRPC_PORT': 6000,
        'REGISTER_CLASS': ConsulRegister,
        'REGISTER_CLIENT': 'consul',
        'CONSUL_HOST': '127.0.0.1',
        'CONSUL_PORT': 8500,
        'CONSUL_DC': 'consul'
    })

    def __init__(self, root_path, env='development', *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not os.path.isabs(root_path):
            root_path = os.path.abspath(root_path)
        self.root_path = root_path
        self.name = os.path.basename(root_path)
        self.env = env
        self.config = self.config_class(root_path, self.default_config)
        self.servicers = {}
        self.extensions = {}

    def register_servicer(self, servicer):
        name = servicer.__name__
        if name in self.servicers:
            raise exceptions.ConfigException(
                'servicer duplicated: {}'.format(name))
        add_func = self._get_servicer_add_func(servicer)
        self.servicers[name] = (add_func, servicer)

    def _get_servicer_add_func(self, servicer):
        for b in servicer.__bases__:
            if b.__name__.endswith('Servicer'):
                m = inspect.getmodule(b)
                return getattr(m, 'add_{}_to_server'.format(b.__name__))

    def register_extension(self, name, ext):
        ext.init_app(self)
        if name in self.extensions:
            raise exceptions.ConfigException(
                'extension duplicated: {}'.format(name))
        self.extensions[name] = ext
