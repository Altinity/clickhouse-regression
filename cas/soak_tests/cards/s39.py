"""S39 mount-lease fault tolerance (P1).

Two fault legs against the object-store proxy. The runner points the ``ca``
disk at that proxy for this card. A down control port fails the card.
"""

import json as _json
import threading
import time
import urllib.request

from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C
from cas.soak_tests.steps import observe as O

_TABLE = "s39_lease"
_CTL = "http://localhost:8474"
_MOUNT_LEASE_TTL_S = 30
_MOUNT_RENEW_PERIOD_S = 10


def _ctl(path, body=None, timeout=10):
    """GET or POST the fault-proxy control port."""
    url = f"{_CTL}{path}"
    if body is None:
        return _json.loads(urllib.request.urlopen(url, timeout=timeout).read().decode())
    req = urllib.request.Request(
        url,
        data=_json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    return _json.loads(urllib.request.urlopen(req, timeout=timeout).read().decode())


def _text_log_count(node, since: str, needle: str, logger: str = "CasMountLeaseRenewer") -> int:
    """Count renewer text_log rows containing needle at or after since. Probe failure is -1.

    26.6.4 logs under CasMountLeaseRenewer: ``physical retry attempt`` (Debug),
    ``recovered after`` (Information), ``fenced after`` (Warning). The older
    CasMountLeaseKeeper sentences this card used to match were removed.
    """
    try:
        node.command("SYSTEM FLUSH LOGS")
        v = node.scalar(
            f"SELECT count() FROM system.text_log WHERE event_time >= '{since}' "
            f"AND logger_name = '{logger}' AND message ILIKE '%{needle}%'"
        )
        return int(v or 0)
    except Exception:
        return -1


def _across(nodes, since: str, needle: str, counter) -> tuple[int | None, dict]:
    """Sum one log counter across every replica.

    A probe failure (-1) on any replica makes the total None. Treating that as
    zero let a fenced replica pass when the card only asked the first node.
    """
    per = {}
    total = 0
    for n in nodes:
        count = counter(n, since, needle)
        per[n.container] = count
        if count < 0:
            return None, per
        total += count
    return total, per


def _watermark_renew_count(node, since: str, outcome: str) -> int:
    """Count cas_log watermark_renew rows with this outcome at or after since. Probe failure is -1."""
    try:
        node.command("SYSTEM FLUSH LOGS")
        v = node.scalar(
            f"SELECT count() FROM system.cas_log WHERE event_time >= '{since}' "
            f"AND event_type = 'watermark_renew' AND outcome = '{outcome}'"
        )
        return int(v or 0)
    except Exception:
        return -1


@register
class S39(Scenario):
    name = "S39"
    title = "mount-lease resilience under a degraded-but-alive S3 (fix #37)"
    priority = "P1"
    compose_variant = "s3faultproxy"
    # Leg B holds PUT/POST 503s past the mount-lease TTL; GC Error finish rows during that window
    # are expected. The lease checks are the card; do not FAIL the common 0-Failed check.
    allow_gc_failed = True
    # INVARIANT (every scale row must keep this, see `_MOUNT_LEASE_TTL_S`/`_MOUNT_RENEW_PERIOD_S`
    # above and the leg-A/leg-B asserts below): short_fault_s < _MOUNT_RENEW_PERIOD_S (10) and
    # << _MOUNT_LEASE_TTL_S (30), so the short leg overlaps at most one renewal beat.
    # long_fault_s > _MOUNT_LEASE_TTL_S (30), so a renewal is still in flight when the confirmed
    # budget runs out. Since #2431 the renewer retries that same renewal until the store answers;
    # a 503 is not a reason to fence. `ci` was 15 and `full` was 20; both overlapped a renewal
    # beat, so both are 9 now.
    param_table = {
        "dev": {"short_fault_s": 8, "long_fault_s": 40, "settle_s": 20, "rows": 2000, "payload_bytes": 512},
        "ci": {"short_fault_s": 9, "long_fault_s": 50, "settle_s": 40, "rows": 20000, "payload_bytes": 1024},
        "full": {"short_fault_s": 9, "long_fault_s": 60, "settle_s": 60, "rows": 100000, "payload_bytes": 2048},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        node = cl.nodes()[0]
        rows = int(p["rows"])
        payload = int(p["payload_bytes"])

        # Disarm first: bring-up must be clean regardless of a prior run's state.
        try:
            hz = _ctl("/healthz")
        except Exception as e:
            result.add(Verdict("fault proxy reachable", "control :8474 up",
                                f"unreachable: {e}", "fail"))
            return
        result.observations["proxy"] = {"healthz": hz}
        _ctl("/config", {"rate": 0.0})

        # Create the ReplicatedMergeTree on EVERY node: a replicated table materializes per-replica
        # (each replica runs its own CREATE against the shared zk path), so creating it only on node1
        # would leave node2 without the table entirely and the end-of-run replica-agreement check would
        # see UNKNOWN_TABLE on node2. All the fault/write legs below still drive node1 (`node`) only --
        # this is a single-writer mount-lease test -- but node2 must exist as a real replica so the
        # standard replica-agreement / fsck end-checks are meaningful.
        for n in cl.nodes():
            C.create_ca_table(n, _TABLE, columns="id UInt64, payload String", order_by="id", wide=True)
        C.insert_random(node, _TABLE, rows=rows // 4, payload_bytes=payload, op_id=0)

        # --- Leg A: SHORT fault (< lease TTL) -- the mount lease must survive ---
        since_a = node.scalar("SELECT toString(now())")
        short_s = int(p["short_fault_s"])
        assert short_s < _MOUNT_LEASE_TTL_S, "leg A's fault window must stay under the lease TTL"
        assert short_s < _MOUNT_RENEW_PERIOD_S, (
            "leg A's fault window must be shorter than the renew period so it can overlap AT MOST "
            "one renewal beat -- a window >= the renew period can fault two consecutive beats and "
            "(correctly) near the lease deadline, which is leg B's job, not leg A's")
        # The best-effort write MUST run in a background thread, NOT inline: a blocking insert keeps
        # retrying under the fault for its whole CAS budget (~20s), which would keep the fault armed
        # for insert-duration + short_s and turn this leg into the long one. This leg asserts the
        # renewer rides out one beat, not that the INSERT succeeds. The write only loads the write
        # path while armed. Decoupling it keeps the armed window exactly short_s, so the window can
        # fault at most one renewal beat.
        errs_a: list[str] = []
        def _bg_write_a():
            try:
                C.insert_random(node, _TABLE, rows=rows // 4, payload_bytes=payload, op_id=rows,
                                  timeout=short_s + 15)
            except Exception as e:
                errs_a.append(str(e))
        _ctl("/config", {"rate": 1.0, "modes": ["503"], "methods": ["PUT", "POST"], "seed": 39})
        writer_a = threading.Thread(target=_bg_write_a, daemon=True)
        writer_a.start()
        time.sleep(short_s)                     # armed window is EXACTLY short_s, write-independent
        _ctl("/config", {"rate": 0.0})
        writer_a.join(timeout=30)               # reap the background writer (faulted or completed)
        if errs_a:
            ctx.log(f"S39 leg A background INSERT under fault (expected to possibly fail/retry): {errs_a[0]}")
        time.sleep(_MOUNT_RENEW_PERIOD_S / 2)   # let the post-clear renewal beat land

        # An 8s window is shorter than the 10s renew period, so it can miss the beat entirely.
        # A miss is not a failure. A hit shows up as an Information "recovered after" line.
        # Count every replica. A run where clickhouse2 fenced and clickhouse1 recovered
        # used to pass, because this card only read the first node's text_log.
        nodes = cl.nodes()
        recovered_a, rec_per = _across(nodes, since_a, "recovered after", _text_log_count)
        fenced_a, fence_per = _across(nodes, since_a, "fenced after", _text_log_count)
        result.observations["leg_a"] = {
            "recovered_lines": recovered_a,
            "fence_lines": fenced_a,
            "recovered_per_replica": rec_per,
            "fence_per_replica": fence_per,
        }
        if recovered_a is None or fenced_a is None:
            result.add(Verdict.inconclusive(
                "leg A (short fault): renewal overlapped the fault window",
                "a readable text_log on every replica",
                f"recovered={rec_per} fenced={fence_per}"))
        elif recovered_a > 0:
            result.add(Verdict.check(
                "leg A (short fault): a renewal that hit the fault recovered",
                "> 0 'recovered after' lines", f"{rec_per}", True, ""))
        elif fenced_a == 0:
            result.add(Verdict.inconclusive(
                "leg A (short fault): renewal overlapped the fault window",
                "a 'recovered after' line, or no renewal during the window",
                "no CasMountLeaseRenewer line on any replica; the 8s window can miss the 10s renew beat"))
        result.add(Verdict.check(
            "leg A (short fault): mount lease NEVER fenced",
            "0 'fenced after' lines on every replica", f"{fence_per}",
            fenced_a == 0,
            "" if fenced_a == 0 else (
                "could not read text_log on every replica"
                if fenced_a is None else "the mount lease fenced during a SHORT fault")))

        # Post-disarm write must succeed on every replica: a fenced peer still
        # refuses writes after the writer has recovered. Record that and stop,
        # so the failure stays on this leg instead of aborting the card.
        write_errs = []
        for i, n in enumerate(nodes):
            try:
                C.insert_random(n, _TABLE, rows=rows // 4, payload_bytes=payload, op_id=2 * rows + i)
            except Exception as e:
                write_errs.append(f"{n.container}: {e}")
        if write_errs:
            result.add(Verdict.check(
                "leg A (short fault): a write succeeds once the fault clears",
                "INSERT succeeds on every replica", "; ".join(write_errs)[:300], False,
                "the short fault left a replica unable to accept writes"))
            return

        # --- Leg B: LONG fault (> lease TTL) -- retry the same renewal, do not fence ---
        # A 503 is not a definitive answer. The renewer keeps sending the same renewal until the
        # store accepts it, including after the confirmed budget hits zero (#2431).
        since_b = node.scalar("SELECT toString(now())")
        _ctl("/config", {"rate": 1.0, "modes": ["503"], "methods": ["PUT", "POST"], "seed": 40})
        long_s = int(p["long_fault_s"])
        assert long_s > _MOUNT_LEASE_TTL_S, "leg B's fault window must exceed the lease TTL"
        try:
            C.insert_random(node, _TABLE, rows=rows // 4, payload_bytes=payload, op_id=3 * rows,
                              timeout=min(long_s, 30))
            node.command(f"OPTIMIZE TABLE {_TABLE} FINAL", timeout=min(long_s, 30))
        except Exception as e:
            ctx.log(f"S39 leg B write/merge under sustained fault (expected to fail/retry): {e}")
        time.sleep(long_s)
        _ctl("/config", {"rate": 0.0})

        # Give the queue's backoff + self-remount time to recover.
        time.sleep(int(p["settle_s"]))

        recovered_b, rec_b_per = _across(nodes, since_b, "recovered after", _text_log_count)
        fenced_b, fence_b_per = _across(nodes, since_b, "fenced after", _text_log_count)
        renew_ok_b, renew_ok_per = _across(nodes, since_b, "recovered", _watermark_renew_count)
        renew_failed_b, renew_fail_per = _across(nodes, since_b, "failed", _watermark_renew_count)
        result.observations["leg_b"] = {
            "recovered_lines": recovered_b,
            "fence_lines": fenced_b,
            "watermark_renew_recovered": renew_ok_b,
            "watermark_renew_failed": renew_failed_b,
            "recovered_per_replica": rec_b_per,
            "fence_per_replica": fence_b_per,
            "watermark_renew_recovered_per_replica": renew_ok_per,
            "watermark_renew_failed_per_replica": renew_fail_per,
        }
        readable = None not in (recovered_b, fenced_b, renew_ok_b, renew_failed_b)
        every_recovered = readable and all(v > 0 for v in rec_b_per.values()) and all(
            v > 0 for v in renew_ok_per.values())
        none_fenced = readable and fenced_b == 0 and renew_failed_b == 0
        leg_b_ok = every_recovered and none_fenced
        result.add(Verdict.check(
            "leg B (long fault): every replica recovered the renewal without fencing",
            "each replica has a 'recovered after' line and a recovered watermark_renew, and no fence",
            f"recovered={rec_b_per} fenced={fence_b_per} "
            f"watermark_recovered={renew_ok_per} watermark_failed={renew_fail_per}",
            leg_b_ok,
            "" if leg_b_ok else
            "a fault held past the lease TTL fenced a replica, or a replica never logged recovery"))

        try:
            queue_rows = node.query(
                f"SELECT num_postponed, num_tries, last_exception FROM system.replication_queue "
                f"WHERE table = '{_TABLE}' ORDER BY num_tries DESC LIMIT 5 FORMAT TabSeparated").strip()
            rows_list = [r.split("\t") for r in queue_rows.splitlines() if r]
        except Exception:
            rows_list = None
        if rows_list is None:
            result.add(Verdict.inconclusive(
                "long fault: replication_queue backoff visibility", "populated or empty",
                "system.replication_queue query failed"))
        elif not rows_list:
            # Nothing queued at all during the outage is a legitimate outcome (no merge happened to
            # collide with the fault window) -- not a failure, just nothing to check here.
            result.observations["leg_b"]["queue_rows_at_check"] = 0
        else:
            any_last_exception_populated = any(r[2].strip() for r in rows_list if len(r) > 2)
            result.observations["leg_b"]["queue_sample"] = rows_list[:5]
            result.add(Verdict.check(
                "long fault: system.replication_queue.last_exception is populated (fixes #37 phases 2/3)",
                "at least one non-empty last_exception among queued/recent entries", "see observations",
                any_last_exception_populated,
                "" if any_last_exception_populated else
                "queue entries exist but last_exception is empty everywhere -- the OLD ABORTED "
                "no-visibility defect may have resurfaced"))

        # Post-recovery: a fresh write must succeed once the fault clears and the self-remount lands.
        # Recovery is ASYNCHRONOUS -- self-remount (~16s per the #37 spec) plus the replication-queue
        # backoff -- and under load it routinely exceeds `settle_s`, so a single bare INSERT here is
        # flaky: it throws the (correct, expected) retry-later NETWORK_ERROR while recovery is still in
        # flight and crashes the leg. POLL instead: retry the write until it lands within a generous
        # budget. A retry-later NETWORK_ERROR means "not recovered yet", NOT a failure; the verdict is
        # the whole point of #37 -- writes RESUME after the fault clears, they are not permanently wedged.
        recovered = False
        last_err = ""
        recover_deadline = time.monotonic() + 90
        while time.monotonic() < recover_deadline:
            try:
                C.insert_random(node, _TABLE, rows=rows // 4, payload_bytes=payload, op_id=4 * rows,
                                  timeout=30)
                recovered = True
                break
            except Exception as e:
                last_err = str(e)
                time.sleep(3)
        final_count = node.scalar(f"SELECT count() FROM {_TABLE}") if recovered else "0"
        result.add(Verdict.check(
            "post-recovery INSERT succeeds within the recovery budget (writes resume, not wedged)",
            "an INSERT lands within 90s of the fault clearing", f"recovered={recovered} count={final_count}",
            recovered and int(final_count or 0) > 0,
            "" if recovered else f"no write succeeded within 90s after the fault cleared -- self-remount "
                                 f"recovery did not resume writes (last error: {last_err[:200]})"))

        # node2 replicates node1's writes through the same faulted S3; after leg B it may still be
        # fetching. Sync it deterministically before the agreement check so we compare converged state,
        # not a mid-catch-up snapshot (the check itself only polls ~8s, too short after a long fault).
        for n in cl.nodes():
            try:
                n.command(f"SYSTEM SYNC REPLICA {_TABLE}", timeout=120)
            except Exception as e:
                ctx.log(f"S39 SYNC REPLICA on a node before agreement check (best-effort): {e}")
        C.assert_replicas_agree(result, cl, C.table_checksum_query(_TABLE),
                                      name="S39 replica agreement")
        C.checkpoint_view(cl, result, [_TABLE], allow_gc_failed=self.allow_gc_failed)
