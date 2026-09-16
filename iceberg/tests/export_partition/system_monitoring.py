"""Export status system tables and profile-event monitoring.

Verifies that an observer can reconstruct "what happened" from the system
tables alone (column population, part-log entries, profile events) and
that provenance fields survive ``KILL EXPORT PARTITION``.

* ``ReplicatedMergeTree`` — ``system.replicated_partition_exports``
* plain ``MergeTree`` — ``system.partition_exports`` (Altinity/ClickHouse#2032)

Commit-info columns (``committed_metadata_file``, ``committed_manifest_list``,
``committed_manifest_file``, ``committed_marker_file``) are persisted on both
engines (Altinity/ClickHouse#2290): ZooKeeper for ``Replicated*MergeTree``,
the on-disk task descriptor for plain ``MergeTree``.
"""

import os
import re

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import (
    RQ_Iceberg_ExportPartition_SystemMonitoring_ReplicatedPartitionExports,
    RQ_Iceberg_ExportPartition_SystemMonitoring_PartLog,
    RQ_Iceberg_ExportPartition_SystemMonitoring_ProfileEvents,
    RQ_Iceberg_ExportPartition_SystemMonitoring_KilledProvenance,
)

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    SOURCE_ENGINE_PLAIN,
    create_replicated_mergetree,
    insert_data,
    source_engine,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
    kill_export_partition,
)
from iceberg.tests.export_partition.steps.export_status import (
    ALREADY_COMMITTED_SENTINEL,
    EXPORT_COMMIT_INFO_COLUMNS,
    export_kill_provenance_columns,
    export_status_table_display_name,
    export_success_monitoring_columns,
    get_export_commit_info,
    get_export_events,
    get_export_row,
    get_exported_part_log,
    wait_for_export_status,
    wait_for_export_to_start,
    wait_for_exports_to_settle,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    as_system_destination_table,
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.manifest_validation import (
    load_pyiceberg_table,
)


SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"


def _seed_source_two_partitions():
    """Two partitions, each with its own MergeTree part."""
    source_table = f"mt_{getuid()}"
    with Given("create the source table"):
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


def _assert_parts_count_invariants(parts_count, parts_to_do):
    """Shared ``parts_count`` / ``parts_to_do`` bounds for both system tables."""
    pc = int(parts_count)
    ptd = int(parts_to_do)
    assert pc >= 1, error(
        f"parts_count should be >= 1 for a non-empty partition, got {parts_count!r}"
    )
    assert 0 <= ptd <= pc, error(
        f"parts_to_do should be in [0, {pc}], got {parts_to_do!r}"
    )


def _assert_identity_columns(
    fields,
    source_table,
    dest_table_in_system,
    expected_partition_id="2020",
):
    (
        src_tab,
        dest_tab,
        partition_id,
    ) = fields[:3]
    assert src_tab == source_table, error(
        f"source_table mismatch: {src_tab!r} vs {source_table!r}"
    )
    assert dest_tab == dest_table_in_system, error(
        f"destination_table mismatch: {dest_tab!r} vs {dest_table_in_system!r}"
    )
    assert partition_id == expected_partition_id, error(
        f"partition_id mismatch: {partition_id!r}"
    )


# Iceberg metadata basenames ClickHouse recognises in
# ``getMetadataFileAndVersion`` (Utils.cpp):
#   1) v<V>.metadata.json / v<V>-<uuid>.metadata.json
#   2) <V>-<uuid>.metadata.json  (<V> is often zero-padded to 5 digits)
# Optional compression infix: .gz / .gzip / .zstd / .sz before .metadata.json.
_METADATA_BASENAME_RE = re.compile(
    r"^(?:v(?P<hive_version>\d+)(?:-.*)?|(?P<hadoop_version>\d+)-.+)"
    r"(?:\.(?:gz|gzip|zstd|sz))?\.metadata\.json$"
)


def _iceberg_metadata_version(path):
    """Return the integer metadata version, or ``None`` if the basename is not
    one of the two Iceberg metadata naming conventions.
    """
    match = _METADATA_BASENAME_RE.match(os.path.basename(path or ""))
    if not match:
        return None
    return int(match.group("hive_version") or match.group("hadoop_version"))


def _recorded_path_matches_actual(recorded, actual):
    """True if the system-table path names the same object as ``actual``.

    The system table may store a bucket-relative key while PyIceberg reports
    an ``s3://`` URI (or the reverse under ``write_full_path_in_iceberg_metadata``).
    """
    if not recorded or not actual:
        return False
    recorded = recorded.rstrip("/")
    actual = actual.rstrip("/")
    if recorded == actual:
        return True
    if recorded in actual or actual in recorded:
        return True
    return os.path.basename(recorded) == os.path.basename(actual)


def _recorded_metadata_matches_actual(recorded, actual):
    """True if both paths name the same Iceberg metadata file or the same version.

    ClickHouse may persist ``v2.metadata.json`` while a REST catalog rewrites
    the pointer to ``00002-<uuid>.metadata.json`` (or the reverse). Those are
    the same metadata version, not a mismatch.
    """
    if _recorded_path_matches_actual(recorded, actual):
        return True
    rec_ver = _iceberg_metadata_version(recorded)
    act_ver = _iceberg_metadata_version(actual)
    return rec_ver is not None and rec_ver == act_ver


def _assert_commit_info_empty(info, when):
    """All four commit-info columns stay empty until a successful Iceberg commit."""
    assert info is not None, error(f"export row missing {when}")
    for column in EXPORT_COMMIT_INFO_COLUMNS:
        value = info.get(column, "")
        assert not value, error(
            f"{column} should be empty {when}, got {value!r}"
        )


def _assert_iceberg_commit_info_populated(
    info, destination, minio_root_user, minio_root_password
):
    """Iceberg commit-info columns name the files just written."""
    assert info is not None, error("export row missing after COMPLETED")

    metadata = info.get("committed_metadata_file") or ""
    manifest_list = info.get("committed_manifest_list") or ""
    manifest_file = info.get("committed_manifest_file") or ""
    marker = info.get("committed_marker_file") or ""

    assert metadata, error("committed_metadata_file is empty after a successful export")
    assert metadata != ALREADY_COMMITTED_SENTINEL, error(
        f"committed_metadata_file should be a real metadata path on first "
        f"commit, got the already-committed sentinel: {metadata!r}"
    )
    assert not metadata.startswith("<"), error(
        f"committed_metadata_file should be a real metadata path, got {metadata!r}"
    )
    assert _iceberg_metadata_version(metadata) is not None, error(
        f"committed_metadata_file should use an Iceberg metadata name "
        f"(v<V>.metadata.json / v<V>-<uuid>.metadata.json, or "
        f"<V>-<uuid>.metadata.json), got {metadata!r}"
    )

    assert manifest_list, error(
        "committed_manifest_list is empty after a successful Iceberg export"
    )
    assert manifest_list.endswith(".avro"), error(
        f"Expected a *.avro path in committed_manifest_list, got {manifest_list!r}"
    )
    assert os.path.basename(manifest_list).startswith("snap-"), error(
        f"Expected committed_manifest_list basename to start with snap-, "
        f"got {manifest_list!r}"
    )

    assert manifest_file, error(
        "committed_manifest_file is empty after a successful Iceberg export"
    )
    assert manifest_file.endswith(".avro"), error(
        f"Expected a *.avro path in committed_manifest_file, got {manifest_file!r}"
    )
    assert os.path.basename(manifest_file) != os.path.basename(manifest_list), error(
        f"committed_manifest_file should name the manifest, not the manifest "
        f"list: both are {manifest_file!r}"
    )

    assert not marker, error(
        f"committed_marker_file should be empty for an Iceberg destination, "
        f"got {marker!r}"
    )

    table = load_pyiceberg_table(
        destination=destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    location = table.metadata_location or ""
    assert _recorded_metadata_matches_actual(metadata, location), error(
        f"committed_metadata_file {metadata!r} does not match destination "
        f"metadata_location {location!r}"
    )
    snapshot = table.current_snapshot()
    assert snapshot is not None, error(
        "destination has no current snapshot after a successful export"
    )
    snapshot_manifest_list = snapshot.manifest_list or ""
    assert _recorded_path_matches_actual(manifest_list, snapshot_manifest_list), error(
        f"committed_manifest_list {manifest_list!r} does not match snapshot "
        f"manifest_list {snapshot_manifest_list!r}"
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_SystemMonitoring_ReplicatedPartitionExports("1.0")
)
@Name("every export status system table column is populated on success")
def system_table_columns_populated_on_success(
    self, minio_root_user, minio_root_password
):
    """After a clean export, the export status system table carries meaningful
    values (identifiers match, ``parts_to_do`` converged, provenance populated,
    no exceptions).
    """
    source_table = _seed_source_two_partitions()
    status_table = export_status_table_display_name()

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    dest_table_in_system = as_system_destination_table(destination)

    with When("export partition 2020 and wait for completion"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
        )

    with Then(f"collect the row from {status_table} as a single tab-separated record"):
        columns = export_success_monitoring_columns()
        row = get_export_row(
            source_table=source_table,
            partition_id="2020",
            destination=destination,
            columns=columns,
        )
        assert row is not None, error(f"Export row missing from {status_table}")
        fields = row.split("\t")
        expected_field_count = 8 if source_engine() == SOURCE_ENGINE_PLAIN else 9
        assert len(fields) == expected_field_count, error(
            f"Expected {expected_field_count} fields in the system row, "
            f"got {len(fields)}: {fields!r}"
        )

    if source_engine() == SOURCE_ENGINE_PLAIN:
        (
            src_tab,
            dest_tab,
            partition_id,
            status,
            parts_count,
            parts_to_do,
            create_time_unix,
            exception_count,
        ) = fields
        _assert_identity_columns(
            fields, source_table, dest_table_in_system, expected_partition_id="2020"
        )
        with And("parts_count > 0 and parts_to_do stays within bounds"):
            _assert_parts_count_invariants(parts_count, parts_to_do)
        with And("status is COMPLETED and provenance fields are populated"):
            assert status == "COMPLETED", error(f"Unexpected status: {status!r}")
            assert int(create_time_unix) > 0, error(
                f"create_time should be a real timestamp, got {create_time_unix!r}"
            )
            assert int(exception_count) == 0, error(
                f"exception_count should be zero for a clean export, "
                f"got {exception_count!r}"
            )
    else:
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
        ) = fields
        _assert_identity_columns(
            fields, source_table, dest_table_in_system, expected_partition_id="2020"
        )
        with And("parts_count > 0 and parts_to_do stays within bounds"):
            # ``parts_to_do`` is populated from the ZK ``processing`` children
            # on ReplicatedMergeTree; those children are not guaranteed to be
            # pruned the moment ``status`` becomes ``COMPLETED``.
            _assert_parts_count_invariants(parts_count, parts_to_do)
        with And("status is COMPLETED and provenance fields are populated"):
            assert status == "COMPLETED", error(f"Unexpected status: {status!r}")
            assert source_replica, error("source_replica must not be empty")
            assert int(create_time_unix) > 0, error(
                f"create_time should be a real timestamp, got {create_time_unix!r}"
            )
            assert int(exception_count) == 0, error(
                f"exception_count should be zero for a clean export, "
                f"got {exception_count!r}"
            )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_SystemMonitoring_PartLog("1.0"))
@Name("system.part_log records one ExportPart per exported part")
def part_log_records_exported_parts(self, minio_root_user, minio_root_password):
    """Each exported part produces an ``ExportPart`` row in
    ``system.part_log`` on the node that drove the export.
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
    with When("snapshot the part-log count before the export"):
        before = len(get_exported_part_log())

    with And("run the export and wait for completion"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
        )
        node.query("SYSTEM FLUSH LOGS")

    with Then("at least one ExportPart entry was appended"):
        after = get_exported_part_log()
        delta = len(after) - before
        parts_count = int(
            get_export_row(
                source_table=source_table,
                partition_id="2020",
                destination=destination,
                columns="parts_count",
            )
        )
        assert 1 <= delta <= max(parts_count, 1), error(
            f"Expected 1..{parts_count} new ExportPart entries, got {delta}"
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_SystemMonitoring_ProfileEvents("1.0"))
@Name("PartsExports and ExportPartitionZooKeeper* profile events increment")
def profile_events_increment_on_success(self, minio_root_user, minio_root_password):
    """``PartsExports`` increases around a clean export; ``PartsExportFailures``
    does not move. On ``ReplicatedMergeTree`` only, ``ExportPartitionZooKeeperRequests``
    also increases.
    """
    source_table = _seed_source_two_partitions()

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    with When("sample profile events before the export"):
        before = get_export_events()

    with And("run the export and wait for completion"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
        )

    with Then("profile events moved in the expected direction"):
        after = get_export_events()
        parts_count = int(
            get_export_row(
                source_table=source_table,
                partition_id="2020",
                destination=destination,
                columns="parts_count",
            )
        )

        parts_delta = after.get("PartsExports", 0) - before.get("PartsExports", 0)
        assert parts_delta >= parts_count, error(
            f"PartsExports should increase by at least {parts_count}, "
            f"got delta={parts_delta}"
        )

        failure_delta = after.get("PartsExportFailures", 0) - before.get(
            "PartsExportFailures", 0
        )
        assert failure_delta == 0, error(
            f"PartsExportFailures must not move during a clean export, "
            f"got delta={failure_delta}"
        )

        if source_engine() != SOURCE_ENGINE_PLAIN:
            zk_key = "ExportPartitionZooKeeperRequests"
            zk_delta = after.get(zk_key, 0) - before.get(zk_key, 0)
            assert zk_delta > 0, error(
                f"{zk_key} should increase during an export, got delta={zk_delta}"
            )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_SystemMonitoring_KilledProvenance("1.0"))
@Name("KILL EXPORT preserves provenance fields")
def kill_export_preserves_provenance(self, minio_root_user, minio_root_password):
    """``KILL EXPORT PARTITION`` transitions the row to ``KILLED`` and
    preserves provenance from the PENDING row (``create_time`` on plain
    ``MergeTree``; ``source_replica`` + ``create_time`` on
    ``ReplicatedMergeTree``). The export is parked with ``SYSTEM STOP MOVES``.
    """
    node = self.context.node
    status_table = export_status_table_display_name()
    source_table = f"mt_{getuid()}"
    with Given("create the source table"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
    with And("insert one part into partition 2020"):
        insert_data(table_name=source_table, values="(1, 2020), (2, 2020), (3, 2020)")

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    with When("SYSTEM STOP MOVES to keep the export PENDING"):
        node.query(f"SYSTEM STOP MOVES {source_table}")

    moves_restored = False
    pending_provenance = None
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

        with And("sample provenance fields in PENDING"):
            wait_for_export_to_start(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
            )
            pending_row = get_export_row(
                source_table=source_table,
                partition_id="2020",
                destination=destination,
                columns=export_kill_provenance_columns(),
            )
            pending_provenance = pending_row.split("\t")
            if source_engine() == SOURCE_ENGINE_PLAIN:
                (pending_create_time,) = pending_provenance
                assert int(pending_create_time) > 0, error(
                    f"create_time should be populated in PENDING row, "
                    f"got {pending_create_time!r}"
                )
            else:
                pending_replica, pending_create_time = pending_provenance
                assert pending_replica, error("source_replica empty in PENDING row")
                assert int(pending_create_time) > 0, error(
                    f"create_time should be populated in PENDING row, "
                    f"got {pending_create_time!r}"
                )

        with And("KILL EXPORT PARTITION"):
            kill_export_partition(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
            )
            wait_for_export_status(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
                expected_status="KILLED",
                timeout=30,
            )
    finally:
        if not moves_restored:
            with Finally("restore the scheduler"):
                node.query(f"SYSTEM START MOVES {source_table}")

    with Then(f"KILLED row in {status_table} preserves the sampled provenance"):
        killed_row = get_export_row(
            source_table=source_table,
            partition_id="2020",
            destination=destination,
            columns=export_kill_provenance_columns(),
        )
        killed_provenance = killed_row.split("\t")
        if source_engine() == SOURCE_ENGINE_PLAIN:
            (killed_create_time,) = killed_provenance
            (pending_create_time,) = pending_provenance
            assert killed_create_time == pending_create_time, error(
                f"create_time changed after KILL: "
                f"{pending_create_time!r} -> {killed_create_time!r}"
            )
        else:
            killed_replica, killed_create_time = killed_provenance
            pending_replica, pending_create_time = pending_provenance
            assert killed_replica == pending_replica, error(
                f"source_replica changed after KILL: "
                f"{pending_replica!r} -> {killed_replica!r}"
            )
            assert killed_create_time == pending_create_time, error(
                f"create_time changed after KILL: "
                f"{pending_create_time!r} -> {killed_create_time!r}"
            )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_SystemMonitoring_ReplicatedPartitionExports("1.0")
)
@Name("commit-info columns name Iceberg files after success")
def commit_info_columns_populated_on_success(
    self, minio_root_user, minio_root_password
):
    """After COMPLETED, Iceberg commit-info columns name the metadata /
    manifest list / manifest files just written, on both
    ``ReplicatedMergeTree`` and plain ``MergeTree``.

    Gated until Altinity/ClickHouse#2290 lands in a released build.
    """
    source_table = _seed_source_two_partitions()

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export partition 2020 and wait for completion"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
        )

    with Then("Iceberg commit-info columns name the files just written"):
        _assert_iceberg_commit_info_populated(
            get_export_commit_info(
                source_table=source_table,
                partition_id="2020",
                destination=destination,
            ),
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_SystemMonitoring_ReplicatedPartitionExports("1.0")
)
@Name("commit-info columns stay empty before commit")
def commit_info_columns_empty_before_commit(
    self, minio_root_user, minio_root_password
):
    """All four commit-info columns stay empty while the export is
    ``PENDING`` and after it is ``KILLED`` before a successful commit.

    Gated until Altinity/ClickHouse#2290 lands in a released build.
    """
    node = self.context.node
    source_table = f"mt_{getuid()}"
    with Given("create the source table"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
    with And("insert one part into partition 2020"):
        insert_data(table_name=source_table, values="(1, 2020), (2, 2020), (3, 2020)")

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    with When("SYSTEM STOP MOVES to keep the export PENDING"):
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

        with And("commit-info columns stay empty while PENDING"):
            wait_for_export_to_start(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
            )
            _assert_commit_info_empty(
                get_export_commit_info(
                    source_table=source_table,
                    partition_id="2020",
                    destination=destination,
                ),
                when="while PENDING (before commit)",
            )

        with And("KILL EXPORT PARTITION"):
            kill_export_partition(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
            )
            wait_for_export_status(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
                expected_status="KILLED",
                timeout=30,
            )
    finally:
        if not moves_restored:
            with Finally("restore the scheduler"):
                node.query(f"SYSTEM START MOVES {source_table}")

    with Then("commit-info columns stay empty after KILL before commit"):
        _assert_commit_info_empty(
            get_export_commit_info(
                source_table=source_table,
                partition_id="2020",
                destination=destination,
            ),
            when="after KILL (export never committed)",
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_SystemMonitoring_KilledProvenance("1.0"))
@Name("KILL EXPORT during commit preserves provenance and diagnostic fields")
def kill_during_commit_preserves_provenance(self, minio_root_user, minio_root_password):
    """Provenance survives a KILL issued while the export is retrying through the
    ``export_partition_commit_always_throw`` failpoint. Complements
    :func:`kill_export_preserves_provenance` by exercising the in-flight commit
    path rather than STOP MOVES.

    The terminal status decides assert-vs-skip: ``KILLED`` runs the
    provenance asserts; ``COMPLETED`` / ``FAILED`` ``skip()`` (failpoint
    ineffective or retries exhausted before we could KILL).
    """
    node = self.context.node
    status_table = export_status_table_display_name()
    failpoint = "export_partition_commit_always_throw"
    source_table = f"mt_{getuid()}"
    with Given("create the source table"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
    with And("insert one part into partition 2020"):
        insert_data(table_name=source_table, values="(1, 2020), (2, 2020), (3, 2020)")

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    failpoint_armed = False
    in_flight_provenance = None
    try:
        with When(f"arm the {failpoint} REGULAR failpoint"):
            node.query(f"SYSTEM ENABLE FAILPOINT {failpoint}")
            failpoint_armed = True

        with And("schedule EXPORT PARTITION with very high max_retries"):
            export_partition(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
                wait_for_completion=False,
                extra_settings=[
                    ("export_merge_tree_partition_max_retries", 1000000),
                ],
            )

        with And("wait for the export to appear in the system table"):
            wait_for_export_to_start(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
            )

        with And(
            "sample provenance fields from the system table while the "
            "export is still PENDING"
        ):
            in_flight_row = get_export_row(
                source_table=source_table,
                partition_id="2020",
                destination=destination,
                columns=export_kill_provenance_columns(),
            )
            assert in_flight_row, error(
                f"Expected a {status_table} row after wait_for_export_to_start"
            )
            in_flight_provenance = in_flight_row.split("\t")
            if source_engine() == SOURCE_ENGINE_PLAIN:
                (in_flight_create_time,) = in_flight_provenance
                assert int(in_flight_create_time) > 0, error(
                    f"create_time should be populated in the in-flight row, "
                    f"got {in_flight_create_time!r}"
                )
            else:
                in_flight_replica, in_flight_create_time = in_flight_provenance
                assert in_flight_replica, error(
                    "source_replica empty in the in-flight row"
                )
                assert int(in_flight_create_time) > 0, error(
                    f"create_time should be populated in the in-flight row, "
                    f"got {in_flight_create_time!r}"
                )

        with When("KILL EXPORT PARTITION immediately while still PENDING"):
            kill_export_partition(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
            )

        with And(
            "wait for any terminal status; treat the result as the "
            "branch selector for assert-vs-skip"
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
                    f"the failpoint is not effective on the commit "
                    f"path in this build, so the KILL-during-commit "
                    f"surface cannot be exercised."
                )
            if terminal_status == "FAILED":
                skip(
                    f"export reached FAILED before we KILLed it "
                    f"(status={terminal_status!r}); cannot run the "
                    f"KILL-path provenance assertions."
                )
            assert terminal_status == "KILLED", error(
                f"Expected terminal status KILLED, COMPLETED, or "
                f"FAILED; got {terminal_status!r}"
            )
    finally:
        if failpoint_armed:
            with Finally(f"disable {failpoint}"):
                node.query(f"SYSTEM DISABLE FAILPOINT {failpoint}")

    with Then(
        f"KILLED row in {status_table} preserves provenance observed "
        "while the export was still in-flight"
    ):
        killed_row = get_export_row(
            source_table=source_table,
            partition_id="2020",
            destination=destination,
            columns=export_kill_provenance_columns(),
        )
        killed_provenance = killed_row.split("\t")
        if source_engine() == SOURCE_ENGINE_PLAIN:
            (killed_create_time,) = killed_provenance
            (in_flight_create_time,) = in_flight_provenance
            assert killed_create_time == in_flight_create_time, error(
                f"create_time changed across KILL: "
                f"{in_flight_create_time!r} -> {killed_create_time!r}"
            )
        else:
            killed_replica, killed_create_time = killed_provenance
            in_flight_replica, in_flight_create_time = in_flight_provenance
            assert killed_replica == in_flight_replica, error(
                f"source_replica changed across KILL: "
                f"{in_flight_replica!r} -> {killed_replica!r}"
            )
            assert killed_create_time == in_flight_create_time, error(
                f"create_time changed across KILL: "
                f"{in_flight_create_time!r} -> {killed_create_time!r}"
            )


SCENARIOS = (
    system_table_columns_populated_on_success,
    part_log_records_exported_parts,
    profile_events_increment_on_success,
    kill_export_preserves_provenance,
    commit_info_columns_populated_on_success,
    commit_info_columns_empty_before_commit,
    kill_during_commit_preserves_provenance,
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
