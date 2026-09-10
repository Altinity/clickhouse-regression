"""Table create/drop helpers for CAS MergeTree, ReplicatedMergeTree, Distributed."""

from testflows.core import *

from cas.tests.steps.disk import (
    REPLICATED_CLUSTER,
    SHARDED_CLUSTER,
    storage_settings,
)

DEFAULT_COLUMNS = "p UInt8, i UInt64"
DEFAULT_PARTITION_BY = "p"
DEFAULT_ORDER_BY = "i"


@TestStep(Given)
@Name("create a CAS MergeTree table")
def create_cas_merge_tree_table(
    self,
    table_name,
    node=None,
    columns=DEFAULT_COLUMNS,
    partition_by=DEFAULT_PARTITION_BY,
    order_by=DEFAULT_ORDER_BY,
    pool_prefix=None,
    server_root_id=None,
    policy=None,
    drop_sync=True,
):
    """Create a non-replicated MergeTree on CAS (policy or inline pool)."""
    if node is None:
        node = self.context.node

    settings = storage_settings(
        self,
        pool_prefix=pool_prefix,
        server_root_id=server_root_id,
        node=node,
        policy=policy or "cas_policy",
    )

    node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")
    node.query(
        f"""
        CREATE TABLE {table_name}
        (
            {columns}
        )
        ENGINE = MergeTree
        PARTITION BY {partition_by}
        ORDER BY {order_by}
        {settings}
        """
    )

    try:
        yield table_name

    finally:
        with Finally(f"drop {table_name}"):
            suffix = " SYNC" if drop_sync else ""
            node.query(f"DROP TABLE IF EXISTS {table_name}{suffix}")


@TestStep(Given)
def create_cas_partitioned_table(
    self,
    table_name,
    pool_prefix,
    partition_by=DEFAULT_PARTITION_BY,
    order_by=DEFAULT_ORDER_BY,
    node=None,
    server_root_id=None,
):
    """Create a MergeTree table on a shared CAS pool."""
    if node is None:
        node = self.context.node

    settings = storage_settings(
        self, pool_prefix=pool_prefix, server_root_id=server_root_id, node=node
    )

    node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")
    node.query(
        f"""
        CREATE TABLE {table_name}
        (
            {DEFAULT_COLUMNS}
        )
        ENGINE = MergeTree
        PARTITION BY {partition_by}
        ORDER BY {order_by}
        {settings}
        """
    )

    try:
        yield table_name

    finally:
        with Finally(f"drop {table_name}"):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestStep(Given)
def create_replicated_cas_table(
    self,
    table_name,
    nodes=None,
    columns=DEFAULT_COLUMNS,
    partition_by=DEFAULT_PARTITION_BY,
    order_by=DEFAULT_ORDER_BY,
    pool_prefix=None,
    policy=None,
    replication_path=None,
    table_uuid=None,
    disk_name=None,
    drop_sync=True,
    extra_settings=None,
):
    """Create the same ReplicatedMergeTree on each node, sharing one ZK path.

    When ``pool_prefix`` is set, every replica gets an inline CAS disk in that
    pool with a distinct ``server_root_id``. Otherwise the named storage policy
    is used (shared ``cas_disk`` endpoint).

    ``extra_settings`` is an optional list of ``name = value`` fragments
    appended to the disk / policy ``SETTINGS`` clause.
    """
    if nodes is None:
        nodes = self.context.nodes

    if replication_path is None:
        replication_path = f"/clickhouse/tables/{table_name}"

    for node in nodes:
        node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")

    for replica_number, node in enumerate(nodes, start=1):
        if pool_prefix is not None:
            settings = storage_settings(
                self,
                pool_prefix=pool_prefix,
                server_root_id=f"cas-{table_name}-{node.name}",
                node=node,
                disk_name=disk_name,
            )
        else:
            settings = storage_settings(self, policy=policy or "cas_policy")

        if extra_settings:
            settings = f"{settings}, {', '.join(extra_settings)}"

        uuid_clause = f"UUID '{table_uuid}'" if table_uuid else ""

        node.query(
            f"""
            CREATE TABLE {table_name} {uuid_clause}
            (
                {columns}
            )
            ENGINE = ReplicatedMergeTree(
                '{replication_path}',
                'replica{replica_number}'
            )
            PARTITION BY {partition_by}
            ORDER BY {order_by}
            {settings}
            """
        )

    try:
        yield table_name

    finally:
        with Finally(f"drop replicated {table_name} on all replicas"):
            suffix = " SYNC" if drop_sync else ""
            for node in nodes:
                node.query(f"DROP TABLE IF EXISTS {table_name}{suffix}", no_checks=True)


@TestStep(Given)
@Name("create a ReplicatedMergeTree on the local disk on every replica")
def create_replicated_local_table(
    self,
    table_name,
    nodes=None,
    columns=DEFAULT_COLUMNS,
    partition_by=DEFAULT_PARTITION_BY,
    order_by=DEFAULT_ORDER_BY,
    replication_path=None,
    table_uuid=None,
    drop_sync=True,
):
    """Create the same ReplicatedMergeTree on each node, on the local disk.

    The suite default policy is local; ``SETTINGS disk = 'default'`` still
    names that disk explicitly so a later config change cannot put this
    control table on CAS.
    """
    if nodes is None:
        nodes = self.context.nodes

    if replication_path is None:
        replication_path = f"/clickhouse/tables/{table_name}"

    for node in nodes:
        node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")

    uuid_clause = f"UUID '{table_uuid}'" if table_uuid else ""

    for replica_number, node in enumerate(nodes, start=1):
        node.query(
            f"""
            CREATE TABLE {table_name} {uuid_clause}
            (
                {columns}
            )
            ENGINE = ReplicatedMergeTree(
                '{replication_path}',
                'replica{replica_number}'
            )
            PARTITION BY {partition_by}
            ORDER BY {order_by}
            SETTINGS disk = 'default'
            """
        )

    try:
        yield table_name
    finally:
        with Finally(f"drop replicated {table_name} on all replicas"):
            suffix = " SYNC" if drop_sync else ""
            for node in nodes:
                node.query(f"DROP TABLE IF EXISTS {table_name}{suffix}", no_checks=True)


@TestStep(Given)
def create_replicated_cas_table_on_cluster(
    self,
    table_name,
    cluster=REPLICATED_CLUSTER,
    node=None,
    nodes=None,
    columns=DEFAULT_COLUMNS,
    partition_by=DEFAULT_PARTITION_BY,
    order_by=DEFAULT_ORDER_BY,
    policy="cas_policy",
    replication_path=None,
    drop_sync=True,
):
    """Create one ReplicatedMergeTree across ``cluster`` in a single DDL.

    Unlike creating the table node by node, ON CLUSTER gives every replica the
    same table UUID, which is what a real replicated deployment looks like. The
    named CAS policy keeps the replicas on one shared pool while each server
    keeps its own ``server_root_id``.
    """
    if node is None:
        node = self.context.node

    if nodes is None:
        nodes = self.context.nodes

    if replication_path is None:
        replication_path = f"/clickhouse/tables/{table_name}"

    settings = storage_settings(self, policy=policy)

    node.query(f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster} SYNC")
    node.query(
        f"""
        CREATE TABLE {table_name} ON CLUSTER {cluster}
        (
            {columns}
        )
        ENGINE = ReplicatedMergeTree(
            '{replication_path}',
            '{{replica}}'
        )
        PARTITION BY {partition_by}
        ORDER BY {order_by}
        {settings}
        """
    )

    try:
        yield table_name
    finally:
        with Finally(f"drop replicated {table_name} on {cluster}"):
            suffix = " SYNC" if drop_sync else ""
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster}{suffix}",
                no_checks=True,
            )


@TestStep(Given)
@Name("create a ReplicatedMergeTree on CAS with a per-replica pool")
def create_replicated_cas_table_cross_pool(
    self,
    table_name,
    pool_prefixes,
    nodes=None,
    columns=DEFAULT_COLUMNS,
    partition_by=DEFAULT_PARTITION_BY,
    order_by=DEFAULT_ORDER_BY,
    replication_path=None,
    drop_sync=True,
):
    """Create RMT replicas that deliberately mount *different* CAS pools.

    Used to prove cross-pool fetch falls back to byte copy.
    ``pool_prefixes`` must align with ``nodes``.
    """
    if nodes is None:
        nodes = self.context.nodes

    assert len(pool_prefixes) == len(
        nodes
    ), "pool_prefixes and nodes must have the same length"

    if replication_path is None:
        replication_path = f"/clickhouse/tables/{table_name}"

    for node in nodes:
        node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")

    for replica_number, (node, pool_prefix) in enumerate(
        zip(nodes, pool_prefixes), start=1
    ):
        settings = storage_settings(
            self,
            pool_prefix=pool_prefix,
            server_root_id=f"cas-{table_name}-{node.name}",
            node=node,
        )
        node.query(
            f"""
            CREATE TABLE {table_name}
            (
                {columns}
            )
            ENGINE = ReplicatedMergeTree(
                '{replication_path}',
                'replica{replica_number}'
            )
            PARTITION BY {partition_by}
            ORDER BY {order_by}
            {settings}
            """
        )

    try:
        yield table_name
    finally:
        with Finally(f"drop cross-pool replicated {table_name}"):
            suffix = " SYNC" if drop_sync else ""
            for node in nodes:
                node.query(f"DROP TABLE IF EXISTS {table_name}{suffix}", no_checks=True)


@TestStep(Given)
@Name("create local CAS MergeTree tables on every shard")
def create_sharded_local_cas_tables(
    self,
    table_name,
    cluster=SHARDED_CLUSTER,
    node=None,
    columns=DEFAULT_COLUMNS,
    partition_by=DEFAULT_PARTITION_BY,
    order_by=DEFAULT_ORDER_BY,
    policy="cas_policy",
    drop_sync=True,
):
    """Create identical local MergeTree tables on each shard via ON CLUSTER."""
    if node is None:
        node = self.context.node

    settings = storage_settings(self, policy=policy)
    node.query(f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster} SYNC")
    node.query(
        f"""
        CREATE TABLE {table_name} ON CLUSTER {cluster}
        (
            {columns}
        )
        ENGINE = MergeTree
        PARTITION BY {partition_by}
        ORDER BY {order_by}
        {settings}
        """
    )

    try:
        yield table_name
    finally:
        with Finally(f"drop sharded local {table_name}"):
            suffix = " SYNC" if drop_sync else ""
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster}{suffix}",
                no_checks=True,
            )


@TestStep(When)
@Name("insert into a Distributed table and wait for the fan-out")
def insert_into_distributed(self, table_name, select, node=None):
    """Insert through a Distributed table, waiting for shards to receive rows.

    Distributed inserts are background by default, so without foreground mode
    a following SELECT can legitimately see fewer rows.
    """
    if node is None:
        node = self.context.node

    node.query(
        f"INSERT INTO {table_name} {select}",
        settings=[("distributed_foreground_insert", 1)],
    )
    node.query(f"SYSTEM FLUSH DISTRIBUTED {table_name}")


@TestStep(Given)
@Name("create a Distributed table over sharded CAS locals")
def create_distributed_over_cas(
    self,
    distributed_table_name,
    local_table_name,
    cluster=SHARDED_CLUSTER,
    sharding_key="i",
    database="default",
    node=None,
    on_cluster=False,
    drop_sync=True,
):
    """Create a Distributed table pointing at local CAS tables on ``cluster``.

    With ``on_cluster`` the Distributed table itself is created on every node,
    so any node can serve the fan-out query.
    """
    if node is None:
        node = self.context.node

    clause = f" ON CLUSTER {cluster}" if on_cluster else ""

    node.query(f"DROP TABLE IF EXISTS {distributed_table_name}{clause} SYNC")
    node.query(
        f"""
        CREATE TABLE {distributed_table_name}{clause} AS {local_table_name}
        ENGINE = Distributed(
            {cluster},
            {database},
            {local_table_name},
            {sharding_key}
        )
        """
    )

    try:
        yield distributed_table_name
    finally:
        with Finally(f"drop distributed {distributed_table_name}"):
            suffix = " SYNC" if drop_sync else ""
            node.query(
                f"DROP TABLE IF EXISTS {distributed_table_name}{clause}{suffix}",
                no_checks=True,
            )
