"""Shared setup for TTL ... EXPORT TO TABLE scenarios.

Tables are created with a short check period and a zero batch window, so a
due part is exported on the next check. Scenarios that need to hold a group
open pass a longer window or ``SYSTEM STOP MOVES``.
"""

import time

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.tests.export_partition.steps.iceberg_destination import (
    DEFAULT_S3_ENDPOINT_HOST,
    DEFAULT_S3_WAREHOUSE_BUCKET,
)


DUE = "2020-01-15 12:00:00"
NOT_DUE = "now()"

CREATE_SETTINGS = [("allow_experimental_export_ttl", 1)]

PAUSE_BEFORE_EXPORT = "export_part_pause_before_schema_validation"
AFTER_COMMIT_BEFORE_COMPLETE = "iceberg_export_after_commit_before_zk_completed"

BASE_SETTINGS = {
    "enable_block_number_column": 1,
    "enable_block_offset_column": 1,
    "ttl_export_check_period_seconds": 1,
}

# The check period is the batch interval. A long period keeps the scheduler
# from shipping a group while a scenario sets one up, after the startup check.
HOLD_SETTINGS = {
    "ttl_export_check_period_seconds": 3600,
}


def _settings_clause(settings):
    parts = []
    for name, value in settings.items():
        if isinstance(value, str):
            parts.append(f"{name} = '{value}'")
        else:
            parts.append(f"{name} = {value}")
    return ", ".join(parts)


def _iceberg_ddl(table, columns, partition_by, url, user, password, if_not_exists=False):
    iff = "IF NOT EXISTS " if if_not_exists else ""
    partition = f"PARTITION BY {partition_by}" if partition_by else ""
    return (
        f"CREATE TABLE {iff}{table} ({columns}) "
        f"ENGINE = IcebergS3('{url}', '{user}', '{password}') "
        f"{partition} SETTINGS s3_retry_attempts = 1"
    )


def query_lines(node, sql):
    # no_checks: a result cell can contain the server's "Exception:" text,
    # which the client wrapper would otherwise treat as a failed query.
    result = node.query(sql, steps=False, no_checks=True, retry_count=0)
    if result.exitcode not in (0, None):
        raise AssertionError(result.output)
    return [line.strip() for line in result.output.splitlines() if line.strip()]


def query_int(node, sql):
    lines = query_lines(node, sql)
    return int(lines[0] if lines else "0")


def query_allowing_error(node, sql, settings=None):
    return node.query(
        sql,
        settings=settings,
        no_checks=True,
        retry_count=0,
        steps=False,
    )


def wait_until(what, predicate, timeout=120, delay=1):
    for attempt in retries(timeout=timeout, delay=delay):
        with attempt:
            assert predicate(), error(what)


def ids(node, table):
    return [int(line) for line in query_lines(node, f"SELECT id FROM {table} ORDER BY id")]


def wait_ids(node, table, expected, timeout=120):
    expected = sorted(expected)

    def ready():
        return ids(node, table) == expected

    wait_until(f"{table} ids are {expected}", ready, timeout=timeout)


def snapshot_count(node, table):
    return query_int(
        node,
        "SELECT count() FROM system.iceberg_history "
        f"WHERE database = currentDatabase() AND table = '{table}'",
    )


def active_parts(node, table, partition_id=None):
    where = f"database = currentDatabase() AND table = '{table}' AND active"
    if partition_id is not None:
        where += f" AND partition_id = '{partition_id}'"
    return query_lines(node, f"SELECT name FROM system.parts WHERE {where} ORDER BY name")


def partition_ids(node, table):
    return query_lines(
        node,
        "SELECT DISTINCT partition_id FROM system.parts "
        f"WHERE database = currentDatabase() AND table = '{table}' AND active "
        "ORDER BY partition_id",
    )


def ttl_rows(node, table):
    columns = (
        "partition_id",
        "exported_parts",
        "claimed_parts",
        "eligible_parts",
        "parts_held_by_delete_gate",
        "last_error",
        "scheduler_replica",
        "current_transaction_id",
    )
    lines = query_lines(
        node,
        f"SELECT {', '.join(columns)} FROM system.ttl_exports "
        f"WHERE database = currentDatabase() AND table = '{table}'",
    )
    rows = {}
    for line in lines:
        fields = line.split("\t")
        # ClickHouse TSV drops a trailing empty field, so the last column
        # (current_transaction_id) is absent while no task is running.
        if len(fields) < 5:
            continue
        fields += [""] * (len(columns) - len(fields))
        row = dict(zip(columns, fields))
        for key in (
            "exported_parts",
            "claimed_parts",
            "eligible_parts",
            "parts_held_by_delete_gate",
        ):
            row[key] = int(row[key] or "0")
        rows[row["partition_id"]] = row
    return rows


def wait_exported(node, table, partition_id, timeout=120):
    def ready():
        row = ttl_rows(node, table).get(partition_id)
        if row is None:
            return False
        return (
            row["exported_parts"] >= 1
            and row["eligible_parts"] == 0
            and row["claimed_parts"] == 0
        )

    wait_until(f"partition {partition_id} of {table} is exported", ready, timeout=timeout)


def wait_last_error(node, table, partition_id, substring, timeout=90):
    def ready():
        row = ttl_rows(node, table).get(partition_id)
        return row is not None and substring in row["last_error"]

    wait_until(
        f"last_error of {table} partition {partition_id} contains {substring!r}",
        ready,
        timeout=timeout,
    )


def ttl_tasks(node, table):
    lines = query_lines(
        node,
        "SELECT transaction_id, status, partition_id, toString(parts), commit_id "
        "FROM system.distributed_exports "
        f"WHERE source_database = currentDatabase() AND source_table = '{table}' "
        "AND source = 'ttl' ORDER BY create_time",
    )
    tasks = []
    for line in lines:
        transaction_id, status, partition_id, parts, commit_id = line.split("\t", 4)
        tasks.append(
            {
                "transaction_id": transaction_id,
                "status": status,
                "partition_id": partition_id,
                "parts": parts,
                "commit_id": commit_id,
            }
        )
    return tasks


def completed_tasks(node, table):
    return [task for task in ttl_tasks(node, table) if task["status"] == "COMPLETED"]


def wait_pending(node, table, timeout=120):
    """Wait until a TTL task is claimed and still running.

    The caller arms ``PAUSE_BEFORE_EXPORT`` first, so the task stays
    pending on whichever replica picked up the part.
    """

    def ready():
        return any(task["status"] == "PENDING" for task in ttl_tasks(node, table))

    wait_until(f"{table} has a pending TTL export", ready, timeout=timeout)


def insert_values(node, table, values):
    node.query(f"INSERT INTO {table} VALUES {values}")


def each(nodes, sql):
    for node in nodes:
        node.query(sql)


def sync_replicas(tables):
    if tables["engine"] != "replicated":
        return
    source = tables["source"]
    for node in tables["nodes"][1:]:
        node.query(f"SYSTEM SYNC REPLICA {source}")


def stop_moves(tables):
    each(tables["nodes"], f"SYSTEM STOP MOVES {tables['source']}")


def start_moves(tables):
    each(tables["nodes"], f"SYSTEM START MOVES {tables['source']}")


def stop_merges(tables):
    each(tables["nodes"], f"SYSTEM STOP MERGES {tables['source']}")


def start_merges(tables):
    each(tables["nodes"], f"SYSTEM START MERGES {tables['source']}")


def optimize_final(node, table, partition_id):
    return query_allowing_error(
        node,
        f"OPTIMIZE TABLE {table} PARTITION ID '{partition_id}' FINAL",
        settings=[("optimize_throw_if_noop", 1)],
    )


def enable_failpoint(node, name):
    node.query(f"SYSTEM ENABLE FAILPOINT {name}", steps=False)


def disable_failpoint(node, name):
    try:
        if node.clickhouse_pid() is None:
            return
    except Exception:
        return
    node.query(
        f"SYSTEM DISABLE FAILPOINT {name}",
        no_checks=True,
        retry_count=0,
        steps=False,
    )


def kill_clickhouse(node):
    node.stop_clickhouse(safe=False, signal="KILL")


def ensure_clickhouse_up(node):
    try:
        if node.clickhouse_pid() is not None:
            return
    except Exception:
        pass
    # A process restart reads config.d again. The suite enables the export
    # server setting at runtime; write it again so a table with an EXPORT TTL
    # can attach.
    node.command(
        "mkdir -p /etc/clickhouse-server/config.d && "
        "cat > /etc/clickhouse-server/config.d/allow_experimental_export_merge_tree_partition.xml <<'EOF'\n"
        "<?xml version=\"1.0\"?>\n"
        "<clickhouse>\n"
        "    <allow_experimental_export_merge_tree_partition>1</allow_experimental_export_merge_tree_partition>\n"
        "</clickhouse>\n"
        "EOF",
        exitcode=0,
    )
    node.start_clickhouse()


def assert_unchanged_for(seconds, predicate, what):
    deadline = time.time() + seconds
    while time.time() < deadline:
        assert predicate(), error(what)
        time.sleep(0.5)


def _drop_created_tables(nodes, source, destination, drop_destination):
    for node in nodes:
        node.query(f"DROP TABLE IF EXISTS {source} SYNC", no_checks=True, steps=False)
        if drop_destination:
            node.query(
                f"DROP TABLE IF EXISTS {destination} SYNC",
                no_checks=True,
                steps=False,
            )


def create_tables(
    columns,
    source_partition_by,
    destination_partition_by,
    ttl,
    minio_root_user,
    minio_root_password,
    engine="replicated",
    nodes=None,
    settings=None,
    order_by="id",
    external_destination=None,
):
    """Create a MergeTree source with an export TTL, and its IcebergS3 destination.

    ``ttl`` is the TTL clause with a ``{destination}`` placeholder. On a
    replicated source the same destination URL is created on every replica;
    later replicas attach to the metadata the first replica wrote.

    ``external_destination`` names a table that already exists (a catalog
    table). No IcebergS3 table is created, and this step does not drop it.
    """
    if nodes is None:
        if engine == "plain":
            nodes = [current().context.node]
        else:
            nodes = list(current().context.nodes[:2])

    suffix = getuid()
    source = f"ttl_src_{suffix}"
    destination = external_destination or f"ttl_dst_{suffix}"
    url = (
        f"{DEFAULT_S3_ENDPOINT_HOST}/{DEFAULT_S3_WAREHOUSE_BUCKET}/data/{destination}/"
    )
    merged = dict(BASE_SETTINGS)
    if settings:
        merged.update(settings)
    partition = f"PARTITION BY {source_partition_by}" if source_partition_by else ""
    ttl_clause = ttl.format(destination=destination)
    replica_names = []

    if external_destination is None:
        for index, node in enumerate(nodes):
            node.query(
                _iceberg_ddl(
                    destination,
                    columns,
                    destination_partition_by,
                    url,
                    minio_root_user,
                    minio_root_password,
                    if_not_exists=(index > 0),
                )
            )

    for index, node in enumerate(nodes):
        if engine == "plain":
            replica = ""
            engine_clause = "MergeTree"
        else:
            replica = f"r{index + 1}"
            engine_clause = f"ReplicatedMergeTree('/clickhouse/tables/{source}', '{replica}')"
        replica_names.append(replica)
        node.query(
            f"CREATE TABLE {source} ({columns}) "
            f"ENGINE = {engine_clause} "
            f"{partition} ORDER BY {order_by} "
            f"TTL {ttl_clause} "
            f"SETTINGS {_settings_clause(merged)}",
            settings=CREATE_SETTINGS,
        )

    tables = {
        "source": source,
        "destination": destination,
        "nodes": nodes,
        "engine": engine,
        "replica_names": replica_names,
        "url": url,
        "columns": columns,
        "destination_partition_by": destination_partition_by,
        "user": minio_root_user,
        "password": minio_root_password,
    }
    current().context.cleanup(
        _drop_created_tables,
        nodes,
        source,
        destination,
        external_destination is None,
    )
    return tables


def recreate_destination(tables, node=None):
    """Attach the Iceberg table again at the same URL after it was dropped.

    ``IF NOT EXISTS`` tells IcebergS3 to keep the metadata already at that
    path instead of refusing with ``TABLE_ALREADY_EXISTS``.
    """
    nodes = [node] if node is not None else tables["nodes"]
    for replica in nodes:
        replica.query(
            _iceberg_ddl(
                tables["destination"],
                tables["columns"],
                tables["destination_partition_by"],
                tables["url"],
                tables["user"],
                tables["password"],
                if_not_exists=True,
            )
        )


def node_for_replica(tables, replica_name):
    for name, node in zip(tables["replica_names"], tables["nodes"]):
        if name == replica_name:
            return node
    raise AssertionError(
        f"scheduler replica {replica_name!r} is not one of {tables['replica_names']}"
    )


def run_scenarios(scenarios, minio_root_user, minio_root_password):
    for scenario in scenarios:
        Scenario(test=scenario, flags=TE)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


def wait_scheduler(tables, timeout=60):
    source = tables["source"]
    node = tables["nodes"][0]

    def ready():
        for row in ttl_rows(node, source).values():
            if row["scheduler_replica"]:
                return True
        return False

    wait_until(f"{source} has a scheduler replica", ready, timeout=timeout)
    for row in ttl_rows(node, source).values():
        if row["scheduler_replica"]:
            return row["scheduler_replica"]
    raise AssertionError(f"{source} lost its scheduler replica")
