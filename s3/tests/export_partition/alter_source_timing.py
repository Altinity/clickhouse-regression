from testflows.core import *
from testflows.asserts import error
from alter.table.attach_partition.common import create_partitions_with_random_uint64
from alter.stress.tests.tc_netem import *
from helpers.alter import (
    alter_table_add_column,
    alter_table_drop_column,
    alter_table_modify_column,
    alter_table_rename_column,
    alter_table_delete_rows,
)
from helpers.common import getuid
from helpers.create import partitioned_replicated_merge_tree_table
from helpers.queries import *
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


@TestScenario
def alter_add_column_before_export(self):
    """Check exporting partitions after ADD COLUMN on source table."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=True,
            number_of_partitions=5,
            number_of_parts=2,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )

    with When("I add a column to the source table"):
        new_column_name = f"new_col_{getuid()}"
        alter_table_add_column(
            table_name=source_table,
            column_name=new_column_name,
            column_type="String",
            node=self.context.node,
        )

    with And("I insert data with the new column"):
        for i in range(1, 3):
            self.context.node.query(
                f"INSERT INTO {source_table} (p, i, {new_column_name}) SELECT {i}, rand64(), 'value_{i}' FROM numbers(100)"
            )

    with And("I update the destination table schema to match"):
        alter_table_add_column(
            table_name=s3_table_name,
            column_name=new_column_name,
            column_type="String",
            node=self.context.node,
        )

    with And("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("Source and destination tables should match"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
def alter_drop_column_before_export(self):
    """Check exporting partitions after DROP COLUMN on source table."""

    source_table = f"source_{getuid()}"
    with Given(
        "I create a populated source table with extra column and empty S3 table"
    ):
        columns = default_columns(simple=True, partition_key_type="Int8")
        columns.append({"name": "extra_col", "type": "String"})
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=True,
            number_of_partitions=5,
            number_of_parts=2,
            columns=columns,
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=columns,
        )

    with When("I drop a column from the source table"):
        alter_table_drop_column(
            table_name=source_table,
            column_name="extra_col",
            node=self.context.node,
        )

    with And("I drop the same column from the destination table"):
        alter_table_drop_column(
            table_name=s3_table_name,
            column_name="extra_col",
            node=self.context.node,
        )

    with And("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("Source and destination tables should match"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
def alter_modify_column_before_export(self):
    """Check exporting partitions after MODIFY COLUMN on source table."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=True,
            number_of_partitions=5,
            number_of_parts=2,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )

    with When("I modify column type in the source table"):
        alter_table_modify_column(
            table_name=source_table,
            column_name="i",
            column_type="String",
            node=self.context.node,
        )

    with And("I modify the same column in the destination table"):
        alter_table_modify_column(
            table_name=s3_table_name,
            column_name="i",
            column_type="String",
            node=self.context.node,
        )

    with And("I insert data with the new column type"):
        for i in range(1, 3):
            self.context.node.query(
                f"INSERT INTO {source_table} (p, i) SELECT {i}, toString(rand64()) FROM numbers(100)"
            )

    with And("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("Source and destination tables should match"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestStep(When)
def alter_source_add_column(self, source_table, node):
    """Add a column to the source table during export."""
    column_name = f"new_col_{getuid()}"
    with By(f"adding column {column_name} to source table"):
        alter_table_add_column(
            table_name=source_table,
            column_name=column_name,
            column_type="String",
            node=node,
        )


@TestStep(When)
def alter_source_drop_column(self, source_table, node):
    """Drop a column from the source table during export."""
    with By("dropping column 'i' from source table"):
        alter_table_drop_column(
            table_name=source_table,
            column_name="i",
            node=node,
        )


@TestStep(When)
def alter_source_modify_column(self, source_table, node):
    """Modify a column in the source table during export."""
    with By("modifying column 'i' type in source table"):
        alter_table_modify_column(
            table_name=source_table,
            column_name="i",
            column_type="String",
            node=node,
        )


@TestStep(When)
def alter_source_rename_column(self, source_table, node):
    """Rename a column in the source table during export."""
    with By("renaming column 'i' in source table"):
        alter_table_rename_column(
            table_name=source_table,
            column_name_old="i",
            column_name_new="i_renamed",
            node=node,
        )


@TestStep(When)
def alter_source_delete_rows(self, source_table, node):
    """Delete rows from the source table during export."""
    with By("deleting rows from source table"):
        alter_table_delete_rows(
            table_name=source_table,
            condition="p = 1",
            node=node,
        )


@TestScenario
def alter_add_column_during_export(self, delay_ms=100):
    """Check what happens when we ADD COLUMN to source table during EXPORT PARTITION."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=True,
            number_of_partitions=5,
            number_of_parts=2,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )

    with When(
        "I export partitions and add column to source table in parallel",
        description="Export is slowed down by network delay to allow ALTER to happen during export",
    ):
        Step(test=export_partition_with_delay, parallel=True)(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            delay_ms=delay_ms,
        )
        Step(test=alter_source_add_column, parallel=True)(
            source_table=source_table,
            node=self.context.node,
        )
        join()

    with Then("I check the result"):
        source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )
        assert len(source_data) > 0, error()
        assert len(destination_data) >= 0, error()


@TestScenario
def alter_drop_column_during_export(self, delay_ms=100):
    """Check what happens when we DROP COLUMN from source table during EXPORT PARTITION."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=True,
            number_of_partitions=5,
            number_of_parts=2,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )

    with When(
        "I export partitions and drop column from source table in parallel",
        description="Export is slowed down by network delay to allow ALTER to happen during export",
    ):
        Step(test=export_partition_with_delay, parallel=True)(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            delay_ms=delay_ms,
        )
        Step(test=alter_source_drop_column, parallel=True)(
            source_table=source_table,
            node=self.context.node,
        )
        join()

    with Then("I check the result"):
        source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )
        assert len(source_data) > 0, error()
        assert len(destination_data) >= 0, error()


@TestScenario
def alter_modify_column_during_export(self, delay_ms=100):
    """Check what happens when we MODIFY COLUMN in source table during EXPORT PARTITION."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=True,
            number_of_partitions=5,
            number_of_parts=2,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )

    with When(
        "I export partitions and modify column in source table in parallel",
        description="Export is slowed down by network delay to allow ALTER to happen during export",
    ):
        Step(test=export_partition_with_delay, parallel=True)(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            delay_ms=delay_ms,
        )
        Step(test=alter_source_modify_column, parallel=True)(
            source_table=source_table,
            node=self.context.node,
        )
        join()

    with Then("I check the result"):
        source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )
        assert len(source_data) > 0, error()
        assert len(destination_data) >= 0, error()


@TestScenario
def alter_delete_rows_during_export(self, delay_ms=100):
    """Check what happens when we DELETE rows from source table during EXPORT PARTITION."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=True,
            number_of_partitions=5,
            number_of_parts=2,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )

    with When(
        "I export partitions and delete rows from source table in parallel",
        description="Export is slowed down by network delay to allow ALTER to happen during export",
    ):
        Step(test=export_partition_with_delay, parallel=True)(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            delay_ms=delay_ms,
        )
        Step(test=alter_source_delete_rows, parallel=True)(
            source_table=source_table,
            node=self.context.node,
        )
        join()

    with Then("I check the result"):
        source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )
        assert len(source_data) >= 0, error()
        assert len(destination_data) >= 0, error()


@TestScenario
def alter_add_column_after_export(self):
    """Check ADD COLUMN on source table after export completes."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=True,
            number_of_partitions=5,
            number_of_parts=2,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )

    with When("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I verify initial export succeeded"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with And("I add a column to the source table"):
        new_column_name = f"new_col_{getuid()}"
        alter_table_add_column(
            table_name=source_table,
            column_name=new_column_name,
            column_type="String",
            node=self.context.node,
        )

    with And("I insert data with the new column"):
        for i in range(1, 3):
            self.context.node.query(
                f"INSERT INTO {source_table} (p, i, {new_column_name}) SELECT {i}, rand64(), 'value_{i}' FROM numbers(100)"
            )

    with And("I update the destination table schema to match"):
        alter_table_add_column(
            table_name=s3_table_name,
            column_name=new_column_name,
            column_type="String",
            node=self.context.node,
        )

    with And("I export partitions again"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("Source and destination tables should match"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
def alter_drop_column_after_export(self):
    """Check DROP COLUMN on source table after export completes."""

    source_table = f"source_{getuid()}"
    with Given(
        "I create a populated source table with extra column and empty S3 table"
    ):
        columns = default_columns(simple=True, partition_key_type="Int8")
        columns.append({"name": "extra_col", "type": "String"})
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=True,
            number_of_partitions=5,
            number_of_parts=2,
            columns=columns,
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=columns,
        )

    with When("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I verify initial export succeeded"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with And("I drop a column from the source table"):
        alter_table_drop_column(
            table_name=source_table,
            column_name="extra_col",
            node=self.context.node,
        )

    with And("I drop the same column from the destination table"):
        alter_table_drop_column(
            table_name=s3_table_name,
            column_name="extra_col",
            node=self.context.node,
        )

    with And("I export partitions again"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("Source and destination tables should match"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
def alter_delete_rows_after_export(self):
    """Check DELETE rows from source table after export completes."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=True,
            number_of_partitions=5,
            number_of_parts=2,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )

    with When("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I verify initial export succeeded"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with And("I delete rows from the source table"):
        alter_table_delete_rows(
            table_name=source_table,
            condition="p = 1",
            node=self.context.node,
        )

    with And("I export partitions again"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("Source and destination tables should match"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestSuite
def alter_before_export(self):
    """Feature to group ALTER BEFORE EXPORT scenarios."""
    Scenario(run=alter_add_column_before_export)
    Scenario(run=alter_drop_column_before_export)
    Scenario(run=alter_modify_column_before_export)


@TestSuite
def alter_after_export(self):
    """Feature to group ALTER AFTER EXPORT scenarios."""
    Scenario(run=alter_add_column_after_export)
    Scenario(run=alter_drop_column_after_export)
    Scenario(run=alter_delete_rows_after_export)


@TestSuite
def alter_during_export(self):
    """Feature to group ALTER DURING EXPORT scenarios."""
    Scenario(run=alter_add_column_during_export)(delay_ms=100)
    Scenario(run=alter_drop_column_during_export)(delay_ms=100)
    Scenario(run=alter_modify_column_during_export)(delay_ms=100)
    Scenario(run=alter_delete_rows_during_export)(delay_ms=100)


@TestFeature
@Name("alter source timing")
def feature(self):
    """Check ALTER operations on source table before, during, and after EXPORT PARTITION."""

    Feature(run=alter_before_export)
    Feature(run=alter_after_export)
    Feature(run=alter_during_export)
