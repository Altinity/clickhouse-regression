from duckdb.duckdb import description
from testflows.core import *
from testflows.asserts import error
from alter.stress.tests.tc_netem import *
from helpers.alter import (
    alter_table_add_column,
    alter_table_drop_column,
    alter_table_modify_column,
    alter_table_rename_column,
    alter_table_delete_rows,
    alter_table_comment_column,
    alter_table_add_constraint,
    alter_table_detach_partition,
    alter_table_attach_partition,
    alter_table_move_partition,
    alter_table_clear_column,
    alter_table_clear_column_in_partition,
    alter_table_freeze_partition,
    alter_table_freeze_partition_with_name,
    alter_table_unfreeze_partition_with_name,
    alter_table_drop_partition,
    alter_table_clear_index_in_partition,
)
from helpers.common import getuid
from helpers.create import partitioned_replicated_merge_tree_table
from helpers.queries import *
from oauth.tests.steps.clikhouse import check_clickhouse_is_alive
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
def add_column(self, source_table, destination_table, node):
    """Add a column to the source table and update destination table schema."""
    new_column_name = f"new_col_{getuid()}"
    with By(f"adding column {new_column_name} to source table"):
        alter_table_add_column(
            table_name=source_table,
            column_name=new_column_name,
            column_type="String",
            node=node,
        )
    with And("I insert data with the new column"):
        for i in range(1, 3):
            node.query(
                f"INSERT INTO {source_table} (p, i, {new_column_name}) SELECT {i}, rand64(), 'value_{i}' FROM numbers(100)"
            )
    with And("I update the destination table schema to match"):
        alter_table_add_column(
            table_name=destination_table,
            column_name=new_column_name,
            column_type="String",
            node=node,
        )


@TestStep(When)
def drop_column(self, source_table, destination_table, node):
    """Drop a column from the source table and update destination table schema."""
    with By("dropping column 'extra_col' from source table"):
        alter_table_drop_column(
            table_name=source_table,
            column_name="extra_col",
            node=node,
        )
    with And("I drop the same column from the destination table"):
        alter_table_drop_column(
            table_name=destination_table,
            column_name="extra_col",
            node=node,
        )


@TestStep(When)
def modify_column(self, source_table, destination_table, node):
    """Modify a column in the source table and update destination table schema."""
    with By("modifying column 'i' type in source table"):
        alter_table_modify_column(
            table_name=source_table,
            column_name="i",
            column_type="String",
            node=node,
        )
    with And("I modify the same column in the destination table"):
        alter_table_modify_column(
            table_name=destination_table,
            column_name="i",
            column_type="String",
            node=node,
        )
    with And("I insert data with the new column type"):
        for i in range(1, 3):
            node.query(
                f"INSERT INTO {source_table} (p, i) SELECT {i}, toString(rand64()) FROM numbers(100)"
            )


@TestStep(When)
def rename_column(self, source_table, destination_table, node):
    """Rename a column in the source table."""
    with By("renaming column 'i' in source table"):
        alter_table_rename_column(
            table_name=source_table,
            column_name_old="i",
            column_name_new="i_renamed",
            node=node,
        )


@TestStep(When)
def delete_rows(self, source_table, destination_table, node):
    """Delete rows from the source table."""
    with By("deleting rows from source table"):
        alter_table_delete_rows(
            table_name=source_table,
            condition="p = 1",
            node=node,
        )


@TestStep(When)
def comment_column(self, source_table, destination_table, node):
    """Comment a column in the source table."""
    with By("commenting column 'i' in source table"):
        alter_table_comment_column(
            table_name=source_table,
            column_name="i",
            comment="test_comment",
            node=node,
        )


@TestStep(When)
def add_constraint(self, source_table, destination_table, node):
    """Add a constraint to the source table."""
    constraint_name = f"constraint_{getuid()}"
    with By(f"adding constraint {constraint_name} to source table"):
        alter_table_add_constraint(
            table_name=source_table,
            constraint_name=constraint_name,
            expression="(i > 1)",
            node=node,
        )


@TestStep(When)
def detach_partition(self, source_table, destination_table, node):
    """Detach a partition from the source table."""
    partition_name = 1
    with By(f"detaching partition {partition_name} from source table"):
        alter_table_detach_partition(
            table_name=source_table,
            partition_name=partition_name,
            node=node,
        )


@TestStep(When)
def attach_partition(self, source_table, destination_table, node):
    """Attach a partition to the source table."""
    partition_name = 1
    with By(f"attaching partition {partition_name} to source table"):
        alter_table_attach_partition(
            table_name=source_table,
            partition_name=partition_name,
            node=node,
        )


@TestStep(When)
def move_partition(self, source_table, destination_table, node):
    """Move a partition to another volume."""
    partition_name = 1
    with By(f"moving partition {partition_name} to external volume"):
        alter_table_move_partition(
            table_name=source_table,
            partition_name=partition_name,
            disk_name="external",
            node=node,
        )


@TestStep(When)
def clear_column(self, source_table, destination_table, node):
    """Clear a column in a partition of the source table."""
    partition_name = 1
    with By(f"clearing column 'i' in partition {partition_name} of source table"):
        alter_table_clear_column_in_partition(
            table_name=source_table,
            partition_name=partition_name,
            column_name="i",
            node=node,
        )


@TestStep(When)
def freeze_partition(self, source_table, destination_table, node):
    """Freeze a partition of the source table."""
    partition_name = 1
    with By(f"freezing partition {partition_name} of source table"):
        alter_table_freeze_partition(
            table_name=source_table,
            partition_name=partition_name,
            node=node,
        )


@TestStep(When)
def freeze_partition_with_name(self, source_table, destination_table, node):
    """Freeze a partition with a name."""
    backup_name = f"backup_{getuid()}"
    with By(f"freezing partition with name {backup_name}"):
        alter_table_freeze_partition_with_name(
            table_name=source_table,
            backup_name=backup_name,
            node=node,
        )


@TestStep(When)
def unfreeze_partition(self, source_table, destination_table, node):
    """Unfreeze a partition with a name."""
    backup_name = f"backup_{getuid()}"
    with By(f"unfreezing partition with name {backup_name}"):
        alter_table_unfreeze_partition_with_name(
            table_name=source_table,
            backup_name=backup_name,
            node=node,
        )


@TestStep(When)
def drop_partition(self, source_table, destination_table, node):
    """Drop a partition from the source table."""
    partition_name = 1
    with By(f"dropping partition {partition_name} from source table"):
        alter_table_drop_partition(
            table_name=source_table,
            partition_name=partition_name,
            node=node,
        )


@TestStep(When)
def clear_index(self, source_table, destination_table, node):
    """Clear an index in a partition of the source table."""
    partition_name = 1
    with By(f"clearing index in partition {partition_name} of source table"):
        alter_table_clear_index_in_partition(
            table_name=source_table,
            partition_name=partition_name,
            index="index_name",
            node=node,
        )


def get_initial_columns(action):
    """Get initial columns for table creation based on the action."""
    columns = default_columns(simple=True, partition_key_type="Int8")
    if action == drop_column:
        columns.append({"name": "extra_col", "type": "String"})
    return columns


@TestOutline
def before_export(self, action):
    """Check exporting partitions after an alter action."""
    source_table = f"source_{getuid()}"

    with Given("I create a populated source table and empty S3 table"):
        columns = get_initial_columns(action)

        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=False,
            number_of_partitions=5,
            number_of_parts=2,
            columns=columns,
            cluster="replicated_cluster"
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=columns,
        )

    with When("I perform an alter action"):
        action(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I check that clickhouse is alive"):
        check_clickhouse_is_alive()

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


@TestOutline
def after_export(self, action):
    """Check alter action on source table after export completes."""
    source_table = f"source_{getuid()}"

    with Given("I create a populated source table and empty S3 table"):
        columns = get_initial_columns(action)

        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=False,
            number_of_partitions=5,
            number_of_parts=2,
            columns=columns,
            cluster="replicated_cluster"
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

    with And("I perform an alter action"):
        action(
            source_table=source_table,
            destination_table=s3_table_name,
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


@TestOutline
def during_export(self, action, delay_ms=100000):
    """Check what happens when we perform an alter action on source table during EXPORT PARTITION."""
    source_table = f"source_{getuid()}"

    with Given(
        "I create a populated source table and empty S3 table",
        description=f"action: {action.__name__}, delay_ms: {delay_ms}, source_table: {source_table}",
    ):
        columns = default_columns(simple=True, partition_key_type="Int8")

        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=False,
            number_of_partitions=5,
            number_of_parts=2,
            columns=columns,
            cluster="replicated_cluster"
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=columns,
        )

    with When(
        "I export partitions and perform alter action on source table in parallel",
        description="Export is slowed down by network delay to allow ALTER to happen during export",
    ):
        with By("applying network delay to slow down export"):
            network_packet_delay(node=self.context.node, delay_ms=delay_ms)

        with And("starting export partitions in background"):
            export_partitions(
                source_table=source_table,
                destination_table=s3_table_name,
                node=self.context.node,
            )

        with And("performing alter action while export runs in background"):
            action(
                source_table=source_table,
                destination_table=s3_table_name,
                node=self.context.node,
            )

    with Then("Remove the delay"):
        self.context.node.command(f"tc qdisc del dev eth0 root netem", exitcode=0)

    with Then("I check the result"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
def alter_before_export(self):
    """Check exporting partitions after alter actions on source table."""
    actions = [
        add_column,
        drop_column,
        modify_column,
        rename_column,
        comment_column,
        add_constraint,
        detach_partition,
        attach_partition,
        move_partition,
        clear_column,
        freeze_partition,
        freeze_partition_with_name,
        drop_partition,
        clear_index,
    ]

    for action in actions:
        Scenario(
            name=f"{action.__name__}".replace("_", " "),
            test=before_export,
        )(action=action)


@TestScenario
def alter_after_export(self):
    """Check alter actions on source table after export completes."""
    actions = [
        add_column,
        drop_column,
        delete_rows,
        rename_column,
        comment_column,
        add_constraint,
        detach_partition,
        attach_partition,
        move_partition,
        clear_column,
        freeze_partition,
        freeze_partition_with_name,
        unfreeze_partition,
        drop_partition,
        clear_index,
    ]

    for action in actions:
        Scenario(
            name=f"{action.__name__}".replace("_", " "),
            test=after_export,
        )(action=action)


@TestScenario
def alter_during_export(self):
    """Check what happens when we perform alter actions on source table during EXPORT PARTITION."""
    actions = [
        add_column,
        drop_column,
        modify_column,
        delete_rows,
        rename_column,
        comment_column,
        add_constraint,
        detach_partition,
        attach_partition,
        move_partition,
        clear_column,
        freeze_partition,
        freeze_partition_with_name,
        unfreeze_partition,
        drop_partition,
        clear_index,
    ]
    for action in actions:
        Scenario(
            name=f"{action.__name__}".replace("_", " "),
            test=during_export,
        )(action=action)


@TestFeature
@Name("alter source timing")
def feature(self):
    """Check ALTER operations on source table before, during, and after EXPORT PARTITION."""

    Scenario(run=alter_before_export)
    Scenario(run=alter_after_export)
    Scenario(run=alter_during_export)
