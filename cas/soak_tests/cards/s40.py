"""S40 acked-then-lost INSERT under S3 outage + replica kill (P0)."""

import os
import subprocess
import threading
import time

from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C
from cas.soak_tests.steps.chaos import ensure_clickhouse_daemon

_TABLE = "s40_dedup_outage"
_RUSTFS = os.environ.get("CA_SOAK_TESTS_RUSTFS_CONTAINER", "cas_soak_tests_rustfs")
_CH2 = os.environ.get("CA_SOAK_TESTS_NODE2_CONTAINER", "soak_tests_env-clickhouse2-1")


def _dock(*args):
    subprocess.run(["docker", *args], capture_output=True, check=True)


@register
class S40(Scenario):
    name = "S40"
    title = "acked-then-lost INSERT under S3 outage + replica kill"
    priority = "P0"
    expect_exception = True
    param_table = {
        "dev": {
            "insert_window_s": 150,
            "pause_s": 105,
            "kill_after_s": 16,
            "ch2_down_s": 50,
            "writers": 6,
            "payload_bytes": 20000,
            "min_acked": 200,
        },
        "ci": {
            "insert_window_s": 150,
            "pause_s": 105,
            "kill_after_s": 16,
            "ch2_down_s": 50,
            "writers": 8,
            "payload_bytes": 20000,
            "min_acked": 200,
        },
        "full": {
            "insert_window_s": 300,
            "pause_s": 105,
            "kill_after_s": 16,
            "ch2_down_s": 50,
            "writers": 8,
            "payload_bytes": 20000,
            "min_acked": 400,
        },
    }

    def run(self, ctx, result):
        p = ctx.params
        node = ctx.cluster.node1
        result.observations["tables"] = [_TABLE]
        payload = "x" * int(p["payload_bytes"])
        C.create_ca_table(node, _TABLE)
        acked = set()
        acked_lock = threading.Lock()
        next_id = [0]
        id_lock = threading.Lock()
        insert_failures = [0]
        fault_errors = []
        stop_at = time.time() + float(p["insert_window_s"])

        def writer():
            while time.time() < stop_at:
                with id_lock:
                    next_id[0] += 1
                    i = next_id[0]
                deadline = time.time() + 240
                while time.time() < deadline:
                    try:
                        node.query(
                            f"INSERT INTO {_TABLE} SETTINGS insert_deduplicate=1, "
                            f"async_insert=0 VALUES ({i}, '{payload}')",
                            timeout=100,
                        )
                        with acked_lock:
                            acked.add(i)
                        break
                    except Exception:
                        with acked_lock:
                            insert_failures[0] += 1
                        time.sleep(1.5)

        def faults():
            try:
                time.sleep(8)
                ctx.log("S40: PAUSE rustfs")
                _dock("pause", _RUSTFS)
                time.sleep(float(p["kill_after_s"]) - 8)
                ctx.log("S40: KILL ch2")
                _dock("kill", _CH2)
                time.sleep(float(p["ch2_down_s"]))
                ctx.log("S40: START ch2")
                _dock("start", _CH2)
                ensure_clickhouse_daemon(_CH2)
                time.sleep(float(p["pause_s"]) - float(p["kill_after_s"]) - float(p["ch2_down_s"]))
                ctx.log("S40: UNPAUSE rustfs")
                _dock("unpause", _RUSTFS)
            except Exception as e:
                fault_errors.append(str(e))
                subprocess.run(["docker", "unpause", _RUSTFS], capture_output=True)
                subprocess.run(["docker", "start", _CH2], capture_output=True)
                try:
                    ensure_clickhouse_daemon(_CH2)
                except Exception:
                    pass

        ft = threading.Thread(target=faults, daemon=True)
        ft.start()
        threads = [threading.Thread(target=writer, daemon=True) for _ in range(int(p["writers"]))]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        ft.join(timeout=float(p["pause_s"]) + 30)
        for _ in range(24):
            try:
                node.query("SELECT 1", timeout=10)
                break
            except Exception:
                time.sleep(5)
        time.sleep(30)
        try:
            node.query(f"SYSTEM SYNC REPLICA {_TABLE}", timeout=300)
        except Exception as e:
            ctx.log(f"S40 SYNC: {e}")
        try:
            present = set(int(x) for x in node.query(f"SELECT id FROM {_TABLE} ORDER BY id").split() if x.strip())
        except Exception:
            present = set()
        lost = sorted(acked - present)
        result.add(
            Verdict.check(
                "fault schedule executed",
                "no docker/fault-thread errors",
                "; ".join(fault_errors) if fault_errors else "clean",
                not fault_errors,
            )
        )
        result.add(
            Verdict.check(
                "outage disturbed inserts",
                "insert_failures > 0",
                f"insert_failures={insert_failures[0]}",
                insert_failures[0] > 0,
            )
        )
        result.add(
            Verdict.check(
                "meaningful acked volume",
                f"acked >= {int(p['min_acked'])}",
                f"acked={len(acked)}",
                len(acked) >= int(p["min_acked"]),
            )
        )
        result.add(
            Verdict.check(
                "every acked insert is present",
                "lost == 0",
                f"acked={len(acked)} present={len(present)} lost={len(lost)}",
                not lost,
            )
        )
        C.standard_end(cluster=ctx.cluster, result=result, tables=[_TABLE], expect_exception=True)
