"""S32 TTL expiry reclaim (P2)."""

from cas.soak_tests.cards._p1 import scale_verdict
from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C
from cas.soak_tests.steps import observe as O


@register
class S32(Scenario):
    name = "S32"
    title = "TTL expiry reclaim"
    priority = "P2"
    param_table = {
        "dev": {"expired_rows": 2000, "future_rows": 2000, "payload_bytes": 512, "ttl_seconds": 1},
        "ci": {"expired_rows": 20000, "future_rows": 20000, "payload_bytes": 512, "ttl_seconds": 1},
        "full": {
            "expired_rows": 200000,
            "future_rows": 200000,
            "payload_bytes": 512,
            "ttl_seconds": 1,
        },
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        table = "s32_ttl"
        expired = int(p["expired_rows"])
        future = int(p["future_rows"])
        payload = int(p["payload_bytes"])
        ttl_s = int(p["ttl_seconds"])
        result.observations["tables"] = [table]
        result.observations["scale"] = {
            "expired_rows": expired,
            "future_rows": future,
            "payload_bytes": payload,
            "ttl_seconds": ttl_s,
        }
        scale_verdict(
            result,
            "core path = TTL DELETE expiry reclaims content",
            f"{expired} expired + {future} future rows (scale={ctx.scale})",
        )
        C.create_ca_table(
            cl.node1,
            table,
            columns="id UInt64, ts DateTime, payload String",
            order_by="id",
            ttl=f"toDateTime(ts) + INTERVAL {ttl_s} SECOND DELETE",
        )
        C.insert_values(
            cl.node1,
            table,
            f"SELECT number AS id, now() - INTERVAL 1 DAY AS ts, "
            f"randomString({payload}) AS payload FROM numbers({expired})",
            timeout=1200,
        )
        C.insert_values(
            cl.node1,
            table,
            f"SELECT {expired} + number AS id, now() + INTERVAL 365 DAY AS ts, "
            f"randomString({payload}) AS payload FROM numbers({future})",
            timeout=1200,
        )
        total_before = int(cl.node1.scalar(f"SELECT count() FROM {table}") or 0)
        result.observations["rows_before_ttl"] = total_before
        try:
            cl.node1.command(f"ALTER TABLE {table} MATERIALIZE TTL", timeout=1200)
        except Exception as e:
            ctx.log(f"S32: MATERIALIZE TTL: {e}")
        try:
            cl.node1.command(f"OPTIMIZE TABLE {table} FINAL", timeout=1200)
        except Exception as e:
            ctx.log(f"S32: OPTIMIZE FINAL: {e}")
        for n in cl.nodes():
            try:
                n.command(f"SYSTEM SYNC REPLICA {table}", timeout=600)
            except Exception as e:
                ctx.log(f"S32: SYNC REPLICA: {e}")
        rows_after = int(cl.node1.scalar(f"SELECT count() FROM {table}") or 0)
        expired_remaining = int(
            cl.node1.scalar(f"SELECT count() FROM {table} WHERE ts < now()") or 0
        )
        result.observations["rows_after_ttl"] = rows_after
        result.observations["expired_remaining"] = expired_remaining
        result.add(
            Verdict.check(
                "expired rows removed by TTL",
                f"only the {future} future rows remain",
                f"rows_after={rows_after} (expected {future}), expired_remaining={expired_remaining}",
                rows_after == future and expired_remaining == 0,
                ""
                if (rows_after == future and expired_remaining == 0)
                else "TTL DELETE did not remove exactly the expired rows",
            )
        )
        C.assert_replicas_agree(
            result,
            cl,
            f"SELECT count() FROM {table} FORMAT TabSeparated",
            name="S32 row-count replica agreement",
        )
        C.assert_replicas_agree(
            result, cl, C.table_checksum_query(table), name="S32 checksum replica agreement"
        )
        end = C.standard_end(cluster=cl, result=result, tables=[table])
        O.assert_fsck_clean(
            result, end, name="no dangling after TTL reclaim", fail_note="dangling refs after TTL"
        )
        O.assert_reclaimable_drained(
            result,
            "expired content reclaimed by GC",
            result.observations.get("gc_residual_unreachable"),
            end,
        )
