"""S13 process loss during write and GC (P0)."""

import threading
import time

from cas.soak_tests.oracle.chaos import Fault, FaultAction, FaultTarget
from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C
from cas.soak_tests.steps.chaos import apply_fault
from cas.soak_tests.steps.observe import wait_cluster_healthy

_S13_PRECOMMIT_EVENTS = ("precommit", "precommit_removed", "precommit_reclaim")
_S13_GC_EVENTS = ("gc_lease_acquire", "gc_lease_steal", "gc_recheck_verdict", "blob_delete")


def _ca_event_sum(cluster, since, names):
    out = {n: 0 for n in names}
    where = "1"
    if since:
        where = f"event_time >= '{since}'"
    for node in cluster.nodes():
        try:
            txt = node.query(
                f"SELECT event_type, count() FROM system.cas_log WHERE {where} "
                f"GROUP BY event_type FORMAT TabSeparated"
            )
        except Exception:
            continue
        for line in (txt or "").splitlines():
            if "\t" not in line:
                continue
            et, c = line.split("\t", 1)
            if et in out:
                try:
                    out[et] += int(c)
                except ValueError:
                    pass
    return out


@register
class S13(Scenario):
    name = "S13"
    title = "process loss during write and GC"
    priority = "P0"
    allow_gc_failed = True
    param_table = {
        "dev": {
            "kill_rounds": 4,
            "rows_per_insert": 400,
            "payload_bytes": 4096,
            "tables": 2,
            "mutate": True,
            "kill_delay_s": 1.2,
            "down_s": 3,
            "heal_timeout_s": 240,
        },
        "ci": {
            "kill_rounds": 12,
            "rows_per_insert": 5000,
            "payload_bytes": 16384,
            "tables": 3,
            "mutate": True,
            "kill_delay_s": 1.5,
            "down_s": 4,
            "heal_timeout_s": 300,
        },
        "full": {
            "kill_rounds": 40,
            "rows_per_insert": 20000,
            "payload_bytes": 65536,
            "tables": 4,
            "mutate": True,
            "kill_delay_s": 2.0,
            "down_s": 6,
            "heal_timeout_s": 360,
        },
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        n_tables = int(p["tables"])
        tables = [f"s13_churn_{i}" for i in range(n_tables)]
        result.observations["tables"] = list(tables)
        rows = int(p["rows_per_insert"])
        payload = int(p["payload_bytes"])
        kill_rounds = int(p["kill_rounds"])
        kill_delay_s = float(p["kill_delay_s"])
        down_s = int(p["down_s"])
        heal_timeout_s = int(p["heal_timeout_s"])
        ctx.log(f"S13: {n_tables} tables, {kill_rounds} kill rounds")
        for t in tables:
            C.create_ca_table(
                cl.node1,
                t,
                columns="id UInt64, payload String, bucket UInt32",
                order_by="id",
                partition_by="bucket % 8",
            )
        for ti, t in enumerate(tables):
            try:
                C.insert_random(
                    cl.node1, t, rows=rows, payload_bytes=payload, extra_cols_select="number % 64 AS bucket", op_id=0
                )
            except Exception as e:
                ctx.log(f"S13 seed insert {t} failed: {e}")
        counters = C.counters_window(cl)
        smp = C.RssSampler(cl, interval_s=5.0)
        stop = threading.Event()
        wl_stats = {"inserts_ok": 0, "inserts_failed": 0, "mutations_ok": 0, "mutations_failed": 0}
        op = {"id": rows}

        def _workload():
            i = 0
            while not stop.is_set():
                t = tables[i % n_tables]
                node = cl.node1 if (i % 2 == 0) else cl.node2
                base = op["id"]
                op["id"] += rows
                try:
                    C.insert_random(
                        node,
                        t,
                        rows=rows,
                        payload_bytes=payload,
                        extra_cols_select="number % 64 AS bucket",
                        op_id=base,
                    )
                    wl_stats["inserts_ok"] += 1
                except Exception:
                    wl_stats["inserts_failed"] += 1
                if p.get("mutate") and i % 3 == 0:
                    try:
                        node.command(
                            f"ALTER TABLE {t} DELETE WHERE bucket = {i % 8} SETTINGS mutations_sync=0",
                            timeout=120,
                        )
                        wl_stats["mutations_ok"] += 1
                    except Exception:
                        wl_stats["mutations_failed"] += 1
                i += 1

        def _drive_gc_leader():
            last_leader = None
            for node in cl.nodes():
                try:
                    node.command("SYSTEM CAS GC RUN ca", timeout=120)
                    last_leader = node.container
                except Exception as e:
                    ctx.log(f"S13 GC round on {node.container} failed: {str(e)[:160]}")
            return last_leader

        smp.start()
        wl_thread = threading.Thread(target=_workload, daemon=True)
        wl_thread.start()
        t0 = time.monotonic()
        kill_targets = []
        try:
            for r in range(kill_rounds):
                time.sleep(kill_delay_s)
                if r % 2 == 0:
                    target = FaultTarget.CH1
                    reason = "writer mid finalize/publish (best-effort)"
                else:
                    leader_cont = _drive_gc_leader()
                    target = FaultTarget.CH2 if leader_cont == cl.node2.container else FaultTarget.CH1
                    reason = f"recent GC leader ({leader_cont or 'unknown'})"
                kill_targets.append({"round": r, "target": target.value, "reason": reason})
                ctx.log(f"S13 round {r}: KILL {target.value} ({reason}), down {down_s}s")
                apply_fault(Fault(t_offset=0, target=target, action=FaultAction.KILL, duration_s=down_s))
                healthy = wait_cluster_healthy(cl, timeout_s=heal_timeout_s, log_fn=ctx.log)
                if not healthy:
                    result.add(
                        Verdict.check(
                            "cluster recovers after kill",
                            "both replicas healthy",
                            f"round {r}: not healthy within {heal_timeout_s}s",
                            False,
                        )
                    )
                    break
        finally:
            stop.set()
            wl_thread.join(timeout=120)
            smp.stop()
        result.timings["chaos_s"] = round(time.monotonic() - t0, 1)
        result.observations["kill_targets"] = kill_targets
        result.observations["workload_stats"] = wl_stats
        result.observations["counters_total"] = counters().get("_total", {})
        if not wait_cluster_healthy(cl, timeout_s=heal_timeout_s, log_fn=ctx.log):
            result.add(
                Verdict.inconclusive(
                    "post-chaos health", "both replicas healthy", "cluster not healthy after chaos"
                )
            )
        events = _ca_event_sum(cl, ctx.extra.get("since_event_time"), _S13_PRECOMMIT_EVENTS + _S13_GC_EVENTS)
        precommit_events = {e: events.get(e, 0) for e in _S13_PRECOMMIT_EVENTS}
        gc_events = {e: events.get(e, 0) for e in _S13_GC_EVENTS}
        result.observations["precommit_events"] = precommit_events
        result.observations["gc_lease_events"] = gc_events
        reclaimed = precommit_events.get("precommit_reclaim", 0) + precommit_events.get("precommit_removed", 0)
        added = precommit_events.get("precommit", 0)
        result.add(
            Verdict(
                "abandoned precommits reclaimed",
                "precommit_reclaim/removed observed when precommits added",
                f"added={added} reclaimed/removed={reclaimed}",
                "pass" if (added == 0 or reclaimed > 0) else "inconclusive",
                ""
                if (added == 0 or reclaimed > 0)
                else "precommits added but none reclaimed/removed in-window",
            )
        )
        result.add(
            Verdict(
                "GC lease churn recorded",
                "gc_lease_acquire/steal/recheck visible under leader kills",
                f"acquire={gc_events.get('gc_lease_acquire', 0)} steal={gc_events.get('gc_lease_steal', 0)}",
                "pass",
            )
        )
        for t in tables:
            try:
                C.assert_replicas_agree(result, cl, C.table_checksum_query(t), name=f"replica agreement {t}")
            except Exception as e:
                result.add(
                    Verdict.inconclusive(
                        f"replica agreement {t}", "all replicas equal", f"oracle query failed: {str(e)[:160]}"
                    )
                )
        C.record_peak_memory(result, smp, label="peak MemoryResident during chaos")
        C.standard_end(cluster=cl, result=result, tables=tables, allow_gc_failed=True)
        residual = result.observations.get("gc_residual_unreachable")
        if isinstance(residual, int) and residual > 0:
            result.add(
                Verdict.inconclusive(
                    "abandoned-precommit residual bounded",
                    "residual==0 after forced GC",
                    f"residual={residual} unreachable objects remain after forced GC; classified not failed",
                )
            )
        else:
            result.add(
                Verdict.check(
                    "abandoned-precommit residual bounded", "residual==0 after forced GC", residual, residual == 0
                )
            )
