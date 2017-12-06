# -*- coding:utf-8 -*-
import json
from google.protobuf.message import Message
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.json_format import ParseDict
EXTENSION_CONTAINER = '___X'

TYPE_CALLABLE_MAP = {
    FieldDescriptor.TYPE_DOUBLE: float,
    FieldDescriptor.TYPE_FLOAT: float,
    FieldDescriptor.TYPE_INT32: int,
    FieldDescriptor.TYPE_INT64: int,
    FieldDescriptor.TYPE_UINT32: int,
    FieldDescriptor.TYPE_UINT64: int,
    FieldDescriptor.TYPE_SINT32: int,
    FieldDescriptor.TYPE_SINT64: int,
    FieldDescriptor.TYPE_FIXED32: int,
    FieldDescriptor.TYPE_FIXED64: int,
    FieldDescriptor.TYPE_SFIXED32: int,
    FieldDescriptor.TYPE_SFIXED64: int,
    FieldDescriptor.TYPE_BOOL: bool,
    FieldDescriptor.TYPE_STRING: str,
    FieldDescriptor.TYPE_BYTES: bytes,
    FieldDescriptor.TYPE_ENUM: int,
}


def _repeated(type_callable):
    return lambda value_list: [type_callable(value) for value in value_list]


def _enum_label_name(field, value):
    return field.enum_type.values_by_number[int(value)].name


def msg2dict(pb, keys=None, use_enum_labels=False):

    result_dict = {}
    extensions = {}
    if keys:
        fields = [(pb.DESCRIPTOR.fields_by_name[key], getattr(pb, key))
                  for key in keys]
    else:
        fields = pb.ListFields()
    for field, value in fields:
        if field.message_type and field.message_type.has_options and \
                field.message_type.GetOptions().map_entry:
            result_dict[field.name] = dict()
            value_field = field.message_type.fields_by_name['value']
            type_callable = _get_field_value_adaptor(
                pb, value_field,
                use_enum_labels)
            for k, v in value.items():
                result_dict[field.name][k] = type_callable(v)
            continue
        type_callable = _get_field_value_adaptor(pb, field,
                                                 use_enum_labels)
        if field.label == FieldDescriptor.LABEL_REPEATED:
            type_callable = _repeated(type_callable)

        if field.is_extension:
            extensions[str(field.number)] = type_callable(value)
            continue

        result_dict[field.name] = type_callable(value)

    if extensions:
        result_dict[EXTENSION_CONTAINER] = extensions
    return result_dict


def _get_field_value_adaptor(pb, field, use_enum_labels=False):
    if field.type == FieldDescriptor.TYPE_MESSAGE:
        # recursively encode protobuf sub-message
        return lambda pb: msg2dict(pb, use_enum_labels=use_enum_labels)

    if use_enum_labels and field.type == FieldDescriptor.TYPE_ENUM:
        return lambda value: _enum_label_name(field, value)

    if field.type in TYPE_CALLABLE_MAP:
        return TYPE_CALLABLE_MAP[field.type]

    raise TypeError("Field %s.%s has unrecognised type id %d" % (
        pb.__class__.__name__, field.name, field.type))


def msg2json(msg, keys=None, indent=4, sort_keys=False):
    d = msg2dict(msg, keys=keys)
    return json.dumps(d, indent=indent, sort_keys=sort_keys)


def dict2msg(d, message, ignore_unknown_fields=False):
    return ParseDict(d, message, ignore_unknown_fields=ignore_unknown_fields)


def stream2dict(stream):
    yield from map(msg2dict, stream)
