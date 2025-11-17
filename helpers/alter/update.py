from testflows.core import *


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
def alter_table_update_columns(
    self, table_name, assignments, condition, node=None, **query_kwargs
):
    """Update multiple columns in the table using alter with condition."""
    if node is None:
        node = self.context.node

    with By("updating multiple columns in the table with condition"):
        if isinstance(assignments, dict):
            assignments_str = ", ".join(
                [f"{col} = {expr}" for col, expr in assignments.items()]
            )
        else:
            assignments_str = assignments

        query = f"ALTER TABLE {table_name} UPDATE {assignments_str} WHERE {condition}"
        node.query(query, **query_kwargs)

