from testflows.core import *
from helpers.common import *
from helpers.tables import *


@TestStep
def create_database(self, database_name=None, node=None):
    if database_name is None:
        database_name = "database_" + getuid()
    if node is None:
        node = self.context.node
    node.query(f"CREATE DATABASE {database_name} ENGINE=Atomic")
    return database_name


@TestStep
def create_replicated_table_old(
    self, table, table_id=None, database_name="default", node=None
):
    if node is None:
        node = self.context.node
    if table_id is None:
        table_id = table
    node.query(
        f"""
        CREATE TABLE {database_name}.{table} (x UInt64) 
        ENGINE = ReplicatedMergeTree('/clickhouse/tables/{{shard}}/{{database}}/{table_id}', '{{replica}}') 
        ORDER BY x 
        SETTINGS index_granularity=8192
        """
    )


@TestStep(Given)
def create_replicated_table(
    self,
    table_name,
    engine="ReplicatedMergeTree",
    database_name="default",
    table_id=None,
    columns=None,
    order_by="tuple()",
    node=None,
    config="graphite_rollup_example",
    sign="sign",
    version="a",
):
    if node is None:
        node = self.context.node
    if table_id is None:
        table_id = table_name
    if columns is None:
        columns = [
            Column(name="time", datatype=DateTime()),
            Column(name="date", datatype=Date()),
            Column(name="extra", datatype=UInt64()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if engine == "ReplicatedGraphiteMergeTree":
        engine = f"ReplicatedGraphiteMergeTree('/clickhouse/tables/{{shard}}/{{database}}/{table_id}', '{{replica}}', '{config}')"
    elif engine == "ReplicatedVersionedCollapsingMergeTree":
        engine = f"ReplicatedVersionedCollapsingMergeTree('/clickhouse/tables/{{shard}}/{{database}}/{table_id}', '{{replica}}', {sign}, {version})"
    elif engine == "ReplicatedCollapsingMergeTree":
        engine = f"ReplicatedCollapsingMergeTree('/clickhouse/tables/{{shard}}/{{database}}/{table_id}', '{{replica}}', {sign})"
    else:
        engine = f"{engine}('/clickhouse/tables/{{shard}}/{{database}}/{table_id}', '{{replica}}')"

    table_name = f"{database_name}.{table_name}"
    create_table(
        node=node,
        engine=engine,
        name=table_name,
        columns=columns,
        order_by=order_by,
    )


@TestStep
def attach_table_UUID(
    self,
    table,
    table_id,
    uuid,
    engine="ReplicatedMergeTree",
    database_name="default",
    order_by="tuple()",
    node=None,
    exitcode=None,
    message=None,
    columns=None,
    config="graphite_rollup_example",
    sign="sign",
    version="a",
):
    if node is None:
        node = self.context.node
    if columns is None:
        columns = [
            Column(name="time", datatype=DateTime()),
            Column(name="date", datatype=Date()),
            Column(name="extra", datatype=UInt64()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]
    columns_def = "(" + ",".join([column.full_definition() for column in columns]) + ")"

    if engine == "ReplicatedGraphiteMergeTree":
        engine = f"ReplicatedGraphiteMergeTree('/clickhouse/tables/{{shard}}/{{database}}/{table_id}', '{{replica}}', '{config}')"
    elif engine == "ReplicatedVersionedCollapsingMergeTree":
        engine = f"ReplicatedVersionedCollapsingMergeTree('/clickhouse/tables/{{shard}}/{{database}}/{table_id}', '{{replica}}', {sign}, {version})"
    elif engine == "ReplicatedCollapsingMergeTree":
        engine = f"ReplicatedCollapsingMergeTree('/clickhouse/tables/{{shard}}/{{database}}/{table_id}', '{{replica}}', {sign})"
    else:
        engine = f"{engine}('/clickhouse/tables/{{shard}}/{{database}}/{table_id}', '{{replica}}')"

    node.query(
        f"""
        ATTACH TABLE {database_name}.{table} UUID '{uuid}' {columns_def}
        ENGINE={engine}
        ORDER BY {order_by}
        SETTINGS index_granularity = 8192
        """,
        exitcode=exitcode,
        message=message,
    )
