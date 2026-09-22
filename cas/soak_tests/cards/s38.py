"""S38 unclean handover: epoch seal makes a late predecessor PUT lose (P0)."""

import threading
import time

from cas.soak_tests.oracle.chaos import Fault, FaultAction, FaultTarget
from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C
from cas.soak_tests.steps.chaos import apply_fault
from cas.soak_tests.steps.observe import wait_cluster_healthy
from cas.soak_tests.steps.s3_inject import (
    HUGE_SEQ,
    POOL_PREFIX,
    REF_LOG_SUFFIX,
    bucket,
    discover_single_life_id,
    list_keys,
    parse_ref_txn_id,
    render_ref_txn_id,
    restamp_ref_log_txn,
    s3_client,
    zstd_decompress,
)

_TABLE = "s38_handover"
_VIOLATION_EVENTS = ("CASRefNeedsRecovery", "CASGCUnappliedFoldedTransactions", "CASRefRecoveryStreamHole")


def _text_log_count(node, since, needle):
    try:
        node.command("SYSTEM FLUSH LOGS")
    except Exception:
        pass
    try:
        v = node.scalar(
            f"SELECT count() FROM system.text_log WHERE event_time >= '{since}' "
            f"AND message ILIKE '%{needle}%'"
        )
        return int(v or 0)
    except Exception:
        return -1


def _violation_counters(cluster, events):
    peak = {e: 0 for e in events}
    names = ", ".join(f"'{e}'" for e in events)
    for node in cluster.nodes():
        txt = node.query(
            f"SELECT event, value FROM system.events WHERE event IN ({names}) "
            f"FORMAT TabSeparated SETTINGS system_events_show_zero_values = 1"
        )
        ev = {}
        for line in (txt or "").splitlines():
            if "\t" in line:
                k, v = line.split("\t", 1)
                try:
                    ev[k] = int(v)
                except ValueError:
                    pass
        missing = [e for e in events if e not in ev]
        if missing:
            raise RuntimeError(f"counter probe on {node!r} missing {missing}")
        for e in events:
            peak[e] = max(peak[e], int(ev[e]))
    return peak


def _events_snapshot(node):
    return C.events_snapshot(node)


@register
class S38(Scenario):
    name = "S38"
    title = "unclean handover: the epoch seal makes a late predecessor PUT lose"
    priority = "P0"
    param_table = {
        "dev": {
            "storm_inserts": 20,
            "rows_per_insert": 50,
            "payload_bytes": 512,
            "kill_delay_s": 1.5,
            "kill_down_s": 3,
            "heal_timeout_s": 180,
        },
        "ci": {
            "storm_inserts": 60,
            "rows_per_insert": 300,
            "payload_bytes": 1024,
            "kill_delay_s": 2.0,
            "kill_down_s": 4,
            "heal_timeout_s": 240,
        },
        "full": {
            "storm_inserts": 150,
            "rows_per_insert": 1000,
            "payload_bytes": 2048,
            "kill_delay_s": 3.0,
            "kill_down_s": 5,
            "heal_timeout_s": 300,
        },
    }

    def run(self, ctx, result):
        try:
            import zstandard  # noqa: F401
            import boto3  # noqa: F401
        except ImportError as e:
            result.add(Verdict.inconclusive("s38 python deps", "boto3+zstandard", str(e)))
            return
        cl = ctx.cluster
        p = ctx.params
        result.observations["tables"] = [_TABLE]
        storm_inserts = int(p["storm_inserts"])
        rows = int(p["rows_per_insert"])
        payload = int(p["payload_bytes"])
        C.create_ca_table(cl.node1, _TABLE)
        since_kill = cl.node1.scalar("SELECT toString(now())")
        stop = threading.Event()
        wl_stats = {"inserts_ok": 0, "inserts_failed": 0}

        def _storm():
            i = 0
            while not stop.is_set() and i < storm_inserts:
                try:
                    C.insert_random(cl.node1, _TABLE, rows=rows, payload_bytes=payload, op_id=i * rows)
                    wl_stats["inserts_ok"] += 1
                except Exception:
                    wl_stats["inserts_failed"] += 1
                i += 1

        wl_thread = threading.Thread(target=_storm, daemon=True)
        wl_thread.start()
        time.sleep(float(p["kill_delay_s"]))
        ctx.log("S38: KILL ch1 mid append-storm")
        apply_fault(
            Fault(
                t_offset=0,
                target=FaultTarget.CH1,
                action=FaultAction.KILL,
                duration_s=int(p["kill_down_s"]),
            )
        )
        stop.set()
        wl_thread.join(timeout=120)
        result.observations["storm_stats"] = wl_stats
        healthy = wait_cluster_healthy(cl, timeout_s=int(p["heal_timeout_s"]), log_fn=ctx.log)
        result.add(Verdict.check("ch1 recovers after kill -9", "healthy within heal_timeout_s", f"healthy={healthy}", healthy))
        if not healthy:
            C.standard_end(cluster=cl, result=result, tables=[_TABLE])
            return
        obs_n = _text_log_count(cl.node1, since_kill, "stale-looking mount lease")
        sparing_n = _text_log_count(cl.node1, since_kill, "delete_pending retired entry recovered in-degree")
        if obs_n < 0:
            result.add(
                Verdict.inconclusive(
                    "observation wait line appears (unclean restart)",
                    ">0 'stale-looking mount lease' rows",
                    "system.text_log not queryable",
                )
            )
        else:
            result.add(
                Verdict.check(
                    "observation wait line appears (unclean restart)",
                    ">0 'stale-looking mount lease' rows",
                    obs_n,
                    obs_n > 0,
                )
            )
        if sparing_n < 0:
            result.add(
                Verdict.inconclusive(
                    "no in-degree sparing warning (delete_pending retired entry recovered)",
                    "0",
                    "system.text_log not queryable",
                )
            )
        else:
            result.add(
                Verdict.check(
                    "no in-degree sparing warning (delete_pending retired entry recovered)",
                    "0",
                    sparing_n,
                    sparing_n == 0,
                )
            )
        pre_inject_checksum = cl.node1.query(C.table_checksum_query(_TABLE)).strip()
        sealed = _events_snapshot(cl.node1).get("CASRefRecoveryEpochSealed", 0)
        result.add(
            Verdict.check(
                "the unclean restart's recovery sealed the dead epoch",
                "CASRefRecoveryEpochSealed > 0",
                sealed,
                sealed > 0,
            )
        )
        if not sealed:
            C.standard_end(cluster=cl, result=result, tables=[_TABLE])
            return
        s3 = s3_client()
        life_id = discover_single_life_id(s3)
        result.observations["discovered_life_id"] = life_id
        if life_id is None:
            result.add(
                Verdict.inconclusive(
                    "opaque life id discovered for injection",
                    "exactly one canonical 32-hex child under cas/ns/stream/",
                    "the single-table pool did not expose one unambiguous life-id child",
                )
            )
            C.standard_end(cluster=cl, result=result, tables=[_TABLE])
            return
        log_prefix = f"{POOL_PREFIX}/cas/ns/stream/{life_id}/_log/"
        ids = [i for i in (parse_ref_txn_id(k[len(log_prefix) :]) for k in list_keys(s3, log_prefix)) if i is not None]
        epochs = sorted({e for e, _ in ids})
        dead_epoch = seal_seq = seal_key = seal_body = None
        for candidate in epochs:
            top = max(sq for e, sq in ids if e == candidate)
            key = f"{log_prefix}{render_ref_txn_id(candidate, top)}{REF_LOG_SUFFIX}"
            body = s3.get_object(Bucket=bucket(), Key=key)["Body"].read()
            if b'"epoch_seal"' in zstd_decompress(body):
                dead_epoch, seal_seq, seal_key, seal_body = candidate, top, key, body
                break
        if dead_epoch is None:
            result.add(
                Verdict.inconclusive(
                    "a dead epoch exists to be sealed",
                    "one listed writer epoch whose highest ref-log id carries an epoch_seal",
                    f"epochs present: {epochs}",
                )
            )
            C.standard_end(cluster=cl, result=result, tables=[_TABLE])
            return
        result.add(
            Verdict.check(
                "the top of the dead epoch's stream IS an epoch seal",
                "the object at the dead epoch's highest ref-log id carries an epoch_seal op",
                render_ref_txn_id(dead_epoch, seal_seq),
                True,
            )
        )
        straggler_body = restamp_ref_log_txn(seal_body, seal_seq)
        outcome = {"raised": None, "http_status": None}
        try:
            s3.put_object(Bucket=bucket(), Key=seal_key, Body=straggler_body, IfNoneMatch="*")
        except Exception as e:
            resp = getattr(e, "response", None) or {}
            outcome["raised"] = type(e).__name__
            outcome["http_status"] = resp.get("ResponseMetadata", {}).get("HTTPStatusCode")
        refused = outcome["http_status"] in (409, 412)
        result.add(
            Verdict.check(
                "a straggler's conditional create at the sealed id is REFUSED by the store",
                "HTTP 412 (or 409)",
                outcome,
                refused,
            )
        )
        after_refusal = s3.get_object(Bucket=bucket(), Key=seal_key)["Body"].read()
        result.add(
            Verdict.check(
                "the seal object is byte-for-byte unchanged by the refused create",
                "GET returns the seal that was there before",
                f"identical={after_refusal == seal_body}",
                after_refusal == seal_body,
            )
        )
        injected_id = render_ref_txn_id(dead_epoch, HUGE_SEQ)
        injected_key = f"{log_prefix}{injected_id}{REF_LOG_SUFFIX}"
        injected_body = restamp_ref_log_txn(seal_body, HUGE_SEQ)
        s3.put_object(Bucket=bucket(), Key=injected_key, Body=injected_body)
        violations_before = _violation_counters(cl, _VIOLATION_EVENTS)
        for _ in range(3):
            C.gc_drive_round(cl, log_fn=ctx.log)
        violations_after = _violation_counters(cl, _VIOLATION_EVENTS)
        moved = {e: violations_after[e] - violations_before[e] for e in _VIOLATION_EVENTS if violations_after[e] > violations_before[e]}
        result.add(
            Verdict.check(
                "no always-zero counter moved across the injection and driven GC",
                f"all of {', '.join(_VIOLATION_EVENTS)} unchanged",
                {"moved": moved} if moved else "unchanged",
                not moved,
            )
        )
        post_inject_checksum = cl.node1.query(C.table_checksum_query(_TABLE)).strip()
        result.add(
            Verdict.check(
                "queries return only sealed truth (the injection has no observable effect)",
                "table checksum unchanged by the injected dead-epoch log",
                f"pre={pre_inject_checksum!r} post={post_inject_checksum!r}",
                post_inject_checksum == pre_inject_checksum,
            )
        )
        C.assert_replicas_agree(result, cl, C.table_checksum_query(_TABLE), name="S38 replica agreement after injection")
        ctx.log("S38: graceful restart ch1")
        apply_fault(Fault(t_offset=0, target=FaultTarget.CH1, action=FaultAction.RESTART, duration_s=0))
        healthy_clean = wait_cluster_healthy(cl, timeout_s=int(p["heal_timeout_s"]), log_fn=ctx.log)
        result.add(Verdict.check("ch1 recovers after a clean restart", "healthy", f"healthy={healthy_clean}", healthy_clean))
        if not healthy_clean:
            C.standard_end(cluster=cl, result=result, tables=[_TABLE])
            return
        rerecovered = cl.node1.query(C.table_checksum_query(_TABLE)).strip()
        result.add(
            Verdict.check(
                "re-recovery from the durable stream still ignores the injected log",
                "checksum after a full restart equals the pre-injection checksum",
                f"pre={pre_inject_checksum!r} re-recovered={rerecovered!r}",
                rerecovered == pre_inject_checksum,
            )
        )
        clean_sealed = _events_snapshot(cl.node1).get("CASRefRecoveryEpochSealed", 0)
        result.add(
            Verdict.check(
                "a CLEAN restart seals its predecessor's epoch too",
                "CASRefRecoveryEpochSealed > 0",
                clean_sealed,
                clean_sealed > 0,
            )
        )
        C.standard_end(cluster=cl, result=result, tables=[_TABLE])
