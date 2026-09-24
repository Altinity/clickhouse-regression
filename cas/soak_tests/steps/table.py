from testflows.core import *

from helpers.common import getuid

CLUSTER = "replicated_cluster"
DATABASE = "ca_soak"

DDL_TEMPLATE = """
CREATE TABLE {table} ON CLUSTER {cluster}
(
    op_id UInt64, writer UInt16, bucket UInt16, k UInt64, ts DateTime64(3),
    version UInt32, v Int64, payload String, row_fp UInt64
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{zk_name}', '{{replica}}')
PARTITION BY toYYYYMMDD(ts)
ORDER BY (bucket, k, op_id)
TTL toDateTime(ts) + INTERVAL 90 MINUTE DELETE
SETTINGS storage_policy='ca', min_bytes_for_wide_part=0, min_rows_for_wide_part=0,
         search_orphaned_parts_disks='local'
""".strip()


@TestStep(Given)
def soak_database(self, node=None):
    """Ensure the dedicated soak database exists on both replicas."""
    if node is None:
        node = self.context.node
    node.query(
        f"CREATE DATABASE IF NOT EXISTS {DATABASE} ON CLUSTER {CLUSTER}"
    )
    return DATABASE


@TestStep(Given)
def soak_table(self, name=None, node=None):
    """Create a ReplicatedMergeTree on storage_policy='ca' matching the soak DDL."""
    if node is None:
        node = self.context.node
    soak_database(node=node)
    short = name or f"t_{getuid()}"
    table = f"{DATABASE}.{short}"
    node.query(f"DROP TABLE IF EXISTS {table} ON CLUSTER {CLUSTER} SYNC")
    node.query(
        DDL_TEMPLATE.format(table=table, cluster=CLUSTER, zk_name=short)
    )
    try:
        yield table
    finally:
        with Finally("drop the soak table"):
            node.query(f"DROP TABLE IF EXISTS {table} ON CLUSTER {CLUSTER} SYNC")
