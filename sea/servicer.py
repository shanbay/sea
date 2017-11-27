from types import FunctionType
from functools import wraps
import json
from google.protobuf.json_format import (
    MessageToDict,
    ParseDict
)

from sea import current_app


def wrap_handler(handler):
    h = handler
    for m in current_app.middlewares:
        h = m(current_app, h, handler)

    @wraps(handler)
    def wrapped(self, request, context):
        return h(self, request, context)

    return wrapped


class ServicerMeta(type):
    def __new__(cls, name, bases, kws):
        _kws = {}
        for k, v in kws.items():
            if isinstance(v, FunctionType):
                v = wrap_handler(v)
            _kws[k] = v
        return super().__new__(cls, name, bases, _kws)


def msg2dict(msg, keys=None):

    d = MessageToDict(msg)
    if keys is not None:
        return {k: d.get(k) for k in keys}
    return d


def msg2json(msg, keys=None, indent=4, sort_keys=False):
    d = msg2dict(msg, keys=keys)
    return json.dumps(d, indent=indent, sort_keys=sort_keys)


def dict2msg(d, message, ignore_unknown_fields=False):
    return ParseDict(d, message, ignore_unknown_fields=ignore_unknown_fields)


def stream2dict(stream):
    yield from map(msg2dict, stream)
