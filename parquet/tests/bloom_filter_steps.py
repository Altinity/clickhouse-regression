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
def file_name(self, file_name):
    return {"fileName": file_name}


@TestStep
def optional(self, name, physical_type, data, logical_type=None):
    """Entry for optional schema type."""
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
    """Entry for required schema type."""
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
    """Entry for repeated schema type."""
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
    """Entry for optional group schema type."""
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
    """Entry for required group schema type."""
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
    """Entry for repeated group schema type."""
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
    """Entry for UTF8 logical type."""
    return {"logicalType": "UTF8"}


@TestStep
def decimal(self, precision, scale):
    """Entry for DECIMAL logical type."""
    return {"logicalType": "DECIMAL", "PRECISION": precision, "SCALE": scale}


@TestStep
def date(self):
    """Entry for DATE logical type."""
    return {"logicalType": "DATE"}


@TestStep
def time_millis(self):
    """Entry for TIME_MILLIS logical type."""
    return {"logicalType": "TIME_MILLIS"}


@TestStep
def time_micros(self):
    """Entry for TIME_MICROS logical type."""
    return {"logicalType": "TIME_MICROS"}


@TestStep
def timestamp_millis(self):
    """Entry for TIMESTAMP_MILLIS logical type."""
    return {"logicalType": "TIMESTAMP_MILLIS"}


@TestStep
def timestamp_micros(self):
    """Entry for TIMESTAMP_MICROS logical type."""
    return {"logicalType": "TIMESTAMP_MICROS"}


@TestStep
def enum(self):
    """Entry for ENUM logical type."""
    return {"logicalType": "ENUM"}


@TestStep
def map(self):
    """Entry for MAP logical type."""
    return {"logicalType": "MAP"}


@TestStep
def list(self):
    """Entry for LIST logical type."""
    return {"logicalType": "LIST"}


@TestStep
def string(self):
    """Entry for STRING logical type."""
    return {"logicalType": "STRING"}


@TestStep
def map_key_value(self):
    """Entry for MAP_KEY_VALUE logical type."""
    return {"logicalType": "MAP_KEY_VALUE"}


@TestStep
def time(self):
    """Entry for TIME logical type."""
    return {"logicalType": "TIME"}


@TestStep
def integer(self):
    """Entry for INTEGER logical type."""
    return {"logicalType": "INTEGER"}


@TestStep
def json(self):
    """Entry for JSON logical type."""
    return {"logicalType": "JSON"}


@TestStep
def bson(self):
    """Entry for BSON logical type."""
    return {"logicalType": "BSON"}


@TestStep
def uuid(self):
    """Entry for UUID logical type."""
    return {"logicalType": "UUID"}


@TestStep
def interval(self):
    """Entry for INTERVAL logical type."""
    return {"logicalType": "INTERVAL"}


@TestStep
def float16(self):
    """Entry for FLOAT16 logical type."""
    return {"logicalType": "FLOAT16"}


@TestStep
def uint8(self):
    """Entry for UINT8 logical type."""
    return {"logicalType": "UINT8"}


@TestStep
def uint16(self):
    """Entry for UINT16 logical type."""
    return {"logicalType": "UINT16"}


@TestStep
def uint32(self):
    """Entry for UINT32 logical type."""
    return {"logicalType": "UINT32"}


@TestStep
def uint64(self):
    """Entry for UINT64 logical type."""
    return {"logicalType": "UINT64"}


@TestStep
def int8(self):
    """Entry for INT8 logical type."""
    return {"logicalType": "INT8"}


@TestStep
def int16(self):
    """Entry for INT16 logical type."""
    return {"logicalType": "INT16"}


@TestStep
def int32(self):
    """Entry for INT32 logical type."""
    return {"logicalType": "INT32"}


@TestStep
def int64(self):
    """Entry for INT64 logical type."""
    return {"logicalType": "INT64"}
