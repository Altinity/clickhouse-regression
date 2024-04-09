from testflows.core import *
from helpers.tables import *


@TestStep
def rename_detached_part(
    self, table_name, part_name, new_part_name, database="default", node=None
):
    """Rename a detached part."""
    if node is None:
        node = self.context.node

    node.command(
        f"mv /var/lib/clickhouse/data/{database}/{table_name}/detached/{part_name} /var/lib/clickhouse/data/{database}/{table_name}/detached/{new_part_name}"
    )


@TestStep
def create_table_on_cluster_with_data(
    self,
    table_name,
    cluster,
    engine="ReplicatedMergeTree",
    order_by="()",
    node=None,
    columns=None,
    config="graphite_rollup_example",
    sign="sign",
    version="id",
    number_of_rows=100000000,
    partition_by="tuple()",
):
    """Create a table on a specified cluster with data."""
    if node is None:
        node = self.context.node

    if columns is None:
        columns = [
            Column(name="id", datatype=Int32()),
            Column(name="a", datatype=Int32()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if "GraphiteMergeTree" in engine:
        engine = f"ReplicatedGraphiteMergeTree('{config}')"
    elif "VersionedCollapsingMergeTree" in engine:
        engine = f"ReplicatedVersionedCollapsingMergeTree({sign},{version})"
    elif "CollapsingMergeTree" in engine:
        engine = f"ReplicatedCollapsingMergeTree({sign})"

    create_table(
        name=table_name,
        cluster=cluster,
        order_by=order_by,
        node=node,
        engine=engine,
        columns=columns,
        partition_by=partition_by,
    )
    node.query(
        f"INSERT INTO {table_name} (id, a, sign) SELECT number, number, 1 FROM numbers({number_of_rows})"
    )


@TestStep
def create_MergeTree_table_with_data(
    self,
    table_name,
    engine="MergeTree",
    order_by="()",
    node=None,
    columns=None,
    config="graphite_rollup_example",
    sign="sign",
    version="id",
    number_of_rows=100000000,
    partition_by="tuple()",
):
    """Create a MergeTree table."""
    if node is None:
        node = self.context.node

    if columns is None:
        columns = [
            Column(name="id", datatype=Int32()),
            Column(name="a", datatype=Int32()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if engine == "GraphiteMergeTree":
        engine = f"GraphiteMergeTree('{config}')"
    elif engine == "VersionedCollapsingMergeTree":
        engine = f"VersionedCollapsingMergeTree({sign},{version})"
    elif engine == "CollapsingMergeTree":
        engine = f"CollapsingMergeTree({sign})"

    create_table(
        name=table_name,
        order_by=order_by,
        node=node,
        engine=engine,
        columns=columns,
        partition_by=partition_by,
    )
    node.query(
        f"INSERT INTO {table_name} (id, a, sign) SELECT number, number, 1 FROM numbers({number_of_rows})"
    )


@TestStep
def optimize_table(self, table_name, node=None):
    """Optimize a table."""
    if node is None:
        node = self.context.node

    node.query(f"OPTIMIZE TABLE {table_name} FINAL")


@TestStep
def update_table(self, table_name, update_column="a", node=None):
    """Update a table."""
    if node is None:
        node = self.context.node

    node.query(
        f"ALTER TABLE {table_name} UPDATE {update_column} = {update_column}+1 WHERE {update_column} > 0"
    )


@TestStep
def insert_data(self, table_name, number_of_rows, node=None):
    """Insert data into a table."""
    if node is None:
        node = self.context.node

    node.query(
        f"INSERT INTO {table_name} (id, a) SELECT number, number FROM numbers({number_of_rows})"
    )


@TestStep
def attach_partition_from(self, source_table, destination_table, partition, node=None):
    """Attach a partition from a source table to a destination table."""
    if node is None:
        node = self.context.node

    node.query(
        f"ALTER TABLE {destination_table} ATTACH PARTITION {partition} FROM {source_table}"
    )


@TestStep
def attach_partition(self, table_name, partition, node=None):
    """Attach a partition to a table."""
    if node is None:
        node = self.context.node

    node.query(f"ALTER TABLE {table_name} ATTACH PARTITION {partition}")


@TestStep
def detach_partition(self, table_name, partition, node=None):
    """Detach a partition from a table."""
    if node is None:
        node = self.context.node

    node.query(f"ALTER TABLE {table_name} DETACH PARTITION {partition}")


@TestStep
def attach_part(self, table_name, part_name, node=None):
    """Attach a part to a table from a detached directory."""
    if node is None:
        node = self.context.node

    node.query(f"ALTER TABLE {table_name} ATTACH PART '{part_name}'")


@TestStep
def detach_part(self, table_name, part_name, node=None):
    """Detach a part from a table."""
    if node is None:
        node = self.context.node

    node.query(f"ALTER TABLE {table_name} DETACH PART '{part_name}'")
