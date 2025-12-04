from testflows.core import *
from helpers.alter import column, constraint, partition, skipping_index
from helpers.create import *
from helpers.queries import *
from s3.tests.export_part.steps import *
from helpers.common import getuid


@TestStep(When)
def alter_table_add_column(
    self, table_name, column_name=None, column_type=None, **query_kwargs
):
    """Add column to a table with default values."""

    if column_name is None:
        column_name = f"new_column_{getuid()}"
    if column_type is None:
        column_type = "UInt64"

    with By("Adding column"):
        column.alter_table_add_column(
            table_name=table_name,
            column_name=column_name,
            column_type=column_type,
            **query_kwargs,
        )

    return column_name


@TestStep(When)
def alter_table_drop_column(self, table_name, column_name=None, **query_kwargs):
    """Drop a column from a table."""

    if column_name is None:
        column_name = alter_table_add_column(table_name=table_name)

    with By("Dropping column"):
        column.alter_table_drop_column(
            table_name=table_name, column_name=column_name, **query_kwargs
        )


@TestStep(When)
def alter_table_modify_column(
    self, table_name, column_name=None, column_type=None, **query_kwargs
):
    """Modify a column type in a table."""

    if column_name is None:
        column_name = alter_table_add_column(table_name=table_name)
    if column_type is None:
        column_type = (
            "String"
            if get_column_type(table_name=table_name, column_name=column_name)
            != "String"
            else "UInt64"
        )

    with By("Modifying column"):
        column.alter_table_modify_column(
            table_name=table_name,
            column_name=column_name,
            column_type=column_type,
            **query_kwargs,
        )


@TestStep(When)
def alter_table_rename_column(
    self, table_name, column_name_old=None, column_name_new=None, **query_kwargs
):
    """Rename a column in a table."""

    if column_name_old is None:
        column_name_old = alter_table_add_column(table_name=table_name)
    if column_name_new is None:
        column_name_new = f"renamed_column_{getuid()}"

    with By("Renaming column"):
        column.alter_table_rename_column(
            table_name=table_name,
            column_name_old=column_name_old,
            column_name_new=column_name_new,
            **query_kwargs,
        )


@TestStep(When)
def alter_table_add_constraint(
    self, table_name, constraint_name=None, expression=None, **query_kwargs
):
    """Add a constraint to a table."""
    if constraint_name is None:
        constraint_name = f"constraint_{getuid()}"
    if expression is None:
        expression = "1 = 1"

    with By("Adding constraint"):
        constraint.alter_table_add_constraint(
            table_name=table_name,
            constraint_name=constraint_name,
            expression=expression,
            **query_kwargs,
        )

    return constraint_name


@TestStep(When)
def alter_table_drop_constraint(self, table_name, constraint_name=None, **query_kwargs):
    """Drop constraint with automatic setup."""

    if constraint_name is None:
        constraint_name = alter_table_add_constraint(table_name=table_name)

    with By("Dropping constraint"):
        constraint.alter_table_drop_constraint(
            table_name=table_name, constraint_name=constraint_name, **query_kwargs
        )


@TestStep(When)
def alter_table_drop_partition(self, table_name, partition_name=None, **query_kwargs):
    """Drop a partition from a table."""
    if partition_name is None:
        partition_name = create_new_partition(table_name=table_name)

    with By("Dropping partition"):
        partition.alter_table_drop_partition(
            table_name=table_name,
            partition_name=partition_name,
            no_checks=True,
            **query_kwargs,
        )


@TestStep(When)
def alter_table_detach_partition(self, table_name, partition_name=None, **query_kwargs):
    """Detach a partition from a table."""
    if partition_name is None:
        partition_name = create_new_partition(table_name=table_name)

    with By("Detaching partition"):
        partition.alter_table_detach_partition(
            table_name=table_name,
            partition_name=partition_name,
            no_checks=True,
            **query_kwargs,
        )


@TestStep(When)
def alter_table_attach_partition(self, table_name, partition_name=None, **query_kwargs):
    """Attach partition with automatic setup."""
    if partition_name is None:
        partition_name = create_new_partition(table_name=table_name)
        alter_table_detach_partition(
            table_name=table_name, partition_name=partition_name
        )

    with By("Attaching partition"):
        partition.alter_table_attach_partition(
            table_name=table_name,
            partition_name=partition_name,
            no_checks=True,
            **query_kwargs,
        )


@TestStep(When)
def alter_table_attach_partition_from(
    self, table_name, partition_name=None, path_to_backup=None, **query_kwargs
):
    """Attach partition from with automatic setup."""

    if path_to_backup is None:
        path_to_backup = partitioned_merge_tree_table(
            table_name="table_" + getuid(),
            partition_by="p",
            stop_merges=True,
            populate=False,
            columns=get_column_info(node=self.context.node, table_name=table_name),
            query_settings=f"storage_policy = 'tiered_storage'",
        )
        partition_name = create_new_partition(table_name=path_to_backup)

    elif partition_name is None:
        partition_name = create_new_partition(table_name=path_to_backup)

    with By("Attaching partition from new table"):
        partition.alter_table_attach_partition_from(
            table_name=table_name,
            partition_name=partition_name,
            path_to_backup=path_to_backup,
            **query_kwargs,
        )


@TestStep(When)
def alter_table_move_partition_to_table(
    self, table_name, partition_name=None, destination_table=None, **query_kwargs
):
    """Move partition to table with automatic setup."""

    if destination_table is None:
        destination_table = partitioned_merge_tree_table(
            table_name="table_" + getuid(),
            partition_by="p",
            stop_merges=True,
            populate=False,
            columns=get_column_info(node=self.context.node, table_name=table_name),
            query_settings=f"storage_policy = 'tiered_storage'",
        )

    if partition_name is None:
        partition_name = create_new_partition(table_name=table_name)

    with By("Moving partition to table"):
        partition.alter_table_move_partition_to_table(
            table_name=table_name,
            partition_name=partition_name,
            destination_table=destination_table,
            no_checks=True,
            **query_kwargs,
        )


@TestStep(When)
def alter_table_move_partition(
    self, table_name, partition_name=None, disk_name=None, **query_kwargs
):
    """Move partition with automatic setup."""
    if partition_name is None:
        partition_name = create_new_partition(table_name=table_name)
    if disk_name is None:
        disk_name = random.choice(["hot", "cold"])

    with By(f"Attempting to move partition to {disk_name} volume"):
        partition.alter_table_move_partition(
            table_name=table_name,
            partition_name=partition_name,
            disk_name=disk_name,
            no_checks=True,
            **query_kwargs,
        )


@TestStep(When)
def alter_table_clear_column_in_partition(
    self, table_name, column_name, partition_name=None, **query_kwargs
):
    """Clear column in partition with automatic setup."""
    if partition_name is None:
        partition_name = get_random_partition(table_name=table_name)

    with By("Clearing column in partition"):
        column.alter_table_clear_column_in_partition(
            table_name=table_name,
            partition_name=partition_name,
            column_name=column_name,
            **query_kwargs,
        )


@TestStep(When)
def alter_table_clear_index_in_partition(
    self, table_name, partition_name=None, index=None, **query_kwargs
):
    """Clear index in partition with automatic setup."""

    if partition_name is None:
        partition_name = get_random_partition(table_name=table_name)
    if index is None:
        index = f"idx_{getuid()}"
        skipping_index.alter_table_add_index(
            table_name=table_name,
            index_name=index,
            index_expression="i",
            index_type="minmax",
            **query_kwargs,
        )

    with By("Clearing index in partition"):
        skipping_index.alter_table_clear_index_in_partition(
            table_name=table_name,
            partition_name=partition_name,
            index=index,
            **query_kwargs,
        )


@TestStep(When)
def alter_table_freeze_partition(self, table_name, partition_name=None, **query_kwargs):
    """Freeze partition with automatic setup."""
    if partition_name is None:
        partition_name = get_random_partition(table_name=table_name)

    with By("Freezing partition"):
        partition.alter_table_freeze_partition(
            table_name=table_name, partition_name=partition_name, **query_kwargs
        )


@TestStep(When)
def alter_table_freeze_partition_with_name(
    self, table_name, partition_name=None, backup_name=None, **query_kwargs
):
    """Freeze partition with automatic setup."""
    if partition_name is None:
        partition_name = get_random_partition(table_name=table_name)
    if backup_name is None:
        backup_name = f"backup_{getuid()}"

    with By("Freezing partition"):
        partition.alter_table_freeze_partition_with_name(
            table_name=table_name,
            backup_name=backup_name,
            partition_name=partition_name,
            **query_kwargs,
        )


@TestStep(When)
def alter_table_unfreeze_partition_with_name(
    self, table_name, partition_name=None, backup_name=None, **query_kwargs
):
    """Unfreeze partition with name with automatic setup."""
    if backup_name is None:
        backup_name = f"backup_{getuid()}"
        partition_name = get_random_partition(table_name=table_name)
        partition.alter_table_freeze_partition_with_name(
            table_name=table_name,
            backup_name=backup_name,
            partition_name=partition_name,
        )

    with By("Unfreezing partition"):
        partition.alter_table_unfreeze_partition_with_name(
            table_name=table_name,
            partition_name=partition_name,
            backup_name=backup_name,
            **query_kwargs,
        )


@TestStep(When)
def alter_table_replace_partition(
    self, table_name, partition_name=None, source_table=None, **query_kwargs
):
    """Replace partition with automatic setup."""

    if source_table is None:
        source_table = partitioned_merge_tree_table(
            table_name="table_" + getuid(),
            partition_by="p",
            stop_merges=True,
            number_of_partitions=1,
            columns=get_column_info(node=self.context.node, table_name=table_name),
            query_settings=f"storage_policy = 'tiered_storage'",
        )

    if partition_name is None:
        partition_name = get_random_partition(table_name=table_name)

    with By("Replacing partition"):
        partition.alter_table_replace_partition(
            table_name=table_name,
            partition_name=partition_name,
            source_table=source_table,
            **query_kwargs,
        )


@TestStep(When)
def alter_table_fetch_partition(
    self,
    table_name,
    partition_name=None,
    path_to_backup=None,
    cleanup=False,
    **query_kwargs,
):
    """Fetch partition with automatic setup."""
    if path_to_backup is None:
        path_to_backup = partitioned_replicated_merge_tree_table(
            table_name="table_" + getuid(),
            partition_by="p",
            populate=False,
            stop_merges=True,
            columns=get_column_info(node=self.context.node, table_name=table_name),
            query_settings=f"storage_policy = 'tiered_storage'",
        )
        partition_name = create_new_partition(table_name=path_to_backup)

    elif partition_name is None:
        partition_name = create_new_partition(table_name=path_to_backup)

    with By(f"Fetching partition {partition_name}"):
        partition.alter_table_fetch_partition(
            table_name=table_name,
            partition_name=partition_name,
            path_to_backup=f"/clickhouse/tables/shard0/{path_to_backup}",
            no_checks=True,
            **query_kwargs,
        )

    if cleanup:
        self.context.node.query(
            f"ALTER TABLE {table_name} DROP DETACHED PARTITION {partition_name}",
            settings=[("allow_drop_detached", 1)],
            exitcode=0,
            steps=True,
        )


@TestStep(When)
def optimize_partition(self, table_name, partition=None, node=None):
    """Optimize a partition of a table."""

    if node is None:
        node = self.context.node
    if partition is None:
        partition = get_random_partition(table_name=table_name, node=node)

    with By(f"Optimizing partition {partition}"):
        node.query(
            f"OPTIMIZE TABLE {table_name} PARTITION '{partition}' FINAL",
            exitcode=0,
            steps=True,
        )


@TestStep(When)
def optimize_table(self, table_name, node=None):
    """Optimize a table using alter."""

    if node is None:
        node = self.context.node

    with By(f"Optimizing {table_name}"):
        optimize(node=node, table_name=table_name, final=True)


@TestStep(When)
def drop_table(self, table_name, node=None, recreate=False):
    """Drop a table."""
    if node is None:
        node = self.context.node

    with By(f"Dropping table {table_name}"):
        node.query(f"DROP TABLE IF EXISTS {table_name}")

    if recreate:
        with And(f"Recreating table {table_name}"):
            partitioned_merge_tree_table(
                table_name=table_name,
                partition_by="p",
                populate=False,
                columns=default_columns(simple=False),
                stop_merges=True,
                query_settings="storage_policy = 'tiered_storage'",
                if_not_exists=True,
            )
