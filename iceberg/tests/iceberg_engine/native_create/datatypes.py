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
    UUID,
    Nullable,
    Array,
    Map,
    Tuple,
)
from helpers.tables import Column

from iceberg.requirements.native_create_drop import *
from iceberg.tests.iceberg_engine.native_create.steps import (
    RawType,
    database_only_setup,
    clickhouse_table_name,
    native_iceberg_table,
    insert_into_native_iceberg_table,
    check_column_value,
    catalog_and_database,
    create_table,
    pyiceberg_schema_shape,
    snapshot_state,
    assert_rejected_no_trace,
    ENGINE_LESS,
    EXPLICIT_ENGINE,
    BAD_ARGUMENTS,
    INCORRECT_QUERY,
    FILE_DOESNT_EXIST,
)


@dataclass
class ScalarTypeConfig:
    type_name: str
    ch_type: object
    insert_val: str
    expected: str
    select_expr: str = "*"


# Types the Iceberg writer does not map (FixedString) are covered by
# ``unsupported_types_rejected`` below, not listed here.
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
]


@TestScenario
def scalar_type_round_trip(self, config):
    """Check that a scalar Iceberg type survives CREATE → INSERT → SELECT."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
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
def nullable_round_trip(self):
    """Check Nullable columns store and return non-null values and NULL."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
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
def list_type_round_trip(self):
    """Check Array columns survive round-trips including nested and empty lists."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
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
def map_type_round_trip(self):
    """Check Map(String, V) columns survive round-trips."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
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
def struct_type_round_trip(self):
    """Check Tuple columns survive round-trips including nested structs."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
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
def all_scalars_in_one_table(self):
    """Check a table with all supported scalar types can be created and queried."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
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
                "'550e8400-e29b-41d4-a716-446655440000'"
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
        ]:
            assert expected in result.output, error()


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Schema_Columns("1.0"))
def required_and_optional_in_catalog_schema(self):
    """C1: plain columns register as required, Nullable ones as optional, and
    nested types carry element ids, as PyIceberg reads them from the catalog."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    create_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        path=self.context.create_path,
        columns=[
            "id Int64",
            "opt Nullable(String)",
            "arr Array(Int64)",
            "nested Array(Array(String))",
            "m Map(String, Int64)",
            "t Tuple(a Int64, b String)",
        ],
    )
    table = catalog.load_table(f"{namespace}.{table_name}")
    shape = pyiceberg_schema_shape(table)
    assert shape[0] == ("id", "long", True), error(shape)
    assert shape[1] == ("opt", "string", False), error(shape)
    assert shape[2][1].startswith("list<"), error(shape)
    assert shape[3][1].startswith("list<list<"), error(shape)
    assert shape[4][1].startswith("map<"), error(shape)
    assert shape[5][1].startswith("struct<"), error(shape)
    ids = [f.field_id for f in table.schema().fields]
    assert ids == sorted(ids) and ids[0] == 1, error(ids)
    assert table.schema().highest_field_id > 6, error("nested element ids not assigned")


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Schema_Columns("1.0"))
def unsupported_types_rejected(self):
    """A column type the Iceberg writer cannot map is rejected with
    BAD_ARGUMENTS and leaves no trace.

    FixedString has no writer mapping to Iceberg `fixed[N]` on any Antalya
    branch or upstream master (Utils.cpp type conversion), although the
    reader maps `fixed[N]` to FixedString (SchemaProcessor.cpp). Found
    2026-09-15; see findings.md, environment facts.
    """
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    for type_name in ("FixedString(5)",):
        with Check(type_name, flags=TE):
            namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
            args = dict(
                catalog=catalog,
                namespace=namespace,
                table_name=table_name,
                database_name=database_name,
            )
            with When("snapshot state"):
                before = snapshot_state(**args)
            create_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                path=self.context.create_path,
                columns=["id Int64", f"col {type_name}"],
                exitcode=BAD_ARGUMENTS,
                message="Unsupported type for iceberg",
            )
            with Then("no trace"):
                after = snapshot_state(**args)
                assert_rejected_no_trace(
                    before=before, after=after, namespace_expected=False
                )


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Schema_Columns("1.0"))
def empty_column_list(self):
    """CREATE TABLE without columns leaves no trace. A bare engine-less
    CREATE is stopped by the generic query validation, INCORRECT_QUERY
    "required list of column descriptions or AS section or SELECT", before
    the DataLakeCatalog code runs (the PR's own "Cannot create table without
    columns" check is not reachable from SQL). With an explicit engine a
    column-less CREATE has always meant "attach to the table at this path and
    infer its columns", so with nothing at the path the server answers
    FILE_DOESNT_EXIST instead."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )
    if self.context.create_path == ENGINE_LESS:
        exitcode, message = INCORRECT_QUERY, "required list of column descriptions"
    else:
        exitcode, message = FILE_DOESNT_EXIST, "doesn't exist"
    with When("snapshot state"):
        before = snapshot_state(**args)
    create_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        path=self.context.create_path,
        columns=[],
        exitcode=exitcode,
        message=message,
    )
    with Then("no trace"):
        with When("snapshot state"):
            after = snapshot_state(**args)
        assert_rejected_no_trace(before=before, after=after, namespace_expected=False)


@TestFeature
@Name("datatypes")
@Requirements(RQ_Iceberg_NativeCreateDrop_Schema_Columns("1.0"))
def feature(self, minio_root_user, minio_root_password):
    """Check Iceberg data types via native CREATE, INSERT, and SELECT, under
    both creation paths."""
    for path in (EXPLICIT_ENGINE, ENGINE_LESS):
        with Feature(path):
            self.context.create_path = path
            for config in SCALAR_TYPE_CONFIGS:
                Scenario(
                    name=f"scalar {config.type_name}",
                    test=scalar_type_round_trip,
                    flags=TE,
                )(config=config)
            for scenario in (
                nullable_round_trip,
                list_type_round_trip,
                map_type_round_trip,
                struct_type_round_trip,
                all_scalars_in_one_table,
                required_and_optional_in_catalog_schema,
                unsupported_types_rejected,
                empty_column_list,
            ):
                Scenario(run=scenario, flags=TE)
