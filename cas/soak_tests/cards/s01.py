"""S01 huge single blob (P0)."""

import threading
import time

from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C

MIB = 1024 * 1024
GIB = 1024 * 1024 * 1024


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

        C.create_ca_table(cl.node1, table)
        baseline = C.cluster_rss_peak(cl)
        result.observations["baseline_rss"] = baseline

        counters = C.counters_window(cl)
        smp = C.RssSampler(cl, interval_s=2.0)
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
        smp.start()
        if gc_thread:
            gc_thread.start()
        t0 = time.monotonic()
        try:
            _insert_one_big_part(
                cl.node1, table, rows=rows, payload_bytes=payload_bytes, log_fn=ctx.log
            )
        finally:
            stop_gc.set()
            if gc_thread:
                gc_thread.join(timeout=10)
            smp.stop()
        result.timings["insert_s"] = round(time.monotonic() - t0, 1)

        delta = counters()
        total = delta.get("_total", {})
        result.observations["counters"] = total
        result.observations["mid_write_gc_rounds"] = mid_gc_ran["n"]

        peak = C.record_peak_memory(result, smp, label="peak MemoryResident during upload")
        if peak is not None and baseline is not None:
            mem_growth = peak - baseline
            result.observations["rss_growth_during_upload"] = mem_growth
            attributable = actual_bytes >= 128 * MIB
            ok = mem_growth < actual_bytes
            if not attributable:
                result.add(
                    Verdict.inconclusive(
                        "RSS growth < blob size",
                        f"< {actual_bytes / GIB:.3f} GiB",
                        f"observed {mem_growth / MIB:.0f} MiB growth, but blob "
                        f"{actual_bytes / MIB:.0f} MiB < 128 MiB is too small to attribute "
                        "RSS growth — rerun at --scenario-scale ci/full",
                    )
                )
            else:
                result.add(
                    Verdict.check(
                        "RSS growth < blob size",
                        f"< {actual_bytes / GIB:.3f} GiB",
                        f"{mem_growth / GIB:.3f} GiB",
                        ok,
                        ""
                        if ok
                        else "process memory grew by ~blob size — blob likely materialized in memory",
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
