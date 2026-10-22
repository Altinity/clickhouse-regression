"""Crashes, kills, and a destination that disappears.

Every scenario ends with each due id present in Iceberg once, unless the
scenario is the plain-MergeTree drop, which exports the same rows again.
"""

import time

from testflows.core import *
from testflows.asserts import error

from iceberg.tests.export_ttl.steps import (
    AFTER_COMMIT_BEFORE_COMPLETE,
    DUE,
    PAUSE_BEFORE_EXPORT,
    completed_tasks,
    create_tables,
    disable_failpoint,
    enable_failpoint,
    ensure_clickhouse_up,
    ids,
    insert_values,
    kill_clickhouse,
    node_for_replica,
    query_allowing_error,
    recreate_destination,
    snapshot_count,
    start_moves,
    sync_replicas,
    ttl_rows,
    ttl_tasks,
    active_parts,
    wait_exported,
    wait_ids,
    wait_last_error,
    wait_pending,
    wait_scheduler,
    assert_unchanged_for,
)


def _arm(tables, name):
    for node in tables["nodes"]:
        enable_failpoint(node, name)


def _disarm(tables, name):
    for node in tables["nodes"]:
        ensure_clickhouse_up(node)
        disable_failpoint(node, name)


def _monthly(minio_root_user, minio_root_password, engine="replicated"):
    return create_tables(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYYYYMM(event_time)",
        destination_partition_by="toMonthNumSinceEpoch(event_time)",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        engine=engine,
    )


@TestScenario
@Name("kill during a claimed group resumes the same task")
def kill_during_claimed_group(self, minio_root_user, minio_root_password):
    """The scheduler is killed after a part export has started. The same task completes, and each row lands once."""
    tables = _monthly(minio_root_user, minio_root_password)
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]
    _arm(tables, PAUSE_BEFORE_EXPORT)
    try:
        insert_values(node, source, f"(1, '{DUE}'), (2, '2020-01-20 00:00:00')")
        sync_replicas(tables)
        wait_pending(node, source)
        transaction_id = ttl_tasks(node, source)[0]["transaction_id"]
        kill_clickhouse(node)
    finally:
        _disarm(tables, PAUSE_BEFORE_EXPORT)

    wait_exported(tables["nodes"][0], source, "202001", timeout=180)
    wait_ids(tables["nodes"][0], destination, [1, 2], timeout=180)
    matching = [
        task
        for task in ttl_tasks(tables["nodes"][0], source)
        if task["transaction_id"] == transaction_id
    ]
    assert matching and matching[0]["status"] == "COMPLETED", error(ttl_tasks(tables["nodes"][0], source))


@TestScenario
@Name("commit that landed is not committed again")
def commit_lands_once(self, minio_root_user, minio_root_password):
    """The Iceberg commit lands and the task is not marked complete. The retry finds the transaction and does not append."""
    tables = _monthly(minio_root_user, minio_root_password)
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]
    snapshots = snapshot_count(node, destination)
    _arm(tables, AFTER_COMMIT_BEFORE_COMPLETE)
    try:
        insert_values(node, source, f"(1, '{DUE}'), (2, '2020-01-20 00:00:00')")
        sync_replicas(tables)
        wait_exported(node, source, "202001", timeout=180)
        wait_ids(node, destination, [1, 2], timeout=180)
    finally:
        _disarm(tables, AFTER_COMMIT_BEFORE_COMPLETE)

    assert snapshot_count(node, destination) == snapshots + 1, error(
        completed_tasks(node, source)
    )
    assert ids(node, destination) == [1, 2], error()


@TestScenario
@Name("killing the other replica leaves one copy")
def kill_other_replica(self, minio_root_user, minio_root_password):
    """The replica that is not running the paused export is killed. The group still commits once."""
    tables = _monthly(minio_root_user, minio_root_password)
    node = tables["nodes"][0]
    peer = tables["nodes"][1]
    source = tables["source"]
    destination = tables["destination"]
    _arm(tables, PAUSE_BEFORE_EXPORT)
    try:
        insert_values(node, source, f"(1, '{DUE}')")
        sync_replicas(tables)
        wait_pending(node, source)
        kill_clickhouse(peer)
    finally:
        ensure_clickhouse_up(peer)
        _disarm(tables, PAUSE_BEFORE_EXPORT)

    wait_ids(node, destination, [1], timeout=180)


@TestScenario
@Name("kill the scheduler while a backfill is waiting")
def kill_scheduler_with_backfill_waiting(self, minio_root_user, minio_root_password):
    """A group is claimed, a second due part is inserted, and the scheduler is killed. Each id lands once, and the second part is not in the claimed task."""
    tables = _monthly(minio_root_user, minio_root_password)
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]
    _arm(tables, PAUSE_BEFORE_EXPORT)
    try:
        insert_values(node, source, f"(1, '{DUE}')")
        sync_replicas(tables)
        wait_pending(node, source)
        claimed = ttl_tasks(node, source)[0]
        insert_values(node, source, "(2, '2020-01-20 00:00:00')")
        sync_replicas(tables)
        second_parts = [
            name
            for name in active_parts(node, source, "202001")
            if name not in claimed["parts"]
        ]
        assert second_parts, error(claimed)
        assert all(name not in claimed["parts"] for name in second_parts), error(claimed)
        scheduler = wait_scheduler(tables)
        kill_clickhouse(node_for_replica(tables, scheduler))
    finally:
        _disarm(tables, PAUSE_BEFORE_EXPORT)

    wait_ids(tables["nodes"][0], destination, [1, 2], timeout=180)
    resumed = [
        task
        for task in ttl_tasks(tables["nodes"][0], source)
        if task["transaction_id"] == claimed["transaction_id"]
    ]
    assert resumed, error(ttl_tasks(tables["nodes"][0], source))
    for name in second_parts:
        assert name not in resumed[0]["parts"], error(resumed)


@TestScenario
@Name("restart every replica then backfill")
def restart_every_replica_then_backfill(self, minio_root_user, minio_root_password):
    """Keeper keeps the export index. After every ClickHouse node restarts, exported rows stay put and a backfill exports once."""
    tables = _monthly(minio_root_user, minio_root_password)
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    insert_values(node, source, f"(1, '{DUE}')")
    sync_replicas(tables)
    wait_ids(node, destination, [1])
    snapshots = snapshot_count(node, destination)

    try:
        for replica in tables["nodes"]:
            kill_clickhouse(replica)
    finally:
        for replica in tables["nodes"]:
            ensure_clickhouse_up(replica)

    assert ids(node, destination) == [1], error()
    assert snapshot_count(node, destination) == snapshots, error()
    insert_values(node, source, "(2, '2020-01-20 00:00:00')")
    sync_replicas(tables)
    wait_ids(node, destination, [1, 2], timeout=180)
    assert snapshot_count(node, destination) == snapshots + 1, error()


@TestScenario
@Name("KILL EXPORT retries the group once")
def kill_export_retries_once(self, minio_root_user, minio_root_password):
    """KILL EXPORT of a TTL task makes it retry. The rows land once."""
    tables = _monthly(minio_root_user, minio_root_password)
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]
    _arm(tables, PAUSE_BEFORE_EXPORT)
    try:
        insert_values(node, source, f"(1, '{DUE}')")
        sync_replicas(tables)
        wait_pending(node, source)
        killed = ttl_tasks(node, source)[0]["transaction_id"]
        node.query(f"KILL EXPORT WHERE transaction_id = '{killed}'")

        def is_killed():
            tasks = [
                task for task in ttl_tasks(node, source) if task["transaction_id"] == killed
            ]
            return bool(tasks) and tasks[0]["status"] == "KILLED"

        from iceberg.tests.export_ttl.steps import wait_until

        wait_until("the TTL task was killed", is_killed, timeout=60)
    finally:
        _disarm(tables, PAUSE_BEFORE_EXPORT)

    wait_ids(node, destination, [1], timeout=180)
    done = completed_tasks(node, source)
    assert len(done) == 1, error(ttl_tasks(node, source))
    assert done[0]["transaction_id"] != killed, error(done)


@TestScenario
@Name("STOP MOVES on the scheduler pauses export")
def stop_moves_on_scheduler_pauses(self, minio_root_user, minio_root_password):
    """``SYSTEM STOP MOVES`` on the scheduler replica pauses new groups. Starting moves there resumes them."""
    tables = create_tables(
        columns="id Int64, customer_id Int64, event_time DateTime",
        source_partition_by="customer_id",
        destination_partition_by="customer_id",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    insert_values(node, source, f"(1, 1, now())")
    sync_replicas(tables)
    scheduler = wait_scheduler(tables)
    scheduler_node = node_for_replica(tables, scheduler)
    scheduler_node.query(f"SYSTEM STOP MOVES {source}")
    try:
        insert_values(node, source, f"(2, 2, '{DUE}')")
        sync_replicas(tables)
        time.sleep(5)
        row = ttl_rows(node, source).get("2")
        assert row is None or row["exported_parts"] == 0, error(ttl_rows(node, source))
        assert ids(node, destination) == [], error(ids(node, destination))
    finally:
        start_moves(tables)

    wait_exported(node, source, "2")
    wait_ids(node, destination, [2])


def _dropped_destination(engine, minio_root_user, minio_root_password):
    tables = _monthly(minio_root_user, minio_root_password, engine=engine)
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    insert_values(node, source, f"(1, '{DUE}')")
    sync_replicas(tables)
    wait_exported(node, source, "202001")
    wait_ids(node, destination, [1])

    for replica in tables["nodes"]:
        replica.query(f"DROP TABLE {destination} SYNC")
    insert_values(node, source, "(2, '2020-01-20 00:00:00')")
    sync_replicas(tables)
    wait_last_error(node, source, "202001", "does not exist")
    assert_unchanged_for(
        3,
        lambda: len(completed_tasks(node, source)) == 1,
        "a group committed while the destination was missing",
    )

    recreate_destination(tables)
    wait_ids(node, destination, [1, 2], timeout=180)
    newest = completed_tasks(node, source)[-1]
    assert newest["parts"].count(",") == 0, error(completed_tasks(node, source))


@TestScenario
@Name("plain MergeTree does not export again after the destination is recreated")
def plain_does_not_reexport_after_recreate(self, minio_root_user, minio_root_password):
    """The destination is identified by name. A table created again under that name does not receive the rows again."""
    _dropped_destination("plain", minio_root_user, minio_root_password)


@TestScenario
@Name("replicated table does not export again after the destination is recreated")
def replicated_does_not_reexport_after_recreate(self, minio_root_user, minio_root_password):
    """Same name identity on ReplicatedMergeTree. Only the part that was not exported yet is written."""
    _dropped_destination("replicated", minio_root_user, minio_root_password)


def _year_tables(minio_root_user, minio_root_password):
    return create_tables(
        columns="id Int64, year Int32, event_time DateTime",
        source_partition_by="year",
        destination_partition_by="",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )


@TestScenario
@Name("FORGET PARTITION is refused while a group is in flight")
def forget_partition_refused_while_exporting(self, minio_root_user, minio_root_password):
    """While the part is still active, FORGET PARTITION is refused. The export then finishes.

    The emptiness check runs before the in-flight claim check, so the error is
    ``Partition is not empty`` for as long as the part exists. The claim check
    (``being exported by the EXPORT TTL``) applies once the partition is empty
    and the task still holds it.
    """
    tables = _year_tables(minio_root_user, minio_root_password)
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]
    _arm(tables, PAUSE_BEFORE_EXPORT)
    try:
        insert_values(node, source, f"(1, 2020, '{DUE}')")
        sync_replicas(tables)
        wait_pending(node, source)
        refused = query_allowing_error(
            node, f"ALTER TABLE {source} FORGET PARTITION ID '2020'"
        )
        assert refused.exitcode not in (0, None), error(refused.output)
        assert (
            "not empty" in refused.output
            or "being exported by the EXPORT TTL" in refused.output
        ), error(refused.output)
    finally:
        _disarm(tables, PAUSE_BEFORE_EXPORT)
        wait_ids(node, destination, [1], timeout=180)


@TestScenario
@Name("dropping the destination while a group is pending")
def drop_destination_while_group_is_pending(self, minio_root_user, minio_root_password):
    """The destination disappears after the group is claimed.

    The scheduler skips the group while the table is gone (``DROP`` without
    ``SYNC``, so the drop does not wait on the paused export). Recreating the
    table at the same path exports the part once.
    """
    tables = _year_tables(minio_root_user, minio_root_password)
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]
    _arm(tables, PAUSE_BEFORE_EXPORT)
    try:
        insert_values(node, source, f"(1, 2020, '{DUE}')")
        sync_replicas(tables)
        wait_pending(node, source)
        for replica in tables["nodes"]:
            replica.query(f"DROP TABLE IF EXISTS {destination}", no_checks=True)
    finally:
        _disarm(tables, PAUSE_BEFORE_EXPORT)

    recreate_destination(tables)
    wait_ids(node, destination, [1], timeout=180)


@TestFeature
@Name("crashes")
def feature(self, minio_root_user, minio_root_password):
    from iceberg.tests.export_ttl.steps import run_scenarios

    run_scenarios(
        [
            kill_during_claimed_group,
            commit_lands_once,
            kill_other_replica,
            kill_scheduler_with_backfill_waiting,
            restart_every_replica_then_backfill,
            kill_export_retries_once,
            stop_moves_on_scheduler_pauses,
            plain_does_not_reexport_after_recreate,
            replicated_does_not_reexport_after_recreate,
            forget_partition_refused_while_exporting,
            drop_destination_while_group_is_pending,
        ],
        minio_root_user,
        minio_root_password,
    )
