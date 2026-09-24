"""S45 decommission victim with hidden Removing catalog entries (P1)."""

import os
import subprocess
import time

from cas.soak_tests.cards._p1 import scale_verdict
from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C
from cas.soak_tests.steps import observe as O
from cas.soak_tests.steps.chaos import ensure_clickhouse_daemon
from cas.soak_tests.steps.checkpoint import FSCK_CONFIG, FSCK_DISK

_VICTIM_SRID = os.environ.get("CA_SOAK_TESTS_VICTIM_SRID", "ca_soak_clickhouse2")
_TABLE_PREFIX = "s45_victim"
_CH1 = os.environ.get("CA_SOAK_TESTS_NODE1_CONTAINER", "soak_tests_env-clickhouse1-1")
_CH2 = os.environ.get("CA_SOAK_TESTS_NODE2_CONTAINER", "soak_tests_env-clickhouse2-1")
_LEASE_WAIT_BOUND_S = 60.0
_LEASE_POLL_INTERVAL_S = 5.0


def _run_drop_member(container, srid, timeout_s=300.0):
    cmd = [
        "docker",
        "exec",
        container,
        "clickhouse",
        "disks",
        "--config-file",
        FSCK_CONFIG,
        "--disk",
        FSCK_DISK,
        "--query",
        f"cas-drop-member {srid}",
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
    out = {"exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    for line in (p.stdout or "").splitlines():
        if "=" in line:
            k, _, v = line.partition("=")
            try:
                out[k.strip()] = int(v.strip())
            except ValueError:
                out[k.strip()] = v.strip()
    return out


def _run_drop_member_after_lease_lapses(container, srid):
    deadline = time.monotonic() + _LEASE_WAIT_BOUND_S
    last = _run_drop_member(container, srid)
    while (
        last.get("exit_code") != 0
        and "alive or contended" in (last.get("stderr") or "")
        and time.monotonic() < deadline
    ):
        time.sleep(_LEASE_POLL_INTERVAL_S)
        last = _run_drop_member(container, srid)
    return last


@register
class S45(Scenario):
    name = "S45"
    title = "decommission a victim member with hidden Removing catalog entries"
    priority = "P1"
    param_table = {
        "dev": {"victim_tables": 3, "rows_per_table": 100},
        "ci": {"victim_tables": 6, "rows_per_table": 500},
        "full": {"victim_tables": 12, "rows_per_table": 2000},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        node = cl.node1
        victim = cl.node2
        tables = [f"{_TABLE_PREFIX}_{i}" for i in range(int(p["victim_tables"]))]
        result.observations["tables"] = list(tables)
        scale_verdict(
            result,
            "cas-drop-member sweeps hidden Removing rows on a killed replica",
            f"{len(tables)} tables (scale={ctx.scale})",
        )
        for t in tables:
            C.create_ca_table(node, t)
            C.insert_random(node, t, rows=int(p["rows_per_table"]), payload_bytes=64)
            try:
                victim.command(f"SYSTEM SYNC REPLICA {t}", timeout=60)
            except Exception as e:
                ctx.log(f"S45 SYNC {t}: {e}")
        for t in tables:
            try:
                node.query(f"DROP TABLE IF EXISTS {t}", timeout=120)
            except Exception as e:
                ctx.log(f"S45 DROP on node1 {t}: {e}")
            try:
                victim.query(f"DROP TABLE IF EXISTS {t}", timeout=120)
            except Exception as e:
                ctx.log(f"S45 DROP on victim {t}: {e}")
        result.observations["tables"] = []
        ctx.log(f"S45: killing victim {_CH2}")
        killed = subprocess.run(["docker", "kill", _CH2], capture_output=True, text=True, timeout=60)
        if killed.returncode != 0:
            result.add(
                Verdict.inconclusive(
                    "cas-drop-member exits cleanly",
                    "exit_code == 0",
                    f"docker kill failed: {killed.stderr[:200]}",
                )
            )
            return
        try:
            report = _run_drop_member_after_lease_lapses(_CH1, _VICTIM_SRID)
            result.observations["drop_member_report"] = {
                k: v for k, v in report.items() if k not in ("stdout", "stderr")
            }
            result.add(
                Verdict.check(
                    "cas-drop-member exits cleanly",
                    "exit_code == 0",
                    f"exit_code={report.get('exit_code')}",
                    report.get("exit_code") == 0,
                    f"stderr: {(report.get('stderr') or '')[:400]}",
                )
            )
            namespaces_removed = report.get("namespaces_removed")
            already = report.get("namespaces_already_removed")
            accounted = None
            if isinstance(namespaces_removed, int) or isinstance(already, int):
                accounted = int(namespaces_removed or 0) + int(already or 0)
            if not accounted:
                result.add(
                    Verdict.inconclusive(
                        "hidden Removing rows are accounted for",
                        f">= {len(tables)}",
                        f"namespaces_removed={namespaces_removed} already_removed={already}",
                    )
                )
            else:
                result.add(
                    Verdict.check(
                        "hidden Removing rows are accounted for",
                        f">= {len(tables)}",
                        f"namespaces_removed={namespaces_removed} already_removed={already}",
                        accounted >= len(tables),
                    )
                )
            _, residual = C.drive_gc_until_stable()
            result.observations["gc_residual_unreachable"] = residual
            fsck = C.run_cas_fsck(detail=False)
            O.assert_fsck_clean(result, fsck)
        finally:
            ctx.log(f"S45: restarting victim {_CH2} so later cards have a 2-replica cluster")
            subprocess.run(["docker", "start", _CH2], capture_output=True, timeout=120)
            ensure_clickhouse_daemon(_CH2)
            O.wait_cluster_healthy(cl, timeout_s=180, log_fn=ctx.log)
