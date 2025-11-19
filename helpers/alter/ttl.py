from testflows.core import *


@TestStep(Given)
def alter_table_modify_ttl(self, table_name, ttl_expression, node=None, **query_kwargs):
    """Modify TTL in the table using alter."""
    if node is None:
        node = self.context.node

    with By("modifying TTL in the table"):
        query = f"ALTER TABLE {table_name} MODIFY TTL {ttl_expression}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_remove_ttl(self, table_name, node=None, **query_kwargs):
    """Remove TTL from the table using alter."""
    if node is None:
        node = self.context.node

    with By("removing TTL from the table"):
        query = f"ALTER TABLE {table_name} REMOVE TTL"
        node.query(query, **query_kwargs)
