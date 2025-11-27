import time

from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from helpers.create import *
from helpers.queries import *
from alter.table.attach_partition.common import create_partitions_with_random_uint64
from s3.tests.export_partition.steps import (
    export_partitions,
    create_s3_table,
    default_columns,
    source_matches_destination,
    wait_for_export_to_complete,
)
from s3.requirements.export_partition import *


@TestStep(When)
def run_single_select(self, table_name, node=None):
    """Run a single SELECT query on a table."""
    if node is None:
        node = self.context.node

    with By(f"running SELECT query on {table_name}"):
        node.query(
            f"SELECT * FROM {table_name} ORDER BY p, i",
            exitcode=0,
            steps=True,
        )


@TestStep(When)
def run_parallel_selects(self, table_name, num_selects=5, node=None):
    """Run multiple SELECT queries in parallel on a table."""
    if node is None:
        node = self.context.node

    with By(f"running {num_selects} parallel SELECT queries"):
        for i in range(num_selects):
            Check(test=run_single_select, parallel=True)(
                table_name=table_name,
                node=node,
            )
        join()


@TestStep(When)
def run_optimize_table(self, table_name, node=None):
    """Run OPTIMIZE TABLE on a table."""
    if node is None:
        node = self.context.node

    with By(f"running OPTIMIZE TABLE on {table_name}"):
        node.query(f"OPTIMIZE TABLE {table_name} FINAL", exitcode=0, steps=True)


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Concurrency_ParallelInserts("1.0"))
def parallel_inserts_with_merge_stop(self):
    """Check that exports work correctly with parallel inserts when merges are stopped."""

    source_table = f"source_{getuid()}"
    with Given(
        "I create an empty source table with merges stopped and an empty S3 table"
    ):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            number_of_partitions=10,
            number_of_parts=5,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When(
        "I insert data in parallel and export partitions in parallel with merges stopped",
        description="""
        Multiple partitions are inserted in parallel while export partition
        is running.""",
    ):
        Check(test=export_partitions, parallel=True)(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )
        time.sleep(0.01)
        Check(test=create_partitions_with_random_uint64, parallel=True)(
            table_name=source_table,
            number_of_partitions=10,
            number_of_parts=2,
            number_of_values=100,
        )

        join()

    with Then("I wait for export to complete"):
        wait_for_export_to_complete(source_table=source_table)

    with And("Source and destination tables should match"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with And("Source table should have all inserted data"):
        source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        assert len(source_data) > 0, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Concurrency_ParallelInserts("1.0"))
def parallel_inserts_with_merge_enabled(self):
    """Check that exports work correctly with parallel inserts when merges are enabled."""

    source_table = f"source_{getuid()}"
    with Given(
        "I create an empty source table with merges enabled and an empty S3 table"
    ):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
            number_of_partitions=10,
            number_of_parts=5,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When(
        "I insert data in parallel and export partitions in parallel with merges enabled",
        description="""
        Multiple partitions are inserted in parallel while export partition
        is running. Since merges are enabled, parts may be merged during export.
    """,
    ):
        Check(test=export_partitions, parallel=True)(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )
        time.sleep(0.01)

        Check(test=create_partitions_with_random_uint64, parallel=True)(
            table_name=source_table,
            number_of_partitions=10,
            number_of_parts=2,
            number_of_values=100,
        )

        join()

    with Then("I wait for export to complete"):
        wait_for_export_to_complete(source_table=source_table)

    with And("Destination data should be a subset of source data"):
        source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )
        assert set(source_data) >= set(destination_data), error()

    with And("Source table should have all inserted data"):
        assert len(source_data) > 0, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Concurrency_OptimizeTable("1.0"))
def export_with_optimize_table_parallel(self):
    """Check that exports work correctly when OPTIMIZE TABLE runs in parallel."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and an empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When(
        "I export partitions and run OPTIMIZE TABLE in parallel",
        description="""
        Export partition runs while OPTIMIZE TABLE is executing in parallel.
        This tests that export can handle concurrent merge operations.
    """,
    ):
        Check(test=export_partitions, parallel=True)(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )
        Check(test=run_optimize_table, parallel=True)(
            table_name=source_table,
            node=self.context.node,
        )
        join()

    with Then("I wait for export to complete"):
        wait_for_export_to_complete(source_table=source_table)

    with And("Source and destination tables should match"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Concurrency_ParallelSelects("1.0"))
def parallel_selects_during_export(self):
    """Check that parallel SELECT queries work correctly while export partition is happening."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and an empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When(
        "I export partitions and run parallel SELECT queries",
        description="""
        Multiple SELECT queries run in parallel while export partition is executing.
        This tests that reads can happen concurrently with export operations.
    """,
    ):
        Check(test=export_partitions, parallel=True)(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )
        Check(test=run_parallel_selects, parallel=True)(
            table_name=source_table,
            num_selects=10,
            node=self.context.node,
        )
        join()

    with Then("I wait for export to complete"):
        wait_for_export_to_complete(source_table=source_table)

    with And("Source and destination tables should match"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with And("Source table data should still be accessible"):
        source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        assert len(source_data) > 0, error()


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_Concurrency_ParallelInserts("1.0"),
    RQ_ClickHouse_ExportPartition_Concurrency_OptimizeTable("1.0"),
)
def parallel_inserts_export_and_optimize(self):
    """Check that exports work correctly with parallel inserts, export partition, and OPTIMIZE TABLE all running concurrently with merges enabled."""

    source_table = f"source_{getuid()}"
    with Given(
        "I create a populated source table with merges enabled and an empty S3 table"
    ):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When(
        "I insert data in parallel, export partitions, and run OPTIMIZE TABLE all concurrently",
        description="""
        Multiple operations run in parallel:
        - INSERT operations adding new partitions
        - EXPORT PARTITION exporting existing partitions
        - OPTIMIZE TABLE merging parts
        All with merges enabled, testing complex concurrent scenarios.
    """,
    ):
        Check(test=export_partitions, parallel=True)(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )
        Check(test=create_partitions_with_random_uint64, parallel=True)(
            table_name=source_table,
            number_of_partitions=10,
            number_of_parts=2,
            number_of_values=100,
        )
        Check(test=run_optimize_table, parallel=True)(
            table_name=source_table,
            node=self.context.node,
        )
        join()

    with Then("I wait for export to complete"):
        wait_for_export_to_complete(source_table=source_table)

    with And("Source and destination tables should match"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with And("Source table should have all inserted data"):
        source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        assert len(source_data) > 0, error()


@TestFeature
@Requirements(
    RQ_ClickHouse_ExportPartition_Concurrency_ParallelInserts("1.0"),
    RQ_ClickHouse_ExportPartition_Concurrency_OptimizeTable("1.0"),
    RQ_ClickHouse_ExportPartition_Concurrency_ParallelSelects("1.0"),
)
@Name("parallel inserts and selects")
def feature(self):
    """Test export partition with various parallel operations including inserts, OPTIMIZE TABLE, and SELECT queries."""

    Scenario(run=parallel_inserts_with_merge_stop)
    Scenario(run=parallel_inserts_with_merge_enabled)
    Scenario(run=export_with_optimize_table_parallel)
    Scenario(run=parallel_selects_during_export)
    Scenario(run=parallel_inserts_export_and_optimize)
