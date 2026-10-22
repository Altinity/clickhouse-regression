"""A manual EXPORT PARTITION does not update the TTL export index.

The TTL exports those parts again. Iceberg then holds two copies. That is
the same rule as exporting a partition twice by hand.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.tests.export_ttl.steps import (
    DUE,
    HOLD_SETTINGS,
    completed_tasks,
    create_tables,
    ids,
    insert_values,
    query_lines,
    sync_replicas,
    ttl_rows,
    wait_ids,
    wait_until,
)


_MANUAL_SETTINGS = [
    ("allow_experimental_insert_into_iceberg", 1),
    ("allow_experimental_export_merge_tree_part", 1),
]


def _query_statuses(node, table):
    return query_lines(
        node,
        "SELECT status FROM system.distributed_exports "
        f"WHERE source_database = currentDatabase() AND source_table = '{table}' "
        "AND source = 'query' ORDER BY create_time",
    )


@TestScenario
@Name("manual export does not satisfy the TTL")
def manual_export_does_not_satisfy_ttl(self, minio_root_user, minio_root_password):
    """EXPORT PARTITION writes the rows and leaves them eligible. The TTL writes them again."""
    tables = create_tables(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYYYYMM(event_time)",
        destination_partition_by="toMonthNumSinceEpoch(event_time)",
        ttl="event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination}",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        settings=HOLD_SETTINGS,
    )
    node = tables["nodes"][0]
    source = tables["source"]
    destination = tables["destination"]

    insert_values(node, source, f"(1, '{DUE}'), (2, '2020-01-20 00:00:00')")
    sync_replicas(tables)
    wait_until(
        "the partition is visible to the TTL",
        lambda: "202001" in ttl_rows(node, source),
        timeout=60,
    )
    assert ttl_rows(node, source)["202001"]["exported_parts"] == 0, error(
        ttl_rows(node, source)
    )

    with When("EXPORT PARTITION runs while the TTL window is still open"):
        node.query(
            f"ALTER TABLE {source} EXPORT PARTITION ID '202001' TO TABLE {destination}",
            settings=_MANUAL_SETTINGS,
        )
        wait_until(
            "the manual export completed",
            lambda: _query_statuses(node, source) == ["COMPLETED"],
            timeout=180,
        )

    with Then("the TTL still considers the parts not exported"):
        row = ttl_rows(node, source)["202001"]
        assert row["exported_parts"] == 0, error(row)
        assert ids(node, destination) == [1, 2], error()

    with When("the TTL window closes"):
        for replica in tables["nodes"]:
            replica.query(
                f"ALTER TABLE {source} MODIFY SETTING ttl_export_check_period_seconds = 1"
            )
        # The scheduler already slept for the old period. A restart runs the check now.
        from iceberg.tests.export_ttl.steps import ensure_clickhouse_up, kill_clickhouse

        for replica in tables["nodes"]:
            kill_clickhouse(replica)
        for replica in tables["nodes"]:
            ensure_clickhouse_up(replica)
        wait_ids(node, destination, [1, 1, 2, 2], timeout=180)

    with And("the second copy came from a TTL task"):
        assert completed_tasks(node, source), error()
        assert ttl_rows(node, source)["202001"]["exported_parts"] >= 1, error(
            ttl_rows(node, source)
        )


@TestFeature
@Name("manual export")
def feature(self, minio_root_user, minio_root_password):
    from iceberg.tests.export_ttl.steps import run_scenarios

    run_scenarios(
        [manual_export_does_not_satisfy_ttl],
        minio_root_user,
        minio_root_password,
    )
