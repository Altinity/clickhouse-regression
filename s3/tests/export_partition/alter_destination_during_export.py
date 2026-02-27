from testflows.core import *
from testflows.asserts import error
from alter.table.attach_partition.common import create_partitions_with_random_uint64
from alter.stress.tests.tc_netem import *
from helpers.alter import (
    alter_table_add_column,
    alter_table_drop_column,
    alter_table_modify_column,
    alter_table_rename_column,
)
from helpers.common import getuid
from helpers.create import partitioned_replicated_merge_tree_table
from helpers.queries import *
from s3.requirements.export_partition import *
from s3.tests.export_partition.steps import (
    export_partitions,
    create_s3_table,
    default_columns,
    source_matches_destination,
)


@TestStep(When)
def export_partition_with_delay(
    self,
    source_table,
    destination_table,
    node,
    delay_ms=100,
    exitcode=0,
):
    """Export partitions with network delay to slow down the operation."""
    with By("applying network delay to slow down export"):
        network_packet_delay(node=node, delay_ms=delay_ms)

    with And("exporting partitions from source to destination"):
        export_partitions(
            source_table=source_table,
            destination_table=destination_table,
            node=node,
            exitcode=exitcode,
        )


@TestStep(When)
def alter_destination_add_column(self, destination_table, node):
    """Add a column to the destination table during export."""
    column_name = f"new_col_{getuid()}"
    with By(f"adding column {column_name} to destination table"):
        alter_table_add_column(
            table_name=destination_table,
            column_name=column_name,
            column_type="String",
            node=node,
        )


@TestStep(When)
def alter_destination_drop_column(self, destination_table, node):
    """Drop a column from the destination table during export."""
    with By("dropping column 'i' from destination table"):
        alter_table_drop_column(
            table_name=destination_table,
            column_name="i",
            node=node,
        )


@TestStep(When)
def alter_destination_modify_column(self, destination_table, node):
    """Modify a column in the destination table during export."""
    with By("modifying column 'i' type in destination table"):
        alter_table_modify_column(
            table_name=destination_table,
            column_name="i",
            column_type="String",
            node=node,
        )


@TestStep(When)
def alter_destination_rename_column(self, destination_table, node):
    """Rename a column in the destination table during export."""
    with By("renaming column 'i' in destination table"):
        alter_table_rename_column(
            table_name=destination_table,
            column_name_old="i",
            column_name_new="i_renamed",
            node=node,
        )


@TestScenario
def alter_add_column_during_export(self, delay_ms=100):
    """Check what happens when we ADD COLUMN to destination table during EXPORT PARTITION."""

    source_table = f"source_{getuid()}"
    destination_table = None

    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=False,
            number_of_partitions=5,
            number_of_parts=2,
            columns=default_columns(simple=True, partition_key_type="Int8"),
            cluster="replicated_cluster",
        )
        destination_table = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )

    with When(
        "I export partitions and add column to destination table in parallel",
        description="Export is slowed down by network delay to allow ALTER to happen during export",
    ):
        Step(test=export_partition_with_delay, parallel=True)(
            source_table=source_table,
            destination_table=destination_table,
            node=self.context.node,
            delay_ms=delay_ms,
        )
        Step(test=alter_destination_add_column, parallel=True)(
            destination_table=destination_table,
            node=self.context.node,
        )
        join()

    with Then("I check the result"):
        source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        destination_data = select_all_ordered(
            table_name=destination_table, node=self.context.node
        )
        assert len(source_data) > 0, error()
        assert len(destination_data) >= 0, error()


@TestScenario
def alter_drop_column_during_export(self, delay_ms=100):
    """Check what happens when we DROP COLUMN from destination table during EXPORT PARTITION."""

    source_table = f"source_{getuid()}"
    destination_table = None

    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=False,
            number_of_partitions=5,
            number_of_parts=2,
            columns=default_columns(simple=True, partition_key_type="Int8"),
            cluster="replicated_cluster",
        )
        destination_table = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )

    with When(
        "I export partitions and drop column from destination table in parallel",
        description="Export is slowed down by network delay to allow ALTER to happen during export",
    ):
        Step(test=export_partition_with_delay, parallel=True)(
            source_table=source_table,
            destination_table=destination_table,
            node=self.context.node,
            delay_ms=delay_ms,
        )
        Step(test=alter_destination_drop_column, parallel=True)(
            destination_table=destination_table,
            node=self.context.node,
        )
        join()

    with Then("I check the result"):
        source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        destination_data = select_all_ordered(
            table_name=destination_table, node=self.context.node
        )
        assert len(source_data) > 0, error()
        assert len(destination_data) >= 0, error()


@TestScenario
def alter_modify_column_during_export(self, delay_ms=100):
    """Check what happens when we MODIFY COLUMN in destination table during EXPORT PARTITION."""

    source_table = f"source_{getuid()}"
    destination_table = None

    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=False,
            number_of_partitions=5,
            number_of_parts=2,
            columns=default_columns(simple=True, partition_key_type="Int8"),
            cluster="replicated_cluster",
        )
        destination_table = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )

    with When(
        "I export partitions and modify column in destination table in parallel",
        description="Export is slowed down by network delay to allow ALTER to happen during export",
    ):
        Step(test=export_partition_with_delay, parallel=True)(
            source_table=source_table,
            destination_table=destination_table,
            node=self.context.node,
            delay_ms=delay_ms,
        )
        Step(test=alter_destination_modify_column, parallel=True)(
            destination_table=destination_table,
            node=self.context.node,
        )
        join()

    with Then("I check the result"):
        source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        destination_data = select_all_ordered(
            table_name=destination_table, node=self.context.node
        )
        assert len(source_data) > 0, error()
        assert len(destination_data) >= 0, error()


@TestScenario
def alter_rename_column_during_export(self, delay_ms=100):
    """Check what happens when we RENAME COLUMN in destination table during EXPORT PARTITION."""

    source_table = f"source_{getuid()}"
    destination_table = None

    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=False,
            number_of_partitions=5,
            number_of_parts=2,
            columns=default_columns(simple=True, partition_key_type="Int8"),
            cluster="replicated_cluster",
        )
        destination_table = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )

    with When(
        "I export partitions and rename column in destination table in parallel",
        description="Export is slowed down by network delay to allow ALTER to happen during export",
    ):
        Step(test=export_partition_with_delay, parallel=True)(
            source_table=source_table,
            destination_table=destination_table,
            node=self.context.node,
            delay_ms=delay_ms,
        )
        Step(test=alter_destination_rename_column, parallel=True)(
            destination_table=destination_table,
            node=self.context.node,
        )
        join()

    with Then("I check the result"):
        source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        destination_data = select_all_ordered(
            table_name=destination_table, node=self.context.node
        )
        assert len(source_data) > 0, error()
        assert len(destination_data) >= 0, error()


@TestFeature
@Name("alter destination during export")
@Requirements(RQ_ClickHouse_ExportPartition_SchemaChangeIsolation("1.0"))
def feature(self):
    """Check what happens when we perform ALTER operations on destination table during EXPORT PARTITION."""

    Scenario(run=alter_add_column_during_export)(delay_ms=100)
    Scenario(run=alter_drop_column_during_export)(delay_ms=100)
    Scenario(run=alter_modify_column_during_export)(delay_ms=100)
    Scenario(run=alter_rename_column_during_export)(delay_ms=100)
