"""Reusable ALTER TABLE helpers for CAS MergeTree scenarios."""

import json

from testflows.core import *

ALTER_COLUMNS = (
    "partition_column UInt8, id UInt64, value Int64, " "string_column String DEFAULT ''"
)


@TestStep(When)
@Name("insert deterministic ALTER test rows")
def insert_alter_rows(
    self, table_name, partitions=(1, 2), rows_per_partition=5, node=None
):
    """Insert rows into the common ALTER test schema."""
    node = node or self.context.node
    for partition in partitions:
        node.query(
            f"INSERT INTO {table_name} "
            f"(partition_column, id, value, string_column) "
            f"SELECT {partition}, number, number, "
            f"concat('p{partition}-', toString(number)) "
            f"FROM numbers({rows_per_partition})"
        )


@TestStep(When)
@Name("add a column")
def add_column(self, table_name, definition, node=None):
    """Add ``definition`` to ``table_name``."""
    return self.context.node.query(f"ALTER TABLE {table_name} ADD COLUMN {definition}")


@TestStep(When)
@Name("drop a column")
def drop_column(self, table_name, column_name, node=None):
    """Drop ``column_name`` from ``table_name``."""
    return self.context.node.query(
        f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
    )


@TestStep(When)
@Name("rename a column")
def rename_column(self, table_name, old_name, new_name, node=None):
    """Rename a non-key column."""
    return self.context.node.query(
        f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name}"
    )


@TestStep(When)
@Name("comment a column")
def comment_column(self, table_name, column_name, comment, node=None):
    """Set a column comment."""
    escaped_comment = comment.replace("\\", "\\\\").replace("'", "\\'")
    return self.context.node.query(
        f"ALTER TABLE {table_name} COMMENT COLUMN {column_name} " f"'{escaped_comment}'"
    )


@TestStep(When)
@Name("modify a column")
def modify_column(self, table_name, definition, node=None, mutation=False):
    """Apply a MODIFY COLUMN definition."""
    settings = [("mutations_sync", 2)] if mutation else None
    return self.context.node.query(
        f"ALTER TABLE {table_name} MODIFY COLUMN {definition}",
        settings=settings,
    )


@TestStep(When)
@Name("remove a column property")
def remove_column_property(self, table_name, column_name, property_name, node=None):
    """Remove a DEFAULT/COMMENT/CODEC/TTL/SETTINGS-style property."""
    return self.context.node.query(
        f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} "
        f"REMOVE {property_name}"
    )


@TestStep(When)
@Name("modify a column setting")
def modify_column_setting(self, table_name, column_name, setting, value, node=None):
    """Modify one column-level setting."""
    return self.context.node.query(
        f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} "
        f"MODIFY SETTING {setting} = {value}"
    )


@TestStep(When)
@Name("reset a column setting")
def reset_column_setting(self, table_name, column_name, setting, node=None):
    """Reset one column-level setting."""
    return self.context.node.query(
        f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} "
        f"RESET SETTING {setting}"
    )


@TestStep(When)
@Name("add enum values")
def add_enum_values(self, table_name, column_name, values, node=None):
    """Append enum values using the ALTER-specific syntax."""
    return self.context.node.query(
        f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} "
        f"ADD ENUM VALUES ({values})"
    )


@TestStep(When)
@Name("materialize a column")
def materialize_column(self, table_name, column_name, partition=None, node=None):
    """Materialize a DEFAULT or MATERIALIZED column synchronously."""
    partition_clause = "" if partition is None else f" IN PARTITION {partition}"
    return self.context.node.query(
        f"ALTER TABLE {table_name} MATERIALIZE COLUMN "
        f"{column_name}{partition_clause}",
        settings=[("mutations_sync", 2)],
    )


@TestStep(When)
@Name("clear a column in a partition")
def clear_column_in_partition(self, table_name, column_name, partition, node=None):
    """Reset a column to its default in one partition."""
    return self.context.node.query(
        f"ALTER TABLE {table_name} CLEAR COLUMN {column_name} "
        f"IN PARTITION {partition}",
        settings=[("mutations_sync", 2)],
    )


@TestStep(When)
@Name("update rows with ALTER TABLE")
def alter_update(self, table_name, assignments, condition, partition=None, node=None):
    """Run a heavyweight UPDATE mutation synchronously."""
    partition_clause = "" if partition is None else f" IN PARTITION {partition}"
    return self.context.node.query(
        f"ALTER TABLE {table_name} UPDATE {assignments}"
        f"{partition_clause} WHERE {condition}",
        settings=[("mutations_sync", 2)],
    )


@TestStep(When)
@Name("delete rows with ALTER TABLE")
def alter_delete(self, table_name, condition, partition=None, node=None):
    """Run a heavyweight DELETE mutation synchronously."""
    partition_clause = "" if partition is None else f" IN PARTITION {partition}"
    return self.context.node.query(
        f"ALTER TABLE {table_name} DELETE" f"{partition_clause} WHERE {condition}",
        settings=[("mutations_sync", 2)],
    )


def _node(self, node):
    """Return the explicitly supplied node or the suite default."""
    return node or self.context.node


def _alter(self, node, sql, mutation=False):
    """Run an ALTER statement, optionally waiting for mutations."""
    settings = [("mutations_sync", 2)] if mutation else None
    return _node(self, node).query(sql, settings=settings)


def _in_partition(partition):
    """Return an IN PARTITION clause or an empty string."""
    return "" if partition is None else f" IN PARTITION {partition}"


@TestStep(Given)
@Name("create a filled ALTER test table")
def create_filled_alter_table(
    self,
    table_name,
    columns=ALTER_COLUMNS,
    partition_by="partition_column",
    order_by="(partition_column, id)",
    insert=True,
    node=None,
):
    """Create a CAS MergeTree table and optionally fill the common schema."""
    from cas.tests.steps.tables import create_cas_merge_tree_table

    create_cas_merge_tree_table(
        table_name=table_name,
        columns=columns,
        partition_by=partition_by,
        order_by=order_by,
        node=node,
    )
    if insert:
        insert_alter_rows(table_name=table_name, node=_node(self, node))
    return table_name


@TestStep(When)
@Name("modify ORDER BY")
def modify_order_by(self, table_name, expression, extra_alters="", node=None):
    """Change the sorting key, optionally in the same ALTER as other actions."""
    prefix = f"{extra_alters}, " if extra_alters else ""
    return _alter(
        self, node, f"ALTER TABLE {table_name} {prefix}MODIFY ORDER BY {expression}"
    )


@TestStep(When)
@Name("modify SAMPLE BY")
def modify_sample_by(self, table_name, expression, node=None):
    """Set the sampling key to a prefix of the primary key."""
    return _alter(self, node, f"ALTER TABLE {table_name} MODIFY SAMPLE BY {expression}")


@TestStep(When)
@Name("remove SAMPLE BY")
def remove_sample_by(self, table_name, node=None):
    """Drop the sampling key."""
    return _alter(self, node, f"ALTER TABLE {table_name} REMOVE SAMPLE BY")


@TestStep(When)
@Name("add an index")
def add_index(self, table_name, definition, node=None):
    """Add a data-skipping index. ``definition`` includes name, expr, TYPE, GRANULARITY."""
    return _alter(self, node, f"ALTER TABLE {table_name} ADD INDEX {definition}")


@TestStep(When)
@Name("drop an index")
def drop_index(self, table_name, index_name, node=None):
    """Drop a data-skipping index."""
    return _alter(
        self, node, f"ALTER TABLE {table_name} DROP INDEX {index_name}", mutation=True
    )


@TestStep(When)
@Name("materialize an index")
def materialize_index(self, table_name, index_name, partition=None, node=None):
    """Materialize a skip index, optionally in one partition."""
    return _alter(
        self,
        node,
        f"ALTER TABLE {table_name} MATERIALIZE INDEX {index_name}"
        f"{_in_partition(partition)}",
        mutation=True,
    )


@TestStep(When)
@Name("clear an index")
def clear_index(self, table_name, index_name, partition=None, node=None):
    """Clear skip-index files, optionally in one partition."""
    return _alter(
        self,
        node,
        f"ALTER TABLE {table_name} CLEAR INDEX {index_name}"
        f"{_in_partition(partition)}",
        mutation=True,
    )


@TestStep(When)
@Name("add a projection")
def add_projection(self, table_name, definition, node=None):
    """Add a projection. ``definition`` is ``name (SELECT ...)``."""
    return _alter(self, node, f"ALTER TABLE {table_name} ADD PROJECTION {definition}")


@TestStep(When)
@Name("drop a projection")
def drop_projection(self, table_name, projection_name, node=None):
    """Drop a projection."""
    return _alter(
        self,
        node,
        f"ALTER TABLE {table_name} DROP PROJECTION {projection_name}",
        mutation=True,
    )


@TestStep(When)
@Name("materialize a projection")
def materialize_projection(
    self, table_name, projection_name, partition=None, node=None
):
    """Materialize a projection, optionally in one partition."""
    return _alter(
        self,
        node,
        f"ALTER TABLE {table_name} MATERIALIZE PROJECTION {projection_name}"
        f"{_in_partition(partition)}",
        mutation=True,
    )


@TestStep(When)
@Name("clear a projection")
def clear_projection(self, table_name, projection_name, partition=None, node=None):
    """Clear projection files, optionally in one partition."""
    return _alter(
        self,
        node,
        f"ALTER TABLE {table_name} CLEAR PROJECTION {projection_name}"
        f"{_in_partition(partition)}",
        mutation=True,
    )


@TestStep(When)
@Name("add a constraint")
def add_constraint(self, table_name, definition, node=None):
    """Add a CHECK or ASSUME constraint. ``definition`` includes name and expression."""
    return _alter(self, node, f"ALTER TABLE {table_name} ADD CONSTRAINT {definition}")


@TestStep(When)
@Name("modify a constraint")
def modify_constraint(self, table_name, definition, node=None):
    """Replace an existing constraint declaration. Requires ClickHouse >= 26.7."""
    return _alter(
        self, node, f"ALTER TABLE {table_name} MODIFY CONSTRAINT {definition}"
    )


@TestStep(When)
@Name("drop a constraint")
def drop_constraint(self, table_name, constraint_name, node=None):
    """Drop a constraint."""
    return _alter(
        self, node, f"ALTER TABLE {table_name} DROP CONSTRAINT {constraint_name}"
    )


@TestStep(When)
@Name("modify TTL")
def modify_ttl(self, table_name, expression, node=None):
    """Set table TTL."""
    return _alter(self, node, f"ALTER TABLE {table_name} MODIFY TTL {expression}")


@TestStep(When)
@Name("remove TTL")
def remove_ttl(self, table_name, node=None):
    """Drop table TTL."""
    return _alter(self, node, f"ALTER TABLE {table_name} REMOVE TTL")


@TestStep(When)
@Name("materialize TTL")
def materialize_ttl(self, table_name, node=None):
    """Force TTL application as a mutation."""
    return _alter(
        self, node, f"ALTER TABLE {table_name} MATERIALIZE TTL", mutation=True
    )


@TestStep(When)
@Name("add statistics")
def add_statistics(self, table_name, definition, node=None):
    """Add column statistics. ``definition`` is ``columns TYPE types``."""
    return _alter(self, node, f"ALTER TABLE {table_name} ADD STATISTICS {definition}")


@TestStep(When)
@Name("modify statistics")
def modify_statistics(self, table_name, definition, node=None):
    """Modify column statistics types."""
    return _alter(
        self, node, f"ALTER TABLE {table_name} MODIFY STATISTICS {definition}"
    )


@TestStep(When)
@Name("drop statistics")
def drop_statistics(self, table_name, columns, node=None):
    """Drop column statistics metadata and files."""
    return _alter(
        self,
        node,
        f"ALTER TABLE {table_name} DROP STATISTICS {columns}",
        mutation=True,
    )


@TestStep(When)
@Name("clear statistics")
def clear_statistics(self, table_name, columns, node=None):
    """Clear statistics objects from parts."""
    return _alter(
        self,
        node,
        f"ALTER TABLE {table_name} CLEAR STATISTICS {columns}",
        mutation=True,
    )


@TestStep(When)
@Name("materialize statistics")
def materialize_statistics(self, table_name, columns="ALL", node=None):
    """Rebuild column statistics as a mutation."""
    return _alter(
        self,
        node,
        f"ALTER TABLE {table_name} MATERIALIZE STATISTICS {columns}",
        mutation=True,
    )


@TestStep(Given)
def table_columns(self, table_name, node=None):
    """Return column names for ``table_name`` in the current database."""
    if node is None:
        node = self.context.node

    result = node.query(
        "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS "
        f"WHERE table_schema = currentDatabase() AND table_name = '{table_name}' "
        "ORDER BY ordinal_position"
    )
    output = result.output.strip()
    return output.split("\n") if output else []


def column_metadata(node, table_name, column_name):
    """Return column metadata as a dict, or None if the column is absent.

    JSONEachRow is used instead of TSV because ``echo -e`` and ``str.strip()``
    both destroy trailing empty tab-separated fields.
    """
    result = node.query(
        "SELECT type, default_kind, default_expression, comment "
        "FROM system.columns "
        f"WHERE database = currentDatabase() AND table = '{table_name}' "
        f"AND name = '{column_name}' FORMAT JSONEachRow"
    )
    output = result.output.strip()
    return json.loads(output) if output else None


def show_create_table(node, table_name):
    """Return the canonical CREATE TABLE statement."""
    return node.query(f"SHOW CREATE TABLE {table_name}").output
