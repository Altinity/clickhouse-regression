"""Aggregate states in standalone Parquet files: what is written, what the
footer records, and how schema inference uses it."""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.aggregate_states import *
from iceberg.tests.iceberg_engine.aggregate_states.steps import *


@TestStep(When)
def write_states_file(self, key, settings=STATE_SETTINGS, node=None):
    """``INSERT INTO FUNCTION s3(...)`` one state per group into ``key``."""
    if node is None:
        node = self.context.node
    return node.query(
        f"INSERT INTO FUNCTION {s3_function(key)} {states_select()}",
        settings=settings,
    )


@TestScenario
@Requirements(
    RQ_Iceberg_AggregateStates_Parquet_Write("1.0"),
    RQ_Iceberg_AggregateStates_Parquet_ColumnTypesMetadata("1.0"),
)
def written_as_plain_binary_with_column_types(self):
    """The state column is a BYTE_ARRAY without a string type, an external
    reader sees binary, and the footer maps the aggregate columns to their
    ClickHouse types."""
    with Given("a Parquet file with states"):
        key = parquet_key()
        write_states_file(key=key)
        metadata = parquet_metadata(key)

    with Then("u is plain binary"):
        u = parquet_column(metadata, "u")
        assert is_plain_binary(u), error(
            f"u is {u.physical_type} logical={u.logical_type} converted={u.converted_type}"
        )

    with And("pyarrow reads u as binary"):
        arrow_type = str(metadata.schema.to_arrow_schema().field("u").type)
        assert arrow_type in ("binary", "large_binary"), error(arrow_type)

    with And("s is an ordinary Int64"):
        s = parquet_column(metadata, "s")
        assert s.physical_type == "INT64", error(s.physical_type)

    with And("clickhouse.column_types names both aggregate columns"):
        column_types = parquet_column_types(key)
        assert column_types is not None, error(
            f"no clickhouse.column_types in {sorted(metadata.metadata or {})}"
        )
        assert column_types.get("u", "").startswith("AggregateFunction("), error(
            column_types
        )
        assert "uniq" in column_types["u"], error(column_types)
        assert column_types.get("s") == S_TYPE, error(column_types)


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Parquet_Write_Disabled("1.0"))
def write_refused_without_setting(self):
    """Without the setting a state column is refused with UNKNOWN_TYPE and no
    file is written."""
    with Given("a key"):
        key = parquet_key()

    with When("INSERT INTO FUNCTION s3 without the setting"):
        query_refused(
            query=f"INSERT INTO FUNCTION {s3_function(key)} {states_select()}",
            exitcode=UNKNOWN_TYPE,
            message="UNKNOWN_TYPE",
        )

    with Then("no file was written"):
        assert not s3.object_exists(key), error(f"{key} written by a refused INSERT")


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Parquet_SchemaInference("1.0"))
def schema_inference_reports_aggregate_types(self):
    """With the setting, DESCRIBE reports the recorded types and the states
    merge without any structure hint."""
    with Given("a Parquet file with states"):
        key = parquet_key()
        write_states_file(key=key)

    with Then("DESCRIBE reports the aggregate types"):
        columns = describe(s3_function(key), settings=STATE_SETTINGS)
        assert columns == [("k", "Int32"), ("u", U_TYPE), ("s", S_TYPE)], error(columns)

    with And("the states merge"):
        assert_merge_matches(source=s3_function(key), expected=expected_result())


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Parquet_SchemaInference_Disabled("1.0"))
def schema_inference_refused_without_setting(self):
    """Without the setting a file naming an AggregateFunction is refused, not
    read as String."""
    with Given("a Parquet file with states"):
        key = parquet_key()
        write_states_file(key=key)

    with Then("DESCRIBE without the setting is refused"):
        query_refused(query=f"DESCRIBE {s3_function(key)}", message=SETTING)

    with And("SELECT without the setting is refused"):
        query_refused(query=f"SELECT u FROM {s3_function(key)}", message=SETTING)


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Parquet_ExplicitStructure("1.0"))
def explicit_structure_overrides_column_types(self):
    """An explicit structure needs no setting: u reads as its raw bytes and a
    CAST turns them back into states."""
    node = self.context.node

    with Given("a Parquet file with states"):
        key = parquet_key()
        write_states_file(key=key)

    with When("reading with u as String and no setting"):
        function = s3_function(key, structure="k Int32, u String, s Int64")
        actual = node.query(
            f"SELECT k, uniqMerge(CAST(u AS {U_TYPE})), sum(s) FROM {function} "
            "GROUP BY k ORDER BY k FORMAT TabSeparated"
        ).output

    with Then("the cast states merge"):
        expected = expected_result()
        assert actual == expected, error(f"merged:\n{actual}\nexpected:\n{expected}")


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Parquet_SimpleAggregateFunction("1.0"))
def simple_column_not_gated(self):
    """A SimpleAggregateFunction column is written and read back without the
    setting, as an ordinary value of its storage type."""
    node = self.context.node

    with Given("a key"):
        key = parquet_key()

    with When("writing a simple column without the setting"):
        node.query(
            f"INSERT INTO FUNCTION {s3_function(key)} "
            "SELECT toInt32(number % 2) AS k, sumSimpleState(toInt64(number)) AS s "
            "FROM numbers(200) GROUP BY k"
        )

    with Then("s is an ordinary Int64 column"):
        s = parquet_column(parquet_metadata(key), "s")
        assert s.physical_type == "INT64", error(s.physical_type)

    with And("DESCRIBE without the setting reports SimpleAggregateFunction"):
        columns = describe(s3_function(key))
        assert columns == [("k", "Int32"), ("s", S_TYPE)], error(columns)


@TestFeature
@Name("parquet footer")
def feature(self):
    """Aggregate states in standalone Parquet files."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
