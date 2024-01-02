from testflows.core import *

from alter.table.attach_partition.common import *
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import (
    getuid,
)
from helpers.tables import *
from alter.table.replace_partition.engines import (
    partitioned_replicated_merge_tree_table,
)


def valid_partition_key_pair(source_partition_key, destination_partition_key):

    """Validates if pair source partition key - destination partition key is valid for `attach partition from` statement."""
    different = {
        "(intDiv(a,2),intDiv(b,2))": [
            "(a%2,b%2)",
            "(b%2,a%2)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "(intDiv(b,2),intDiv(a,2))": [
            "(a%2,b%2)",
            "(b%2,a%2)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
    }
    not_subset = {
        "tuple()": [
            "a",
            "a%2",
            "a%3",
            "intDiv(a,2)",
            "intDiv(a,3)",
            "b",
            "b%2",
            "intDiv(b,2)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2), b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
            "(b,a)",
            "(b%2,a%2)",
            "(intDiv(b,2),intDiv(a,2))",
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "a": [
            "b",
            "b%2",
            "intDiv(b,2)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2), b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
            "(b,a)",
            "(b%2,a%2)",
            "(intDiv(b,2),intDiv(a,2))",
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "a%2": [
            "b",
            "b%2",
            "intDiv(b,2)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2), b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
            "(b,a)",
            "(b%2,a%2)",
            "(intDiv(b,2),intDiv(a,2))",
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "a%3": [
            "b",
            "b%2",
            "intDiv(b,2)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2), b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
            "(b,a)",
            "(b%2,a%2)",
            "(intDiv(b,2),intDiv(a,2))",
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "intDiv(a,2)": [
            "b",
            "b%2",
            "intDiv(b,2)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2), b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
            "(b,a)",
            "(b%2,a%2)",
            "(intDiv(b,2),intDiv(a,2))",
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "intDiv(a,3)": [
            "b",
            "b%2",
            "intDiv(b,2)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2), b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
            "(b,a)",
            "(b%2,a%2)",
            "(intDiv(b,2),intDiv(a,2))",
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "b": [
            "a",
            "a%2",
            "a%3",
            "intDiv(a,2)",
            "intDiv(a,3)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2), b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
            "(b,a)",
            "(b%2,a%2)",
            "(intDiv(b,2),intDiv(a,2))",
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "b%2": [
            "a",
            "a%2",
            "a%3",
            "intDiv(a,2)",
            "intDiv(a,3)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2), b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
            "(b,a)",
            "(b%2,a%2)",
            "(intDiv(b,2),intDiv(a,2))",
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "intDiv(b,2)": [
            "a",
            "a%2",
            "a%3",
            "intDiv(a,2)",
            "intDiv(a,3)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2), b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
            "(b,a)",
            "(b%2,a%2)",
            "(intDiv(b,2),intDiv(a,2))",
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "(a,b)": [
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "(a,b%2)": [
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "(intDiv(a,2), b)": [
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "(a%2,b%2)": [
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "(intDiv(a,2),intDiv(b,2))": [
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "(a,intDiv(b,2))": [
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "(b,a)": [
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "(b%2,a%2)": [
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "(intDiv(b,2),intDiv(a,2))": [
            "(b,c)",
            "(a,c)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
    }

    not_monotonic = {
        "a": ["a%2", "a%3"],
        "a%2": ["a%3"],
        "a%3": ["a%2"],
        "intDiv(a,2)": ["a%2", "a%3"],
        "intDiv(a,3)": ["a%2", "a%3"],
        "b": ["b%2"],
        "intDiv(b,2)": ["b%2"],
        "(a,b)": ["a%2", "a%3", "b%2", "(a,b%2)", "(a%2,b%2)", "(b%2,a%2)"],
        "(a,b%2)": [
            "a%2",
            "a%3",
            "(a%2,b%2)",
            "(b%2,a%2)",
        ],
        "(intDiv(a,2), b)": ["a%2", "a%3", "b%2", "(a,b%2)", "(a%2,b%2)", "(b%2,a%2)"],
        "(a%2,b%2)": ["a%3", "(a,b%2)"],
        "(intDiv(a,2),intDiv(b,2))": [
            "a%2",
            "a%3",
            "b%2",
            "(a,b%2)",
            "(a%2,b%2)",
            "(b%2,a%2)",
        ],
        "(a,intDiv(b,2))": ["a%2", "a%3", "b%2", "(a,b%2)", "(a%2,b%2)", "(b%2,a%2)"],
        "(b,a)": ["a%2", "a%3", "b%2", "(a,b%2)", "(a%2,b%2)", "(b%2,a%2)"],
        "(b%2,a%2)": ["a%3", "(a,b%2)"],
        "(b,c)": ["b%2"],
        "(a,c)": ["b%2"],
        "(intDiv(b,2),intDiv(a,2))": [
            "a%2",
            "a%3",
            "b%2",
            "(a,b%2)",
            "(a%2,b%2)",
            "(b%2,a%2)",
        ],
        "(a,b,c)": ["a%2", "a%3", "b%2", "(a,b%2)", "(a%2,b%2)", "(b%2,a%2)"],
        "(a,c,b)": ["a%2", "a%3", "b%2", "(a,b%2)", "(a%2,b%2)", "(b%2,a%2)"],
        "(b,a,c)": ["a%2", "a%3", "b%2", "(a,b%2)", "(a%2,b%2)", "(b%2,a%2)"],
        "(b,c,a)": ["a%2", "a%3", "b%2", "(a,b%2)", "(a%2,b%2)", "(b%2,a%2)"],
        "(c,a,b)": ["a%2", "a%3", "b%2", "(a,b%2)", "(a%2,b%2)", "(b%2,a%2)"],
        "(c,b,a)": ["a%2", "a%3", "b%2", "(a,b%2)", "(a%2,b%2)", "(b%2,a%2)"],
    }

    partially_different = {
        "a%2": ["a", "intDiv(a,2)", "intDiv(a,3)"],
        "a%3": ["a", "intDiv(a,3)"],
        "intDiv(a,2)": ["a", "intDiv(a,3)"],
        "intDiv(a,3)": ["a", "intDiv(a,2)"],
        "b%2": ["b", "intDiv(b,2)"],
        "intDiv(b,2)": ["b"],
        "(intDiv(a,2),intDiv(b,2))": [
            "a",
            "b",
            "(a,b)",
            "(b,a)",
            "intDiv(a,3)",
            "(a,intDiv(b,2))",
            "(intDiv(a,2), b)",
        ],
        "(a%2,b%2)": [
            "a",
            "b",
            "intDiv(a,2)",
            "intDiv(a,3)",
            "intDiv(b,2)",
            "(a,b)",
            "(b,a)",
            "(intDiv(a,2),intDiv(b,2))",
            "(intDiv(b,2),intDiv(a,2))",
            "(a,intDiv(b,2))",
            "(intDiv(a,2), b)",
        ],
        "(intDiv(b,2),intDiv(a,2))": [
            "a",
            "b",
            "(a,b)",
            "(b,a)",
            "intDiv(a,3)",
            "(a,intDiv(b,2))",
            "(intDiv(a,2), b)",
        ],
        "(b%2,a%2)": [
            "a",
            "b",
            "intDiv(a,2)",
            "intDiv(a,3)",
            "intDiv(b,2)",
            "(a,b)",
            "(b,a)",
            "(intDiv(a,2),intDiv(b,2))",
            "(intDiv(b,2),intDiv(a,2))",
            "(a,intDiv(b,2))",
            "(intDiv(a,2), b)",
        ],
    }

    if destination_partition_key in not_monotonic.get(source_partition_key, ""):
        return False, "not monotonic"

    if destination_partition_key in not_subset.get(source_partition_key, ""):
        return False, "not subset"

    if destination_partition_key in different.get(source_partition_key, ""):
        return False, "different"

    if destination_partition_key in partially_different.get(source_partition_key, ""):
        return False, "partially different"

    return True, ""


@TestScenario
@Flags(TE)
def check_attach_partition_from(
    self,
    source_table,
    destination_table,
    source_partition_key,
    destination_partition_key,
    source_table_engine="MergeTree",
    destination_table_engine="MergeTree",
):
    """Check `attach partition from` statement with different types of source and destination tables."""
    node = self.context.node

    source_table_name = "source_" + getuid()
    destination_table_name = "destination_" + getuid()

    with Given(
        "I create two tables with specified engines and partition keys",
        description=f"""
               partition keys:
               source table partition key: {source_partition_key}
               destination table partition key: {destination_partition_key}
               engines:
               source table engine: {destination_table_engine}
               destination table: {source_table_engine}
               """,
    ):
        source_table(
            table_name=source_table_name,
            engine=source_table_engine,
            partition_by=source_partition_key,
        )
        destination_table(
            table_name=destination_table_name,
            engine=destination_table_engine,
            partition_by=destination_partition_key,
        )

    with And("I attach partition from source table into destination table"):
        partition_ids = set(
            node.query(
                f"SELECT partition_id FROM system.parts WHERE table='{source_table_name}'"
            ).output.split()
        )
        valid, reason = valid_partition_key_pair(
            source_partition_key, destination_partition_key
        )
        if valid:
            for partition_id in partition_ids:
                query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION ID '{partition_id}' FROM {source_table_name}"
                node.query(query)

            with Then("I check that specidied partition was attached"):
                source_partition_data = node.query(
                    f"SELECT * FROM {source_table_name} ORDER BY a,b,c"
                ).output
                destination_partition_data = node.query(
                    f"SELECT * FROM {destination_table_name} ORDER BY a,b,c"
                ).output

                assert source_partition_data == destination_partition_data
        else:
            exitcode = None
            message = None

            if reason == "not monotonic":
                exitcode = 36
                message = "DB::Exception: Destination table partition expression is not monotonically increasing."
            elif reason == "not subset":
                exitcode = 36
                message = "DB::Exception: Destination table partition expression columns must be a subset of source table partition expression columns."
            elif reason == "different":
                exitcode = 248
                message = "DB::Exception: Can not create the partition. A partition can not contain values that have different partition ids."
            elif reason == "partially different":
                skip("to do")

            for partition_id in partition_ids:
                query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION ID '{partition_id}' FROM {source_table_name}"
                node.query(
                    query,
                    exitcode=exitcode,
                    message=message,
                )


@TestSketch(Scenario)
@Flags(TE)
def attach_partition_from(self):
    """Run test check with different partition keys for both source and destination tables to see if `attach partition from` is possible."""

    partition_keys = {
        "tuple()",
        "a",
        "a%2",
        "a%3",
        "intDiv(a,2)",
        "intDiv(a,3)",
        "b",
        "b%2",
        "intDiv(b,2)",
        "(a,b)",
        "(b,c)",
        "(a,c)",
        "(a%2,b%2)",
        "(a,intDiv(b,2))",
        "(a,b%2)",
        "(intDiv(a,2), b)",
        "(intDiv(a,2),intDiv(b,2))",
        "(b,a)",
        "(b%2,a%2)",
        "(intDiv(b,2),intDiv(a,2))",
        "(a,b,c)",
        "(a,c,b)",
        "(b,a,c)",
        "(b,c,a)",
        "(c,a,b)",
        "(c,b,a)",
    }

    engines = {
        "MergeTree",
        # "ReplacingMergeTree",
        # "AggregatingMergeTree",
        # "SummingMergeTree",
        #     # "CollapsingMergeTree",
        #     # "VersionedCollapsingMergeTree",
        #     # "GraphiteMergeTree",
    }

    check_attach_partition_from(
        source_table=create_partitioned_table_with_data,
        destination_table=create_empty_partitioned_table,
        source_table_engine=either(*engines),
        destination_table_engine=either(*engines),
        source_partition_key=either(*partition_keys),
        destination_partition_key=either(*partition_keys),
    )


@TestFeature
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Key_PartitionKey(
        "1.0"
    )
)
@Name("partition key")
def feature(self, node="clickhouse1"):
    """Check conditions for partition key."""

    self.context.node = self.context.cluster.node(node)

    Scenario(run=attach_partition_from)
