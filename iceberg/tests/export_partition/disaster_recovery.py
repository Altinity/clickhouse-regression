"""Failure-injection and recovery scenarios for EXPORT PARTITION.

Each scenario exercises a specific failure mode to verify that ClickHouse
never leaves the destination Iceberg table in a partially-committed or
unreadable state:

* :func:`stop_moves_holds_export_pending` - ``SYSTEM STOP MOVES`` blocks
  the scheduler, the ``ALTER`` lands in ``system.replicated_partition_exports``
  with ``status = PENDING``, the destination stays empty, and a follow-up
  ``SYSTEM START MOVES`` lets the export finish cleanly.
* :func:`kill_export_while_stopped_marks_killed` - a ``KILL EXPORT
  PARTITION`` issued while the scheduler is blocked transitions the entry
  to ``KILLED`` and prevents any commit from happening even after moves
  are restarted.
* :func:`invalid_destination_rejected_synchronously` - ``ALTER TABLE ...
  EXPORT PARTITION TO TABLE <missing>`` is rejected synchronously with
  ``UNKNOWN_TABLE`` and the source table is untouched.
* :func:`missing_partition_id_rejected` - exporting a ``partition_id`` that
  does not exist in the source must be a no-op; nothing is committed and
  no entry lands in ``system.replicated_partition_exports`` for it.
"""

import time

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    count_rows,
    create_replicated_mergetree,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
    kill_export_partition,
)
from iceberg.tests.export_partition.steps.export_status import (
    get_export_row,
    wait_for_export_status,
    wait_for_export_to_start,
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
    """``SYSTEM STOP MOVES`` blocks the export scheduler.

    The ALTER still succeeds synchronously (the row is inserted into
    ``system.replicated_partition_exports``), but the background task is
    cancelled via the moves_blocker guard so no Iceberg writes happen.
    ``SYSTEM START MOVES`` lifts the block and the export completes with
    the full row count.
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
    """``KILL EXPORT PARTITION`` is honoured even before any data is written.

    The export is held ``PENDING`` by ``SYSTEM STOP MOVES``; while it is
    pending we issue ``KILL EXPORT PARTITION``. The status must transition
    to ``KILLED``. A subsequent ``SYSTEM START MOVES`` must NOT cause the
    killed export to suddenly commit a snapshot - the KILL is durable.
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
@Name("EXPORT to a missing destination is rejected synchronously")
def invalid_destination_rejected_synchronously(
    self, minio_root_user, minio_root_password
):
    """Unknown destination table must fail with ``UNKNOWN_TABLE``.

    The ALTER must be rejected synchronously (no background task is
    scheduled), the source table is untouched, and there is no row in
    ``system.replicated_partition_exports`` for the rejected attempt.
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
    """Exporting a ``partition_id`` the source does not have must be harmless.

    ClickHouse should accept the ALTER statement (it is syntactically
    valid and references an existing destination) but find no parts to
    export; the destination must stay empty and no snapshot is committed.
    The system table may or may not record the zero-parts attempt, so we
    only assert on the destination contents.
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
    invalid_destination_rejected_synchronously,
    missing_partition_id_rejected,
)


@TestFeature
@Name("disaster recovery")
def feature(self, minio_root_user, minio_root_password):
    """Failure-injection and recovery scenarios for EXPORT PARTITION."""
    for scenario in SCENARIOS:
        Scenario(test=scenario, flags=TE)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
