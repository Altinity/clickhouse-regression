from testflows.core import *


@TestStep(When)
def insert_values_into_table(self, table_name, values, node=None):
    """Insert one or more value tuples into a table."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    if not isinstance(values, str):
        values = ", ".join(values)

    node.query(f"INSERT INTO {table_name} VALUES {values}")


insert_values = (
    " ('data1', 1, 0),"
    " ('data1', 2, 0),"
    " ('data1', 3, 0),"
    " ('data1', 3, 0),"
    " ('data1', 1, 1),"
    " ('data1', 2, 1),"
    " ('data2', 1, 0),"
    " ('data2', 2, 0),"
    " ('data2', 3, 0),"
    " ('data2', 3, 1),"
    " ('data2', 1, 1),"
    " ('data2', 2, 1),"
    " ('data3', 1, 0),"
    " ('data3', 2, 0),"
    " ('data3', 3, 0),"
    " ('data3', 3, 1),"
    " ('data3', 1, 1),"
    " ('data3', 2, 1)"
)
