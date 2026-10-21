"""TTL export to a plain S3 table.

Iceberg commits are covered elsewhere. Here the destination is object storage,
so the task is done only when its commit file exists, and a killed task is
retried under that same commit id.
"""

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
    PAUSE_BEFORE_EXPORT,
    BASE_SETTINGS,
    _settings_clause,
    completed_tasks,
    disable_failpoint,
    enable_failpoint,
    insert_values,
    query_lines,
    sync_replicas,
    ttl_tasks,
    wait_exported,
    wait_pending,
)


def _create_s3_ttl(minio_root_user, minio_root_password):
    nodes = list(current().context.nodes[:2])
    suffix = getuid()
    source = f"ttl_src_{suffix}"
    destination = f"ttl_s3_{suffix}"
    url = (
        f"{DEFAULT_S3_ENDPOINT_HOST}/{DEFAULT_S3_WAREHOUSE_BUCKET}/data/"
        f"{destination}/{{_partition_id}}/{{_file}}.parquet"
    )
    settings = _settings_clause(BASE_SETTINGS)
    for node in nodes:
        node.query(
            f"CREATE TABLE {destination} (id Int64, year Int32, event_time DateTime) "
            f"ENGINE = S3('{url}', '{minio_root_user}', '{minio_root_password}', 'Parquet') "
            "PARTITION BY year"
        )
    for index, node in enumerate(nodes):
        replica = f"r{index + 1}"
        node.query(
            f"CREATE TABLE {source} (id Int64, year Int32, event_time DateTime) "
            f"ENGINE = ReplicatedMergeTree('/clickhouse/tables/{source}', '{replica}') "
            "PARTITION BY year ORDER BY id "
            f"TTL event_time + INTERVAL 1 DAY EXPORT TO TABLE {destination} "
            f"SETTINGS {settings}",
            settings=CREATE_SETTINGS,
        )

    def _drop():
        for node in nodes:
            node.query(f"DROP TABLE IF EXISTS {source} SYNC", no_checks=True, steps=False)
            node.query(
                f"DROP TABLE IF EXISTS {destination} SYNC", no_checks=True, steps=False
            )

    current().context.cleanup(_drop)
    return {
        "source": source,
        "destination": destination,
        "nodes": nodes,
        "engine": "replicated",
        "user": minio_root_user,
        "password": minio_root_password,
    }


def _marker(node, source):
    lines = query_lines(
        node,
        "SELECT committed_marker_file FROM system.distributed_exports "
        f"WHERE source_database = currentDatabase() AND source_table = '{source}' "
        "AND source = 'ttl' AND status = 'COMPLETED' "
        "ORDER BY create_time DESC LIMIT 1",
    )
    return lines[0] if lines else ""


def _s3(node, url, user, password, fmt, structure=None, select="_file"):
    structure_sql = f", '{structure}'" if structure else ""
    return query_lines(
        node,
        f"SELECT {select} FROM s3('{url}', '{user}', '{password}', '{fmt}'{structure_sql})",
    )


def _committed_ids(node, tables):
    """Ids whose parquet file is named by a commit file.

    ``SELECT`` on a partitioned S3 engine table is not implemented, and a
    killed export can leave a parquet object that no commit file names.
    """
    destination = tables["destination"]
    user = tables["user"]
    password = tables["password"]
    base = (
        f"{DEFAULT_S3_ENDPOINT_HOST}/{DEFAULT_S3_WAREHOUSE_BUCKET}/data/{destination}"
    )
    committed = set()
    for line in _s3(node, f"{base}/commit_*", user, password, "LineAsString", select="line"):
        name = line.strip().split("/")[-1]
        if name:
            committed.add(name)
    ids = []
    for line in _s3(
        node,
        f"{base}/**.parquet",
        user,
        password,
        "Parquet",
        structure="id Int64, year Int32, event_time DateTime",
        select="_file, id",
    ):
        filename, row_id = line.split("\t", 1)
        if filename in committed:
            ids.append(int(row_id))
    return sorted(ids), committed


@TestScenario
@Name("S3 destination commits through a marker file")
def s3_destination_commits_once(self, minio_root_user, minio_root_password):
    """A due part is written once. The completed task names the commit file that makes that write visible."""
    tables = _create_s3_ttl(minio_root_user, minio_root_password)
    node = tables["nodes"][0]
    source = tables["source"]

    insert_values(node, source, f"(1, 2020, '{DUE}')")
    sync_replicas(tables)
    wait_exported(node, source, "2020")
    committed_ids, commit_names = _committed_ids(node, tables)
    assert committed_ids == [1], error(commit_names)
    assert len(commit_names) == 1, error(commit_names)
    assert _marker(node, source), error(ttl_tasks(node, source))


@TestScenario
@Name("killed S3 export retries under the same commit id")
def killed_s3_export_reuses_commit_id(self, minio_root_user, minio_root_password):
    """The retry is a new task with the killed task's commit id. The S3 table still has the row once."""
    tables = _create_s3_ttl(minio_root_user, minio_root_password)
    node = tables["nodes"][0]
    source = tables["source"]

    for replica in tables["nodes"]:
        enable_failpoint(replica, PAUSE_BEFORE_EXPORT)
    try:
        insert_values(node, source, f"(1, 2020, '{DUE}')")
        sync_replicas(tables)
        wait_pending(node, source)
        killed = ttl_tasks(node, source)[0]["transaction_id"]
        node.query(f"KILL EXPORT WHERE transaction_id = '{killed}'")

        def is_killed():
            matches = [
                task
                for task in ttl_tasks(node, source)
                if task["transaction_id"] == killed
            ]
            return bool(matches) and matches[0]["status"] == "KILLED"

        from iceberg.tests.export_ttl.steps import wait_until

        wait_until("the S3 export was killed", is_killed, timeout=60)
    finally:
        for replica in tables["nodes"]:
            disable_failpoint(replica, PAUSE_BEFORE_EXPORT)

    wait_exported(node, source, "2020", timeout=180)
    done = completed_tasks(node, source)
    assert len(done) == 1, error(ttl_tasks(node, source))
    assert done[0]["commit_id"] == killed, error(done)
    committed_ids, commit_names = _committed_ids(node, tables)
    assert committed_ids == [1], error(commit_names)
    assert len(commit_names) == 1, error(commit_names)
    assert _marker(node, source), error(done)


@TestFeature
@Name("object storage")
def feature(self, minio_root_user, minio_root_password):
    from iceberg.tests.export_ttl.steps import run_scenarios

    run_scenarios(
        [s3_destination_commits_once, killed_s3_export_reuses_commit_id],
        minio_root_user,
        minio_root_password,
    )
