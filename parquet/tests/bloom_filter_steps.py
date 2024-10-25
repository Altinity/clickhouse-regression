from testflows.core import *

@TestStep
def parquet_file_name(self, filename):
    """Define the name of the created Parquet file."""
    return {"fileName": filename}


@TestStep
def schema(self, schema):
    """Define the schema of the Parquet file."""
    return {"schema": schema}


@TestStep
def options(self, options):
    """Define the options of the Parquet file."""
    return {"options": options}


@TestStep
def writer_version_1_0(self):
    """Define the writer version of the Parquet file."""
    return {"writerVersion": "1.0"}


@TestStep
def writer_version_2_0(self):
    """Define the writer version of the Parquet file."""
    return {"writerVersion": "2.0"}


@TestStep
def snappy_compression(self):
    """Define the compression of the Parquet file as SNAPPY."""
    return {"compression": "SNAPPY"}


@TestStep
def gzip_compression(self):
    """Define the compression of the Parquet file as GZIP."""
    return {"compression": "GZIP"}


@TestStep
def lzo_compression(self):
    """Define the compression of the Parquet file as LZO."""
    return {"compression": "LZO"}


@TestStep
def uncompressed(self):
    """Define the compression of the Parquet file as UNCOMPRESSED."""
    return {"compression": "UNCOMPRESSED"}


@TestStep
def row_group_size(self, row_group_size=134217728):
    """Define the row group size of the Parquet file."""
    return {"rowGroupSize": row_group_size}


@TestStep
def page_size(self, page_size=1048576):
    """Define the page size of the Parquet file."""
    return {"pageSize": page_size}


@TestStep
def encodings(self, encodings=None):
    """Define the encodings of the Parquet file."""
    if encodings is None:
        encodings = ["PLAIN"]
    return {"encodings": encodings}


@TestStep
def bloom_filter(self, filter="all"):
    """Define the bloom filter of the Parquet file."""
    return {"bloomFilter": filter}


@TestStep
def optional(self, name, data, physical_type=None, logical_type=None):
    """Entry for optional schema type."""
    optional_type = {
        "name": name,
        "schemaType": "optional",
        "data": data,
    }

    if logical_type is not None:
        optional_type.update(logical_type)

    if physical_type is not None:
        optional_type.update(physical_type)

    return optional_type


@TestStep
def required(self, name, data, physical_type=None, logical_type=None):
    """Entry for required schema type."""
    required_type = {
        "name": name,
        "schemaType": "required",
        "data": data,
    }

    if logical_type is not None:
        required_type.update(logical_type)

    if physical_type is not None:
        required_type.update(physical_type)

    return required_type


@TestStep
def repeated(self, name, data, physical_type=None, logical_type=None):
    """Entry for repeated schema type."""
    repeated_type = {
        "name": name,
        "schemaType": "repeated",
        "data": data,
    }

    if logical_type is not None:
        repeated_type.update(logical_type)

    if physical_type is not None:
        repeated_type.update(physical_type)

    return repeated_type


@TestStep
def optional_group(self, name, data, physical_type=None, logical_type=None):
    """Entry for optional group schema type."""
    schema = {
        "name": name,
        "schemaType": "repeated",
    }

    if logical_type is not None:
        schema.update(logical_type)

    if physical_type is not None:
        schema.update(physical_type)

    optional_group_type = {
        "name": name,
        "schemaType": "optionalGroup",
        "fields": [schema],
        "data": data,
    }

    return optional_group_type


@TestStep
def required_group(self, name, data, physical_type=None, logical_type=None):
    """Entry for required group schema type."""
    schema = {
        "name": name,
        "schemaType": "repeated",
    }

    if logical_type is not None:
        schema.update(logical_type)

    if physical_type is not None:
        schema.update(physical_type)

    required_group_type = {
        "name": name,
        "schemaType": "requiredGroup",
        "fields": [schema],
        "data": data,
    }

    return required_group_type


@TestStep
def repeated_group(self, name, data, physical_type=None, logical_type=None):
    """Entry for repeated group schema type."""
    schema = {
        "name": name,
        "schemaType": "repeated",
    }

    if logical_type is not None:
        schema.update(logical_type)

    if physical_type is not None:
        schema.update(physical_type)

    repeated_group_type = {
        "name": name,
        "schemaType": "repeatedGroup",
        "fields": [schema],
        "data": data,
    }

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


@TestStep
def int32_physical(self):
    """Entry for INT32 physical type."""
    return {"physicalType": "INT32"}


@TestStep
def int64_physical(self):
    """Entry for INT64 physical type."""
    return {"physicalType": "INT64"}


@TestStep
def int96_physical(self):
    """Entry for INT96 physical type."""
    return {"physicalType": "INT96"}


@TestStep
def boolean_physical(self):
    """Entry for BOOLEAN physical type."""
    return {"physicalType": "BOOLEAN"}


@TestStep
def float_physical(self):
    """Entry for FLOAT physical type."""
    return {"physicalType": "FLOAT"}


@TestStep
def double_physical(self):
    """Entry for DOUBLE physical type."""
    return {"physicalType": "DOUBLE"}


@TestStep
def binary_physical(self):
    """Entry for BINARY physical type."""
    return {"physicalType": "BINARY"}


@TestStep
def fixed_len_byte_array_physical(self, length=2):
    """Entry for FIXED_LEN_BYTE_ARRAY physical type."""
    return {"physicalType": "FIXED_LEN_BYTE_ARRAY", "length": length}
