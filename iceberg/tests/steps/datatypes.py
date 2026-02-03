import uuid
import random
import pyarrow as pa

from decimal import Decimal
from pyiceberg.types import *

random.seed(42)


class BaseIcebergTypeTest:
    name: str = None
    iceberg_type = None
    arrow_type = None

    def generate(self):
        """Return a test value for this type"""
        raise NotImplementedError

    def filter_clause(self, column_name: str, value=None, comparison_operator="="):
        """Return a SQL WHERE clause for filtering on this type"""
        raise NotImplementedError

    def format_value(self, value):
        """Format a value for a SQL WHERE clause"""
        return str(value)

    def filter_clause(self, column_name, value=None, comparison_operator="="):
        """Return a SQL WHERE clause for filtering on this type"""
        if value is None:
            value = self.generate()
        return f"{column_name} {comparison_operator} {self.format_value(value)}"


class IcebergIntegerType(BaseIcebergTypeTest):
    name = "integer"
    iceberg_type = IntegerType()
    arrow_type = pa.int32()

    def __init__(self, required=False):
        self.required = required

    def generate(self):
        return random.randint(0, 10000)


class IcebergLongType(BaseIcebergTypeTest):
    name = "long"
    iceberg_type = LongType()
    arrow_type = pa.int64()

    def __init__(self, required=False):
        self.required = required

    def generate(self):
        return random.randint(0, 10000)


class IcebergDoubleType(BaseIcebergTypeTest):
    name = "double"
    iceberg_type = DoubleType()
    arrow_type = pa.float64()

    def __init__(self, required=False):
        self.required = required

    def generate(self):
        return random.uniform(0, 100)


class IcebergFloatType(BaseIcebergTypeTest):
    name = "float"
    iceberg_type = FloatType()
    arrow_type = pa.float32()

    def __init__(self, required=False):
        self.required = required

    def generate(self):
        return random.uniform(0, 100)


class IcebergBooleanType(BaseIcebergTypeTest):
    name = "boolean"
    iceberg_type = BooleanType()
    arrow_type = pa.bool_()

    def __init__(self, required=False):
        self.required = required

    def generate(self):
        return random.choice([True, False])


class IcebergTimestampType(BaseIcebergTypeTest):
    name = "timestamp"
    iceberg_type = TimestampType()
    arrow_type = pa.timestamp("us")

    def __init__(self, required=False):
        self.required = required

    def generate(self):
        return random.randint(0, 100000000)

    def format_value(self, value):
        """Format a value for a SQL WHERE clause"""
        return f"toDateTime64({value}/1000000, 6)"


class IcebergTimestamptzType(BaseIcebergTypeTest):
    name = "timestamptz"
    timezone = "UTC"
    iceberg_type = TimestamptzType()
    arrow_type = pa.timestamp("us", tz="UTC")

    def __init__(self, required=False):
        self.required = required

    def generate(self):
        return random.randint(0, 10000)

    def format_value(self, value):
        """Format a value for a SQL WHERE clause"""
        return f"toDateTime64({value}/1000000, 6, '{self.timezone}')"


class IcebergDateType(BaseIcebergTypeTest):
    name = "date"
    iceberg_type = DateType()
    arrow_type = pa.date32()

    def __init__(self, required=False):
        self.required = required

    def generate(self):
        return random.randint(0, 10000)

    def format_value(self, value):
        """Format a value for a SQL WHERE clause"""
        return f"toDate32({value})"


class IcebergStringType(BaseIcebergTypeTest):
    name = "string"
    iceberg_type = StringType()
    arrow_type = pa.string()

    def __init__(self, required=False):
        self.required = required

    def generate(self):
        return random.choice(["test", "test2", "test3"])

    def format_value(self, value):
        """Format a value for a SQL WHERE clause"""
        return f"'{value}'"


class IcebergFixedStringType(BaseIcebergTypeTest):
    name = "fixed_string"
    iceberg_type = FixedType(length=10)
    arrow_type = pa.binary(10)

    def __init__(self, required=False):
        self.required = required

    def generate(self):
        # Generate exactly 10 bytes for fixed-length binary
        return bytes([i % 256 for i in range(10)])

    def format_value(self, value):
        """Format a value for a SQL WHERE clause"""
        value_str = value.decode("utf-8").rstrip()
        return f"'{value_str}'"


class IcebergUUIDType(BaseIcebergTypeTest):
    name = "uuid"
    iceberg_type = UUIDType()
    arrow_type = pa.binary(16)

    def __init__(self, required=False):
        self.required = required

    def generate(self):
        return uuid.uuid4().bytes

    def format_value(self, value):
        """Format a value for a SQL WHERE clause"""
        uuid_str = str(uuid.UUID(bytes=value))
        return f"'{uuid_str}'"


class IcebergBinaryType(BaseIcebergTypeTest):
    name = "binary"
    iceberg_type = BinaryType()
    arrow_type = pa.binary()

    def __init__(self, required=False):
        self.required = required

    def generate(self):
        return random.choice(["test", "test2", "test3"])

    def format_value(self, value):
        """Format a value for a SQL WHERE clause"""
        return f"'{value}'"


class IcebergDecimalType(BaseIcebergTypeTest):
    name = "decimal"
    iceberg_type = DecimalType(38, 18)
    arrow_type = pa.decimal128(38, 18)

    def __init__(self, required=False):
        self.required = required

    def generate(self):
        return Decimal(random.randint(0, 10000)) / Decimal(100)


class IcebergTimeType(BaseIcebergTypeTest):
    name = "time"
    iceberg_type = TimeType()
    arrow_type = pa.time64("us")

    def __init__(self, required=False):
        self.required = required

    def generate(self):
        return random.randint(0, 100000000)

    def format_value(self, value):
        """Format a value for a SQL WHERE clause"""
        return f"'{value}'"
