from testflows.core import *


@TestStep(When)
def kill_node(self, node):
    """Hard-kill a ClickHouse node (SIGKILL, no graceful shutdown)."""
    node.stop_clickhouse(safe=False, signal="KILL")


@TestStep(When)
def start_node(self, node):
    """Start a ClickHouse node back up."""
    node.start_clickhouse()


@TestStep(Then)
def wait_for_nodes_ready(self, nodes, timeout=90, delay=2):
    """Wait until every node answers a trivial query."""
    for node in nodes:
        for attempt in retries(timeout=timeout, delay=delay):
            with attempt:
                node.query("SELECT 1", exitcode=0)
