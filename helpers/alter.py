from testflows.core import *


@TestStep(Given)
def alter_table_add_column(
    self,
    table_name,
    column_name,
    column_type,
    column_name_after=None,
    node=None,
):
    """Add column to the existing table using alter."""
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
    if column_name_after:
        query += f" AFTER {column_name_after}"

    node.query(query)


@TestStep(Given)
def alter_table_drop_column(
    self,
    table_name,
    column_name,
    node=None,
):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
    node.query(query)


@TestStep(Given)
def alter_table_modify_column(self, table_name, column_name, column_type, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} {column_type}"
    node.query(query)


@TestStep(Given)
def alter_table_rename_column(
    self, table_name, column_name_old, column_name_new, node=None
):
    if node is None:
        node = self.context.node

    query = (
        f"ALTER TABLE {table_name} RENAME COLUMN {column_name_old} TO {column_name_new}"
    )
    node.query(query)


@TestStep(Given)
def alter_table_comment_column(self, table_name, column_name, comment, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} COMMENT COLUMN {column_name} '{comment}'"
    node.query(query)


@TestStep(Given)
def alter_table_add_constraint(
    self, table_name, constraint_name, expression, node=None
):
    if node is None:
        node = self.context.node

    query = (
        f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} CHECK {expression}"
    )

    node.query(query)


@TestStep(Given)
def alter_table_drop_constraint(self, table_name, constraint_name, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} DROP CONSTRAINT {constraint_name}"

    node.query(query)


@TestStep(Given)
def alter_table_modify_ttl(self, table_name, ttl_expression, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} MODIFY TTL {ttl_expression}"
    node.query(query)


@TestStep(Given)
def alter_table_detach_partition(self, table_name, partition_name, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} DETACH PARTITION {partition_name}"
    node.query(query)


@TestStep(Given)
def alter_table_attach_partition(self, table_name, partition_name, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} ATTACH PARTITION {partition_name}"
    node.query(query)


@TestStep(Given)
def alter_table_attach_partition_from(
    self, table_name, partition_name, path_to_backup, node=None
):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} ATTACH PARTITION {partition_name} FROM {path_to_backup}"
    node.query(query)


@TestStep(Given)
def alter_table_move_partition_to_table(
    self, table_name, partition_name, path_to_backup, node=None
):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} MOVE PARTITION {partition_name} TO TABLE {path_to_backup}"
    node.query(query)


@TestStep(Given)
def alter_table_move_partition(self, table_name, partition_name, disk_name, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} MOVE PARTITION {partition_name} TO VOLUME '{disk_name}'"
    node.query(query)


@TestStep(Given)
def alter_table_clear_column_in_partition(
    self, table_name, partition_name, column_name, node=None
):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} CLEAR COLUMN {column_name} IN PARTITION {partition_name}"
    node.query(query)


@TestStep(Given)
def alter_table_fetch_partition(
    self, table_name, partition_name, path_to_backup, node=None
):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} FETCH PARTITION {partition_name} FROM '{path_to_backup}'"
    node.query(query)


@TestStep(Given)
def alter_table_freeze_partition(self, table_name, partition_name, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} FREEZE PARTITION {partition_name}"
    node.query(query)


@TestStep(Given)
def alter_table_freeze_partition_with_name(self, table_name, backup_name, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} FREEZE WITH NAME '{backup_name}'"
    node.query(query)


@TestStep(Given)
def alter_table_unfreeze_partition_with_name(self, table_name, backup_name, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} UNFREEZE WITH NAME '{backup_name}'"
    node.query(query)


@TestStep(Given)
def alter_table_replace_partition(
    self, table_name, partition_name, path_to_backup, node=None
):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} REPLACE PARTITION {partition_name} FROM {path_to_backup}"
    node.query(query)


@TestStep(Given)
def alter_table_update_column(
    self, table_name, column_name, expression, condition, node=None
):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} UPDATE {column_name} = {expression} WHERE {condition}"
    node.query(query)


@TestStep(Given)
def alter_table_delete_rows(self, table_name, condition, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} DELETE WHERE {condition}"
    node.query(query)


@TestStep(Given)
def alter_table_modify_comment(self, table_name, comment, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} MODIFY COMMENT '{comment}'"
    node.query(query)
