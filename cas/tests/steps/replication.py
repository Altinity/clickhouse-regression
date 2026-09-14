"""Replication sync and replica-agreement helpers."""

from testflows.core import *
from testflows.asserts import error

from cas.tests.steps.checksums import table_checksum


@TestStep(When)
@Name("sync replica on one node")
def sync_replica(self, table_name, node=None):
    """Run SYSTEM SYNC REPLICA for ``table_name`` on one node."""
    if node is None:
        node = self.context.node
    node.query(f"SYSTEM SYNC REPLICA {table_name}")


@TestStep(When)
@Name("sync replica on all nodes")
def sync_replicas(self, table_name, nodes=None):
    """Run SYSTEM SYNC REPLICA for ``table_name`` on every replica."""
    if nodes is None:
        nodes = self.context.nodes
    for node in nodes:
        node.query(f"SYSTEM SYNC REPLICA {table_name}")


@TestStep(When)
@Name("stop fetches on replica")
def stop_fetches(self, table_name, node):
    """Pause replication fetches so a leader can get ahead."""
    node.query(f"SYSTEM STOP FETCHES {table_name}")


@TestStep(When)
@Name("start fetches on replica")
def start_fetches(self, table_name, node):
    """Resume replication fetches after a controlled lag window."""
    node.query(f"SYSTEM START FETCHES {table_name}")


@TestStep(Then)
@Name("assert all replicas agree on table checksum")
def assert_replicas_agree(self, table_name, nodes=None, checksum_fn=None):
    """Assert every replica returns the same checksum for ``table_name``."""
    if nodes is None:
        nodes = self.context.nodes
    if checksum_fn is None:
        checksum_fn = table_checksum

    sync_replicas(table_name=table_name, nodes=nodes)

    expected = None
    for node in nodes:
        actual = checksum_fn(node, table_name)
        note(f"{node.name}: {actual}")
        if expected is None:
            expected = actual
        else:
            assert actual == expected, error(
                f"replica disagreement on {table_name}: "
                f"{nodes[0].name}={expected}, {node.name}={actual}"
            )
    return expected


@TestStep(Then)
@Name("assert replication queue has no permanent errors")
def assert_replication_queue_healthy(self, table_name, nodes=None):
    """Assert no replica has a non-empty last_exception on the replication queue."""
    if nodes is None:
        nodes = self.context.nodes

    for node in nodes:
        failed = node.query(
            f"SELECT count() FROM system.replication_queue "
            f"WHERE table = '{table_name}' AND last_exception != ''"
        ).output.strip()
        if failed != "0":
            details = node.query(
                "SELECT type, new_part_name, last_exception "
                "FROM system.replication_queue "
                f"WHERE table = '{table_name}' AND last_exception != '' "
                "FORMAT Vertical"
            ).output
            assert False, error(
                f"{node.name} has failed replication queue entries for "
                f"{table_name}:\n{details}"
            )
