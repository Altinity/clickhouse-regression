import random
import uuid

import pyarrow as pa
from pyiceberg.types import *


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


class IcebergIntegerType(BaseIcebergTypeTest):
    name = "integer"
    iceberg_type = IntegerType()
    arrow_type = pa.int32()

    def generate(self):
        return random.randint(0, 10000)

    def filter_clause(self, column_name, value=None, comparison_operator="="):
        if value is None:
            value = self.generate()
        return f"{column_name} {comparison_operator} {value}"


class IcebergLongType(BaseIcebergTypeTest):
    name = "long"
    iceberg_type = LongType()
    arrow_type = pa.int64()

    def generate(self):
        return random.randint(0, 10000)

    def filter_clause(self, column_name, value=None, comparison_operator="="):
        if value is None:
            value = self.generate()
        return f"{column_name} {comparison_operator} {value}"


class IcebergDoubleType(BaseIcebergTypeTest):
    name = "double"
    iceberg_type = DoubleType()
    arrow_type = pa.float64()

    def generate(self):
        return random.uniform(0, 100)

    def filter_clause(self, column_name, value=None, comparison_operator="="):
        if value is None:
            value = self.generate()
        return f"{column_name} {comparison_operator} {value}"


class IcebergFloatType(BaseIcebergTypeTest):
    name = "float"
    iceberg_type = FloatType()
    arrow_type = pa.float32()

    def generate(self):
        return random.uniform(0, 100)

    def filter_clause(self, column_name, value=None, comparison_operator="="):
        if value is None:
            value = self.generate()
        return f"{column_name} {comparison_operator} {value}"


class IcebergBooleanType(BaseIcebergTypeTest):
    name = "boolean"
    iceberg_type = BooleanType()
    arrow_type = pa.bool_()

    def generate(self):
        return random.choice([True, False])

    def filter_clause(self, column_name, value=None, comparison_operator="="):
        if value is None:
            value = self.generate()
        return f"{column_name} {comparison_operator} {value}"


class IcebergTimestampType(BaseIcebergTypeTest):
    name = "timestamp"
    iceberg_type = TimestampType()
    arrow_type = pa.timestamp("us")

    def generate(self):
        return random.randint(0, 100000000)

    def filter_clause(self, column_name, value=None, comparison_operator="="):
        if value is None:
            value = self.generate()
        return f"{column_name} {comparison_operator} toDateTime64({value}/1000000, 6)"


class IcebergTimestamptzType(BaseIcebergTypeTest):
    name = "timestamptz"
    timezone = "UTC"
    iceberg_type = TimestamptzType()
    arrow_type = pa.timestamp("us", tz="UTC")

    def generate(self):
        return random.randint(0, 10000)

    def filter_clause(self, column_name, value=None, comparison_operator="="):
        if value is None:
            value = self.generate()
        return f"{column_name} {comparison_operator} toDateTime64({value}/1000000, 6, '{self.timezone}')"


class IcebergDateType(BaseIcebergTypeTest):
    name = "date"
    iceberg_type = DateType()
    arrow_type = pa.date32()

    def generate(self):
        return random.randint(0, 10000)

    def filter_clause(self, column_name, value=None, comparison_operator="="):
        if value is None:
            value = self.generate()
        return f"{column_name} {comparison_operator} toDate32({value})"


class IcebergStringType(BaseIcebergTypeTest):
    name = "string"
    iceberg_type = StringType()
    arrow_type = pa.string()

    def generate(self):
        return random.choice(["test", "test2", "test3"])

    def filter_clause(self, column_name, value=None, comparison_operator="="):
        if value is None:
            value = self.generate()
        return f"{column_name} {comparison_operator} '{value}'"


class IcebergFixedStringType(BaseIcebergTypeTest):
    name = "fixed_string"
    iceberg_type = FixedType(length=10)
    arrow_type = pa.fixed_size_binary(10)

    def generate(self):
        return random.choice(["test", "test2", "test3"])

    def filter_clause(self, column_name, value=None, comparison_operator="="):
        if value is None:
            value = self.generate()
        return f"{column_name} {comparison_operator} '{value}'"


class IcebergUUIDType(BaseIcebergTypeTest):
    name = "uuid"
    iceberg_type = UUIDType()
    arrow_type = pa.uuid()

    def generate(self):
        return uuid.uuid4().bytes

    def filter_clause(self, column_name, value=None, comparison_operator="="):
        if value is None:
            value = self.generate()
        # Convert UUID bytes back to string for SQL query
        uuid_str = str(uuid.UUID(bytes=value))
        return f"{column_name} {comparison_operator} '{uuid_str}'"


class IcebergBinaryType(BaseIcebergTypeTest):
    name = "binary"
    iceberg_type = BinaryType()
    arrow_type = pa.binary()

    def generate(self):
        return random.choice(["test", "test2", "test3"])

    def filter_clause(self, column_name, value=None, comparison_operator="="):
        if value is None:
            value = self.generate()
        return f"{column_name} {comparison_operator} '{value}'"


class IcebergDecimalType(BaseIcebergTypeTest):
    name = "decimal"
    iceberg_type = DecimalType(38, 18)
    arrow_type = pa.decimal128(38, 18)

    def generate(self):
        return random.randint(0, 10000)

    def filter_clause(self, column_name, value=None, comparison_operator="="):
        if value is None:
            value = self.generate()
        return f"{column_name} {comparison_operator} {value}"


class IcebergTimeType(BaseIcebergTypeTest):
    name = "time"
    iceberg_type = TimeType()
    arrow_type = pa.time64("us")

    def generate(self):
        return random.randint(0, 100000000)

    def filter_clause(self, column_name, value=None, comparison_operator="="):
        if value is None:
            value = self.generate()
        return f"{column_name} {comparison_operator} toTime64({value}/1000000, 6)"


class IcebergTimestampTypeNano(BaseIcebergTypeTest):
    name = "timestamp_nano"
    iceberg_type = TimestampType()
    arrow_type = pa.timestamp("ns")

    def generate(self):
        return random.randint(0, 1000000000000000000)

    def filter_clause(self, column_name, value=None, comparison_operator="="):
        if value is None:
            value = self.generate()
        return (
            f"{column_name} {comparison_operator} toDateTime64({value}/1000000000, 9)"
        )


class IcebergTimeStamptzNano(BaseIcebergTypeTest):
    name = "timestamptz_nano"
    timezone = "UTC"
    iceberg_type = TimestamptzType()
    arrow_type = pa.timestamp("ns", tz=timezone)

    def generate(self):
        return random.randint(0, 1000000000000000000)

    def filter_clause(self, column_name, value=None, comparison_operator="="):
        if value is None:
            value = self.generate()
        return f"{column_name} {comparison_operator} toDateTime64({value}/1000000000, 9, '{self.timezone}')"
