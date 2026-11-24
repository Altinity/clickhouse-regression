"""S46: a local part larger than the 90s CAS write budget must still move onto CAS.

Uploads of about 6 GiB and larger finish after that budget is already spent.
The publication then fails in PartWriteTxn::ensureBlobPresent while marking the
blob Clean, with zero attempts left, and the move or merge is retried from
scratch. dev and ci stay under that size. full is 8 GiB, past the line.
"""

import time

from cas.soak_tests.cards._p1 import scale_verdict
from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C

MIB = 1024 * 1024
# Customer uploads at or above about 6 GiB miss the 90s write policy.
SLOW_PART_MIB = 6 * 1024
_ROW_BYTES = MIB


def _parts_by_disk(node, table):
    txt = node.query(
        "SELECT name, disk_name FROM system.parts "
        f"WHERE table = '{table}' AND active FORMAT TabSeparated"
    )
    out = {}
    for line in (txt or "").splitlines():
        if not line.strip():
            continue
        name, disk = line.split("\t")
        out[name] = disk
    return out


def _active_bytes(node, table):
    txt = node.query(
        "SELECT sum(bytes_on_disk), count() FROM system.parts "
        f"WHERE table = '{table}' AND active FORMAT TabSeparated"
    ).strip()
    if not txt:
        return 0, 0
    nbytes, nparts = txt.split("\t")
    return int(nbytes or 0), int(nparts or 0)


@register
class S46(Scenario):
    name = "S46"
    title = "volume move of a part that outlasts the 90s CAS write budget"
    priority = "P1"
    compose_variant = "multidisk"
    param_table = {
        "dev": {"part_mib": 8, "move_timeout_s": 300},
        "ci": {"part_mib": 64, "move_timeout_s": 900},
        # 8 GiB is past the ~6 GiB line where customer uploads stop committing.
        "full": {"part_mib": 8192, "move_timeout_s": 3600},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        part_mib = int(p["part_mib"])
        move_timeout_s = int(p["move_timeout_s"])
        rows = max(1, (part_mib * MIB) // _ROW_BYTES)
        table = "s46_slow_move"
        result.observations["tables"] = [table]
        crosses = part_mib >= SLOW_PART_MIB
        scale_verdict(
            result,
            "a local part moved onto CAS after publication longer than 90s",
            f"{part_mib} MiB ({'past' if crosses else 'under'} the {SLOW_PART_MIB} MiB line)",
            "dev and ci finish the move well inside 90s; only --scenario-scale full "
            "uploads a body the customer's cluster cannot commit",
        )

        C.create_ca_table(
            cl.node1,
            table,
            columns="id UInt64, payload String",
            order_by="id",
            extra_settings={"storage_policy": "'local_then_ca'"},
        )
        C.insert_random(
            cl.node1,
            table,
            rows=rows,
            payload_bytes=_ROW_BYTES,
            timeout=move_timeout_s,
            settings={
                "max_block_size": str(rows),
                "max_insert_block_size_rows": str(rows),
                "min_insert_block_size_rows": str(rows),
            },
        )
        cl.node1.command(f"SYSTEM SYNC REPLICA {table}", timeout=move_timeout_s)

        nbytes, nparts = _active_bytes(cl.node1, table)
        before = _parts_by_disk(cl.node1, table)
        result.observations["before_move"] = {
            "bytes_on_disk": nbytes,
            "parts": nparts,
            "disks": before,
        }
        one_local_part = (
            nparts == 1
            and nbytes >= (part_mib * MIB * 8) // 10
            and set(before.values()) == {"local1"}
        )
        result.add(Verdict.check(
            "one source part sits on the local disk",
            "1 active part on local1, at least the requested size",
            {"bytes_on_disk": nbytes, "parts": nparts, "disks": before},
            one_local_part,
            "" if one_local_part else
            "the insert split or landed on ca, so the move would not publish one slow body",
        ))
        if not one_local_part:
            C.standard_end(cluster=cl, result=result, tables=[table])
            return

        checksum_before = cl.node1.query(C.table_checksum_query(table)).strip()
        move_error = None
        t0 = time.monotonic()
        try:
            cl.node1.command(
                f"ALTER TABLE {table} MOVE PARTITION ID 'all' TO VOLUME 'cas'",
                timeout=move_timeout_s,
            )
        except Exception as e:
            move_error = str(e)[:500]
        result.timings["move_s"] = round(time.monotonic() - t0, 1)
        cl.node1.command(f"SYSTEM SYNC REPLICA {table}", timeout=move_timeout_s)

        after = _parts_by_disk(cl.node1, table)
        result.observations["after_move"] = after
        on_ca = bool(after) and set(after.values()) == {"ca"}
        deadline_hit = bool(move_error) and (
            "policy deadline" in move_error or "ensureBlobPresent" in move_error
        )
        result.add(Verdict.check(
            "MOVE TO VOLUME 'cas' commits",
            "the statement returns and every active part is on disk ca",
            move_error or after,
            move_error is None and on_ca,
            "the 90s write policy expired while the body was published"
            if deadline_hit else (move_error or ""),
        ))

        checksum_after = cl.node1.query(C.table_checksum_query(table)).strip()
        result.add(Verdict.check(
            "moved part keeps its rows",
            checksum_before,
            checksum_after,
            checksum_after == checksum_before,
        ))
        C.assert_replicas_agree(
            result, cl, C.table_checksum_query(table), name="S46 replica agreement"
        )
        C.standard_end(cluster=cl, result=result, tables=[table])
