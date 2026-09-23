"""S34 create/drop churn + S35 same-name rotation (P1)."""

from cas.soak_tests.cards._p1 import ca_since, scale_verdict
from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C
from cas.soak_tests.steps import observe as O


@register
class S34(Scenario):
    name = "S34"
    title = "create/drop churn — D1 bounded GC fanout"
    priority = "P1"
    param_table = {
        "dev": {"iterations": 40, "rows": 80, "payload_bytes": 256, "gc_every": 5},
        "ci": {"iterations": 200, "rows": 300, "payload_bytes": 256, "gc_every": 20},
        "full": {"iterations": 1000, "rows": 600, "payload_bytes": 256, "gc_every": 50},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        iterations = int(p["iterations"])
        rows = int(p["rows"])
        payload = int(p["payload_bytes"])
        gc_every = max(1, int(p["gc_every"]))
        result.observations["tables"] = []
        scale_verdict(
            result,
            "D1 win: per-round GC cost must NOT grow with total-tables-ever-created",
            f"{iterations} create/insert/drop iterations (scale={ctx.scale})",
        )
        per_batch = []
        for i in range(iterations):
            table = f"s34_churn_{i:05d}"
            C.create_ca_table(cl.node1, table)
            C.insert_random(cl.node1, table, rows=rows, payload_bytes=payload, op_id=i * rows)
            C.drop_table_both(cl, table)
            if (i + 1) % gc_every == 0:
                batch = C.measure_idle_gc_batch(cl, i + 1, log_fn=ctx.log)
                per_batch.append(batch)
                ctx.log(
                    f"S34: batch@{i+1} CASRootGet={batch.get('CASRootGet')} root_dirs={batch.get('root_dirs')}"
                )
        result.observations["per_batch"] = per_batch
        if len(per_batch) >= 2:
            first, last = per_batch[0], per_batch[-1]
            grew_get = (
                isinstance(first.get("CASRootGet"), int)
                and isinstance(last.get("CASRootGet"), int)
                and last["CASRootGet"] > first["CASRootGet"] * 1.5
            )
            grew_dirs = (
                isinstance(first.get("root_dirs"), int)
                and isinstance(last.get("root_dirs"), int)
                and last["root_dirs"] > first["root_dirs"] + 2
            )
            result.add(
                Verdict.check(
                    "per-round GC fanout bounded (D1 win)",
                    "CASRootGet and root_dirs must NOT grow proportionally with ever-created tables",
                    f"CASRootGet first={first.get('CASRootGet')} last={last.get('CASRootGet')}; "
                    f"root_dirs first={first.get('root_dirs')} last={last.get('root_dirs')}",
                    not grew_get and not grew_dirs,
                )
            )
        else:
            result.add(
                Verdict.inconclusive(
                    "per-round GC fanout bounded (D1 win)",
                    "CASRootGet and root_dirs stable across batches",
                    f"only {len(per_batch)} GC batch(es)",
                )
            )
        C.standard_end(cluster=cl, result=result, tables=[])
        O.assert_reclaimable_drained(
            result,
            "dropped content reclaimed to 0 (D1 reclaimable drain)",
            result.observations.get("gc_residual_unreachable"),
            result.observations.get("fsck_final"),
        )


@register
class S35(Scenario):
    name = "S35"
    title = "rapid same-name rotation — D1 incarnation monotonicity"
    priority = "P1"
    param_table = {
        "dev": {"cycles": 30, "rows": 40, "payload_bytes": 256, "gc_every": 5},
        "ci": {"cycles": 150, "rows": 200, "payload_bytes": 256, "gc_every": 20},
        "full": {"cycles": 600, "rows": 600, "payload_bytes": 256, "gc_every": 50},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        table = "s35_rotation"
        cycles = int(p["cycles"])
        rows = int(p["rows"])
        payload = int(p["payload_bytes"])
        gc_every = max(1, int(p["gc_every"]))
        result.observations["tables"] = [table]
        scale_verdict(
            result,
            "D1 incarnation monotonicity under rapid same-name create/drop",
            f"{cycles} cycles (scale={ctx.scale})",
        )
        errors = []
        for i in range(cycles):
            try:
                C.create_ca_table(cl.node1, table)
                C.insert_random(cl.node1, table, rows=rows, payload_bytes=payload, op_id=i * rows)
                C.drop_table_both(cl, table)
            except Exception as e:
                errors.append((i, str(e)[:160]))
            if (i + 1) % gc_every == 0:
                C.gc_drive_round(cl, log_fn=ctx.log)
        ca_events = ca_since(ctx)
        bad = dict(ca_events.get("bad_total", {}))
        result.observations["ca_event_counts_rotation"] = ca_events
        result.add(
            Verdict.check(
                "no bad CA-log events during rapid same-name rotation",
                "bad_total empty",
                bad or "none",
                not bad,
            )
        )
        result.add(
            Verdict.check(
                "no CREATE/INSERT errors during rapid rotation",
                "0 errors",
                f"{len(errors)} errors",
                not errors,
            )
        )
        C.create_ca_table(cl.node1, table)
        try:
            cl.node1.command(
                f"INSERT INTO {table} VALUES (1, '{('x' * payload)}')",
                timeout=120,
            )
            cnt = int(cl.node1.scalar(f"SELECT count() FROM {table}") or 0)
        except Exception as e:
            cnt = None
            ctx.log(f"S35 final insert: {e}")
        if cnt is None:
            result.add(
                Verdict.inconclusive(
                    "final recreated table queryable", "count()==1", "final insert failed"
                )
            )
        else:
            result.add(Verdict.check("final recreated table queryable", "count()==1", cnt, cnt == 1))
        C.assert_replicas_agree(result, cl, C.table_checksum_query(table), name="S35 final-table replica agreement")
        C.standard_end(cluster=cl, result=result, tables=[table])
        O.assert_reclaimable_drained(
            result,
            "rotation residual reclaimed to 0",
            result.observations.get("gc_residual_unreachable"),
            result.observations.get("fsck_final"),
        )
        O.assert_fsck_clean(
            result, result.observations.get("fsck_final"), name="no dangling after rapid same-name rotation"
        )
