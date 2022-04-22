import logging
import numbers
import os

from sea.datatypes import ConstantsObject
from sea.utils import strtobool

log = logging.getLogger("sea.config")


class ConfigAttribute:
    """Makes an attribute forward to the config"""

    def __init__(self, name, get_converter=None):
        self.__name__ = name
        self.get_converter = get_converter

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        rv = obj.config[self.__name__]
        if self.get_converter is not None:
            rv = self.get_converter(rv)
        return rv

    def __set__(self, obj, value):
        obj.config[self.__name__] = value


class Config(dict):

    def __init__(self, root_path, defaults=None):
        super().__init__(defaults or {})
        self.root_path = root_path

    def from_object(self, obj):
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def get_namespace(self, namespace, lowercase=True, trim_namespace=True):
        rv = {}
        for k, v in self.items():
            if not k.startswith(namespace):
                continue
            if trim_namespace:
                key = k[len(namespace):]
            else:
                key = k
            if lowercase:
                key = key.lower()
            rv[key] = v
        return ConstantsObject(rv)

    def load_config_from_env(self):
        """
        read environment variables and overwrite same name key's values.
        only bool/str/numbers.Number could be overwritten
        `True` will be converted to python's bool `True`.
        `1` will be converted to python's int `1`.
        """
        keys = self.keys()

        for k in keys:
            env_value = os.getenv(k)
            if not env_value:
                continue
            log.info("config item {} overwriting by env {}={}",
                     k.upper(), k.upper(), env_value)
            value_type = type(self[k])
            if value_type is bool:
                self[k] = strtobool(env_value)
            elif isinstance(env_value, (str, numbers.Number)):
                self[k] = value_type(env_value)
            else:
                log.debug("{} type config item {} can't cast from env",
                          value_type, k.upper())

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict.__repr__(self))
