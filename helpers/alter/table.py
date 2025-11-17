from testflows.core import *


@TestStep(Given)
def alter_table_modify_comment(self, table_name, comment, node=None, **query_kwargs):
    """Modify table comment using alter."""
    if node is None:
        node = self.context.node

    with By("modifying table comment"):
        query = f"ALTER TABLE {table_name} MODIFY COMMENT '{comment}'"
        node.query(query, **query_kwargs)

