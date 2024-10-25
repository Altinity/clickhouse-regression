from testflows.core import *

schema_type = [
    "optional",
    "required",
    "repeated",
    "optionalGroup",
    "requiredGroup",
    "repeatedGroup",
]


@TestStep
def optional(self, name, physical_type, data, logical_type=None):
    optional_type = {
        "name": name,
        "schemaType": "optional",
        "physicalType": physical_type,
        "logicalType": logical_type,
        "data": data,
    }

    if logical_type is not None:
        optional_type.update(logical_type)

    return optional_type


@TestStep
def required(self, name, physical_type, data, logical_type=None):
    required_type = {
        "name": name,
        "schemaType": "required",
        "physicalType": physical_type,
        "data": data,
    }

    if logical_type is not None:
        required_type.update(logical_type)

    return required_type


@TestStep
def repeated(self, name, data, physical_type, logical_type=None):
    repeated_type = {
        "name": name,
        "schemaType": "repeated",
        "physicalType": physical_type,
        "data": data,
    }

    if logical_type is not None:
        repeated_type.update(logical_type)

    return repeated_type


@TestStep
def optional_group(self, name, physical_type, data, logical_type=None):
    schema = {
        "name": name,
        "schemaType": "repeated",
        "physicalType": physical_type,
    }
    optional_group_type = {
        "name": name,
        "schemaType": "optionalGroup",
        "fields": [schema],
        "data": data,
    }

    if logical_type is not None:
        schema.update(logical_type)

    return optional_group_type


@TestStep
def required_group(self, name, physical_type, data, logical_type=None):
    schema = {
        "name": name,
        "schemaType": "repeated",
        "physicalType": physical_type,
    }
    required_group_type = {
        "name": name,
        "schemaType": "requiredGroup",
        "fields": [schema],
        "data": data,
    }

    if logical_type is not None:
        schema.update(logical_type)

    return required_group_type


@TestStep
def repeated_group(self, name, physical_type, data, logical_type=None):
    schema = {
        "name": name,
        "schemaType": "repeated",
        "physicalType": physical_type,
    }
    repeated_group_type = {
        "name": name,
        "schemaType": "repeatedGroup",
        "fields": [schema],
        "data": data,
    }

    if logical_type is not None:
        schema.update(logical_type)

    return repeated_group_type


@TestStep
def utf8(self):
    return {"logicalType": "INT16"}


@TestStep
def decimal(self, precision, scale):
    return {"logicalType": "DECIMAL", "PRECISION": precision, "SCALE": scale}


@TestStep
def date(self):
    return {"logicalType": "DATE"}


@TestStep
def time_millis(self):
    return {"logicalType": "TIME_MILLIS"}


@TestStep
def time_micros(self):
    return {"logicalType": "TIME_MICROS"}


@TestStep
def timestamp_millis(self):
    return {"logicalType": "TIMESTAMP_MILLIS"}


@TestStep
def timestamp_micros(self):
    return {"logicalType": "TIMESTAMP_MICROS"}


@TestStep
def enum(self):
    return {"logicalType": "ENUM"}


@TestStep
def map(self):
    return {"logicalType": "MAP"}


@TestStep
def list(self):
    return {"logicalType": "LIST"}


@TestStep
def string(self):
    return {"logicalType": "STRING"}


@TestStep
def map_key_value(self):
    return {"logicalType": "MAP_KEY_VALUE"}


@TestStep
def time(self):
    return {"logicalType": "TIME"}


@TestStep
def integer(self):
    return {"logicalType": "INTEGER"}


@TestStep
def json(self):
    return {"logicalType": "JSON"}


@TestStep
def bson(self):
    return {"logicalType": "BSON"}


@TestStep
def uuid(self):
    return {"logicalType": "UUID"}


@TestStep
def interval(self):
    return {"logicalType": "INTERVAL"}


@TestStep
def float16(self):
    return {"logicalType": "FLOAT16"}


@TestStep
def uint8(self):
    return {"logicalType": "UINT8"}


@TestStep
def uint16(self):
    return {"logicalType": "UINT16"}


@TestStep
def uint32(self):
    return {"logicalType": "UINT32"}


@TestStep
def uint64(self):
    return {"logicalType": "UINT64"}


@TestStep
def int8(self):
    return {"logicalType": "INT8"}


@TestStep
def int16(self):
    return {"logicalType": "INT16"}


@TestStep
def int32(self):
    return {"logicalType": "INT32"}


@TestStep
def int64(self):
    return {"logicalType": "INT64"}
