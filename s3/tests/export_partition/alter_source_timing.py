from testflows.core import *
from testflows.asserts import error
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
def action_add_column(self, source_table, node):
    """Add a column to the source table."""
    new_column_name = f"new_col_{getuid()}"
    with By(f"adding column {new_column_name} to source table"):
        alter_table_add_column(
            table_name=source_table,
            column_name=new_column_name,
            column_type="String",
            node=node,
        )
    return new_column_name


@TestStep(When)
def action_drop_column(self, source_table, node):
    """Drop a column from the source table."""
    with By("dropping column 'extra_col' from source table"):
        alter_table_drop_column(
            table_name=source_table,
            column_name="extra_col",
            node=node,
        )


@TestStep(When)
def action_modify_column(self, source_table, node):
    """Modify a column in the source table."""
    with By("modifying column 'i' type in source table"):
        alter_table_modify_column(
            table_name=source_table,
            column_name="i",
            column_type="String",
            node=node,
        )


@TestStep(When)
def action_rename_column(self, source_table, node):
    """Rename a column in the source table."""
    with By("renaming column 'i' in source table"):
        alter_table_rename_column(
            table_name=source_table,
            column_name_old="i",
            column_name_new="i_renamed",
            node=node,
        )


@TestStep(When)
def action_delete_rows(self, source_table, node):
    """Delete rows from the source table."""
    with By("deleting rows from source table"):
        alter_table_delete_rows(
            table_name=source_table,
            condition="p = 1",
            node=node,
        )


@TestOutline
def before_export(self, action):
    """Check exporting partitions after an alter action."""
    source_table = f"source_{getuid()}"

    with Given("I create a populated source table and empty S3 table"):
        columns = default_columns(simple=True, partition_key_type="Int8")

        if action == action_drop_column:
            columns.append({"name": "extra_col", "type": "String"})

        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=False,
            number_of_partitions=5,
            number_of_parts=2,
            columns=columns,
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=columns,
        )

    with When("I perform an alter action on the source table"):
        result = action(source_table=source_table, node=self.context.node)

        if action == action_add_column:
            new_column_name = result
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
        elif action == action_drop_column:
            with And("I drop the same column from the destination table"):
                alter_table_drop_column(
                    table_name=s3_table_name,
                    column_name="extra_col",
                    node=self.context.node,
                )
        elif action == action_modify_column:
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
        columns = default_columns(simple=True, partition_key_type="Int8")

        if action == action_drop_column:
            columns.append({"name": "extra_col", "type": "String"})

        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=False,
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

    with And("I perform an alter action on the source table"):
        result = action(source_table=source_table, node=self.context.node)

        if action == action_add_column:
            new_column_name = result
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
        elif action == action_drop_column:
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


@TestOutline
def during_export(self, actions, delay_ms=10000):
    """Check what happens when we perform an alter action on source table during EXPORT PARTITION."""
    source_table = f"source_{getuid()}"

    with Given("I create a populated source table and empty S3 table"):
        columns = default_columns(simple=True, partition_key_type="Int8")

        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=False,
            number_of_partitions=5,
            number_of_parts=2,
            columns=columns,
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
            for action in actions:
                action(source_table=source_table, node=self.context.node)

    with Then("Remove the delay"):
        network_packet_delay(node=self.context.node, delay_ms=0)

    with Then("I check the result"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
def alter_before_export_scenarios(self):
    """Check exporting partitions after alter actions on source table."""
    actions = [
        action_add_column,
        action_drop_column,
        action_modify_column,
    ]

    for action in actions:
        Scenario(
            name=f"{action.__name__}".replace("_", " "),
            test=before_export,
        )(action=action)


@TestScenario
def alter_after_export_scenarios(self):
    """Check alter actions on source table after export completes."""
    actions = [
        action_add_column,
        action_drop_column,
        action_delete_rows,
    ]

    for action in actions:
        Scenario(
            name=f"{action.__name__}".replace("_", " "),
            test=after_export,
        )(action=action)


@TestScenario
def alter_during_export_scenarios(self):
    """Check what happens when we perform alter actions on source table during EXPORT PARTITION."""
    actions = [
        action_add_column,
        action_drop_column,
        action_modify_column,
        action_delete_rows,
    ]

    Scenario(
        name="alter during export",
        test=during_export,
    )(action=actions)


@TestFeature
@Name("alter source timing")
def feature(self):
    """Check ALTER operations on source table before, during, and after EXPORT PARTITION."""

    Scenario(run=alter_before_export_scenarios)
    Scenario(run=alter_after_export_scenarios)
    Scenario(run=alter_during_export_scenarios)
