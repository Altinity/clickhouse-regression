"""S01 huge single blob (P0)."""

import threading
import time

from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C

MIB = 1024 * 1024
GIB = 1024 * 1024 * 1024


_TRACKING_SQL = (
    "SELECT value FROM system.metrics WHERE metric = 'MemoryTracking' FORMAT TabSeparated"
)


def _memory_tracking(node):
    """Allocator memory. Unlike MemoryResident, this updates as the insert allocates."""
    try:
        value = node.scalar(_TRACKING_SQL)
        return int(value) if value not in (None, "") else None
    except Exception:
        return None


def _writer_growth(node, work):
    """Peak MemoryTracking on `node` while `work()` runs, minus the sample taken just before it."""
    baseline = _memory_tracking(node)
    peak = baseline or 0
    stop = threading.Event()

    def poll():
        nonlocal peak
        while not stop.is_set():
            sample = _memory_tracking(node)
            if sample is not None:
                peak = max(peak, sample)
            stop.wait(0.05)
        sample = _memory_tracking(node)
        if sample is not None:
            peak = max(peak, sample)

    thread = threading.Thread(target=poll, daemon=True)
    thread.start()
    try:
        work()
    finally:
        stop.set()
        thread.join(timeout=5)
    growth = None if baseline is None else peak - baseline
    return baseline, peak if baseline is not None else None, growth


def _insert_one_big_part(node, name, *, rows, payload_bytes, op_id=0, timeout=2400.0, log_fn=print):
    """Bounded inserts (~1 GiB each) then OPTIMIZE FINAL to one huge part."""
    batch_rows = max(1, GIB // payload_bytes)
    done = 0
    while done < rows:
        n_rows = min(batch_rows, rows - done)
        C.insert_random(
            node,
            name,
            rows=n_rows,
            payload_bytes=payload_bytes,
            op_id=op_id + done,
            timeout=timeout,
        )
        done += n_rows
        log_fn(f"  inserted {done}/{rows} rows ({done * payload_bytes / GIB:.2f} GiB)")
    if rows > batch_rows:
        log_fn(
            f"  OPTIMIZE FINAL -> single part of {rows * payload_bytes / GIB:.2f} GiB"
        )
        node.command(f"OPTIMIZE TABLE {name} FINAL", timeout=timeout)


@register
class S01(Scenario):
    name = "S01"
    title = "huge single blob"
    priority = "P0"
    param_table = {
        "dev": {"blob_mib": 64, "payload_mib": 1, "mid_write_gc": True},
        "ci": {"blob_mib": 512, "payload_mib": 2, "mid_write_gc": True},
        "full": {"blob_mib": 102400, "payload_mib": 8, "mid_write_gc": True},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        table = "s01_huge"
        result.observations["tables"] = [table]
        payload_bytes = int(p["payload_mib"]) * MIB
        rows = max(1, (int(p["blob_mib"]) * MIB) // payload_bytes)
        actual_bytes = rows * payload_bytes
        result.observations["target_blob_bytes"] = actual_bytes
        ctx.log(f"S01: one part of ~{actual_bytes / GIB:.3f} GiB ({rows} rows x {payload_bytes} B)")

        # The INSERT holds the blob. A same-sized MergeTree insert on the local disk is what
        # that costs without CAS. putBlob streams the staged file, so CAS should not add another
        # full copy on top of that.
        local = "s01_local"
        local_growth = None
        try:
            cl.node1.command(
                f"CREATE TABLE {local} (id UInt64, payload String) ENGINE = MergeTree ORDER BY id "
                "SETTINGS min_bytes_for_wide_part = 0, min_rows_for_wide_part = 0",
                timeout=60,
            )
            _, local_peak, local_growth = _writer_growth(
                cl.node1,
                lambda: _insert_one_big_part(
                    cl.node1, local, rows=rows, payload_bytes=payload_bytes, log_fn=ctx.log
                ),
            )
            result.observations["local_rss_peak"] = local_peak
            result.observations["local_rss_growth"] = local_growth
        except Exception as e:
            ctx.log(f"S01 local control: {e}")
        finally:
            try:
                cl.node1.command(f"DROP TABLE IF EXISTS {local} SYNC", timeout=120)
            except Exception as e:
                ctx.log(f"S01 drop local: {e}")

        C.create_ca_table(cl.node1, table)
        baseline = _memory_tracking(cl.node1)
        result.observations["baseline_memory_tracking"] = baseline

        counters = C.counters_window(cl)
        smp = C.RssSampler(cl, interval_s=0.25)
        tracking_peak = {"n": baseline or 0}
        stop_tracking = threading.Event()

        def _poll_tracking():
            while not stop_tracking.is_set():
                sample = _memory_tracking(cl.node1)
                if sample is not None:
                    tracking_peak["n"] = max(tracking_peak["n"], sample)
                stop_tracking.wait(0.05)
        mid_gc_ran = {"n": 0}
        stop_gc = threading.Event()

        def _mid_gc():
            while not stop_gc.is_set():
                if stop_gc.wait(3):
                    break
                try:
                    C.gc_round(cl.node2, timeout=120)
                    mid_gc_ran["n"] += 1
                except Exception:
                    pass

        gc_thread = threading.Thread(target=_mid_gc, daemon=True) if p.get("mid_write_gc") else None
        tracking_thread = threading.Thread(target=_poll_tracking, daemon=True)
        smp.start()
        tracking_thread.start()
        if gc_thread:
            gc_thread.start()
        t0 = time.monotonic()
        try:
            _insert_one_big_part(
                cl.node1, table, rows=rows, payload_bytes=payload_bytes, log_fn=ctx.log
            )
        finally:
            stop_gc.set()
            stop_tracking.set()
            if gc_thread:
                gc_thread.join(timeout=10)
            tracking_thread.join(timeout=5)
            smp.stop()
        result.timings["insert_s"] = round(time.monotonic() - t0, 1)

        delta = counters()
        total = delta.get("_total", {})
        result.observations["counters"] = total
        result.observations["mid_write_gc_rounds"] = mid_gc_ran["n"]

        C.record_peak_memory(result, smp, label="peak MemoryResident during upload")
        writer_peak = tracking_peak["n"] if baseline is not None else None
        if writer_peak is not None and baseline is not None:
            mem_growth = writer_peak - baseline
            result.observations["memory_tracking_growth"] = mem_growth
            attributable = actual_bytes >= 128 * MIB
            if not attributable:
                result.add(
                    Verdict.inconclusive(
                        "CAS memory growth < local insert + one blob",
                        "no extra full copy",
                        f"blob {actual_bytes / MIB:.0f} MiB < 128 MiB is too small to separate "
                        "an extra copy from the insert block — rerun at --scenario-scale ci/full",
                    )
                )
            elif local_growth is None or local_growth < actual_bytes // 2:
                result.add(
                    Verdict.inconclusive(
                        "CAS memory growth < local insert + one blob",
                        "no extra full copy",
                        f"local control growth={local_growth} did not observe the insert block",
                    )
                )
            else:
                limit = local_growth + actual_bytes
                result.add(
                    Verdict.check(
                        "CAS memory growth < local insert + one blob",
                        f"< {limit / GIB:.3f} GiB",
                        f"cas={mem_growth / GIB:.3f} GiB local={local_growth / GIB:.3f} GiB",
                        mem_growth < limit,
                        ""
                        if mem_growth < limit
                        else "writer RSS grew by a full extra blob over the same insert on local disk",
                    )
                )

        mp = {
            k: total.get(k, 0)
            for k in (
                "DiskS3CreateMultipartUpload",
                "DiskS3UploadPart",
                "DiskS3CompleteMultipartUpload",
                "DiskS3AbortMultipartUpload",
                "DiskS3PutObject",
                "CASBlobPut",
            )
        }
        result.observations["multipart_counters"] = mp
        result.add(
            Verdict.check(
                "blob uploaded",
                "CASBlobPut > 0",
                mp.get("CASBlobPut", 0),
                mp.get("CASBlobPut", 0) > 0,
            )
        )
        if actual_bytes >= 64 * MIB:
            used_mp = mp.get("DiskS3CreateMultipartUpload", 0) > 0
            result.add(
                Verdict(
                    "multipart upload used",
                    "> 0 for large blobs",
                    str(mp.get("DiskS3CreateMultipartUpload", 0)),
                    "pass" if used_mp else "inconclusive",
                    ""
                    if used_mp
                    else "no multipart create observed at this size — single PUT path",
                )
            )

        C.assert_replicas_agree(result, cl, C.table_checksum_query(table))
        C.standard_end(cluster=cl, result=result, tables=[table])
        fsck = result.observations.get("fsck_final") or {}
        dangling = fsck.get("dangling")
        if dangling is None:
            result.add(
                Verdict.inconclusive(
                    "live blob retained", "fsck dangling==0 & part live", "fsck unavailable"
                )
            )
        else:
            result.add(
                Verdict.check(
                    "live blob retained",
                    "fsck dangling==0 & part live",
                    dangling,
                    dangling == 0,
                )
            )
