from testflows.core import *


@TestStep(Given)
def alter_table_add_index(
    self,
    table_name,
    index_name,
    index_expression,
    index_type,
    granularity=None,
    node=None,
    **query_kwargs,
):
    """Add skipping index to the table using alter."""
    if node is None:
        node = self.context.node

    with By("adding skipping index to the table"):
        query = f"ALTER TABLE {table_name} ADD INDEX {index_name} {index_expression} TYPE {index_type}"

        if granularity:
            query += f" GRANULARITY {granularity}"

        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_drop_index(self, table_name, index_name, node=None, **query_kwargs):
    """Drop skipping index from the table using alter."""
    if node is None:
        node = self.context.node

    with By("dropping skipping index from the table"):
        query = f"ALTER TABLE {table_name} DROP INDEX {index_name}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_materialize_index(
    self, table_name, index_name, partition_name=None, node=None, **query_kwargs
):
    """Materialize skipping index in the table using alter."""
    if node is None:
        node = self.context.node

    with By("materializing skipping index in the table"):
        query = f"ALTER TABLE {table_name} MATERIALIZE INDEX {index_name}"

        if partition_name:
            query += f" IN PARTITION {partition_name}"

        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_clear_index(
    self, table_name, index_name, partition_name=None, node=None, **query_kwargs
):
    """Clear skipping index in the table using alter."""
    if node is None:
        node = self.context.node

    with By("clearing skipping index in the table"):
        query = f"ALTER TABLE {table_name} CLEAR INDEX {index_name}"

        if partition_name:
            query += f" IN PARTITION {partition_name}"

        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_clear_index_in_partition(
    self, table_name, partition_name, index, node=None, **query_kwargs
):
    """Clear index in partition using alter."""
    if node is None:
        node = self.context.node

    with By("clearing index in partition"):
        query = f"ALTER TABLE {table_name} CLEAR INDEX {index} IN PARTITION {partition_name}"
        node.query(query, **query_kwargs)
