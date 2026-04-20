"""Common helpers shared by every export_partition test.

The utilities here cover:

* Creating and tearing down the source ``ReplicatedMergeTree`` table the
  export reads from.
* Cheap lookups against ``system.parts`` /
  ``system.replicated_partition_exports`` used by almost every scenario.

The experimental feature itself is enabled server-side via
``configs/clickhouse/config.d/export_partition.xml``
(``enable_experimental_export_merge_tree_partition_feature``), so scenarios
don't need to pass per-query settings to use EXPORT PARTITION.
"""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid


@TestStep(Given)
def create_replicated_mergetree(
    self,
    table_name=None,
    columns="id Int64, year Int32",
    partition_by="year",
    order_by="tuple()",
    zk_path=None,
    replica_name="replica1",
    extra_settings=None,
    node=None,
    on_cluster=None,
    cleanup=True,
):
    """Create a ReplicatedMergeTree source table used by EXPORT PARTITION.

    The defaults match the ClickHouse integration tests in the PR: an
    ``(id, year)`` schema partitioned by ``year`` with the block number/offset
    columns enabled (required by the export scheduler).

    Args:
        table_name: Name for the source table. Defaults to a unique name.
        columns: Column list for the ``CREATE TABLE`` body.
        partition_by: Expression used for ``PARTITION BY``.
        order_by: Expression used for ``ORDER BY``.
        zk_path: ZooKeeper path for the replicated table. Defaults to
            ``/clickhouse/tables/<table_name>``.
        replica_name: Replica identifier used in ``ReplicatedMergeTree``.
        extra_settings: Optional list of ``"key = value"`` strings appended to
            the default SETTINGS clause.
        node: ClickHouse node to create the table on (defaults to
            ``self.context.node``).
        on_cluster: Optional cluster name to attach ``ON CLUSTER <name>``.
        cleanup: If ``True`` the table is dropped with ``SYNC`` in ``Finally``.
    """
    if node is None:
        node = self.context.node

    if table_name is None:
        table_name = f"mt_{getuid()}"

    if zk_path is None:
        zk_path = f"/clickhouse/tables/{table_name}"

    base_settings = [
        "enable_block_number_column = 1",
        "enable_block_offset_column = 1",
    ]
    if extra_settings:
        base_settings.extend(extra_settings)
    settings_str = ", ".join(base_settings)

    cluster_clause = f"ON CLUSTER {on_cluster} " if on_cluster else ""

    query = f"""
        CREATE TABLE {table_name} {cluster_clause}({columns})
        ENGINE = ReplicatedMergeTree('{zk_path}', '{replica_name}')
        PARTITION BY {partition_by}
        ORDER BY {order_by}
        SETTINGS {settings_str}
        """

    try:
        node.query(query)
        yield table_name
    finally:
        if cleanup:
            with Finally(f"drop source table {table_name}"):
                drop_query = f"DROP TABLE IF EXISTS {table_name}"
                if on_cluster:
                    drop_query += f" ON CLUSTER {on_cluster}"
                drop_query += " SYNC"
                node.query(drop_query)


@TestStep(Given)
def insert_data(self, table_name, values, node=None):
    """Insert a literal ``VALUES`` payload into the source table."""
    if node is None:
        node = self.context.node
    node.query(f"INSERT INTO {table_name} VALUES {values}")


@TestStep(When)
def get_partition_ids(self, table_name, node=None, active_only=True):
    """Return the sorted list of distinct ``partition_id`` values for the given
    source table.

    The default ``active_only=True`` mirrors every existing PR test and filters
    out parts that are not currently active.
    """
    if node is None:
        node = self.context.node

    active_filter = "AND active" if active_only else ""
    output = node.query(
        f"SELECT DISTINCT partition_id FROM system.parts "
        f"WHERE table = '{table_name}' AND database = currentDatabase() {active_filter}"
    ).output
    return sorted({row.strip() for row in output.splitlines() if row.strip()})


@TestStep(When)
def first_partition_id(self, table_name, node=None):
    """Return a single partition_id for the source table.

    Fails the scenario if the source table has no active parts.
    """
    ids = get_partition_ids(table_name=table_name, node=node)
    assert ids, error(f"No active partitions found for table {table_name}")
    return ids[0]


@TestStep(When)
def count_rows(self, table_name, where=None, node=None):
    """Return ``SELECT count() FROM <table> [WHERE <where>]`` as an int."""
    if node is None:
        node = self.context.node
    query = f"SELECT count() FROM {table_name}"
    if where:
        query += f" WHERE {where}"
    return int(node.query(query).output.strip())


@TestStep(Given)
def sync_replica(self, table_name, node):
    """Run ``SYSTEM SYNC REPLICA`` on the given node for a replicated table."""
    node.query(f"SYSTEM SYNC REPLICA {table_name}")
