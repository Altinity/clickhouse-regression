from testflows.core import *


@TestStep(Given)
def parquet_file_name(self, filename):
    """Define the name of the created Parquet file."""
    return {"fileName": filename}


@TestStep(Given)
def schema(self, schema):
    """Define the schema of the Parquet file."""
    return {"schema": [schema]}


@TestStep(Given)
def options(self, options):
    """Define the options of the Parquet file."""
    return {"options": options}


@TestStep(Given)
def writer_version_1_0(self):
    """Define the writer version of the Parquet file."""
    return {"writerVersion": "1.0"}


@TestStep(Given)
def writer_version_2_0(self):
    """Define the writer version of the Parquet file."""
    return {"writerVersion": "2.0"}


@TestStep(Given)
def snappy_compression(self):
    """Define the compression of the Parquet file as SNAPPY."""
    return {"compression": "SNAPPY"}


@TestStep(Given)
def gzip_compression(self):
    """Define the compression of the Parquet file as GZIP."""
    return {"compression": "GZIP"}


@TestStep(Given)
def lzo_compression(self):
    """Define the compression of the Parquet file as LZO."""
    return {"compression": "LZO"}


@TestStep(Given)
def uncompressed(self):
    """Define the compression of the Parquet file as UNCOMPRESSED."""
    return {"compression": "UNCOMPRESSED"}


@TestStep(Given)
def row_group_size(self, size=134217728):
    """Define the row group size of the Parquet file."""
    return {"rowGroupSize": size}


@TestStep(Given)
def page_size(self, size=1048576):
    """Define the page size of the Parquet file."""
    return {"pageSize": size}


@TestStep(Given)
def encodings(self, encodings=None):
    """Define the encodings of the Parquet file."""
    if encodings is None:
        encodings = ["PLAIN"]
    return {"encodings": encodings}


@TestStep(Given)
def bloom_filter(self, filter="all"):
    """Define the bloom filter of the Parquet file."""
    return {"bloomFilter": filter}


@TestStep(Given)
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


@TestStep(Given)
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


@TestStep(Given)
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


@TestStep(Given)
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

    if logical_type["logicalType"] not in ["MAP", "LIST"]:
        data = [{name: i} for i in data]

    optional_group_type = {
        "name": name,
        "schemaType": "optionalGroup",
        "fields": [schema],
        "data": data,
    }

    return optional_group_type


@TestStep(Given)
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

    if logical_type["logicalType"] not in ["MAP", "LIST"]:
        data = [{name: i} for i in data]

    required_group_type = {
        "name": name,
        "schemaType": "requiredGroup",
        "fields": [schema],
        "data": data,
    }

    return required_group_type


@TestStep(Given)
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

    if logical_type["logicalType"] not in ["MAP", "LIST"]:
        data = [{name: i} for i in data]

    repeated_group_type = {
        "name": name,
        "schemaType": "repeatedGroup",
        "fields": [schema],
        "data": data,
    }

    return repeated_group_type


@TestStep(Given)
def utf8(self):
    """Entry for UTF8 logical type."""
    return {"logicalType": "UTF8"}


@TestStep(Given)
def decimal(self, precision=3, scale=2):
    """Entry for DECIMAL logical type."""
    return {"logicalType": "DECIMAL", "precision": precision, "scale": scale}


@TestStep(Given)
def date(self):
    """Entry for DATE logical type."""
    return {"logicalType": "DATE"}


@TestStep(Given)
def time_millis(self):
    """Entry for TIME_MILLIS logical type."""
    return {"logicalType": "TIME_MILLIS"}


@TestStep(Given)
def time_micros(self):
    """Entry for TIME_MICROS logical type."""
    return {"logicalType": "TIME_MICROS"}


@TestStep(Given)
def timestamp_millis(self):
    """Entry for TIMESTAMP_MILLIS logical type."""
    return {"logicalType": "TIMESTAMP_MILLIS"}


@TestStep(Given)
def timestamp_micros(self):
    """Entry for TIMESTAMP_MICROS logical type."""
    return {"logicalType": "TIMESTAMP_MICROS"}


@TestStep(Given)
def enum(self):
    """Entry for ENUM logical type."""
    return {"logicalType": "ENUM"}


@TestStep(Given)
def map(self):
    """Entry for MAP logical type."""
    return {"logicalType": "MAP"}


@TestStep(Given)
def list(self):
    """Entry for LIST logical type."""
    return {"logicalType": "LIST"}


@TestStep(Given)
def string(self):
    """Entry for STRING logical type."""
    return {"logicalType": "STRING"}


@TestStep(Given)
def map_key_value(self):
    """Entry for MAP_KEY_VALUE logical type."""
    return {"logicalType": "MAP_KEY_VALUE"}


@TestStep(Given)
def time(self):
    """Entry for TIME logical type."""
    return {"logicalType": "TIME"}


@TestStep(Given)
def integer(self):
    """Entry for INTEGER logical type."""
    return {"logicalType": "INTEGER"}


@TestStep(Given)
def json_type(self):
    """Entry for JSON logical type."""
    return {"logicalType": "JSON"}


@TestStep(Given)
def bson(self):
    """Entry for BSON logical type."""
    return {"logicalType": "BSON"}


@TestStep(Given)
def uuid(self):
    """Entry for UUID logical type."""
    return {"logicalType": "UUID"}


@TestStep(Given)
def interval(self):
    """Entry for INTERVAL logical type."""
    return {"logicalType": "INTERVAL"}


@TestStep(Given)
def float16(self):
    """Entry for FLOAT16 logical type."""
    return {"logicalType": "FLOAT16"}


@TestStep(Given)
def uint8(self):
    """Entry for UINT8 logical type."""
    return {"logicalType": "UINT8"}


@TestStep(Given)
def uint16(self):
    """Entry for UINT16 logical type."""
    return {"logicalType": "UINT16"}


@TestStep(Given)
def uint32(self):
    """Entry for UINT32 logical type."""
    return {"logicalType": "UINT32"}


@TestStep(Given)
def uint64(self):
    """Entry for UINT64 logical type."""
    return {"logicalType": "UINT64"}


@TestStep(Given)
def int8(self):
    """Entry for INT8 logical type."""
    return {"logicalType": "INT8"}


@TestStep(Given)
def int16(self):
    """Entry for INT16 logical type."""
    return {"logicalType": "INT16"}


@TestStep(Given)
def int32(self):
    """Entry for INT32 logical type."""
    return {"logicalType": "INT32"}


@TestStep(Given)
def int64(self):
    """Entry for INT64 logical type."""
    return {"logicalType": "INT64"}


@TestStep(Given)
def int32_physical(self):
    """Entry for INT32 physical type."""
    return {"physicalType": "INT32"}


@TestStep(Given)
def int64_physical(self):
    """Entry for INT64 physical type."""
    return {"physicalType": "INT64"}


@TestStep(Given)
def int96_physical(self):
    """Entry for INT96 physical type."""
    return {"physicalType": "INT96"}


@TestStep(Given)
def boolean_physical(self):
    """Entry for BOOLEAN physical type."""
    return {"physicalType": "BOOLEAN"}


@TestStep(Given)
def float_physical(self):
    """Entry for FLOAT physical type."""
    return {"physicalType": "FLOAT"}


@TestStep(Given)
def double_physical(self):
    """Entry for DOUBLE physical type."""
    return {"physicalType": "DOUBLE"}


@TestStep(Given)
def binary_physical(self):
    """Entry for BINARY physical type."""
    return {"physicalType": "BINARY"}


@TestStep(Given)
def fixed_len_byte_array_physical(self, length=3):
    """Entry for FIXED_LEN_BYTE_ARRAY physical type."""
    return {"physicalType": "FIXED_LEN_BYTE_ARRAY", "length": length}


@TestStep(Given)
def no_logical_type(self):
    """Entry for no logical type."""
    return {"logicalType": "NONE"}


conversions = [
    "toBool",
    "toInt8",
    "toInt8OrZero",
    "toInt8OrNull",
    "toInt8OrDefault",
    "toInt16",
    "toInt16OrZero",
    "toInt16OrNull",
    "toInt16OrDefault",
    "toInt32",
    "toInt32OrZero",
    "toInt32OrNull",
    "toInt32OrDefault",
    "toInt64",
    "toInt64OrZero",
    "toInt64OrNull",
    "toInt64OrDefault",
    "toInt128",
    "toInt128OrZero",
    "toInt128OrNull",
    "toInt128OrDefault",
    "toInt256",
    "toInt256OrZero",
    "toInt256OrNull",
    "toInt256OrDefault",
    "toUInt8",
    "toUInt8OrZero",
    "toUInt8OrNull",
    "toUInt8OrDefault",
    "toUInt16",
    "toUInt16OrZero",
    "toUInt16OrNull",
    "toUInt16OrDefault",
    "toUInt32",
    "toUInt32OrZero",
    "toUInt32OrNull",
    "toUInt32OrDefault",
    "toUInt64",
    "toUInt64OrZero",
    "toUInt64OrNull",
    "toUInt64OrDefault",
    "toUInt128",
    "toUInt128OrZero",
    "toUInt128OrNull",
    "toUInt128OrDefault",
    "toUInt256",
    "toUInt256OrZero",
    "toUInt256OrNull",
    "toUInt256OrDefault",
    "toFloat32",
    "toFloat32OrZero",
    "toFloat32OrNull",
    "toFloat32OrDefault",
    "toFloat64",
    "toFloat64OrZero",
    "toFloat64OrNull",
    "toFloat64OrDefault",
    "toDate",
    "toDateOrZero",
    "toDateOrNull",
    "toDateOrDefault",
    "toDateTime",
    "toDateTimeOrZero",
    "toDateTimeOrNull",
    "toDateTimeOrDefault",
    "toDate32",
    "toDate32OrZero",
    "toDate32OrNull",
    "toDate32OrDefault",
    "toDateTime64",
    "toDateTime64OrZero",
    "toDateTime64OrNull",
    "toDateTime64OrDefault",
    "toDecimal32",
    "toDecimal32OrZero",
    "toDecimal32OrNull",
    "toDecimal32OrDefault",
    "toDecimal64",
    "toDecimal64OrZero",
    "toDecimal64OrNull",
    "toDecimal64OrDefault",
    "toDecimal128",
    "toDecimal128OrZero",
    "toDecimal128OrNull",
    "toDecimal128OrDefault",
    "toDecimal256",
    "toDecimal256OrZero",
    "toDecimal256OrNull",
    "toDecimal256OrDefault",
    "toString",
    "toFixedString",
    "toStringCutToZero",
    "toDecimalString",
    "reinterpretAsUInt8",
    "reinterpretAsUInt16",
    "reinterpretAsUInt32",
    "reinterpretAsUInt64",
    "reinterpretAsUInt128",
    "reinterpretAsUInt256",
    "reinterpretAsInt8",
    "reinterpretAsInt16",
    "reinterpretAsInt32",
    "reinterpretAsInt64",
    "reinterpretAsInt128",
    "reinterpretAsInt256",
    "reinterpretAsFloat32",
    "reinterpretAsFloat64",
    "reinterpretAsDate",
    "reinterpretAsDateTime",
    "reinterpretAsString",
    "reinterpretAsFixedString",
    "reinterpretAsUUID",
    "reinterpret",
    "CAST",
    "accurateCast(x, T)",
    "accurateCastOrNull(x, T)",
    "accurateCastOrDefault(x, T, default_value)",
    "toIntervalYear",
    "toIntervalQuarter",
    "toIntervalMonth",
    "toIntervalWeek",
    "toIntervalDay",
    "toIntervalHour",
    "toIntervalMinute",
    "toIntervalSecond",
    "toIntervalMillisecond",
    "toIntervalMicrosecond",
    "toIntervalNanosecond",
    "parseDateTime",
    "parseDateTimeOrZero",
    "parseDateTimeOrNull",
    "parseDateTimeInJodaSyntax",
    "parseDateTimeInJodaSyntaxOrZero",
    "parseDateTimeInJodaSyntaxOrNull",
    "parseDateTimeBestEffort",
    "parseDateTime32BestEffort",
    "parseDateTimeBestEffortUS",
    "parseDateTime32BestEffortOrNull",
    "parseDateTimeBestEffortOrZero",
    "parseDateTime32BestEffortOrZero",
    "parseDateTimeBestEffortUSOrNull",
    "parseDateTimeBestEffortUSOrZero",
    "parseDateTime64BestEffort",
    "parseDateTime64BestEffortUS",
    "parseDateTime64BestEffortOrNull",
    "parseDateTime64BestEffortOrZero",
    "parseDateTime64BestEffortUSOrNull",
    "parseDateTime64BestEffortUSOrZero",
    "toLowCardinality",
    "toUnixTimestamp64Milli",
    "toUnixTimestamp64Micro",
    "toUnixTimestamp64Nano",
    "fromUnixTimestamp64Milli",
    "fromUnixTimestamp64Micro",
    "fromUnixTimestamp64Nano",
    "formatRow",
    "formatRowNoNewline",
]

writer_version = [writer_version_1_0, writer_version_2_0]
compression = [snappy_compression, gzip_compression, lzo_compression, uncompressed]
schema_type = [
    optional,
    required,
    repeated,
    optional_group,
    required_group,
    repeated_group,
]
physical_types = [
    int32_physical,
    int64_physical,
    int96_physical,
    boolean_physical,
    float_physical,
    double_physical,
    binary_physical,
    fixed_len_byte_array_physical,
]
logical_types = [
    utf8,
    decimal,
    date,
    time_millis,
    time_micros,
    timestamp_millis,
    timestamp_micros,
    enum,
    map,
    list,
    string,
    map_key_value,
    time,
    integer,
    json_type,
    bson,
    uuid,
    interval,
    float16,
    uint8,
    uint16,
    uint32,
    uint64,
    int8,
    int16,
    int32,
    int64,
    no_logical_type,
]

simple_logical_types = [
    utf8,
    decimal,
    date,
    time_millis,
    time_micros,
    timestamp_millis,
    timestamp_micros,
    enum,
    string,
    time,
    integer,
    json_type,
    bson,
    uuid,
    interval,
    float16,
    uint8,
    uint16,
    uint32,
    uint64,
    int8,
    int16,
    int32,
    int64,
    no_logical_type,
]

complex_logical_types = [map, list, map_key_value]

clickhouse_datatypes = [
    "JSON",
    "Dynamic",
    "Polygon",
    "Ring",
    "Point",
    "SimpleAggregateFunction",
    "IntervalQuarter",
    "IntervalMonth",
    "Int64",
    "IntervalDay",
    "IntervalHour",
    "IPv4",
    "IntervalSecond",
    "LowCardinality",
    "Int16",
    "UInt256",
    "AggregateFunction",
    "MultiPolygon",
    "LineString",
    "IPv6",
    "Nothing",
    "Decimal256",
    "Tuple",
    "Array",
    "IntervalMicrosecond",
    "Bool",
    "Enum16",
    "IntervalMinute",
    "FixedString",
    "String",
    "DateTime",
    "Object",
    "Map",
    "UUID",
    "Decimal64",
    "Nullable",
    "Enum",
    "Int32",
    "UInt8",
    "Date",
    "Decimal32",
    "UInt128",
    "Variant",
    "Float64",
    "Nested",
    "UInt16",
    "IntervalMillisecond",
    "Int128",
    "Decimal128",
    "Int8",
    "Decimal",
    "Int256",
    "DateTime64",
    "Enum8",
    "DateTime32",
    "Date32",
    "IntervalWeek",
    "UInt64",
    "MultiLineString",
    "IntervalNanosecond",
    "IntervalYear",
    "UInt32",
    "Float32",
    "bool",
    "INET6",
    "INET4",
    "ENUM",
    "BINARY",
    "GEOMETRY",
    "NATIONAL CHAR VARYING",
    "BINARY VARYING",
    "NCHAR LARGE OBJECT",
    "NATIONAL CHARACTER VARYING",
    "boolean",
    "NATIONAL CHARACTER LARGE OBJECT",
    "NATIONAL CHARACTER",
    "NATIONAL CHAR",
    "CHARACTER VARYING",
    "LONGBLOB",
    "TINYBLOB",
    "CLOB",
    "BLOB",
    "MEDIUMTEXT",
    "TEXT",
    "VARCHAR2",
    "CHARACTER LARGE OBJECT",
    "DOUBLE PRECISION",
    "LONGTEXT",
    "NVARCHAR",
    "INT1 UNSIGNED",
    "VARCHAR",
    "CHAR VARYING",
    "MEDIUMBLOB",
    "NCHAR",
    "VARBINARY",
    "CHAR",
    "SMALLINT UNSIGNED",
    "TIMESTAMP",
    "FIXED",
    "TINYTEXT",
    "NUMERIC",
    "DEC",
    "DOUBLE",
    "BYTEA",
    "INT",
    "SINGLE",
    "BIT",
    "BIGINT UNSIGNED",
    "UNSIGNED",
    "TINYINT UNSIGNED",
    "INTEGER UNSIGNED",
    "INT UNSIGNED",
    "REAL",
    "CHARACTER",
    "BYTE",
    "SIGNED",
    "MEDIUMINT",
    "YEAR",
    "CHAR LARGE OBJECT",
    "TINYINT",
    "BIGINT",
    "SMALLINT",
    "INTEGER SIGNED",
    "NCHAR VARYING",
    "INT SIGNED",
    "BIGINT SIGNED",
    "BINARY LARGE OBJECT",
    "SMALLINT SIGNED",
    "FLOAT",
    "SET",
    "TIME",
    "MEDIUMINT SIGNED",
    "INT1 SIGNED",
    "INTEGER",
    "MEDIUMINT UNSIGNED",
    "INT1",
    "TINYINT SIGNED",
]
