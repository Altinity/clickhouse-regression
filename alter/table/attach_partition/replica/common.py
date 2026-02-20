import json
import time

from testflows.asserts import error
from testflows.core import *
from testflows._core.flags import LAST_RETRY

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
    if_not_exists=True,
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
        f"INSERT INTO {table_name} {column_names} SELECT 1, {'rand(),'*(len(columns)-2)} 1 FROM numbers({rows})",
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
    with self.context.replica_operation_lock:
        if keep_one_replica:
            if (len(active_replicas) == 1) and (0 in active_replicas):
                skip("Can not delete last replica")
            elif 0 in active_replicas:
                self.context.nodes[0].query(f"DROP TABLE {table_name} SYNC", exitcode=0)
                active_replicas.remove(0)
        else:
            if 0 in active_replicas:
                self.context.nodes[0].query(f"DROP TABLE {table_name} SYNC", exitcode=0)
                active_replicas.remove(0)


@TestStep
def delete_replica_on_second_node(
    self, active_replicas, table_name, keep_one_replica=False
):
    """Delete the local copy of a replicated table on second node."""
    with self.context.replica_operation_lock:
        if keep_one_replica:
            if (len(active_replicas) == 1) and (1 in active_replicas):
                skip("Can not delete last replica")
            elif 1 in active_replicas:
                self.context.nodes[1].query(f"DROP TABLE {table_name} SYNC", exitcode=0)
                active_replicas.remove(1)
        else:
            if 1 in active_replicas:
                self.context.nodes[1].query(f"DROP TABLE {table_name} SYNC", exitcode=0)
                active_replicas.remove(1)


@TestStep
def delete_replica_on_third_node(
    self, active_replicas, table_name, keep_one_replica=False
):
    """Delete the local copy of a replicated table on third node."""
    with self.context.replica_operation_lock:
        if keep_one_replica:
            if (len(active_replicas) == 1) and (2 in active_replicas):
                skip("Can not delete last replica")
            elif 2 in active_replicas:
                self.context.nodes[2].query(f"DROP TABLE {table_name} SYNC", exitcode=0)
                active_replicas.remove(2)
        else:
            if 2 in active_replicas:
                self.context.nodes[2].query(f"DROP TABLE {table_name} SYNC", exitcode=0)
                active_replicas.remove(2)


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
    config="graphite_rollup_example",
    sign="sign",
    version="a",
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

    if "ReplicatedGraphiteMergeTree" in engine:
        engine = f"{engine}('/clickhouse/tables/{replica_path_suffix}', '{replica_name}', '{config}')"
    elif "ReplicatedVersionedCollapsingMergeTree" in engine:
        engine = f"{engine}('/clickhouse/tables/{replica_path_suffix}', '{replica_name}', {sign}, {version})"
    elif "ReplicatedCollapsingMergeTree" in engine:
        engine = f"{engine}('/clickhouse/tables/{replica_path_suffix}', '{replica_name}', {sign})"
    elif "Replicated" in engine:
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
        with self.context.replica_operation_lock:
            if 0 not in active_replicas:
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
        with self.context.replica_operation_lock:
            if 1 not in active_replicas:
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
        with self.context.replica_operation_lock:
            if 2 not in active_replicas:
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
                active_replicas.append(2)


@TestStep
def add_remove_replica_on_first_node(
    self, table_name, active_replicas, engine, delay_before_delete=None, order_by="tuple()"
):
    "Create replica on first node, wait less that 2 seconds and delete replica from the node."
    create_replica_on_first_node(
        table_name=table_name, active_replicas=active_replicas, engine=engine, order_by=order_by
    )

    if delay_before_delete is None:
        delay_before_delete = random.random() * 10

    time.sleep(delay_before_delete)

    delete_replica_on_first_node(
        table_name=table_name,
        active_replicas=active_replicas,
        keep_one_replica=True,
    )


@TestStep
def add_remove_replica_on_second_node(
    self, table_name, active_replicas, engine, delay_before_delete=None, order_by="tuple()"
):
    "Create replica on second node, wait less that 2 seconds and delete replica from the node."
    create_replica_on_second_node(
        table_name=table_name, active_replicas=active_replicas, engine=engine, order_by=order_by
    )

    if delay_before_delete is None:
        delay_before_delete = random.random() * 10

    time.sleep(delay_before_delete)

    delete_replica_on_second_node(
        table_name=table_name,
        active_replicas=active_replicas,
        keep_one_replica=True,
    )


@TestStep
def add_remove_replica_on_third_node(
    self, table_name, active_replicas, engine, delay_before_delete=None, order_by="tuple()"
):
    "Create replica on third node, wait less that 2 seconds and delete replica from the node."
    create_replica_on_third_node(
        table_name=table_name,
        active_replicas=active_replicas,
        engine=engine,
        order_by=order_by
    )

    if delay_before_delete is None:
        delay_before_delete = random.random() * 10

    time.sleep(delay_before_delete)

    delete_replica_on_third_node(
        table_name=table_name,
        active_replicas=active_replicas,
        keep_one_replica=True,
    )


@TestStep(Given)
def get_partition_list(self, table_name, node, exitcode=None, message=None):
    "Get list of partitions from system.parts table."
    partition_list_query = f"SELECT partition FROM system.parts WHERE table='{table_name}' FORMAT TabSeparated"
    partition_ids = sorted(
        list(
            set(
                node.query(
                    partition_list_query, exitcode=exitcode, message=message
                ).output.split()
            )
        )
    )
    return partition_ids


@TestStep
def attach_partition_from(self, source_table_name, destination_table_name):
    """Attach partition from source table to the destination table
    on random active node."""

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
    self,
    source_table_name,
    destination_table_name,
    node,
    source_table_engine,
    destination_table_engine,
):
    """Attach partition from source table to the destination table
    if source table exists on specified node."""
    try:
        query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION 1 FROM {source_table_name}"
        node.query(query)
        num_rows = node.query(
            f"SELECT count() from {destination_table_name} FORMAT TabSeparated"
        )

        for attempt in retries(timeout=30, delay=2):
            with attempt:
                if (
                    source_table_engine == "ReplicatedReplacingMergeTree"
                    or source_table_engine == "ReplicatedCollapsingMergeTree"
                    or source_table_engine == "ReplicatedGraphiteMergeTree"
                ):
                    values = [0, 1]
                    value = 1
                else:
                    values = [0, 10]
                    value = 10

                if attempt.kwargs["flags"] & LAST_RETRY:
                    assert int(num_rows.output) in values, error()
                    if int(num_rows.output) == 0:
                        return False
                else:
                    assert int(num_rows.output) == value, error()

        return True

    except Exception as e:
        # 60 - Table doesn't exist
        # 218 - Table is dropped or detached
        message = "DB::Exception: Table default.source"
        assert message in e.message and (
            "Code: 60" in e.message or "Code: 218" in e.message
        ), error()


@TestStep
def detach_partition_on_node(self, table_name, node, partition="1"):
    "Detach partition from table on specified node."
    query = f"ALTER TABLE {table_name} DETACH PARTITION {partition}"
    node.query(query)


@TestStep
def check_partition_was_attached(self, table_name, expected):
    "Check that partition was attached and data is the same on all nodes."
    data = None
    for node in self.context.nodes:
        if data is None:
            data = node.query(
                f"SELECT * FROM {table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
            )
            for attempt in retries(timeout=30, delay=2):
                with attempt:
                    assert data.output == expected
        else:
            current_data = node.query(
                f"SELECT * FROM {table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
            )
            for attempt in retries(timeout=30, delay=2):
                with attempt:
                    assert current_data.output == data.output == expected
