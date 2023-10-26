from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid
from helpers.tables import create_table_partitioned_by_column


@TestStep(Given)
def insert_into_table_random_uint64(self, table_name, number_of_values, node=None):
    """Insert random UInt64 values into a column."""
    if node is None:
        node = self.context.node

    with By("Inserting random values into a column with uint64 datatype"):
        node.query(
            f"INSERT INTO {table_name} (p, i) SELECT 1, rand64() FROM numbers({number_of_values})"
        )


@TestStep(Given)
def create_two_tables_partitioned_by_column_with_data(
    self, destination_table, source_table
):
    """Creating two tables that are partitioned by the same column and arr filled with random data."""

    with By("I create two tables with the same structure"):
        create_table_partitioned_by_column(table_name=source_table)
        create_table_partitioned_by_column(table_name=destination_table)

    with And("I insert data into both tables"):
        insert_into_table_random_uint64(
            table_name=destination_table, number_of_values=10
        )
        insert_into_table_random_uint64(table_name=source_table, number_of_values=10)
