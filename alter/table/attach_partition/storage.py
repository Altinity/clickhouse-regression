from alter.table.attach_partition.common import (
    create_partitioned_table_with_data,
    create_empty_partitioned_table,
)
from alter.table.attach_partition.requirements.requirements import *
from helpers.alter import *
from helpers.common import (
    getuid,
    attach_partition_from,
    attach_partition,
    detach_partition,
    error,
    check_clickhouse_version,
)
from parquet.tests.common import start_minio


@TestScenario
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Shards("1.0"))
def shards(self):
    """Check that it is not possible to attach partition from source table to the destination table that is stored on a
    different shard."""
    node = self.context.node
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    destination_table_shard = "shard_destination_" + getuid()
    source_table_shard = "shard_source_" + getuid()

    with Given("I have a partitioned destination table that is stored on disk1"):
        create_partitioned_table_with_data(
            table_name=destination_table,
            partition_by="a",
            query_settings="storage_policy = 'policy1'",
        )

    with And("I have a partitioned source table that is stored on the disk2"):
        create_empty_partitioned_table(
            table_name=source_table,
            partition_by="a",
            query_settings="storage_policy = 'policy2'",
        )

    with When("I create two distributed tables on two different shards"):
        node.query(
            f"CREATE TABLE {destination_table_shard} as {destination_table} ENGINE = Distributed(test_cluster_two_shards_localhost, currentDatabase(), {destination_table}, a);"
        )
        node.query(
            f"CREATE TABLE {source_table_shard} as {source_table} ENGINE = Distributed(test_cluster_two_shards_localhost, currentDatabase(), {source_table}, a);"
        )

    with Then("I try to attach partition to the destination distributed table"):
        attach_partition_from(
            destination_table=destination_table_shard,
            source_table=destination_table_shard,
            message="DB::Exception: Table engine Distributed doesn't support partitioning.",
            exitcode=48,
        )


@TestCheck
def check_attach_partition_on_different_types_of_disks(
    self, destination_table, source_table
):
    """Check attach partition from with difrenet types of source and table storages."""
    destination_table_name = "destination_" + getuid()
    source_table_name = "source_" + getuid()

    with Given(
        "I create two MergeTree tables and one or both of them are stored on a minio disk",
        description=f"""
            table types:
            source table: {source_table.__name__}
            destination table: {destination_table.__name__}
            """,
    ):
        source_table(table_name=source_table_name)
        destination_table(table_name=destination_table_name)

    with Then(
        "I attach partition to the destination table and validate that the data was attached"
    ):
        if ("not" in source_table.__name__) == ("not" in destination_table.__name__):
            for partition in [1, 2, 3, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]:
                attach_partition_from(
                    destination_table=destination_table_name,
                    source_table=source_table_name,
                    partition=partition,
                )
            source_partition_data = self.context.node.query(
                f"SELECT * FROM {source_table_name} ORDER BY a,b,c,extra"
            )
            destination_partition_data = self.context.node.query(
                f"SELECT * FROM {destination_table_name} ORDER BY a,b,c,extra"
            )
            for attempt in retries(timeout=30, delay=2):
                with attempt:
                    assert (
                        destination_partition_data.output
                        == source_partition_data.output
                    ), error()
        else:
            if check_clickhouse_version(">=24.3")(self):
                exitcode, message = None, None
            else:
                exitcode, message = 36, "Exception: Could not clone and load part"
                
            attach_partition_from(
                destination_table=destination_table_name,
                source_table=source_table_name,
                message=message,
                exitcode=exitcode,
            )


@TestCheck
def check_attach_partition_detached_on_different_types_of_disks(self, table):
    """Check attach partition from detached folder when table stored on
    different types of disks."""

    table_name = "destination_" + getuid()

    with Given(
        "I create MergeTree table",
        description=f"""
            table type: {table.__name__}
            """,
    ):
        table(table_name=table_name)

        table_before = self.context.node.query(
            f"SELECT * FROM {table_name} ORDER BY a,b,c,extra"
        ).output

    with And("I detach partition from the table and check that partition was detached"):
        detach_partition(table=table_name)
        table_after_detach = self.context.node.query(
            f"SELECT * FROM {table_name} ORDER BY a,b,c,extra"
        )
        for attempt in retries(timeout=30, delay=2):
            with attempt:
                assert table_before != table_after_detach.output, error()

    with And("I attach detached partition back"):
        attach_partition(table=table_name)

    with Then("I check that data is the same as it was before attach detach"):
        table_after = self.context.node.query(
            f"SELECT * FROM {table_name} ORDER BY a,b,c,extra"
        )
        for attempt in retries(timeout=30, delay=2):
            with attempt:
                assert table_before == table_after.output, error()


@TestStep(Given)
def table_stored_on_minio_disk(self, table_name):
    """Create a MergeTree table partitioned by a colum that is stored on a minio disk."""
    create_partitioned_table_with_data(
        table_name=table_name,
        partition_by="a",
        query_settings="storage_policy = 's3_policy'",
    )


@TestStep(Given)
def empty_table_stored_on_minio_disk(self, table_name):
    """Create a MergeTree table partitioned by a colum that is stored on a minio disk."""
    create_empty_partitioned_table(
        table_name=table_name,
        partition_by="a",
        query_settings="storage_policy = 's3_policy'",
    )


@TestStep(Given)
def table_not_stored_on_minio_disk(self, table_name):
    """Create table that is not stored in a minio disk."""
    create_partitioned_table_with_data(table_name=table_name, partition_by="a")


@TestStep(Given)
def empty_table_not_stored_on_minio_disk(self, table_name):
    """Create table that is not stored in a minio disk."""
    create_empty_partitioned_table(table_name=table_name, partition_by="a")


@TestSketch(Scenario)
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_S3("1.0"))
@Flags(TE)
def attach_partition_on_minio_and_default_disks(self):
    """Run check that validates if it is possible to use attach partition from with tables that are and are not stored on minio storage."""
    source_tables = {
        table_stored_on_minio_disk,
        table_not_stored_on_minio_disk,
    }
    destination_tables = {
        empty_table_stored_on_minio_disk,
        empty_table_not_stored_on_minio_disk,
    }

    with Given("I start a minio client"):
        start_minio()

    check_attach_partition_on_different_types_of_disks(
        source_table=either(*source_tables),
        destination_table=either(*destination_tables),
    )


@TestSketch(Scenario)
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_S3("1.0"))
@Flags(TE)
def attach_partition_detached_on_different_types_of_disks(self):
    """Run check attach partition from detached folder."""
    tables = {table_stored_on_minio_disk, table_not_stored_on_tiered_storage}

    with Given("I start a minio client"):
        start_minio()

    check_attach_partition_detached_on_different_types_of_disks(
        table=either(*tables),
    )


@TestStep(Given)
def table_stored_on_tiered_storage(self, table_name):
    """Create a table stored in a tiered storage."""
    create_partitioned_table_with_data(
        table_name=table_name,
        partition_by="a",
        query_settings="storage_policy = 'fast_med_and_slow'",
    )


@TestStep(Given)
def empty_table_stored_on_tiered_storage(self, table_name):
    """Create a table stored in a tiered storage."""
    create_empty_partitioned_table(
        table_name=table_name,
        partition_by="a",
        query_settings="storage_policy = 'fast_med_and_slow'",
    )


@TestStep(Given)
def table_not_stored_on_tiered_storage(self, table_name):
    """Create a table which is not stored in the tiered storage."""
    create_partitioned_table_with_data(
        table_name=table_name,
        partition_by="a",
        query_settings="storage_policy = 'default'",
    )


@TestStep(Given)
def empty_table_not_stored_on_tiered_storage(self, table_name):
    """Create a table which is not stored in the tiered storage."""
    create_empty_partitioned_table(
        table_name=table_name,
        partition_by="a",
        query_settings="storage_policy = 'default'",
    )


@TestSketch(Scenario)
@Flags(TE)
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_TieredStorage("1.0"))
def attach_partition_on_tiered_and_default_storages(self):
    """Run check that validates if it is possible to use attach partition from with tables that are and are not stored on tiered storage."""
    source_tables = {
        table_stored_on_tiered_storage,
        table_not_stored_on_tiered_storage,
    }
    destination_tables = {
        empty_table_stored_on_tiered_storage,
        empty_table_not_stored_on_tiered_storage,
    }

    check_attach_partition_on_different_types_of_disks(
        source_table=either(*source_tables),
        destination_table=either(*destination_tables),
    )


@TestFeature
@Name("storage")
def feature(self, node="clickhouse1"):
    """Check it is possible to attach partition from source table to a destination table when tables are stored in different storage
    types."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=shards)
    Scenario(run=attach_partition_on_minio_and_default_disks)
    Scenario(run=attach_partition_on_tiered_and_default_storages)
    Scenario(run=attach_partition_detached_on_different_types_of_disks)
