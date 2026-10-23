"""Manual CAS garbage-collection helpers."""

import json

from testflows.asserts import error
from testflows.core import *

# ``SYSTEM CAS GC RUN`` result, one row per disk. Names and types match
# ``contentAddressedGcRoundColumns`` in InterpreterSystemQuery.cpp.
# Counters on a deferred row, or a row that did not acquire the lease, are zero.
# The SRS text also names ``entries_redelete_failed``; the command does not return it.
GC_RUN_COLUMNS = (
    "disk",
    "acquired_lease",
    "deferred",
    "round",
    "candidates_marked",
    "objects_deleted",
    "objects_absent",
    "objects_replaced",
    "objects_spared",
    "manifests_deleted",
    "entries_condemned",
    "entries_graduated",
    "entries_redeleted",
    "fence_outs",
    "anomalies",
    "pending_candidates",
    "pending_condemned",
    "pending_retired",
)


def parse_gc_run_report(output, disk):
    """Parse the one JSONEachRow object ``SYSTEM CAS GC RUN`` printed for ``disk``."""
    rows = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("{"):
            rows.append(json.loads(line))

    assert len(rows) == 1, error(
        f"SYSTEM CAS GC RUN '{disk}' did not return one row:\n{output}"
    )

    row = rows[0]
    missing = [name for name in GC_RUN_COLUMNS if name not in row]
    assert not missing, error(f"GC report for {disk} is missing {missing}: {row}")
    assert row["disk"] == disk, error(row)

    parsed = {"disk": row["disk"]}
    for name in GC_RUN_COLUMNS[1:]:
        parsed[name] = int(row[name])
    return parsed


def _run_report(node, disk):
    # The statement grammar ends at the disk name. FORMAT in the SQL is a
    # syntax error; the client --format option selects JSONEachRow instead.
    result = node.query(
        f"SYSTEM CAS GC RUN '{disk}'",
        settings=[("format", "JSONEachRow")],
    )
    return parse_gc_run_report(result.output, disk)


@TestStep(When)
@Name("run one garbage collection round")
def run_garbage_collection(self, disk, node=None):
    """Run one manual GC round on ``disk`` and return its report row.

    The row is the ``SYSTEM CAS GC RUN`` result. Reclamation is staged: a round
    condemns unreachable blobs, a later round graduates them, and a round after
    that deletes the bodies. ``objects_deleted`` on the condemning round stays 0.
    """
    if node is None:
        node = self.context.node

    return _run_report(node, disk)


@TestStep(When)
@Name("run garbage collection on a CAS pool")
def collect_garbage(self, disk, nodes=None, rounds=4):
    """Run garbage collection on ``disk`` from every server mounting the pool.

    Returns one report dict per round per node, in the order the rounds ran.
    Reclamation is staged — a round condemns what it found unreachable and a
    later round deletes it — and only one server holds the collection lease at
    a time, so a single round on a single server proves nothing either way.
    """
    if nodes is None:
        nodes = self.context.nodes

    reports = []
    for _ in range(rounds):
        for node in nodes:
            reports.append(_run_report(node, disk))
    return reports


@TestStep(Given)
@Name("stop background garbage collection")
def stop_garbage_collection(self, disk, nodes=None):
    """Pause the background GC scheduler on ``disk`` on every given server.

    STOP is process-local and does not survive restart. Manual
    ``SYSTEM CAS GC RUN`` still runs. The scheduler is started again on
    every given node when this step finishes.
    """
    if nodes is None:
        nodes = self.context.nodes

    for node in nodes:
        node.query(f"SYSTEM CAS GC STOP '{disk}'")

    try:
        yield
    finally:
        with Finally("resume background garbage collection"):
            start_garbage_collection(disk=disk, nodes=nodes)


@TestStep(When)
@Name("start background garbage collection")
def start_garbage_collection(self, disk, nodes=None):
    """Resume the background GC scheduler on ``disk`` on every given server."""
    if nodes is None:
        nodes = self.context.nodes

    for node in nodes:
        node.query(f"SYSTEM CAS GC START '{disk}'")
