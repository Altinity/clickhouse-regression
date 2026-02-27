from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from helpers.create import *
from helpers.queries import *
from s3.tests.export_partition.steps import *
from s3.requirements.export_partition import *


@TestStep(When)
def perform_lightweight_delete(
    self,
    table_name,
    where_condition,
    node=None,
):
    """Perform a lightweight DELETE operation."""
    if node is None:
        node = self.context.node

    with By(f"performing lightweight DELETE on {table_name}"):
        node.query(
            f"DELETE FROM {table_name} WHERE {where_condition}",
            exitcode=0,
        )


@TestStep(When)
def verify_deleted_rows_exist(self, table_name, node=None):
    """Verify that deleted rows exist in the table (marked with _row_exists = 0)."""
    if node is None:
        node = self.context.node

    with By("checking for deleted rows"):
        result = node.query(
            f"SELECT COUNT(*) FROM {table_name} WHERE _row_exists = 0",
            exitcode=0,
        )
        deleted_count = int(result.output.strip())
        note(f"Found {deleted_count} deleted rows")
        return deleted_count


@TestStep(When)
def get_row_count(self, table_name, node=None, include_deleted=False):
    """Get the total row count from a table."""
    if node is None:
        node = self.context.node

    if include_deleted:
        query = f"SELECT COUNT(*) FROM {table_name} SETTINGS allow_experimental_lightweight_delete = 1"
    else:
        query = f"SELECT COUNT(*) FROM {table_name}"

    result = node.query(query, exitcode=0)
    return int(result.output.strip())


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_S3("1.0"),
    RQ_ClickHouse_ExportPartition_LightweightDelete("1.0"),
)
def export_with_lightweight_delete_masks(self):
    """Test that EXPORT PARTITION succeeds and excludes deleted rows when lightweight deletes exist.

    The requirement is that EXPORT should succeed even when deleted rows exist,
    and should automatically apply the _row_exists mask to exclude deleted rows.
    """
    source_table = f"source_{getuid()}"

    with Given("I create source and destination tables"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=[
                {"name": "p", "type": "UInt16"},
                {"name": "i", "type": "UInt64"},
                {"name": "extra", "type": "UInt8"},
            ],
            stop_merges=False,
            number_of_partitions=5,
            number_of_parts=5,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get all partitions from the source table"):
        all_partitions = get_partitions(table_name=source_table, node=self.context.node)

    with And("I get the initial row count"):
        initial_row_count = get_row_count(
            table_name=source_table, include_deleted=False
        )

    with When("I perform lightweight deletes on some partitions"):
        for partition in all_partitions[:3]:
            perform_lightweight_delete(
                table_name=source_table,
                where_condition=f"p = {partition} AND i % 2 = 0",
            )

    with And("I verify that deleted rows exist"):
        deleted_count = verify_deleted_rows_exist(
            table_name=source_table, node=self.context.node
        )
        assert deleted_count > 0, error("Expected deleted rows to exist")

    with And("I verify that visible row count decreased"):
        visible_row_count = get_row_count(
            table_name=source_table, include_deleted=False
        )
        assert visible_row_count < initial_row_count, error(
            "Expected visible row count to decrease after delete"
        )

    with Then("I export partitions while deleted rows exist"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            partitions=all_partitions,
        )

    with And("I verify that export completed successfully and excluded deleted rows"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with And("I verify that destination table has correct row count"):
        destination_row_count = get_row_count(
            table_name=s3_table_name, include_deleted=False
        )
        assert destination_row_count == visible_row_count, error(
            f"Expected destination to have {visible_row_count} rows, got {destination_row_count}"
        )


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_S3("1.0"),
    RQ_ClickHouse_ExportPartition_LightweightDelete("1.0"),
    RQ_ClickHouse_ExportPartition_LightweightDelete_MultipleDeletes("1.0"),
)
def export_with_multiple_lightweight_deletes(self):
    """Test EXPORT PARTITION with multiple lightweight deletes on the same partition."""
    source_table = f"source_{getuid()}"

    with Given("I create source and destination tables"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=[
                {"name": "p", "type": "UInt16"},
                {"name": "i", "type": "UInt64"},
                {"name": "extra", "type": "UInt8"},
            ],
            stop_merges=False,
            number_of_partitions=3,
            number_of_parts=5,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get all partitions from the source table"):
        all_partitions = get_partitions(table_name=source_table, node=self.context.node)

    with And("I get the initial row count"):
        initial_row_count = get_row_count(
            table_name=source_table, include_deleted=False
        )

    with When("I perform multiple lightweight deletes on the same partition"):
        target_partition = all_partitions[0]
        perform_lightweight_delete(
            table_name=source_table,
            where_condition=f"p = {target_partition} AND i % 2 = 0",
        )
        perform_lightweight_delete(
            table_name=source_table,
            where_condition=f"p = {target_partition} AND i % 3 = 0",
        )
        perform_lightweight_delete(
            table_name=source_table,
            where_condition=f"p = {target_partition} AND i % 5 = 0",
        )

    with And("I verify that deleted rows exist"):
        deleted_count = verify_deleted_rows_exist(
            table_name=source_table, node=self.context.node
        )
        assert deleted_count > 0, error("Expected deleted rows to exist")

    with And("I get the visible row count after deletes"):
        visible_row_count = get_row_count(
            table_name=source_table, include_deleted=False
        )

    with Then("I export the partition with multiple deletes"):
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

    with And("I verify that destination table has correct row count"):
        destination_row_count = get_row_count(
            table_name=s3_table_name, include_deleted=False
        )
        assert destination_row_count == visible_row_count, error(
            f"Expected destination to have {visible_row_count} rows, got {destination_row_count}"
        )


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_S3("1.0"),
    RQ_ClickHouse_ExportPartition_LightweightDelete("1.0"),
    RQ_ClickHouse_ExportPartition_LightweightDelete_Concurrent("1.0"),
)
def export_after_lightweight_deletes_on_all_partitions(self):
    """Test EXPORT PARTITION after lightweight deletes on all partitions."""
    source_table = f"source_{getuid()}"

    with Given("I create source and destination tables"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=[
                {"name": "p", "type": "UInt16"},
                {"name": "i", "type": "UInt64"},
                {"name": "extra", "type": "UInt8"},
            ],
            stop_merges=False,
            number_of_partitions=5,
            number_of_parts=5,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get all partitions from the source table"):
        all_partitions = get_partitions(table_name=source_table, node=self.context.node)

    with And("I get the initial row count"):
        initial_row_count = get_row_count(
            table_name=source_table, include_deleted=False
        )

    with When("I perform lightweight deletes on all partitions"):
        for partition in all_partitions:
            perform_lightweight_delete(
                table_name=source_table,
                where_condition=f"p = {partition} AND i % 3 = 0",
            )

    with And("I verify that deleted rows exist"):
        deleted_count = verify_deleted_rows_exist(
            table_name=source_table, node=self.context.node
        )
        assert deleted_count > 0, error("Expected deleted rows to exist")

    with And("I get the visible row count after deletes"):
        visible_row_count = get_row_count(
            table_name=source_table, include_deleted=False
        )

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

    with And("I verify that destination table has correct row count"):
        destination_row_count = get_row_count(
            table_name=s3_table_name, include_deleted=False
        )
        assert destination_row_count == visible_row_count, error(
            f"Expected destination to have {visible_row_count} rows, got {destination_row_count}"
        )


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_S3("1.0"),
    RQ_ClickHouse_ExportPartition_LightweightDelete("1.0"),
)
def export_with_partial_delete(self):
    """Test EXPORT PARTITION when only some rows in a partition are deleted."""
    source_table = f"source_{getuid()}"

    with Given("I create source and destination tables"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=[
                {"name": "p", "type": "UInt16"},
                {"name": "i", "type": "UInt64"},
                {"name": "extra", "type": "UInt8"},
            ],
            stop_merges=False,
            number_of_partitions=3,
            number_of_parts=5,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get all partitions from the source table"):
        all_partitions = get_partitions(table_name=source_table, node=self.context.node)

    with And("I get the initial row count for the first partition"):
        initial_row_count = self.context.node.query(
            f"SELECT COUNT(*) FROM {source_table} WHERE p = {all_partitions[0]}",
            exitcode=0,
        )
        initial_count = int(initial_row_count.output.strip())

    with When("I delete half of the rows in the first partition"):
        perform_lightweight_delete(
            table_name=source_table,
            where_condition=f"p = {all_partitions[0]} AND i % 2 = 0",
        )

    with And("I verify the row count decreased"):
        visible_row_count = self.context.node.query(
            f"SELECT COUNT(*) FROM {source_table} WHERE p = {all_partitions[0]}",
            exitcode=0,
        )
        visible_count = int(visible_row_count.output.strip())
        assert visible_count < initial_count, error(
            "Expected visible row count to decrease after delete"
        )

    with Then("I export the partially deleted partition"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            partitions=[all_partitions[0]],
        )

    with And("I verify that export completed successfully"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with And("I verify that destination has correct row count"):
        destination_row_count = self.context.node.query(
            f"SELECT COUNT(*) FROM {s3_table_name} WHERE p = {all_partitions[0]}",
            exitcode=0,
        )
        destination_count = int(destination_row_count.output.strip())
        assert destination_count == visible_count, error(
            f"Expected destination to have {visible_count} rows, got {destination_count}"
        )


@TestFeature
@Name("lightweight delete export partition")
@Requirements(RQ_ClickHouse_ExportPartition_S3("1.0"))
def feature(self, node="clickhouse1"):
    """Test that EXPORT PARTITION works correctly with lightweight deletes."""
    self.context.node = self.context.cluster.node(node)

    with Given("I set up MinIO storage configuration"):
        minio_storage_configuration(restart=True)

    Scenario(run=export_with_lightweight_delete_masks)
    Scenario(run=export_with_multiple_lightweight_deletes)
    Scenario(run=export_after_lightweight_deletes_on_all_partitions)
    Scenario(run=export_with_partial_delete)
