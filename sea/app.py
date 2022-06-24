import inspect
import logging
import os
import os.path
import sys

from sea import exceptions, utils
from sea.config import Config, ConfigAttribute
from sea.datatypes import ConstantsObject, ImmutableDict

if sys.version_info.minor >= 8:
    from functools import cached_property
else:
    from sea.utils import cached_property


class BaseApp:
    """The BaseApp object implements grpc application

    :param root_path: the root path
    :param env: the env
    """

    config_class = Config
    testing = ConfigAttribute("TESTING")
    tz = ConfigAttribute("TIMEZONE")
    default_config = ImmutableDict(
        {
            "TESTING": False,
            "TIMEZONE": "UTC",
            "GRPC_WORKERS": 4,
            "GRPC_THREADS": 1,  # Only appliable in multiprocessing server
            "GRPC_WORKER_MODE": "threading",  # Worker mode. threading|multiprocessing
            "GRPC_HOST": "0.0.0.0",
            "GRPC_PORT": 6000,
            "GRPC_LOG_LEVEL": "WARNING",
            "GRPC_LOG_HANDLER": logging.StreamHandler(),
            "GRPC_LOG_FORMAT": "[%(asctime)s %(levelname)s in %(module)s] %(message)s",  # NOQA
            "GRPC_GRACE": 5,
            "PROMETHEUS_SCRAPE": False,
            "PROMETHEUS_PORT": 9091,
            "MIDDLEWARES": ["sea.middleware.RpcErrorMiddleware"],
        }
    )

    def __init__(self, root_path, env):
        if not os.path.isabs(root_path):
            root_path = os.path.abspath(root_path)
        self.root_path = root_path
        self.name = os.path.basename(root_path)
        self.env = env
        self.debug = (
            os.environ.get("SEA_DEBUG") not in (None, "0", "false", "no")
            or env == "development"
        )
        self.config = self.config_class(root_path, self.default_config)
        self._servicers = {}
        self._extensions = {}
        self._middlewares = []

    def _setup_root_logger(self):
        fmt = self.config["GRPC_LOG_FORMAT"]
        lvl = self.config["GRPC_LOG_LEVEL"]
        h = self.config["GRPC_LOG_HANDLER"]
        h.setFormatter(logging.Formatter(fmt))
        root = logging.getLogger()
        root.setLevel(lvl)
        root.addHandler(h)

    @cached_property
    def logger(self):
        self._setup_root_logger()

        logger = logging.getLogger("sea.app")
        if self.debug and logger.level == logging.NOTSET:
            logger.setLevel(logging.DEBUG)
        if not utils.logger_has_level_handler(logger):
            h = logging.StreamHandler()
            h.setFormatter(logging.Formatter("%(message)s"))
            logger.addHandler(h)
        return logger

    @cached_property
    def servicers(self):
        rv = ConstantsObject(self._servicers)
        del self._servicers
        return rv

    @cached_property
    def extensions(self):
        rv = ConstantsObject(self._extensions)
        del self._extensions
        return rv

    @cached_property
    def middlewares(self):
        rv = tuple(self._middlewares)
        del self._middlewares
        return rv

    def _register_servicer(self, servicer):
        """register serviser

        :param servicer: servicer
        """
        name = servicer.__name__
        if name in self._servicers:
            raise exceptions.ConfigException("servicer duplicated: {}".format(name))
        add_func = self._get_servicer_add_func(servicer)
        self._servicers[name] = (add_func, servicer)

    def _get_servicer_add_func(self, servicer):
        for b in servicer.__bases__:
            if b.__name__.endswith("Servicer"):
                m = inspect.getmodule(b)
                return getattr(m, "add_{}_to_server".format(b.__name__))

    def _register_extension(self, name, ext):
        """register extension

        :param name: extension name
        :param ext: extension object
        """
        ext.init_app(self)
        if name in self._extensions:
            raise exceptions.ConfigException("extension duplicated: {}".format(name))
        self._extensions[name] = ext

    def load_middlewares(self):
        mids = ["sea.middleware.GuardMiddleware"] + self.config.get("MIDDLEWARES")
        for mn in mids:
            m = utils.import_string(mn)
            self._middlewares.insert(0, m)
        return self.middlewares

    def load_extensions_in_module(self, module):
        def is_ext(ins):
            return not inspect.isclass(ins) and hasattr(ins, "init_app")

        for n, ext in inspect.getmembers(module, is_ext):
            self._register_extension(n, ext)
        return self.extensions

    def load_servicers_in_module(self, module):
        for _, _servicer in inspect.getmembers(module, inspect.isclass):
            if _servicer.__name__.endswith("Servicer"):
                self._register_servicer(_servicer)
        return self.servicers

    def ready(self):
        pass
