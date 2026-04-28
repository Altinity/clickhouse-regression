"""Concurrent / interleaved EXPORT PARTITION scenarios.

ClickHouse serialises Iceberg snapshot commits through ZooKeeper, so even
when several EXPORT PARTITIONs are scheduled at the same time the
destination must end up with a single linear chain of ``append`` snapshots.
These scenarios exercise that property through the interfaces the feature
actually exposes:

* The ``ALTER TABLE ... EXPORT PARTITION ..., EXPORT PARTITION ...``
  multi-statement form - ClickHouse schedules the entries concurrently via
  its internal task queue; each one must still commit an independent
  snapshot.
* Back-to-back ALTERs for the same ``(source, destination, partition)``
  triple - the ZooKeeper idempotency lock rejects everything except the
  winner. The ``duplicate_export_within_ttl_rejected`` scenario in
  ``transactions.py`` covers the single-query variant; here we additionally
  cover the multi-statement variant where the ``(partition, destination)``
  pair is repeated inside one ALTER.
* An asynchronous EXPORT interleaved with an INSERT that lands on the
  source table *after* the ALTER was scheduled but *before* the snapshot
  is committed. The new part must not be pulled into the running export;
  it only shows up on a subsequent export.

The scenarios deliberately avoid TestFlows' ``Pool``-based parallelism
against the same ClickHouse container - TestFlows' pty management is
sensitive to two concurrent bash sessions on the same node and segfaults
the test runner intermittently. The multi-statement ALTER form achieves
the same "several exports in flight simultaneously" effect inside a
single client call, which is the only surface area the feature actually
exposes to end users.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import RQ_Iceberg_ExportPartition_ConcurrentWrites

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    count_rows,
    create_replicated_mergetree,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
    prepare_export_partition_settings,
)
from iceberg.tests.export_partition.steps.export_status import (
    wait_for_export_status,
    wait_for_exports_to_settle,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    as_destination_name,
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.manifest_validation import (
    get_snapshots,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
    assert_source_and_destination_match,
)


SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"

BAD_ARGUMENTS = 36


def _seed_source(values, partition_by=SIMPLE_PARTITION_BY, columns=SIMPLE_COLUMNS):
    """Create a ReplicatedMergeTree and insert a single batch of values."""
    source_table = f"mt_{getuid()}"
    with Given("create the source ReplicatedMergeTree"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=columns,
            partition_by=partition_by,
        )
    with And("insert partitioned values"):
        insert_data(table_name=source_table, values=values)
    return source_table


@TestScenario
@Name("multi-statement ALTER commits each partition as its own snapshot")
def multi_statement_alter_commits_each_partition(
    self, minio_root_user, minio_root_password
):
    """Fire three EXPORT PARTITIONs from a single ALTER statement.

    ClickHouse dispatches the individual EXPORT entries to its export
    task queue concurrently; the Iceberg commit protocol linearises
    them through ZooKeeper. The destination must end up with exactly
    three append snapshots (one per partition), every snapshot must
    carry an ``append`` operation, and the final row count must equal
    the source.
    """
    node = self.context.node
    partitions = ["2020", "2021", "2022"]
    values = ", ".join(
        f"({i * 10 + k}, {year})"
        for i, year in enumerate(partitions)
        for k in range(3)
    )
    source_table = _seed_source(values=values)

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    dest_name = as_destination_name(destination)

    with When("fire a single ALTER with one EXPORT PARTITION per partition"):
        export_clauses = ",\n  ".join(
            f"EXPORT PARTITION ID '{pid}' TO TABLE {dest_name}"
            for pid in partitions
        )
        node.query(
            f"ALTER TABLE {source_table}\n  {export_clauses}",
            settings=prepare_export_partition_settings(
                self.context.catalog, None
            ),
        )

    with And("wait for every export row to report COMPLETED"):
        for pid in partitions:
            wait_for_export_status(
                source_table=source_table,
                destination=destination,
                partition_id=pid,
                expected_status="COMPLETED",
            )

    with Then(f"snapshot log has exactly {len(partitions)} entries"):
        snapshots = get_snapshots(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert len(snapshots) == len(partitions), error(
            f"Expected {len(partitions)} snapshots, got {len(snapshots)}"
        )

    with And("every snapshot records an append operation"):
        for snap in snapshots:
            operation = getattr(snap.summary, "operation", None)
            op_str = str(getattr(operation, "value", operation))
            assert op_str == "append", error(
                f"Expected append snapshot, got {op_str!r} for "
                f"snapshot_id={snap.snapshot_id}"
            )

    with And("destination row count matches the source"):
        expected_rows = count_rows(table_name=source_table)
        assert_destination_row_count(
            destination=destination,
            expected=expected_rows,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert_source_and_destination_match(
            source_table=source_table,
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            order_by="id",
        )


@TestScenario
@Name("duplicate EXPORT inside one ALTER commits at most once")
def duplicate_export_inside_one_alter(
    self, minio_root_user, minio_root_password
):
    """A single ALTER that lists the same partition twice still linearises.

    The multi-statement ALTER form schedules each EXPORT PARTITION entry
    through the same ZooKeeper idempotency lock that guards sequential
    ALTERs: the first entry installs the ZK manifest and commits its
    snapshot, the duplicate entry is rejected with ``BAD_ARGUMENTS``
    ("Export with key ..."). The destination must therefore end up with
    at most one append snapshot (the lock exists precisely to prevent
    the partition's rows from being committed twice).
    """
    node = self.context.node
    source_table = _seed_source(values="(1, 2020), (2, 2020), (3, 2020)")

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    dest_name = as_destination_name(destination)

    with When("issue an ALTER that references partition 2020 twice"):
        node.query(
            f"ALTER TABLE {source_table}\n"
            f"  EXPORT PARTITION ID '2020' TO TABLE {dest_name},\n"
            f"  EXPORT PARTITION ID '2020' TO TABLE {dest_name}",
            settings=prepare_export_partition_settings(
                self.context.catalog, None
            ),
            exitcode=BAD_ARGUMENTS,
            message="Export with key",
            ignore_exception=True,
        )

    with And("drain any background export tasks the ALTER left running"):
        # The parser/scheduler rejects the duplicate entry with
        # BAD_ARGUMENTS but the first entry's background task may still be
        # in flight when the client's ALTER returns. If we inspect the
        # destination now we race PyIceberg's metadata.json read against
        # the snapshot commit and can observe "0 snapshots but 3 rows" -
        # PyIceberg loaded the pre-commit metadata.json while CH's
        # IcebergS3 storage refreshed metadata on SELECT a moment later.
        # Waiting for every matching row in
        # ``system.replicated_partition_exports`` to reach a terminal
        # state (COMPLETED / FAILED / CANCELLED) removes the race.
        wait_for_exports_to_settle(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
        )

    with Then("at most one snapshot was committed (the duplicate was rejected)"):
        snapshots = get_snapshots(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert len(snapshots) <= 1, error(
            f"The ZK lock must reject the duplicate, got "
            f"{len(snapshots)} snapshots: {[s.snapshot_id for s in snapshots]!r}"
        )

    with And("destination row count matches the committed partition once"):
        committed_rows = 0
        if snapshots:
            committed_rows = 3
        assert_destination_row_count(
            destination=destination,
            expected=committed_rows,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestScenario
@Name("INSERT after a scheduled EXPORT does not leak into the snapshot")
def insert_after_scheduled_export_is_isolated(
    self, minio_root_user, minio_root_password
):
    """EXPORT snapshots the active parts at ALTER time.

    Schedule an export with ``wait_for_completion=False``, then
    immediately INSERT a new row into a *different* partition. When the
    original export eventually reports ``COMPLETED`` the destination
    must still only hold the rows that existed at ALTER time; the newly
    inserted partition stays in the source and is only reachable via a
    subsequent export.
    """
    source_table = _seed_source(
        values="(1, 2020), (2, 2020), (3, 2020)"
    )

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("schedule EXPORT PARTITION 2020 without waiting"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            wait_for_completion=False,
        )

    with And("INSERT into a different partition before the export finishes"):
        insert_data(
            table_name=source_table,
            values="(10, 2021), (20, 2021)",
        )

    with And("wait for the scheduled export to complete"):
        wait_for_export_status(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            expected_status="COMPLETED",
        )

    with Then("destination holds exactly the 2020 partition's rows"):
        assert_destination_row_count(
            destination=destination,
            expected=3,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert_destination_row_count(
            destination=destination,
            expected=0,
            where_clause="year = 2021",
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("a follow-up export of 2021 recovers the new rows"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2021",
        )
        assert_destination_row_count(
            destination=destination,
            expected=5,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert_source_and_destination_match(
            source_table=source_table,
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            order_by="id",
        )

    with And(
        "snapshot log has two linearised append snapshots (original + follow-up)"
    ):
        snapshots = get_snapshots(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert len(snapshots) == 2, error(
            f"Expected 2 snapshots after interleaved INSERT + follow-up export, "
            f"got {len(snapshots)}"
        )
        assert snapshots[1].parent_snapshot_id == snapshots[0].snapshot_id, error(
            "Follow-up snapshot must chain to the first"
        )


SCENARIOS = (
    multi_statement_alter_commits_each_partition,
    duplicate_export_inside_one_alter,
    insert_after_scheduled_export_is_isolated,
)


@TestFeature
@Requirements(RQ_Iceberg_ExportPartition_ConcurrentWrites("1.0"))
@Name("concurrent writes")
def feature(self, minio_root_user, minio_root_password):
    """Concurrent / interleaved EXPORT PARTITION scenarios."""
    for scenario in SCENARIOS:
        Scenario(test=scenario, flags=TE)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
