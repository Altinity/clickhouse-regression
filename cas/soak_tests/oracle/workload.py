"""SQL emitters for the soak workload.

Each emitter must produce SQL whose effect on ReplicatedMergeTree is exactly what
``Model.apply`` does, so a quiesced checkpoint can be asserted op-for-op.

``ts`` is a Unix-seconds value; the table column is ``DateTime64(3)``. Inserting a
bare integer stores ticks as milliseconds, so we emit ``toDateTime64(<ts>,3)``.
"""

from .rowgen import BASE_TIME, insert_rids, row_for_rid

_COLS = ["op_id", "writer", "bucket", "k", "ts", "version", "v", "payload", "row_fp"]


def insert_values_sql(
    seed: int,
    op_id: int,
    n: int,
    table: str,
    base_time: int = BASE_TIME,
    settings: str = "",
) -> str:
    rows = [row_for_rid(seed, rid, base_time) for rid in insert_rids(op_id, n)]
    tuples = []
    for r in rows:
        tuples.append(
            "({op_id},{writer},{bucket},{k},toDateTime64({ts},3),{version},{v},'{payload}',{row_fp})".format(
                op_id=r["op_id"],
                writer=r["writer"],
                bucket=r["bucket"],
                k=r["k"],
                ts=r["ts"],
                version=r["version"],
                v=r["v"],
                payload=r["payload"],
                row_fp=r["row_fp"],
            )
        )
    cols = ",".join(_COLS)
    # SETTINGS must precede VALUES: after VALUES the parser treats the rest as data.
    settings_clause = f" {settings.strip()}" if settings.strip() else ""
    return f"INSERT INTO {table} ({cols}){settings_clause} VALUES " + ",".join(tuples)


def update_sql(table: str, bucket: int) -> str:
    return (
        f"ALTER TABLE {table} UPDATE v = v + 1, version = version + 1 "
        f"WHERE bucket = {bucket}"
    )


def delete_sql(table: str, bucket: int) -> str:
    return f"ALTER TABLE {table} DELETE WHERE bucket = {bucket}"


def truncate_sql(table: str) -> str:
    return f"TRUNCATE TABLE {table}"


def select_range_sql(table: str, bucket: int, k_lo: int, k_hi: int) -> str:
    """Bounded read that still touches payload so the CAS read path is exercised."""
    return (
        f"SELECT count(), sum(v), max(version), sum(cityHash64(payload)) FROM {table} "
        f"WHERE bucket = {bucket} AND k BETWEEN {k_lo} AND {k_hi}"
    )


def select_recent_sql(table: str, bucket: int, seconds: int) -> str:
    return (
        f"SELECT count(), avg(v), max(version) FROM {table} "
        f"WHERE bucket = {bucket} AND ts >= now() - INTERVAL {seconds} SECOND"
    )
