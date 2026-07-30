"""Common helpers shared by every export_partition test.

The utilities here cover:

* Creating and tearing down the source MergeTree-family table the export
  reads from (``ReplicatedMergeTree`` or plain ``MergeTree``).
* Cheap lookups against ``system.parts`` and the export status system tables
  (``system.replicated_partition_exports`` or ``system.partition_exports``).

The experimental feature itself is enabled server-side via
``configs/clickhouse/config.d/export_partition.xml``
(``allow_experimental_export_merge_tree_partition``), so scenarios
don't need to pass per-query settings to use EXPORT PARTITION.
"""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

SOURCE_ENGINE_REPLICATED = "replicated"
SOURCE_ENGINE_PLAIN = "plain"


def source_engine(test=None):
    """Return ``self.context.source_engine`` (defaults to ``replicated``)."""
    if test is None:
        test = current()
    return getattr(test.context, "source_engine", SOURCE_ENGINE_REPLICATED)


def partition_exports_system_table(test=None):
    """System table that tracks EXPORT PARTITION for the current source engine."""
    if source_engine(test) == SOURCE_ENGINE_PLAIN:
        return "system.partition_exports"
    return "system.replicated_partition_exports"


def require_replicated_source(reason):
    """Skip unless ``self.context.source_engine`` is ``replicated``."""
    engine = source_engine()
    if engine != SOURCE_ENGINE_REPLICATED:
        skip(
            f"scenario is replicated-only: {reason} "
            f"(current source engine: {engine!r})"
        )


def _export_source_base_settings(extra_settings):
    base_settings = [
        "enable_block_number_column = 1",
        "enable_block_offset_column = 1",
    ]
    if extra_settings:
        base_settings.extend(extra_settings)
    return ", ".join(base_settings)


@TestStep(Given)
def create_export_source_table(
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
    """Create a source table for EXPORT PARTITION.

    Dispatches on ``self.context.source_engine``:

    * ``replicated`` (default): ``ReplicatedMergeTree`` with ZooKeeper path.
    * ``plain``: plain ``MergeTree`` (Altinity/ClickHouse#2032).

    The defaults match the ClickHouse integration tests: an ``(id, year)``
    schema partitioned by ``year`` with block number/offset columns enabled
    (required by the export scheduler).
    """
    if node is None:
        node = self.context.node

    if table_name is None:
        table_name = f"mt_{getuid()}"

    settings_str = _export_source_base_settings(extra_settings)
    cluster_clause = f"ON CLUSTER {on_cluster} " if on_cluster else ""

    if source_engine(self) == SOURCE_ENGINE_PLAIN:
        engine_clause = "ENGINE = MergeTree()"
    else:
        if zk_path is None:
            zk_path = f"/clickhouse/tables/{table_name}"
        engine_clause = (
            f"ENGINE = ReplicatedMergeTree('{zk_path}', '{replica_name}')"
        )

    query = f"""
        CREATE TABLE {table_name} {cluster_clause}({columns})
        {engine_clause}
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


# Backward-compatible alias — all existing call sites dispatch via context.
create_replicated_mergetree = create_export_source_table


@TestStep(Given)
def insert_data(self, table_name, values, node=None):
    """Insert a literal ``VALUES`` payload into the source table."""
    if node is None:
        node = self.context.node
    node.query(f"INSERT INTO {table_name} VALUES {values}")


def resolve_partition_ids(table_name, node, active_only=True):
    """Return sorted distinct ``partition_id`` values from ``system.parts``.

    Plain helper for use outside a TestFlows ``with`` block.  Calling a
    ``@TestStep``-decorated step directly returns an ``OK`` wrapper, not the
    step's return value.
    """
    active_filter = "AND active" if active_only else ""
    output = node.query(
        f"SELECT DISTINCT partition_id FROM system.parts "
        f"WHERE table = '{table_name}' AND database = currentDatabase() {active_filter}"
    ).output
    return sorted({row.strip() for row in output.splitlines() if row.strip()})


def resolve_first_partition_id(table_name, node, active_only=True):
    """Return one ``partition_id`` for ``table_name`` (see :func:`resolve_partition_ids`)."""
    ids = resolve_partition_ids(table_name, node, active_only)
    assert ids, error(f"No active partitions found for table {table_name}")
    return ids[0]


@TestStep(When)
def get_partition_ids(self, table_name, node=None, active_only=True):
    """Return the sorted list of distinct ``partition_id`` values for the given
    source table.

    The default ``active_only=True`` mirrors every existing PR test and filters
    out parts that are not currently active.
    """
    if node is None:
        node = self.context.node
    return resolve_partition_ids(table_name, node, active_only)


@TestStep(When)
def get_active_part_name(self, table_name, partition_id=None, node=None):
    """Return one active part ``name`` for ``table_name``.

    When ``partition_id`` is set, restrict to parts in that partition
    (the form used by ``EXPORT PART '…'`` on a partitioned table).
    """
    if node is None:
        node = self.context.node

    where = [
        f"table = '{table_name}'",
        "database = currentDatabase()",
        "active",
    ]
    if partition_id is not None:
        where.append(f"partition_id = '{partition_id}'")
    output = node.query(
        "SELECT name FROM system.parts WHERE "
        + " AND ".join(where)
        + " ORDER BY name LIMIT 1"
    ).output.strip()
    assert output, error(
        f"No active part found for table {table_name}"
        + (f" partition_id={partition_id!r}" if partition_id else "")
    )
    return output


@TestStep(When)
def first_partition_id(self, table_name, node=None):
    """Return a single partition_id for the source table.

    Fails the scenario if the source table has no active parts.
    """
    if node is None:
        node = self.context.node
    return resolve_first_partition_id(table_name, node)


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
    require_replicated_source(
        "SYSTEM SYNC REPLICA applies only to ReplicatedMergeTree sources"
    )
    node.query(f"SYSTEM SYNC REPLICA {table_name}")
