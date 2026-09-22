"""S44 rebirth with concurrent mutation writers (P1)."""

import threading
import time

from cas.soak_tests.cards._p1 import scale_verdict
from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C
from cas.soak_tests.steps import observe as O

_TABLE = "s44_rebirth_nsfile"
_VIOLATION_EVENTS = ("CASRefNeedsRecovery", "CASRefRecoveryStreamHole")


def _mutation_writer(node, stop_flag, errors, applied_counter):
    i = 0
    while not stop_flag["stop"]:
        i += 1
        try:
            node.query(
                f"ALTER TABLE {_TABLE} UPDATE payload = concat(payload, '.') "
                f"WHERE id % 7 = {i % 7} SETTINGS mutations_sync = 0",
                timeout=30,
            )
            applied_counter[0] += 1
        except Exception as e:
            msg = str(e)
            if (
                "doesn't exist" not in msg
                and "UNKNOWN_TABLE" not in msg
                and "shutdown called" not in msg
            ):
                errors.append(msg[:300])
        time.sleep(0.2)


@register
class S44(Scenario):
    name = "S44"
    title = "rebirth adversarial with concurrent namespace-file (mutation) readers/writers"
    priority = "P1"
    param_table = {
        "dev": {"cycles": 6, "rows_per_cycle": 200, "cycle_pause_s": 2.0},
        "ci": {"cycles": 15, "rows_per_cycle": 500, "cycle_pause_s": 1.0},
        "full": {"cycles": 40, "rows_per_cycle": 2000, "cycle_pause_s": 0.5},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        node = cl.node1
        result.observations["tables"] = [_TABLE]
        scale_verdict(
            result,
            "mutation writers across drop/recreate incarnation boundaries",
            f"{int(p['cycles'])} cycles (scale={ctx.scale})",
        )
        stop_flag = {"stop": False}
        mutation_errors = []
        applied_counter = [0]
        counters = C.counters_window(cl)
        writer = threading.Thread(
            target=_mutation_writer,
            args=(node, stop_flag, mutation_errors, applied_counter),
            daemon=True,
        )
        writer.start()
        latencies = []
        try:
            for cycle in range(int(p["cycles"])):
                t0 = time.monotonic()
                C.create_ca_table(node, _TABLE)
                C.insert_random(node, _TABLE, rows=int(p["rows_per_cycle"]), payload_bytes=64, op_id=cycle)
                time.sleep(float(p["cycle_pause_s"]))
                node.command(f"DROP TABLE IF EXISTS {_TABLE} SYNC", timeout=120)
                latencies.append(time.monotonic() - t0)
        finally:
            stop_flag["stop"] = True
            writer.join(timeout=30)
        result.observations["recreate_latencies_s"] = [round(x, 3) for x in latencies]
        result.observations["mutations_applied"] = applied_counter[0]
        result.add(
            Verdict.check(
                "no unexpected mutation errors across incarnation boundaries",
                "errors == 0 (besides drop-window UNKNOWN_TABLE / shutdown called)",
                f"errors={len(mutation_errors)}",
                not mutation_errors,
            )
        )
        if len(latencies) >= 4:
            first = latencies[: len(latencies) // 2]
            second = latencies[len(latencies) // 2 :]
            avg1 = sum(first) / len(first)
            avg2 = sum(second) / len(second)
            result.add(
                Verdict.check(
                    "recreate latency does not grow across cycles",
                    f"second-half avg <= 2x first-half avg ({avg1:.3f}s)",
                    f"first_half_avg={avg1:.3f}s second_half_avg={avg2:.3f}s",
                    avg2 <= 2.0 * avg1 + 0.05,
                )
            )
        delta = counters().get("_total", {})
        for ev in _VIOLATION_EVENTS:
            count = int(delta.get(ev, 0) or 0)
            result.add(Verdict.check(f"{ev} stays at zero", "0", count, count == 0))
        C.standard_end(cluster=cl, result=result, tables=[_TABLE])
        O.assert_fsck_clean(result, result.observations.get("fsck_final"))
