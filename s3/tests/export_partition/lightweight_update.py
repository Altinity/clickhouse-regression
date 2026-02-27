from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from helpers.create import *
from helpers.queries import *
from s3.tests.export_partition.steps import *
from s3.requirements.export_partition import *


@TestStep(Given)
def create_table_with_lightweight_update_support(
    self,
    table_name,
    columns=None,
    partition_by="p",
    number_of_partitions=5,
    number_of_parts=10,
    cluster="replicated_cluster",
):
    """Create a table with lightweight update support enabled.

    Args:
        table_name: Name of the table to create
        columns: List of column definitions
        partition_by: Partition key
        number_of_partitions: Number of partitions to create
        number_of_parts: Number of parts per partition
        cluster: Cluster name
    """
    if columns is None:
        columns = [
            {"name": "p", "type": "UInt16"},
            {"name": "i", "type": "UInt64"},
            {"name": "extra", "type": "UInt8"},
        ]

    with Given(f"I create table {table_name} with lightweight update support"):
        partitioned_replicated_merge_tree_table(
            table_name=table_name,
            partition_by=partition_by,
            columns=columns,
            stop_merges=False,
            number_of_partitions=number_of_partitions,
            number_of_parts=number_of_parts,
            query_settings=(
                "enable_block_number_column = 1, " "enable_block_offset_column = 1"
            ),
            cluster=cluster,
        )


@TestStep(When)
def perform_lightweight_update(
    self,
    table_name,
    update_column,
    update_value,
    where_condition,
    node=None,
):
    """Perform a lightweight UPDATE operation.

    Args:
        table_name: Table to update
        update_column: Column to update
        update_value: Value to set
        where_condition: WHERE clause condition
        node: ClickHouse node to execute on
    """
    if node is None:
        node = self.context.node

    with By(f"performing lightweight UPDATE on {table_name}"):
        node.query(
            f"UPDATE {table_name} SET {update_column} = {update_value} "
            f"WHERE {where_condition}",
            exitcode=0,
        )


@TestStep(When)
def verify_patch_parts_exist(self, table_name, node=None):
    """Verify that patch parts exist for the table.

    Args:
        table_name: Table name to check
        node: ClickHouse node to execute on
    """
    if node is None:
        node = self.context.node

    with By("checking for patch parts"):
        result = node.query(
            f"SELECT COUNT(*) FROM system.parts "
            f"WHERE table = '{table_name}' AND name LIKE 'patch-%'",
            exitcode=0,
        )
        patch_count = int(result.output.strip())
        note(f"Found {patch_count} patch parts")
        return patch_count


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_S3("1.0"),
    RQ_ClickHouse_ExportPartition_LightweightUpdate("1.0"),
)
def export_with_lightweight_update_patch_parts(self):
    """Test that EXPORT PARTITION succeeds when patch parts exist from lightweight updates.

    The requirement is that EXPORT should succeed even in the presence of patch parts,
    though the patches might not be applied to the exported data.
    """
    source_table = f"source_{getuid()}"

    with Given("I create source and destination tables"):
        create_table_with_lightweight_update_support(
            table_name=source_table,
            number_of_partitions=5,
            number_of_parts=5,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get all partitions from the source table"):
        all_partitions = get_partitions(table_name=source_table, node=self.context.node)

    with When("I perform lightweight updates to create patch parts"):
        for partition in all_partitions[:3]:
            perform_lightweight_update(
                table_name=source_table,
                update_column="extra",
                update_value="99",
                where_condition=f"p = {partition}",
            )

    with And("I verify that patch parts exist"):
        patch_count = verify_patch_parts_exist(
            table_name=source_table, node=self.context.node
        )
        assert patch_count > 0, error("Expected patch parts to exist")

    with Then("I export partitions while patch parts exist"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            partitions=all_partitions,
        )

    with And("I verify that export completed successfully"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_S3("1.0"),
    RQ_ClickHouse_ExportPartition_LightweightUpdate("1.0"),
    RQ_ClickHouse_ExportPartition_LightweightUpdate_MultiplePatches("1.0"),
)
def export_with_multiple_lightweight_updates(self):
    """Test EXPORT PARTITION with multiple lightweight updates on the same partition."""
    source_table = f"source_{getuid()}"

    with Given("I create source and destination tables"):
        create_table_with_lightweight_update_support(
            table_name=source_table,
            number_of_partitions=3,
            number_of_parts=5,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get all partitions from the source table"):
        all_partitions = get_partitions(table_name=source_table, node=self.context.node)

    with When("I perform multiple lightweight updates on the same partition"):
        target_partition = all_partitions[0]
        perform_lightweight_update(
            table_name=source_table,
            update_column="extra",
            update_value="10",
            where_condition=f"p = {target_partition} AND i % 2 = 0",
        )
        perform_lightweight_update(
            table_name=source_table,
            update_column="extra",
            update_value="20",
            where_condition=f"p = {target_partition} AND i % 3 = 0",
        )
        perform_lightweight_update(
            table_name=source_table,
            update_column="extra",
            update_value="30",
            where_condition=f"p = {target_partition} AND i % 5 = 0",
        )

    with And("I verify that patch parts exist"):
        patch_count = verify_patch_parts_exist(
            table_name=source_table, node=self.context.node
        )
        assert patch_count > 0, error("Expected patch parts to exist")

    with Then("I export the updated partition"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            partitions=[target_partition],
        )

    with And("I verify that export completed successfully"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_S3("1.0"),
    RQ_ClickHouse_ExportPartition_LightweightUpdate("1.0"),
    RQ_ClickHouse_ExportPartition_LightweightUpdate_Concurrent("1.0"),
)
def export_after_lightweight_updates_on_all_partitions(self):
    """Test EXPORT PARTITION after lightweight updates on all partitions."""
    source_table = f"source_{getuid()}"

    with Given("I create source and destination tables"):
        create_table_with_lightweight_update_support(
            table_name=source_table,
            number_of_partitions=5,
            number_of_parts=5,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get all partitions from the source table"):
        all_partitions = get_partitions(table_name=source_table, node=self.context.node)

    with When("I perform lightweight updates on all partitions"):
        for i, partition in enumerate(all_partitions):
            perform_lightweight_update(
                table_name=source_table,
                update_column="extra",
                update_value=str(50 + i),
                where_condition=f"p = {partition}",
            )

    with And("I verify that patch parts exist"):
        patch_count = verify_patch_parts_exist(
            table_name=source_table, node=self.context.node
        )
        assert patch_count > 0, error("Expected patch parts to exist")

    with Then("I export all partitions"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            partitions=all_partitions,
        )

    with And("I verify that export completed successfully"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestFeature
@Name("lightweight update export partition")
@Requirements(RQ_ClickHouse_ExportPartition_S3("1.0"))
def feature(self, node="clickhouse1"):
    """Test that EXPORT PARTITION works correctly with lightweight updates."""
    self.context.node = self.context.cluster.node(node)

    with Given("I set up MinIO storage configuration"):
        minio_storage_configuration(restart=True)

    Scenario(run=export_with_lightweight_update_patch_parts)
    Scenario(run=export_with_multiple_lightweight_updates)
    Scenario(run=export_after_lightweight_updates_on_all_partitions)
