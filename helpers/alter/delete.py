from testflows.core import *


@TestStep(Given)
def alter_table_delete_rows(self, table_name, condition, node=None, **query_kwargs):
    """Delete rows from the table using alter with condition."""
    if node is None:
        node = self.context.node

    with By("deleting rows from the table with condition"):
        query = f"ALTER TABLE {table_name} DELETE WHERE {condition}"
        node.query(query, **query_kwargs)

