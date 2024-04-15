"""
Helpers.queries contains functions that wrap  SQL queries.
"""

import json

from testflows.core import *
from testflows.uexpect.uexpect import ExpectTimeoutError
from testflows.connect.shell import Command

from helpers.cluster import ClickHouseNode


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


@TestStep
def get_column_names(self, node: ClickHouseNode, table_name: str, timeout=30) -> list:
    """Get a list of a table's column names."""
    r = node.query(
        f"DESCRIBE TABLE {table_name} FORMAT JSONColumns",
        timeout=timeout,
    )
    return json.loads(r.output)["name"]


@TestStep
def get_active_parts(self, node: ClickHouseNode, table_name: str, timeout=30) -> list:
    """Get a list of active parts in a table."""
    r = node.query(
        f"SELECT name FROM system.parts WHERE table='{table_name}' and active=1 FORMAT JSONColumns",
        timeout=timeout,
    )
    return json.loads(r.output)["name"]


@TestStep
def get_active_partition_ids(
    self, node: ClickHouseNode, table_name: str, timeout=30
) -> list:
    """Get a list of active partitions in a table."""
    r = node.query(
        f"SELECT partition_id FROM system.parts WHERE table='{table_name}' and active=1 FORMAT JSONColumns",
        timeout=timeout,
    )
    return json.loads(r.output)["partition_id"]


@TestStep
def get_row_count(self, node: ClickHouseNode, table_name: str, timeout=30) -> int:
    """Get the number of rows in the given table."""
    r = node.query(
        f"SELECT count() FROM {table_name} FORMAT JSONColumns", exitcode=0, timeout=timeout
    )
    return int(json.loads(r.output)["count()"][0])


@TestStep
def get_projections(self, node: ClickHouseNode, table_name: str) -> list:
    """
    Get a list of active projections for a given table.
    """
    r = node.query(
        f"SELECT distinct(name) FROM system.projection_parts WHERE table='{table_name}' and active FORMAT JSONColumns",
        exitcode=0,
    )
    return json.loads(r.output)["name"]


@TestStep
def get_indexes(self, node: ClickHouseNode, table_name: str) -> list:
    """
    Get a list of secondary indexes for a given table.
    """
    r = node.query(
        f"SELECT name FROM system.data_skipping_indices WHERE table='{table_name}' FORMAT JSONColumns",
        exitcode=0,
    )
    return json.loads(r.output)["name"]


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
