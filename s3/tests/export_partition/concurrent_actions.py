import random

from testflows.core import *
from testflows.asserts import error
from s3.tests.export_partition.steps import *
from helpers.common import getuid
from helpers.create import *
from helpers.queries import *
from helpers.alter import *
from s3.requirements.export_partition import *

source_table = "source_" + getuid()
destination_table = "destination_" + getuid()


def get_n_random_items(lst, n):
    """Get n random elements from the list."""
    if n >= len(lst):
        return lst
    else:
        return random.sample(lst, n)


@TestStep(When)
def export_partition_by_id(
    self,
    source_table,
    destination_table,
    partition_id,
    node=None,
    exitcode=0,
    settings=None,
):
    """Export partition by ID from source table to destination table."""
    if node is None:
        node = self.context.node

    if settings is None:
        settings = self.context.default_settings

    with By(
        f"exporting partition {partition_id} from {source_table} to {destination_table}"
    ):
        query = f"ALTER TABLE {source_table} EXPORT PARTITION ID '{partition_id}' TO TABLE {destination_table}"
        node.query(
            query,
            exitcode=exitcode,
            settings=settings,
            inline_settings=settings,
        )


@TestStep(Then)
def export_partition_and_validate_data(
    self,
    partition_to_export,
    source_table=None,
    destination_table=None,
    delay_before=None,
    delay_after=None,
    validate=None,
    exitcode=None,
    message=None,
    node=None,
):
    """
    Export partition and validate that the data on the destination table matches the source table.
    Also check that the data on the source table was not lost during export.

    Args:
        partition_to_export (str): The partition identifier that needs to be exported.
        source_table (str, optional): The name of the source table from which to export the partition.
        Defaults to None, in which case the table name is taken from the test context.
        destination_table (str, optional): The name of the destination table where the partition is to be exported.
        Defaults to None, in which case the table name is taken from the test context.
        delay_before (float, optional): The delay in seconds to wait before performing the partition export.
        Defaults to None, which causes a random delay.
        delay_after (float, optional): The delay in seconds to wait after performing the partition export.
        Defaults to None, which causes a random delay.
        validate (bool, optional): A flag determining whether to perform validation checks after the partition export.
        Defaults to True.
    """
    from time import sleep

    if node is None:
        node = self.context.node

    if validate is None:
        validate = True
    else:
        validate = self.context.validate

    if source_table is None:
        source_table = self.context.source_table

    if destination_table is None:
        destination_table = self.context.destination_table

    if delay_before is None:
        delay_before = random.random()

    if delay_after is None:
        delay_after = random.random()

    with By("saving the data from the source table before exporting partition"):
        source_data_before = node.query(
            f"SELECT i FROM {source_table} WHERE p = {partition_to_export} ORDER BY tuple(*) FORMAT TabSeparated"
        )

    with And("exporting partition from the source table to the destination table"):
        sleep(delay_before)

        export_partition_by_id(
            source_table=source_table,
            destination_table=destination_table,
            partition_id=partition_to_export,
            node=node,
            exitcode=exitcode,
        )

        sleep(delay_after)

    if validate:
        with Then("checking that the partition was exported correctly"):
            for retry in retries(timeout=600, delay=30):
                with retry:
                    source_data = node.query(
                        f"SELECT i FROM {source_table} WHERE p = {partition_to_export} ORDER BY tuple(*) FORMAT TabSeparated"
                    )
                    destination_data = node.query(
                        f"SELECT i FROM {destination_table} WHERE p = {partition_to_export} ORDER BY tuple(*) FORMAT TabSeparated"
                    )

                    assert (
                        source_data.output.strip() == destination_data.output.strip()
                    ), error()

                    assert (
                        source_data_before.output.strip() == source_data.output.strip()
                    ), error()


@TestStep(When)
def add_column(self, table_name):
    """Add column to the table."""
    alter_table_add_column(
        table_name=table_name,
        column_name="column_" + getuid(),
        column_type="String",
    )


@TestStep(When)
def add_column_to_source_table(self):
    """Alter add column to the source table."""
    add_column(table_name=source_table)


@TestStep(When)
def add_column_to_destination_table(self):
    """Alter add column to the destination table."""
    add_column(table_name=destination_table)


@TestStep(When)
def add_column_to_source_and_destination(self):
    """Add column with the same name to both source and destination tables."""
    column_name = "column_" + getuid()

    alter_table_add_column(
        table_name=source_table,
        column_name=column_name,
        column_type="String",
    )

    alter_table_add_column(
        table_name=destination_table,
        column_name=column_name,
        column_type="String",
    )


@TestStep(When)
def export_partition_from_source_table(self):
    """Export partition from the source table to the destination table."""
    number_of_partitions = self.context.number_of_partitions

    with By(
        f"exporting a partition from the {source_table} table to the {destination_table} table"
    ):
        partition_to_export = random.randrange(1, number_of_partitions)
        export_partition_by_id(
            source_table=source_table,
            destination_table=destination_table,
            partition_id=partition_to_export,
        )


@TestStep(When)
def drop_column(self, table_name):
    """Drop column on the table."""
    alter_table_drop_column(table_name=table_name, column_name="extra1")


@TestStep(When)
def drop_column_on_source_table(self):
    """Drop column on the source table."""
    drop_column(table_name=source_table)


@TestStep(When)
def drop_column_on_destination_table(self):
    """Drop column on the destination table."""
    drop_column(table_name=destination_table)


@TestStep(When)
def drop_column_on_source_and_destination(self):
    """Drop the same column on source and destination tables."""
    drop_column_on_source_table()
    drop_column_on_destination_table()


@TestStep(Given)
def drop_partition(self, table_name):
    """Drop partition on the table."""
    partition_name = random.randrange(5, 100)
    alter_table_drop_partition(table_name=table_name, partition_name=partition_name)


@TestStep(Given)
def drop_partition_on_source(self):
    """Drop partition on the source table."""
    drop_partition(table_name=source_table)


@TestStep(Given)
def drop_partition_on_destination(self):
    """Drop partition on the destination table."""
    drop_partition(table_name=destination_table)


@TestStep(Given)
def drop_partition_on_source_and_destination(self):
    """Drop partition on the source and destination tables."""
    drop_partition_on_source()
    drop_partition_on_destination()


@TestStep(Given)
def unfreeze_partition(self, table_name):
    """Unfreeze partition on the table."""
    partition_name = random.randrange(5, 100)
    alter_table_unfreeze_partition_with_name(
        table_name=table_name, backup_name=partition_name
    )


@TestStep(Given)
def unfreeze_source_partition(self):
    """Unfreeze partition on the source table."""
    unfreeze_partition(table_name=source_table)


@TestStep(Given)
def unfreeze_destination_partition(self):
    """Unfreeze partition on the destination table."""
    unfreeze_partition(table_name=destination_table)


@TestStep(Given)
def unfreeze_source_and_destination_partition(self):
    """Unfreeze partition on the source and destination tables."""
    unfreeze_source_partition()
    unfreeze_destination_partition()


@TestStep(Given)
def delete_in_partition(self, table_name):
    """Delete rows in partition."""
    alter_table_delete_rows(table_name=table_name, condition="p < 1")


@TestStep(Given)
def delete_in_source_partition(self):
    """Delete rows in the source partition."""
    delete_in_partition(table_name=source_table)


@TestStep(Given)
def delete_in_destination_partition(self):
    """Delete rows in the destination partition."""
    delete_in_partition(table_name=destination_table)


@TestStep(Given)
def delete_in_source_and_destination_partition(self):
    """Delete rows in the source and destination partitions."""
    delete_in_source_partition()
    delete_in_destination_partition()


@TestStep(When)
def modify_column(self, table_name):
    """Modify column type of the table."""
    alter_table_modify_column(
        table_name=table_name, column_name="extra", column_type="String"
    )


@TestStep(When)
def modify_source_table_column(self):
    """Modify column on the source table."""
    modify_column(table_name=source_table)


@TestStep(When)
def modify_destination_table_column(self):
    """Modify column on the destination table."""
    modify_column(table_name=destination_table)


@TestStep(When)
def modify_column_source_and_destination(self):
    """Modify column on source and destination tables."""
    modify_source_table_column()
    modify_destination_table_column()


@TestStep(When)
def rename_column(self, table_name):
    """Rename column on the table."""
    alter_table_rename_column(
        table_name=table_name, column_name_old="extra2", column_name_new="extra_new"
    )


@TestStep(When)
def rename_source_table_column(self):
    """Rename the column on the source table."""
    rename_column(table_name=source_table)


@TestStep(When)
def rename_destination_table_column(self):
    """Rename the column on the destination table."""
    rename_column(table_name=destination_table)


@TestStep
def rename_column_source_and_destination(self):
    """Rename column on source and destination tables."""
    rename_source_table_column()
    rename_destination_table_column()


@TestStep(When)
def comment_column(self, table_name):
    """Comment column on the table."""
    alter_table_comment_column(
        table_name=table_name, column_name="extra", comment="test_comment"
    )


@TestStep(When)
def comment_source_table_column(self):
    """Comment column on the source table."""
    comment_column(table_name=source_table)


@TestStep(When)
def comment_destination_table_column(self):
    """Comment column on the destination table."""
    comment_column(table_name=destination_table)


@TestStep(When)
def comment_source_and_destination_column(self):
    """Comment columns on source and destination tables."""
    comment_source_table_column()
    comment_destination_table_column()


@TestStep(When)
def add_constraint(self, table_name):
    """Add constraint to the table."""
    constraint_name = "constraint_" + getuid()

    alter_table_add_constraint(
        table_name=table_name, constraint_name=constraint_name, expression="(i > 1)"
    )


@TestStep(When)
def add_constraint_to_the_source_table(self):
    """Add constraint to the source table."""
    add_constraint(table_name=source_table)


@TestStep(When)
def add_constraint_to_the_destination_table(self):
    """Add constraint to the destination table."""
    add_constraint(table_name=destination_table)


@TestStep(When)
def add_constraint_to_source_and_destination(self):
    """Add constraint to source and destination tables."""
    add_constraint_to_the_source_table()
    add_constraint_to_the_destination_table()


@TestStep(When)
def detach_partition(self, table_name):
    """Detach partition from the table."""
    partition_name = random.randrange(5, 100)
    alter_table_detach_partition(table_name=table_name, partition_name=partition_name)


@TestStep(When)
def detach_partition_from_source_table(self):
    """Detach partition from the source table."""
    detach_partition(table_name=source_table)


@TestStep(When)
def detach_partition_from_destination_table(self):
    """Detach partition from the destination table."""
    detach_partition(table_name=destination_table)


@TestStep(When)
def detach_partition_from_source_and_destination(self):
    """Detach partition from source and destination tables."""
    detach_partition_from_source_table()
    detach_partition_from_destination_table()


@TestStep(When)
def attach_partition(self, table_name):
    """Attach partition to the table."""
    alter_table_attach_partition(table_name=table_name, partition_name=12)


@TestStep(When)
def attach_partition_to_source_table(self):
    """Attach partition to the source table."""
    attach_partition(table_name=source_table)


@TestStep(When)
def attach_partition_to_destination_table(self):
    """Attach partition to the destination table."""
    attach_partition(table_name=destination_table)


@TestStep(When)
def attach_partition_to_source_and_destination(self):
    """Attach partition to source and destination tables."""
    attach_partition_to_source_table()
    attach_partition_to_destination_table()


@TestStep(When)
def move_partition_to_volume(
    self, table_name, number_of_partitions=None, partition_name=None
):
    """Move partition to another volume."""
    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    if partition_name is None:
        partition_name = random.randrange(5, number_of_partitions)

    alter_table_move_partition(
        table_name=table_name,
        partition_name=partition_name,
        disk_name="external",
    )


@TestStep(When)
def move_source_partition(self):
    """Move the partition from the source table to external volume."""
    move_partition_to_volume(table_name=source_table)


@TestStep(When)
def move_destination_partition(self):
    """Move the partition from the destination table to external volume."""
    move_partition_to_volume(table_name=destination_table)


@TestStep(When)
def move_source_and_destination_partition(self):
    """Move partition to external volume from source and destination tables."""
    number_of_partitions = self.context.number_of_partitions

    partition_name = random.randrange(5, number_of_partitions)
    move_partition_to_volume(table_name=source_table, partition_name=partition_name)
    move_partition_to_volume(
        table_name=destination_table, partition_name=partition_name
    )


@TestStep(When)
def clear_index(self, table_name, number_of_partitions=None):
    """Clear index inside the partition of the table."""
    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    partition_name = random.randrange(5, number_of_partitions)
    alter_table_clear_index_in_partition(
        table_name=table_name, index="index_name", partition_name=partition_name
    )


@TestStep(When)
def clear_index_source(self):
    """Clear index on the source table."""
    clear_index(table_name=source_table)


@TestStep(When)
def clear_index_destination(self):
    """Clear index on the destination table."""
    clear_index(table_name=destination_table)


@TestStep(When)
def clear_index_source_and_destination(self):
    """Clear index on source and destination tables."""
    clear_index_source()
    clear_index_destination()


@TestStep(When)
def clear_column(self, table_name, number_of_partitions=None):
    """Clear column in a specific partition of the table."""
    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    partition_name = random.randrange(5, number_of_partitions)
    alter_table_clear_column_in_partition(
        table_name=table_name, partition_name=partition_name, column_name="i"
    )


@TestStep(When)
def clear_source_table_column(self):
    """Clear column on the source table."""
    clear_column(table_name=source_table)


@TestStep(When)
def clear_destination_table_column(self):
    """Clear column on the destination table."""
    clear_column(table_name=destination_table)


@TestStep(When)
def clear_column_on_source_and_destination(self):
    """Clear column on source and destination columns."""
    clear_source_table_column()
    clear_destination_table_column()


@TestStep(When)
def freeze_partition(self, table_name, number_of_partitions=None):
    """Freeze a random partition of the table."""
    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    partition_name = random.randrange(5, number_of_partitions)
    alter_table_freeze_partition(table_name=table_name, partition_name=partition_name)


@TestStep(When)
def freeze_source_partition(self):
    """Freeze partition on the source table."""
    freeze_partition(table_name=source_table)


@TestStep(When)
def freeze_destination_partition(self):
    """Freeze partition on the destination table."""
    freeze_partition(table_name=destination_table)


@TestStep(When)
def freeze_partition_on_source_and_destination(self):
    """Freeze partition on source and destination tables."""
    freeze_source_partition()
    freeze_destination_partition()


@TestStep(When)
def freeze_partition_with_name(self, table_name):
    """Freeze partition with name on the table."""
    partition_name = random.randrange(5, 100)
    alter_table_freeze_partition_with_name(
        table_name=table_name, backup_name=partition_name
    )


@TestStep(When)
def freeze_source_partition_with_name(self):
    """Freeze partition on the source table using name of the partition."""
    freeze_partition_with_name(table_name=source_table)


@TestStep(When)
def freeze_destination_partition_with_name(self):
    """Freeze partition on the destination table using name of the partition."""
    freeze_partition_with_name(table_name=destination_table)


@TestStep(When)
def freeze_source_and_destination_partition_with_name(self):
    """Freeze partitions on source and destination tables with name."""
    freeze_source_partition_with_name()
    freeze_destination_partition_with_name()


@TestStep(When)
def concurrent_export_with_multiple_actions(
    self,
    actions,
    number_of_iterations=None,
    number_of_partitions=None,
    number_of_concurrent_queries=None,
):
    """Concurrently run export partition with a number of other actions."""
    if number_of_concurrent_queries is None:
        number_of_concurrent_queries = self.context.number_of_concurrent_queries

    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    if number_of_iterations is None:
        number_of_iterations = self.context.number_of_iterations

    with By(
        "running the export partition number of times and each time run number of other actions in parallel"
    ):
        for i in range(number_of_iterations):
            partition_to_export = random.randrange(1, number_of_partitions)
            for retry in retries(timeout=60):
                with retry:
                    Check(
                        name=f"export partition on the source table #{i}",
                        test=export_partition_and_validate_data,
                        parallel=True,
                    )(
                        source_table=source_table,
                        destination_table=destination_table,
                        partition_to_export=partition_to_export,
                    )

            for action in get_n_random_items(actions, number_of_concurrent_queries):
                for retry in retries(timeout=60):
                    with retry:
                        Check(
                            name=f"{action.__name__} #{i}",
                            test=action,
                            parallel=True,
                        )()
        join()


@TestStep(When)
def export_partition_with_single_concurrent_action(
    self,
    actions,
    number_of_iterations=None,
    number_of_partitions=None,
):
    """Concurrently run a single export partition and another actions that is run a number of times."""
    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    if number_of_iterations is None:
        number_of_iterations = self.context.number_of_iterations

    partition_to_export = random.randrange(1, number_of_partitions)

    for retry in retries(timeout=30):
        with retry:
            Check(
                name=f"export partition on the source table",
                test=export_partition_and_validate_data,
                parallel=True,
            )(
                source_table=source_table,
                destination_table=destination_table,
                partition_to_export=partition_to_export,
            )

        for i in range(number_of_iterations):
            for retry in retries(timeout=60):
                with retry:
                    Check(
                        name=f"{actions.__name__} #{i}",
                        test=actions,
                        parallel=True,
                    )()
    join()


@TestCheck
def concurrent_export(
    self,
    actions,
    concurrent_scenario,
    number_of_partitions=None,
):
    """Concurrently run multiple actions along with export partition."""
    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    with Given(
        "I have a source MergeTree table and destination S3 table with the same structure"
    ):
        columns_with_extras = [
            {"name": "p", "type": "UInt16"},
            {"name": "i", "type": "UInt64"},
            {"name": "extra", "type": "UInt8"},
            {"name": "extra1", "type": "UInt8"},
            {"name": "extra2", "type": "UInt8"},
        ]

        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=columns_with_extras,
            stop_merges=True,
            number_of_partitions=number_of_partitions,
        )

        simple_columns = default_columns(simple=True)
        s3_table_name = create_s3_table(
            table_name=destination_table,
            create_new_bucket=True,
            columns=simple_columns,
        )
        self.context.destination_table = s3_table_name
        self.context.source_table = source_table

    with When("I execute multiple export partitions along with other actions"):
        concurrent_scenario(actions=actions)


@TestScenario
def one_export_partition(self):
    """Check that it is possible to execute a single export partition while the number of other actions is being executed."""
    actions = [
        add_column_to_source_table,
        add_column_to_destination_table,
        export_partition_from_source_table,
        drop_column_on_source_table,
        drop_column_on_destination_table,
        modify_source_table_column,
        modify_destination_table_column,
        rename_source_table_column,
        rename_destination_table_column,
        comment_source_table_column,
        comment_destination_table_column,
        add_constraint_to_the_source_table,
        add_constraint_to_the_destination_table,
        detach_partition_from_source_table,
        detach_partition_from_destination_table,
        attach_partition_to_source_table,
        attach_partition_to_destination_table,
        move_source_partition,
        move_destination_partition,
        clear_destination_table_column,
        clear_source_table_column,
        freeze_source_partition,
        freeze_destination_partition,
        freeze_destination_partition_with_name,
        freeze_source_partition_with_name,
    ]

    for action in actions:
        Scenario(
            name=f"{action.__name__}".replace("_", " "),
            test=concurrent_export,
        )(
            actions=action,
            concurrent_scenario=export_partition_with_single_concurrent_action,
        )


@TestScenario
def export_partition_along_other_actions(self):
    """Check that when we run multiple export partitions in a loop along with other actions, export partitions
    executes successfully."""
    actions = [
        add_column_to_source_and_destination,
        drop_column_on_source_and_destination,
        modify_column_source_and_destination,
        rename_column_source_and_destination,
        comment_source_and_destination_column,
        add_constraint_to_source_and_destination,
        detach_partition_from_source_and_destination,
        attach_partition_to_source_and_destination,
        move_source_and_destination_partition,
        clear_column_on_source_and_destination,
        freeze_partition_on_source_and_destination,
        freeze_source_and_destination_partition_with_name,
        export_partition_from_source_table,
        drop_partition_on_source_and_destination,
        unfreeze_source_and_destination_partition,
        delete_in_source_and_destination_partition,
        clear_index_source_and_destination,
    ]

    Scenario(test=concurrent_export)(
        concurrent_scenario=concurrent_export_with_multiple_actions, actions=actions
    )


@TestFeature
@Requirements(RQ_ClickHouse_ExportPartition_Concurrency("1.0"))
@Name("concurrent actions")
def feature(
    self,
    node="clickhouse1",
    number_of_concurrent_queries=3,
    number_of_partitions=500,
    number_of_iterations=100,
    delay_before=None,
    delay_after=None,
    validate=True,
):
    """
    Concurrently execute export partition on a source table with
    different number of concurrent alter actions being executed in parallel.
    """
    self.context.node = self.context.cluster.node(node)
    self.context.number_of_concurrent_queries = number_of_concurrent_queries
    self.context.number_of_partitions = number_of_partitions
    self.context.number_of_iterations = number_of_iterations
    self.context.delay_before = delay_before
    self.context.delay_after = delay_after
    self.context.validate = validate

    Scenario(run=one_export_partition)
    Scenario(run=export_partition_along_other_actions)
