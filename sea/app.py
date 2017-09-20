import inspect
import logging
import os.path

from sea import exceptions, utils
from sea.config import Config, ConfigAttribute
from sea.datatypes import ImmutableDict
from sea.extensions import AbstractExtension


class Sea:
    """The Sea object implements grpc application

    :param root_path: the root path
    :param env: the env default is 'development'
    """
    config_class = Config
    debug = ConfigAttribute('DEBUG')
    testing = ConfigAttribute('TESTING')
    tz = ConfigAttribute('TIMEZONE')
    default_config = ImmutableDict({
        'DEBUG': False,
        'TESTING': False,
        'TIMEZONE': 'UTC',
        'GRPC_WORKERS': 3,
        'GRPC_HOST': '[::]',
        'GRPC_PORT': 6000,
        'GRPC_LOG_LEVEL': 'INFO',
        'GRPC_LOG_HANDLER': logging.StreamHandler(),
        'GRPC_LOG_FORMAT': '[%(asctime)s %(levelname)s in %(module)s] %(message)s',  # NOQA
        'REGISTER_CLASS': 'sea.register.ConsulRegister',
        'REGISTER_CLIENT': 'consul',
        'CONSUL_HOST': '127.0.0.1',
        'CONSUL_PORT': 8500,
        'CONSUL_DC': 'consul',
        'MIDDLEWARES': [
            'sea.middleware.RpcErrorMiddleware'
        ]
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
        self.middlewares = []

    @utils.cached_property
    def logger(self):
        logger = logging.getLogger('sea.app')
        if self.debug and logger.level == logging.NOTSET:
            logger.setLevel(logging.DEBUG)
        if not utils.logger_has_level_handler(logger):
            h = logging.StreamHandler()
            h.setFormatter(logging.Formatter('%(message)s'))
            logger.addHandler(h)
        return logger

    def register_servicer(self, servicer):
        """register serviser

        :param servicer: servicer
        """
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
        """register extension

        :param name: extension name
        :param ext: extension object
        """
        ext.init_app(self)
        if name in self.extensions:
            raise exceptions.ConfigException(
                'extension duplicated: {}'.format(name))
        self.extensions[name] = ext

    def load_middlewares(self):
        mids = ['sea.middleware.GuardMiddleware'] + \
            self.config.get('MIDDLEWARES')
        for mn in mids:
            m = utils.import_string(mn)
            self.middlewares.insert(0, m)

    def load_extensions_in_module(self, module):
        for _ext_name in dir(module):
            _ext = getattr(module, _ext_name)
            if isinstance(_ext, AbstractExtension):
                self.register_extension(_ext_name, _ext)

    def load_servicers_in_module(self, module):
        for _, _servicer in inspect.getmembers(module, inspect.isclass):
            if _servicer.__name__.endswith('Servicer'):
                self.register_servicer(_servicer)
