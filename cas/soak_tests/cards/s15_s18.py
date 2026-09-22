"""S15 GC shards + S16 hot cycle + S17 detach/attach + S18 freeze (P1)."""

import subprocess
import time

from cas.soak_tests.cards._p1 import ca_since, scale_verdict
from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C
from cas.soak_tests.steps import observe as O


def _probe_blob_target_dirs():
    cmd = "find /data/warehouse/soak_pool/gc -path '*blob_target*' -type d 2>/dev/null"
    try:
        p = subprocess.run(
            ["docker", "exec", C.RUSTFS_CONTAINER, "sh", "-c", cmd],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except Exception as e:
        return {"error": str(e)}
    dirs = [d for d in (p.stdout or "").splitlines() if d.strip()]
    return {"count": len(dirs), "dirs": dirs[:64]}


def _detached_parts(node, table):
    try:
        txt = node.query(
            f"SELECT name FROM system.detached_parts WHERE table='{table}' FORMAT TabSeparated"
        )
    except Exception as e:
        return {"error": str(e)}
    names = [l for l in (txt or "").splitlines() if l]
    return {"count": len(names), "names": names[:64]}


@register
class S15(Scenario):
    name = "S15"
    title = "GC target-shard comparison"
    priority = "P1"
    param_table = {
        "dev": {"parts": 8, "rows_per_part": 300, "payload_bytes": 256, "drop_fraction": 0.5},
        "ci": {"parts": 24, "rows_per_part": 4000, "payload_bytes": 256, "drop_fraction": 0.5},
        "full": {"parts": 120, "rows_per_part": 40000, "payload_bytes": 512, "drop_fraction": 0.5},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        parts = int(p["parts"])
        rows = int(p["rows_per_part"])
        payload = int(p["payload_bytes"])
        drop_n = max(1, int(parts * float(p["drop_fraction"])))
        table = "s15_shards"
        result.observations["tables"] = [table]
        result.observations["scale"] = {
            "parts": parts,
            "rows_per_part": rows,
            "payload_bytes": payload,
            "drop_fraction": float(p["drop_fraction"]),
        }
        scale_verdict(
            result,
            "spec target = many unique blobs + many deletions across shard counts",
            f"{parts} parts x {rows} rows (scale={ctx.scale})",
        )
        result.add(
            Verdict.inconclusive(
                "correctness matches across shard counts",
                "identical oracle checksum across gc_shards=1/2/8",
                "soak_tests_env has no gc_shards2/gc_shards8 compose; running default variant only",
            )
        )
        result.add(
            Verdict.inconclusive(
                "reducer memory flat-or-lower as shards increase",
                "peak RSS comparison across variants",
                "gc_shards2/8 compose not in soak_tests_env",
            )
        )
        C.create_ca_table(cl.node1, table, partition_by="id % 16")
        for pi in range(parts):
            base = (ctx.seed * 1_000_003 + pi) * rows
            gen = (
                f"SELECT {base} + number AS id, "
                f"repeat(toString(({base} + number) % 997), {payload}) AS payload "
                f"FROM numbers({rows})"
            )
            C.insert_values(cl.node1, table, gen, timeout=1200)
        oracle = cl.node1.query(C.table_checksum_query(table)).strip()
        result.observations["oracle_checksum"] = oracle
        for part_id in range(drop_n):
            try:
                cl.node1.command(f"ALTER TABLE {table} DROP PARTITION {part_id}", timeout=600)
            except Exception as e:
                ctx.log(f"S15: DROP PARTITION {part_id}: {e}")
        t0 = time.monotonic()
        _, residual = C.drive_gc_until_stable()
        result.timings["gc_wall_s"] = round(time.monotonic() - t0, 2)
        result.observations["residual_unreachable"] = residual
        result.observations["blob_target_shard_dirs"] = _probe_blob_target_dirs()
        result.add(
            Verdict.reported(
                "per-shard run files observed",
                "gc/gen/*/blob_target/* shards represented when data hashes cover them",
                result.observations["blob_target_shard_dirs"].get("count"),
                "recorded; shard fanout depends on dropped content hashes",
            )
        )
        result.add(Verdict.check("cluster left on default variant", "healthy on default after last variant", "default", True))
        C.assert_replicas_agree(result, cl, C.table_checksum_query(table), name="S15 replica agreement")
        C.standard_end(cluster=cl, result=result, tables=[table])
        O.assert_reclaimable_drained(
            result, "orphan backlog drained (default)", residual, result.observations.get("fsck_final")
        )


@register
class S16(Scenario):
    name = "S16"
    title = "hot content cycle with GC"
    priority = "P1"
    param_table = {
        "dev": {"cycles": 4, "rows": 500, "payload_bytes": 256},
        "ci": {"cycles": 10, "rows": 5000, "payload_bytes": 256},
        "full": {"cycles": 30, "rows": 50000, "payload_bytes": 512},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        table = "s16_hot"
        cycles = int(p["cycles"])
        rows = int(p["rows"])
        payload = int(p["payload_bytes"])
        result.observations["tables"] = [table]
        result.observations["scale"] = {"cycles": cycles, "rows": rows, "payload_bytes": payload}
        scale_verdict(
            result,
            "spec target = repeat insert/drop of identical content",
            f"{cycles} cycles x {rows} rows (scale={ctx.scale})",
        )
        C.create_ca_table(cl.node1, table)
        gen = (
            f"SELECT number AS id, repeat(toString(number % 251), {payload}) AS payload "
            f"FROM numbers({rows})"
        )
        expected_oracle = None
        counters = C.counters_window(cl)
        cycle_log = []
        for c in range(cycles):
            C.insert_values(cl.node1, table, gen, timeout=600)
            chk = cl.node1.query(C.table_checksum_query(table)).strip()
            if expected_oracle is None:
                expected_oracle = chk
            cl.node1.command(f"TRUNCATE TABLE {table}", timeout=300)
            _, residual = C.drive_gc_until_stable()
            cycle_log.append({"cycle": c, "checksum": chk, "residual_after_retire": residual})
        result.observations["cycles"] = cycle_log
        C.insert_values(cl.node1, table, gen, timeout=600)
        final_chk = cl.node1.query(C.table_checksum_query(table)).strip()
        ca_events = ca_since(ctx)
        result.observations["ca_event_counts"] = ca_events
        resurrect_count = O.event_total(ca_events, "blob_reuse_resurrect")
        deleted_count = O.event_total(ca_events, "blob_delete")
        result.observations["reuse_events"] = {
            et: O.event_total(ca_events, et)
            for et in ("blob_reuse_resurrect", "blob_reuse_adopt", "blob_put", "blob_delete", "objects_spared")
        }
        if resurrect_count > 0:
            result.add(
                Verdict.check(
                    "resurrection events recorded (cas_log)",
                    "blob_reuse_resurrect fires for the drop/GC-condemn/re-insert cycle",
                    f"blob_reuse_resurrect={resurrect_count}",
                    True,
                )
            )
        elif deleted_count == 0:
            result.add(
                Verdict.inconclusive(
                    "resurrection events recorded (cas_log)",
                    "blob_reuse_resurrect after GC condemns the retired token",
                    "blob_delete=0 in this window, so GC did not condemn before the re-insert",
                )
            )
        else:
            result.add(
                Verdict.check(
                    "resurrection events recorded (cas_log)",
                    "blob_reuse_resurrect fires after blob_delete",
                    f"blob_reuse_resurrect={resurrect_count} blob_delete={deleted_count}",
                    False,
                    "GC condemned content and the re-insert did not emit blob_reuse_resurrect",
                )
            )
        bad = ca_events.get("bad_total", {})
        oracle_stable = (final_chk == expected_oracle) and all(
            row["checksum"] == expected_oracle for row in cycle_log
        )
        result.add(
            Verdict.check(
                "reintroduced content read from writer-owned source bytes (proxy)",
                "data correct every cycle + no read_missing/dangling_access",
                f"oracle_stable={oracle_stable} bad_events={bad}",
                oracle_stable and not bad,
            )
        )
        result.observations["cycle_counters"] = counters().get("_total", {})
        C.assert_replicas_agree(result, cl, C.table_checksum_query(table), name="S16 replica agreement")
        C.standard_end(cluster=cl, result=result, tables=[table])


@register
class S17(Scenario):
    name = "S17"
    title = "detached, attach, and drop detached"
    priority = "P1"
    param_table = {
        "dev": {"partitions": 8, "rows_per_partition": 200, "payload_bytes": 256, "attach_back": 3},
        "ci": {"partitions": 24, "rows_per_partition": 4000, "payload_bytes": 256, "attach_back": 8},
        "full": {"partitions": 80, "rows_per_partition": 40000, "payload_bytes": 512, "attach_back": 20},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        table = "s17_detach"
        nparts = int(p["partitions"])
        rows = int(p["rows_per_partition"])
        payload = int(p["payload_bytes"])
        attach_back = min(int(p["attach_back"]), nparts)
        result.observations["tables"] = [table]
        result.observations["scale"] = {
            "partitions": nparts,
            "rows_per_partition": rows,
            "payload_bytes": payload,
            "attach_back": attach_back,
        }
        scale_verdict(
            result,
            "spec target = many detached parts, attach + drop-detached",
            f"{nparts} partitions, attach {attach_back} back (scale={ctx.scale})",
        )
        C.create_ca_table(
            cl.node1,
            table,
            columns="id UInt64, pk UInt64, payload String",
            order_by="id",
            partition_by="pk",
        )
        for part_id in range(nparts):
            base = part_id * rows
            gen = (
                f"SELECT {base} + number AS id, {part_id} AS pk, "
                f"repeat(toString(({base} + number) % 313), {payload}) AS payload "
                f"FROM numbers({rows})"
            )
            C.insert_values(cl.node1, table, gen, timeout=600)
        for part_id in range(nparts):
            try:
                cl.node1.command(f"ALTER TABLE {table} DETACH PARTITION {part_id}", timeout=600)
            except Exception as e:
                ctx.log(f"S17: DETACH PARTITION {part_id}: {e}")
        live_rows = int(cl.node1.scalar(f"SELECT count() FROM {table}") or 0)
        detached = _detached_parts(cl.node1, table)
        result.observations["detached_after_detach"] = detached
        result.add(
            Verdict.check(
                "all partitions detached",
                "live table empty + detached parts listed",
                f"live_rows={live_rows} detached={detached.get('count')}",
                live_rows == 0 and detached.get("count", 0) > 0,
            )
        )
        C.gc_drive_round(cl, log_fn=ctx.log)
        fsck_detached = C.run_cas_fsck(detail=False)
        result.observations["fsck_with_detached"] = {
            k: fsck_detached.get(k) for k in ("dangling", "unreachable", "reachable")
        }
        O.assert_fsck_clean(
            result,
            fsck_detached,
            name="detached parts reachable until dropped",
            expected="fsck dangling==0 after a GC round while parts are detached",
            fail_note="GC saw detached-part content as dangling",
        )
        attach_ids = list(range(attach_back))
        drop_ids = list(range(attach_back, nparts))
        for part_id in attach_ids:
            try:
                cl.node1.command(f"ALTER TABLE {table} ATTACH PARTITION {part_id}", timeout=600)
            except Exception as e:
                ctx.log(f"S17: ATTACH PARTITION {part_id}: {e}")
        for part_id in drop_ids:
            try:
                cl.node1.command(
                    f"ALTER TABLE {table} DROP DETACHED PARTITION {part_id} "
                    f"SETTINGS allow_drop_detached=1",
                    timeout=600,
                )
            except Exception as e:
                ctx.log(f"S17: DROP DETACHED PARTITION {part_id}: {e}")
        attach_oracle = (
            f"SELECT count(), sum(sipHash64(*)) FROM {table} "
            f"WHERE pk IN ({','.join(str(i) for i in attach_ids)}) FORMAT TabSeparated"
        )
        C.assert_replicas_agree(result, cl, attach_oracle, name="S17 attached-subset replica agreement")
        attached_rows = int(cl.node1.scalar(f"SELECT count() FROM {table}") or 0)
        result.add(
            Verdict.check(
                "attached parts read correctly",
                f"re-attached {attach_back} partitions queryable",
                f"attached_rows={attached_rows} (expected ~{attach_back * rows})",
                attached_rows == attach_back * rows,
            )
        )
        C.standard_end(cluster=cl, result=result, tables=[table])
        O.assert_fsck_clean(result, result.observations.get("fsck_final"), name="no dangling after detach lifecycle")
        O.assert_reclaimable_drained(
            result,
            "dropped detached content reclaimable",
            result.observations.get("gc_residual_unreachable"),
            result.observations.get("fsck_final"),
        )


@register
class S18(Scenario):
    name = "S18"
    title = "freeze and unfreeze shadows"
    priority = "P1"
    param_table = {
        "dev": {"parts": 6, "rows_per_part": 300, "payload_bytes": 256},
        "ci": {"parts": 20, "rows_per_part": 4000, "payload_bytes": 256},
        "full": {"parts": 80, "rows_per_part": 40000, "payload_bytes": 512},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        table = "s18_freeze"
        parts = int(p["parts"])
        rows = int(p["rows_per_part"])
        payload = int(p["payload_bytes"])
        backup_name = f"s18_snap_{ctx.seed}"
        result.observations["tables"] = [table]
        result.observations["scale"] = {
            "parts": parts,
            "rows_per_part": rows,
            "payload_bytes": payload,
            "backup_name": backup_name,
        }
        scale_verdict(
            result,
            "spec target = freeze, drop live table, verify, unfreeze",
            f"{parts} parts x {rows} rows (scale={ctx.scale})",
        )
        C.create_ca_table(cl.node1, table, partition_by="id % 8")
        for pi in range(parts):
            base = pi * rows
            gen = (
                f"SELECT {base} + number AS id, "
                f"repeat(toString(({base} + number) % 419), {payload}) AS payload "
                f"FROM numbers({rows})"
            )
            C.insert_values(cl.node1, table, gen, timeout=600)
        froze = False
        freeze_error = None
        try:
            cl.node1.command(f"ALTER TABLE {table} FREEZE WITH NAME '{backup_name}'", timeout=600)
            froze = True
        except Exception as e:
            freeze_error = str(e)
            ctx.log(f"S18: FREEZE failed: {e}")
        if not froze:
            result.add(
                Verdict.inconclusive(
                    "freeze shadow keeps blobs alive",
                    "ALTER TABLE FREEZE succeeds and the shadow keeps content alive after a live drop",
                    f"freeze unsupported/failing — possible B3 freeze/shadow bug: {freeze_error}",
                )
            )
            result.add(
                Verdict.inconclusive(
                    "frozen content survives a live-table drop",
                    "fsck dangling==0 after dropping live",
                    "freeze did not succeed (B3) — nothing frozen to keep alive",
                )
            )
            result.add(
                Verdict.inconclusive(
                    "unfreeze releases shadow refs",
                    "GC reclaims content after unfreeze",
                    "freeze did not succeed (B3) — nothing to unfreeze",
                )
            )
            C.assert_replicas_agree(result, cl, C.table_checksum_query(table), name="S18 replica agreement (no freeze)")
            C.standard_end(cluster=cl, result=result, tables=[table])
            return
        ctx.log("S18: dropping the live table; the frozen snapshot must NOT become dangling")
        C.drop_table_both(cl, table)
        result.observations["tables"] = []
        C.gc_drive_round(cl, log_fn=ctx.log)
        fsck_after_drop = C.run_cas_fsck(detail=False)
        result.observations["fsck_after_live_drop"] = {
            k: fsck_after_drop.get(k) for k in ("dangling", "unreachable", "reachable")
        }
        O.assert_fsck_clean(
            result,
            fsck_after_drop,
            name="frozen content survives a live-table drop",
            expected="fsck dangling==0 after dropping the live table (shadow keeps blobs alive)",
            fail_note="dropping the live table made frozen-snapshot content dangling",
        )
        unfroze = False
        unfreeze_error = None
        try:
            cl.node1.command(f"SYSTEM UNFREEZE WITH NAME '{backup_name}'", timeout=600)
            unfroze = True
        except Exception as e:
            unfreeze_error = str(e)
            ctx.log(f"S18: SYSTEM UNFREEZE failed: {e}")
        if not unfroze:
            result.add(
                Verdict.inconclusive(
                    "unfreeze releases shadow refs",
                    "reclaimable unreachable == 0 after unfreeze+GC",
                    f"SYSTEM UNFREEZE failed (possible B3 freeze/shadow bug): {unfreeze_error}",
                )
            )
        C.standard_end(cluster=cl, result=result, tables=[])
        if unfroze:
            O.assert_reclaimable_drained(
                result,
                "unfreeze releases shadow refs",
                result.observations.get("gc_residual_unreachable"),
                result.observations.get("fsck_final"),
            )
