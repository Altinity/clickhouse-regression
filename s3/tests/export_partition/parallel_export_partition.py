from testflows.core import *
from testflows.asserts import error

from helpers.datasets.nyc_taxi import nyc_taxi, nyc_columns
from s3.tests.export_partition.steps import *
from helpers.common import getuid
from helpers.create import *
from s3.requirements.export_partition import *


def divide_partitions(partitions, num_export_operations):
    """Divide partitions among different export operations.

    Args:
        partitions: List of partition IDs
        num_export_operations: Number of parallel export operations

    Returns:
        List of lists, where each inner list contains partitions for one export operation
    """
    if num_export_operations <= 0:
        return []

    # Calculate partitions per operation
    partitions_per_op = len(partitions) // num_export_operations
    remainder = len(partitions) % num_export_operations

    divided = []
    start_idx = 0

    for i in range(num_export_operations):
        num_for_this_op = partitions_per_op + (1 if i < remainder else 0)
        end_idx = start_idx + num_for_this_op
        divided.append(partitions[start_idx:end_idx])
        start_idx = end_idx

    return divided


@TestStep(When)
def export_partition_subset(
    self,
    source_table,
    destination_table,
    partitions,
    node=None,
    exitcode=0,
):
    """Export a subset of partitions from source table to destination table.

    Args:
        source_table: Source table name
        destination_table: Destination table name
        partitions: List of partition IDs to export
        node: ClickHouse node to execute on
        exitcode: Expected exit code
    """
    if node is None:
        node = self.context.node

    if not partitions:
        note("No partitions to export for this operation")
        return

    with By(f"exporting {len(partitions)} partitions: {partitions}"):
        export_partitions(
            source_table=source_table,
            destination_table=destination_table,
            node=node,
            partitions=partitions,
            exitcode=exitcode,
        )


@TestStep(Given)
def create_nyc_taxi_source_and_destination_tables(
    self,
    from_range=0,
    to_range=2,
):
    """Create source and destination tables for NYC Taxi dataset export partition tests"""
    source_table = f"source_{getuid()}"

    with Given("I create source and destination tables"):
        nyc_taxi(
            table_name=source_table,
            from_range=from_range,
            to_range=to_range,
            node=self.context.node,
        )

        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            partition_by="pickup_datetime",
            columns=nyc_columns(),
        )

        return source_table, s3_table_name

@TestStep(Given)
def create_source_and_destination_tables(
    self, number_of_partitions=None, number_of_parts=None
):
    """Create source and destination tables for export partition tests"""

    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    if number_of_parts is None:
        number_of_parts = self.context.number_of_parts

    source_table = f"source_{getuid()}"

    with Given("I create source and destination tables"):
        columns = [
            {"name": "p", "type": "UInt16"},
            {"name": "i", "type": "UInt64"},
            {"name": "extra", "type": "UInt8"},
        ]

        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=columns,
            stop_merges=False,
            number_of_partitions=number_of_partitions,
            number_of_parts=number_of_parts,
            query_settings=f"storage_policy = 'tiered_storage'",
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(
            table_name="s3", create_new_bucket=True, columns=columns
        )

        return source_table, s3_table_name


@TestOutline
def parallel_export_partitions(
    self,
    source_and_destination,
    number_of_parallel_exports=None,
):
    """Test running multiple EXPORT PARTITION operations in parallel with non-overlapping partitions.

    Args:
        number_of_parallel_exports: Number of parallel EXPORT PARTITION operations to run
    """

    if number_of_parallel_exports is None:
        number_of_parallel_exports = self.context.number_of_parallel_exports

    source_table = f"source_{getuid()}"

    with Given("I create source and destination tables"):
        source_table, s3_table_name = source_and_destination()

    with And("I get all partitions from the source table"):
        all_partitions = get_partitions(table_name=source_table, node=self.context.node)

    with And("I divide partitions between export operations"):
        partition_groups = divide_partitions(
            partitions=all_partitions,
            num_export_operations=number_of_parallel_exports,
        )

        all_exported_partitions = []
        for group in partition_groups:
            all_exported_partitions.extend(group)

    with When(
        f"I run {number_of_parallel_exports} EXPORT PARTITION operations in parallel"
    ):
        with Pool(number_of_parallel_exports) as pool:
            for i, partition_group in enumerate(partition_groups):
                Check(
                    name=f"export_operation_{i+1}",
                    test=export_partition_subset,
                    parallel=True,
                    executor=pool,
                )(
                    source_table=source_table,
                    destination_table=s3_table_name,
                    partitions=partition_group,
                    node=self.context.node,
                )
            join()

    with Then("Source and destination tables should match"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
def generated_dataset(self):
    """Test parallel EXPORT PARTITION with dataset that we generate on the fly."""
    parallel_export_partitions(source_and_destination=create_source_and_destination_tables)

@TestScenario
def nyc_taxi_dataset(self):
    """Test parallel EXPORT PARTITION with NYC Taxi dataset."""
    parallel_export_partitions(
        source_and_destination=create_nyc_taxi_source_and_destination_tables
    )

@TestFeature
@Requirements(RQ_ClickHouse_ExportPartition_Concurrency("1.0"))
@Name("parallel export partition")
def feature(
    self,
    node="clickhouse1",
    number_of_partitions=30,
    number_of_parts=30,
    number_of_parallel_exports=3,
):
    """
    Test running multiple EXPORT PARTITION operations in parallel.
    Partitions are divided among export operations to ensure no partition
    is exported by multiple operations simultaneously.
    """
    self.context.node = self.context.cluster.node(node)
    self.context.number_of_partitions = number_of_partitions
    self.context.number_of_parts = number_of_parts
    self.context.number_of_parallel_exports = number_of_parallel_exports

    with Given("I set up MinIO storage configuration"):
        minio_storage_configuration(restart=True)

    Scenario(run=generated_dataset)
