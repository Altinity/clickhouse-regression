from testflows.core import *

from alter.table.replace_partition.common import (
    check_partition_was_replaced,
    create_partitions_with_random_uint64,
)
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid, replace_partition
from helpers.create import (
    partitioned_merge_tree_table,
    partitioned_replacing_merge_tree_table,
    partitioned_summing_merge_tree_table,
    partitioned_collapsing_merge_tree_table,
    partitioned_versioned_collapsing_merge_tree_table,
    partitioned_graphite_merge_tree_table,
    partitioned_aggregating_merge_tree_table,
    create_replicated_merge_tree_table,
)


@TestStep(Given)
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Replicas("1.0"))
def partitioned_replicated_merge_tree_table(self, table_name, partition, columns=None):
    """Create a ReplicatedMergeTree table partitioned by a specific column."""
    with By(
        f"creating a partitioned {table_name} table with a ReplicatedMergeTree engine"
    ):
        create_replicated_merge_tree_table(
            table_name=table_name, columns=columns, partition_by=partition
        )

    with And("populating it with the data needed to create multiple partitions"):
        create_partitions_with_random_uint64(table_name=table_name)


def columns():
    partition_columns = [
        {"name": "p", "type": "Int8"},
        {"name": "i", "type": "UInt64"},
        {"name": "Path", "type": "String"},
        {"name": "Time", "type": "DateTime"},
        {"name": "Value", "type": "Float64"},
        {"name": "Timestamp", "type": "Int64"},
    ]

    return partition_columns


@TestCheck
def check_replace_partition(self, destination_table, source_table):
    """Check that it is possible to use the replace partition command on tables with different table engines."""
    destination_table_name = "destination_" + getuid()
    source_table_name = "source_" + getuid()

    with Given(
        "I create two tables that have partitions with specific engines",
        description=f"""
               Table engines:
               Destination table: {destination_table.__name__}
               Source table: {source_table.__name__}
               """,
    ):
        destination_table(
            table_name=destination_table_name, partition="p", columns=columns()
        )
        source_table(table_name=source_table_name, partition="p", columns=columns())

    with When("I replace partition from the source table to the destination table"):
        replace_partition(
            destination_table=destination_table_name,
            source_table=source_table_name,
            partition=1,
        )

    with Then("I check that the partition on the destination table was replaced"):
        check_partition_was_replaced(
            destination_table=destination_table_name, source_table=source_table_name
        )


@TestSketch(Scenario)
@Flags(TE)
def replace_partition_with_different_engines(self):
    """Run test check with different table engines to see if replace partition is possible."""
    values = {
        partitioned_merge_tree_table,
        partitioned_replacing_merge_tree_table,
        partitioned_summing_merge_tree_table,
        partitioned_collapsing_merge_tree_table,
        partitioned_versioned_collapsing_merge_tree_table,
        partitioned_graphite_merge_tree_table,
        partitioned_aggregating_merge_tree_table,
        partitioned_replicated_merge_tree_table,
    }

    check_replace_partition(
        destination_table=either(*values),
        source_table=either(*values),
    )


@TestFeature
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Supported_Engines("1.0")
)
@Name("engines")
def feature(self, node="clickhouse1"):
    """Check replace partition with MergeTree family engines.

    Engines from MergeTree family:
    * MergeTree
    * ReplacingMergeTree
    * SummingMergeTree
    * CollapsingMergeTree
    * VersionedCollapsingMergeTree
    * GraphiteMergeTree
    * AggregatingMergeTree
    * ReplicatedMergeTree
    """
    self.context.node = self.context.cluster.node(node)

    Scenario(run=replace_partition_with_different_engines)
