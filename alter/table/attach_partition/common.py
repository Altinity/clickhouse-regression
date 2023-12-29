from testflows.asserts import *
from testflows.core import *

from helpers.tables import *


@TestStep(Given)
def create_partitioned_table_with_data(
    self,
    table_name,
    engine="MergeTree",
    partition_by="tuple()",
    columns=None,
    query_settings=None,
    order_by="tuple()",
    node=None,
    number_of_partitions=3,
    bias=4,
):
    """Create a table that is partitioned by specified columns."""

    if node is None:
        node = self.context.node

    if columns is None:
        columns = [
            Column(name="a", datatype=UInt16()),
            Column(name="b", datatype=UInt16()),
            Column(name="c", datatype=UInt16()),
            Column(name="extra", datatype=UInt64()),
        ]

    with By(f"creating a table that is partitioned by '{partition_by}'"):
        create_table(
            name=table_name,
            engine=engine,
            partition_by=partition_by,
            order_by=order_by,
            columns=columns,
            query_settings=query_settings,
            if_not_exists=True,
            node=node,
        )

    with And(f"inserting data that will create multiple partitions"):
        for i in range(1, number_of_partitions + 1):
            node.query(
                f"INSERT INTO {table_name} (a, b, c, extra) SELECT {i}, {i+4}, {i+8}, number+1000 FROM numbers({10})"
            )


@TestStep(Given)
def create_empty_partitioned_table(
    self,
    table_name,
    engine="MergeTree",
    partition_by="tuple()",
    columns=None,
    query_settings=None,
    order_by="tuple()",
    node=None,
):
    """Create a table that is partitioned by specified columns."""

    if node is None:
        node = self.context.node

    if columns is None:
        columns = [
            Column(name="a", datatype=UInt16()),
            Column(name="b", datatype=UInt16()),
            Column(name="c", datatype=UInt16()),
            Column(name="extra", datatype=UInt64()),
        ]

    with By(f"creating a table that is partitioned by '{partition_by}'"):
        create_table(
            name=table_name,
            engine=engine,
            partition_by=partition_by,
            order_by=order_by,
            columns=columns,
            query_settings=query_settings,
            if_not_exists=True,
            node=node,
        )


@TestStep(Then)
def check_partition_was_attached(
    self,
    table,
    node=None,
    sort_column="p",
    partition=1,
    column="i",
    list=False,
):
    """Check that the partition was attached on the table."""
    if node is None:
        node = self.context.node

    with By("selecting data from the table"):
        partition_values = node.query(
            f"SELECT partition_id FROM system.detached_parts WHERE table = '{table}' and partition_id = '{partition}' ORDER BY tuple(*)"
        ).output

        assert len(partition_values) == 0


@TestStep(Then)
def check_partition_was_detached(
    self,
    table,
    node=None,
    sort_column="p",
    partition=1,
    column="i",
    list=False,
):
    """Check that the partition was detached from the table."""
    if node is None:
        node = self.context.node

    with By("selecting data from the table"):
        partition_values = node.query(
            f"SELECT partition_id FROM system.detached_parts WHERE table = '{table}' and partition_id = '{partition}' ORDER BY tuple(*)"
        ).output

        assert len(partition_values) > 0


@TestStep(Given)
def insert_data(
    self,
    table_name,
    number_of_values=3,
    number_of_partitions=5,
    number_of_parts=1,
    node=None,
    bias=0,
):
    """Insert random UInt64 values into a column and create multiple partitions based on the value of number_of_partitions."""
    if node is None:
        node = self.context.node

    with By("Inserting random values into a column with uint64 datatype"):
        for i in range(1, number_of_partitions + 1):
            for parts in range(1, number_of_parts + 1):
                node.query(
                    f"INSERT INTO {table_name} (a, b, i) SELECT {i%4+bias}, {i}, rand64() FROM numbers({number_of_values})"
                )


@TestStep(Given)
def insert_date_data(
    self,
    table_name,
    number_of_partitions=5,
    node=None,
    bias=0,
):
    """Insert Date data into table."""
    if node is None:
        node = self.context.node

    with By("Inserting values into a column with Date datatype"):
        for i in range(1, number_of_partitions + 1):
            node.query(
                f"INSERT INTO {table_name} (timestamp) VALUES (toDate('2023-12-20')+{i}+{bias})"
            )
