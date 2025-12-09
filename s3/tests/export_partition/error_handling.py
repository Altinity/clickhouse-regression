from testflows.core import *
from testflows.asserts import error
from s3.tests.export_partition.steps import export_partitions
from s3.tests.export_part.steps import *
from helpers.queries import *
from helpers.common import getuid
from s3.requirements.export_partition import *


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_SourcePartition("1.0"))
def partition_does_not_exist(self):
    """Check that exporting a non-existent partition returns the correct error."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I create an invalid part name"):
        invalid_partition = "999999"

    with When("I try to export the invalid part"):
        results = export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            partitions=[invalid_partition],
            exitcode=1,
            check_export=False
        )

    with Then("I should see an error related to the invalid part name"):
        assert results[0].exitcode == 36, error()
        assert (
            f"Partition {invalid_partition} doesn't exist." in results[0].output
        ), error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_SameTable("1.0"))
def same_table(self):
    """Check exporting partitions where source and destination tables are the same."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
        )

    with When("I try to export partitions to itself"):
        results = export_partitions(
            source_table=source_table,
            destination_table=source_table,
            node=self.context.node,
            exitcode=1,
            check_export=False
        )

    with Then("I should see an error related to same table exports"):
        assert results[0].exitcode == 36, error()
        assert (
            "Exporting to the same table is not allowed" in results[0].output
        ), error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_LocalTable("1.0"))
def local_table(self):
    """Test exporting partitions to a local table."""

    source_table = f"source_{getuid()}"
    destination_table = f"destination_{getuid()}"
    with Given("I create a populated source table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
        )

    with And("I create an empty local table"):
        partitioned_replicated_merge_tree_table(
            table_name=destination_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
            populate=False,
        )

    with When("I export partitions to the local table"):
        results = export_partitions(
            source_table=source_table,
            destination_table=destination_table,
            node=self.context.node,
            exitcode=1,
            check_export=False
        )

    with Then("I should see an error related to local table exports"):
        assert results[0].exitcode == 48, error()
        assert (
            "Destination storage ReplicatedMergeTree does not support MergeTree parts or uses unsupported partitioning."
            in results[0].output
        ), error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("1.0"))
def different_partition_key(self):
    """Check exporting partitions with a different partition key returns the correct error."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="i",
            columns=default_columns(),
            stop_merges=False,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I try to export the partitions"):
        results = export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            exitcode=1,
            check_export=False
        )

    with Then("I should see an error related to the different partition key"):
        assert results[0].exitcode == 36, error()
        assert "Tables have different partition key" in results[0].output, error()


@TestFeature
@Name("error handling")
@Requirements(
    RQ_ClickHouse_ExportPartition_Restrictions_SameTable("1.0"),
    RQ_ClickHouse_ExportPartition_Restrictions_LocalTable("1.0"),
    RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("1.0"),
    RQ_ClickHouse_ExportPartition_Settings_AllowExperimental_Disabled("1.0"),
)
def feature(self):
    """Check correct error handling when exporting partitions."""

    Scenario(run=partition_does_not_exist)
    Scenario(run=same_table)
    Scenario(run=local_table)
    Scenario(run=different_partition_key)
