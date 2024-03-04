import json

from testflows.asserts import error
from testflows.core import *

from helpers.tables import *


@TestStep
def insert_random(
    self,
    node,
    table_name,
    rows: int = 1000,
    columns: list = None,
):
    """Insert random UInt32 data to the table."""

    if columns == None:
        columns = ["a", "b", "c", "extra", "sign"]

    column_names = f"({','.join(columns)})"

    node.query(
        f"INSERT INTO {table_name} {column_names} SELECT {'rand(),'*(len(columns)-1)} 1 FROM numbers({rows})",
        exitcode=0,
    )


@TestStep
def get_row_count(self, node, table_name):
    """Get the number of rows in the given table."""
    r = node.query(
        f"SELECT count() FROM {table_name} FORMAT JSON",
        exitcode=0,
    )
    return int(json.loads(r.output)["data"][0]["count()"])


@TestStep(Then)
def assert_row_count(self, node, table_name: str, rows: int = 1000000):
    """Assert that the number of rows in a table is as expected."""
    if node is None:
        node = current().context.node

    actual_count = get_row_count(node=node, table_name=table_name)
    assert rows == actual_count, error()


@TestStep
def delete_one_replica(self, node, table_name):
    """Delete the local copy of a replicated table."""
    r = node.query(f"DROP TABLE IF EXISTS {table_name} SYNC", exitcode=0)
    return r


@TestStep(Given)
def create_one_replica(
    self,
    node,
    table_name,
    partition_by=None,
    replica_path_suffix=None,
    replica_name="{replica}",
    columns=None,
    engine="ReplicatedMergeTree",
    order_by="tuple()",
):
    """
    Create a simple replicated table on the given node.
    Call multiple times with the same table name and different nodes
    to create multiple replicas.
    """
    if columns is None:
        columns = [
            Column(name="a", datatype=UInt32()),
            Column(name="b", datatype=UInt16()),
            Column(name="c", datatype=UInt16()),
            Column(name="extra", datatype=UInt64()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if replica_path_suffix is None:
        replica_path_suffix = table_name

    with Given("I create table on specified node"):
        query = create_table(
            name=table_name,
            columns=columns,
            engine=f"{engine}('/clickhouse/tables/{replica_path_suffix}', '{replica_name}')",
            if_not_exists=True,
            partition_by=partition_by,
            node=node,
            order_by=order_by,
        )

    return query


@TestStep
def create_one_replica_on_random_node(self, table_name, nodes=None):
    if nodes is None:
        nodes = self.context.nodes


@TestStep
def get_partition_list(self, table_name, node):
    partition_list_query = f"SELECT partition_id FROM system.parts WHERE table='{table_name}' ORDER BY partition_id"
    partition_ids = sorted(list(set(node.query(partition_list_query).output.split())))
    return partition_ids


@TestStep
def attach_partition_from(self, source_table_name, destination_table_name, node):
    with Given("I get partition list"):
        partition_ids = get_partition_list(table_name=source_table_name, node=node)

    with Then("I attach all partitions from the source table to the destination table"):
        for partition_id in partition_ids:
            query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION {partition_id} FROM {source_table_name}"
            node.query(query)
