import random
import time

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.datatypes import (
    Array,
    Boolean,
    Date32,
    DateTime64,
    Decimal32,
    FixedString,
    Float32,
    Float64,
    Int32,
    Int64,
    Map,
    Nullable,
    String,
    Tuple,
    UUID,
)
from helpers.tables import Column
import iceberg.tests.steps.common as common
from pyiceberg.schema import Schema, NestedField
from pyiceberg.types import (
    BinaryType,
    BooleanType,
    DateType,
    DecimalType,
    DoubleType,
    FixedType,
    FloatType,
    IntegerType,
    ListType,
    LongType,
    MapType,
    StringType,
    StructType,
    TimestampType,
    TimestamptzType,
    TimeType,
    UUIDType,
)


class TableRef:
    """Minimal table handle for insert helpers (name / columns / engine)."""

    def __init__(self, name, columns, engine):
        self.name = name
        self.columns = columns
        self.engine = engine


class DateTime64WithTimezone:
    """``DateTime64(p, tz)`` shim with value generators for random inserts."""

    def __init__(self, precision, timezone):
        self.precision = precision
        self.timezone = timezone
        self.name = f"DateTime64({precision}, '{timezone}')"

    def max_value(self):
        return (
            f"toDateTime64('2299-12-31 23:59:59.999999', {self.precision}, "
            f"'{self.timezone}')"
        )

    def min_value(self):
        return (
            f"toDateTime64('1900-01-01 00:00:00.000000', {self.precision}, "
            f"'{self.timezone}')"
        )

    def zero_or_null_value(self):
        return (
            f"toDateTime64('1970-01-01 00:00:00.000000', {self.precision}, "
            f"'{self.timezone}')"
        )

    def rand_value(self, random=None):
        rng = random if random is not None else __import__("random")
        return (
            f"toDateTime64({rng.randint(1072549200, 1672549200)}, "
            f"{self.precision}, '{self.timezone}')"
        )


class IcebergTime64:
    """ClickHouse ``Time64(6)`` representation of Iceberg ``time``."""

    name = "Time64(6)"

    @staticmethod
    def from_microseconds(value):
        hours, remainder = divmod(value, 3_600_000_000)
        minutes, remainder = divmod(remainder, 60_000_000)
        seconds, microseconds = divmod(remainder, 1_000_000)
        return (
            f"toTime64('{hours:02}:{minutes:02}:{seconds:02}." f"{microseconds:06}', 6)"
        )

    def max_value(self):
        return self.from_microseconds(86_399_999_999)

    def min_value(self):
        return self.from_microseconds(0)

    def zero_or_null_value(self):
        return self.from_microseconds(0)

    def rand_value(self, random=None):
        rng = random if random is not None else __import__("random")
        return self.from_microseconds(rng.randint(0, 86_399_999_999))


class ExactFixedString(FixedString):
    """FixedString that always emits exactly ``length`` bytes (Iceberg ``fixed``)."""

    def rand_value(self, random=None):
        rng = random if random is not None else __import__("random")
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTUVWXYZ"
        ch = alphabet[rng.randint(0, len(alphabet) - 1)]
        return f"toFixedString('{ch * self.length}', {self.length})"


def alter_support_schema_columns():
    """ClickHouse columns covering Iceberg v2 primitives and nested types."""
    return [
        Column(name="boolean_col", datatype=Boolean()),
        Column(name="int32_col", datatype=Int32()),
        Column(name="int64_col", datatype=Int64()),
        Column(name="float32_col", datatype=Float32()),
        Column(name="float64_col", datatype=Float64()),
        Column(name="decimal_col", datatype=Decimal32(2)),
        Column(name="date32_col", datatype=Date32()),
        Column(name="time_col", datatype=IcebergTime64()),
        Column(name="datetime64_col", datatype=DateTime64(6)),
        Column(
            name="timestamptz_col",
            datatype=DateTime64WithTimezone(6, "UTC"),
        ),
        Column(name="string_col", datatype=String()),
        # Iceberg binary has no distinct ClickHouse column type.
        Column(name="binary_col", datatype=String()),
        Column(name="fixed_col", datatype=ExactFixedString(5)),
        Column(name="uuid_col", datatype=UUID()),
        Column(name="nullable_boolean_col", datatype=Nullable(Boolean())),
        Column(name="nullable_int64_col", datatype=Nullable(Int64())),
        Column(name="nullable_decimal_col", datatype=Nullable(Decimal32(2))),
        Column(name="nullable_string_col", datatype=Nullable(String())),
        Column(name="array_int32_col", datatype=Array(Int32())),
        Column(name="array_string_col", datatype=Array(String())),
        Column(name="array_array_int32_col", datatype=Array(Array(Int32()))),
        Column(name="map_string_int64_col", datatype=Map(key=String(), value=Int64())),
        Column(name="tuple_col", datatype=Tuple([Int32(), String()])),
    ]


def alter_support_iceberg_schema():
    """PyIceberg schema matching ``alter_support_schema_columns()``."""
    next_id = 1

    def take():
        nonlocal next_id
        field_id = next_id
        next_id += 1
        return field_id

    array_int32_element = take()
    array_string_element = take()
    array_array_inner_element = take()
    array_array_outer_element = take()
    map_key = take()
    map_value = take()
    tuple_0 = take()
    tuple_1 = take()

    return Schema(
        NestedField(take(), "boolean_col", BooleanType(), required=True),
        NestedField(take(), "int32_col", IntegerType(), required=True),
        NestedField(take(), "int64_col", LongType(), required=True),
        NestedField(take(), "float32_col", FloatType(), required=True),
        NestedField(take(), "float64_col", DoubleType(), required=True),
        NestedField(take(), "decimal_col", DecimalType(9, 2), required=True),
        NestedField(take(), "date32_col", DateType(), required=True),
        NestedField(take(), "time_col", TimeType(), required=True),
        NestedField(take(), "datetime64_col", TimestampType(), required=True),
        NestedField(take(), "timestamptz_col", TimestamptzType(), required=True),
        NestedField(take(), "string_col", StringType(), required=True),
        NestedField(take(), "binary_col", BinaryType(), required=True),
        NestedField(take(), "fixed_col", FixedType(5), required=True),
        NestedField(take(), "uuid_col", UUIDType(), required=True),
        NestedField(take(), "nullable_boolean_col", BooleanType(), required=False),
        NestedField(take(), "nullable_int64_col", LongType(), required=False),
        NestedField(take(), "nullable_decimal_col", DecimalType(9, 2), required=False),
        NestedField(take(), "nullable_string_col", StringType(), required=False),
        NestedField(
            take(),
            "array_int32_col",
            ListType(
                element_id=array_int32_element,
                element_type=IntegerType(),
                element_required=True,
            ),
            required=False,
        ),
        NestedField(
            take(),
            "array_string_col",
            ListType(
                element_id=array_string_element,
                element_type=StringType(),
                element_required=True,
            ),
            required=False,
        ),
        NestedField(
            take(),
            "array_array_int32_col",
            ListType(
                element_id=array_array_outer_element,
                element_type=ListType(
                    element_id=array_array_inner_element,
                    element_type=IntegerType(),
                    element_required=True,
                ),
                element_required=True,
            ),
            required=False,
        ),
        NestedField(
            take(),
            "map_string_int64_col",
            MapType(
                key_id=map_key,
                key_type=StringType(),
                value_id=map_value,
                value_type=LongType(),
                value_required=True,
            ),
            required=True,
        ),
        NestedField(
            take(),
            "tuple_col",
            StructType(
                NestedField(tuple_0, "_0", IntegerType(), required=True),
                NestedField(tuple_1, "_1", StringType(), required=True),
            ),
            required=True,
        ),
    )


def clickhouse_sql_table_name(table_name):
    """Normalize TestFlows-style escaped backticks for long SQL queries."""
    return table_name.replace("\\`", "`")


@TestStep(Given)
def insert_random_rows_into_tables(self, tables, row_count=10, node=None, random=None):
    """Insert the same randomly generated rows into each table."""
    if node is None:
        node = self.context.node

    if not tables:
        return

    columns = [col for col in tables[0].columns if col.datatype is not None]
    columns_values = [
        column.values(
            row_count=row_count,
            cardinality=1,
            random=random,
            shuffle_values=True,
        )
        for column in columns
    ]
    values = [
        "(" + ",".join(next(column_values) for column_values in columns_values) + ")"
        for _ in range(row_count)
    ]
    values_clause = ",".join(values)

    for table in tables:
        table_name = clickhouse_sql_table_name(table.name)
        inline_settings = None
        if "Iceberg" in table.engine:
            inline_settings = [("allow_insert_into_iceberg", 1)]
        with By(f"inserting {row_count} random rows into {table.name}"):
            node.query(
                f"INSERT INTO {table_name} VALUES {values_clause}",
                inline_settings=inline_settings,
                use_file=True,
            )


ADDABLE_COLUMN_TYPES = [
    # "Nullable(Bool)",
    "Nullable(Int32)",
    "Nullable(String)",
    "Nullable(Int64)",
    "Nullable(Float32)",
    "Nullable(Float64)",
    # "Nullable(Decimal(9, 2))",
    "Nullable(Date32)",
    "Nullable(Time64(6))",
    "Nullable(DateTime64(6))",
    "Nullable(UUID)",
]


def _alter_query(table_name, alter_clause):
    return f"SET allow_insert_into_iceberg = 1; ALTER TABLE {table_name} {alter_clause}"


@TestStep(Given)
def rename_column(self, table_name, column_name, new_column_name):
    """Rename column in the existing table using ALTER."""
    with By("executing alter rename column command on the table"):
        self.context.node.query(
            _alter_query(
                table_name, f"RENAME COLUMN {column_name} TO {new_column_name}"
            )
        )


@TestStep(Given)
def add_column(self, table_name, column_name, column_type):
    """Add column to the existing table using ALTER."""
    with By("executing alter add column command on the table"):
        self.context.node.query(
            _alter_query(table_name, f"ADD COLUMN {column_name} {column_type}")
        )


@TestStep(Given)
def drop_column(self, table_name, column_name):
    """Drop column from the existing table using ALTER."""
    with By("executing alter drop column command on the table"):
        self.context.node.query(_alter_query(table_name, f"DROP COLUMN {column_name}"))


@TestStep(When)
def drop_column_expecting_rejection(self, table_name, column_name):
    """Try to drop a layout column and require Iceberg to reject the operation."""
    result = self.context.node.query(
        _alter_query(table_name, f"DROP COLUMN {column_name}"),
        no_checks=True,
    )
    assert result.exitcode != 0, error(
        f"Iceberg allowed dropping layout column {column_name!r}"
    )
    assert "Code: 736." in result.output, error(result.output)
    assert (
        "Iceberg alter: catalog commit failed for "
        "'s3://warehouse/data/metadata/" in result.output
    ), error(result.output)
    assert (
        "after metadata file was written successfully. "
        "(DATALAKE_DATABASE_ERROR)" in result.output
    ), error(result.output)
    return result


@TestStep(Given)
def modify_column_datatype(self, table_name, column_name, new_column_type):
    """Modify a column data type using ALTER."""
    with By("executing alter modify column datatype command on the table"):
        self.context.node.query(
            _alter_query(table_name, f"MODIFY COLUMN {column_name} {new_column_type}")
        )


def _apply_alter_on_tables(self, table_names, alter_clause):
    """Run the same ALTER clause on every table."""
    for table_name in table_names:
        self.context.node.query(_alter_query(table_name, alter_clause))


@TestStep(Given)
def add_tracked_column(self, table_names):
    """Add one new column to all tables and record it in context.columns."""
    column_name = f"new_column_{getuid()}"
    column_type = random.choice(ADDABLE_COLUMN_TYPES)

    with By(f"add column {column_name} {column_type}"):
        _apply_alter_on_tables(
            self, table_names, f"ADD COLUMN {column_name} {column_type}"
        )

    with And("update column list"):
        self.context.columns.append({"name": column_name, "type": column_type})


@TestStep(Given)
def drop_tracked_column(self, table_names):
    """Drop one tracked column from all tables."""
    if not self.context.columns:
        return

    column = random.choice(self.context.columns)
    with By(f"drop column {column['name']}"):
        _apply_alter_on_tables(self, table_names, f"DROP COLUMN {column['name']}")

    with And("update column list"):
        self.context.columns.remove(column)


@TestStep(Given)
def rename_tracked_column(self, table_names):
    """Rename one tracked column on all tables."""
    if not self.context.columns:
        return

    with By("choose column to rename"):
        column = random.choice(self.context.columns)
        old_column_name = column["name"]
        new_column_name = f"renamed_{getuid()}"

    with And(f"rename column {old_column_name} to {new_column_name}"):
        _apply_alter_on_tables(
            self,
            table_names,
            f"RENAME COLUMN {old_column_name} TO {new_column_name}",
        )

    with And("update column list"):
        column["name"] = new_column_name


@TestStep(Given)
def modify_tracked_column_datatype(self, table_names):
    """Promote Int32->Int64 or Float32->Float64 when possible."""
    column = None
    new_column_type = None

    with By("search for column to promote"):
        candidates = list(self.context.columns)
        random.shuffle(candidates)
        for candidate in candidates:
            if candidate["type"] in ("Int32", "Nullable(Int32)"):
                column = candidate
                new_column_type = candidate["type"].replace("Int32", "Int64")
                break
            if candidate["type"] in ("Float32", "Nullable(Float32)"):
                column = candidate
                new_column_type = candidate["type"].replace("Float32", "Float64")
                break

        if column is None or new_column_type is None:
            return

    with And(f"modify column {column['name']} to {new_column_type}"):
        _apply_alter_on_tables(
            self,
            table_names,
            f"MODIFY COLUMN {column['name']} {new_column_type}",
        )

    with And("update column list"):
        column["type"] = new_column_type


def alter_actions():
    """Return ALTER action steps that use tracked columns."""
    return [
        add_tracked_column,
        drop_tracked_column,
        rename_tracked_column,
        modify_tracked_column_datatype,
    ]


@TestStep(Then)
def run_random_alter_sequence_and_compare(
    self,
    merge_tree_table_name,
    iceberg_table_name,
    num_actions=15,
    enabled_actions=None,
):
    """Run random ALTER steps on both tables and compare SELECT results."""
    table_names = [merge_tree_table_name, iceberg_table_name]
    actions = alter_actions()
    if enabled_actions is not None:
        actions = [action for action in actions if action.__name__ in enabled_actions]

    for step in range(num_actions):
        action = random.choice(actions)
        with By(f"step {step + 1}/{num_actions}: {action.__name__}"):
            action(table_names=table_names)

        with And(f"compare tables after step {step + 1}"):
            common.compare_data_in_two_tables(
                table_name1=merge_tree_table_name,
                table_name2=iceberg_table_name,
            )
            time.sleep(0.5)
