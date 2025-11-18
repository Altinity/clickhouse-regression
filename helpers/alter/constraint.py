from testflows.core import *


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
