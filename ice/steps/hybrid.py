from testflows.core import *

from helpers.common import getuid


@TestStep(Given)
def create_hybrid_table(
    self,
    table_name=None,
    node=None,
    columns_definition=None,
    database_name="default",
    left_table_name=None,
    right_table_name=None,
    left_predicate=None,
    right_predicate=None,
):
    """Test step to create a hybrid table."""
    if node is None:
        node = self.context.node

    if table_name is None:
        table_name = f"hybrid_table_{getuid()}"

    query = f"SET allow_experimental_hybrid_table = 1;\n"

    query += f"CREATE TABLE {database_name}.{table_name}\n"

    if columns_definition is not None:
        query += f"{columns_definition}\n"

    query += f"ENGINE = Hybrid({left_table_name}, {left_predicate}, {right_table_name}, {right_predicate})\n"

    try:
        with By(f"creating hybrid table {database_name}.{table_name}"):
            node.query(query)
            yield table_name

    finally:
        with Finally(f"drop the hybrid table {database_name}.{table_name}"):
            pass
            # node.query(f"DROP TABLE IF EXISTS {database_name}.{table_name}")
