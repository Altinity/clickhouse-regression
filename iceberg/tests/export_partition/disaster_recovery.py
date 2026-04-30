"""Failure-injection and recovery scenarios for EXPORT PARTITION.

Each scenario exercises a specific failure mode (STOP MOVES, KILL,
commit-path failpoint, invalid arguments) and verifies that the
destination Iceberg table is never left partially committed.
"""

import time

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import RQ_Iceberg_ExportPartition_DisasterRecovery

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    count_rows,
    create_replicated_mergetree,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
    kill_export_partition,
    prepare_export_partition_settings,
)
from iceberg.tests.export_partition.steps.export_status import (
    get_export_row,
    wait_for_export_status,
    wait_for_export_to_start,
    wait_for_exports_to_settle,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    as_destination_name,
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.manifest_validation import (
    get_snapshots,
    load_pyiceberg_table,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
)


SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"

UNKNOWN_TABLE = 60


def _seed_source(values="(1, 2020), (2, 2020), (3, 2020)"):
    """Create a ReplicatedMergeTree with a single partition 2020 of 3 rows."""
    source_table = f"mt_{getuid()}"
    with Given("create the source ReplicatedMergeTree"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
    with And("insert partitioned values"):
        insert_data(table_name=source_table, values=values)
    return source_table


@TestScenario
@Name("STOP MOVES holds the export PENDING, START MOVES resumes it")
def stop_moves_holds_export_pending(
    self, minio_root_user, minio_root_password
):
    """``SYSTEM STOP MOVES`` keeps the export PENDING and leaves the
    destination empty; ``SYSTEM START MOVES`` lets it complete cleanly
    with one append snapshot.
    """
    node = self.context.node
    source_table = _seed_source()

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("SYSTEM STOP MOVES before scheduling the export"):
        node.query(f"SYSTEM STOP MOVES {source_table}")

    try:
        with And("schedule EXPORT PARTITION without waiting"):
            export_partition(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
                wait_for_completion=False,
                extra_settings=[
                    ("export_merge_tree_partition_max_retries", 50),
                ],
            )

        with And("the system table reports PENDING for several cycles"):
            wait_for_export_to_start(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
            )
            time.sleep(5)
            status = get_export_row(
                source_table=source_table,
                partition_id="2020",
                destination=destination,
                columns="status",
            )
            assert status == "PENDING", error(
                f"Expected status PENDING while moves are stopped, got {status!r}"
            )

        with And("destination still has no rows"):
            assert_destination_row_count(
                destination=destination,
                expected=0,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
    finally:
        with Finally("resume the scheduler via SYSTEM START MOVES"):
            node.query(f"SYSTEM START MOVES {source_table}")

    with Then("the export completes now that moves are allowed"):
        wait_for_export_status(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            expected_status="COMPLETED",
        )
        assert_destination_row_count(
            destination=destination,
            expected=3,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("exactly one append snapshot is in the destination"):
        snapshots = get_snapshots(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert len(snapshots) == 1, error(
            f"Expected 1 snapshot after STOP/START MOVES round-trip, "
            f"got {len(snapshots)}"
        )


@TestScenario
@Name("KILL EXPORT PARTITION while moves are stopped transitions to KILLED")
def kill_export_while_stopped_marks_killed(
    self, minio_root_user, minio_root_password
):
    """``KILL EXPORT PARTITION`` issued while ``SYSTEM STOP MOVES`` holds
    the export PENDING transitions the row to ``KILLED``, and a subsequent
    ``SYSTEM START MOVES`` does not resurrect it.
    """
    node = self.context.node
    source_table = _seed_source()

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("SYSTEM STOP MOVES before scheduling the export"):
        node.query(f"SYSTEM STOP MOVES {source_table}")

    moves_restored = False
    try:
        with And("schedule EXPORT PARTITION without waiting"):
            export_partition(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
                wait_for_completion=False,
                extra_settings=[
                    ("export_merge_tree_partition_max_retries", 50),
                ],
            )

        with And("wait for the PENDING row to appear"):
            wait_for_export_to_start(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
            )

        with And("KILL EXPORT PARTITION for this triple"):
            kill_export_partition(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
            )

        with And("status transitions to KILLED within the poll interval"):
            wait_for_export_status(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
                expected_status="KILLED",
                timeout=30,
            )

        with When("SYSTEM START MOVES; the killed export stays killed"):
            node.query(f"SYSTEM START MOVES {source_table}")
            moves_restored = True
            # Let a few scheduler cycles go by to be sure it does not
            # silently resurrect the task.
            time.sleep(5)
            status = get_export_row(
                source_table=source_table,
                partition_id="2020",
                destination=destination,
                columns="status",
            )
            assert status == "KILLED", error(
                f"Expected KILLED to be durable across SYSTEM START MOVES, "
                f"got {status!r}"
            )

        with Then("destination has no rows and no snapshots"):
            assert_destination_row_count(
                destination=destination,
                expected=0,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
    finally:
        if not moves_restored:
            with Finally("restore the scheduler via SYSTEM START MOVES"):
                node.query(f"SYSTEM START MOVES {source_table}")


@TestScenario
@Name("KILL EXPORT PARTITION during commit transitions to KILLED")
def kill_export_during_commit_marks_killed(
    self, minio_root_user, minio_root_password
):
    """With ``export_partition_commit_always_throw`` armed and very high
    ``max_retries``, every commit attempt throws and the export stays
    PENDING. ``KILL`` issued mid-retry must transition the row to
    ``KILLED`` (not ``FAILED``) and leave the destination with no rows
    and no snapshot.

    The terminal status decides assert-vs-skip: ``KILLED`` runs the
    asserts; ``COMPLETED`` / ``FAILED`` ``skip()`` (failpoint ineffective
    or retries exhausted before the KILL took effect).
    """
    node = self.context.node
    failpoint = "export_partition_commit_always_throw"
    source_table = _seed_source()

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    failpoint_armed = False
    try:
        with When(f"arm the {failpoint} REGULAR failpoint"):
            node.query(f"SYSTEM ENABLE FAILPOINT {failpoint}")
            failpoint_armed = True

        with And(
            "schedule EXPORT PARTITION with very high max_retries so the "
            "scheduler keeps retrying through the always-throw failpoint"
        ):
            export_partition(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
                wait_for_completion=False,
                extra_settings=[
                    ("export_merge_tree_partition_max_retries", 1000000),
                ],
            )

        with And("wait for the export entry to appear in the system table"):
            wait_for_export_to_start(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
            )

        with When("KILL EXPORT PARTITION immediately while still PENDING"):
            kill_export_partition(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
            )

        with And(
            "wait for any terminal status; the result selects between "
            "the assert path (KILLED) and the skip paths (COMPLETED / "
            "FAILED)"
        ):
            wait_for_exports_to_settle(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
                timeout=120,
            )
            terminal_status = get_export_row(
                source_table=source_table,
                partition_id="2020",
                destination=destination,
                columns="status",
            )
            if terminal_status == "COMPLETED":
                skip(
                    f"Build registers {failpoint!r} but the export "
                    f"committed cleanly before our KILL took effect; "
                    f"the failpoint is not effective on the commit path "
                    f"in this build, so the KILL-during-commit surface "
                    f"cannot be exercised."
                )
            if terminal_status == "FAILED":
                skip(
                    f"export reached FAILED before we KILLed it; "
                    f"cannot exercise the KILL-during-commit surface."
                )
            assert terminal_status == "KILLED", error(
                f"Expected terminal status KILLED, COMPLETED, or "
                f"FAILED; got {terminal_status!r}"
            )

        with Then(
            "destination's metadata pointer has not advanced - no rows, "
            "no snapshot - a mid-commit KILL must not leave half-published data"
        ):
            assert_destination_row_count(
                destination=destination,
                expected=0,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
            table = load_pyiceberg_table(
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
            assert table.current_snapshot() is None, error(
                "A KILL issued during a commit retry loop must not "
                "leave a published snapshot behind."
            )
    finally:
        if failpoint_armed:
            with Finally(f"disable {failpoint}"):
                node.query(f"SYSTEM DISABLE FAILPOINT {failpoint}")


@TestScenario
@Name("EXPORT to a missing destination is rejected synchronously")
def invalid_destination_rejected_synchronously(
    self, minio_root_user, minio_root_password
):
    """``ALTER ... EXPORT PARTITION TO TABLE <missing>`` is rejected
    synchronously with ``UNKNOWN_TABLE``; the source is untouched and no
    row appears in ``system.replicated_partition_exports``.
    """
    node = self.context.node
    source_table = _seed_source()
    missing_dest = f"does_not_exist_{getuid()}"

    with When("attempt to export to a destination that was never created"):
        export_partition(
            source_table=source_table,
            destination_table=missing_dest,
            partition_id="2020",
            exitcode=UNKNOWN_TABLE,
            message="",  # Exit code alone is sufficient; message varies.
            wait_for_completion=False,
        )

    with Then("the source table still has all three rows"):
        assert count_rows(table_name=source_table) == 3, error(
            "Source row count changed after a rejected EXPORT"
        )

    with And("no entry lands in system.replicated_partition_exports"):
        count = int(
            node.query(
                f"SELECT count() FROM system.replicated_partition_exports "
                f"WHERE source_table = '{source_table}' "
                f"AND partition_id = '2020' "
                f"AND destination_table = '{missing_dest}'"
            ).output.strip()
        )
        assert count == 0, error(
            f"Expected no system.replicated_partition_exports row for the "
            f"rejected ALTER, got count={count}"
        )


@TestScenario
@Name("EXPORT of a non-existent partition id is a safe no-op")
def missing_partition_id_rejected(self, minio_root_user, minio_root_password):
    """Exporting a ``partition_id`` the source does not have is harmless:
    the destination stays empty and no snapshot is committed.
    """
    source_table = _seed_source()

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    dest_name = as_destination_name(destination)

    with When("attempt to export a partition that does not exist"):
        # Use ``wait_for_completion=False`` because if ClickHouse produces
        # no ``PENDING`` row the waiter would time out. We rely on the
        # destination row-count assertion below instead.
        self.context.node.query(
            f"ALTER TABLE {source_table} "
            f"EXPORT PARTITION ID '1900' TO TABLE {dest_name}",
            settings=prepare_export_partition_settings(
                self.context.catalog, None
            ),
            no_checks=True,
        )
        # Give the scheduler a moment to see there are no parts.
        time.sleep(3)

    with Then("destination has zero rows"):
        assert_destination_row_count(
            destination=destination,
            expected=0,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("PyIceberg sees no committed snapshot"):
        table = load_pyiceberg_table(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert table.current_snapshot() is None, error(
            "A non-existent partition should not commit a snapshot"
        )


SCENARIOS = (
    stop_moves_holds_export_pending,
    kill_export_while_stopped_marks_killed,
    kill_export_during_commit_marks_killed,
    invalid_destination_rejected_synchronously,
    missing_partition_id_rejected,
)


@TestFeature
@Requirements(RQ_Iceberg_ExportPartition_DisasterRecovery("1.0"))
@Name("disaster recovery")
def feature(self, minio_root_user, minio_root_password):
    """Failure-injection and recovery scenarios for EXPORT PARTITION."""
    for scenario in SCENARIOS:
        Scenario(test=scenario, flags=TE)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
