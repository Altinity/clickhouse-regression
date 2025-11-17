"""
Helpers.queries contains functions that wrap SQL queries.
"""

import json

from testflows.core import *
from testflows.uexpect.uexpect import ExpectTimeoutError
from testflows.connect.shell import Command

from helpers.cluster import ClickHouseNode

# The use of JSONCompactEachRow with groupArray has the following benefits:
# 1. groupArray keeps the output on one line, for concise logs.
# 2. JSONCompactEachRow ensures that the output can be parsed as JSON.
# The extra [0] could be avoided with TSV format, but that does not guarantee valid JSON.


@TestStep(Given)
def get_cluster_nodes(self, cluster, node=None):
    """Get all nodes in a cluster."""

    if node is None:
        node = self.context.node

    result = node.query(
        f"SELECT host_name FROM system.clusters WHERE cluster = '{cluster}'", exitcode=0
    )

    nodes = [line.strip() for line in result.output.splitlines() if line.strip()]
    return nodes


@TestStep(When)
def select_all_ordered(self, table_name, node, order_by="p, i"):
    """Select all data from a table ordered by partition and index columns."""

    return node.query(
        f"SELECT * FROM {table_name} ORDER BY {order_by}", exitcode=0
    ).output.splitlines()


@TestStep(When)
def sync_replica(
    self, node: ClickHouseNode, table_name: str, raise_on_timeout=False, **kwargs
) -> Command:
    """Call SYSTEM SYNC REPLICA on the given node and table."""
    try:
        return node.query(f"SYSTEM SYNC REPLICA {table_name}", **kwargs)
    except (ExpectTimeoutError, TimeoutError):
        if raise_on_timeout:
            raise


@TestStep(When)
def optimize(
    self, node: ClickHouseNode, table_name: str, final=False, no_checks=False
) -> Command:
    """Apply OPTIMIZE on the given table and node."""
    q = f"OPTIMIZE TABLE {table_name}" + " FINAL" if final else ""
    return node.query(q, no_checks=no_checks, exitcode=0)


@TestStep(Given)
def get_column_names(self, node: ClickHouseNode, table_name: str, timeout=30) -> list:
    """Get a list of a table's column names."""
    r = node.query(
        f"SELECT groupArray(name) FROM system.columns WHERE table='{table_name}' FORMAT JSONCompactEachRow",
        timeout=timeout,
    )
    return json.loads(r.output)[0]


@TestStep
def get_active_parts(self, node: ClickHouseNode, table_name: str, timeout=30) -> list:
    """Get a list of active parts in a table."""
    r = node.query(
        f"SELECT groupArray(name) FROM system.parts WHERE table='{table_name}' and active=1 FORMAT JSONCompactEachRow",
        timeout=timeout,
    )
    return json.loads(r.output)[0]


@TestStep
def get_active_partition_ids(
    self, node: ClickHouseNode, table_name: str, timeout=30
) -> list:
    """Get a list of active partitions in a table."""
    r = node.query(
        f"SELECT groupArray(partition_id) FROM system.parts WHERE table='{table_name}' and active=1 FORMAT JSONCompactEachRow",
        timeout=timeout,
    )
    return json.loads(r.output)[0]


@TestStep
def get_row_count(
    self, node: ClickHouseNode, table_name: str, timeout=30, column: str = None
) -> int:
    """
    Get the number of rows in the given table.

    """
    if column is None:
        column = ""

    r = node.query(
        f"SELECT count({column}) FROM {table_name} FORMAT JSONCompactEachRow",
        exitcode=0,
        timeout=timeout,
    )
    return int(json.loads(r.output)[0])


@TestStep
def get_projections(self, node: ClickHouseNode, table_name: str) -> list:
    """
    Get a list of active projections for a given table.
    """
    r = node.query(
        f"SELECT groupArray(distinct(name)) FROM system.projection_parts WHERE table='{table_name}' and active FORMAT JSONCompactEachRow",
        exitcode=0,
    )
    return json.loads(r.output)[0]


@TestStep
def get_indexes(self, node: ClickHouseNode, table_name: str) -> list:
    """
    Get a list of secondary indexes for a given table.
    """
    r = node.query(
        f"SELECT groupArray(name) FROM system.data_skipping_indices WHERE table='{table_name}' FORMAT JSONCompactEachRow",
        exitcode=0,
    )
    return json.loads(r.output)[0]


@TestStep
def get_column_string(self, node: ClickHouseNode, table_name: str, timeout=30) -> str:
    """
    Get a string with column names and types.
    This converts the output from DESCRIBE TABLE to a string
    that can be passed into CREATE or INSERT.
    """
    r = node.query(
        f"DESCRIBE TABLE {table_name}",
        timeout=timeout,
    )
    return ",".join([l.strip() for l in r.output.splitlines()])


@TestStep(When)
def drop_column(self, node, table_name, column_name):
    """Drop a column from a table."""

    node.query(
        f"ALTER TABLE {table_name} DROP COLUMN {column_name}", exitcode=0, steps=True
    )
