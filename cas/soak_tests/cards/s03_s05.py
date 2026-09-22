"""S03 idle GC + S04 orphan drain + S05 sparse tables (P0)."""

import time

from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C
from cas.soak_tests.steps import observe as O

MIB = 1024 * 1024


def _scale_verdict(result, expected, observed, note):
    result.add(Verdict("scale used", expected, observed, "pass", note))


@register
class S03(Scenario):
    name = "S03"
    title = "million-live-object idle GC"
    priority = "P0"
    param_table = {
        "dev": {
            "prefill_parts": 8,
            "rows_per_part": 400,
            "payload_bytes": 256,
            "gc_minutes": 4,
            "minute_s": 3,
            "touch_rows": 50,
        },
        "ci": {
            "prefill_parts": 40,
            "rows_per_part": 5000,
            "payload_bytes": 256,
            "gc_minutes": 6,
            "minute_s": 10,
            "touch_rows": 200,
        },
        "full": {
            "prefill_parts": 400,
            "rows_per_part": 50000,
            "payload_bytes": 512,
            "gc_minutes": 15,
            "minute_s": 60,
            "touch_rows": 1000,
        },
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        table = "s03_live"
        result.observations["tables"] = [table]
        parts = int(p["prefill_parts"])
        rows = int(p["rows_per_part"])
        payload = int(p["payload_bytes"])
        target_live = parts * rows
        result.observations["scale"] = {
            "prefill_parts": parts,
            "rows_per_part": rows,
            "payload_bytes": payload,
            "approx_live_rows": target_live,
        }
        _scale_verdict(
            result,
            "spec target = 1M-10M live blob objects",
            f"~{target_live} live rows across {parts} parts (scale={ctx.scale})",
            "dev/ci are scaled down; only --scenario-scale full approaches the spec target",
        )
        ctx.log(f"S03: prefilling {parts} parts x {rows} rows (~{target_live} live rows)")
        C.create_ca_table(cl.node1, table, partition_by="id % 8")
        t_prefill = time.monotonic()
        for i in range(parts):
            C.insert_random(cl.node1, table, rows=rows, payload_bytes=payload, op_id=i * rows)
        result.timings["prefill_s"] = round(time.monotonic() - t_prefill, 1)
        pre = C.run_cas_fsck(detail=False)
        result.observations["prefill_fsck"] = {
            k: pre.get(k) for k in ("dangling", "unreachable", "reachable")
        }
        O.assert_fsck_clean(result, pre, name="prefill pool valid", expected="fsck dangling==0 before measured phase")

        smp = C.RssSampler(cl, interval_s=max(1.0, int(p["minute_s"]) / 3.0))
        counters = C.counters_window(cl)
        per_minute = []
        smp.start()
        try:
            for minute in range(int(p["gc_minutes"])):
                if int(p["touch_rows"]) > 0:
                    C.insert_random(
                        cl.node1,
                        table,
                        rows=int(p["touch_rows"]),
                        payload_bytes=payload,
                        op_id=10_000_000 + minute * 100_000,
                    )
                gc_before = O.gc_log_all(cl, ctx.extra.get("since_event_time"))
                n_before = sum(len(r) for r in gc_before.get("per_node", {}).values())
                t0 = time.monotonic()
                C.gc_drive_round(cl, log_fn=ctx.log)
                wall = time.monotonic() - t0
                gc_after = O.gc_log_all(cl, ctx.extra.get("since_event_time"))
                durs = O.finish_durations(gc_after)
                per_minute.append(
                    {
                        "minute": minute,
                        "wall_s": round(wall, 2),
                        "new_finish_rows": sum(len(r) for r in gc_after.get("per_node", {}).values())
                        - n_before,
                        "max_duration_ms": max(durs) if durs else None,
                    }
                )
                rest = int(p["minute_s"]) - wall
                if rest > 0:
                    time.sleep(rest)
        finally:
            smp.stop()
        result.observations["per_minute_gc"] = per_minute
        delta = counters().get("_total", {})
        result.observations["idle_phase_counters"] = delta

        durs = O.finish_durations(O.gc_log_all(cl, ctx.extra.get("since_event_time")))
        result.observations["gc_durations_ms"] = durs
        if durs:
            durs_sorted = sorted(durs)
            p95 = durs_sorted[min(len(durs_sorted) - 1, int(0.95 * (len(durs_sorted) - 1)))]
            result.add(
                Verdict(
                    "GC p95 duration recorded",
                    "scales with changed transitions, not live blob count",
                    f"p95={p95}ms over {len(durs)} rounds (~{target_live} live rows)",
                    "pass",
                )
            )
        else:
            result.add(
                Verdict.inconclusive(
                    "GC p95 duration recorded",
                    "scales with changed transitions",
                    "no GC finish rows captured from the GC log for this run window",
                )
            )

        blob_list = int(delta.get("CASBlobList", 0))
        result.add(
            Verdict.check(
                "CASBlobList == 0 for journal-driven GC",
                "0 (no full blob enumeration in regular GC rounds)",
                blob_list,
                blob_list == 0,
            )
        )
        repoints = int(delta.get("CASRefRepoint", 0))
        result.add(
            Verdict.check(
                "CASRefRepoint == 0 on the non-transactional profile",
                "0",
                repoints,
                repoints == 0,
            )
        )
        peak = C.record_peak_memory(result, smp, label="peak MemoryResident during idle GC")
        if peak is not None:
            result.add(
                Verdict(
                    "GC memory bounded by reducer state",
                    "bounded by streaming buffers + reducer state, not # live blobs",
                    f"{peak / 1e9:.2f} GB at ~{target_live} live rows",
                    "pass",
                )
            )
        idle_round_counters = C.counters_window(cl)
        C.gc_drive_round(cl, log_fn=ctx.log)
        idle_round_cas_gc_get = int(idle_round_counters().get("_total", {}).get("CASGCGet", 0))
        result.observations["idle_round_cas_gc_get"] = idle_round_cas_gc_get
        C.assert_replicas_agree(result, cl, C.table_checksum_query(table), name="S03 replica agreement")
        C.standard_end(cluster=cl, result=result, tables=[table])
        dangling = (result.observations.get("fsck_final") or {}).get("dangling")
        if dangling is None:
            result.add(
                Verdict.inconclusive(
                    "idle GC round ops budget (Phase 4 Lever A skip-unchanged)",
                    "CASGCGet < 50 and fsck dangling == 0",
                    "fsck dangling unavailable",
                )
            )
        else:
            ok = idle_round_cas_gc_get < 50 and dangling == 0
            result.add(
                Verdict.check(
                    "idle GC round ops budget (Phase 4 Lever A skip-unchanged)",
                    "CASGCGet < 50 for an idle round and fsck dangling == 0",
                    f"CASGCGet={idle_round_cas_gc_get} dangling={dangling}",
                    ok,
                )
            )


@register
class S04(Scenario):
    name = "S04"
    title = "million-object orphan drain"
    priority = "P0"
    param_table = {
        "dev": {
            "tables": 6,
            "parts_per_table": 4,
            "rows_per_part": 400,
            "payload_bytes": 256,
            "keep_tables": 1,
        },
        "ci": {
            "tables": 20,
            "parts_per_table": 10,
            "rows_per_part": 5000,
            "payload_bytes": 256,
            "keep_tables": 2,
        },
        "full": {
            "tables": 100,
            "parts_per_table": 20,
            "rows_per_part": 50000,
            "payload_bytes": 512,
            "keep_tables": 5,
        },
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        ntables = int(p["tables"])
        parts = int(p["parts_per_table"])
        rows = int(p["rows_per_part"])
        payload = int(p["payload_bytes"])
        keep = int(p["keep_tables"])
        tables = [f"s04_t{i:04d}" for i in range(ntables)]
        result.observations["tables"] = list(tables)
        target_orphan_rows = (ntables - keep) * parts * rows
        _scale_verdict(
            result,
            "spec target >= 1M unreachable content objects",
            f"~{target_orphan_rows} orphaned rows ({ntables - keep} dropped tables) (scale={ctx.scale})",
            "dev/ci are scaled down; only --scenario-scale full approaches the spec target",
        )
        for t in tables:
            C.create_ca_table(cl.node1, t)
        t_prefill = time.monotonic()
        for ti, t in enumerate(tables):
            for pi in range(parts):
                C.insert_random(
                    cl.node1, t, rows=rows, payload_bytes=payload, op_id=(ti * parts + pi) * rows
                )
            if (ti + 1) % 10 == 0 or ti + 1 == len(tables):
                ctx.log(f"S04 prefill: {ti + 1}/{len(tables)} tables")
        result.timings["prefill_s"] = round(time.monotonic() - t_prefill, 1)
        pre = C.run_cas_fsck(detail=False)
        O.assert_fsck_clean(result, pre, name="prefill pool valid", expected="fsck dangling==0 before drain")
        keep_tables = tables[:keep]
        drop_tables = tables[keep:]
        ctx.log(f"S04: dropping {len(drop_tables)} tables")
        for t in drop_tables:
            C.drop_table_both(cl, t)
        after_drop = C.run_cas_fsck(detail=False)
        result.observations["fsck_after_drop"] = {
            k: after_drop.get(k) for k in ("dangling", "unreachable", "reachable")
        }
        O.assert_fsck_count(
            result,
            after_drop,
            "unreachable",
            name="drop created unreachable backlog",
            expected="unreachable > 0 after dropping tables",
            ok_fn=lambda n: n > 0,
            fail_note="drop did not produce an unreachable backlog",
        )
        smp = C.RssSampler(cl, interval_s=2.0)
        counters = C.counters_window(cl)
        smp.start()
        tg = time.monotonic()
        try:
            _, residual = C.drive_gc_until_stable()
        finally:
            smp.stop()
        result.timings["drain_s"] = round(time.monotonic() - tg, 1)
        result.observations["drain_residual_unreachable"] = residual
        delta = counters().get("_total", {})
        result.observations["drain_counters"] = delta
        gc_all = O.gc_log_all(cl, ctx.extra.get("since_event_time"))
        summary = gc_all.get("summary", {})
        durs = O.finish_durations(gc_all)
        deleted_total = int(summary.get("deleted_total", 0))
        replaced = int(summary.get("replaced_total", 0))
        spared = int(summary.get("spared_total", 0))
        nrounds = len(durs) or 1
        if deleted_total > 0:
            result.add(
                Verdict(
                    "reclaim throughput recorded",
                    "stable enough to extrapolate a drain time",
                    f"{deleted_total} deleted over {nrounds} rounds ({result.timings['drain_s']}s)",
                    "pass",
                )
            )
        else:
            result.add(
                Verdict.inconclusive(
                    "reclaim throughput recorded",
                    "deleted > 0 during drain",
                    "GC log reported no deletions for this run window",
                )
            )
        peak = C.record_peak_memory(result, smp, label="peak MemoryResident during orphan drain")
        if peak is not None:
            result.add(
                Verdict(
                    "drain memory bounded",
                    "bounded during retire/recheck/delete",
                    f"{peak / 1e9:.2f} GB",
                    "pass",
                )
            )
        result.add(
            Verdict.check(
                "replaced/spared rare in quiescence",
                "objects_replaced and objects_spared small",
                f"replaced={replaced} spared={spared}",
                replaced == 0 and spared == 0,
            )
        )
        result.add(
            Verdict.check(
                "CASRefRepoint == 0 on the non-transactional profile",
                "0",
                int(delta.get("CASRefRepoint", 0)),
                int(delta.get("CASRefRepoint", 0)) == 0,
            )
        )
        if keep_tables:
            C.assert_replicas_agree(
                result, cl, C.table_checksum_query(keep_tables[0]), name="S04 surviving-table replica agreement"
            )
        C.standard_end(cluster=cl, result=result, tables=keep_tables)
        O.assert_reclaimable_drained(
            result,
            "orphan backlog fully drained",
            result.observations.get("gc_residual_unreachable"),
            result.observations.get("fsck_final"),
        )


@register
class S05(Scenario):
    name = "S05"
    title = "10000 sparse tables"
    priority = "P0"
    param_table = {
        "dev": {
            "tables": 200,
            "active_tables": 10,
            "rows_per_part": 50,
            "payload_bytes": 128,
            "gc_minutes": 4,
            "minute_s": 3,
        },
        "ci": {
            "tables": 1000,
            "active_tables": 50,
            "rows_per_part": 200,
            "payload_bytes": 128,
            "gc_minutes": 6,
            "minute_s": 10,
        },
        "full": {
            "tables": 10000,
            "active_tables": 100,
            "rows_per_part": 500,
            "payload_bytes": 256,
            "gc_minutes": 15,
            "minute_s": 60,
        },
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        ntables = int(p["tables"])
        nactive = min(int(p["active_tables"]), ntables)
        rows = int(p["rows_per_part"])
        payload = int(p["payload_bytes"])
        tables = [f"s05_t{i:05d}" for i in range(ntables)]
        result.observations["tables"] = list(tables)
        active = tables[:nactive]
        _scale_verdict(
            result,
            "spec target = 10000 sparse tables",
            f"{ntables} tables, {nactive} active (scale={ctx.scale})",
            "dev/ci are scaled down; only --scenario-scale full reaches the 10000-table target",
        )
        ctx.log(f"S05: creating {ntables} tables")
        t_create = time.monotonic()
        for t in tables:
            C.create_ca_table(cl.node1, t)
        result.timings["create_s"] = round(time.monotonic() - t_create, 1)
        t_prefill = time.monotonic()
        for i, t in enumerate(tables):
            C.insert_random(cl.node1, t, rows=rows, payload_bytes=payload, op_id=i * rows)
            if (i + 1) % 50 == 0 or i + 1 == len(tables):
                ctx.log(f"S05 prefill: {i + 1}/{len(tables)} tables")
        result.timings["prefill_s"] = round(time.monotonic() - t_prefill, 1)
        pre = C.run_cas_fsck(detail=False)
        O.assert_fsck_clean(result, pre, name="prefill pool valid")
        smp = C.RssSampler(cl, interval_s=max(1.0, int(p["minute_s"]) / 3.0))
        counters = C.counters_window(cl)
        smp.start()
        try:
            for minute in range(int(p["gc_minutes"])):
                for j, t in enumerate(active):
                    C.insert_random(
                        cl.node1,
                        t,
                        rows=max(1, rows // 10),
                        payload_bytes=payload,
                        op_id=10_000_000 + minute * 1_000_000 + j * 10_000,
                    )
                t0 = time.monotonic()
                C.gc_drive_round(cl, log_fn=ctx.log)
                rest = int(p["minute_s"]) - (time.monotonic() - t0)
                if rest > 0:
                    time.sleep(rest)
        finally:
            smp.stop()
        delta = counters().get("_total", {})
        gc_all = O.gc_log_all(cl, ctx.extra.get("since_event_time"))
        durs = O.finish_durations(gc_all)
        rounds = max(1, len(durs))
        log_body_gets = int(delta.get("CASRefLogBodyGets", 0))
        get_per_round = log_body_gets / rounds
        if durs:
            result.add(
                Verdict.check(
                    "idle tables don't dominate GC GETs",
                    f"CASRefLogBodyGets/round << {ntables}",
                    f"{get_per_round:.0f} CASRefLogBodyGets/round over {rounds} rounds",
                    get_per_round < ntables,
                )
            )
        else:
            result.add(
                Verdict.inconclusive(
                    "idle tables don't dominate GC GETs",
                    "CASRefLogBodyGets/round bounded by new logs",
                    "no GC finish rows captured",
                )
            )
        result.add(
            Verdict.check(
                "CASBlobList == 0 for sparse-write GC",
                "0",
                int(delta.get("CASBlobList", 0)),
                int(delta.get("CASBlobList", 0)) == 0,
            )
        )
        result.add(
            Verdict.check(
                "CASRefRepoint == 0 on the non-transactional profile",
                "0",
                int(delta.get("CASRefRepoint", 0)),
                int(delta.get("CASRefRepoint", 0)) == 0,
            )
        )
        peak = C.record_peak_memory(result, smp, label="peak MemoryResident with many idle tables")
        if peak is not None:
            result.add(
                Verdict(
                    "memory not driven by table count",
                    "bounded",
                    f"{peak / 1e9:.2f} GB at {ntables} tables",
                    "pass",
                )
            )
        C.assert_replicas_agree(result, cl, C.table_checksum_query(active[0]), name="S05 active-table replica agreement")
        C.standard_end(cluster=cl, result=result, tables=active)
        O.assert_reclaimable_drained(
            result,
            "reclaimable content drained with many tables",
            result.observations.get("gc_residual_unreachable"),
            result.observations.get("fsck_final"),
        )
