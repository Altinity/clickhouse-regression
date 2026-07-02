from testflows.core import *
from testflows.asserts import error

# Failpoints added by Altinity/ClickHouse#1984. They fire from the async
# part-export worker so the whole error-classification/back-off path is exercised.
RETRYABLE_FAILPOINT = "export_part_retryable_throw"
NON_RETRYABLE_FAILPOINT = "export_part_non_retryable_throw"

# New per-part local exponential back-off settings (Altinity/ClickHouse#1984).
# The retry budget (export_merge_tree_partition_max_retries) was removed; retryable
# failures now back off locally until success or the absolute task timeout elapses.
INITIAL_BACKOFF_SECONDS = "export_merge_tree_partition_retry_initial_backoff_seconds"
MAX_BACKOFF_SECONDS = "export_merge_tree_partition_retry_max_backoff_seconds"
TASK_TIMEOUT_SECONDS = "export_merge_tree_partition_task_timeout_seconds"


@TestStep(When)
def enable_failpoint(self, failpoint, nodes=None):
    """Enable a failpoint on the given nodes (defaults to all cluster nodes)."""
    if nodes is None:
        nodes = self.context.nodes

    for node in nodes:
        node.query(f"SYSTEM ENABLE FAILPOINT {failpoint}", exitcode=0)


@TestStep(Finally)
def disable_failpoint(self, failpoint, nodes=None):
    """Disable a failpoint on the given nodes (defaults to all cluster nodes)."""
    if nodes is None:
        nodes = self.context.nodes

    for node in nodes:
        node.query(f"SYSTEM DISABLE FAILPOINT {failpoint}", exitcode=0)


@TestStep(When)
def stop_moves(self, source_table, nodes):
    """Stop the export/move scheduler for the source table on the given nodes.

    ``SYSTEM STOP MOVES`` is a node-local operation, so this only pauses the
    scheduler on the nodes passed in. Used to control which replica is allowed
    to pick up a part first (see ``local_backoff_is_replica_local``).
    """
    for node in nodes:
        node.query(f"SYSTEM STOP MOVES {source_table}", exitcode=0)


@TestStep(When)
def start_moves(self, source_table, nodes):
    """Resume the export/move scheduler for the source table on the given nodes."""
    for node in nodes:
        node.query(f"SYSTEM START MOVES {source_table}", exitcode=0)


@TestStep(When)
def start_export(self, source_table, destination_table, partition, node, settings=None):
    """Issue a single asynchronous EXPORT PARTITION and return without waiting."""
    inline_settings = list(self.context.default_settings)
    if settings:
        inline_settings += settings

    return node.query(
        f"ALTER TABLE {source_table} EXPORT PARTITION ID '{partition}' "
        f"TO TABLE {destination_table}",
        settings=inline_settings,
        exitcode=0,
    )


@TestStep(Then)
def wait_for_export_status(
    self, source_table, partition, status, node=None, timeout=90, delay=3
):
    """Wait until an export for the partition reaches the given status."""
    from .export_status import check_export_status

    for attempt in retries(timeout=timeout, delay=delay):
        with attempt:
            exports = check_export_status(
                status=status,
                source_table=source_table,
                partition_id=partition,
                node=node,
            )
            assert int(exports.output.strip()) > 0, error()


@TestStep(Then)
def get_export_status(self, source_table, partition, node=None):
    """Return the current export status for the partition on a node."""
    if node is None:
        node = self.context.node

    return node.query(
        f"SELECT status FROM system.replicated_partition_exports "
        f"WHERE source_table = '{source_table}' AND partition_id = '{partition}'",
        exitcode=0,
    ).output.strip()


@TestStep(Then)
def get_local_backoff_count(self, source_table, partition, node):
    """Return the number of local back-off entries for the partition on one node."""
    result = node.query(
        f"SELECT sum(length(local_backoff_per_part)) "
        f"FROM system.replicated_partition_exports "
        f"WHERE source_table = '{source_table}' "
        f"AND partition_id = '{partition}'",
        exitcode=0,
    )
    value = result.output.strip()
    if not value or value == "\\N":
        return 0
    return int(value)


@TestStep(Then)
def wait_for_local_backoff(
    self, source_table, partition, nodes=None, timeout=60, delay=2
):
    """Wait until some replica reports a local back-off entry for the partition."""
    if nodes is None:
        nodes = self.context.nodes

    for attempt in retries(timeout=timeout, delay=delay):
        with attempt:
            total = sum(
                get_local_backoff_count(
                    source_table=source_table, partition=partition, node=node
                )
                for node in nodes
            )
            assert total > 0, error()


@TestStep(Then)
def get_local_backoff_column_type(self, node=None):
    """Return the type of the local_backoff_per_part column, asserting it exists."""
    if node is None:
        node = self.context.node

    structure = node.query(
        "DESCRIBE TABLE system.replicated_partition_exports FORMAT TabSeparated",
        exitcode=0,
    )
    columns = {
        line.split("\t")[0].strip(): line.split("\t")[1].strip()
        for line in structure.output.strip().splitlines()
        if line.strip()
    }
    assert "local_backoff_per_part" in columns, error()
    return columns["local_backoff_per_part"]
