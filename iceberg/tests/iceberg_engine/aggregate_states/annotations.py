"""How ClickHouse reads `clickhouse.type` annotations it did not write
itself: a wrong one is refused, a missing one falls back to the Iceberg type.

Each scenario stores an edited copy of the table's metadata as the next
metadata version, as another writer committing to the table would."""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.aggregate_states import *
from iceberg.tests.iceberg_engine.aggregate_states.steps import *


@TestCheck
def check_annotation_refused(self, field, annotation, message):
    """Another writer sets ``field``'s annotation to ``annotation``: reading
    the table fails with ``message`` instead of choosing a deserializer."""
    with Given("a table with states"):
        table_name = iceberg_s3_table()
        insert_states(table_name=table_name)
        prefix = table_prefix(table_name)

    with When(f"another writer sets {field} to {annotation}"):
        metadata, _ = read_latest_metadata(prefix)
        write_metadata_version(prefix, edit_annotations(metadata, {field: annotation}))

    with Then("reading the table is refused"):
        query_refused(
            query=merge_select(icebergs3_function(table_name)),
            settings=STATE_SETTINGS,
            message=message,
        )


@TestSketch(Scenario)
@Flags(TE)
@Requirements(RQ_Iceberg_AggregateStates_Iceberg_Annotation_Mismatch("1.0"))
def mismatched_annotation_refused(self):
    """An annotation of a different shape than the field's Iceberg type, or
    one that is no valid type at all, fails the read."""
    field, annotation, message = either(
        ("s", U_TYPE, "ICEBERG_SPECIFICATION_VIOLATION"),
        (
            "k",
            "SimpleAggregateFunction(groupArrayArray, Array(Int32))",
            "ICEBERG_SPECIFICATION_VIOLATION",
        ),
        ("k", "SimpleAggregateFunction(sum, String)", "ILLEGAL_TYPE_OF_ARGUMENT"),
        ("u", "NotAClickHouseType(1)", "UNKNOWN_TYPE"),
    )
    check_annotation_refused(field=field, annotation=annotation, message=message)


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Iceberg_Annotation_Mismatch("1.0"))
def primitive_retype_refused(self):
    """An annotation naming a different primitive type than the field's,
    `SimpleAggregateFunction(anyLast, String)` on an `int` field, fails the
    read rather than reading the column as String."""
    check_annotation_refused(
        field="k",
        annotation="SimpleAggregateFunction(anyLast, String)",
        message="ICEBERG_SPECIFICATION_VIOLATION",
    )


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Iceberg_Annotation_Missing("1.0"))
def missing_annotation_reads_storage_type(self):
    """With the annotations gone the columns read as their Iceberg types, no
    setting is needed, and casting the binary column back recovers the states.
    This is what a ClickHouse reader sees after an external engine drops them."""
    node = self.context.node

    with Given("a table with states"):
        table_name = iceberg_s3_table()
        insert_states(table_name=table_name)
        prefix = table_prefix(table_name)
        function = icebergs3_function(table_name)

    with When("another writer drops the annotations"):
        metadata, _ = read_latest_metadata(prefix)
        write_metadata_version(
            prefix, edit_annotations(metadata, {"u": None, "s": None})
        )

    with Then("DESCRIBE without the setting reports the storage types"):
        columns = describe(function)
        assert columns == [("k", "Int32"), ("u", "String"), ("s", "Int64")], error(
            columns
        )

    with And("casting u back to its state type recovers the merge"):
        actual = node.query(
            f"SELECT k, uniqMerge(CAST(u AS {U_TYPE})), sum(s) FROM {function} "
            "GROUP BY k ORDER BY k FORMAT TabSeparated"
        ).output
        expected = expected_result()
        assert actual == expected, error(f"merged:\n{actual}\nexpected:\n{expected}")


@TestFeature
@Name("annotations")
def feature(self):
    """Annotations written by someone else."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
