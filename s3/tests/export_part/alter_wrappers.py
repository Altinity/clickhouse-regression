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
        partition_name = get_random_partition(table_name=table_name)

    if partition_name != "":
        with By("Dropping partition"):
            partition.alter_table_drop_partition(
                table_name=table_name, partition_name=partition_name, **query_kwargs
            )


@TestStep(When)
def alter_table_detach_partition(self, table_name, partition_name=None, **query_kwargs):
    """Detach a partition from a table."""
    if partition_name is None:
        partition_name = get_random_partition(table_name=table_name)

    if partition_name != "":
        with By("Detaching partition"):
            partition.alter_table_detach_partition(
                table_name=table_name, partition_name=partition_name, **query_kwargs
            )


@TestStep(When)
def alter_table_attach_partition(self, table_name, partition_name=None, **query_kwargs):
    """Attach partition with automatic setup."""
    if partition_name is None:
        partition_name = get_random_partition(table_name=table_name)
        if partition_name != "":
            alter_table_detach_partition(
                table_name=table_name, partition_name=partition_name
            )
            partition.alter_table_attach_partition(
                table_name=table_name, partition_name=partition_name, **query_kwargs
            )
    else:
        with By("Attaching partition"):
            partition.alter_table_attach_partition(
                table_name=table_name, partition_name=partition_name, **query_kwargs
            )


@TestStep(When)
def alter_table_attach_partition_from(self, table_name, partition_name, **query_kwargs):
    """Attach partition from with automatic setup (creates temp table)."""

    with By("Creating new table"):
        new_table_name = partitioned_merge_tree_table(
            table_name="table_" + getuid(),
            partition_by="p",
            columns=get_column_info(node=self.context.node, table_name=table_name),
            query_settings="storage_policy = 'tiered_storage'",
        )

    with And("Attaching partition from new table"):
        partition.alter_table_attach_partition_from(
            table_name=table_name,
            partition_name=partition_name,
            path_to_backup=new_table_name,
            **query_kwargs,
        )


@TestStep(When)
def alter_table_move_partition_to_table(
    self, table_name, partition_name, **query_kwargs
):
    """Move partition to table with automatic setup (creates temp table)."""

    with By("Creating temp table"):
        partitioned_merge_tree_table(
            table_name=table_name + "_temp",
            partition_by="p",
            columns=get_column_info(node=self.context.node, table_name=table_name),
            query_settings="storage_policy = 'tiered_storage'",
        )

    with And("Moving partition to table"):
        partition.alter_table_move_partition_to_table(
            table_name=f"{table_name}_temp",
            partition_name=partition_name,
            destination_table=table_name,
            **query_kwargs,
        )


@TestStep(When)
def alter_table_clear_index_in_partition(
    self, table_name, partition_name, index, **query_kwargs
):
    """Clear index in partition with automatic setup (adds index first)."""

    with By("Adding index"):
        self.context.node.query(
            f"ALTER TABLE {table_name} ADD INDEX {index} i TYPE minmax GRANULARITY 1"
        )

    with And("Clearing index in partition"):
        skipping_index.alter_table_clear_index_in_partition(
            table_name=table_name,
            partition_name=partition_name,
            index=index,
            **query_kwargs,
        )


@TestStep(When)
def alter_table_unfreeze_partition_with_name(
    self, table_name, partition_name, backup_name, **query_kwargs
):
    """Unfreeze partition with name with automatic setup (freezes partition first)."""

    with By("Freezing partition"):
        partition.alter_table_freeze_partition_with_name(
            table_name=table_name,
            backup_name=backup_name,
            partition_name=partition_name,
        )

    with And("Unfreezing partition"):
        partition.alter_table_unfreeze_partition_with_name(
            table_name=table_name,
            partition_name=partition_name,
            backup_name=backup_name,
            **query_kwargs,
        )


@TestStep(When)
def alter_table_replace_partition(self, table_name, partition_name, **query_kwargs):
    """Replace partition with automatic setup (creates temp table)."""

    with By("Creating temp table"):
        partitioned_merge_tree_table(
            table_name=table_name + "_temp",
            partition_by="p",
            columns=get_column_info(node=self.context.node, table_name=table_name),
            query_settings="storage_policy = 'tiered_storage'",
        )

    with And("Replacing partition"):
        partition.alter_table_replace_partition(
            table_name=table_name,
            partition_name=partition_name,
            source_table=f"{table_name}_temp",
            **query_kwargs,
        )


@TestStep(When)
def alter_table_fetch_partition(self, table_name, partition_name, **query_kwargs):
    """Fetch partition with automatic setup (creates temp replicated table)."""

    with By("Creating temp replicated table"):
        partitioned_replicated_merge_tree_table(
            table_name=table_name + "_temp",
            partition_by="p",
            columns=get_column_info(node=self.context.node, table_name=table_name),
            query_settings="storage_policy = 'tiered_storage'",
        )

    with And("Fetching partition"):
        partition.alter_table_fetch_partition(
            table_name=table_name,
            partition_name=partition_name,
            path_to_backup=f"/clickhouse/tables/shard0/{table_name}_temp",
            **query_kwargs,
        )


@TestStep(When)
def alter_table_move_partition(self, table_name, partition_name, **query_kwargs):
    """Move partition with automatic setup (creates temp table)."""
    moved = False
    for volume in ["hot", "cold"]:
        try:
            partition.alter_table_move_partition(
                table_name=table_name,
                partition_name=partition_name,
                disk_name=volume,
                **query_kwargs,
            )
            moved = True
            break
        except Exception as e:
            note(f"Failed to move to {volume}: {e}")
    if not moved:
        raise Exception("Failed to move partition to any volume")


@TestStep(When)
def optimize_table(self, table_name):
    """Optimize a table using alter."""

    self.context.node.query(
        f"SYSTEM START MERGES {table_name}",
        exitcode=0,
    )

    with By(f"Optimizing {table_name}"):
        optimize(node=self.context.node, table_name=table_name, final=True)
