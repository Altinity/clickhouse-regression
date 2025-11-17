from testflows.core import *


@TestStep(Given)
def alter_table_drop_statistics(
    self, table_name, statistics_name=None, node=None, **query_kwargs
):
    """Drop statistics from the table using alter."""
    if node is None:
        node = self.context.node

    with By("dropping statistics from the table"):
        if statistics_name:
            query = f"ALTER TABLE {table_name} DROP STATISTICS {statistics_name}"
        else:
            query = f"ALTER TABLE {table_name} DROP STATISTICS"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_collect_statistics(
    self, table_name, statistics_name=None, node=None, **query_kwargs
):
    """Collect statistics for the table using alter."""
    if node is None:
        node = self.context.node

    with By("collecting statistics for the table"):
        if statistics_name:
            query = f"ALTER TABLE {table_name} COLLECT STATISTICS {statistics_name}"
        else:
            query = f"ALTER TABLE {table_name} COLLECT STATISTICS"
        node.query(query, **query_kwargs)

