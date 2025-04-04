from testflows.core import *


@TestStep(Given)
def alter_table_add_column(
    self,
    table_name,
    column_name,
    column_type,
    column_name_after=None,
    node=None,
    if_not_exists=False,
    **query_kwargs,
):
    """Add column to the existing table using alter."""
    if node is None:
        node = self.context.node

    if if_not_exists:
        if_not_exists = "IF NOT EXISTS "

    with By("executing alter add column command on the table"):
        query = f"ALTER TABLE {table_name} ADD COLUMN {if_not_exists}{column_name} {column_type}"

        if column_name_after:
            query += f" AFTER {column_name_after}"

        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_drop_column(self, table_name, column_name, node=None, **query_kwargs):
    """Drop column from the table using alter."""
    if node is None:
        node = self.context.node

    with By("dropping column from the table"):
        query = f"ALTER TABLE {table_name} DROP COLUMN IF EXISTS {column_name}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_modify_column(
    self, table_name, column_name, column_type, node=None, **query_kwargs
):
    """Modify column type in the table using alter."""
    if node is None:
        node = self.context.node

    with By("modifying column type in the table"):
        query = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} {column_type}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_rename_column(
    self, table_name, column_name_old, column_name_new, node=None, **query_kwargs
):
    """Rename column in the table using alter."""
    if node is None:
        node = self.context.node

    with By("renaming column in the table"):
        query = f"ALTER TABLE {table_name} RENAME COLUMN IF EXISTS {column_name_old} TO {column_name_new}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_comment_column(
    self, table_name, column_name, comment, node=None, **query_kwargs
):
    """Comment column in the table using alter."""
    if node is None:
        node = self.context.node

    with By("commenting column in the table"):
        query = f"ALTER TABLE {table_name} COMMENT COLUMN {column_name} '{comment}'"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_add_constraint(
    self, table_name, constraint_name, expression, node=None, **query_kwargs
):
    """Add constraint to the table using alter."""
    if node is None:
        node = self.context.node

    with By("adding constraint to the table"):
        query = f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} CHECK {expression}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_drop_constraint(
    self, table_name, constraint_name, node=None, **query_kwargs
):
    """Drop constraint from the table using alter."""
    if node is None:
        node = self.context.node

    with By("dropping constraint from the table"):
        query = f"ALTER TABLE {table_name} DROP CONSTRAINT {constraint_name}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_drop_partition(
    self, table_name, partition_name, node=None, **query_kwargs
):
    """Drop partition from the table using alter."""
    if node is None:
        node = self.context.node

    with By("dropping partition from the table"):
        query = f"ALTER TABLE {table_name} DROP PARTITION {partition_name}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_modify_ttl(self, table_name, ttl_expression, node=None, **query_kwargs):
    """Modify TTL in the table using alter."""
    if node is None:
        node = self.context.node

    with By("modifying TTL in the table"):
        query = f"ALTER TABLE {table_name} MODIFY TTL {ttl_expression}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_detach_partition(
    self, table_name, partition_name, node=None, **query_kwargs
):
    """Detach partition from the table using alter."""
    if node is None:
        node = self.context.node

    with By("detaching partition from the table"):
        query = f"ALTER TABLE {table_name} DETACH PARTITION {partition_name}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_attach_partition(
    self, table_name, partition_name, node=None, **query_kwargs
):
    """Attach partition to the table using alter."""
    if node is None:
        node = self.context.node

    with By("attaching partition to the table"):
        query = f"ALTER TABLE {table_name} ATTACH PARTITION {partition_name}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_attach_partition_from(
    self, table_name, partition_name, path_to_backup, node=None, **query_kwargs
):
    """Attach partition from a backup to the table using alter."""
    if node is None:
        node = self.context.node

    with By("attaching partition from a backup to the table"):
        query = f"ALTER TABLE {table_name} ATTACH PARTITION {partition_name} FROM {path_to_backup}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_move_partition_to_table(
    self, table_name, partition_name, path_to_backup, node=None, **query_kwargs
):
    """Move partition to another table using alter."""
    if node is None:
        node = self.context.node

    with By("moving partition to another table"):
        query = f"ALTER TABLE {table_name} MOVE PARTITION {partition_name} TO TABLE {path_to_backup}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_move_partition(
    self,
    table_name,
    partition_name,
    disk_name,
    node=None,
    disk="VOLUME",
    **query_kwargs,
):
    """Move partition to a different disk or volume using alter."""
    if node is None:
        node = self.context.node

    with By("moving partition to a different disk or volume"):
        query = f"ALTER TABLE {table_name} MOVE PARTITION {partition_name} TO {disk} '{disk_name}'"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_clear_column_in_partition(
    self, table_name, partition_name, column_name, node=None, **query_kwargs
):
    """Clear column in partition using alter."""
    if node is None:
        node = self.context.node

    with By("clearing column in partition"):
        query = f"ALTER TABLE {table_name} CLEAR COLUMN {column_name} IN PARTITION {partition_name}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_clear_index_in_partition(
    self, table_name, partition_name, index, node=None, **query_kwargs
):
    """Clear index in partition using alter."""
    if node is None:
        node = self.context.node

    with By("clearing column in partition"):
        query = f"ALTER TABLE {table_name} CLEAR INDEX {index} IN PARTITION {partition_name}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_fetch_partition(
    self, table_name, partition_name, path_to_backup, node=None, **query_kwargs
):
    """Fetch partition from a source table using alter."""
    if node is None:
        node = self.context.node

    with By("fetching partition from a source table"):
        query = f"ALTER TABLE {table_name} FETCH PARTITION {partition_name} FROM '{path_to_backup}'"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_freeze_partition(
    self, table_name, partition_name, node=None, **query_kwargs
):
    """Freeze partition for backup using alter."""
    if node is None:
        node = self.context.node

    with By("freezing partition for backup"):
        query = f"ALTER TABLE {table_name} FREEZE PARTITION {partition_name}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_freeze_partition_with_name(
    self, table_name, backup_name, partition_name=None, node=None, **query_kwargs
):
    """Freeze partition with a name using alter."""
    if node is None:
        node = self.context.node

    partition = ""
    if partition_name:
        partition = f"PARTITION {partition_name} "

    with By("freezing partition with a name"):
        query = f"ALTER TABLE {table_name} FREEZE {partition}WITH NAME '{backup_name}'"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_unfreeze_partition_with_name(
    self, table_name, backup_name, partition_name=None, node=None, **query_kwargs
):
    """Unfreeze partition with a name using alter."""
    if node is None:
        node = self.context.node

    partition = ""
    if partition_name:
        partition = f"PARTITION {partition_name} "

    with By("unfreezing partition with a name"):
        query = (
            f"ALTER TABLE {table_name} UNFREEZE {partition}WITH NAME '{backup_name}'"
        )
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_replace_partition(
    self, table_name, partition_name, path_to_backup, node=None, **query_kwargs
):
    """Replace partition from a source table using alter."""
    if node is None:
        node = self.context.node

    with By("replacing partition from a source table to the destination table"):
        query = f"ALTER TABLE {table_name} REPLACE PARTITION {partition_name} FROM {path_to_backup}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_update_column(
    self, table_name, column_name, expression, condition, node=None, **query_kwargs
):
    """Update specific column in the table using alter with condition."""
    if node is None:
        node = self.context.node

    with By("updating specific column in the table with condition"):
        query = f"ALTER TABLE {table_name} UPDATE {column_name} = {expression} WHERE {condition}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_delete_rows(self, table_name, condition, node=None, **query_kwargs):
    """Delete rows from the table using alter with condition."""
    if node is None:
        node = self.context.node

    with By("deleting rows from the table with condition"):
        query = f"ALTER TABLE {table_name} DELETE WHERE {condition}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_modify_comment(self, table_name, comment, node=None, **query_kwargs):
    """Modify table comment using alter."""
    if node is None:
        node = self.context.node

    with By("modifying table comment"):
        query = f"ALTER TABLE {table_name} MODIFY COMMENT '{comment}'"
        node.query(query, **query_kwargs)
