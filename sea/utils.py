import sys
import datetime
from google.protobuf.json_format import (
    MessageToDict,
    MessageToJson,
    ParseDict
)


def import_string(import_name):
    import_name = str(import_name).replace(':', '.')
    try:
        __import__(import_name)
    except ImportError:
        if '.' not in import_name:
            raise
    else:
        return sys.modules[import_name]

    module_name, obj_name = import_name.rsplit('.', 1)
    module = __import__(module_name, None, None, [obj_name])
    try:
        return getattr(module, obj_name)
    except AttributeError as e:
        raise ImportError(e)


class cached_property:
    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res


def logger_has_level_handler(logger):
    """Check if there is a handler in the logging chain that will handle the
    given logger's :meth:`effective level <~logging.Logger.getEffectiveLevel>`.
    """
    level = logger.getEffectiveLevel()
    current = logger

    while current:
        if any(handler.level <= level for handler in current.handlers):
            return True

        if not current.propagate:
            break

        current = current.parent

    return False


def offset2tz(offset_in_hour=0):
    return datetime.timezone(datetime.timedelta(hours=offset_in_hour))


def protobuf2json(message,
                  including_default_value_fields=False,
                  preserving_proto_field_name=False,
                  indent=4,
                  sort_keys=False):
    return MessageToJson(
        message, including_default_value_fields=including_default_value_fields,
        preserving_proto_field_name=preserving_proto_field_name,
        indent=indent, sort_keys=sort_keys
    )


def protobuf2dict(message,
                including_default_value_fields=False,
                preserving_proto_field_name=False):
    return MessageToDict(
        message, including_default_value_fields=including_default_value_fields,
        preserving_proto_field_name=preserving_proto_field_name
    )


def dict2protobuf(d, message, ignore_unknown_fields=False):
    return ParseDict(d, message, ignore_unknown_fields=ignore_unknown_fields)