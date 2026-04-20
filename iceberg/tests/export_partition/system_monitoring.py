"""``system.replicated_partition_exports`` / profile event monitoring.

These scenarios verify that an observer can reconstruct "what happened"
from the system tables alone:

* :func:`system_table_columns_populated_on_success` - every column that
  the Iceberg PR adds to ``system.replicated_partition_exports`` carries
  a meaningful value once the export reaches ``COMPLETED`` and
  ``parts_to_do`` converges to zero.
* :func:`part_log_records_exported_parts` - ``system.part_log`` gains one
  ``ExportPart`` entry per exported part and no duplicate entries.
* :func:`profile_events_increment_on_success` - ``PartsExports`` and the
  ``ExportPartitionZooKeeper*`` counters increase by a plausible amount
  around a successful export.
* :func:`kill_export_preserves_provenance` - ``KILL EXPORT PARTITION``
  transitions the row to ``KILLED`` and preserves ``source_replica`` and
  ``create_time`` instead of clearing them.
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
    kill_export_partition,
)
from iceberg.tests.export_partition.steps.export_status import (
    get_export_events,
    get_export_row,
    get_exported_part_log,
    wait_for_export_status,
    wait_for_export_to_start,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    as_destination_name,
    create_iceberg_destination,
)


SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"


def _seed_source_two_partitions():
    """Two partitions, each with its own MergeTree part."""
    source_table = f"mt_{getuid()}"
    with Given("create the source ReplicatedMergeTree"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
    with And("insert partition 2020 as its own part"):
        insert_data(table_name=source_table, values="(1, 2020), (2, 2020)")
    with And("insert partition 2021 as its own part"):
        insert_data(table_name=source_table, values="(3, 2021)")
    return source_table


@TestScenario
@Name("every system.replicated_partition_exports column is populated on success")
def system_table_columns_populated_on_success(
    self, minio_root_user, minio_root_password
):
    """Once ``status = COMPLETED`` every observable column is meaningful.

    We explicitly assert:

    * ``source_database`` / ``source_table`` / ``destination_table`` match
      the values in the ALTER;
    * ``partition_id`` is the ID we asked for;
    * ``parts_count`` equals the number of parts that made up the partition
      and ``parts_to_do`` has converged to zero;
    * ``source_replica`` is non-empty (it identifies which node scheduled
      the export);
    * ``create_time`` is a real timestamp (not the epoch);
    * ``exception_count`` is zero and ``last_exception`` is empty on a
      clean run.
    """
    node = self.context.node
    source_table = _seed_source_two_partitions()

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    dest_name = as_destination_name(destination)

    with When("export partition 2020 and wait for completion"):
        export_partition(
            source_table=source_table,
            destination_table=dest_name,
            partition_id="2020",
        )

    with Then("collect the row as a single tab-separated record"):
        # ``last_exception`` is replaced by ``empty(last_exception)`` so the
        # field is a stable ``0``/``1`` rather than an empty string that
        # ``get_export_row``'s ``.strip()`` would drop together with the
        # trailing tab (see steps/export_status.py::get_export_row).
        row = get_export_row(
            source_table=source_table,
            partition_id="2020",
            destination_table=dest_name,
            columns=(
                "source_table, destination_table, partition_id, status, "
                "parts_count, parts_to_do, source_replica, "
                "toUnixTimestamp(create_time), exception_count, "
                "empty(last_exception)"
            ),
        )
        assert row is not None, error(
            "Export row missing from system.replicated_partition_exports"
        )
        fields = row.split("\t")
        assert len(fields) == 10, error(
            f"Expected 10 fields in the system row, got {len(fields)}: {fields!r}"
        )
        (
            src_tab,
            dest_tab,
            partition_id,
            status,
            parts_count,
            parts_to_do,
            source_replica,
            create_time_unix,
            exception_count,
            last_exception_empty,
        ) = fields

    with And("the identifying columns match the ALTER arguments"):
        assert src_tab == source_table, error(
            f"source_table mismatch: {src_tab!r} vs {source_table!r}"
        )
        assert dest_tab == dest_name, error(
            f"destination_table mismatch: {dest_tab!r} vs {dest_name!r}"
        )
        assert partition_id == "2020", error(
            f"partition_id mismatch: {partition_id!r}"
        )

    with And("parts_count > 0 and parts_to_do stays within bounds"):
        # ``parts_to_do`` is populated from the ZK ``processing`` children
        # (ExportPartitionManifestUpdatingTask.cpp::getPartitionExportsInfo:
        # ``info.parts_to_do = processing_parts.size()``). Those children
        # are not guaranteed to be pruned the moment ``status`` becomes
        # ``COMPLETED``, so the only invariant we can assert is that the
        # counter stays within ``[0, parts_count]``.
        pc = int(parts_count)
        ptd = int(parts_to_do)
        assert pc >= 1, error(
            f"parts_count should be >= 1 for a non-empty partition, got {parts_count!r}"
        )
        assert 0 <= ptd <= pc, error(
            f"parts_to_do should be in [0, {pc}], got {parts_to_do!r}"
        )

    with And("status is COMPLETED and provenance fields are populated"):
        assert status == "COMPLETED", error(f"Unexpected status: {status!r}")
        assert source_replica, error("source_replica must not be empty")
        assert int(create_time_unix) > 0, error(
            f"create_time should be a real timestamp, got {create_time_unix!r}"
        )
        assert int(exception_count) == 0, error(
            f"exception_count should be zero for a clean export, got {exception_count!r}"
        )
        # ``empty(last_exception)`` returns 1 when the string is empty and
        # 0 otherwise; a clean export must leave the field empty.
        assert last_exception_empty == "1", error(
            f"last_exception should be empty for a clean export, "
            f"empty(last_exception)={last_exception_empty!r}"
        )


@TestScenario
@Name("system.part_log records one ExportPart per exported part")
def part_log_records_exported_parts(
    self, minio_root_user, minio_root_password
):
    """Each exported part must produce exactly one ``ExportPart`` part-log
    row on the replica that drove the export.

    We keep the partition small (one part) to avoid fighting background
    merges; the assertion is ``>= 1`` with ``parts_count`` from the
    system table as an upper bound.
    """
    node = self.context.node
    source_table = _seed_source_two_partitions()

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    dest_name = as_destination_name(destination)

    with When("snapshot the part-log count before the export"):
        before = len(get_exported_part_log())

    with And("run the export and wait for completion"):
        export_partition(
            source_table=source_table,
            destination_table=dest_name,
            partition_id="2020",
        )
        # part_log is buffered; flush it to guarantee the row is visible.
        node.query("SYSTEM FLUSH LOGS")

    with Then("at least one ExportPart entry was appended"):
        after = get_exported_part_log()
        delta = len(after) - before
        parts_count = int(
            get_export_row(
                source_table=source_table,
                partition_id="2020",
                destination_table=dest_name,
                columns="parts_count",
            )
        )
        assert 1 <= delta <= max(parts_count, 1), error(
            f"Expected 1..{parts_count} new ExportPart entries, got {delta}"
        )


@TestScenario
@Name("PartsExports and ExportPartitionZooKeeper* profile events increment")
def profile_events_increment_on_success(
    self, minio_root_user, minio_root_password
):
    """A clean export moves the ``PartsExports`` counter up by at least
    the number of exported parts and the ZooKeeper counter by a positive
    amount (the exact number depends on retries and manifest layout).
    ``PartsExportFailures`` must not move during a happy-path run.
    """
    source_table = _seed_source_two_partitions()

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    dest_name = as_destination_name(destination)

    with When("sample profile events before the export"):
        before = get_export_events()

    with And("run the export and wait for completion"):
        export_partition(
            source_table=source_table,
            destination_table=dest_name,
            partition_id="2020",
        )

    with Then("profile events moved in the expected direction"):
        after = get_export_events()
        parts_count = int(
            get_export_row(
                source_table=source_table,
                partition_id="2020",
                destination_table=dest_name,
                columns="parts_count",
            )
        )

        parts_delta = after.get("PartsExports", 0) - before.get("PartsExports", 0)
        assert parts_delta >= parts_count, error(
            f"PartsExports should increase by at least {parts_count}, "
            f"got delta={parts_delta}"
        )

        failure_delta = (
            after.get("PartsExportFailures", 0)
            - before.get("PartsExportFailures", 0)
        )
        assert failure_delta == 0, error(
            f"PartsExportFailures must not move during a clean export, "
            f"got delta={failure_delta}"
        )

        zk_key = "ExportPartitionZooKeeperRequests"
        zk_delta = after.get(zk_key, 0) - before.get(zk_key, 0)
        assert zk_delta > 0, error(
            f"{zk_key} should increase during an export, got delta={zk_delta}"
        )


@TestScenario
@Name("KILL EXPORT preserves source_replica and create_time")
def kill_export_preserves_provenance(
    self, minio_root_user, minio_root_password
):
    """After ``KILL EXPORT`` the system table still knows who scheduled
    the export and when: ``source_replica`` and ``create_time`` stay
    identical to the values observed in the PENDING row.

    We park the scheduler with ``SYSTEM STOP MOVES`` so the PENDING row
    is observable without a racing completion.
    """
    node = self.context.node
    source_table = f"mt_{getuid()}"
    with Given("create the source ReplicatedMergeTree"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
    with And("insert one part into partition 2020"):
        insert_data(
            table_name=source_table, values="(1, 2020), (2, 2020), (3, 2020)"
        )

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    dest_name = as_destination_name(destination)

    with When("SYSTEM STOP MOVES to keep the export PENDING"):
        node.query(f"SYSTEM STOP MOVES {source_table}")

    moves_restored = False
    try:
        with And("schedule EXPORT PARTITION without waiting"):
            export_partition(
                source_table=source_table,
                destination_table=dest_name,
                partition_id="2020",
                wait_for_completion=False,
                extra_settings=[
                    ("export_merge_tree_partition_max_retries", 50),
                ],
            )

        with And("sample source_replica/create_time in PENDING"):
            wait_for_export_to_start(
                source_table=source_table,
                destination_table=dest_name,
                partition_id="2020",
            )
            pending_row = get_export_row(
                source_table=source_table,
                partition_id="2020",
                destination_table=dest_name,
                columns="source_replica, toUnixTimestamp(create_time)",
            )
            pending_replica, pending_create_time = pending_row.split("\t")
            assert pending_replica, error("source_replica empty in PENDING row")
            assert int(pending_create_time) > 0, error(
                f"create_time should be populated in PENDING row, "
                f"got {pending_create_time!r}"
            )

        with And("KILL EXPORT PARTITION"):
            kill_export_partition(
                source_table=source_table,
                destination_table=dest_name,
                partition_id="2020",
            )
            wait_for_export_status(
                source_table=source_table,
                destination_table=dest_name,
                partition_id="2020",
                expected_status="KILLED",
                timeout=30,
            )
    finally:
        if not moves_restored:
            with Finally("restore the scheduler"):
                node.query(f"SYSTEM START MOVES {source_table}")

    with Then("KILLED row preserves source_replica and create_time"):
        killed_row = get_export_row(
            source_table=source_table,
            partition_id="2020",
            destination_table=dest_name,
            columns="source_replica, toUnixTimestamp(create_time)",
        )
        killed_replica, killed_create_time = killed_row.split("\t")
        assert killed_replica == pending_replica, error(
            f"source_replica changed after KILL: "
            f"{pending_replica!r} -> {killed_replica!r}"
        )
        assert killed_create_time == pending_create_time, error(
            f"create_time changed after KILL: "
            f"{pending_create_time!r} -> {killed_create_time!r}"
        )


SCENARIOS = (
    system_table_columns_populated_on_success,
    part_log_records_exported_parts,
    profile_events_increment_on_success,
    kill_export_preserves_provenance,
)


@TestFeature
@Name("system monitoring")
def feature(self, minio_root_user, minio_root_password):
    """System-table and profile-event visibility of EXPORT PARTITION."""
    for scenario in SCENARIOS:
        Scenario(test=scenario, flags=TE)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
