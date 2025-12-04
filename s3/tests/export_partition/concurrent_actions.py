import random
import time

from testflows.core import *
from testflows.asserts import error

from alter.stress.tests.tc_netem import network_packet_rate_limit
from s3.tests.export_partition.steps import *
from helpers.common import getuid
from helpers.create import *
from helpers.queries import *
from helpers.alter import *
from s3.requirements.export_partition import *


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
def add_column_to_source(self, source_table):
    """Add column to the source table."""
    add_column(table_name=source_table)


@TestStep(When)
def drop_column(self, table_name):
    """Drop column on the table."""
    alter_table_drop_column(table_name=table_name, column_name="extra1")


@TestStep(When)
def drop_column_on_source_table(self):
    """Drop column on the source table."""
    drop_column(table_name=source_table)


@TestStep(When)
def drop_column_on_source(self):
    """Drop column on the source table."""
    drop_column_on_source_table()


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
def unfreeze_partition_on_source(self):
    """Unfreeze partition on the source table."""
    unfreeze_source_partition()


@TestStep(Given)
def delete_in_partition(self, table_name):
    """Delete rows in partition."""
    alter_table_delete_rows(table_name=table_name, condition="p < 1")


@TestStep(Given)
def delete_in_source_partition(self):
    """Delete rows in the source partition."""
    delete_in_partition(table_name=source_table)


@TestStep(Given)
def delete_in_partition_on_source(self):
    """Delete rows in the source partition."""
    delete_in_source_partition()


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
def modify_column_on_source(self):
    """Modify column on the source table."""
    modify_source_table_column()


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


@TestStep
def rename_column_on_source(self):
    """Rename column on the source table."""
    rename_source_table_column()


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
def comment_column_on_source(self):
    """Comment column on the source table."""
    comment_source_table_column()


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
def add_constraint_to_source(self):
    """Add constraint to the source table."""
    add_constraint_to_the_source_table()


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
def detach_partition_from_source(self):
    """Detach partition from the source table."""
    detach_partition_from_source_table()


@TestStep(When)
def attach_partition(self, table_name):
    """Attach partition to the table."""
    alter_table_attach_partition(table_name=table_name, partition_name=12)


@TestStep(When)
def attach_partition_to_source_table(self):
    """Attach partition to the source table."""
    attach_partition(table_name=source_table)


@TestStep(When)
def attach_partition_to_source(self):
    """Attach partition to the source table."""
    attach_partition_to_source_table()


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
def move_partition_on_source(self):
    """Move partition to external volume from the source table."""
    move_source_partition()


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
def clear_index_on_source(self):
    """Clear index on the source table."""
    clear_index_source()


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
def clear_column_on_source(self):
    """Clear column on the source table."""
    clear_source_table_column()


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
def freeze_partition_on_source(self):
    """Freeze partition on the source table."""
    freeze_source_partition()


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
def freeze_partition_on_source_with_name(self):
    """Freeze partition on the source table with name."""
    freeze_source_partition_with_name()


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

    with By("applying a delay on clickhouse queries"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.05)

    with And(
        "running the export partition number of times and each time run number of other actions in parallel"
    ):
        for i in range(number_of_iterations):
            partition_to_export = random.randrange(1, number_of_partitions)
            for retry in retries(timeout=60):
                with retry:
                    Check(
                        name=f"export partition on the source table #{i}",
                        test=export_partition_and_validate_data,
                    )(
                        source_table=source_table,
                        destination_table=destination_table,
                        partition_to_export=partition_to_export,
                    )

            time.sleep(1)

            for action in get_n_random_items(actions, number_of_concurrent_queries):
                for retry in retries(timeout=60):
                    with retry:
                        Check(
                            name=f"{action.__name__} #{i}",
                            test=action,
                        )()
        join()


@TestCheck
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

    source_table = f"source_{getuid()}"
    with Given("I create source and destination tables"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
            number_of_partitions=10,
            number_of_parts=20,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)
    with And("I apply a delay on clickhouse queries"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.05)

    with And("running the export partition along with another action multiple times"):
        for retry in retries(timeout=30):
            with retry:
                Check(test=export_partitions, parallel=True)(
                    source_table=source_table,
                    destination_table=s3_table_name,
                    node=self.context.node,
                )
            for i in range(number_of_iterations):
                for retry in retries(timeout=60):
                    with retry:
                        Check(
                            name=f"{actions.__name__} #{i}",
                            test=actions,
                        )(
                            source_table=source_table,
                        )
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
            stop_merges=False,
            number_of_partitions=number_of_partitions,
        )

        s3_table_name = create_s3_table(
            table_name=destination_table,
            create_new_bucket=True,
            columns=columns_with_extras,
        )
        self.context.destination_table = s3_table_name
        self.context.source_table = source_table

    with When("I execute multiple export partitions along with other actions"):
        concurrent_scenario(actions=actions)


@TestScenario
def one_export_partition(self):
    """Check that it is possible to execute a single export partition while the number of other actions is being executed."""
    actions = [
        add_column_to_source,
        drop_column_on_source_table,
        modify_source_table_column,
        rename_source_table_column,
        comment_source_table_column,
        add_constraint_to_the_source_table,
        detach_partition_from_source_table,
        attach_partition_to_source_table,
        move_source_partition,
        clear_source_table_column,
        freeze_source_partition,
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
        add_column_to_source,
        drop_column_on_source,
        modify_column_on_source,
        rename_column_on_source,
        comment_column_on_source,
        add_constraint_to_source,
        detach_partition_from_source,
        attach_partition_to_source,
        move_partition_on_source,
        clear_column_on_source,
        freeze_partition_on_source,
        freeze_partition_on_source_with_name,
        drop_partition_on_source,
        unfreeze_partition_on_source,
        delete_in_partition_on_source,
        clear_index_on_source,
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
