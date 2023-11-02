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
def alter_table_add_index(
    self,
    table_name,
    index_name,
    expression,
    index_type,
    partition_name=None,
    granularity=None,
    node=None,
):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} ADD INDEX {index_name} {expression} TYPE {index_type}"
    if partition_name:
        query += f" IN PARTITION {partition_name}"
    if granularity:
        query += f" GRANULARITY {granularity}"

    node.query(query)


@TestStep(Given)
def alter_table_drop_index(self, table_name, index_name, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} DROP INDEX {index_name}"
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
def alter_table_modify_settings(self, table_name, key, value, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} MODIFY SETTINGS {key}={value}"

    node.query(query)


@TestStep(Given)
def alter_table_modify_partition_by(self, table_name, expression, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} MODIFY PARTITION BY {expression}"
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
    node.quer(query)


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
def alter_table_unfreeze_partition(self, table_name, partition_name, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} UNFREEZE PARTITION {partition_name}"
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

    query = f"ALTER TABLE {table_name} REPLACE PARTITION {partition_name} FROM '{path_to_backup}'"
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
def alter_table_update_ttl(self, table_name, ttl_expression, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} UPDATE TTL {ttl_expression}"
    node.query(query)


@TestStep(Given)
def alter_table_modify_comment(self, table_name, comment, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} MODIFY COMMENT '{comment}'"
    node.query(query)


@TestStep(Given)
def alter_table_modify_codec_compression(
    self, table_name, param1, value1, param2=None, value2=None, node=None
):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} MODIFY CODEC COMPRESSION {param1}={value1}"
    if param2 and value2:
        query += f", {param2}={value2}"
    node.query(query)


@TestStep(Given)
def alter_table_modify_ttl_to_future(self, table_name, interval, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} MODIFY TTL now() TO now() + INTERVAL {interval}"
    node.query(query)


@TestStep(Given)
def alter_table_modify_ttl_to_past(self, table_name, interval, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} MODIFY TTL now() - INTERVAL {interval}"
    node.query(query)


@TestStep(Given)
def alter_table_modify_ttl_to_now(self, table_name, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} MODIFY TTL now()"
    node.query(query)


@TestStep(Given)
def alter_table_modify_ttl_clear(self, table_name, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} MODIFY TTL CLEAR"
    node.query(query)


@TestStep(Given)
def alter_table_modify_codec_delete_compression(self, table_name, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} MODIFY CODEC DELETE COMPRESSION"
    node.query(query)


@TestStep(Given)
def alter_table_modify_codec_recompress(self, table_name, node=None):
    if node is None:
        node = self.context.node

    query = f"ALTER TABLE {table_name} MODIFY CODEC RECOMPRESS"
    node.query(query)
