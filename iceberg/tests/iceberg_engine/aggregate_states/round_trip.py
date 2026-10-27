"""States written to an Iceberg table merge exactly as in AggregatingMergeTree."""

import re

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.requirements.aggregate_states import *
from iceberg.tests.iceberg_engine.aggregate_states.steps import *


@TestScenario
@Requirements(
    RQ_Iceberg_AggregateStates_Iceberg_TypeMapping("1.0"),
    RQ_Iceberg_AggregateStates_Iceberg_Annotation("1.0"),
    RQ_Iceberg_AggregateStates_Iceberg_MergeEquivalence("1.0"),
    RQ_Iceberg_AggregateStates_Parquet_ColumnTypesMetadata("1.0"),
    RQ_Iceberg_AggregateStates_Parquet_Write("1.0"),
)
def uniq_and_sum(self):
    """The issue #2206 shape: `uniq` states and a `sum` simple column in a
    partitioned table. The types map, the fields are annotated, every data
    file records the types in its footer, and the states merge."""
    with Given("a partitioned table with states"):
        table_name = iceberg_s3_table(partition_by="k")
        insert_states(table_name=table_name)
        prefix = table_prefix(table_name)

    with Then("the table engine and the table function report the annotated types"):
        expected_columns = [("k", "Int32"), ("u", U_TYPE), ("s", S_TYPE)]
        for expr in (table_name, icebergs3_function(table_name)):
            with By(f"DESCRIBE {expr.split('(')[0]}"):
                columns = describe(expr, settings=STATE_SETTINGS)
                assert columns == expected_columns, error(columns)

    with And("the states merge to the result over the original rows"):
        assert_merge_matches(source=table_name, expected=expected_result())
        assert_merge_matches(
            source=icebergs3_function(table_name), expected=expected_result()
        )

    with And("the Iceberg types map and only the aggregate fields are annotated"):
        metadata, key = read_latest_metadata(prefix)
        fields = fields_by_name(metadata)
        assert [fields[name]["type"] for name in ("k", "u", "s")] == [
            "int",
            "binary",
            "long",
        ], error(fields)
        assert_annotations(
            metadata=metadata,
            expected={"k": None, "u": U_TYPE, "s": S_TYPE},
            where=key,
        )

    with And("every data file is plain binary for u and records the types"):
        keys = data_file_keys(prefix)
        assert len(keys) == 2, error(f"expected one data file per partition: {keys}")
        for key in keys:
            with By(key.rsplit("/", 1)[-1]):
                column_types = parquet_column_types(key)
                assert column_types is not None, error("no clickhouse.column_types")
                assert column_types.get("u", "").startswith("AggregateFunction("), error(
                    column_types
                )
                assert "uniq" in column_types["u"], error(column_types)
                assert column_types.get("s") == S_TYPE, error(column_types)
                u = parquet_column(parquet_metadata(key), "u")
                assert is_plain_binary(u), error(
                    f"u is {u.physical_type} logical={u.logical_type} "
                    f"converted={u.converted_type}"
                )


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Iceberg_MergeEquivalence("1.0"))
def merge_across_inserts(self):
    """Overlapping inserts land in separate data files; merging across all of
    them equals aggregating the multiset of original rows."""
    node = self.context.node
    batches = [(0, 200), (100, 200), (250, 150)]

    with Given("a table"):
        table_name = iceberg_s3_table()

    with When("three overlapping inserts"):
        for start, count in batches:
            insert_states(table_name=table_name, start=start, count=count)

    with Then("there is a data file per insert"):
        keys = data_file_keys(table_prefix(table_name))
        assert len(keys) >= len(batches), error(keys)

    with And("the merge equals the aggregate over every inserted row"):
        union = " UNION ALL ".join(
            f"SELECT number FROM numbers({start}, {count})" for start, count in batches
        )
        expected = node.query(
            "SELECT toInt32(number % 2) AS k, uniq(toUInt64(number % 23)), "
            f"sum(toInt64(number)) FROM ({union}) GROUP BY k ORDER BY k "
            "FORMAT TabSeparated"
        ).output
        assert_merge_matches(source=table_name, expected=expected)


@TestOutline(Scenario)
@Requirements(
    RQ_Iceberg_AggregateStates_Iceberg_MergeEquivalence("1.0"),
    RQ_Iceberg_AggregateStates_Iceberg_Annotation("1.0"),
)
@Examples(
    "type_name state merge direct",
    [
        ("AggregateFunction(count)", "countState()", "countMerge(v)", "count()"),
        (
            "AggregateFunction(avg, Float64)",
            "avgState(toFloat64(number))",
            "avgMerge(v)",
            "avg(toFloat64(number))",
        ),
        (
            "AggregateFunction(uniqExact, String)",
            "uniqExactState(toString(number % 37))",
            "uniqExactMerge(v)",
            "uniqExact(toString(number % 37))",
        ),
        (
            "AggregateFunction(groupArray, UInt64)",
            "groupArrayState(number)",
            "arraySort(groupArrayMerge(v))",
            "arraySort(groupArray(number))",
        ),
        (
            "AggregateFunction(quantileExact(0.5), UInt64)",
            "quantileExactState(0.5)(number)",
            "quantileExactMerge(0.5)(v)",
            "quantileExact(0.5)(number)",
        ),
        (
            "AggregateFunction(argMax, String, UInt64)",
            "argMaxState(toString(number), number)",
            "argMaxMerge(v)",
            "argMax(toString(number), number)",
        ),
        (
            "SimpleAggregateFunction(max, UInt64)",
            "maxSimpleState(number)",
            "max(v)",
            "max(number)",
        ),
        (
            "SimpleAggregateFunction(min, Nullable(String))",
            "minSimpleState(toNullable(toString(number)))",
            "min(v)",
            "min(toString(number))",
        ),
    ],
    args=Args(flags=TE),
)
def aggregate_function(self, type_name, state, merge, direct):
    """One aggregate column of the given type, written in two inserts,
    merges to the aggregate over all rows and is annotated with its type."""
    node = self.context.node

    with Given(f"a table with v {type_name}"):
        table_name = iceberg_s3_table(columns=f"k Int32, v {type_name}")

    with When("two inserts"):
        for start in (0, 300):
            node.query(
                f"INSERT INTO {table_name} SELECT toInt32(number % 3) AS k, {state} "
                f"FROM numbers({start}, 300) GROUP BY k",
                settings=write_settings(),
            )

    with Then("DESCRIBE reports the type"):
        columns = describe(table_name, settings=STATE_SETTINGS)
        assert columns == [("k", "Int32"), ("v", type_name)], error(columns)

    with And("the merge equals the aggregate over all rows"):
        actual = node.query(
            f"SELECT k, {merge} FROM {table_name} GROUP BY k ORDER BY k "
            "FORMAT TabSeparated",
            settings=STATE_SETTINGS,
        ).output
        expected = node.query(
            f"SELECT toInt32(number % 3) AS k, {direct} FROM numbers(0, 600) "
            "GROUP BY k ORDER BY k FORMAT TabSeparated"
        ).output
        assert actual == expected, error(f"merged:\n{actual}\nexpected:\n{expected}")

    with And("the field is annotated"):
        metadata, key = read_latest_metadata(table_prefix(table_name))
        annotation = annotations(metadata)["v"]
        family, arguments = type_name.split("(", 1)
        function = re.split(r"[(,)]", arguments)[0]
        assert annotation is not None, error(f"v is not annotated in {key}")
        assert annotation.startswith(f"{family}("), error(annotation)
        assert function in annotation, error(annotation)


@TestScenario
@Requirements(
    RQ_Iceberg_AggregateStates_Iceberg_InsertSelectFromAggregatingMergeTree("1.0")
)
def insert_select_from_aggregating_merge_tree(self):
    """INSERT SELECT from an AggregatingMergeTree copies the states byte for
    byte, and both sides merge to the same result."""
    node = self.context.node

    with Given("an AggregatingMergeTree with two parts"):
        source = aggregating_merge_tree()
        for start in (0, 200):
            node.query(f"INSERT INTO {source} " + states_select(start=start, count=200))

    with And("an Iceberg table"):
        table_name = iceberg_s3_table()

    with When("INSERT INTO the Iceberg table SELECT * FROM the source"):
        node.query(
            f"INSERT INTO {table_name} SELECT * FROM {source}",
            settings=write_settings(),
        )

    with Then("the states are byte-identical"):
        query = "SELECT k, hex(u), s FROM {} ORDER BY k, hex(u), s FORMAT TabSeparated"
        source_rows = node.query(query.format(source)).output
        iceberg_rows = node.query(query.format(table_name), settings=STATE_SETTINGS).output
        assert iceberg_rows == source_rows, error(
            f"iceberg:\n{iceberg_rows}\nsource:\n{source_rows}"
        )

    with And("both sides merge to the same result"):
        assert_merge_matches(
            source=table_name, expected=node.query(merge_select(source)).output
        )


@TestFeature
@Name("round trip")
def feature(self):
    """States written by ClickHouse merge back to the same result."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
