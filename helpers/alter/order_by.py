from testflows.core import *


@TestStep(Given)
def alter_table_modify_order_by(
    self, table_name, order_by_expression, node=None, **query_kwargs
):
    """Modify ORDER BY expression of the table using alter."""
    if node is None:
        node = self.context.node

    with By("modifying ORDER BY expression of the table"):
        query = f"ALTER TABLE {table_name} MODIFY ORDER BY {order_by_expression}"
        node.query(query, **query_kwargs)
