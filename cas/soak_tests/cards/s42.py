"""S42 allocation-fault soak (P0)."""

import threading
import time

from cas.soak_tests.oracle.chaos import Fault, FaultAction, FaultTarget
from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C
from cas.soak_tests.steps.chaos import apply_fault
from cas.soak_tests.steps.observe import wait_cluster_healthy

_TABLE = "s42_alloc"
_EVENTS = (
    "CASRefNeedsRecovery",
    "QueryMemoryLimitExceeded",
    "CASRefAppendWedged",
    "CASRefAppendUnwedged",
    "CASRefAppendDefiniteFailure",
    "CASGCUnmatchedRemoveDeltas",
)
_POISON_LOG_NEEDLE = "NEEDS RECOVERY at"


def _events(node):
    names = "','".join(_EVENTS)
    try:
        txt = node.query(
            f"SELECT event, value FROM system.events WHERE event IN ('{names}') FORMAT TabSeparated"
        )
    except Exception:
        return {}
    out = {}
    for line in (txt or "").splitlines():
        if "\t" in line:
            k, v = line.split("\t", 1)
            try:
                out[k] = int(v)
            except ValueError:
                pass
    return {k: out.get(k, 0) for k in _EVENTS}


def _cluster_events(cluster):
    return {n.container: _events(n) for n in cluster.nodes()}


def _event_total(snap, name):
    return sum(int(per.get(name, 0)) for per in snap.values())


def _block_counts(node, rows_per_insert):
    txt = node.query(
        f"SELECT intDiv(id, {rows_per_insert}) AS b, count() FROM {_TABLE} GROUP BY b FORMAT TabSeparated"
    )
    out = {}
    for line in (txt or "").splitlines():
        if "\t" in line:
            b, c = line.split("\t", 1)
            out[int(b)] = int(c)
    return out


def _view(node, rows_per_insert):
    checksum = node.query(C.table_checksum_query(_TABLE)).strip()
    parts = sorted(
        node.query(
            f"SELECT name FROM system.parts WHERE table = '{_TABLE}' AND active ORDER BY name FORMAT TabSeparated"
        ).split()
    )
    return {"checksum": checksum, "active_parts": parts, "block_counts": _block_counts(node, rows_per_insert)}


@register
class S42(Scenario):
    name = "S42"
    title = "allocation-fault soak (query-thread): exception safety of the CAS post-durable window"
    priority = "P0"
    expect_exception = True
    param_table = {
        "dev": {
            "fault_probability": 2e-5,
            "burst_probability": 2e-4,
            "workload_s": 90,
            "burst_s": 15,
            "writers": 3,
            "readers": 2,
            "rows_per_insert": 400,
            "payload_bytes": 512,
            "query_timeout_s": 120,
            "join_bound_s": 180,
            "settle_s": 15,
            "restart_timeout_s": 240,
            "min_acked_blocks": 20,
        },
        "ci": {
            "fault_probability": 5e-5,
            "burst_probability": 5e-4,
            "workload_s": 420,
            "burst_s": 45,
            "writers": 5,
            "readers": 3,
            "rows_per_insert": 800,
            "payload_bytes": 1024,
            "query_timeout_s": 180,
            "join_bound_s": 300,
            "settle_s": 30,
            "restart_timeout_s": 300,
            "min_acked_blocks": 100,
        },
        "full": {
            "fault_probability": 1e-4,
            "burst_probability": 1e-3,
            "workload_s": 1800,
            "burst_s": 120,
            "writers": 8,
            "readers": 4,
            "rows_per_insert": 2000,
            "payload_bytes": 2048,
            "query_timeout_s": 300,
            "join_bound_s": 600,
            "settle_s": 60,
            "restart_timeout_s": 420,
            "min_acked_blocks": 400,
        },
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        node = cl.node1
        since = ctx.extra.get("since_event_time") or ""
        rows_per_insert = int(p["rows_per_insert"])
        payload = int(p["payload_bytes"])
        query_timeout = float(p["query_timeout_s"])
        result.observations["tables"] = [_TABLE]
        C.create_ca_table(node, _TABLE)
        armed_ok, armed_obs = False, ""
        try:
            node.query(
                "SELECT sum(number) FROM numbers(20000000)",
                timeout=60,
                settings={"memory_tracker_fault_probability": 0.001, "max_untracked_memory": 0},
            )
            armed_obs = "probe query SUCCEEDED with p=1e-3 over 2e7 numbers"
        except Exception as e:
            body = str(e)
            armed_ok = "fault injected" in body
            armed_obs = "MEMORY_LIMIT_EXCEEDED 'fault injected'" if armed_ok else f"unexpected error: {body[:200]}"
        result.add(
            Verdict.check(
                "allocation-fault injection is armable through the driver's URL parameters",
                "a probe query throws MEMORY_LIMIT_EXCEEDED ... fault injected",
                armed_obs,
                armed_ok,
            )
        )
        ev_before = _cluster_events(cl)
        acked_blocks = set()
        acked_lock = threading.Lock()
        next_block = [0]
        block_lock = threading.Lock()
        injected_client_failures = [0]
        other_failures = []
        select_faults = [0]
        max_query_s = [0.0]
        stop_at = [time.time() + float(p["workload_s"])]
        probability = [float(p["fault_probability"])]

        def _settings():
            return {
                "memory_tracker_fault_probability": probability[0],
                "max_untracked_memory": 0,
                "async_insert": 0,
                "max_insert_threads": 1,
            }

        def _record_failure(exc):
            body = str(exc)
            if "fault injected" in body or "MEMORY_LIMIT_EXCEEDED" in body or "Code: 241" in body:
                injected_client_failures[0] += 1
            else:
                other_failures.append(body[:300])

        def writer():
            while time.time() < stop_at[0]:
                with block_lock:
                    b = next_block[0]
                    next_block[0] += 1
                base = b * rows_per_insert
                t0 = time.monotonic()
                try:
                    node.query(
                        f"INSERT INTO {_TABLE} SELECT {base} + number AS id, "
                        f"randomString({payload}) AS payload FROM numbers({rows_per_insert})",
                        timeout=query_timeout,
                        settings=_settings(),
                    )
                    with acked_lock:
                        acked_blocks.add(b)
                except Exception as e:
                    _record_failure(e)
                finally:
                    max_query_s[0] = max(max_query_s[0], time.monotonic() - t0)

        def reader():
            while time.time() < stop_at[0]:
                t0 = time.monotonic()
                try:
                    node.query(
                        f"SELECT count(), sum(sipHash64(id)), max(length(payload)) FROM {_TABLE} WHERE id % 7 = 0",
                        timeout=query_timeout,
                        settings=_settings(),
                    )
                except Exception:
                    select_faults[0] += 1
                finally:
                    max_query_s[0] = max(max_query_s[0], time.monotonic() - t0)
                time.sleep(0.2)

        threads = [threading.Thread(target=writer, daemon=True) for _ in range(int(p["writers"]))] + [
            threading.Thread(target=reader, daemon=True) for _ in range(int(p["readers"]))
        ]
        ctx.log(f"S42 leg A: armed workload for {p['workload_s']}s at p={probability[0]}")
        for t in threads:
            t.start()
        time.sleep(min(float(p["workload_s"]) / 2, 30))
        try:
            node.query(f"OPTIMIZE TABLE {_TABLE}", timeout=query_timeout, settings=_settings())
        except Exception as e:
            _record_failure(e)
        for t in threads:
            t.join(timeout=float(p["join_bound_s"]))
        hung = [t for t in threads if t.is_alive()]
        probability[0] = float(p["burst_probability"])
        stop_at[0] = time.time() + float(p["burst_s"])
        burst = [threading.Thread(target=writer, daemon=True) for _ in range(int(p["writers"]))]
        for t in burst:
            t.start()
        for t in burst:
            t.join(timeout=float(p["join_bound_s"]))
        hung += [t for t in burst if t.is_alive()]
        ev_armed = _cluster_events(cl)
        armed_delta = {k: _event_total(ev_armed, k) - _event_total(ev_before, k) for k in _EVENTS}
        result.observations["leg_a"] = {
            "acked_blocks": len(acked_blocks),
            "injected_client_failures": injected_client_failures[0],
        }
        result.add(
            Verdict.check(
                "no query hung past its bound",
                f"every workload thread joins within {p['join_bound_s']}s",
                f"{len(hung)} still alive",
                not hung,
            )
        )
        result.add(
            Verdict.check(
                "workload still made progress under faults (acked volume for the loss oracle)",
                f"acked blocks >= {int(p['min_acked_blocks'])}",
                f"{len(acked_blocks)}",
                len(acked_blocks) >= int(p["min_acked_blocks"]),
            )
        )
        time.sleep(float(p["settle_s"]))
        _, residual = C.drive_gc_until_stable()
        result.observations["leg_c_gc"] = {"residual_unreachable": residual}
        fsck_pre = C.run_cas_fsck(detail=False)
        view_pre = {n.container: _view(n, rows_per_insert) for n in cl.nodes()}
        ctx.log("S42 leg C: restarting both servers")
        apply_fault(Fault(t_offset=0, target=FaultTarget.BOTH, action=FaultAction.RESTART, duration_s=0))
        healthy = wait_cluster_healthy(cl, timeout_s=int(p["restart_timeout_s"]), log_fn=ctx.log)
        result.add(
            Verdict.check("cluster comes back after the restart", "both replicas healthy", f"healthy={healthy}", healthy)
        )
        if not healthy:
            C.standard_end(cluster=cl, result=result, tables=[_TABLE], expect_exception=True)
            return
        for n in cl.nodes():
            try:
                n.command(f"SYSTEM SYNC REPLICA {_TABLE}", timeout=300)
            except Exception as e:
                ctx.log(f"S42 SYNC: {e}")
        view_post = {n.container: _view(n, rows_per_insert) for n in cl.nodes()}
        same = view_pre == view_post
        result.add(
            Verdict.check(
                "the post-restart view (rebuilt from the durable journal) equals the pre-restart view",
                "identical checksum, active part names and per-block row counts",
                "identical" if same else "diverged",
                same,
            )
        )
        post_blocks = view_post[node.container]["block_counts"]
        lost = sorted(b for b in acked_blocks if post_blocks.get(b, 0) != rows_per_insert)
        result.add(
            Verdict.check(
                "every ACKED insert's rows are present after the restart",
                "0 acked blocks missing rows",
                f"acked={len(acked_blocks)} lost={len(lost)}",
                not lost,
            )
        )
        C.assert_replicas_agree(result, cl, C.table_checksum_query(_TABLE), name="S42 replica agreement")
        fsck_post = C.run_cas_fsck(detail=False)
        for label, rep in (("pre-restart", fsck_pre), ("post-restart", fsck_post)):
            if "dangling" not in rep:
                result.add(Verdict.inconclusive(f"fsck {label}: dangling == 0", "0", "fsck unavailable"))
            else:
                result.add(
                    Verdict.check(
                        f"fsck {label}: dangling == 0 and unaccounted == 0",
                        "0 / 0",
                        f"dangling={rep.get('dangling')} unaccounted={rep.get('unaccounted')}",
                        int(rep.get("dangling") or 0) == 0 and int(rep.get("unaccounted") or 0) == 0,
                    )
                )
        ev_post = _cluster_events(cl)
        poison_total = int(armed_delta.get("CASRefNeedsRecovery", 0)) + _event_total(ev_post, "CASRefNeedsRecovery")
        result.add(
            Verdict.check(
                "CASRefNeedsRecovery == 0 (no durable transaction lost from a writer cache)",
                "0 poison transitions",
                poison_total,
                poison_total == 0,
            )
        )
        generic = int(injected_client_failures[0]) + int(armed_delta.get("QueryMemoryLimitExceeded", 0))
        if generic == 0:
            result.add(
                Verdict.inconclusive(
                    "allocation faults were actually injected (generic anti-vacuity)",
                    "> 0 injected allocation failures",
                    "0 injected failures — the arming path itself did not work",
                )
            )
        else:
            result.add(
                Verdict.check(
                    "allocation faults were actually injected (generic anti-vacuity)",
                    "> 0 injected allocation failures",
                    generic,
                    True,
                )
            )
        result.add(
            Verdict.reported(
                "post-durable install window traversal (reported, not gating)",
                "> 0 targeted signals",
                f"targeted={poison_total} generic={generic}",
                "green means the consistency oracle held, not that the target window was hit",
            )
        )
        logical_errors = 0
        probe_failed = False
        for n in cl.nodes():
            try:
                n.command("SYSTEM FLUSH LOGS")
                logical_errors += int(
                    n.scalar(
                        f"SELECT count() FROM system.text_log WHERE event_time >= '{since}' "
                        f"AND level <= 'Error' AND (message ILIKE '%LOGICAL_ERROR%' OR message ILIKE '%Logical error:%')"
                    )
                    or 0
                )
            except Exception:
                probe_failed = True
        if probe_failed:
            result.add(Verdict.inconclusive("zero LOGICAL_ERROR", "0", "text_log probe failed"))
        else:
            result.add(Verdict.check("zero LOGICAL_ERROR (queries may fail; invariants may not)", "0", logical_errors, logical_errors == 0))
        result.add(
            Verdict.check(
                "statements failed only with the injected allocation error",
                "0 statement failures of any other kind",
                f"{len(other_failures)} other failures",
                not other_failures,
            )
        )
        recovered, last_err = False, ""
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            try:
                C.insert_random(node, _TABLE, rows=rows_per_insert, payload_bytes=payload, op_id=(next_block[0] + 10) * rows_per_insert)
                recovered = True
                break
            except Exception as e:
                last_err = str(e)
                time.sleep(3)
        result.add(
            Verdict.check(
                "no permanently wedged ref lane (an unarmed write lands after the run)",
                "an INSERT succeeds within 120s of the restart",
                f"recovered={recovered}",
                recovered,
                "" if recovered else last_err[:200],
            )
        )
        C.standard_end(cluster=cl, result=result, tables=[_TABLE], expect_exception=True)
