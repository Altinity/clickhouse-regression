"""Partition expression and TTL expression are independent.

A group is the due parts of one source partition. The partition does not have
to be closed, and the TTL does not have to match the partition key. A
destination that is finer than the rows in a group does not export that group.
"""

from collections import defaultdict

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.tests.export_partition.steps.iceberg_destination import (
    DEFAULT_S3_ENDPOINT_HOST,
    DEFAULT_S3_WAREHOUSE_BUCKET,
)

from iceberg.tests.export_ttl.steps import (
    CREATE_SETTINGS,
    DUE,
    NOT_DUE,
    _iceberg_ddl,
    active_parts,
    completed_tasks,
    create_tables,
    ids,
    insert_values,
    optimize_final,
    partition_ids,
    query_allowing_error,
    query_lines,
    start_moves,
    stop_merges,
    stop_moves,
    sync_replicas,
    ttl_rows,
    wait_exported,
    wait_ids,
    wait_last_error,
    assert_unchanged_for,
)


def _monthly_source(ttl, minio_root_user, minio_root_password, destination_partition_by):
    return create_tables(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYYYYMM(event_time)",
        destination_partition_by=destination_partition_by,
        ttl=ttl,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )


@TestScenario
@Name("customer partition exports by event time")
def customer_partition(self, minio_root_user, minio_root_password):
    """``PARTITION BY customer_id`` never closes. Due parts export; a later due insert is its own group."""
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

    insert_values(node, source, f"(1, 1, '{DUE}')")
    insert_values(node, source, f"(2, 1, {NOT_DUE})")
    insert_values(node, source, f"(3, 2, {NOT_DUE})")
    sync_replicas(tables)
    wait_exported(node, source, "1")
    wait_ids(node, destination, [1])
    assert_unchanged_for(
        4,
        lambda: ids(node, destination) == [1],
        "a customer whose rows are not due was exported",
    )
    assert ttl_rows(node, source).get("2", {}).get("exported_parts", 0) == 0, error(
        ttl_rows(node, source)
    )

    with When("another due row arrives for customer 1"):
        insert_values(node, source, "(4, 1, '2020-02-01 00:00:00')")
        sync_replicas(tables)
        wait_ids(node, destination, [1, 4])

    with Then("the not-due row is still absent"):
        assert 2 not in ids(node, destination), error(ids(node, destination))


@TestScenario
@Name("compound partition exports each month on its own")
def compound_partition(self, minio_root_user, minio_root_password):
    """``(customer_id, month)`` keeps January 2020 and the current month apart. Both groups land on ``customer_id``."""
    tables = create_tables(
        columns="id Int64, customer_id Int64, event_time DateTime",
        source_partition_by="(customer_id, toYYYYMM(event_time))",
        destination_partition_by="customer_id",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    insert_values(node, source, f"(1, 7, '{DUE}')")
    insert_values(node, source, f"(2, 7, {NOT_DUE})")
    sync_replicas(tables)
    due_partitions = [
        partition_id
        for partition_id in partition_ids(node, source)
        if partition_id != _partition_of_id(node, source, 2)
    ]
    assert len(due_partitions) == 1, error(partition_ids(node, source))
    wait_exported(node, source, due_partitions[0])
    wait_ids(node, destination, [1])
    assert_unchanged_for(
        4,
        lambda: ids(node, destination) == [1],
        "the current month was exported with January",
    )


def _partition_of_id(node, table, row_id):
    found = query_lines(
        node,
        "SELECT _partition_id FROM "
        f"(SELECT _partition_id FROM {table} WHERE id = {row_id} LIMIT 1)",
    )
    assert found, error(f"no partition for id {row_id}")
    return found[0]


@TestScenario
@Name("monthly partition exports hourly parts into a month")
def monthly_partition_hourly_ttl(self, minio_root_user, minio_root_password):
    """``PARTITION BY toYYYYMM`` with an hourly TTL. The month does not have to close."""
    tables = _monthly_source(
        "event_time + INTERVAL 1 HOUR EXPORT TO TABLE {destination}",
        minio_root_user,
        minio_root_password,
        "toMonthNumSinceEpoch(event_time)",
    )
    _assert_january_exports_and_now_does_not(tables)


@TestScenario
@Name("monthly partition exports toStartOfHour parts into a month")
def monthly_partition_hour_function_ttl(self, minio_root_user, minio_root_password):
    """The TTL is ``toStartOfHour(event_time) + INTERVAL 1 HOUR``. The destination is still the month."""
    tables = _monthly_source(
        "toStartOfHour(event_time) + INTERVAL 1 HOUR EXPORT TO TABLE {destination}",
        minio_root_user,
        minio_root_password,
        "toMonthNumSinceEpoch(event_time)",
    )
    _assert_january_exports_and_now_does_not(tables)


def _assert_january_exports_and_now_does_not(tables):
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]
    stop_moves(tables)
    insert_values(node, source, "(1, '2020-01-05 01:00:00')")
    insert_values(node, source, "(2, '2020-01-05 15:00:00')")
    insert_values(node, source, "(3, '2020-01-20 08:00:00')")
    insert_values(node, source, f"(4, {NOT_DUE})")
    sync_replicas(tables)
    start_moves(tables)
    wait_exported(node, source, "202001")
    wait_ids(node, destination, [1, 2, 3])
    current = _partition_of_id(node, source, 4)
    assert current != "202001", error(current)
    assert_unchanged_for(
        4,
        lambda: ids(node, destination) == [1, 2, 3]
        and ttl_rows(node, source).get(current, {}).get("exported_parts", 0) == 0,
        "the current month was exported",
    )


@TestScenario
@Name("hash partition shares a group inside one bucket")
def hash_partition(self, minio_root_user, minio_root_password):
    """``intHash64(id) % 8``. Customers in one bucket ship together. Another bucket is its own group."""
    tables = create_tables(
        columns="id Int64, event_time DateTime",
        source_partition_by="intHash64(id) % 8",
        destination_partition_by="",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]
    buckets = defaultdict(list)
    for line in query_lines(
        node,
        "SELECT toString(intHash64(number) % 8), toString(number) "
        "FROM numbers(1, 80)",
    ):
        bucket, number = line.split("\t")
        buckets[bucket].append(int(number))
    shared = next(bucket for bucket, members in buckets.items() if len(members) >= 2)
    other = next(bucket for bucket in buckets if bucket != shared)
    left, right = buckets[shared][:2]
    alone = buckets[other][0]

    stop_merges(tables)
    stop_moves(tables)
    insert_values(node, source, f"({left}, '{DUE}')")
    insert_values(node, source, f"({right}, '{DUE}')")
    insert_values(node, source, f"({alone}, '{DUE}')")
    sync_replicas(tables)
    by_partition = {}
    for name in active_parts(node, source):
        found = query_lines(
            node,
            "SELECT partition_id FROM system.parts "
            f"WHERE database = currentDatabase() AND table = '{source}' "
            f"AND name = '{name}' AND active",
        )
        by_partition.setdefault(found[0], []).append(name)
    shared_parts = next(parts for parts in by_partition.values() if len(parts) == 2)
    alone_parts = next(parts for parts in by_partition.values() if len(parts) == 1)
    shared_partition = next(
        partition for partition, parts in by_partition.items() if len(parts) == 2
    )
    alone_partition = next(
        partition for partition, parts in by_partition.items() if len(parts) == 1
    )
    start_moves(tables)
    wait_exported(node, source, shared_partition)
    wait_exported(node, source, alone_partition)
    wait_ids(node, destination, sorted([left, right, alone]))

    shared_tasks = [
        task
        for task in completed_tasks(node, source)
        if task["partition_id"] == shared_partition
    ]
    assert len(shared_tasks) == 1, error(completed_tasks(node, source))
    for name in shared_parts:
        assert name in shared_tasks[0]["parts"], error(shared_tasks)
    other_tasks = [
        task
        for task in completed_tasks(node, source)
        if task["partition_id"] == alone_partition
    ]
    assert len(other_tasks) == 1, error(completed_tasks(node, source))
    assert len(alone_parts) == 1, error(alone_parts)


@TestScenario
@Name("daily destination rejects a part that spans two days")
def daily_destination_rejects_a_span(self, minio_root_user, minio_root_password):
    """A monthly source and an Iceberg day transform. One day exports. A part that covers two days does not."""
    tables = _monthly_source(
        "event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user,
        minio_root_password,
        "toRelativeDayNum(event_time)",
    )
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    insert_values(
        node,
        source,
        "(1, '2020-01-05 01:00:00'), (2, '2020-01-05 23:00:00')",
    )
    insert_values(
        node,
        source,
        "(3, '2020-02-05 10:00:00'), (4, '2020-02-06 10:00:00')",
    )
    sync_replicas(tables)
    wait_exported(node, source, "202001")
    wait_last_error(node, source, "202002", "multiple destination partitions")
    wait_ids(node, destination, [1, 2])
    assert_unchanged_for(
        4,
        lambda: ids(node, destination) == [1, 2],
        "the part that spans two days was exported",
    )


@TestScenario
@Name("daily destination accepts one day at a time")
def daily_destination_one_day_at_a_time(self, minio_root_user, minio_root_password):
    """January 5th exports. January 6th, inserted after that, exports as the next group."""
    tables = _monthly_source(
        "event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user,
        minio_root_password,
        "toRelativeDayNum(event_time)",
    )
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    insert_values(node, source, "(1, '2020-01-05 01:00:00')")
    sync_replicas(tables)
    wait_exported(node, source, "202001")
    wait_ids(node, destination, [1])
    insert_values(node, source, "(2, '2020-01-06 01:00:00')")
    sync_replicas(tables)
    wait_ids(node, destination, [1, 2])
    assert len(completed_tasks(node, source)) == 2, error(completed_tasks(node, source))


@TestScenario
@Name("monthly destination rejects a group that spans two months")
def monthly_destination_rejects_a_span(self, minio_root_user, minio_root_password):
    """``PARTITION BY toYear``. January and February, collected together, do not fit one month."""
    tables = create_tables(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYear(event_time)",
        destination_partition_by="toMonthNumSinceEpoch(event_time)",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    stop_moves(tables)
    insert_values(node, source, "(1, '2020-01-05 00:00:00')")
    insert_values(node, source, "(2, '2020-02-05 00:00:00')")
    sync_replicas(tables)
    assert partition_ids(node, source) == ["2020"], error(partition_ids(node, source))
    start_moves(tables)
    wait_last_error(node, source, "2020", "multiple destination partitions")
    assert_unchanged_for(
        4,
        lambda: ids(node, destination) == [],
        "a group spanning two months was exported",
    )


@TestScenario
@Name("monthly destination accepts one month at a time")
def monthly_destination_one_month_at_a_time(self, minio_root_user, minio_root_password):
    """January exports. February, inserted after that, exports as the next group."""
    tables = create_tables(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYear(event_time)",
        destination_partition_by="toMonthNumSinceEpoch(event_time)",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    insert_values(node, source, "(1, '2020-01-05 00:00:00')")
    sync_replicas(tables)
    wait_exported(node, source, "2020")
    wait_ids(node, destination, [1])
    insert_values(node, source, "(2, '2020-02-05 00:00:00')")
    sync_replicas(tables)
    wait_ids(node, destination, [1, 2])


@TestScenario
@Name("delete waits until the part is exported")
def delete_waits_for_export(self, minio_root_user, minio_root_password):
    """A part that still holds a row not due for export is not deleted. A fully due part is exported, then deleted."""
    tables = create_tables(
        columns="id Int64, customer_id Int64, event_time DateTime",
        source_partition_by="customer_id",
        destination_partition_by="customer_id",
        ttl=(
            "event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}, "
            "event_time + INTERVAL 90 DAY DELETE"
        ),
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    insert_values(node, source, f"(1, 1, '{DUE}'), (2, 1, {NOT_DUE})")
    insert_values(node, source, f"(3, 2, '{DUE}')")
    sync_replicas(tables)
    wait_exported(node, source, "2")
    wait_ids(node, destination, [3])

    with When("OPTIMIZE applies the delete to the exported part"):
        result = optimize_final(node, source, "2")
        assert result.exitcode == 0, error(result.output)

        def deleted():
            return ids(node, source) == [1, 2]

        from iceberg.tests.export_ttl.steps import wait_until

        wait_until("exported rows were deleted from the source", deleted, timeout=60)

    with Then("the mixed part is held and is not in Iceberg"):
        node.query(
            f"ALTER TABLE {source} MATERIALIZE TTL",
            settings=[("mutations_sync", 2)],
        )
        row = ttl_rows(node, source).get("1")
        assert row is not None and row["parts_held_by_delete_gate"] >= 1, error(
            ttl_rows(node, source)
        )
        assert row["exported_parts"] == 0, error(row)
        assert ids(node, destination) == [3], error()


_REFUSALS = (
    (
        "id Int64, event_time DateTime",
        "toYYYYMM(event_time)",
        "id",
        "not part of the source MergeTree partition key",
    ),
    (
        "id Int64, event_time DateTime",
        "toYYYYMM(event_time)",
        "toDayOfWeek(event_time)",
        "is not monotonic",
    ),
    (
        "id Int64, event_time DateTime",
        "toYYYYMM(event_time)",
        "icebergBucket(8, event_time)",
        "partition key of the destination",
    ),
    (
        "id Int64, event_time DateTime",
        "",
        "toYearNumSinceEpoch(event_time)",
        "not part of the source MergeTree partition key",
    ),
)


@TestScenario
@Name("incompatible destination is refused")
def incompatible_destination_is_refused(self, minio_root_user, minio_root_password):
    """CREATE and ALTER both refuse a destination that can never hold a group."""
    node = self.context.node
    for columns, source_partition, dest_partition, substring in _REFUSALS:
        suffix = getuid()
        destination = f"ttl_bad_dst_{suffix}"
        source = f"ttl_bad_src_{suffix}"
        url = (
            f"{DEFAULT_S3_ENDPOINT_HOST}/{DEFAULT_S3_WAREHOUSE_BUCKET}/data/"
            f"{destination}/"
        )
        partition = f"PARTITION BY {source_partition}" if source_partition else ""
        try:
            destination_created = query_allowing_error(
                node,
                _iceberg_ddl(
                    destination,
                    columns,
                    dest_partition,
                    url,
                    minio_root_user,
                    minio_root_password,
                )
            )
            if destination_created.exitcode != 0:
                assert "Exception:" in destination_created.output, error(
                    destination_created.output
                )
                continue
            created = query_allowing_error(
                node,
                f"CREATE TABLE {source} ({columns}) ENGINE = MergeTree "
                f"{partition} ORDER BY id "
                f"TTL event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination} "
                "SETTINGS enable_block_number_column = 1, enable_block_offset_column = 1",
                settings=CREATE_SETTINGS,
            )
            assert created.exitcode != 0, error(created.output)
            assert "BAD_ARGUMENTS" in created.output, error(created.output)
            assert substring in created.output, error(created.output)

            node.query(
                f"CREATE TABLE {source} ({columns}) ENGINE = MergeTree "
                f"{partition} ORDER BY id "
                "TTL event_time + INTERVAL 30 DAY DELETE"
            )
            altered = query_allowing_error(
                node,
                f"ALTER TABLE {source} MODIFY TTL "
                f"event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
                settings=CREATE_SETTINGS,
            )
            assert altered.exitcode != 0, error(altered.output)
            assert "BAD_ARGUMENTS" in altered.output, error(altered.output)
            assert substring in altered.output, error(altered.output)
        finally:
            node.query(f"DROP TABLE IF EXISTS {source} SYNC", no_checks=True)
            node.query(f"DROP TABLE IF EXISTS {destination} SYNC", no_checks=True)


@TestFeature
@Name("partition and ttl")
def feature(self, minio_root_user, minio_root_password):
    from iceberg.tests.export_ttl.steps import run_scenarios

    run_scenarios(
        [
            customer_partition,
            compound_partition,
            monthly_partition_hourly_ttl,
            monthly_partition_hour_function_ttl,
            hash_partition,
            daily_destination_rejects_a_span,
            daily_destination_one_day_at_a_time,
            monthly_destination_rejects_a_span,
            monthly_destination_one_month_at_a_time,
            delete_waits_for_export,
            incompatible_destination_is_refused,
        ],
        minio_root_user,
        minio_root_password,
    )
