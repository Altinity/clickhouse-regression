import json

from testflows.asserts import error
from testflows.core import *

from helpers.tables import *


@TestStep(Given)
def create_table(
    self,
    columns,
    engine="MergeTree",
    table_name=None,
    order_by=None,
    partition_by=None,
    primary_key=None,
    comment=None,
    as_select=None,
    settings=None,
    query_settings=None,
    empty=None,
    if_not_exists=False,
    node=None,
    cluster=None,
):
    """Create a table with specified table_name and engine."""
    if settings is None:
        settings = [("allow_suspicious_low_cardinality_types", 1)]

    if table_name is None:
        table_name = f"table_{getuid()}"

    if node is None:
        node = current().context.node

    columns_def = "(" + ",".join([column.full_definition() for column in columns]) + ")"

    if if_not_exists:
        if_not_exists = "IF NOT EXISTS "
    else:
        if_not_exists = ""

    if cluster is not None:
        on_cluster = f" ON CLUSTER {cluster}"
    else:
        on_cluster = ""

    with By(f"creating table {table_name}"):
        query = (
            f"CREATE TABLE {if_not_exists}{table_name}{on_cluster} {columns_def}\n"
            f"ENGINE = {engine}"
        )
        if primary_key is not None:
            query += f"\nPRIMARY KEY {primary_key}"

        if partition_by is not None:
            query += f"\nPARTITION BY {partition_by}"

        if order_by is not None:
            query += f"\nORDER BY {order_by}"

        if comment is not None:
            query += f"\nCOMMENT '{comment}'"

        if empty is not None:
            query += f"\nEMPTY AS {empty}"

        if as_select is not None:
            query += f"\nAS SELECT {as_select}"
        if query_settings is not None:
            query += f"\nSETTINGS {query_settings}"

        node.query(
            query,
            settings=settings,
        )


@TestStep
def insert_random(
    self,
    node,
    table_name,
    rows: int = 10,
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
def insert_to_random_replica(
    self,
    table_name,
    active_replicas,
    nodes=None,
    rows: int = 10,
    columns: list = None,
):
    """Insert random UInt32 data to the table on random active node."""

    if columns is None:
        columns = ["a", "b", "c", "extra", "sign"]

    if nodes is None:
        nodes = self.context.nodes

    column_names = f"({','.join(columns)})"

    if len(active_replicas) > 0:
        node_num = random.choice(active_replicas)
        node = nodes[node_num]
        node.query(
            f"INSERT INTO {table_name} {column_names} SELECT {'rand(),'*(len(columns)-1)} 1 FROM numbers({rows})",
            exitcode=0,
        )
        # node.query(f"SYSTEM SYNC REPLICA {table_name} PULL")
        self.context.num_inserted_rows += rows
    else:
        skip("No active replicas to insert data")


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


@TestStep
def delete_replica_on_first_node(
    self, table_name, active_replicas, keep_one_replica=False
):
    """Delete the local copy of a replicated table on first node."""
    if keep_one_replica:
        if len(active_replicas) == 0:
            skip("Can not delete last replica")

    r = self.context.nodes[0].query(
        f"DROP TABLE IF EXISTS {table_name} SYNC", exitcode=0
    )

    if 0 in active_replicas:
        active_replicas.remove(0)

    if len(active_replicas) == 0:
        self.context.num_inserted_rows = 0
    return r


@TestStep
def delete_replica_on_second_node(
    self, active_replicas, table_name, keep_one_replica=False
):
    """Delete the local copy of a replicated table on second node."""
    if keep_one_replica:
        if len(active_replicas) == 0:
            skip("Can not delete last replica")

    r = self.context.nodes[1].query(
        f"DROP TABLE IF EXISTS {table_name} SYNC", exitcode=0
    )

    if 1 in active_replicas:
        active_replicas.remove(1)

    if len(active_replicas) == 0:
        self.context.num_inserted_rows = 0
    return r


@TestStep
def delete_replica_on_third_node(
    self, active_replicas, table_name, keep_one_replica=False
):
    """Delete the local copy of a replicated table on third node."""
    if keep_one_replica:
        if len(active_replicas) == 0:
            skip("Can not delete last replica")

    r = self.context.nodes[2].query(
        f"DROP TABLE IF EXISTS {table_name} SYNC", exitcode=0
    )

    if 2 in active_replicas:
        active_replicas.remove(2)

    if len(active_replicas) == 0:
        self.context.num_inserted_rows = 0
    return r


@TestStep(Given)
def create_one_replica(
    self,
    node,
    table_name,
    partition_by="a",
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

    if "Replicated" in engine:
        engine = (
            f"{engine}('/clickhouse/tables/{replica_path_suffix}', '{replica_name}')"
        )

    with Given("I create table on specified node"):
        query = create_table(
            table_name=table_name,
            columns=columns,
            engine=engine,
            if_not_exists=True,
            partition_by=partition_by,
            node=node,
            order_by=order_by,
        )

    return query


@TestStep
def create_replica_on_first_node(
    self,
    table_name,
    active_replicas,
    partition_by="a",
    replica_path_suffix=None,
    replica_name="{replica}",
    columns=None,
    engine="ReplicatedMergeTree",
    order_by="tuple()",
):
    with Given("I create replica on first node"):
        create_one_replica(
            node=self.context.nodes[0],
            table_name=table_name,
            partition_by=partition_by,
            replica_path_suffix=replica_path_suffix,
            replica_name=replica_name,
            columns=columns,
            engine=engine,
            order_by=order_by,
        )

    if 0 not in active_replicas:
        active_replicas.append(0)


@TestStep
def create_replica_on_second_node(
    self,
    table_name,
    active_replicas,
    partition_by="a",
    replica_path_suffix=None,
    replica_name="{replica}",
    columns=None,
    engine="ReplicatedMergeTree",
    order_by="tuple()",
):
    with Given("I create replica on second node"):
        create_one_replica(
            node=self.context.nodes[1],
            table_name=table_name,
            partition_by=partition_by,
            replica_path_suffix=replica_path_suffix,
            replica_name=replica_name,
            columns=columns,
            engine=engine,
            order_by=order_by,
        )

    if 1 not in active_replicas:
        active_replicas.append(1)


@TestStep
def create_replica_on_third_node(
    self,
    table_name,
    active_replicas,
    partition_by="a",
    replica_path_suffix=None,
    replica_name="{replica}",
    columns=None,
    engine="ReplicatedMergeTree",
    order_by="tuple()",
):
    with Given("I create replica on third node"):
        create_one_replica(
            node=self.context.nodes[2],
            table_name=table_name,
            partition_by=partition_by,
            replica_path_suffix=replica_path_suffix,
            replica_name=replica_name,
            columns=columns,
            engine=engine,
            order_by=order_by,
        )

    if 2 not in active_replicas:
        active_replicas.append(2)


@TestStep
def get_partition_list(self, table_name, node):
    partition_list_query = (
        f"SELECT partition FROM system.parts WHERE table='{table_name}'"
    )
    partition_ids = sorted(list(set(node.query(partition_list_query).output.split())))
    return partition_ids


@TestStep
def attach_partition_from(self, source_table_name, destination_table_name):
    if len(self.context.active_replicas) > 0:
        with Given("I choose random active node"):
            node_num = random.choice(self.context.active_replicas)
            node = self.context.nodes[node_num]

        with And("I track number of attached rows"):
            self.context.total_attached_rows += self.context.num_inserted_rows

        with And("I get partition list"):
            partition_ids = get_partition_list(table_name=source_table_name, node=node)

        with Then(
            "I attach all partitions from the source table to the destination table"
        ):
            for partition_id in partition_ids:
                query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION {partition_id} FROM {source_table_name}"
                node.query(query)
    else:
        skip("No active nodes to perform attach")


@TestStep
def attach_partition_from_on_node(
    self, source_table_name, destination_table_name, node
):
    with Given("I track number of attached rows"):
        self.context.total_attached_rows += self.context.num_inserted_rows

    try:
        with And("I get partition list"):
            partition_ids = get_partition_list(table_name=source_table_name, node=node)

        with Then(
            "I attach all partitions from the source table to the destination table"
        ):
            for partition_id in partition_ids:
                query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION {partition_id} FROM {source_table_name}"
                node.query(query)

    except:
        self.context.total_attached_rows -= self.context.num_inserted_rows