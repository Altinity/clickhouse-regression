from testflows.core import *


@TestStep(Given)
def alter_table_apply_deleted_mask(
    self, table_name, node=None, **query_kwargs
):
    """Apply deleted mask to the table using alter."""
    if node is None:
        node = self.context.node

    with By("applying deleted mask to the table"):
        query = f"ALTER TABLE {table_name} APPLY DELETED MASK"
        node.query(query, **query_kwargs)

