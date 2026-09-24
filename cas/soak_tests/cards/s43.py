"""S43 same-uuid pool recreation refuses a residual survivor write (P0)."""

from cas.soak_tests.oracle.chaos import Fault, FaultAction, FaultTarget
from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C
from cas.soak_tests.steps.chaos import apply_fault
from cas.soak_tests.steps.http import QueryError
from cas.soak_tests.steps.observe import wait_cluster_healthy
from cas.soak_tests.steps.s3_inject import (
    POOL_PREFIX,
    REF_LOG_SUFFIX,
    bucket,
    discover_single_life_id,
    list_keys,
    render_ref_txn_id,
    restamp_ref_log_txn,
    s3_client,
    zstd_decompress,
)

_TABLE = "w3_recreated"
_DISK = "ca"
_UUID = "3e1f0a2b-4c5d-4e6f-8a9b-0c1d2e3f4a5b"
_SURVIVOR_EPOCH = 1
_SURVIVOR_SEQ = 2
_VIOLATION_EVENTS = ("CASRefNeedsRecovery", "CASRefRecoveryStreamHole")


def _create(node, name, table_uuid):
    node.command(
        f"CREATE TABLE {name} UUID '{table_uuid}' (id UInt64, payload String) "
        f"ENGINE = MergeTree ORDER BY (id) "
        f"SETTINGS storage_policy='ca', min_bytes_for_wide_part=0, min_rows_for_wide_part=0, "
        f"search_orphaned_parts_disks='local'"
    )


def _wipe_pool(s3, log_fn):
    keys = list_keys(s3, f"{POOL_PREFIX}/")
    for i in range(0, len(keys), 1000):
        s3.delete_objects(Bucket=bucket(), Delete={"Objects": [{"Key": k} for k in keys[i : i + 1000]]})
    log_fn(f"S43: wiped {len(keys)} objects under {POOL_PREFIX}/")
    return len(keys)


def _violation_counters(cluster, events):
    from cas.soak_tests.cards.s38 import _violation_counters as _vc

    return _vc(cluster, events)


@register
class S43(Scenario):
    name = "S43"
    title = "same-uuid pool recreation refuses a residual survivor write"
    priority = "P0"
    param_table = {
        "dev": {"rows": 200, "payload_bytes": 256, "heal_timeout_s": 240},
        "ci": {"rows": 2000, "payload_bytes": 512, "heal_timeout_s": 300},
        "full": {"rows": 20000, "payload_bytes": 1024, "heal_timeout_s": 360},
    }

    def run(self, ctx, result):
        try:
            import zstandard  # noqa: F401
            import boto3  # noqa: F401
        except ImportError as e:
            result.add(Verdict.inconclusive("s43 python deps", "boto3+zstandard", str(e)))
            return
        cl = ctx.cluster
        p = ctx.params
        result.observations["tables"] = [_TABLE]
        rows = int(p["rows"])
        payload = int(p["payload_bytes"])
        heal_timeout_s = int(p["heal_timeout_s"])
        cl.node1.command(f"DROP TABLE IF EXISTS {_TABLE} SYNC")
        _create(cl.node1, _TABLE, _UUID)
        C.insert_random(cl.node1, _TABLE, rows=rows, payload_bytes=payload, op_id=0)
        life1_rows = int(cl.node1.scalar(f"SELECT count() FROM {_TABLE}") or 0)
        life1_checksum = cl.node1.query(C.table_checksum_query(_TABLE)).strip()
        result.add(
            Verdict.check(
                "life 1 has content to be absorbed",
                f"{rows} rows written and readable",
                life1_rows,
                life1_rows == rows,
            )
        )
        s3 = s3_client()
        life_id = discover_single_life_id(s3)
        if life_id is None:
            result.add(
                Verdict.inconclusive(
                    "life 1 has one opaque stream",
                    "exactly one canonical 32-hex child under cas/ns/stream/",
                    "unambiguous life-id child not found",
                )
            )
            C.standard_end(cluster=cl, result=result, tables=[_TABLE])
            return
        log_prefix = f"{POOL_PREFIX}/cas/ns/stream/{life_id}/_log/"
        life1_keys = list_keys(s3, log_prefix)
        if not life1_keys:
            result.add(Verdict.inconclusive("life 1 wrote a ref-log stream", ">0 objects", f"none under {log_prefix}"))
            C.standard_end(cluster=cl, result=result, tables=[_TABLE])
            return
        donor_key = sorted(life1_keys)[-1]
        donor_body = s3.get_object(Bucket=bucket(), Key=donor_key)["Body"].read()
        cl.node1.command(f"DROP TABLE {_TABLE} SYNC")
        forgotten = {}
        for node in cl.nodes():
            try:
                node.command(f"SYSTEM CAS FORGET '{_DISK}'")
                forgotten[repr(node)] = (
                    node.scalar(
                        f"SELECT lifecycle || '(' || lifecycle_reason || ')' FROM system.cas_mounts WHERE disk = '{_DISK}'"
                    )
                    or "(no row)"
                )
            except QueryError as e:
                forgotten[repr(node)] = f"ERROR: {str(e)[:160]}"
        all_vanished = all("vanished" in v for v in forgotten.values())
        result.add(
            Verdict.check(
                "both mounts FORGOT the pool before its prefix was reused",
                "system.cas_mounts reports vanished(...) on every node",
                forgotten,
                all_vanished,
            )
        )
        if not all_vanished:
            C.standard_end(cluster=cl, result=result, tables=[_TABLE])
            return
        _wipe_pool(s3, ctx.log)
        survivor_id = render_ref_txn_id(_SURVIVOR_EPOCH, _SURVIVOR_SEQ)
        survivor_key = f"{log_prefix}{survivor_id}{REF_LOG_SUFFIX}"
        survivor_body = restamp_ref_log_txn(donor_body, _SURVIVOR_SEQ, writer_epoch=_SURVIVOR_EPOCH, keep_ops=True)
        survivor_ops = len(zstd_decompress(survivor_body).decode().splitlines()) - 3
        result.add(
            Verdict.check(
                "the planted survivor carries observable operations",
                ">0 ops",
                survivor_ops,
                survivor_ops > 0,
            )
        )
        s3.put_object(Bucket=bucket(), Key=survivor_key, Body=survivor_body)
        planted = s3.get_object(Bucket=bucket(), Key=survivor_key)["Body"].read()
        result.add(
            Verdict.check(
                "the survivor's write is present in the recreated pool before life 2 starts",
                "GET of the injected id returns the injected body",
                f"{len(planted)} bytes",
                planted == survivor_body,
            )
        )
        apply_fault(Fault(t_offset=0, target=FaultTarget.BOTH, action=FaultAction.RESTART, duration_s=0))
        healthy = wait_cluster_healthy(cl, timeout_s=90, log_fn=ctx.log)
        result.add(
            Verdict.check(
                "the recreated pool REFUSES to bootstrap over the survivor's residual write",
                "servers do not come up over residual data",
                f"healthy={healthy}",
                not healthy,
                "" if not healthy else "servers came up over a prefix holding a foreign ref-log object",
            )
        )
        s3.delete_object(Bucket=bucket(), Key=survivor_key)
        apply_fault(Fault(t_offset=0, target=FaultTarget.BOTH, action=FaultAction.RESTART, duration_s=0))
        healthy_after = wait_cluster_healthy(cl, timeout_s=heal_timeout_s, log_fn=ctx.log)
        result.add(
            Verdict.check(
                "and the refusal is caused by the planted survivor, nothing else",
                "removing that one object lets the same prefix bootstrap",
                f"healthy={healthy_after}",
                healthy_after,
            )
        )
        if not healthy_after:
            C.standard_end(cluster=cl, result=result, tables=[_TABLE])
            return
        before = _violation_counters(cl, _VIOLATION_EVENTS)
        create_error = None
        try:
            _create(cl.node1, _TABLE, _UUID)
        except QueryError as e:
            create_error = str(e)[:400]
        life2_rows = None
        if create_error is None:
            try:
                life2_rows = int(cl.node1.scalar(f"SELECT count() FROM {_TABLE}") or 0)
            except QueryError:
                pass
        after = _violation_counters(cl, _VIOLATION_EVENTS)
        absorbed = life2_rows is not None and life2_rows > 0
        result.add(
            Verdict.check(
                "the recreated table does not absorb the previous life's state",
                "life 2 exposes 0 rows (or refuses outright)",
                f"create_error={create_error} rows={life2_rows}",
                not absorbed,
            )
        )
        moved = {e: after[e] - before[e] for e in _VIOLATION_EVENTS if after[e] > before[e]}
        result.add(
            Verdict.check(
                "no always-zero counter moved across the recreation",
                f"all of {', '.join(_VIOLATION_EVENTS)} unchanged",
                {"moved": moved} if moved else "unchanged",
                not moved,
            )
        )
        C.standard_end(cluster=cl, result=result, tables=[_TABLE])
