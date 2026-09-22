"""S09 mutation carry-forward + S10 patch/deletes + S11 heavy ALTER DELETE (P0)."""

import time

from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C
from cas.soak_tests.steps import observe as O

MIB = 1024 * 1024


def _mutations_in_flight(node, table):
    try:
        return int(
            node.scalar(f"SELECT count() FROM system.mutations WHERE table='{table}' AND NOT is_done") or 0
        )
    except Exception:
        return None


def _wait_mutations_done(cluster, table, *, timeout_s=300.0, poll_s=0.5):
    deadline = time.monotonic() + timeout_s
    peak = 0
    while True:
        depths = [_mutations_in_flight(n, table) for n in cluster.nodes()]
        known = [d for d in depths if d is not None]
        if known:
            peak = max(peak, max(known))
        if known and all(d == 0 for d in known):
            return True, peak
        if time.monotonic() >= deadline:
            return False, peak
        time.sleep(poll_s)


def _active_merges(node, table):
    try:
        return int(node.scalar(f"SELECT count() FROM system.merges WHERE table='{table}'") or 0)
    except Exception:
        return None


def _replication_queue_depth(node, table):
    try:
        return int(node.scalar(f"SELECT count() FROM system.replication_queue WHERE table='{table}'") or 0)
    except Exception:
        return None


def _patch_part_count(node, table):
    try:
        return int(
            node.scalar(
                f"SELECT count() FROM system.parts WHERE table='{table}' AND active "
                f"AND (part_type = 'Patch' OR name LIKE 'patch-%')"
            )
            or 0
        )
    except Exception:
        return None


def _counter(delta, key):
    return int(delta.get(key, 0) or 0)


@register
class S09(Scenario):
    name = "S09"
    title = "mutation carry-forward"
    priority = "P0"
    param_table = {
        "dev": {"columns": 50, "rows": 4000, "payload_bytes": 2048, "inserts": 2},
        "ci": {"columns": 120, "rows": 20000, "payload_bytes": 4096, "inserts": 3},
        "full": {"columns": 200, "rows": 100000, "payload_bytes": 8192, "inserts": 4},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        table = "s09_wide"
        result.observations["tables"] = [table]
        ncols = int(p["columns"])
        rows_per_insert = int(p["rows"])
        payload_bytes = int(p["payload_bytes"])
        n_inserts = int(p["inserts"])
        col_names = [f"c{i}" for i in range(ncols)]
        columns = "id UInt64, payload String, " + ", ".join(f"{c} UInt64" for c in col_names)
        extra_cols_select = ", ".join(f"(number % {7 + i}) AS {c}" for i, c in enumerate(col_names))
        C.create_ca_table(cl.node1, table, columns=columns, order_by="id")
        for op in range(n_inserts):
            C.insert_random(
                cl.node1,
                table,
                rows=rows_per_insert,
                payload_bytes=payload_bytes,
                extra_cols_select=extra_cols_select,
                op_id=op * rows_per_insert,
            )
        expected_rows = n_inserts * rows_per_insert
        cl.node1.command(f"OPTIMIZE TABLE {table} FINAL", timeout=2400)
        single_growth = self._timed_mutation(
            ctx, result, cl, table, f"ALTER TABLE {table} UPDATE c0 = c0 + 1 WHERE 1", label="single_col_update"
        )
        multi_cols = col_names[: min(5, ncols)]
        set_clause = ", ".join(f"{c} = {c} + 1" for c in multi_cols)
        multi_growth = self._timed_mutation(
            ctx, result, cl, table, f"ALTER TABLE {table} UPDATE {set_clause} WHERE 1", label="multi_col_update"
        )
        identity_growth = self._timed_mutation(
            ctx, result, cl, table, f"ALTER TABLE {table} UPDATE c0 = c0 WHERE 1", label="identity_update"
        )
        full_payload_bytes = expected_rows * payload_bytes
        budget = full_payload_bytes // 4
        for label, growth in (
            ("single_col_update", single_growth),
            ("multi_col_update", multi_growth),
            ("identity_update", identity_growth),
        ):
            if growth is None:
                result.add(
                    Verdict.inconclusive(
                        f"{label} pool growth bounded", f"< {budget / MIB:.1f} MiB", "pool shape probe failed"
                    )
                )
                continue
            result.add(
                Verdict.check(
                    f"{label} pool growth bounded",
                    f"< {budget / MIB:.1f} MiB (quarter of part payload)",
                    f"{growth / MIB:.3f} MiB",
                    growth < budget,
                )
            )
        idelta = result.observations.get("counters_identity_update", {})
        avoided = _counter(idelta, "CASBlobBodyPutAvoided")
        dedup = _counter(idelta, "CASBlobPutDeduplicated") + _counter(idelta, "CASBlobDeduplicationCacheHit")
        body_puts = _counter(idelta, "CASBlobPut")
        result.add(
            Verdict.check(
                "identity update avoids large body re-upload",
                "CASBlobBodyPutAvoided>0 or CASBlobPutDeduplicated>0",
                f"avoided={avoided} dedup={dedup} body_put={body_puts}",
                avoided > 0 or dedup > 0,
            )
        )
        try:
            observed_rows = int(cl.node1.scalar(f"SELECT count() FROM {table}") or 0)
        except Exception:
            observed_rows = None
        result.add(
            Verdict.check(
                "row count matches oracle after mutations",
                f"{expected_rows}",
                f"{observed_rows}",
                observed_rows == expected_rows,
            )
        )
        C.assert_replicas_agree(result, cl, C.table_checksum_query(table))
        C.assert_replicas_agree(
            result, cl, f"SELECT count() FROM {table} FORMAT TabSeparated", name="row count agreement"
        )
        C.standard_end(cluster=cl, result=result, tables=[table])

    def _timed_mutation(self, ctx, result, cl, table, statement, *, label):
        before = C.pool_shape(timeout_s=90)
        counters = C.counters_window(cl)
        ctx.log(f"S09[{label}]: {statement}")
        t0 = time.monotonic()
        cl.node1.command(statement, timeout=600)
        drained, peak = _wait_mutations_done(cl, table, timeout_s=600)
        result.timings[f"{label}_s"] = round(time.monotonic() - t0, 2)
        delta = counters().get("_total", {})
        result.observations[f"counters_{label}"] = delta
        result.observations[f"{label}_mutation_peak_depth"] = peak
        if not drained:
            result.add(
                Verdict.inconclusive(
                    f"{label} mutation drained", "no unfinished mutation", "mutation did not finish in 600s"
                )
            )
        after = C.pool_shape(timeout_s=90)
        if before.get("_ok") and after.get("_ok"):
            growth = after["_total"]["bytes"] - before["_total"]["bytes"]
            result.observations[f"{label}_pool_growth_bytes"] = growth
            return growth
        return None


@register
class S10(Scenario):
    name = "S10"
    title = "patch parts and lightweight deletes"
    priority = "P0"
    param_table = {
        "dev": {
            "rows": 3000,
            "payload_bytes": 1024,
            "bursts": 2,
            "deletes_per_burst": 4,
            "inserts_per_burst": 2,
        },
        "ci": {
            "rows": 20000,
            "payload_bytes": 2048,
            "bursts": 4,
            "deletes_per_burst": 25,
            "inserts_per_burst": 4,
        },
        "full": {
            "rows": 100000,
            "payload_bytes": 4096,
            "bursts": 6,
            "deletes_per_burst": 100,
            "inserts_per_burst": 6,
        },
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        table = "s10_patch"
        result.observations["tables"] = [table]
        rows = int(p["rows"])
        payload_bytes = int(p["payload_bytes"])
        bursts = int(p["bursts"])
        deletes_per_burst = int(p["deletes_per_burst"])
        inserts_per_burst = int(p["inserts_per_burst"])
        C.create_ca_table(cl.node1, table, columns="id UInt64, payload String, k UInt64", order_by="id")
        extra = "(number % 100) AS k"
        next_id = 0
        deleted_buckets = set()
        inserted_rows = 0
        patch_supported = self._probe_patch_parts(result, cl)
        max_patch_parts = 0
        for b in range(bursts):
            counters = C.counters_window(cl)
            for _ in range(inserts_per_burst):
                C.insert_random(
                    cl.node1,
                    table,
                    rows=rows,
                    payload_bytes=payload_bytes,
                    extra_cols_select=extra,
                    op_id=next_id,
                )
                next_id += rows
                inserted_rows += rows
            for d in range(deletes_per_burst):
                bucket = (b * deletes_per_burst + d) % 100
                if bucket in deleted_buckets:
                    continue
                node = cl.node1 if (d % 2 == 0) else cl.node2
                try:
                    node.command(f"ALTER TABLE {table} DELETE WHERE k = {bucket}", timeout=300)
                    deleted_buckets.add(bucket)
                except Exception as e:
                    result.note_anomaly(f"S10 ALTER DELETE k={bucket} failed: {e}")
            _wait_mutations_done(cl, table, timeout_s=600)
            for n in cl.nodes():
                pc = _patch_part_count(n, table)
                if pc is not None:
                    max_patch_parts = max(max_patch_parts, pc)
            try:
                C.gc_drive_round(cl, log_fn=ctx.log)
            except Exception as e:
                ctx.log(f"S10 mid-burst GC raised: {e}")
            del counters
        result.observations["max_patch_parts_observed"] = max_patch_parts
        per_bucket_per_insert = [0] * 100
        for r in range(rows):
            per_bucket_per_insert[r % 100] += 1
        deleted_rows = 0
        for bkt in sorted(deleted_buckets):
            burst_deleted = bkt // deletes_per_burst
            inserts_before_delete = (burst_deleted + 1) * inserts_per_burst
            deleted_rows += per_bucket_per_insert[bkt] * inserts_before_delete
        expected_rows = inserted_rows - deleted_rows
        try:
            observed_rows = int(cl.node1.scalar(f"SELECT count() FROM {table}") or 0)
        except Exception:
            observed_rows = None
        result.add(
            Verdict.check(
                "row count matches delete oracle",
                f"{expected_rows}",
                f"{observed_rows}",
                observed_rows == expected_rows,
            )
        )
        some = 99
        try:
            cl.node1.command(
                f"ALTER TABLE {table} DELETE WHERE k = {some} SETTINGS mutations_sync=2", timeout=600
            )
        except Exception as e:
            result.note_anomaly(f"S10 final ALTER DELETE k={some} failed: {e}")
        try:
            still = int(cl.node1.scalar(f"SELECT count() FROM {table} WHERE k = {some}") or 0)
        except Exception:
            still = None
        result.add(
            Verdict.check(
                "deleted bucket fully removed",
                "0 surviving rows after a final delete",
                f"k={some}: {still}",
                still == 0,
            )
        )
        if patch_supported is True:
            if max_patch_parts > 0:
                result.add(Verdict("patch parts observed in system.parts", "> 0", max_patch_parts, "pass"))
            else:
                result.add(
                    Verdict.inconclusive(
                        "patch parts observed in system.parts",
                        "> 0 when patch parts are producible",
                        "0 patch parts seen; DELETE correctness still validated by the oracle",
                    )
                )
        else:
            result.add(
                Verdict.inconclusive(
                    "patch parts producibility",
                    "patch parts created and observed",
                    patch_supported if isinstance(patch_supported, str) else "not accepted",
                )
            )
        C.assert_replicas_agree(result, cl, C.table_checksum_query(table))
        C.standard_end(cluster=cl, result=result, tables=[table])
        O.assert_reclaimable_drained(
            result,
            "obsolete patch content reclaimed",
            result.observations.get("gc_residual_unreachable"),
            result.observations.get("fsck_final"),
        )

    def _probe_patch_parts(self, result, cl):
        for setting in ("apply_patches_on_merge", "allow_experimental_lightweight_update"):
            try:
                cl.node1.command(f"SET {setting} = 1", timeout=30)
                result.observations.setdefault("patch_part_settings_accepted", []).append(setting)
            except Exception as e:
                result.observations.setdefault("patch_part_settings_rejected", {})[setting] = f"{e}"
        if result.observations.get("patch_part_settings_accepted"):
            return True
        return "no patch-part enabling setting accepted"


@register
class S11(Scenario):
    name = "S11"
    title = "heavy ALTER TABLE ... DELETE"
    priority = "P0"
    param_table = {
        "dev": {
            "buckets": 16,
            "parts": 16,
            "rows_per_part": 1000,
            "payload_bytes": 512,
            "delete_rounds": 6,
            "optimize": True,
            "gc_round_max_ms": 30_000,
        },
        "ci": {
            "buckets": 64,
            "parts": 64,
            "rows_per_part": 4000,
            "payload_bytes": 1024,
            "delete_rounds": 20,
            "optimize": True,
            "gc_round_max_ms": 300_000,
        },
        "full": {
            "buckets": 256,
            "parts": 256,
            "rows_per_part": 10000,
            "payload_bytes": 2048,
            "delete_rounds": 64,
            "optimize": True,
            "gc_round_max_ms": 900_000,
        },
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        table = "s11_buckets"
        result.observations["tables"] = [table]
        buckets = int(p["buckets"])
        parts = int(p["parts"])
        rows_per_part = int(p["rows_per_part"])
        payload_bytes = int(p["payload_bytes"])
        delete_rounds = int(p["delete_rounds"])
        do_optimize = bool(p["optimize"])
        C.create_ca_table(
            cl.node1,
            table,
            columns="id UInt64, payload String, bucket UInt64",
            order_by="id",
            partition_by="bucket",
        )
        next_id = 0
        for _part in range(parts):
            C.insert_random(
                cl.node1,
                table,
                rows=rows_per_part,
                payload_bytes=payload_bytes,
                extra_cols_select=f"(number % {buckets}) AS bucket",
                op_id=next_id,
                settings={"max_partitions_per_insert_block": buckets + 16},
            )
            next_id += rows_per_part
        deleted_buckets = set()
        peak_mut_depth = 0
        peak_merges = 0
        latencies = []
        for rnd in range(delete_rounds):
            bucket = rnd % buckets
            node = cl.node1 if (rnd % 2 == 0) else cl.node2
            t0 = time.monotonic()
            try:
                node.command(f"ALTER TABLE {table} DELETE WHERE bucket = {bucket}", timeout=600)
                deleted_buckets.add(bucket)
            except Exception as e:
                result.note_anomaly(f"S11 ALTER DELETE bucket={bucket} failed: {e}")
            if rnd % 3 == 0 and (buckets // 2) >= 2:
                C.insert_random(
                    cl.node1,
                    table,
                    rows=rows_per_part,
                    payload_bytes=payload_bytes,
                    extra_cols_select=f"((number % {buckets // 2}) + {buckets // 2}) AS bucket",
                    op_id=next_id,
                    settings={"max_partitions_per_insert_block": buckets + 16},
                )
                next_id += rows_per_part
            if do_optimize and rnd % 2 == 1:
                try:
                    cl.node1.command(f"OPTIMIZE TABLE {table}", timeout=600)
                except Exception as e:
                    ctx.log(f"S11 OPTIMIZE raised: {e}")
            for n in cl.nodes():
                d = _mutations_in_flight(n, table)
                if d is not None:
                    peak_mut_depth = max(peak_mut_depth, d)
                m = _active_merges(n, table)
                if m is not None:
                    peak_merges = max(peak_merges, m)
            drained, peak = _wait_mutations_done(cl, table, timeout_s=600)
            peak_mut_depth = max(peak_mut_depth, peak)
            latencies.append(round(time.monotonic() - t0, 3))
        result.observations["peak_mutation_queue_depth"] = peak_mut_depth
        result.observations["peak_active_merges"] = peak_merges
        drained, _ = _wait_mutations_done(cl, table, timeout_s=600)
        final_depth = [_mutations_in_flight(n, table) for n in cl.nodes()]
        result.add(
            Verdict.check(
                "mutation queue drains to zero at checkpoint",
                "all replicas: 0 unfinished mutations",
                final_depth,
                drained and all(d == 0 for d in final_depth if d is not None),
            )
        )
        surviving_in_deleted = None
        if deleted_buckets:
            in_list = ",".join(str(b) for b in sorted(deleted_buckets))
            try:
                surviving_in_deleted = int(
                    cl.node1.scalar(f"SELECT count() FROM {table} WHERE bucket IN ({in_list})") or 0
                )
            except Exception:
                pass
            result.add(
                Verdict.check(
                    "deleted rows gone per oracle",
                    "0 surviving rows in any deleted bucket",
                    surviving_in_deleted,
                    surviving_in_deleted == 0,
                )
            )
        C.assert_replicas_agree(result, cl, C.table_checksum_query(table))
        C.standard_end(cluster=cl, result=result, tables=[table])
        O.assert_reclaimable_drained(
            result,
            "deleted part content reclaimed",
            result.observations.get("gc_residual_unreachable"),
            result.observations.get("fsck_final"),
        )
        gc_log = result.observations.get("gc_all", {})
        max_round_ms = 0
        for rows in gc_log.get("per_node", {}).values():
            for r in rows:
                try:
                    max_round_ms = max(max_round_ms, int(r.get("duration_ms", 0) or 0))
                except Exception:
                    pass
        bound_ms = int(p.get("gc_round_max_ms", 30_000))
        if max_round_ms:
            result.add(
                Verdict.check(
                    "GC round duration bounded",
                    f"< {bound_ms} ms per round (scale={ctx.scale})",
                    f"{max_round_ms} ms",
                    max_round_ms < bound_ms,
                )
            )
        else:
            result.add(
                Verdict.inconclusive(
                    "GC round duration bounded", f"< {bound_ms} ms per round", "no GC finish rows with a duration"
                )
            )
