from alter.table.replace_partition.common import (
    create_table_partitioned_by_column_with_data,
    replace_partition_and_validate_data,
)
from alter.table.replace_partition.requirements.requirements import *
from helpers.alter import *
from helpers.common import getuid, replace_partition
from helpers.create import partitioned_replicated_merge_tree_table
from parquet.tests.common import start_minio


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Disks("1.0"))
def different_disks(self):
    """Check that it is not possible to replace partition on a destination table from a source tale that is stored on a
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
            destination_table=destination_table,
            source_table=source_table,
            message="DB::Exception: Could not clone and load part",
            exitcode=36,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Shards("1.0"))
def shards(self):
    """Check that it is not possible to replace partition on a destination table from a source tale that is stored on a
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
            destination_table=destination_table_shard,
            source_table=destination_table_shard,
            message="DB::Exception: Table engine Distributed doesn't support partitioning.",
            exitcode=48,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Replicas("1.0"))
def replicas(self):
    """Check that it is possible to replace partition on the destination table when both destination and source
    tables are replicated."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given("I have replicas of both destination and source tables created"):
        partitioned_replicated_merge_tree_table(
            table_name=destination_table, partition="p"
        )
        partitioned_replicated_merge_tree_table(table_name=source_table, partition="p")

    with Then(
        "I replace partition on the replicated destination table from the replicated source table"
    ):
        replace_partition_and_validate_data(
            destination_table=destination_table,
            source_table=source_table,
            partition_to_replace="1",
        )


@TestCheck
def check_replace_partition_on_different_types_of_disks(
    self, destination_table, source_table
):
    """Replace partition on a table that is stored in minio."""
    destination_table_name = "destination_" + getuid()
    source_table_name = "source_" + getuid()

    with Given(
        "I create two MergeTree tables and one of both of them are stored on a minio disk"
    ):
        destination_table(table_name=destination_table_name)
        source_table(table_name=source_table_name)

    with Then(
        "I replace partition on the destination table and validate that the data was replaced"
    ):
        replace_partition_and_validate_data(
            destination_table=destination_table_name,
            source_table=source_table_name,
            partition_to_replace=1,
        )


@TestStep(Given)
def table_stored_on_minio_disk(self, table_name):
    """Create a MergeTree table partitioned by a colum that is stored on a minio disk."""
    create_table_partitioned_by_column_with_data(
        table_name=table_name, query_settings="storage_policy = 's3_policy'"
    )


@TestStep(Given)
def table_not_stored_on_minio_disk(self, table_name):
    """Create table that is not stored in a minio disk."""
    create_table_partitioned_by_column_with_data(table_name=table_name)


@TestSketch(Scenario)
@Flags(TE)
def replace_partition_on_minio_and_default_disks(self):
    """Run check that validates if it is possible to replace partition on tables that are and are not stored on minio storage."""
    values = {
        table_stored_on_minio_disk,
        table_not_stored_on_minio_disk,
    }

    with Given("I start a minio client"):
        start_minio()

    check_replace_partition_on_different_types_of_disks(
        destination_table=either(*values),
        source_table=either(*values),
    )


@TestStep(Given)
def table_stored_on_tiered_storage(self, table_name):
    """Create a table stored in a tiered storage."""
    create_table_partitioned_by_column_with_data(
        table_name=table_name, query_settings="storage_policy = 'tiered_storage'"
    )


@TestStep(Given)
def table_not_stored_on_tiered_storage(self, table_name):
    """Create a table which is not stored in the tiered storage."""
    create_table_partitioned_by_column_with_data(table_name=table_name)


@TestSketch(Scenario)
@Flags(TE)
def replace_partition_on_tiered_and_default_storages(self):
    """Run check that validates if it is possible to replace partition on tables that are and are not stored on tiered storage."""
    values = {table_stored_on_tiered_storage, table_not_stored_on_tiered_storage}

    check_replace_partition_on_different_types_of_disks(
        destination_table=either(*values),
        source_table=either(*values),
    )


@TestFeature
@Name("storage")
def feature(self, node="clickhouse1"):
    """Check it is possible to replace partition on a destination table when tables are stored in different storage
    types."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=different_disks)
    Scenario(run=shards)
    Scenario(run=replicas)
    Scenario(run=replace_partition_on_minio_and_default_disks)
    Scenario(run=replace_partition_on_tiered_and_default_storages)
