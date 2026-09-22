"""Live GC-log / fsck / health probes for scenario cards. No cas.soak imports."""

import time

from cas.soak_tests.oracle.pool import classify_pool_path
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps.http import QueryError

GC_LOG = "system.cas_gc_log"
_GC_COLS = (
    "event_time",
    "gc_id",
    "trigger",
    "round",
    "outcome",
    "objects_deleted",
    "objects_replaced",
    "objects_spared",
    "manifests_deleted",
    "duration_ms",
    "error",
)
RECLAIMABLE = ("blobs", "_manifests")


def _is_missing_table(exc):
    if not isinstance(exc, QueryError):
        return False
    body = exc.body or ""
    return "Code: 60." in body or "UNKNOWN_TABLE" in body


CA_LOG = "system.cas_log"
BAD_EVENT_TYPES = (
    "read_missing",
    "dangling_access",
    "corrupt_dangle",
    "corrupt_decode",
    "snap_journal_incoherent",
    "exception",
)


def ca_event_counts(node, since_event_time=None):
    where = "1"
    if since_event_time:
        where = f"event_time >= '{since_event_time}'"
    out = {"by_event_type": {}, "bad": {}, "rows": 0}
    try:
        txt = node.query(
            f"SELECT event_type, count() FROM {CA_LOG} WHERE {where} "
            f"GROUP BY event_type ORDER BY event_type FORMAT TabSeparated"
        )
    except Exception as e:
        if _is_missing_table(e):
            return out
        raise
    for line in (txt or "").splitlines():
        if "\t" not in line:
            continue
        et, c = line.split("\t", 1)
        try:
            c = int(c)
        except ValueError:
            continue
        out["by_event_type"][et] = c
        out["rows"] += c
        if et in BAD_EVENT_TYPES:
            out["bad"][et] = c
    return out


def ca_event_counts_all(cluster, since_event_time=None):
    per_node = {}
    bad_total = {}
    rows_total = 0
    for n in cluster.nodes():
        c = ca_event_counts(n, since_event_time)
        per_node[n.container] = c
        rows_total += c.get("rows", 0)
        for k, v in c["bad"].items():
            bad_total[k] = bad_total.get(k, 0) + v
    return {"per_node": per_node, "bad_total": bad_total, "rows_total": rows_total}


def event_total(ca_events, event_type):
    total = 0
    for c in ca_events.get("per_node", {}).values():
        total += int(c.get("by_event_type", {}).get(event_type, 0) or 0)
    return total


def gc_log_rows(node, since_event_time=None, poll_tries=3, poll_interval_s=3.0):
    where = "event_type='Finish'"
    if since_event_time:
        where += f" AND event_time >= '{since_event_time}'"
    cols = ", ".join(_GC_COLS)
    last = []
    for attempt in range(max(1, poll_tries)):
        try:
            node.command("SYSTEM FLUSH LOGS")
            txt = node.query(
                f"SELECT {cols} FROM {GC_LOG} WHERE {where} "
                f"ORDER BY event_time FORMAT TabSeparated"
            )
        except Exception as e:
            if not _is_missing_table(e):
                raise
            txt = ""
        rows = []
        for line in (txt or "").splitlines():
            parts = line.split("\t")
            if len(parts) != len(_GC_COLS):
                continue
            d = dict(zip(_GC_COLS, parts))
            for k in _GC_COLS:
                if k not in ("event_time", "gc_id", "trigger", "outcome", "error"):
                    try:
                        d[k] = int(d[k])
                    except (TypeError, ValueError):
                        pass
            rows.append(d)
        last = rows
        if rows or attempt == poll_tries - 1:
            return rows
        time.sleep(poll_interval_s)
    return last


def gc_log_all(cluster, since_event_time=None):
    per_node = {}
    summary = {
        "failed": 0,
        "not_a_leader": 0,
        "success": 0,
        "deleted_total": 0,
        "spared_total": 0,
        "replaced_total": 0,
        "rows_total": 0,
    }
    for n in cluster.nodes():
        rows = gc_log_rows(n, since_event_time)
        per_node[n.container] = rows
        summary["rows_total"] += len(rows)
        for r in rows:
            oc = r.get("outcome", "")
            if oc == "Error":
                summary["failed"] += 1
            elif oc == "NotALeader":
                summary["not_a_leader"] += 1
            elif oc == "Success":
                summary["success"] += 1
            summary["deleted_total"] += int(r.get("objects_deleted", 0) or 0)
            summary["spared_total"] += int(r.get("objects_spared", 0) or 0)
            summary["replaced_total"] += int(r.get("objects_replaced", 0) or 0)
    return {"per_node": per_node, "summary": summary}


def finish_durations(gc_all):
    out = []
    for rows in gc_all.get("per_node", {}).values():
        for r in rows:
            d = r.get("duration_ms")
            if isinstance(d, int):
                out.append(d)
    return out


def parts_summary(node, table):
    def _i(sql):
        try:
            return int(node.scalar(sql) or 0)
        except Exception:
            return 0

    return {
        "active": _i(
            f"SELECT count() FROM system.parts WHERE table='{table}' AND active"
        ),
        "inactive": _i(
            f"SELECT count() FROM system.parts WHERE table='{table}' AND NOT active"
        ),
        "rows": _i(
            f"SELECT sum(rows) FROM system.parts WHERE table='{table}' AND active"
        ),
        "bytes_on_disk": _i(
            f"SELECT sum(bytes_on_disk) FROM system.parts WHERE table='{table}' AND active"
        ),
    }


def wait_cluster_healthy(cluster, timeout_s=240.0, log_fn=print):
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            if all(n.ping() for n in cluster.nodes()):
                for n in cluster.nodes():
                    n.query("SELECT 1", timeout=5)
                return True
        except Exception:
            pass
        time.sleep(1)
    log_fn(f"cluster not healthy within {timeout_s}s")
    return False


def fsck_dangling(fsck):
    if not fsck:
        return None
    try:
        return int(fsck["dangling"])
    except (KeyError, TypeError, ValueError):
        return None


def assert_fsck_clean(result, fsck, *, name="fsck dangling", expected="0", fail_note=""):
    dangling = fsck_dangling(fsck)
    if dangling is None:
        result.add(
            Verdict.inconclusive(
                name, expected, "fsck summary unavailable"
            )
        )
        return
    result.add(
        Verdict.check(
            name, expected, dangling, dangling == 0, "" if dangling == 0 else fail_note
        )
    )


def assert_fsck_count(result, fsck, key, name, expected, ok_fn, fail_note=""):
    try:
        val = int(fsck[key])
    except (KeyError, TypeError, ValueError):
        result.add(Verdict.inconclusive(name, expected, f"fsck {key} unavailable"))
        return
    ok = bool(ok_fn(val))
    result.add(Verdict.check(name, expected, val, ok, "" if ok else fail_note))


def classify_unreachable(fsck_detail):
    buckets = {}
    detail = (fsck_detail or {}).get("detail") or []
    for row in detail:
        if not isinstance(row, dict) or row.get("class") not in ("unreachable",):
            continue
        b = classify_pool_path(row.get("key", ""))
        buckets[b] = buckets.get(b, 0) + 1
    return buckets


def assert_reclaimable_drained(result, verdict_name, residual, fsck_detail=None):
    if residual is None:
        result.add(
            Verdict.inconclusive(
                verdict_name,
                "reclaimable unreachable == 0 (blobs/_manifests)",
                "residual unavailable",
            )
        )
        return
    buckets = classify_unreachable(fsck_detail) if fsck_detail else {}
    reclaimable = sum(buckets.get(p, 0) for p in RECLAIMABLE)
    if residual == 0 or reclaimable == 0:
        result.add(
            Verdict.check(
                verdict_name,
                "reclaimable unreachable == 0 (blobs/_manifests)",
                reclaimable if buckets else residual,
                True,
            )
        )
        return
    if not buckets:
        result.add(
            Verdict.inconclusive(
                verdict_name,
                "reclaimable unreachable == 0 (blobs/_manifests)",
                f"residual={residual} but no fsck detail to classify by prefix",
            )
        )
        return
    result.add(
        Verdict.check(
            verdict_name,
            "reclaimable unreachable == 0 (blobs/_manifests)",
            f"{reclaimable} reclaimable (by_prefix={buckets})",
            False,
        )
    )
