"""Checkpoint predicates. Pure: no cluster I/O."""

from .fsck import stale_edge_verdict


class CheckpointFailure(Exception):
    pass


AGGREGATE_SQL = (
    "SELECT count(), toUInt64(sum(row_fp)), uniqExact((bucket, k)), sum(v), sum(version), "
    "min(op_id), max(op_id) FROM {table} FORMAT TabSeparated"
)

PIPELINE_CLASSES = ("unreachable", "pending-gc", "awaiting-gc")


def parse_aggregates(tsv: str) -> dict:
    """Parse one replica's aggregate TSV into Model.aggregates keys."""
    row = tsv.strip().split("\t")
    if int(row[0]) == 0:
        return {
            "count": 0,
            "sum_fp": 0,
            "uniq_keys": 0,
            "sum_v": 0,
            "sum_version": 0,
            "min_op": None,
            "max_op": None,
        }
    return {
        "count": int(row[0]),
        "sum_fp": int(row[1]),
        "uniq_keys": int(row[2]),
        "sum_v": int(row[3]),
        "sum_version": int(row[4]),
        "min_op": int(row[5]),
        "max_op": int(row[6]),
    }


def compare_aggregates(model: dict, node1: dict, node2: dict):
    """Raise CheckpointFailure on the first divergence of either replica from the model."""
    for label, got in (("node1", node1), ("node2", node2)):
        for key in (
            "count",
            "sum_fp",
            "uniq_keys",
            "sum_v",
            "sum_version",
            "min_op",
            "max_op",
        ):
            if model.get(key) != got.get(key):
                raise CheckpointFailure(
                    f"{label} {key}: model={model.get(key)} got={got.get(key)}"
                )
    return None


def dryrun_subset_check(detail_rows, dryrun_entries, *, log_fn=None):
    """GC must never preview deletion of a reachable object.

    A dryrun key must either be in a deletion-pipeline class, or absent from
    fsck detail (already deleted, pending fold — tolerated).
    """
    pipeline_keys = {
        row["key"] for row in detail_rows if row["class"] in PIPELINE_CLASSES
    }
    detail_class_by_key = {row["key"]: row["class"] for row in detail_rows}

    already_deleted_count = 0
    for entry in dryrun_entries:
        if entry["key"] not in detail_class_by_key:
            already_deleted_count += 1
        elif entry["key"] not in pipeline_keys:
            other = detail_class_by_key.get(entry["key"], "unknown")
            class_counts = {}
            for row in detail_rows:
                class_counts[row["class"]] = class_counts.get(row["class"], 0) + 1
            raise CheckpointFailure(
                f"dryrun key {entry['key']!r} previews deletion of a non-pipeline blob "
                f"(fsck class={other!r}) — a dryrun key must be in a deletion-pipeline class "
                f"{PIPELINE_CLASSES} (absent-from-detail means the blob is already deleted); "
                f"dryrun_count={len(dryrun_entries)} pipeline_keys={len(pipeline_keys)} "
                f"detail_class_counts={class_counts}"
            )

    if already_deleted_count > 0 and log_fn:
        log_fn(
            f"dryrun: {already_deleted_count} keys already deleted, pending fold — tolerated"
        )
    return already_deleted_count


def is_genuine_hang(
    *,
    backlog_flat: bool,
    active_merges: int,
    errored_queue: int,
    grace_exceeded: bool,
    budget_exceeded: bool,
    absolute_cap_exceeded: bool,
):
    """A flat backlog is a hang only when nothing is executing."""
    if errored_queue > 0:
        return True, "errored"
    if active_merges > 0:
        return False, ""
    if backlog_flat and grace_exceeded and budget_exceeded:
        return True, "idle-flat"
    if absolute_cap_exceeded:
        return True, "capped"
    return False, ""


def gc_fixpoint_reached(history: list, stable: int = 2) -> bool:
    if len(history) <= stable:
        return False
    tail = history[-stable:]
    return len(set(tail)) == 1


def require_clean_stale_edge(fsck_result: dict, *, detail: bool):
    verdict, why = stale_edge_verdict(fsck_result, detail=detail)
    if verdict in ("absent", "found"):
        raise CheckpointFailure(f"stale_edge {verdict}: {why}")
    return verdict, why


def wait_for_pool_consistent(
    fsck_fn,
    *,
    timeout_s=180.0,
    stable=2,
    interval_s=3.0,
    sleep_fn=None,
    monotonic_fn=None,
    log_fn=None,
):
    """Poll fsck until dangling==0 is stable, or degrade on flapping-clean (B185)."""
    import time as _time

    sleep_fn = sleep_fn or _time.sleep
    monotonic_fn = monotonic_fn or _time.monotonic
    deadline = monotonic_fn() + timeout_s
    consecutive_clean = 0
    last = None
    last_clean = None
    while True:
        last = fsck_fn()
        clean = (
            last.get("dangling") == 0
            and last.get("exit_code", 0) == 0
            and not last.get("partial")
        )
        if clean:
            last_clean = last
        consecutive_clean = consecutive_clean + 1 if clean else 0
        if consecutive_clean >= stable:
            return last
        if monotonic_fn() > deadline:
            if last_clean is not None:
                if log_fn:
                    log_fn(
                        "WARNING [B185] pool reached dangling==0 but did not hold it; "
                        "continuing on last clean reading"
                    )
                return last_clean
            raise CheckpointFailure(
                f"CA pool never reached dangling==0 within {timeout_s:.0f}s "
                f"(dangling={last.get('dangling')})"
            )
        sleep_fn(interval_s)
