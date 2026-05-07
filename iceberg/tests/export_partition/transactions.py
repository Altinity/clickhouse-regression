"""Atomicity, idempotency, and snapshot linearity of EXPORT PARTITION.

Verifies that successful exports append exactly one linearised snapshot,
that the ZooKeeper-backed idempotency key rejects duplicates within the
TTL (and that ``force_export`` and TTL expiry release that gate), and
that failpoints in the commit path leave the destination atomically
either committed or untouched.
"""

import time

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import (
    RQ_Iceberg_ExportPartition_Transactions_SnapshotChain,
    RQ_Iceberg_ExportPartition_Transactions_Idempotency,
    RQ_Iceberg_ExportPartition_Transactions_CrashRecovery,
)

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
@Requirements(RQ_Iceberg_ExportPartition_Transactions_SnapshotChain("1.0"))
@Name("sequential exports append one append-snapshot each")
def sequential_exports_append_snapshots(
    self, minio_root_user, minio_root_password
):
    """Two sequential exports produce two append snapshots, linearly
    chained, with strictly increasing ``sequence_number``.
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
@Requirements(RQ_Iceberg_ExportPartition_Transactions_Idempotency("1.0"))
@Name("duplicate export within TTL is rejected")
def duplicate_export_within_ttl_rejected(
    self, minio_root_user, minio_root_password
):
    """A second export of the same ``(source, destination, partition)``
    within the manifest TTL is rejected with ``BAD_ARGUMENTS`` /
    "Export with key ... already exported"; the snapshot log is unchanged.
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
@Requirements(RQ_Iceberg_ExportPartition_Transactions_Idempotency("1.0"))
@Name("force_export overrides the idempotency gate")
def force_export_bypasses_ttl_gate(self, minio_root_user, minio_root_password):
    """``export_merge_tree_partition_force_export = 1`` re-exports the
    same partition inside the TTL window, producing a second linearly
    chained snapshot.
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
@Requirements(RQ_Iceberg_ExportPartition_Transactions_Idempotency("1.0"))
@Name("TTL expiry permits re-export of the same partition")
def ttl_expiry_permits_reexport(self, minio_root_user, minio_root_password):
    """After the manifest TTL expires the gate is released and a re-export
    of the same partition succeeds, adding a second snapshot.
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
@Requirements(RQ_Iceberg_ExportPartition_Transactions_CrashRecovery("1.0"))
@Name("commit survives pre-publish failure (non-retry cleanup)")
def commit_survives_pre_publish_failure(
    self, minio_root_user, minio_root_password
):
    """With ``iceberg_writes_non_retry_cleanup`` armed, the commit retries
    after a pre-publish exception and ends with exactly one append
    snapshot containing the full row count (data files are not discarded).
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
@Requirements(RQ_Iceberg_ExportPartition_Transactions_CrashRecovery("1.0"))
@Name("commit idempotent after post-commit pre-status crash window")
def commit_idempotent_after_post_commit_pre_status_crash(
    self, minio_root_user, minio_root_password
):
    """With ``iceberg_export_after_commit_before_zk_completed`` armed
    (crash between Iceberg commit and the ``COMPLETED`` Keeper status),
    the retry recognises its own prior commit via the
    ``clickhouse.export-partition-transaction-id`` snapshot marker and
    converges to ``COMPLETED`` with exactly one snapshot.
    """
    node = self.context.node
    failpoint = "iceberg_export_after_commit_before_zk_completed"
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
            "status converges to COMPLETED on retry "
            "(not FAILED / KILLED)"
        ):
            wait_for_export_status(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
                expected_status="COMPLETED",
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

        with And(
            "exactly one snapshot exists - the transaction-id check "
            "must short-circuit the second commit attempt"
        ):
            snapshots = get_snapshots(
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
            assert len(snapshots) == 1, error(
                f"Expected 1 snapshot after post-commit retry, got "
                f"{len(snapshots)}: {[s.snapshot_id for s in snapshots]!r}. "
                f"More than one means the idempotency marker did not "
                f"prevent a double-commit."
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
                f"Expected snapshot summary to carry {txn_id_key!r} so "
                f"that retries after the post-commit / pre-status crash "
                f"window are idempotent; got keys: "
                f"{sorted(summary.keys())!r}"
            )
    finally:
        with Finally(f"disable {failpoint} in case it did not trigger"):
            _disable_failpoint(failpoint, node=node)


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_Transactions_CrashRecovery("1.0"))
@Name("manifest status transition failure is retried without duplicate commit")
def manifest_status_transition_failure_retried_idempotently(
    self, minio_root_user, minio_root_password
):
    """A throw inside a manifest status transition
    (``export_partition_status_change_throw``) is retried without
    re-issuing the underlying Iceberg commit; the export reaches
    ``COMPLETED`` with exactly one append snapshot.
    """
    node = self.context.node
    failpoint = "export_partition_status_change_throw"
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

        with And("status reaches COMPLETED after the manifest-update retry"):
            wait_for_export_status(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
                expected_status="COMPLETED",
            )

        with Then("destination has the full row count"):
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
            "exactly one append snapshot exists - the status-update "
            "retry must not republish the data"
        ):
            snapshots = get_snapshots(
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
            assert len(snapshots) == 1, error(
                f"Expected 1 snapshot after status-transition retry, got "
                f"{len(snapshots)}: {[s.snapshot_id for s in snapshots]!r}. "
                f"More than one means the retry path re-issued the "
                f"underlying Iceberg commit."
            )
            operation = getattr(snapshots[0].summary, "operation", None)
            op_str = str(getattr(operation, "value", operation))
            assert op_str == "append", error(
                f"Expected append snapshot, got {op_str!r}"
            )
    finally:
        with Finally(f"disable {failpoint} in case it did not trigger"):
            _disable_failpoint(failpoint, node=node)


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_Transactions_CrashRecovery("1.0"))
@Name("commit durable across post-publish exception")
def commit_durable_across_post_publish_exception(
    self, minio_root_user, minio_root_password
):
    """With ``iceberg_writes_post_publish_throw`` armed, the published
    snapshot survives a post-publish exception (manifests intact); the
    retry recognises the prior commit and finishes ``COMPLETED``.
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
    commit_idempotent_after_post_commit_pre_status_crash,
    manifest_status_transition_failure_retried_idempotently,
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
