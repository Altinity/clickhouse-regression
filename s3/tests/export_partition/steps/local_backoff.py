import time

from testflows.core import *
from testflows.asserts import error

from helpers.queries import select_all_ordered

from .containers import kill_minio, start_minio
from .export_status import wait_for_export_to_complete
from .verification import source_matches_destination
from .nodes import kill_node, start_node, wait_for_nodes_ready

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

# Obsolete/ignored retry-budget setting kept for backward compatibility.
OBSOLETE_MAX_RETRIES = "export_merge_tree_partition_max_retries"

# Default values (see the corresponding RQ.* requirements).
DEFAULT_INITIAL_BACKOFF = 5
DEFAULT_MAX_BACKOFF = 300
DEFAULT_TASK_TIMEOUT = 86400

# Injection modes for the multi-replica orchestration helpers.
FAILPOINT_MODE = "failpoint"
MINIO_MODE = "minio"


def short_backoff_settings(initial=1, max_backoff=2):
    """Small back-off settings so retries happen quickly during tests."""
    return [
        (INITIAL_BACKOFF_SECONDS, str(initial)),
        (MAX_BACKOFF_SECONDS, str(max_backoff)),
    ]


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


@TestStep(Then)
def get_backoff_attempts(self, source_table, partition, node):
    """Return the highest back-off attempt count for the partition on one node (0 if none)."""
    result = node.query(
        f"SELECT max(tupleElement(t, 'attempts')) FROM ("
        f"SELECT arrayJoin(local_backoff_per_part) AS t "
        f"FROM system.replicated_partition_exports "
        f"WHERE source_table = '{source_table}' AND partition_id = '{partition}')",
        exitcode=0,
    )
    value = result.output.strip()
    if not value or value == "\\N":
        return 0
    return int(value)


@TestStep(Then)
def wait_for_backoff_attempts(
    self, source_table, partition, min_attempts, nodes=None, timeout=60, delay=2
):
    """Wait until some replica reaches at least ``min_attempts`` back-off attempts."""
    if nodes is None:
        nodes = self.context.nodes

    for attempt in retries(timeout=timeout, delay=delay):
        with attempt:
            current = max(
                get_backoff_attempts(
                    source_table=source_table, partition=partition, node=node
                )
                for node in nodes
            )
            assert current >= min_attempts, error(
                f"expected >= {min_attempts} attempts, got {current}"
            )


@TestStep(Then)
def backoff_next_retry_in_future(self, source_table, partition, node):
    """Return True if some back-off entry's next_retry_time is still in the future."""
    result = node.query(
        f"SELECT count() FROM ("
        f"SELECT arrayJoin(local_backoff_per_part) AS t "
        f"FROM system.replicated_partition_exports "
        f"WHERE source_table = '{source_table}' AND partition_id = '{partition}') "
        f"WHERE tupleElement(t, 'next_retry_time') > now()",
        exitcode=0,
    )
    return int(result.output.strip()) > 0


@TestStep(Then)
def wait_for_backoff_next_retry_in_future(
    self, source_table, partition, node, timeout=30, delay=1
):
    """Wait until a back-off entry shows a next_retry_time in the future.

    The requirement is that a part failing with a retryable error is armed with a
    future next_retry_time. With the short test back-off (initial=1s, max=2s) that
    future window is only ~1-2s wide, and there is a brief interval where the
    deadline is already due (next_retry_time <= now()) but the replica has not
    re-fired the retry yet. Sampling once is therefore racy, so we poll to observe
    the entry at a moment when its next retry is genuinely still in the future."""
    for attempt in retries(timeout=timeout, delay=delay):
        with attempt:
            assert backoff_next_retry_in_future(
                source_table=source_table, partition=partition, node=node
            ), error()


@TestStep(Then)
def wait_for_local_backoff_on_all(
    self, source_table, partition, nodes=None, timeout=90, delay=2
):
    """Wait until every given replica reports its own back-off entry for the partition."""
    if nodes is None:
        nodes = self.context.nodes

    for attempt in retries(timeout=timeout, delay=delay):
        with attempt:
            for node in nodes:
                count = get_local_backoff_count(
                    source_table=source_table, partition=partition, node=node
                )
                assert count > 0, error(
                    f"replica {node.name} has no back-off entry yet"
                )


@TestStep(Then)
def assert_task_stays_pending(self, source_table, partition, node=None, duration=15):
    """Sleep for ``duration`` seconds and assert the task is still PENDING (never terminal)."""
    time.sleep(duration)
    status = get_export_status(
        source_table=source_table, partition=partition, node=node
    )
    assert status == "PENDING", error(
        f"task must stay PENDING, got {status!r} after {duration}s"
    )


@TestStep(Then)
def assert_destination_empty(self, destination_table, node=None):
    """Assert that no rows reached the destination table."""
    if node is None:
        node = self.context.node
    rows = select_all_ordered(table_name=destination_table, node=node)
    assert len(rows) == 0, error(f"expected empty destination, got {len(rows)} rows")


@TestStep(Then)
def assert_destination_unchanged(self, destination_table, expected_rows, node=None):
    """Assert the destination still holds exactly ``expected_rows`` (no rows added,
    removed, or duplicated). Used when a fail-fast export runs against a destination
    that was already populated by an earlier successful export: the failed export MUST
    NOT write any rows, so the pre-existing data has to stay exactly as it was."""
    if node is None:
        node = self.context.node
    rows = select_all_ordered(table_name=destination_table, node=node)
    assert rows == expected_rows, error(
        f"expected destination unchanged with {len(expected_rows)} rows, "
        f"got {len(rows)} rows"
    )


@TestStep(Then)
def assert_setting_rejected(
    self, source_table, destination_table, partition, setting, value, node=None
):
    """Assert that an EXPORT PARTITION with an invalid setting value is rejected."""
    if node is None:
        node = self.context.node

    result = node.query(
        f"ALTER TABLE {source_table} EXPORT PARTITION ID '{partition}' "
        f"TO TABLE {destination_table}",
        settings=list(self.context.default_settings) + [(setting, value)],
        no_checks=True,
    )
    assert result.exitcode != 0, error(
        f"expected {setting}={value!r} to be rejected, but it was accepted"
    )


@TestStep(Then)
def assert_export_fails_fast(
    self,
    source_table,
    destination_table,
    partition,
    node=None,
    settings=None,
    timeout=60,
    expected_rows=None,
):
    """Assert a deterministic (non-retryable) error stops the export quickly and writes
    no data: either the ALTER is rejected synchronously, or the task transitions to
    FAILED. It MUST NOT sit retrying until the task timeout.

    The destination check reflects the "not writing any exported rows from the failed
    export" guarantee (RQ.ClickHouse.ExportPartition.ErrorClassification.NonRetryable):
    * When ``expected_rows`` is None (destination started empty) it must stay empty.
    * When ``expected_rows`` is given (destination was pre-populated by an earlier
      successful export) it must stay exactly those rows, since the failed export must
      not add, remove, or duplicate any data.
    """
    if node is None:
        node = self.context.node

    inline = list(self.context.default_settings)
    if settings:
        inline += settings

    result = node.query(
        f"ALTER TABLE {source_table} EXPORT PARTITION ID '{partition}' "
        f"TO TABLE {destination_table}",
        settings=inline,
        no_checks=True,
    )

    if result.exitcode == 0:
        wait_for_export_status(
            source_table=source_table,
            partition=partition,
            status="FAILED",
            node=node,
            timeout=timeout,
        )

    if expected_rows is None:
        assert_destination_empty(destination_table=destination_table, node=node)
    else:
        assert_destination_unchanged(
            destination_table=destination_table,
            expected_rows=expected_rows,
            node=node,
        )


@TestStep(Finally)
def reset_backoff_test_state(self, source_table, nodes=None):
    """Best-effort recovery after failover/chaos tests: restart any down node, bring
    MinIO back, and clear failpoints/stopped moves. Safe to call unconditionally."""
    if nodes is None:
        nodes = self.context.nodes

    for node in nodes:
        try:
            node.start_clickhouse()
        except Exception:
            pass

    try:
        start_minio()
    except Exception:
        pass

    for node in nodes:
        try:
            node.query(
                f"SYSTEM DISABLE FAILPOINT {RETRYABLE_FAILPOINT}", no_checks=True
            )
            node.query(f"SYSTEM START MOVES {source_table}", no_checks=True)
        except Exception:
            pass


@TestStep(When)
def inject_retryable_failure(self, mode, nodes=None):
    """Cause retryable part-export failures, either via the failpoint (per node) or by
    taking MinIO down (cluster-wide)."""
    if mode == FAILPOINT_MODE:
        enable_failpoint(failpoint=RETRYABLE_FAILPOINT, nodes=nodes)
    else:
        kill_minio()


@TestStep(When)
def clear_retryable_failure(self, mode, nodes=None):
    """Clear a previously injected retryable failure."""
    if mode == FAILPOINT_MODE:
        disable_failpoint(failpoint=RETRYABLE_FAILPOINT, nodes=nodes)
    else:
        start_minio()


@TestStep(When)
def run_relay_failover(self, source_table, destination_table, partition, nodes, mode):
    """Scripted relay: each replica in turn fails and backs off, then is killed so the
    next replica takes over. Finally the failure clears, killed replicas restart, and
    the export completes exactly once.

    ``mode`` selects the failure source: ``FAILPOINT_MODE`` (per-replica retryable
    failpoint) or ``MINIO_MODE`` (shared MinIO outage).
    """
    # A real MinIO outage first spins inside the AWS SDK's own retry loop before the
    # background export worker sees a failure, so the first local back-off entry only
    # appears after ~60-70s (see retryable_minio_outage_recovers). The failpoint
    # throws immediately, so the default wait is fine there.
    backoff_timeout = 120 if mode == MINIO_MODE else 60

    with When("I inject a retryable failure and let the first replica start"):
        inject_retryable_failure(mode=mode, nodes=nodes)
        stop_moves(source_table=source_table, nodes=nodes[1:])
        start_export(
            source_table=source_table,
            destination_table=destination_table,
            partition=partition,
            node=nodes[0],
            settings=short_backoff_settings(),
        )

    with And(f"the first replica {nodes[0].name} backs off"):
        wait_for_local_backoff(
            source_table=source_table,
            partition=partition,
            nodes=[nodes[0]],
            timeout=backoff_timeout,
        )

    for i in range(len(nodes) - 1):
        with When(
            f"I kill {nodes[i].name} and hand the part off to {nodes[i + 1].name}"
        ):
            kill_node(node=nodes[i])
            start_moves(source_table=source_table, nodes=[nodes[i + 1]])

        with And(f"{nodes[i + 1].name} picks up the part and backs off"):
            wait_for_local_backoff(
                source_table=source_table,
                partition=partition,
                nodes=[nodes[i + 1]],
                timeout=backoff_timeout,
            )

    with When("I clear the failure, restart the killed replicas and resume moves"):
        clear_retryable_failure(mode=mode, nodes=[nodes[-1]])
        for node in nodes[:-1]:
            start_node(node=node)
        wait_for_nodes_ready(nodes=nodes)
        if mode == FAILPOINT_MODE:
            disable_failpoint(failpoint=RETRYABLE_FAILPOINT, nodes=nodes)
        start_moves(source_table=source_table, nodes=nodes)

    with Then("the export completes and destination matches source exactly"):
        wait_for_export_to_complete(
            source_table=source_table, partition_id=partition, node=nodes[-1]
        )
        source_matches_destination(
            source_table=source_table, destination_table=destination_table
        )


@TestStep(When)
def run_chaos_failover(
    self, source_table, destination_table, partition, nodes, mode, iterations=5
):
    """Randomized chaos: inject a retryable failure, then repeatedly kill/restart random
    replicas (always leaving at least one alive). Finally restore everything and assert
    the export still completes exactly once."""
    import random

    down = set()

    # See run_relay_failover: a MinIO outage takes ~60-70s to surface the first
    # ClickHouse-level failure, so the first local back-off needs a longer wait.
    backoff_timeout = 120 if mode == MINIO_MODE else 60

    with When("I inject a retryable failure and start the export"):
        inject_retryable_failure(mode=mode, nodes=nodes)
        start_export(
            source_table=source_table,
            destination_table=destination_table,
            partition=partition,
            node=nodes[0],
            settings=short_backoff_settings(),
        )
        wait_for_local_backoff(
            source_table=source_table, partition=partition, timeout=backoff_timeout
        )

    with When("I randomly kill and restart replicas"):
        for _ in range(iterations):
            node = random.choice(nodes)
            if node.name in down:
                start_node(node=node)
                down.discard(node.name)
            elif len(down) < len(nodes) - 1:
                kill_node(node=node)
                down.add(node.name)
            time.sleep(random.uniform(2, 5))

    with When("I restore all replicas and clear the failure"):
        for node in nodes:
            if node.name in down:
                start_node(node=node)
        wait_for_nodes_ready(nodes=nodes)
        clear_retryable_failure(mode=mode, nodes=nodes)
        if mode == FAILPOINT_MODE:
            disable_failpoint(failpoint=RETRYABLE_FAILPOINT, nodes=nodes)
        start_moves(source_table=source_table, nodes=nodes)

    with Then("the export completes and destination matches source exactly"):
        wait_for_export_to_complete(
            source_table=source_table, partition_id=partition, node=nodes[-1]
        )
        source_matches_destination(
            source_table=source_table, destination_table=destination_table
        )
