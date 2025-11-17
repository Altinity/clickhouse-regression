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
    first=False,
    default_expr=None,
    codec=None,
    **query_kwargs,
):
    """Add column to the existing table using alter."""
    if node is None:
        node = self.context.node

    if if_not_exists:
        if_not_exists = "IF NOT EXISTS "
    else:
        if_not_exists = ""

    with By("executing alter add column command on the table"):
        query = f"ALTER TABLE {table_name} ADD COLUMN {if_not_exists}{column_name} {column_type}"

        if default_expr:
            query += f" DEFAULT {default_expr}"

        if codec:
            query += f" CODEC({codec})"

        if first:
            query += " FIRST"
        elif column_name_after:
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
    self,
    table_name,
    column_name,
    column_type=None,
    default_expr=None,
    codec=None,
    ttl=None,
    comment=None,
    node=None,
    first=False,
    column_name_after=None,
    **query_kwargs,
):
    """Modify column type, default expression, codec, TTL, comment, or position in the table using alter."""
    if node is None:
        node = self.context.node

    with By("modifying column in the table"):
        query = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name}"

        if column_type:
            query += f" {column_type}"

        if default_expr:
            query += f" DEFAULT {default_expr}"

        if codec:
            query += f" CODEC({codec})"

        if ttl:
            query += f" TTL {ttl}"

        if comment:
            query += f" COMMENT '{comment}'"

        if first:
            query += " FIRST"
        elif column_name_after:
            query += f" AFTER {column_name_after}"

        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_modify_column_remove(
    self, table_name, column_name, property_name, node=None, **query_kwargs
):
    """Remove column property (DEFAULT, ALIAS, MATERIALIZED, CODEC, COMMENT, TTL, SETTINGS) using alter."""
    if node is None:
        node = self.context.node

    with By(f"removing {property_name} property from column"):
        query = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} REMOVE {property_name}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_modify_column_modify_setting(
    self, table_name, column_name, settings, node=None, **query_kwargs
):
    """Modify column setting using alter."""
    if node is None:
        node = self.context.node

    with By("modifying column setting"):
        query = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} MODIFY SETTING {settings}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_modify_column_reset_setting(
    self, table_name, column_name, setting_names, node=None, **query_kwargs
):
    """Reset column setting to default value using alter."""
    if node is None:
        node = self.context.node

    with By("resetting column setting"):
        if isinstance(setting_names, str):
            setting_names = [setting_names]
        settings = ", ".join(setting_names)
        query = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} RESET SETTING {settings}"
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
def alter_table_clear_column(
    self, table_name, column_name, node=None, **query_kwargs
):
    """Clear column values in the table using alter."""
    if node is None:
        node = self.context.node

    with By("clearing column values in the table"):
        query = f"ALTER TABLE {table_name} CLEAR COLUMN {column_name}"
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
def alter_table_materialize_column(
    self,
    table_name,
    column_name,
    partition_name=None,
    partition_id=None,
    node=None,
    **query_kwargs,
):
    """Materialize column with DEFAULT or MATERIALIZED value expression using alter."""
    if node is None:
        node = self.context.node

    with By("materializing column"):
        query = f"ALTER TABLE {table_name} MATERIALIZE COLUMN {column_name}"

        if partition_name:
            query += f" IN PARTITION {partition_name}"
        elif partition_id:
            query += f" IN PARTITION ID '{partition_id}'"

        node.query(query, **query_kwargs)

