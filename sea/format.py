# -*- coding:utf-8 -*-
import json
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


def repeated(type_callable):
    return lambda value_list: [type_callable(value) for value in value_list]


def enum_label_name(field, value):
    return field.enum_type.values_by_number[int(value)].name


def _is_map_entry(field):
    return (field.type == FieldDescriptor.TYPE_MESSAGE and
            field.message_type.has_options and
            field.message_type.GetOptions().map_entry)


def _is_repeat_label(field):
    return field.label == FieldDescriptor.LABEL_REPEATED


def msg2dict(pb, keys=None, use_enum_labels=False,
             including_default_value_fields=True):

    if keys:
        field_values = [(pb.DESCRIPTOR.fields_by_name[key],
                         getattr(pb, key)) for key in keys]
    else:
        field_values = pb.ListFields()

    result_dict, extensions = _handle_field_values(
        pb, field_values, use_enum_labels, including_default_value_fields)
    # Serialize default value if including_default_value_fields is True.
    if including_default_value_fields:
        result_dict = _handle_default_value_fields(pb, keys, result_dict)

    if extensions:
        result_dict[EXTENSION_CONTAINER] = extensions
    return result_dict


def msg2json(msg, keys=None, indent=2, sort_keys=False):
    d = msg2dict(msg, keys=keys)
    return json.dumps(d, indent=indent, sort_keys=sort_keys)


def dict2msg(d, message, ignore_unknown_fields=False):
    return ParseDict(d, message, ignore_unknown_fields=ignore_unknown_fields)


def stream2dict(stream):
    yield from map(msg2dict, stream)


def _handle_field_values(pb, field_values,
                         use_enum_labels, including_default_value_fields):
    result_dict = {}
    extensions = {}
    for field, value in field_values:
        if field.message_type and field.message_type.has_options and \
                field.message_type.GetOptions().map_entry:
            result_dict[field.name] = dict()
            value_field = field.message_type.fields_by_name['value']
            type_callable = _get_field_value_adaptor(
                pb, value_field,
                use_enum_labels, including_default_value_fields)
            for k, v in value.items():
                result_dict[field.name][k] = type_callable(v)
            continue
        type_callable = _get_field_value_adaptor(
            pb, field, use_enum_labels, including_default_value_fields)
        if field.label == FieldDescriptor.LABEL_REPEATED:
            type_callable = repeated(type_callable)

        if field.is_extension:
            extensions[str(field.number)] = type_callable(value)
            continue
        result_dict[field.name] = type_callable(value)
    return result_dict, extensions


def _handle_default_value_fields(pb, keys, result_dict):
    for field in pb.DESCRIPTOR.fields:
        if keys and field.name not in keys:
            continue
        # Singular message fields and oneof fields will not be affected.
        if ((field.label != FieldDescriptor.LABEL_REPEATED and
             field.cpp_type == FieldDescriptor.CPPTYPE_MESSAGE) or
                field.containing_oneof):
            continue
        if field.name in result_dict:
            # Skip the field which has been serailized already.
            continue
        if _is_map_entry(field):
            result_dict[field.name] = {}
        elif _is_repeat_label(field):
            result_dict[field.name] = []
        else:
            result_dict[field.name] = field.default_value
    return result_dict


def _get_field_value_adaptor(pb, field, use_enum_labels,
                             including_default_value_fields):
    if field.type == FieldDescriptor.TYPE_MESSAGE:
        # recursively encode protobuf sub-message
        return lambda pb: msg2dict(
            pb, use_enum_labels=use_enum_labels,
            including_default_value_fields=including_default_value_fields)

    if use_enum_labels and field.type == FieldDescriptor.TYPE_ENUM:
        return lambda value: enum_label_name(field, value)

    if field.type in TYPE_CALLABLE_MAP:
        return TYPE_CALLABLE_MAP[field.type]

    raise TypeError("Field %s.%s has unrecognised type id %d" % (
        pb.__class__.__name__, field.name, field.type))
