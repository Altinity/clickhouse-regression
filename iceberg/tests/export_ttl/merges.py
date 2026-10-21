"""The export fence has three states: exported, claimed, and not exported.

Exported parts merge only with exported parts. Claimed parts merge with
nothing until the group commits. Parts that are not exported merge with
each other, including a due part that nobody has claimed yet and a part
that is not due.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.tests.export_ttl.steps import (
    DUE,
    NOT_DUE,
    PAUSE_BEFORE_EXPORT,
    active_parts,
    completed_tasks,
    create_tables,
    disable_failpoint,
    enable_failpoint,
    ids,
    insert_values,
    optimize_final,
    snapshot_count,
    start_merges,
    start_moves,
    stop_merges,
    stop_moves,
    sync_replicas,
    ttl_rows,
    ttl_tasks,
    wait_exported,
    wait_ids,
    wait_pending,
    wait_until,
    assert_unchanged_for,
)


@TestScenario
@Name("three export states do not merge in one customer partition")
def three_states_one_partition(self, minio_root_user, minio_root_password):
    """Exported, claimed, and not-due parts of one ``customer_id`` partition stay apart."""
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

    stop_merges(tables)
    insert_values(node, source, f"(1, 1, '{DUE}')")
    sync_replicas(tables)
    wait_exported(node, source, "1")
    wait_ids(node, destination, [1])

    for replica in tables["nodes"]:
        enable_failpoint(replica, PAUSE_BEFORE_EXPORT)
    try:
        insert_values(node, source, f"(2, 1, '{DUE}')")
        sync_replicas(tables)
        wait_pending(node, source)
        assert ttl_rows(node, source)["1"]["claimed_parts"] >= 1, error(ttl_rows(node, source))
        insert_values(node, source, f"(3, 1, {NOT_DUE})")
        sync_replicas(tables)
        assert len(active_parts(node, source, "1")) == 3, error(active_parts(node, source, "1"))
        start_merges(tables)
        result = optimize_final(node, source, "1")
        assert result.exitcode != 0, error(result.output)
        assert len(active_parts(node, source, "1")) == 3, error(active_parts(node, source, "1"))
        assert ids(node, destination) == [1], error()
    finally:
        for replica in tables["nodes"]:
            disable_failpoint(replica, PAUSE_BEFORE_EXPORT)

    wait_ids(node, destination, [1, 2])
    assert_unchanged_for(
        4,
        lambda: 3 not in ids(node, destination),
        "the row that is not due was exported",
    )


@TestScenario
@Name("eligible parts merge before the group is claimed")
def eligible_parts_merge_before_claim(self, minio_root_user, minio_root_password):
    """Two due parts merge while moves are stopped, so the group is not claimed yet, then export as one part."""
    tables = create_tables(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYYYYMM(event_time)",
        destination_partition_by="toMonthNumSinceEpoch(event_time)",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    stop_merges(tables)
    stop_moves(tables)
    insert_values(node, source, f"(1, '{DUE}')")
    insert_values(node, source, "(2, '2020-01-20 00:00:00')")
    sync_replicas(tables)
    start_merges(tables)
    result = optimize_final(node, source, "202001")
    assert result.exitcode == 0, error(result.output)
    merged = active_parts(node, source, "202001")
    assert len(merged) == 1, error(merged)

    with When("moves start"):
        start_moves(tables)
        wait_ids(node, destination, [1, 2])

    with Then("the merged part is the only part in the task"):
        done = completed_tasks(node, source)
        assert len(done) == 1, error(ttl_tasks(node, source))
        assert merged[0] in done[0]["parts"], error(done)


@TestScenario
@Name("exported parts merge and are not exported again")
def exported_parts_merge(self, minio_root_user, minio_root_password):
    """Two exported parts become one part. Iceberg does not gain a snapshot."""
    tables = create_tables(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYYYYMM(event_time)",
        destination_partition_by="toMonthNumSinceEpoch(event_time)",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    stop_merges(tables)
    insert_values(node, source, f"(1, '{DUE}')")
    insert_values(node, source, "(2, '2020-01-20 00:00:00')")
    sync_replicas(tables)
    wait_exported(node, source, "202001")
    wait_ids(node, destination, [1, 2])
    snapshots = snapshot_count(node, destination)
    tasks_before = len(completed_tasks(node, source))
    start_merges(tables)
    result = optimize_final(node, source, "202001")
    assert result.exitcode == 0, error(result.output)
    assert len(active_parts(node, source, "202001")) == 1, error()
    assert_unchanged_for(
        4,
        lambda: snapshot_count(node, destination) == snapshots
        and len(completed_tasks(node, source)) == tasks_before
        and ids(node, destination) == [1, 2],
        "merging exported parts wrote them again",
    )


@TestScenario
@Name("a mutation keeps the part exported")
def mutation_keeps_exported(self, minio_root_user, minio_root_password):
    """ALTER UPDATE rewrites the part under the same block range. It is not exported again."""
    tables = create_tables(
        columns="id Int64, payload String, event_time DateTime",
        source_partition_by="toYYYYMM(event_time)",
        destination_partition_by="toMonthNumSinceEpoch(event_time)",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    insert_values(node, source, f"(1, 'original', '{DUE}')")
    sync_replicas(tables)
    wait_exported(node, source, "202001")
    wait_ids(node, destination, [1])
    snapshots = snapshot_count(node, destination)
    node.query(
        f"ALTER TABLE {source} UPDATE payload = 'changed' WHERE id = 1",
        settings=[("mutations_sync", 2)],
    )
    assert_unchanged_for(
        4,
        lambda: snapshot_count(node, destination) == snapshots
        and ids(node, destination) == [1],
        "the mutated part was exported again",
    )
    assert (
        node.query(f"SELECT payload FROM {destination}").output.strip() == "original"
    ), error()


@TestScenario
@Name("lightweight delete before export writes no row")
def lightweight_delete_before_export(self, minio_root_user, minio_root_password):
    """A part whose rows were all deleted exports nothing. A delete after export leaves Iceberg unchanged."""
    tables = create_tables(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYYYYMM(event_time)",
        destination_partition_by="toMonthNumSinceEpoch(event_time)",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    from iceberg.tests.export_ttl.steps import start_moves, stop_moves

    stop_moves(tables)
    insert_values(node, source, f"(1, '{DUE}')")
    node.query(f"DELETE FROM {source} WHERE id = 1")
    wait_until(
        "the lightweight delete is visible",
        lambda: ids(node, source) == [],
        timeout=60,
    )
    start_moves(tables)
    wait_exported(node, source, "202001")
    assert_unchanged_for(
        4,
        lambda: ids(node, destination) == [],
        "a fully deleted part wrote a row",
    )
    assert completed_tasks(node, source), error(ttl_tasks(node, source))

    insert_values(node, source, "(2, '2020-01-20 00:00:00')")
    sync_replicas(tables)
    wait_ids(node, destination, [2])
    node.query(f"DELETE FROM {source} WHERE id = 2")
    wait_until("id 2 is deleted in the source", lambda: 2 not in ids(node, source), timeout=60)
    assert ids(node, destination) == [2], error()


@TestScenario
@Name("OPTIMIZE on the other replica cannot cross the fence")
def optimize_on_peer_cannot_cross_fence(self, minio_root_user, minio_root_password):
    """The replica that does not schedule still refuses to merge an exported part with one that is not."""
    tables = create_tables(
        columns="id Int64, customer_id Int64, event_time DateTime",
        source_partition_by="customer_id",
        destination_partition_by="customer_id",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    first, peer = tables["nodes"]
    source = tables["source"]
    destination = tables["destination"]

    insert_values(first, source, f"(1, 1, '{DUE}')")
    sync_replicas(tables)
    wait_exported(first, source, "1")
    insert_values(first, source, f"(2, 1, {NOT_DUE})")
    sync_replicas(tables)
    result = optimize_final(peer, source, "1")
    assert result.exitcode != 0, error(result.output)
    assert "different export states" in result.output, error(result.output)
    assert len(active_parts(peer, source, "1")) == 2, error(active_parts(peer, source, "1"))
    assert ids(first, destination) == [1], error()


@TestFeature
@Name("merges")
def feature(self, minio_root_user, minio_root_password):
    from iceberg.tests.export_ttl.steps import run_scenarios

    run_scenarios(
        [
            three_states_one_partition,
            eligible_parts_merge_before_claim,
            exported_parts_merge,
            mutation_keeps_exported,
            lightweight_delete_before_export,
            optimize_on_peer_cannot_cross_fence,
        ],
        minio_root_user,
        minio_root_password,
    )
