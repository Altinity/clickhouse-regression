import random

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
from s3.requirements.export_partition import *
from s3.tests.export_partition.steps import (
    export_partitions,
    create_s3_table,
    default_columns,
    source_matches_destination,
    get_partitions,
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
def add_column(self, source_table, destination_table=None, node=None):
    """Add a column to the source table and optionally to the destination table."""
    if node is None:
        node = self.context.node
    partitions = get_partitions(table_name=source_table, node=node)
    for _ in partitions:
        new_column_name = "column_" + getuid()
        with By(f"adding column {new_column_name} to source table"):
            alter_table_add_column(
                table_name=source_table,
                column_name=new_column_name,
                column_type="String",
                node=node,
            )
        if destination_table is not None:
            with And(f"adding column {new_column_name} to destination table"):
                alter_table_add_column(
                    table_name=destination_table,
                    column_name=new_column_name,
                    column_type="String",
                    node=node,
                )


@TestStep(When)
def drop_column(self, source_table, destination_table=None, node=None):
    """Drop a column from the source table and optionally from the destination table."""
    if node is None:
        node = self.context.node
    partitions = get_partitions(table_name=source_table, node=node)
    for _ in partitions:
        with By("dropping column 'extra1' from source table"):
            alter_table_drop_column(
                table_name=source_table,
                column_name="extra1",
                node=node,
            )
        if destination_table is not None:
            with And("dropping column 'extra1' from destination table"):
                alter_table_drop_column(
                    table_name=destination_table,
                    column_name="extra1",
                    node=node,
                )


@TestStep(When)
def modify_column(self, source_table, destination_table=None, node=None):
    """Modify a column in the source table and optionally in the destination table."""
    if node is None:
        node = self.context.node
    partitions = get_partitions(table_name=source_table, node=node)
    for _ in partitions:
        with By("modifying column 'extra' type in source table"):
            alter_table_modify_column(
                table_name=source_table,
                column_name="extra",
                column_type="String",
                node=node,
            )
        if destination_table is not None:
            with And("modifying column 'extra' type in destination table"):
                alter_table_modify_column(
                    table_name=destination_table,
                    column_name="extra",
                    column_type="String",
                    node=node,
                )


@TestStep(When)
def rename_column(self, source_table, destination_table=None, node=None):
    """Rename a column in the source table and optionally in the destination table."""
    if node is None:
        node = self.context.node
    partitions = get_partitions(table_name=source_table, node=node)
    for _ in partitions:
        with By("renaming column 'extra2' in source table"):
            alter_table_rename_column(
                table_name=source_table,
                column_name_old="extra2",
                column_name_new="extra_new",
                node=node,
            )
        if destination_table is not None:
            with And("renaming column 'extra2' in destination table"):
                alter_table_rename_column(
                    table_name=destination_table,
                    column_name_old="extra2",
                    column_name_new="extra_new",
                    node=node,
                )


@TestStep(When)
def delete_rows(self, source_table, destination_table=None, node=None):
    """Delete rows from the source table and optionally from the destination table."""
    if node is None:
        node = self.context.node
    partitions = get_partitions(table_name=source_table, node=node)
    for _ in partitions:
        with By("deleting rows from source table"):
            alter_table_delete_rows(
                table_name=source_table,
                condition="p < 1",
                node=node,
            )
        if destination_table is not None:
            with And("deleting rows from destination table"):
                alter_table_delete_rows(
                    table_name=destination_table,
                    condition="p < 1",
                    node=node,
                )


@TestStep(When)
def comment_column(self, source_table, destination_table=None, node=None):
    """Comment a column in the source table and optionally in the destination table."""
    if node is None:
        node = self.context.node
    partitions = get_partitions(table_name=source_table, node=node)
    for _ in partitions:
        with By("commenting column 'extra' in source table"):
            alter_table_comment_column(
                table_name=source_table,
                column_name="extra",
                comment="test_comment",
                node=node,
            )
        if destination_table is not None:
            with And("commenting column 'extra' in destination table"):
                alter_table_comment_column(
                    table_name=destination_table,
                    column_name="extra",
                    comment="test_comment",
                    node=node,
                )


@TestStep(When)
def add_constraint(self, source_table, destination_table=None, node=None):
    """Add a constraint to the source table and optionally to the destination table."""
    if node is None:
        node = self.context.node
    partitions = get_partitions(table_name=source_table, node=node)
    for _ in partitions:
        constraint_name = "constraint_" + getuid()
        with By(f"adding constraint {constraint_name} to source table"):
            alter_table_add_constraint(
                table_name=source_table,
                constraint_name=constraint_name,
                expression="(i > 1)",
                node=node,
            )
        if destination_table is not None:
            with And(f"adding constraint {constraint_name} to destination table"):
                alter_table_add_constraint(
                    table_name=destination_table,
                    constraint_name=constraint_name,
                    expression="(i > 1)",
                    node=node,
                )


@TestStep(When)
def detach_partition(self, source_table, destination_table=None, node=None):
    """Detach a partition from the source table and optionally from the destination table."""
    if node is None:
        node = self.context.node
    partitions = get_partitions(table_name=source_table, node=node)
    # Use negative partition IDs that are valid Int8 but don't exist in the table
    non_existent_partitions = [str(-1 - i) for i in range(len(partitions))]
    for partition_id in non_existent_partitions:
        with By(f"detaching partition {partition_id} from source table"):
            alter_table_detach_partition(
                table_name=source_table,
                partition_name=partition_id,
                node=node,
            )


@TestStep(When)
def attach_partition(self, source_table, destination_table=None, node=None):
    """Attach a partition to the source table and optionally to the destination table."""
    if node is None:
        node = self.context.node
    partitions = get_partitions(table_name=source_table, node=node)
    for partition_id in partitions:
        with By(f"attempting to attach partition {partition_id} to source table"):
            alter_table_attach_partition(
                table_name=source_table,
                partition_name=partition_id,
                node=node,
                exitcode=None,
            )
        # Note: attach_partition may not be applicable to S3 tables, skipping destination


@TestStep(When)
def move_partition(self, source_table, destination_table=None, node=None):
    """Move a partition to another volume."""
    if node is None:
        node = self.context.node
    partitions = get_partitions(table_name=source_table, node=node)
    for partition_id in partitions:
        with By(f"moving partition {partition_id} to external volume"):
            alter_table_move_partition(
                table_name=source_table,
                partition_name=partition_id,
                disk_name=random.choice(["hot", "cold"]),
                no_checks=True,
                node=node,
            )
        # Note: move_partition may not be applicable to S3 tables, skipping destination


@TestStep(When)
def clear_column(self, source_table, destination_table=None, node=None):
    """Clear a column in a partition of the source table and optionally in the destination table."""
    if node is None:
        node = self.context.node
    partitions = get_partitions(table_name=source_table, node=node)
    for partition_id in partitions:
        with By(f"clearing column 'i' in partition {partition_id} of source table"):
            alter_table_clear_column_in_partition(
                table_name=source_table,
                partition_name=partition_id,
                column_name="i",
                node=node,
            )
        if destination_table is not None:
            with And(
                f"clearing column 'i' in partition {partition_id} of destination table"
            ):
                alter_table_clear_column_in_partition(
                    table_name=destination_table,
                    partition_name=partition_id,
                    column_name="i",
                    node=node,
                )


@TestStep(When)
def freeze_partition(self, source_table, destination_table=None, node=None):
    """Freeze a partition of the source table and optionally of the destination table."""
    if node is None:
        node = self.context.node
    partitions = get_partitions(table_name=source_table, node=node)
    for partition_id in partitions:
        with By(f"freezing partition {partition_id} of source table"):
            alter_table_freeze_partition(
                table_name=source_table,
                partition_name=partition_id,
                node=node,
            )
        # Note: freeze_partition may not be applicable to S3 tables, skipping destination


@TestStep(When)
def freeze_partition_with_name(self, source_table, destination_table=None, node=None):
    """Freeze a partition with a name."""
    if node is None:
        node = self.context.node
    partitions = get_partitions(table_name=source_table, node=node)
    for partition_id in partitions:
        backup_name = f"{partition_id}_{getuid()}"
        with By(f"freezing partition with name {backup_name}"):
            alter_table_freeze_partition_with_name(
                table_name=source_table,
                backup_name=backup_name,
                node=node,
            )
        # Note: freeze_partition_with_name may not be applicable to S3 tables, skipping destination


@TestStep(When)
def unfreeze_partition(self, source_table, destination_table=None, node=None):
    """Unfreeze a partition with a name."""
    if node is None:
        node = self.context.node
    partitions = get_partitions(table_name=source_table, node=node)
    for partition_id in partitions:
        with By(f"attempting to unfreeze partition with name {partition_id}"):
            alter_table_unfreeze_partition_with_name(
                table_name=source_table,
                backup_name=partition_id,
                node=node,
                exitcode=None,
            )
        # Note: unfreeze_partition may not be applicable to S3 tables, skipping destination


@TestStep(When)
def drop_partition(self, source_table, destination_table=None, node=None):
    """Drop a partition from the source table and optionally from the destination table."""
    if node is None:
        node = self.context.node
    partitions = get_partitions(table_name=source_table, node=node)
    # Use negative partition IDs that are valid Int8 but don't exist in the table
    non_existent_partitions = [str(-1 - i) for i in range(len(partitions))]
    for partition_id in non_existent_partitions:
        with By(f"dropping partition {partition_id} from source table"):
            alter_table_drop_partition(
                table_name=source_table,
                partition_name=partition_id,
                node=node,
            )
        # Note: drop_partition may not be applicable to S3 tables, skipping destination


@TestStep(When)
def clear_index(self, source_table, destination_table=None, node=None):
    """Clear an index in a partition of the source table and optionally in the destination table."""
    if node is None:
        node = self.context.node
    partitions = get_partitions(table_name=source_table, node=node)
    for partition_id in partitions:
        with By(f"clearing index in partition {partition_id} of source table"):
            alter_table_clear_index_in_partition(
                table_name=source_table,
                partition_name=partition_id,
                index="index_name",
                node=node,
            )
        # Note: clear_index may not be applicable to S3 tables, skipping destination


def get_initial_columns(action):
    """Get initial columns for table creation based on the action."""
    columns = default_columns(simple=True, partition_key_type="Int8")
    columns.append({"name": "extra", "type": "UInt8"})
    columns.append({"name": "extra1", "type": "UInt8"})
    columns.append({"name": "extra2", "type": "UInt8"})
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
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=columns,
        )

    with When("I perform an alter action on both source and destination tables"):
        action(
            source_table=source_table,
            destination_table=s3_table_name,
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
            cluster="replicated_cluster",
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

    with Then("I perform an alter action"):
        action(
            source_table=source_table,
            node=self.context.node,
        )


@TestOutline
def during_export(self, action, delay_ms=0.05):
    """Check what happens when we perform an alter action on source table during EXPORT PARTITION."""
    source_table = f"source_{getuid()}"

    with Given(
        "I create a populated source table and empty S3 table",
        description=f"action: {action.__name__}, delay_ms: {delay_ms}, source_table: {source_table}",
    ):
        columns = get_initial_columns(action)

        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=False,
            number_of_partitions=5,
            number_of_parts=2,
            columns=columns,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=columns,
        )

    with When(
        "I export partitions and perform alter action on source and destination tables in parallel",
    ):
        with By("starting export partitions in background"):
            with Pool(2) as pool:
                Check(test=export_partitions, parallel=True, executor=pool)(
                    source_table=source_table,
                    destination_table=s3_table_name,
                    node=self.context.node,
                )

                Check(test=action, parallel=True, executor=pool)(
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
@Requirements(RQ_ClickHouse_ExportPartition_SchemaChangeIsolation("1.0"))
def feature(self):
    """Check ALTER operations on source table before, during, and after EXPORT PARTITION."""
    Scenario(run=alter_before_export)
    Scenario(run=alter_after_export)
    Scenario(run=alter_during_export)
