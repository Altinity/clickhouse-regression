"""S02 huge duplicate blob (P0).

Second insert of identical large content into a different table must avoid the remote body PUT.
Payload is seeded generateRandom (incompressible). repeat() compresses away; randomString is not
byte-identical across inserts.
"""

from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C

MIB = 1024 * 1024
GIB = 1024 * 1024 * 1024
GEN_SEED = 20260703
STRING_CAP = 1_000_000


def insert_plan(params):
    """Row count, generator SQL, and insert settings for a scale's blob/payload sizes."""
    per_row = min(int(params["payload_mib"]) * MIB, STRING_CAP)
    rows = max(1, (int(params["blob_mib"]) * MIB) // per_row)
    seed = int(params.get("gen_seed", GEN_SEED))
    block_rows = max(1, (512 * MIB) // per_row)
    gen = (
        f"SELECT rowNumberInAllBlocks() AS id, payload "
        f"FROM generateRandom('payload String', {seed}, {per_row}) "
        f"LIMIT {rows}"
    )
    return {
        "per_row": per_row,
        "rows": rows,
        "actual_bytes": rows * per_row,
        "seed": seed,
        "gen": gen,
        "settings": {
            "max_block_size": block_rows,
            "min_insert_block_size_rows": block_rows,
            "max_threads": 1,
        },
    }


@register
class S02(Scenario):
    name = "S02"
    title = "huge duplicate blob"
    priority = "P0"
    param_table = {
        "dev": {"blob_mib": 64, "payload_mib": 1},
        "ci": {"blob_mib": 512, "payload_mib": 2},
        "full": {"blob_mib": 102400, "payload_mib": 8},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        plan = insert_plan(ctx.params)
        actual_bytes = plan["actual_bytes"]
        t1, t2 = "s02_first", "s02_second"
        result.observations["tables"] = [t1, t2]
        result.observations["target_blob_bytes"] = actual_bytes

        C.create_ca_table(cl.node1, t1)
        C.create_ca_table(cl.node1, t2)

        ctx.log(f"S02: first insert ~{actual_bytes / GIB:.3f} GiB")
        C.insert_values(
            cl.node1, t1, plan["gen"], timeout=2400, settings=plan["settings"]
        )
        bytes_after_first = C.pool_shape(timeout_s=90)
        result.observations["pool_after_first"] = bytes_after_first.get("_total")

        counters = C.counters_window(cl)
        ctx.log("S02: second identical insert (expect remote body PUT avoided)")
        C.insert_values(
            cl.node1, t2, plan["gen"], timeout=2400, settings=plan["settings"]
        )
        delta = counters().get("_total", {})
        result.observations["second_insert_counters"] = delta
        bytes_after_second = C.pool_shape(timeout_s=90)
        result.observations["pool_after_second"] = bytes_after_second.get("_total")

        avoided = delta.get("CASBlobBodyPutAvoided", 0)
        dedup_hits = delta.get("CASBlobPutDeduplicated", 0) + delta.get(
            "CASBlobDeduplicationCacheHit", 0
        )
        body_puts = delta.get("CASBlobPut", 0)
        result.add(
            Verdict.check(
                "dedup avoided body upload",
                "CASBlobBodyPutAvoided>0 or CASBlobPutDeduplicated>0",
                f"avoided={avoided} dedup={dedup_hits} put={body_puts}",
                avoided > 0 or dedup_hits > 0,
            )
        )

        if bytes_after_first.get("_ok") and bytes_after_second.get("_ok"):
            grew = (
                bytes_after_second["_total"]["bytes"]
                - bytes_after_first["_total"]["bytes"]
            )
            result.observations["pool_byte_growth_second_insert"] = grew
            ok = grew < actual_bytes // 2
            result.add(
                Verdict.check(
                    "pool grew by metadata only",
                    f"< {actual_bytes // 2 / GIB:.3f} GiB (half a blob)",
                    f"{grew / MIB:.1f} MiB",
                    ok,
                )
            )

        C.assert_replicas_agree(result, cl, C.table_checksum_query(t1))
        C.assert_replicas_agree(result, cl, C.table_checksum_query(t2))
        C.standard_end(cluster=cl, result=result, tables=[t1, t2])
