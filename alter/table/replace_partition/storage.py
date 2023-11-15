from alter.table.replace_partition.common import (
    create_table_partitioned_by_column_with_data,
)
from alter.table.replace_partition.requirements.requirements import *
from helpers.alter import *
from helpers.common import getuid, replace_partition


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Disks("1.0"))
def different_disks(self):
    """Check that it is possible to replace partition on a destination table from a source tale that is stored on a
    different disk."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given("I have a partitioned destination table that is stored on disk1"):
        create_table_partitioned_by_column_with_data(
            table_name=destination_table, query_settings="storage_policy = 'policy1'"
        )

    with And("I have a partitioned source table that is stored on the disk2"):
        create_table_partitioned_by_column_with_data(
            table_name=source_table, query_settings="storage_policy = 'policy2'"
        )

    with Then("I try to replace partition on the destination table"):
        replace_partition(
            destination_table=destination_table, source_table=source_table
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Shards("1.0"))
def shards(self):
    """Check that it is possible to replace partition on a destination table from a source tale that is stored on a
    different shard."""
    node = self.context.node
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    destination_table_shard = "shard_destination_" + getuid()
    source_table_shard = "shard_source_" + getuid()

    with Given("I have a partitioned destination table that is stored on disk1"):
        create_table_partitioned_by_column_with_data(
            table_name=destination_table, query_settings="storage_policy = 'policy1'"
        )

    with And("I have a partitioned source table that is stored on the disk2"):
        create_table_partitioned_by_column_with_data(
            table_name=source_table, query_settings="storage_policy = 'policy2'"
        )

    with When("I create two distributed tables on two different shards"):
        node.query(
            f"CREATE TABLE {destination_table_shard} as {destination_table} ENGINE = Distributed(test_cluster_two_shards_localhost, currentDatabase(), {destination_table}, p);"
        )
        node.query(
            f"CREATE TABLE {source_table_shard} as {source_table} ENGINE = Distributed(test_cluster_two_shards_localhost, currentDatabase(), {source_table}, p);"
        )

    with Then("I try to replace partition on the destination distributed table"):
        replace_partition(
            destination_table=destination_table, source_table=source_table
        )


@TestFeature
@Name("storage")
def feature(self, node="clickhouse1"):
    """Check it is possible to replace partition on a destination table when tables are stored in different storage types."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=different_disks)
    Scenario(run=shards)
