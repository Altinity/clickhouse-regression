import random

from helpers.alter import *
from helpers.common import getuid
from helpers.create import *
from helpers.queries import *
from s3.requirements.export_partition import *
from s3.tests.export_partition.steps import *


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


@TestStep(When)
def add_column(self, table_name, partitions=None, node=None):
    """Add column to the table."""
    if node is None:
        node = self.context.node

    if partitions is None:
        partitions = get_partitions(table_name=table_name, node=node)

    for _ in partitions:
        alter_table_add_column(
            table_name=table_name,
            column_name="column_" + getuid(),
            column_type="String",
        )


@TestStep(When)
def drop_column(self, table_name, partitions=None, node=None):
    """Drop column on the table."""
    if node is None:
        node = self.context.node

    if partitions is None:
        partitions = get_partitions(table_name=table_name, node=node)

    for _ in partitions:
        alter_table_drop_column(table_name=table_name, column_name="extra1")


@TestStep(When)
def drop_column_on_source_table(self, source_table):
    """Drop column on the source table."""
    drop_column(table_name=source_table)


@TestStep(Given)
def drop_partition(self, table_name, partitions=None, node=None):
    """Drop partition on the table."""
    if node is None:
        node = self.context.node

    if partitions is None:
        partitions = get_partitions(table_name=table_name, node=node)

    non_existent_partitions = [str(1000 + i) for i in range(len(partitions))]
    for partition_id in non_existent_partitions:
        alter_table_drop_partition(table_name=table_name, partition_name=partition_id)


@TestStep(Given)
def drop_partition_on_source(self, source_table):
    """Drop partition on the source table."""
    drop_partition(table_name=source_table)


@TestStep(Given)
def unfreeze_partition(self, table_name, partitions=None, node=None):
    """Unfreeze partition on the table."""
    if node is None:
        node = self.context.node

    if partitions is None:
        partitions = get_partitions(table_name=table_name, node=node)

    for partition_id in partitions:
        alter_table_unfreeze_partition_with_name(
            table_name=table_name, backup_name=partition_id
        )


@TestStep(Given)
def unfreeze_source_partition(self, source_table):
    """Unfreeze partition on the source table."""
    unfreeze_partition(table_name=source_table)


@TestStep(Given)
def unfreeze_partition_on_source(self, source_table):
    """Unfreeze partition on the source table."""
    unfreeze_partition(table_name=source_table)


@TestStep(Given)
def delete_in_partition(self, table_name, partitions=None, node=None):
    """Delete rows in partition."""
    if node is None:
        node = self.context.node

    if partitions is None:
        partitions = get_partitions(table_name=table_name, node=node)

    for _ in partitions:
        alter_table_delete_rows(table_name=table_name, condition="p < 1")


@TestStep(Given)
def delete_in_source_partition(self, source_table):
    """Delete rows in the source partition."""
    delete_in_partition(table_name=source_table)


@TestStep(Given)
def delete_in_partition_on_source(self, source_table):
    """Delete rows in the source partition."""
    delete_in_partition(table_name=source_table)


@TestStep(When)
def modify_column(self, table_name, partitions=None, node=None):
    """Modify column type of the table."""
    if node is None:
        node = self.context.node

    if partitions is None:
        partitions = get_partitions(table_name=table_name, node=node)

    for _ in partitions:
        alter_table_modify_column(
            table_name=table_name, column_name="extra", column_type="String"
        )


@TestStep(When)
def modify_source_table_column(self, source_table):
    """Modify column on the source table."""
    modify_column(table_name=source_table)


@TestStep(When)
def rename_column(self, table_name, partitions=None, node=None):
    """Rename column on the table."""
    if node is None:
        node = self.context.node

    if partitions is None:
        partitions = get_partitions(table_name=table_name, node=node)

    for _ in partitions:
        alter_table_rename_column(
            table_name=table_name, column_name_old="extra2", column_name_new="extra_new"
        )


@TestStep(When)
def rename_source_table_column(self, source_table):
    """Rename the column on the source table."""
    rename_column(table_name=source_table)


@TestStep(When)
def comment_column(self, table_name, partitions=None, node=None):
    """Comment column on the table."""
    if node is None:
        node = self.context.node

    if partitions is None:
        partitions = get_partitions(table_name=table_name, node=node)

    for _ in partitions:
        alter_table_comment_column(
            table_name=table_name, column_name="extra", comment="test_comment"
        )


@TestStep(When)
def comment_source_table_column(self, source_table):
    """Comment column on the source table."""
    comment_column(table_name=source_table)


@TestStep(When)
def add_constraint(self, table_name, partitions=None, node=None):
    """Add constraint to the table."""
    if node is None:
        node = self.context.node

    if partitions is None:
        partitions = get_partitions(table_name=table_name, node=node)

    for _ in partitions:
        constraint_name = "constraint_" + getuid()
        alter_table_add_constraint(
            table_name=table_name, constraint_name=constraint_name, expression="(i > 1)"
        )


@TestStep(When)
def add_constraint_to_the_source_table(self, source_table):
    """Add constraint to the source table."""
    add_constraint(table_name=source_table)


@TestStep(When)
def add_column_to_source(self, source_table):
    """Add column to the source table."""
    add_column(table_name=source_table)


@TestStep(When)
def drop_column_on_source(self, source_table):
    """Drop column on the source table."""
    drop_column(table_name=source_table)


@TestStep(When)
def modify_column_on_source(self, source_table):
    """Modify column on the source table."""
    modify_column(table_name=source_table)


@TestStep(When)
def rename_column_on_source(self, source_table):
    """Rename column on the source table."""
    rename_column(table_name=source_table)


@TestStep(When)
def comment_column_on_source(self, source_table):
    """Comment column on the source table."""
    comment_column(table_name=source_table)


@TestStep(When)
def add_constraint_to_source(self, source_table):
    """Add constraint to the source table."""
    add_constraint(table_name=source_table)


@TestStep(When)
def detach_partition(self, table_name, partitions=None, node=None):
    """Detach partition from the table."""
    if node is None:
        node = self.context.node

    if partitions is None:
        partitions = get_partitions(table_name=table_name, node=node)

    non_existent_partitions = [str(1000 + i) for i in range(len(partitions))]
    for partition_id in non_existent_partitions:
        alter_table_detach_partition(table_name=table_name, partition_name=partition_id)


@TestStep(When)
def detach_partition_from_source_table(self, source_table):
    """Detach partition from the source table."""
    detach_partition(table_name=source_table)


@TestStep(When)
def detach_partition_from_source(self, source_table):
    """Detach partition from the source table."""
    detach_partition_from_source_table(source_table=source_table)


@TestStep(When)
def attach_partition(self, table_name, partitions=None, node=None):
    """Attach partition to the table."""
    if node is None:
        node = self.context.node

    if partitions is None:
        partitions = get_partitions(table_name=table_name, node=node)

    for partition_id in partitions:
        alter_table_attach_partition(table_name=table_name, partition_name=partition_id)


@TestStep(When)
def attach_partition_to_source_table(self, source_table):
    """Attach partition to the source table."""
    attach_partition(table_name=source_table)


@TestStep(When)
def attach_partition_to_source(self, source_table):
    """Attach partition to the source table."""
    attach_partition_to_source_table(source_table=source_table)


@TestStep(When)
def move_partition_to_volume(self, table_name, partitions=None, node=None):
    """Move partition to another volume."""
    if node is None:
        node = self.context.node

    if partitions is None:
        partitions = get_partitions(table_name=table_name, node=node)

    for partition_id in partitions:
        alter_table_move_partition(
            table_name=table_name,
            partition_name=partition_id,
            disk_name=random.choice(["hot", "cold"]),
            no_checks=True,
        )


@TestStep(When)
def move_source_partition(self, source_table):
    """Move the partition from the source table to external volume."""
    move_partition_to_volume(table_name=source_table)


@TestStep(When)
def move_partition_on_source(self, source_table):
    """Move partition to external volume from the source table."""
    move_source_partition(source_table=source_table)


@TestStep(When)
def clear_index(self, table_name, partitions=None, node=None):
    """Clear index inside the partition of the table."""
    if node is None:
        node = self.context.node

    if partitions is None:
        partitions = get_partitions(table_name=table_name, node=node)

    for partition_id in partitions:
        alter_table_clear_index_in_partition(
            table_name=table_name, index="index_name", partition_name=partition_id
        )


@TestStep(When)
def clear_index_source(self, source_table):
    """Clear index on the source table."""
    clear_index(table_name=source_table)


@TestStep(When)
def clear_index_on_source(self, source_table):
    """Clear index on the source table."""
    clear_index(table_name=source_table)


@TestStep(When)
def clear_column(self, table_name, partitions=None, node=None):
    """Clear column in a specific partition of the table."""
    if node is None:
        node = self.context.node

    if partitions is None:
        partitions = get_partitions(table_name=table_name, node=node)

    for partition_id in partitions:
        alter_table_clear_column_in_partition(
            table_name=table_name, partition_name=partition_id, column_name="i"
        )


@TestStep(When)
def clear_source_table_column(self, source_table):
    """Clear column on the source table."""
    clear_column(table_name=source_table)


@TestStep(When)
def clear_column_on_source(self, source_table):
    """Clear column on the source table."""
    clear_source_table_column(source_table=source_table)


@TestStep(When)
def freeze_partition(self, table_name, partitions=None, node=None):
    """Freeze a random partition of the table."""
    if node is None:
        node = self.context.node

    if partitions is None:
        partitions = get_partitions(table_name=table_name, node=node)

    for partition_id in partitions:
        alter_table_freeze_partition(table_name=table_name, partition_name=partition_id)


@TestStep(When)
def freeze_source_partition(self, source_table):
    """Freeze partition on the source table."""
    freeze_partition(table_name=source_table)


@TestStep(When)
def freeze_partition_on_source(self, source_table):
    """Freeze partition on the source table."""
    freeze_source_partition(source_table=source_table)


@TestStep(When)
def freeze_partition_with_name(self, table_name, partitions=None, node=None):
    """Freeze partition with name on the table."""
    if node is None:
        node = self.context.node

    if partitions is None:
        partitions = get_partitions(table_name=table_name, node=node)

    for partition_id in partitions:
        alter_table_freeze_partition_with_name(
            table_name=table_name, backup_name=f"{partition_id}_{getuid()}"
        )


@TestStep(When)
def freeze_source_partition_with_name(self, source_table):
    """Freeze partition on the source table using name of the partition."""
    freeze_partition_with_name(table_name=source_table)


@TestStep(When)
def freeze_partition_on_source_with_name(self, source_table):
    """Freeze partition on the source table with name."""
    freeze_source_partition_with_name(source_table=source_table)


@TestCheck
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

    source_table = f"source_{getuid()}"
    table_for_actions = f"source_actions_{getuid()}"
    with Given("I create source and destination tables"):
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
            number_of_parts=10,
            query_settings=f"storage_policy = 'tiered_storage'",
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(
            table_name="s3", create_new_bucket=True, columns=columns_with_extras
        )

    with And("I create another table to run actions on"):
        partitioned_replicated_merge_tree_table(
            table_name=table_for_actions,
            partition_by="p",
            columns=columns_with_extras,
            stop_merges=False,
            number_of_partitions=number_of_partitions,
            number_of_parts=10,
            query_settings=f"storage_policy = 'tiered_storage'",
            cluster="replicated_cluster",
        )

    with And(
        "running the export partition number of times and each time run number of other actions in parallel"
    ):
        with Pool(2) as pool:
            Check(test=export_partitions, parallel=True, executor=pool)(
                source_table=source_table,
                destination_table=s3_table_name,
                node=self.context.node,
            )

            for action in get_n_random_items(actions, number_of_concurrent_queries):
                Check(name=f"{action.__name__}", test=action, executor=pool)(
                    source_table=table_for_actions
                )
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
    table_for_actions = f"source_actions_{getuid()}"
    with Given("I create source and destination tables"):
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
            number_of_parts=10,
            query_settings=f"storage_policy = 'tiered_storage'",
            cluster="replicated_cluster",
        )

        s3_table_name = create_s3_table(
            table_name="s3", create_new_bucket=True, columns=columns_with_extras
        )

        self.context.source_table = source_table
        self.context.destination_table = s3_table_name

    with And("I create another table to run actions on"):
        partitioned_replicated_merge_tree_table(
            table_name=table_for_actions,
            partition_by="p",
            columns=columns_with_extras,
            stop_merges=False,
            number_of_partitions=number_of_partitions,
            number_of_parts=10,
            query_settings=f"storage_policy = 'tiered_storage'",
            cluster="replicated_cluster",
        )

    with And("running the export partition along with another action multiple times"):
        with Pool(2) as pool:
            Check(test=export_partitions, parallel=True, executor=pool)(
                source_table=source_table,
                destination_table=s3_table_name,
                node=self.context.node,
            )
            Check(
                name=f"{actions.__name__}", test=actions, parallel=True, executor=pool
            )(
                source_table=table_for_actions,
            )

            join()


@TestScenario
def one_export_partition(self):
    """Check that it is possible to execute a single export partition while the number of other actions is being executed."""
    actions = [
        add_column_to_source,
        drop_column_on_source,
        modify_column_on_source,
        rename_column_on_source,
        comment_column_on_source,
        add_constraint_to_source,
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
            test=export_partition_with_single_concurrent_action,
        )(
            actions=action,
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

    Scenario(test=concurrent_export_with_multiple_actions)(actions=actions)


@TestFeature
@Requirements(RQ_ClickHouse_ExportPartition_Concurrency("1.0"))
@Name("concurrent actions")
def feature(
    self,
    node="clickhouse1",
    number_of_concurrent_queries=3,
    number_of_partitions=10,
    number_of_iterations=10,
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

    with Given("I set up MinIO storage configuration"):
        minio_storage_configuration(restart=True)

    Scenario(run=one_export_partition)
    Scenario(run=export_partition_along_other_actions)
