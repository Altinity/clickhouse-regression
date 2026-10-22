"""Late inserts into a partition that was already exported.

A part that has been exported must not merge with one that has not. The new
part is exported on its own, and each id lands in Iceberg once.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.tests.export_ttl.steps import (
    DUE,
    NOT_DUE,
    active_parts,
    completed_tasks,
    create_tables,
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
    wait_scheduler,
    node_for_replica,
    assert_unchanged_for,
)


def _late_insert(engine, minio_root_user, minio_root_password):
    tables = create_tables(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYYYYMM(event_time)",
        destination_partition_by="toMonthNumSinceEpoch(event_time)",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        engine=engine,
    )
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    with When("two due parts of 202001 export"):
        insert_values(node, source, f"(1, '{DUE}')")
        insert_values(node, source, "(2, '2020-01-20 00:00:00')")
        sync_replicas(tables)
        wait_exported(node, source, "202001")
        wait_ids(node, destination, [1, 2])
        snapshots = snapshot_count(node, destination)

    with And("exported parts merge with each other and stay exported"):
        result = optimize_final(node, source, "202001")
        assert len(active_parts(node, source, "202001")) == 1, error(result.output)
        assert ids(node, destination) == [1, 2], error()
        assert snapshot_count(node, destination) == snapshots, error(
            "merging two exported parts exported them again"
        )

    with And("a later 2020 insert cannot merge into the exported part"):
        stop_moves(tables)
        insert_values(node, source, "(3, '2020-01-10 00:00:00')")
        sync_replicas(tables)
        assert_unchanged_for(
            3,
            lambda: len(active_parts(node, source, "202001")) == 2,
            "background merge combined the backfill with an exported part",
        )
        result = optimize_final(node, source, "202001")
        assert result.exitcode != 0, error(result.output)
        assert "different export states" in result.output, error(result.output)
        assert len(active_parts(node, source, "202001")) == 2, error(active_parts(node, source, "202001"))
        assert ids(node, destination) == [1, 2], error()

    with Then("the backfill exports once, in its own group"):
        start_moves(tables)
        wait_ids(node, destination, [1, 2, 3])
        assert snapshot_count(node, destination) == snapshots + 1, error(
            completed_tasks(node, source)
        )


@TestScenario
@Name("late insert does not merge into exported parts")
def late_insert_replicated(self, minio_root_user, minio_root_password):
    """ReplicatedMergeTree. A January 2020 backfill stays a separate part, then reaches Iceberg once."""
    _late_insert("replicated", minio_root_user, minio_root_password)


@TestScenario
@Name("late insert on plain MergeTree")
def late_insert_plain(self, minio_root_user, minio_root_password):
    """Plain MergeTree. Same backfill story, with the export index on local disk."""
    _late_insert("plain", minio_root_user, minio_root_password)


@TestScenario
@Name("late insert on the replica that does not schedule")
def late_insert_on_peer(self, minio_root_user, minio_root_password):
    """The backfill is inserted on the replica that is not ``scheduler_replica``."""
    tables = create_tables(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYYYYMM(event_time)",
        destination_partition_by="toMonthNumSinceEpoch(event_time)",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    source = tables["source"]
    destination = tables["destination"]
    first = tables["nodes"][0]

    insert_values(first, source, f"(1, '{DUE}')")
    sync_replicas(tables)
    wait_exported(first, source, "202001")
    scheduler = wait_scheduler(tables)
    assert scheduler in tables["replica_names"], error(
        f"scheduler_replica {scheduler!r} is not {tables['replica_names']}"
    )
    peer = node_for_replica(
        tables,
        next(name for name in tables["replica_names"] if name != scheduler),
    )

    with When(f"insert the backfill on {peer.name}, scheduler is {scheduler}"):
        insert_values(peer, source, "(2, '2020-01-20 00:00:00')")
        sync_replicas(tables)

    with Then("the row is exported once"):
        wait_ids(first, destination, [1, 2])
        assert ttl_rows(first, source)["202001"]["exported_parts"] >= 1, error()


@TestScenario
@Name("backfill joins an open batch")
def backfill_joins_open_batch(self, minio_root_user, minio_root_password):
    """Two due parts inserted while moves are stopped ship in one group."""
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
    parts = active_parts(node, source, "202001")
    assert len(parts) == 2, error(parts)

    with When("moves start"):
        start_moves(tables)
        wait_ids(node, destination, [1, 2])

    with Then("both parts are in one completed task"):
        done = completed_tasks(node, source)
        assert len(done) == 1, error(ttl_tasks(node, source))
        for name in parts:
            assert name in done[0]["parts"], error(done)


@TestScenario
@Name("backfill stays out of a claimed group")
def backfill_stays_out_of_claimed_group(self, minio_root_user, minio_root_password):
    """A row inserted while a group is claimed is not part of that task."""
    from iceberg.tests.export_ttl.steps import (
        PAUSE_BEFORE_EXPORT,
        disable_failpoint,
        enable_failpoint,
        wait_pending,
    )

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
    for replica in tables["nodes"]:
        enable_failpoint(replica, PAUSE_BEFORE_EXPORT)
    try:
        insert_values(node, source, f"(1, '{DUE}')")
        sync_replicas(tables)
        wait_pending(node, source)
        claimed = ttl_tasks(node, source)
        assert claimed and claimed[0]["status"] == "PENDING", error(claimed)
        first_part = active_parts(node, source, "202001")
        assert len(first_part) == 1, error(first_part)
        assert first_part[0] in claimed[0]["parts"], error(claimed)

        insert_values(node, source, "(2, '2020-01-20 00:00:00')")
        sync_replicas(tables)
        second = [name for name in active_parts(node, source, "202001") if name not in first_part]
        assert len(second) == 1, error(active_parts(node, source, "202001"))
        assert second[0] not in ttl_tasks(node, source)[0]["parts"], error(ttl_tasks(node, source))
        assert len(active_parts(node, source, "202001")) == 2, error()
    finally:
        for replica in tables["nodes"]:
            disable_failpoint(replica, PAUSE_BEFORE_EXPORT)

    start_merges(tables)
    wait_ids(node, destination, [1, 2])
    done = completed_tasks(node, source)
    assert len(done) == 2, error(ttl_tasks(node, source))


def _due_merges_with_not_due(
    source_partition_by, minio_root_user, minio_root_password
):
    tables = create_tables(
        columns="id Int64, event_time DateTime",
        source_partition_by=source_partition_by,
        destination_partition_by="",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    stop_moves(tables)
    stop_merges(tables)
    insert_values(node, source, f"(1, '{DUE}')")
    insert_values(node, source, f"(2, {NOT_DUE})")
    sync_replicas(tables)
    partition_id = partition_id_of(node, source)
    start_merges(tables)
    result = optimize_final(node, source, partition_id)
    assert result.exitcode == 0, error(result.output)
    assert len(active_parts(node, source, partition_id)) == 1, error(result.output)

    with When("moves start"):
        start_moves(tables)

    with Then("the merged part waits, because it still holds a row that is not due"):
        assert_unchanged_for(
            5,
            lambda: ids(node, destination) == [] and completed_tasks(node, source) == [],
            "a part that still holds a row that is not due was exported",
        )


def partition_id_of(node, table):
    from iceberg.tests.export_ttl.steps import partition_ids

    found = partition_ids(node, table)
    assert len(found) == 1, error(found)
    return found[0]


@TestScenario
@Name("due backfill merges with a not-due row of the same customer")
def due_merges_with_not_due_customer(self, minio_root_user, minio_root_password):
    """``PARTITION BY customer_id``. A due part that is not claimed yet may merge with a row that is not due, and then waits."""
    tables = create_tables(
        columns="id Int64, customer_id Int64, event_time DateTime",
        source_partition_by="customer_id",
        destination_partition_by="customer_id",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        order_by="id",
    )
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    stop_moves(tables)
    stop_merges(tables)
    insert_values(node, source, f"(1, 1, '{DUE}')")
    insert_values(node, source, f"(2, 1, {NOT_DUE})")
    start_merges(tables)
    result = optimize_final(node, source, "1")
    assert result.exitcode == 0, error(result.output)
    assert len(active_parts(node, source, "1")) == 1, error(active_parts(node, source, "1"))
    start_moves(tables)
    assert_unchanged_for(
        5,
        lambda: ids(node, destination) == [],
        "customer 1 was exported before its newest row was due",
    )


@TestScenario
@Name("due backfill merges with a not-due row of an unpartitioned table")
def due_merges_with_not_due_unpartitioned(self, minio_root_user, minio_root_password):
    """``PARTITION BY tuple()`` puts every row in one partition, so this wait is the common case."""
    _due_merges_with_not_due("tuple()", minio_root_user, minio_root_password)


@TestScenario
@Name("parts on either side of an exported block stay apart")
def no_merge_across_exported_block(self, minio_root_user, minio_root_password):
    """Plain MergeTree. Two not-due parts with an exported part between them do not merge. After a restart a new due part exports."""
    from iceberg.tests.export_ttl.steps import (
        ensure_clickhouse_up,
        kill_clickhouse,
        partition_ids,
    )

    tables = create_tables(
        columns="id Int64, event_time DateTime",
        source_partition_by="tuple()",
        destination_partition_by="",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        engine="plain",
    )
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    stop_merges(tables)
    insert_values(node, source, f"(1, {NOT_DUE})")
    insert_values(node, source, f"(2, '{DUE}')")
    insert_values(node, source, f"(3, {NOT_DUE})")
    partition_id = partition_ids(node, source)[0]
    wait_exported(node, source, partition_id)
    assert len(active_parts(node, source)) == 3, error(active_parts(node, source))
    start_merges(tables)
    result = optimize_final(node, source, partition_id)
    assert result.exitcode != 0, error(result.output)
    assert len(active_parts(node, source)) == 3, error(active_parts(node, source))
    assert ids(node, destination) == [2], error()

    with When("the node is killed and started again"):
        try:
            kill_clickhouse(node)
        finally:
            ensure_clickhouse_up(node)

    with Then("a new due part exports, and the not-due rows stay in MergeTree"):
        insert_values(node, source, "(4, '2020-06-01 00:00:00')")
        wait_ids(node, destination, [2, 4])


@TestScenario
@Name("late insert into a REST catalog table")
def late_insert_rest_catalog(self, minio_root_user, minio_root_password):
    """The same backfill against an Iceberg REST catalog, on two replicas."""
    import shutil

    from iceberg.tests.export_ttl.steps import wait_until

    if shutil.which("aws") is None:
        skip("the REST catalog helper lists buckets with the aws CLI, which is not installed")

    from helpers.common import getuid
    from iceberg.tests.export_partition.steps.iceberg_destination import (
        create_pyiceberg_catalog_destination,
    )
    from iceberg.tests.export_partition.steps.pyiceberg_schema import (
        ch_columns_to_pyiceberg_schema,
        ch_partition_by_to_pyiceberg_spec,
    )

    previous = getattr(self.context, "catalog", None)
    self.context.catalog = "ice"
    try:
        # Iceberg ``date`` is read back as ``Date32``. ``toYearNumSinceEpoch`` on
        # ``Date32`` is not treated as monotonic unless both ends of the range
        # are known, and at CREATE there are no parts yet. A ``DateTime`` with
        # ``toMonthNumSinceEpoch`` is monotonic with no range required.
        columns = "id Int64, event_time DateTime"
        source_partition_by = "toYYYYMM(event_time)"
        destination_partition_by = "toMonthNumSinceEpoch(event_time)"
        schema, column_id_map = ch_columns_to_pyiceberg_schema(columns)
        suffix = getuid()
        namespace = f"export_ns_{suffix}"
        iceberg_name = f"iceberg_{suffix}"
        database_name = f"datalake_{suffix}"
        create_pyiceberg_catalog_destination(
            schema=schema,
            partition_spec=ch_partition_by_to_pyiceberg_spec(
                destination_partition_by, column_id_map
            ),
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            namespace=namespace,
            table_name=iceberg_name,
            database_name=database_name,
            cluster_name="replicated_cluster",
        )
        # Backticks are escaped so they survive the shell that feeds clickhouse-client.
        dest_sql = f"{database_name}.\\`{namespace}.{iceberg_name}\\`"
        tables = create_tables(
            columns=columns,
            source_partition_by=source_partition_by,
            destination_partition_by=destination_partition_by,
            ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            external_destination=dest_sql,
        )
        node = tables["nodes"][0]
        source = tables["source"]

        def catalog_ids():
            text = node.query(
                f"SELECT id FROM {dest_sql} ORDER BY id", steps=False
            ).output
            return [int(line) for line in text.splitlines() if line.strip()]

        insert_values(
            node,
            source,
            "(1, '2020-01-05 00:00:00'), (2, '2020-01-20 00:00:00')",
        )
        sync_replicas(tables)
        wait_until(
            "REST destination has the first two rows",
            lambda: catalog_ids() == [1, 2],
            timeout=180,
        )
        stop_moves(tables)
        insert_values(node, source, "(3, '2020-01-10 00:00:00')")
        sync_replicas(tables)
        result = optimize_final(node, source, "202001")
        assert result.exitcode != 0, error(result.output)
        assert "different export states" in result.output, error(result.output)
        start_moves(tables)
        wait_until(
            "REST destination has the backfill once",
            lambda: catalog_ids() == [1, 2, 3],
            timeout=180,
        )
    finally:
        self.context.catalog = previous


@TestFeature
@Name("backfill")
def feature(self, minio_root_user, minio_root_password):
    from iceberg.tests.export_ttl.steps import run_scenarios

    run_scenarios(
        [
            late_insert_replicated,
            late_insert_plain,
            late_insert_on_peer,
            backfill_joins_open_batch,
            backfill_stays_out_of_claimed_group,
            due_merges_with_not_due_customer,
            due_merges_with_not_due_unpartitioned,
            no_merge_across_exported_block,
            late_insert_rest_catalog,
        ],
        minio_root_user,
        minio_root_password,
    )
