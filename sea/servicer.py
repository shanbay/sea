from types import FunctionType
from functools import wraps

from sea import exceptions


def wrap_handler(default_msg_class, func):
    @wraps(func)
    def wrapped(self, request, context):
        try:
            return func(self, request, context)
        except exceptions.RpcException as e:
            context.set_code(e.code)
            context.set_details(e.details)
            return default_msg_class()

    return wrapped


class ServicerMeta(type):
    def __new__(cls, name, bases, kws):
        _kws = {}
        default_msg_class = kws.pop('DEFAULT_MSG_CLASS')
        for k, v in kws.items():
            if isinstance(v, FunctionType):
                v = wrap_handler(default_msg_class, v)
            _kws[k] = v
        return super().__new__(cls, name, bases, _kws)
