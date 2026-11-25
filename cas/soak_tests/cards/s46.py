"""S46: a local part larger than the 90s CAS write budget must still move onto CAS.

Uploads of about 6 GiB and larger finish after that budget is already spent.
The publication then fails in PartWriteTxn::ensureBlobPresent while marking the
blob Clean, with zero attempts left, and the move or merge is retried from
scratch. dev and ci stay under that size. full is 8 GiB, past the line.
"""

import subprocess
import time

from cas.soak_tests.cards._p1 import scale_verdict
from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C

MIB = 1024 * 1024
# Customer uploads at or above about 6 GiB miss the 90s write policy.
SLOW_PART_MIB = 6 * 1024
_ROW_BYTES = MIB
# Blocks small enough that randomString does not stall the mount renewer.
_INSERT_ROWS = 256
# 80 Mbit/s with a small burst. An 8 GiB body takes about 14 min, past the
# 90s write policy. A lease PUT is a few hundred bytes and still fits in the
# burst, so the mount can stay live the way the customer's does.
_SLOW_RATE = "80mbit"


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


def _largest_part(node, table):
    txt = node.query(
        "SELECT name, disk_name, bytes_on_disk FROM system.parts "
        f"WHERE table = '{table}' AND active "
        "ORDER BY bytes_on_disk DESC LIMIT 1 FORMAT TabSeparated"
    ).strip()
    if not txt:
        return None, None, 0
    name, disk, nbytes = txt.split("\t")
    return name, disk, int(nbytes)


def _limit_bulk_upload(enabled):
    """Rate-limit each replica's egress, leaving a burst for the lease PUT."""
    action = "add" if enabled else "del"
    for container in ("soak_tests_env-clickhouse1-1", "soak_tests_env-clickhouse2-1"):
        cmd = ["docker", "exec", container, "tc", "qdisc", action, "dev", "eth0", "root"]
        if enabled:
            cmd += ["tbf", "rate", _SLOW_RATE, "burst", "256kb", "latency", "50ms"]
        subprocess.run(cmd, capture_output=True, timeout=30)


def _wait_ca_writable(node, probe, timeout_s):
    """Insert one row onto the CAS disk until the mount is Live.

    A large local insert can fence the renewer. The customer's publication
    runs against a live mount, so the move waits for that before it starts.
    """
    deadline = time.monotonic() + timeout_s
    last = "mount probe did not run"
    while time.monotonic() < deadline:
        try:
            C.insert_random(
                node, probe, rows=1, payload_bytes=8, op_id=int(time.time()) % 1_000_000, timeout=60
            )
            return None
        except Exception as e:
            last = str(e)[:300]
            time.sleep(5)
    return last


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
        probe = "s46_mount_probe"
        result.observations["tables"] = [table, probe]
        C.create_ca_table(cl.node1, probe, columns="id UInt64, payload String", order_by="id")
        inserted = 0
        while inserted < rows:
            batch = min(_INSERT_ROWS, rows - inserted)
            C.insert_random(
                cl.node1,
                table,
                rows=batch,
                payload_bytes=_ROW_BYTES,
                op_id=inserted,
                timeout=move_timeout_s,
                settings={
                    "max_block_size": str(batch),
                    "max_insert_block_size_rows": str(batch),
                    "min_insert_block_size_rows": str(batch),
                },
            )
            inserted += batch
        # Fold on local1. The CAS publication is the later MOVE of this one part.
        cl.node1.command(f"OPTIMIZE TABLE {table} FINAL", timeout=move_timeout_s)
        cl.node1.command(f"SYSTEM SYNC REPLICA {table}", timeout=move_timeout_s)

        name, disk, nbytes = _largest_part(cl.node1, table)
        before = _parts_by_disk(cl.node1, table)
        result.observations["before_move"] = {
            "largest": {"name": name, "disk": disk, "bytes_on_disk": nbytes},
            "disks": before,
        }
        big_enough = nbytes >= (part_mib * MIB * 8) // 10
        on_local = disk == "local1" and big_enough
        result.add(Verdict.check(
            "a large source part sits on the local disk",
            "largest active part on local1, at least the requested size",
            {"name": name, "disk": disk, "bytes_on_disk": nbytes, "parts": before},
            on_local,
            "" if on_local else
            "no single local part is large enough for one slow publication",
        ))
        if not on_local:
            C.standard_end(cluster=cl, result=result, tables=[table, probe])
            return

        checksum_before = cl.node1.query(C.table_checksum_query(table)).strip()
        mount_error = _wait_ca_writable(cl.node1, probe, timeout_s=min(move_timeout_s, 300))
        move_error = mount_error
        t0 = time.monotonic()
        if mount_error is None and crosses:
            _limit_bulk_upload(True)
        if mount_error is None:
            try:
                cl.node1.command(
                    f"ALTER TABLE {table} MOVE PART '{name}' TO VOLUME 'cas'",
                    timeout=move_timeout_s,
                )
            except Exception as e:
                move_error = str(e)[:500]
            finally:
                if crosses:
                    _limit_bulk_upload(False)
        result.timings["move_s"] = round(time.monotonic() - t0, 1)
        cl.node1.command(f"SYSTEM SYNC REPLICA {table}", timeout=move_timeout_s)

        after = _parts_by_disk(cl.node1, table)
        result.observations["after_move"] = after
        moved = [part for part, part_disk in after.items() if part_disk == "ca"]
        deadline_hit = bool(move_error) and (
            "ensureBlobPresent" in move_error or "zero attempt" in move_error
        )
        result.add(Verdict.check(
            "MOVE PART TO VOLUME 'cas' commits",
            "the statement returns and the part is on disk ca",
            move_error or after,
            move_error is None and bool(moved),
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
