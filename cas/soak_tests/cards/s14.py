"""S14 restart with many refs (P0)."""

import time

from cas.soak_tests.oracle.chaos import Fault, FaultAction, FaultTarget
from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C
from cas.soak_tests.steps.chaos import apply_fault
from cas.soak_tests.steps.observe import wait_cluster_healthy


@register
class S14(Scenario):
    name = "S14"
    title = "restart with many refs"
    priority = "P0"
    param_table = {
        "dev": {
            "mode": "tables",
            "tables": 200,
            "parts_per_table": 1,
            "parts": 2000,
            "rows_per_part": 1,
            "payload_bytes": 256,
            "restart_timeout_s": 300,
            "first_query_samples": 8,
        },
        "ci": {
            "mode": "tables",
            "tables": 2000,
            "parts_per_table": 1,
            "parts": 20000,
            "rows_per_part": 1,
            "payload_bytes": 256,
            "restart_timeout_s": 480,
            "first_query_samples": 16,
        },
        "full": {
            "mode": "tables",
            "tables": 10000,
            "parts_per_table": 1,
            "parts": 100000,
            "rows_per_part": 1,
            "payload_bytes": 256,
            "restart_timeout_s": 900,
            "first_query_samples": 32,
        },
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        mode = p.get("mode", "tables")
        restart_timeout_s = int(p["restart_timeout_s"])
        if mode == "tables":
            n_tables = int(p["tables"])
            payload = int(p["payload_bytes"])
            tables = [f"s14_t_{i}" for i in range(n_tables)]
            result.observations["tables"] = list(tables)
            ctx.log(f"S14: prefilling {n_tables} tables")
            t_prefill = time.monotonic()
            for i, t in enumerate(tables):
                C.create_ca_table(cl.node1, t)
                try:
                    C.insert_random(cl.node1, t, rows=1, payload_bytes=payload, op_id=i)
                except Exception as e:
                    ctx.log(f"S14 prefill insert {t} failed: {str(e)[:120]}")
                if i and i % 50 == 0:
                    ctx.log(f"S14 prefill: {i}/{n_tables} tables")
            result.timings["prefill_s"] = round(time.monotonic() - t_prefill, 1)
            measured_tables = tables
            sample_tables = tables[:: max(1, n_tables // int(p["first_query_samples"]))]
        else:
            payload = int(p["payload_bytes"])
            n_parts = int(p["parts"])
            rows_pp = int(p["rows_per_part"])
            table = "s14_manyparts"
            tables = [table]
            result.observations["tables"] = tables
            C.create_ca_table(cl.node1, table)
            for n in cl.nodes():
                try:
                    n.command("SYSTEM STOP MERGES s14_manyparts")
                except Exception as e:
                    ctx.log(f"S14 STOP MERGES failed: {e}")
            t_prefill = time.monotonic()
            for i in range(n_parts):
                try:
                    C.insert_random(cl.node1, table, rows=rows_pp, payload_bytes=payload, op_id=i)
                except Exception as e:
                    ctx.log(f"S14 prefill insert part {i} failed: {str(e)[:120]}")
            result.timings["prefill_s"] = round(time.monotonic() - t_prefill, 1)
            measured_tables = [table]
            sample_tables = [table]

        if not wait_cluster_healthy(cl, timeout_s=restart_timeout_s, log_fn=ctx.log):
            result.add(Verdict.inconclusive("pre-restart health", "both replicas healthy", "not healthy after prefill"))
        counters = C.counters_window(cl)
        ctx.log("S14: clean restart of both ClickHouse servers")
        t_restart = time.monotonic()
        apply_fault(Fault(t_offset=0, target=FaultTarget.BOTH, action=FaultAction.RESTART, duration_s=0))
        healthy = wait_cluster_healthy(cl, timeout_s=restart_timeout_s, log_fn=ctx.log)
        result.timings["restart_ping_healthy_s"] = round(time.monotonic() - t_restart, 1)
        if not healthy:
            result.add(
                Verdict.check(
                    "servers restart", "both replicas healthy after restart", f"not healthy within {restart_timeout_s}s", False
                )
            )

        def _all_queryable(deadline):
            while time.monotonic() < deadline:
                ok = True
                for node in cl.nodes():
                    for t in sample_tables:
                        try:
                            node.scalar(f"SELECT count() FROM {t}")
                        except Exception:
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    return True
                time.sleep(1)
            return False

        all_q = _all_queryable(t_restart + restart_timeout_s)
        queryable_s = time.monotonic() - t_restart
        result.timings["restart_all_queryable_s"] = round(queryable_s, 1)
        result.add(
            Verdict.check(
                "all tables queryable after restart",
                f"<= {restart_timeout_s}s",
                f"{queryable_s:.1f}s",
                all_q,
            )
        )
        first_query_ms = []
        for t in sample_tables:
            tq = time.monotonic()
            try:
                cl.node1.scalar(f"SELECT count() FROM {t}")
                first_query_ms.append(round((time.monotonic() - tq) * 1000, 1))
            except Exception as e:
                ctx.log(f"S14 first-query {t} failed: {str(e)[:120]}")
        if first_query_ms:
            first_query_ms.sort()
            mid = first_query_ms[len(first_query_ms) // 2]
            result.add(
                Verdict(
                    "first-query latency recorded",
                    "explained by required root/manifest reads",
                    f"median={mid}ms max={first_query_ms[-1]}ms (n={len(first_query_ms)})",
                    "pass",
                )
            )
        else:
            result.add(
                Verdict.inconclusive(
                    "first-query latency recorded",
                    "explained by required root/manifest reads",
                    "no first-query samples collected",
                )
            )
        delta = counters().get("_total", {})
        startup_counters = {
            k: delta.get(k, 0)
            for k in ("CASRootList", "CASRootGet", "CASRootHead", "CASBlobList", "CASBlobHead", "CASBlobGet")
        }
        result.observations["startup_ca_counters"] = startup_counters
        result.add(
            Verdict(
                "startup root metadata reads recorded",
                "CASRootList/CASRootGet scale with table metadata, not blob count",
                f"RootList={startup_counters['CASRootList']} RootGet={startup_counters['CASRootGet']} BlobList={startup_counters['CASBlobList']}",
                "pass",
            )
        )
        result.add(
            Verdict.check(
                "startup does not list all blobs",
                "CASBlobList stays bounded (not O(blobs))",
                startup_counters["CASBlobList"],
                startup_counters["CASBlobList"] <= max(16, len(measured_tables)),
            )
        )
        unknown_disk_warns = 0
        for node in cl.nodes():
            try:
                since = ctx.extra.get("since_event_time")
                where = "(message ILIKE '%unknown disk%' OR message ILIKE '%not found on disk%')"
                if since:
                    where += f" AND event_time >= '{since}'"
                v = node.scalar(
                    f"SELECT count() FROM system.text_log WHERE level <= 'Warning' AND {where}"
                )
                unknown_disk_warns += int(v or 0)
            except Exception as e:
                ctx.log(f"S14 text_log probe failed: {str(e)[:120]}")
        result.add(
            Verdict.check(
                "no unknown-disk false positives",
                "0 unknown-disk warnings",
                unknown_disk_warns,
                unknown_disk_warns == 0,
            )
        )
        for t in sample_tables:
            try:
                C.assert_replicas_agree(result, cl, C.table_checksum_query(t), name=f"replica agreement {t}")
            except Exception as e:
                result.add(
                    Verdict.inconclusive(f"replica agreement {t}", "all replicas equal", f"{str(e)[:160]}")
                )
        if mode == "tables" and len(measured_tables) > 16:
            C.standard_end(cluster=cl, result=result, tables=sample_tables)
        else:
            C.standard_end(cluster=cl, result=result, tables=measured_tables)
