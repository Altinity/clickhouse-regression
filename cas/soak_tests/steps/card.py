"""Live helpers for scenario cards. No imports from cas.soak.

Background threads (mid-write GC, RSS sampler) MUST use HTTP, not TestFlows node.query.
"""

import os
import subprocess
import threading
import time

from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.oracle.events import cluster_events_delta
from cas.soak_tests.oracle.pool import POOL_PREFIXES, parse_pool_find
from cas.soak_tests.oracle.verdict import FAIL, Verdict
from cas.soak_tests.steps.checkpoint import (
    assert_pool_is_clean,
    cas_fsck,
    cas_gc_dryrun,
    gc_until_stable,
    quiesce,
)
from cas.soak_tests.steps.http import (
    QueryError,
    http_nodes_from_context,
    retry_on_aborted,
    retry_on_transport,
)
from cas.soak_tests.steps.observe import gc_log_all

CLUSTER = "replicated_cluster"
GC_SQL = "SYSTEM CAS GC RUN ca"
EVENTS_SQL = (
    "SELECT event, value FROM system.events "
    "WHERE event LIKE 'CAS%' OR event LIKE 'DiskS3%' OR event LIKE 'S3%' "
    "FORMAT TabSeparated"
)
RSS_SQL = (
    "SELECT value FROM system.asynchronous_metrics "
    "WHERE metric='MemoryResident' FORMAT TabSeparated"
)
RUSTFS_CONTAINER = os.environ.get(
    "CA_SOAK_TESTS_RUSTFS_CONTAINER", "cas_soak_tests_rustfs"
)
POOL_DIR = os.environ.get("CA_SOAK_TESTS_POOL_DIR", "/data/warehouse/soak_pool")


def run_cas_fsck(**kwargs):
    return cas_fsck(**kwargs)


def drive_gc_until_stable(**kwargs):
    return gc_until_stable(**kwargs)


def run_cas_gc_dryrun(**kwargs):
    return cas_gc_dryrun(**kwargs)


class ClusterView:
    """HTTP-backed replica list with the original soak.cluster shape (nodes/node1/node2)."""

    def __init__(self, http_nodes):
        self.node1 = http_nodes[0]
        self.node2 = http_nodes[1] if len(http_nodes) > 1 else http_nodes[0]
        self._nodes = list(http_nodes)

    def nodes(self):
        return list(self._nodes)


def cluster_from_context(context=None):
    context = context or current().context
    return ClusterView(http_nodes_from_context(context.nodes))


def create_ca_table(
    node,
    name,
    *,
    columns="id UInt64, payload String",
    order_by="id",
    partition_by=None,
    extra_settings=None,
    client_settings=None,
    wide=True,
    ttl=None,
    replica_path=None,
):
    settings = {
        "storage_policy": "'ca'",
        "search_orphaned_parts_disks": "'local'",
    }
    if wide:
        settings["min_bytes_for_wide_part"] = "0"
        settings["min_rows_for_wide_part"] = "0"
    if extra_settings:
        settings.update(extra_settings)
    setting_sql = ", ".join(f"{k}={v}" for k, v in settings.items())
    zk = replica_path or f"/clickhouse/tables/{{shard}}/{name}"
    create = (
        f"CREATE TABLE {name} ON CLUSTER {CLUSTER} ({columns}) "
        f"ENGINE = ReplicatedMergeTree('{zk}', '{{replica}}')"
    )
    if partition_by:
        create += f" PARTITION BY {partition_by}"
    create += f" ORDER BY ({order_by})"
    if ttl:
        create += f" TTL {ttl}"
    create += f" SETTINGS {setting_sql}"
    node.command(f"DROP TABLE IF EXISTS {name} ON CLUSTER {CLUSTER} SYNC", timeout=120)
    node.command(create, timeout=120, settings=client_settings)


def drop_table_both(cluster, name, timeout=120):
    for node in cluster.nodes():
        try:
            node.command(f"DROP TABLE IF EXISTS {name} ON CLUSTER {CLUSTER} SYNC", timeout=timeout)
            return
        except QueryError:
            continue


def drop_tables_like(cluster, like, timeout=120):
    try:
        txt = cluster.node1.query(
            "SELECT name FROM system.tables WHERE database=currentDatabase() "
            f"AND name LIKE '{like}' FORMAT TabSeparated"
        )
    except Exception:
        return
    for name in (txt or "").splitlines():
        if name.strip():
            drop_table_both(cluster, name.strip(), timeout=timeout)


def insert_random(
    node,
    table,
    *,
    rows,
    payload_bytes,
    op_id=0,
    extra_cols_select="",
    timeout=1200.0,
    settings=None,
):
    extra = f", {extra_cols_select}" if extra_cols_select else ""
    sql = (
        f"INSERT INTO {table} "
        f"SELECT {op_id} + number AS id, randomString({payload_bytes}) AS payload{extra} "
        f"FROM numbers({rows})"
    )
    s = {"max_insert_threads": 1}
    if settings:
        s.update(settings)

    def one():
        node.command(sql, timeout=timeout, settings=s)

    retry_on_transport(lambda: retry_on_aborted(one), attempts=5, retry_timeouts=False)


def insert_values(node, table, values_sql, *, timeout=600.0, settings=None):
    """INSERT ... VALUES / INSERT ... SELECT with caller-provided body, retry-wrapped."""
    sql = f"INSERT INTO {table} {values_sql}"

    def one():
        node.command(sql, timeout=timeout, settings=settings)

    retry_on_transport(lambda: retry_on_aborted(one), attempts=5, retry_timeouts=False)


def pool_shape(timeout_s=120.0):
    """Object count + bytes by prefix via `find` inside the RustFS container.

    Timeout/failure yields `_ok=False` with no `_total` — never fake zeros that a card
    could mistake for an empty pool.
    """
    empty = {p: {"objects": 0, "bytes": 0} for p in POOL_PREFIXES}
    empty["other"] = {"objects": 0, "bytes": 0}
    empty["_ok"] = False
    cmd = (
        f"cd {POOL_DIR} 2>/dev/null && find . -type f 2>/dev/null | "
        "xargs -r stat -c '%s\\t%n' 2>/dev/null"
    )
    try:
        proc = subprocess.run(
            [
                "docker",
                "exec",
                RUSTFS_CONTAINER,
                "timeout",
                str(int(timeout_s)),
                "sh",
                "-c",
                cmd,
            ],
            capture_output=True,
            text=True,
            timeout=timeout_s + 10,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return empty
    if proc.returncode != 0 and not proc.stdout:
        return empty
    return parse_pool_find(proc.stdout)


def count_root_dirs(timeout_s=60.0):
    """First-level dirs under soak_pool/roots — proxy for GC namespace fanout."""
    cmd = f"find {POOL_DIR}/roots -maxdepth 1 -type d 2>/dev/null | wc -l"
    try:
        proc = subprocess.run(
            ["docker", "exec", RUSTFS_CONTAINER, "sh", "-c", cmd],
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except Exception:
        return None
    try:
        return max(0, int(proc.stdout.strip().splitlines()[-1]) - 1)
    except (ValueError, IndexError):
        return None


def blob_body_puts(delta):
    return int(delta.get("CASBlobPut", 0) or 0)


def measure_idle_gc_batch(cluster, after_iter, log_fn=print):
    """Drive GC until an idle round (CASGCDelete==0 and CASRootGet==0); return fanout counters."""
    last = {}
    for attempt in range(20):
        before = cluster_events_snapshot(cluster)
        t0 = time.monotonic()
        gc_drive_round(cluster, log_fn=log_fn)
        wall = time.monotonic() - t0
        after = cluster_events_snapshot(cluster)
        delta = cluster_events_delta(before, after).get("_total", {})
        last = {
            "after_iter": after_iter,
            "gc_wall_s": round(wall, 3),
            "drain_rounds": attempt + 1,
            "CASRootList": int(delta.get("CASRootList", 0)),
            "CASRootGet": int(delta.get("CASRootGet", 0)),
            "CASGCGet": int(delta.get("CASGCGet", 0)),
            "CASGCDelete": int(delta.get("CASGCDelete", 0)),
            "root_dirs": count_root_dirs(),
        }
        if last["CASGCDelete"] == 0 and last["CASRootGet"] == 0:
            break
    return last


def manifests_shape(timeout_s=120.0):
    shape = pool_shape(timeout_s=timeout_s)
    if not shape.get("_ok"):
        return {"_ok": False}
    return {
        "_ok": True,
        "_manifests": shape.get("_manifests"),
        "refs": shape.get("refs"),
        "_total": shape.get("_total"),
    }


def gc_drive_round(cluster, timeout=120.0, log_fn=print, node_index=0):
    node = cluster.nodes()[node_index]
    try:
        gc_round(node, timeout=timeout)
        return 1
    except QueryError as e:
        if getattr(e, "is_aborted", False):
            log_fn(f"GC round on {node.container} raced background tick (ABORTED) — benign")
            return 0
        raise


def table_checksum_query(table):
    return (
        f"SELECT count(), sum(sipHash64(*)) FROM {table} FORMAT TabSeparated"
    )


def replicas_agree(cluster, query):
    vals = {}
    for node in cluster.nodes():
        try:
            vals[node.container] = node.query(query).strip()
        except Exception as e:
            vals[node.container] = f"ERROR: {e}"
    distinct = set(vals.values())
    return (
        len(distinct) == 1 and not any(v.startswith("ERROR") for v in vals.values())
    ), vals


def assert_replicas_agree(
    result, cluster, query, name="replica agreement", attempts=5, poll_s=2.0, sleep_fn=time.sleep
):
    agree, vals = replicas_agree(cluster, query)
    for _ in range(max(0, attempts - 1)):
        if agree:
            break
        sleep_fn(poll_s)
        agree, vals = replicas_agree(cluster, query)
    result.observations.setdefault("replica_values", {})[name] = vals
    if not agree and any(str(v).startswith("ERROR") for v in vals.values()):
        result.add(
            Verdict.inconclusive(
                name,
                "all replicas equal",
                f"replica query error after {attempts} samples: {vals}",
            )
        )
        return False
    result.add(
        Verdict.check(
            name,
            "all replicas equal",
            vals,
            agree,
            ""
            if agree
            else (
                f"divergence persisted through {attempts} samples over "
                f"~{poll_s * max(0, attempts - 1):.0f}s: {vals}"
            ),
        )
    )
    return agree


def events_snapshot(node) -> dict:
    try:
        txt = node.query(EVENTS_SQL)
    except Exception:
        return {}
    out = {}
    for line in txt.splitlines():
        if "\t" in line:
            k, v = line.split("\t", 1)
            try:
                out[k] = int(v)
            except ValueError:
                pass
    return out


def cluster_events_snapshot(cluster) -> dict:
    return {n.container: events_snapshot(n) for n in cluster.nodes()}


def counters_window(cluster):
    before = cluster_events_snapshot(cluster)

    def finish():
        after = cluster_events_snapshot(cluster)
        return cluster_events_delta(before, after)

    return finish


def server_memory(node):
    """MemoryResident and MemoryTracking in bytes. A probe gap is None, not 0."""

    def _q(sql):
        try:
            v = node.scalar(sql)
            return int(v) if v not in (None, "") else None
        except Exception:
            return None

    return {
        "mem_resident": _q(
            "SELECT value FROM system.asynchronous_metrics WHERE metric='MemoryResident'"
        ),
        "mem_tracking": _q(
            "SELECT toUInt64(value) FROM system.metrics WHERE metric='MemoryTracking'"
        ),
    }


def cluster_memory(cluster):
    return {n.container: server_memory(n) for n in cluster.nodes()}


def server_rss(node):
    try:
        v = node.scalar(RSS_SQL)
        return int(v) if v not in (None, "") else None
    except Exception:
        return None


def cluster_rss_peak(cluster):
    vals = [server_rss(n) for n in cluster.nodes()]
    present = [v for v in vals if v]
    return max(present) if present else None


class RssSampler(threading.Thread):
    """Poll MemoryResident over HTTP. Safe from a background thread."""

    def __init__(self, cluster, interval_s=2.0):
        super().__init__(daemon=True, name="rss-sampler")
        self.cluster = cluster
        self.interval_s = interval_s
        self.stop_event = threading.Event()
        self.peak_mem_resident = {}
        self.error = None

    def run(self):
        try:
            while not self.stop_event.is_set():
                self._sample()
                self.stop_event.wait(self.interval_s)
            self._sample()
        except Exception as e:
            self.error = e

    def _sample(self):
        for node in self.cluster.nodes():
            rss = server_rss(node)
            if rss is None:
                continue
            self.peak_mem_resident[node.container] = max(
                self.peak_mem_resident.get(node.container, 0), rss
            )

    def start_and_stop(self):
        self.start()
        return self

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.stop()

    def stop(self):
        self.stop_event.set()
        self.join(timeout=10)


def record_peak_memory(result, sampler, *, budget_bytes=None, label="peak MemoryResident"):
    peaks = sampler.peak_mem_resident or {}
    peak = max(peaks.values()) if peaks else None
    if peak is None:
        result.add(Verdict.inconclusive(label, "bounded", "no memory samples collected"))
        return None
    result.observations["peak_mem_resident_by_node"] = peaks
    if budget_bytes is not None:
        ok = peak <= budget_bytes
        result.add(Verdict.check(label, f"<= {budget_bytes / 1e9:.2f} GB", f"{peak / 1e9:.2f} GB", ok))
    else:
        result.add(Verdict(label, "(recorded; no fixed budget)", f"{peak / 1e9:.2f} GB", "pass"))
    return peak


def gc_round(node, timeout=120.0):
    node.command(GC_SQL, timeout=timeout)


def log_fn(msg):
    note(msg)


def checkpoint_view(cluster, result, tables, **_ignored):
    """standard_end plus the dict shape the original cards read back."""
    fsck = standard_end(cluster=cluster, result=result, tables=tables)
    if not isinstance(fsck, dict):
        fsck = {}
    return {
        "fsck_final": fsck,
        "fsck_detail": fsck,
        "residual_unreachable": result.observations.get("gc_residual_unreachable"),
    }


def standard_end(*, cluster, result, tables, optimize=True, expect_exception=False, allow_gc_failed=False):
    """Quiesce, one explicit GC round, fsck dangling==0, dryrun subset."""
    del optimize, allow_gc_failed
    if expect_exception:
        note("end checkpoint: skipping quiesce (expect_exception card)")
    else:
        for table in tables:
            note(f"end checkpoint: quiesce {table}")
            try:
                quiesce(table=table, materialize_ttl=False)
            except Exception as e:
                note(f"end checkpoint: quiesce {table} raised: {e}")
    try:
        gc_round(cluster.node1, timeout=120)
    except Exception as e:
        note(f"end checkpoint: explicit GC raised: {e}")
    _, residual = drive_gc_until_stable()
    result.observations["gc_residual_unreachable"] = residual
    fsck = run_cas_fsck(detail=False)
    dryrun = run_cas_gc_dryrun()
    if not isinstance(fsck, dict):
        fsck = {}
    stored = {k: v for k, v in fsck.items() if k not in ("stdout", "stderr")}
    result.observations["fsck_final"] = stored
    result.observations["gc_all"] = gc_log_all(
        cluster, result.observations.get("since_event_time")
    )
    dangling = fsck.get("dangling")
    if dangling is None:
        result.add(
            Verdict.inconclusive(
                "fsck dangling", "0", "fsck summary unavailable"
            )
        )
    else:
        result.add(Verdict.check("fsck dangling", "0", dangling, dangling == 0))
        if dangling == 0:
            assert_pool_is_clean(fsck, dryrun, detail=False)
    return fsck


def apply_card_result(result):
    """Map card status onto TestFlows: FAIL fails, inconclusive/pass/skipped are OK."""
    result.finalize()
    fsck = result.observations.get("fsck_final")
    if isinstance(fsck, dict) and isinstance(fsck.get("detail"), list):
        fsck = dict(fsck)
        fsck["detail"] = {"rows": len(fsck["detail"])}
        result.observations["fsck_final"] = fsck
    note(result.to_markdown())
    if result.status == FAIL:
        fail(f"{result.scenario} status=FAIL")
    return result
