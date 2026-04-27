"""Atomicity, idempotency, and snapshot linearity of EXPORT PARTITION.

These scenarios exercise the transactional guarantees ClickHouse makes when
committing an Iceberg snapshot on behalf of ``ALTER TABLE ... EXPORT
PARTITION``:

* A successful export appends exactly one snapshot whose
  ``parent_snapshot_id`` chains to the previous snapshot and whose
  ``sequence_number`` is strictly larger than the parent's. Every snapshot
  the export produces must be an ``append`` operation.
* The idempotency key that lives in ZooKeeper (``export_merge_tree_partition_manifest_ttl``)
  rejects a second EXPORT PARTITION for the same ``(source, destination,
  partition)`` triple with ``Export with key ... already exported`` while
  the TTL window is still active.
* ``export_merge_tree_partition_force_export = 1`` overrides that ZooKeeper
  guard: the previous entry is dropped and a new snapshot is committed even
  within the original TTL window.
* After the TTL elapses the gate is released automatically and a re-export
  produces a fresh snapshot.
* Two failpoints in the ClickHouse commit path are exercised to show the
  commit remains atomic across exceptions:

  - ``iceberg_writes_non_retry_cleanup`` simulates a failure while writing
    the manifest entry file (*before* the snapshot is published). The
    commit is retried internally; the final snapshot exists and contains
    every row, which proves the pre-publish cleanup does not discard the
    uploaded data files.
  - ``iceberg_writes_post_publish_throw`` simulates a failure *after* the
    snapshot has been published (e.g. metadata-cache invalidation raising).
    The snapshot stays durable, the manifest chain is intact, and
    ``system.replicated_partition_exports`` still reports ``COMPLETED``.

Every scenario runs with ``flags=TE`` so one transactional regression does
not mask the rest of the matrix. Failpoints in ClickHouse are ONCE (they
consume themselves on the first trigger), but each scenario still re-runs
``SYSTEM DISABLE FAILPOINT`` in ``Finally`` to leave the node in a known
state if the scenario fails before the failpoint has a chance to fire.
"""

import time

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    create_replicated_mergetree,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
)
from iceberg.tests.export_partition.steps.export_status import (
    wait_for_export_status,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.manifest_validation import (
    get_current_snapshot_summary,
    get_snapshots,
    load_pyiceberg_table,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
    assert_source_and_destination_match,
)


SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"

BAD_ARGUMENTS = 36


def _seed_source(values="(1, 2020), (2, 2020), (3, 2021), (4, 2021)"):
    """Create a ReplicatedMergeTree with two partitions (2020, 2021)."""
    source_table = f"mt_{getuid()}"
    with Given("create source ReplicatedMergeTree"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
    with And("insert partitioned values"):
        insert_data(table_name=source_table, values=values)
    return source_table


def _enable_failpoint(name, node=None):
    """Enable a ClickHouse ONCE failpoint and make sure we disable it on exit."""
    if node is None:
        node = current().context.node
    node.query(f"SYSTEM ENABLE FAILPOINT {name}")


def _disable_failpoint(name, node=None):
    """Best-effort ``SYSTEM DISABLE FAILPOINT`` used inside ``Finally``."""
    if node is None:
        node = current().context.node
    node.query(f"SYSTEM DISABLE FAILPOINT {name}")


@TestScenario
@Name("sequential exports append one append-snapshot each")
def sequential_exports_append_snapshots(
    self, minio_root_user, minio_root_password
):
    """Two sequential exports -> two linearised append snapshots.

    We assert three separate properties of Iceberg's snapshot log, which
    together encode the "every export is an atomic append" contract:

    * each export adds exactly one snapshot (count is ``N`` after ``N``
      exports);
    * ``sequence_number`` is strictly increasing;
    * each new snapshot's ``parent_snapshot_id`` points at the previous
      snapshot id (the chain is linear, no forks);
    * every snapshot's ``summary.operation`` is ``"append"``.
    """
    source_table = _seed_source()

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    with When("export partition 2020"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
        )

    with And("export partition 2021"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2021",
        )

    with Then("snapshot list has exactly two entries and is linearly chained"):
        snapshots = get_snapshots(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert len(snapshots) == 2, error(
            f"Expected 2 snapshots after two exports, got {len(snapshots)}: "
            f"{[s.snapshot_id for s in snapshots]!r}"
        )

        first, second = snapshots[0], snapshots[1]
        # PyIceberg surfaces "no parent" as ``None`` when the metadata
        # explicitly omits the field and as ``-1`` when ClickHouse writes
        # the Iceberg spec's "null snapshot" marker; accept both.
        assert first.parent_snapshot_id in (None, 0, -1), error(
            f"First snapshot must have no parent, got "
            f"parent_snapshot_id={first.parent_snapshot_id!r}"
        )
        assert second.parent_snapshot_id == first.snapshot_id, error(
            f"Second snapshot parent_snapshot_id should be {first.snapshot_id}, "
            f"got {second.parent_snapshot_id}"
        )
        assert second.sequence_number > first.sequence_number, error(
            f"Expected strictly increasing sequence_number, got "
            f"first={first.sequence_number} second={second.sequence_number}"
        )

    with And("every snapshot records an append operation"):
        for snap in snapshots:
            summary = snap.summary
            operation = getattr(summary, "operation", None)
            op_str = str(getattr(operation, "value", operation))
            assert op_str == "append", error(
                f"Expected append snapshot, got {op_str!r} for "
                f"snapshot_id={snap.snapshot_id}"
            )


@TestScenario
@Name("duplicate export within TTL is rejected")
def duplicate_export_within_ttl_rejected(
    self, minio_root_user, minio_root_password
):
    """Re-exporting the same partition before the manifest TTL expires fails.

    ClickHouse persists a per-export manifest in ZooKeeper keyed by
    ``(source_table, destination_table, partition_id)``. Until it expires,
    a second ``ALTER TABLE ... EXPORT PARTITION`` for the same triple must
    be rejected synchronously with ``Export with key ... already exported``
    (``BAD_ARGUMENTS``). The destination snapshot log must NOT gain a
    second snapshot, otherwise the idempotency guard is broken.
    """
    source_table = _seed_source()

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    with When("first export succeeds"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            extra_settings=[("export_merge_tree_partition_manifest_ttl", 300)],
        )

    with Then("second export is rejected with duplicate-export error"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            extra_settings=[("export_merge_tree_partition_manifest_ttl", 300)],
            exitcode=BAD_ARGUMENTS,
            message="Export with key",
            wait_for_completion=False,
        )

    with And("only one snapshot was ever committed"):
        snapshots = get_snapshots(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert len(snapshots) == 1, error(
            f"Expected 1 snapshot (duplicate export must not commit), "
            f"got {len(snapshots)}"
        )


@TestScenario
@Name("force_export overrides the idempotency gate")
def force_export_bypasses_ttl_gate(self, minio_root_user, minio_root_password):
    """``export_merge_tree_partition_force_export`` must re-export in-window.

    The gate is keyed on ZK state, so bypassing it and re-running the same
    partition produces a second snapshot whose ``parent_snapshot_id`` chains
    to the first. No extra rows are produced (the source still has the same
    three), but the destination must expose the latest snapshot with the
    same row count.
    """
    source_table = _seed_source(values="(1, 2020), (2, 2020), (3, 2020)")

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    with When("first export establishes the ZK idempotency entry"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            extra_settings=[("export_merge_tree_partition_manifest_ttl", 300)],
        )

    with And("re-export inside the TTL window with force_export = 1"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            extra_settings=[
                ("export_merge_tree_partition_manifest_ttl", 300),
                ("export_merge_tree_partition_force_export", 1),
            ],
        )

    with Then("two snapshots exist and they are linearly chained"):
        snapshots = get_snapshots(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert len(snapshots) == 2, error(
            f"Expected 2 snapshots after forced re-export, got {len(snapshots)}"
        )
        assert snapshots[1].parent_snapshot_id == snapshots[0].snapshot_id, error(
            "Forced re-export snapshot must chain to the original"
        )


@TestScenario
@Name("TTL expiry permits re-export of the same partition")
def ttl_expiry_permits_reexport(self, minio_root_user, minio_root_password):
    """The idempotency gate releases automatically after the TTL expires.

    Lower the TTL to a few seconds, wait it out, then re-export. The new
    export must succeed and the snapshot log must gain a second entry.
    """
    ttl_seconds = 3
    source_table = _seed_source(values="(1, 2020), (2, 2020), (3, 2020)")

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    with When(f"first export with {ttl_seconds}s manifest TTL"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            extra_settings=[
                ("export_merge_tree_partition_manifest_ttl", ttl_seconds),
            ],
        )

    with And(f"wait long enough for the TTL to expire ({ttl_seconds * 2}s)"):
        time.sleep(ttl_seconds * 2)

    with And("second export is accepted after TTL expiry"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            extra_settings=[
                ("export_merge_tree_partition_manifest_ttl", ttl_seconds),
            ],
        )

    with Then("snapshot log has grown by one"):
        snapshots = get_snapshots(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert len(snapshots) == 2, error(
            f"Expected 2 snapshots after TTL-expiry re-export, "
            f"got {len(snapshots)}"
        )


@TestScenario
@Name("commit survives pre-publish failure (non-retry cleanup)")
def commit_survives_pre_publish_failure(
    self, minio_root_user, minio_root_password
):
    """``iceberg_writes_non_retry_cleanup`` fires before the snapshot is published.

    The ONCE failpoint throws while writing the manifest entry file. The
    commit path must clean up the partial manifest files *without* deleting
    the already-uploaded data files and the export scheduler must retry
    internally, producing exactly one successful append snapshot with the
    full row count.
    """
    node = self.context.node
    failpoint = "iceberg_writes_non_retry_cleanup"
    source_table = _seed_source(values="(1, 2020), (2, 2020), (3, 2020)")

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    try:
        with And(f"arm the {failpoint} failpoint"):
            _enable_failpoint(failpoint, node=node)

        with When("run EXPORT PARTITION under the failpoint"):
            export_partition(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
            )

        with Then("destination row count matches the source"):
            assert_destination_row_count(
                destination=destination,
                expected=3,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
            assert_source_and_destination_match(
                source_table=source_table,
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                partition_where="year = 2020",
                order_by="id",
            )

        with And("exactly one append snapshot is visible"):
            snapshots = get_snapshots(
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
            assert len(snapshots) == 1, error(
                f"Expected 1 snapshot after retried commit, got {len(snapshots)}"
            )
    finally:
        with Finally(f"disable {failpoint} in case it did not trigger"):
            _disable_failpoint(failpoint, node=node)


@TestScenario
@Name("commit durable across post-publish exception")
def commit_durable_across_post_publish_exception(
    self, minio_root_user, minio_root_password
):
    """``iceberg_writes_post_publish_throw`` fires after the snapshot is published.

    The metadata file is already on disk and referenced by
    ``version-hint.text``; any follow-up cache invalidation raising must
    NOT delete the manifest list / manifest entries that the live snapshot
    now points at. The retry loop detects the commit is already done (via
    the stable transaction id written into the snapshot summary) and
    finishes reporting ``COMPLETED``.
    """
    node = self.context.node
    failpoint = "iceberg_writes_post_publish_throw"
    source_table = _seed_source(values="(1, 2020), (2, 2020), (3, 2020)")

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    try:
        with And(f"arm the {failpoint} failpoint"):
            _enable_failpoint(failpoint, node=node)

        with When("run EXPORT PARTITION under the failpoint"):
            export_partition(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
            )

        with And(
            "status is reported as COMPLETED (the idempotency check "
            "recognises the already-published commit on retry)"
        ):
            wait_for_export_status(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
                expected_status="COMPLETED",
            )

        with Then("the published snapshot is readable with every row"):
            assert_destination_row_count(
                destination=destination,
                expected=3,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
            assert_source_and_destination_match(
                source_table=source_table,
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                partition_where="year = 2020",
                order_by="id",
            )

        with And(
            "snapshot summary carries the ClickHouse export transaction id"
        ):
            summary = get_current_snapshot_summary(
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
            txn_id_key = "clickhouse.export-partition-transaction-id"
            assert txn_id_key in summary, error(
                f"Expected snapshot summary to carry {txn_id_key!r} so that "
                f"retries after a post-publish exception are idempotent; "
                f"got keys: {sorted(summary.keys())!r}"
            )
    finally:
        with Finally(f"disable {failpoint} in case it did not trigger"):
            _disable_failpoint(failpoint, node=node)


SCENARIOS = (
    sequential_exports_append_snapshots,
    duplicate_export_within_ttl_rejected,
    force_export_bypasses_ttl_gate,
    ttl_expiry_permits_reexport,
    commit_survives_pre_publish_failure,
    commit_durable_across_post_publish_exception,
)


@TestFeature
@Name("transactions")
def feature(self, minio_root_user, minio_root_password):
    """Atomicity / idempotency / snapshot-linearity scenarios."""
    for scenario in SCENARIOS:
        Scenario(test=scenario, flags=TE)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
