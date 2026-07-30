from dataclasses import dataclass

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.datatypes import (
    Int32,
    Int64,
    Float32,
    Float64,
    Decimal32,
    Date32,
    DateTime64,
    String,
    FixedString,
    UUID,
    Nullable,
    Array,
    Map,
    Tuple,
)
from helpers.tables import Column

from iceberg.tests.iceberg_engine.native_create.steps import (
    RawType,
    database_only_setup,
    clickhouse_table_name,
    native_iceberg_table,
    insert_into_native_iceberg_table,
    check_column_value,
)


@dataclass
class ScalarTypeConfig:
    type_name: str
    ch_type: object
    insert_val: str
    expected: str
    select_expr: str = "*"


# Bool unsupported for native Iceberg CREATE (Code 36); see xfails in iceberg/regression.py.
SCALAR_TYPE_CONFIGS = [
    ScalarTypeConfig("integer", Int32(), "42", "42"),
    ScalarTypeConfig("long", Int64(), "1234567890123", "1234567890123"),
    ScalarTypeConfig("float", Float32(), "toFloat32(1.5)", "1.5"),
    ScalarTypeConfig("double", Float64(), "toFloat64(2.5)", "2.5"),
    ScalarTypeConfig("decimal", Decimal32(2), "toDecimal32('99.99', 2)", "99.99"),
    ScalarTypeConfig("date", Date32(), "toDate32('2024-06-01')", "2024-06-01"),
    ScalarTypeConfig(
        "timestamp",
        DateTime64(6),
        "toDateTime64('2024-06-01 12:00:00.000000', 6)",
        "2024-06-01 12:00:00.000000",
    ),
    ScalarTypeConfig(
        "timestamptz",
        RawType("DateTime64(6, 'UTC')"),
        "toDateTime64('2024-06-01 12:00:00.000000', 6, 'UTC')",
        "2024-06-01 12:00:00.000000",
        select_expr="toTimeZone(col, 'UTC')",
    ),
    ScalarTypeConfig("string", String(), "'hello iceberg'", "hello iceberg"),
    ScalarTypeConfig(
        "uuid",
        UUID(),
        "'550e8400-e29b-41d4-a716-446655440000'",
        "550e8400-e29b-41d4-a716-446655440000",
    ),
    ScalarTypeConfig("fixed", FixedString(5), "toFixedString('abcde', 5)", "abcde"),
]


@TestScenario
def scalar_type_round_trip(self, minio_root_user, minio_root_password, config):
    """Check that a scalar Iceberg type survives CREATE → INSERT → SELECT."""
    table_name = f"t_{config.type_name}_{getuid()}"
    col_name = "col"

    with Given("create DataLakeCatalog database"):
        namespace, database_name = database_only_setup(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    ch_name = clickhouse_table_name(database_name, namespace, table_name)

    with And(f"natively CREATE TABLE with a single {config.type_name} column"):
        native_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            columns=[Column(name=col_name, datatype=config.ch_type)],
        )

    with When(f"INSERT test value: {config.insert_val}"):
        insert_into_native_iceberg_table(
            table_name=ch_name,
            values_sql=f"({config.insert_val})",
        )

    with Then("SELECT and verify the value round-trips"):
        check_column_value(
            table_name=ch_name,
            expected=config.expected,
            columns=config.select_expr,
            order_by=col_name,
        )


@TestScenario
def nullable_round_trip(self, minio_root_user, minio_root_password):
    """Check Nullable columns store and return non-null values and NULL."""
    table_name = f"t_nullable_{getuid()}"

    with Given("create DataLakeCatalog database"):
        namespace, database_name = database_only_setup(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    ch_name = clickhouse_table_name(database_name, namespace, table_name)

    with And("natively CREATE TABLE with required and Nullable columns"):
        columns = [
            Column(name="id", datatype=Int32()),
            Column(name="nullable_int", datatype=Nullable(Int32())),
            Column(name="nullable_str", datatype=Nullable(String())),
        ]
        native_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            columns=columns,
            order_by="id",
        )

    with When("INSERT a row with non-null values"):
        insert_into_native_iceberg_table(
            table_name=ch_name,
            values_sql="(1, 99, 'present')",
        )

    with And("INSERT a row where nullable columns are NULL"):
        insert_into_native_iceberg_table(
            table_name=ch_name,
            values_sql="(2, NULL, NULL)",
        )

    with Then("non-null values appear in the output"):
        result = check_column_value(
            table_name=ch_name,
            expected="99",
            order_by="id",
        )
        assert "present" in result.output, error()

    with And("NULL values are represented as \\N"):
        assert "\\N" in result.output, error()


@TestScenario
def list_type_round_trip(self, minio_root_user, minio_root_password):
    """Check Array columns survive round-trips including nested and empty lists."""
    table_name = f"t_list_{getuid()}"

    with Given("create DataLakeCatalog database"):
        namespace, database_name = database_only_setup(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    ch_name = clickhouse_table_name(database_name, namespace, table_name)

    with And("natively CREATE TABLE with Array columns"):
        columns = [
            Column(name="id", datatype=Int32()),
            Column(name="flat_list", datatype=Array(Int32())),
            Column(name="string_list", datatype=Array(String())),
            Column(name="nested_list", datatype=Array(Array(Int32()))),
        ]
        native_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            columns=columns,
            order_by="id",
        )

    with When("INSERT a row with array values"):
        insert_into_native_iceberg_table(
            table_name=ch_name,
            values_sql="(1, [1, 2, 3], ['a', 'b'], [[10, 20], [30]])",
        )

    with And("INSERT a row with empty arrays"):
        insert_into_native_iceberg_table(
            table_name=ch_name,
            values_sql="(2, [], [], [])",
        )

    with Then("flat integer list round-trips"):
        result = check_column_value(
            table_name=ch_name,
            expected="[1,2,3]",
            order_by="id",
        )

    with And("string list round-trips"):
        assert "['a','b']" in result.output, error()

    with And("nested list round-trips"):
        assert "[[10,20],[30]]" in result.output, error()

    with And("empty arrays are preserved"):
        assert "[]" in result.output, error()


@TestScenario
def map_type_round_trip(self, minio_root_user, minio_root_password):
    """Check Map(String, V) columns survive round-trips."""
    table_name = f"t_map_{getuid()}"

    with Given("create DataLakeCatalog database"):
        namespace, database_name = database_only_setup(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    ch_name = clickhouse_table_name(database_name, namespace, table_name)

    with And("natively CREATE TABLE with Map columns"):
        columns = [
            Column(name="id", datatype=Int32()),
            Column(name="int_map", datatype=Map(String(), Int64())),
            Column(name="str_map", datatype=Map(String(), String())),
        ]
        native_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            columns=columns,
            order_by="id",
        )

    with When("INSERT a row with maps"):
        insert_into_native_iceberg_table(
            table_name=ch_name,
            values_sql="(1, map('key', toInt64(42)), map('greeting', 'hello'))",
        )

    with And("INSERT a row with empty maps"):
        insert_into_native_iceberg_table(
            table_name=ch_name,
            values_sql="(2, map(), map())",
        )

    with Then("integer-value map round-trips"):
        result = check_column_value(
            table_name=ch_name,
            expected="{'key':42}",
            order_by="id",
        )

    with And("string-value map round-trips"):
        assert "{'greeting':'hello'}" in result.output, error()

    with And("empty maps are preserved"):
        assert "{}" in result.output, error()


@TestScenario
def struct_type_round_trip(self, minio_root_user, minio_root_password):
    """Check Tuple columns survive round-trips including nested structs."""
    table_name = f"t_struct_{getuid()}"

    with Given("create DataLakeCatalog database"):
        namespace, database_name = database_only_setup(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    ch_name = clickhouse_table_name(database_name, namespace, table_name)

    with And("natively CREATE TABLE with Tuple columns"):
        columns = [
            Column(name="id", datatype=Int32()),
            Column(name="flat_struct", datatype=Tuple([Int32(), String()])),
            Column(
                name="nested_struct",
                datatype=Tuple([Int32(), Tuple([String(), Float64()])]),
            ),
        ]
        native_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            columns=columns,
            order_by="id",
        )

    with When("INSERT a row with struct values"):
        insert_into_native_iceberg_table(
            table_name=ch_name,
            values_sql="(1, (42, 'hello'), (7, ('world', toFloat64(3.14))))",
        )

    with Then("flat struct round-trips"):
        result = check_column_value(
            table_name=ch_name,
            expected="(42,'hello')",
            order_by="id",
        )

    with And("nested struct round-trips"):
        assert "(7,('world',3.14))" in result.output, error()


@TestScenario
def all_scalars_in_one_table(self, minio_root_user, minio_root_password):
    """Check a table with all supported scalar types can be created and queried."""
    table_name = f"t_all_scalars_{getuid()}"

    with Given("create DataLakeCatalog database"):
        namespace, database_name = database_only_setup(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    ch_name = clickhouse_table_name(database_name, namespace, table_name)

    columns = [
        Column(name="int32_col", datatype=Int32()),
        Column(name="int64_col", datatype=Int64()),
        Column(name="float32_col", datatype=Float32()),
        Column(name="float64_col", datatype=Float64()),
        Column(name="decimal_col", datatype=Decimal32(2)),
        Column(name="date32_col", datatype=Date32()),
        Column(name="dt64_col", datatype=DateTime64(6)),
        Column(name="dt64tz_col", datatype=RawType("DateTime64(6, 'UTC')")),
        Column(name="string_col", datatype=String()),
        Column(name="uuid_col", datatype=UUID()),
        Column(name="fixed_col", datatype=FixedString(5)),
    ]

    with And("natively CREATE TABLE with all scalar types"):
        native_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            columns=columns,
            order_by="int32_col",
        )

    with When("INSERT one row covering every column"):
        insert_into_native_iceberg_table(
            table_name=ch_name,
            values_sql=(
                "("
                "1, "
                "toInt64(2), "
                "toFloat32(3.0), "
                "toFloat64(4.0), "
                "toDecimal32('5.55', 2), "
                "toDate32('2024-01-01'), "
                "toDateTime64('2024-01-01 00:00:00.000000', 6), "
                "toDateTime64('2024-01-01 00:00:00.000000', 6, 'UTC'), "
                "'hello', "
                "'550e8400-e29b-41d4-a716-446655440000', "
                "toFixedString('abcde', 5)"
                ")"
            ),
        )

    with Then("SELECT * succeeds and all values appear"):
        node = self.context.node
        result = node.query(
            f"SELECT * FROM {ch_name} ORDER BY int32_col FORMAT TabSeparated"
        )
        for expected in [
            "1",
            "2",
            "3",
            "4",
            "5.55",
            "2024-01-01",
            "2024-01-01 00:00:00.000000",
            "hello",
            "550e8400-e29b-41d4-a716-446655440000",
            "abcde",
        ]:
            assert expected in result.output, error()


@TestFeature
@Name("datatypes")
def feature(self, minio_root_user, minio_root_password):
    """Check Iceberg v2 data types via native CREATE, INSERT, and SELECT."""
    for config in SCALAR_TYPE_CONFIGS:
        Scenario(
            name=f"scalar {config.type_name}",
            test=scalar_type_round_trip,
        )(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            config=config,
        )

    Scenario(test=nullable_round_trip)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=list_type_round_trip)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=map_type_round_trip)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=struct_type_round_trip)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=all_scalars_in_one_table)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
