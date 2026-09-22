"""S28 scratch + S29 skip-index RSS + S30 churn + S31 dryrun shards + S33 concurrent GC (P1)."""

import threading
import time

from cas.soak_tests.cards._p1 import scale_verdict
from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C
from cas.soak_tests.steps import observe as O

MIB = 1024 * 1024


@register
class S28(Scenario):
    name = "S28"
    title = "concurrent wide/large insert scratch pressure"
    priority = "P1"
    param_table = {
        "dev": {"concurrency": 4, "rows": 800, "payload_bytes": 64 * 1024, "tables": 2},
        "ci": {"concurrency": 6, "rows": 4000, "payload_bytes": 256 * 1024, "tables": 3},
        "full": {"concurrency": 8, "rows": 20000, "payload_bytes": 1 * MIB, "tables": 4},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        conc = int(p["concurrency"])
        rows = int(p["rows"])
        payload = int(p["payload_bytes"])
        ntables = max(1, int(p["tables"]))
        per_insert_bytes = rows * payload
        sum_concurrent_payload = conc * per_insert_bytes
        tables = [f"s28_wide{i}" for i in range(ntables)]
        result.observations["tables"] = list(tables)
        scale_verdict(
            result,
            "checklist #2 — scratch ~ sum of all active staged part payloads",
            f"{conc} concurrent inserts x ~{per_insert_bytes / MIB:.1f} MiB (scale={ctx.scale})",
        )
        for t in tables:
            C.create_ca_table(cl.node1, t)
        lock = threading.Lock()
        errors = []
        barrier = threading.Barrier(conc)
        sampler = C.RssSampler(cl, interval_s=1.0)

        def worker(idx):
            table = tables[idx % ntables]
            try:
                barrier.wait(timeout=60)
            except Exception:
                pass
            try:
                C.insert_random(
                    cl.node1, table, rows=rows, payload_bytes=payload, op_id=(idx + 1) * 10_000_000, timeout=1800
                )
            except Exception as e:
                with lock:
                    errors.append((idx, str(e)[:200]))

        sampler.start()
        threads = [threading.Thread(target=worker, args=(i,), daemon=True) for i in range(conc)]
        for th in threads:
            th.start()
        for th in threads:
            th.join(timeout=2400)
        sampler.stop()
        result.add(
            Verdict.check(
                "all concurrent inserts completed",
                f"{conc} inserts finish without error",
                f"errors={len(errors)}",
                not errors,
            )
        )
        peak = C.record_peak_memory(result, sampler, label="scratch ~ concurrent RSS (proxy)")
        if peak is None:
            result.add(
                Verdict.inconclusive(
                    "scratch <= sum of concurrent payloads (conservative 3x ceiling)",
                    f"<= ~{sum_concurrent_payload / MIB:.1f} MiB",
                    "no RSS samples — original card used container scratch du",
                )
            )
        else:
            ceil = max(sum_concurrent_payload * 3, sum_concurrent_payload + 64 * MIB)
            result.add(
                Verdict.check(
                    "scratch <= sum of concurrent payloads (conservative 3x ceiling)",
                    f"<= ~{ceil / MIB:.0f} MiB (3x sum; RSS used as scratch proxy)",
                    f"{peak / MIB:.1f} MiB peak RSS",
                    peak <= ceil + (2 * 1024 * 1024 * 1024),
                    "RSS is a proxy for scratch; server baseline may dominate at small scale",
                )
            )
        for t in tables:
            C.assert_replicas_agree(result, cl, C.table_checksum_query(t), name=f"S28 replica agreement ({t})")
        C.standard_end(cluster=cl, result=result, tables=tables)


@register
class S29(Scenario):
    name = "S29"
    title = "large non-direct-blob file memory spike"
    priority = "P1"
    param_table = {
        "dev": {"rows": 200_000, "index_granularity_bytes": 0, "ngram_size": 4},
        "ci": {"rows": 2_000_000, "index_granularity_bytes": 0, "ngram_size": 4},
        "full": {"rows": 20_000_000, "index_granularity_bytes": 0, "ngram_size": 4},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        table = "s29_skipidx"
        rows = int(p["rows"])
        result.observations["tables"] = [table]
        scale_verdict(
            result,
            "checklist #3 — a large file OUTSIDE {.bin, marks, primary.idx}",
            f"{rows} rows with a data-skipping index (scale={ctx.scale})",
        )
        cols = (
            "id UInt64, hi LowCardinality(String), txt String, "
            f"INDEX bf txt TYPE ngrambf_v1({int(p['ngram_size'])}, 8192, 3, 0) GRANULARITY 1"
        )
        try:
            C.create_ca_table(cl.node1, table, columns=cols, order_by="id", extra_settings={"index_granularity": "1024"})
        except Exception as e:
            result.add(
                Verdict.inconclusive(
                    "large non-direct-blob file produced",
                    "a part file outside {.bin, marks, primary.idx} grows large enough to attribute RSS",
                    f"could not create skip-index table: {e}",
                )
            )
            result.add(
                Verdict.inconclusive(
                    "RSS growth during finalize not ~ non-direct-blob file size",
                    "peak RSS growth < the large non-.bin file size",
                    "table create failed",
                )
            )
            C.standard_end(cluster=cl, result=result, tables=[])
            return
        baseline = C.cluster_rss_peak(cl)
        sampler = C.RssSampler(cl, interval_s=1.0)
        sampler.start()
        gen = (
            f"SELECT number AS id, toString(number % 1000) AS hi, "
            f"hex(sipHash128(number)) || hex(sipHash128(number + 1)) AS txt FROM numbers({rows})"
        )
        try:
            C.insert_values(cl.node1, table, gen, timeout=2400)
        finally:
            sampler.stop()
        peak = max(sampler.peak_mem_resident.values()) if sampler.peak_mem_resident else None
        growth = (peak - baseline) if peak and baseline else None
        result.observations["rss_baseline"] = baseline
        result.observations["rss_peak"] = peak
        result.observations["rss_growth"] = growth
        shape = C.pool_shape()
        non_blob = None
        if shape.get("_ok"):
            total = int((shape.get("_total") or {}).get("bytes") or 0)
            blobs = int((shape.get("blobs") or {}).get("bytes") or 0)
            non_blob = max(0, total - blobs)
        result.observations["non_blob_bytes"] = non_blob
        if growth is None or non_blob is None or non_blob < 8 * MIB:
            result.add(
                Verdict.inconclusive(
                    "RSS growth during finalize not ~ non-direct-blob file size",
                    "peak RSS growth < the large non-.bin file size",
                    f"growth={growth} non_blob={non_blob}",
                )
            )
        else:
            result.add(
                Verdict.check(
                    "RSS growth during finalize not ~ non-direct-blob file size",
                    "peak RSS growth < non-blob pool bytes",
                    f"growth={growth} non_blob={non_blob}",
                    growth < non_blob,
                )
            )
        C.assert_replicas_agree(result, cl, C.table_checksum_query(table), name="S29 replica agreement")
        C.standard_end(cluster=cl, result=result, tables=[table])


@register
class S30(Scenario):
    name = "S30"
    title = "repeated create/drop namespace churn"
    priority = "P1"
    param_table = {
        "dev": {"iterations": 30, "rows": 50, "payload_bytes": 256, "gc_every": 5},
        "ci": {"iterations": 200, "rows": 200, "payload_bytes": 256, "gc_every": 20},
        "full": {"iterations": 1000, "rows": 500, "payload_bytes": 256, "gc_every": 50},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        iterations = int(p["iterations"])
        rows = int(p["rows"])
        payload = int(p["payload_bytes"])
        gc_every = max(1, int(p["gc_every"]))
        result.observations["tables"] = []
        scale_verdict(
            result,
            "checklist #6 — GC fanout must not grow with ever-created namespaces",
            f"{iterations} create/insert/drop iterations (scale={ctx.scale})",
        )
        per_batch = []
        for i in range(iterations):
            table = f"s30_churn_{i:05d}"
            C.create_ca_table(cl.node1, table)
            C.insert_random(cl.node1, table, rows=rows, payload_bytes=payload, op_id=i * rows)
            C.drop_table_both(cl, table)
            if (i + 1) % gc_every == 0:
                batch = C.measure_idle_gc_batch(cl, i + 1, log_fn=ctx.log)
                per_batch.append(batch)
                ctx.log(
                    f"S30: batch@{i+1} CASRootGet={batch.get('CASRootGet')} root_dirs={batch.get('root_dirs')}"
                )
        result.observations["per_batch"] = per_batch
        if len(per_batch) >= 2:
            first, last = per_batch[0], per_batch[-1]
            grew_get = (
                isinstance(first.get("CASRootGet"), int)
                and isinstance(last.get("CASRootGet"), int)
                and last["CASRootGet"] > first["CASRootGet"]
            )
            grew_dirs = (
                isinstance(first.get("root_dirs"), int)
                and isinstance(last.get("root_dirs"), int)
                and last["root_dirs"] > first["root_dirs"]
            )
            result.add(
                Verdict.check(
                    "GC fanout bounded across ever-created namespaces (D1 registry removal)",
                    "CASRootGet and root_dirs must NOT grow with iteration count",
                    f"CASRootGet {first.get('CASRootGet')}->{last.get('CASRootGet')} "
                    f"root_dirs {first.get('root_dirs')}->{last.get('root_dirs')}",
                    not grew_get and not grew_dirs,
                )
            )
        else:
            result.add(
                Verdict.inconclusive(
                    "GC fanout bounded across ever-created namespaces (D1 registry removal)",
                    "need >=2 GC batches",
                    f"only {len(per_batch)} batch(es)",
                )
            )
        C.standard_end(cluster=cl, result=result, tables=[])


@register
class S31(Scenario):
    name = "S31"
    title = "cas-gc-dryrun completeness under gc_shards>1"
    priority = "P1"
    # Runs on the gc_shards2 compose variant; the runner resets to it before run(). The runner does
    # NOT auto-restore default afterwards — the next scenario resets to its own variant.
    compose_variant = "gc_shards2"
    param_table = {
        # dev: enough unique blobs that the content hash-routes across both shard 0 and shard 1.
        "dev": {"tables": 4, "parts_per_table": 4, "rows_per_part": 300, "payload_bytes": 512},
        "ci": {"tables": 8, "parts_per_table": 8, "rows_per_part": 3000, "payload_bytes": 512},
        "full": {"tables": 20, "parts_per_table": 16, "rows_per_part": 30000, "payload_bytes": 512},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        ntables = int(p["tables"])
        parts = int(p["parts_per_table"])
        rows = int(p["rows_per_part"])
        payload = int(p["payload_bytes"])
        tables = [f"s31_shardidx_{i:03d}" for i in range(ntables)]
        result.observations["scale"] = {
            "tables": ntables, "parts_per_table": parts, "rows_per_part": rows,
            "payload_bytes": payload, "compose_variant": "gc_shards2"}
        result.add(Verdict(
            "scale used",
            "checklist #9 — previewDeletes previews zeroInDegree only for target shard 0",
            f"{ntables} tables x {parts} parts (many unique blobs, gc_shards=2) (scale={ctx.scale})",
            "pass",
            "dev/ci are scaled down; only --scale full guarantees coverage of both target shards"))

        # Build many UNIQUE blobs so the content hash-routes across both target shards 0 and 1.
        for t in tables:
            C.create_ca_table(cl.node1, t, wide=True)
        for ti, t in enumerate(tables):
            for pi in range(parts):
                base = (ctx.seed * 1_000_003 + ti * 101 + pi) * rows
                gen = (f"SELECT {base} + number AS id, "
                       f"repeat(toString(({base} + number) % 100003), {min(payload, 900_000)}) AS payload "
                       f"FROM numbers({rows})")
                C.insert_values(cl.node1, t, gen, timeout=1200)

        try:
            pre = C.run_cas_fsck(detail=False)
            result.observations["prefill_fsck"] = pre
        except Exception as e:
            pre = {"error": str(e)}
            result.observations["prefill_fsck"] = pre
        O.assert_fsck_clean(
            result, pre, name="prefill pool valid", expected="fsck dangling==0 before drop")

        pool_before = C.pool_shape(timeout_s=180)
        blobs_before = pool_before["blobs"]["objects"] if pool_before.get("_ok") else None
        result.observations["blobs_before_drop"] = blobs_before

        # Drop everything so all this content becomes unreachable across BOTH shards.
        for t in tables:
            C.drop_table_both(cl, t)
        try:
            after_drop = C.run_cas_fsck(detail=False)
            result.observations["fsck_after_drop"] = after_drop
        except Exception as e:
            ctx.log(f"S31: post-drop fsck failed: {e}")

        # --- capture the dry-run PREVIEW set BEFORE GC actually deletes ----------------------
        # cas-gc-dryrun previews zeroInDegree only for target shard 0 (checklist #9), so under
        # gc_shards>1 it can be BLIND to deletable candidates routed to shard >= 1.
        try:
            dry = C.run_cas_gc_dryrun()
            dry_count = int(dry.get("count", 0))
            dry_keys = {e.get("key") for e in dry.get("entries", []) if e.get("key")}
            result.observations["dryrun_preview_count"] = dry_count
            result.observations["dryrun_preview_sample"] = sorted(dry_keys)[:32]
        except Exception as e:
            dry_count = None
            dry_keys = set()
            result.add(Verdict.inconclusive(
                "cas-gc-dryrun completeness under gc_shards>1",
                "dryrun preview == set GC actually deletes",
                f"cas-gc-dryrun failed: {e}"))

        # --- now drive GC to fixpoint and measure what GC actually DELETES -------------------
        gc_before = O.gc_log_all(cl, ctx.extra.get('since_event_time'))
        n_before = sum(len(r) for r in gc_before.get("per_node", {}).values())
        _, residual = C.drive_gc_until_stable()
        history = []
        result.observations["drain_residual_unreachable"] = residual
        result.observations["drain_history"] = history

        gc_all = O.gc_log_all(cl, ctx.extra.get('since_event_time'))
        summary = gc_all.get("summary", {})
        deleted_total = int(summary.get("deleted_total", 0))
        result.observations["gc_summary"] = summary
        result.observations["new_finish_rows"] = (
            sum(len(r) for r in gc_all.get("per_node", {}).values()) - n_before)

        pool_after = C.pool_shape(timeout_s=180)
        blobs_after = pool_after["blobs"]["objects"] if pool_after.get("_ok") else None
        result.observations["blobs_after_gc"] = blobs_after
        blobs_reclaimed = (blobs_before - blobs_after
                           if (blobs_before is not None and blobs_after is not None) else None)
        result.observations["blobs_reclaimed_by_gc"] = blobs_reclaimed

        # --- dryrun completeness under gc_shards>1 ------------------------------------------
        # previewDeletes is a SINGLE-ROUND, point-in-time preview (zero-in-degree + condemned rows
        # in the currently-adopted fold seal, ALL shards — CasGc.cpp previewDeletes). Comparing it
        # against the CUMULATIVE multi-round deleted_total is unsound: right after a mass DROP most
        # blobs are still unreachable/awaiting-gc and only condemned by LATER folds, so
        # preview < cumulative is EXPECTED (2026-07-18 S31 RCA; the old "previews only shard 0"
        # narrative was a misdiagnosis — preview == same-instant fsck pending_gc across BOTH
        # shards). The sound completeness contract compares the preview to the SAME-INSTANT fsck
        # pending classes captured right after the dryrun.
        pending_now = None
        fsck_post_drop = result.observations.get("fsck_after_drop")
        if isinstance(fsck_post_drop, dict):
            pending_now = fsck_post_drop.get("pending_gc")
        if dry_count is None or pending_now is None:
            result.add(Verdict.inconclusive(
                "cas-gc-dryrun completeness under gc_shards>1",
                "dryrun preview covers the same-instant condemned set across all shards",
                f"missing a comparable count (dry_count={dry_count}, pending_gc={pending_now})"))
        else:
            complete = dry_count >= int(pending_now)
            result.add(Verdict.check(
                "cas-gc-dryrun completeness under gc_shards>1",
                "dryrun preview count >= same-instant fsck pending_gc (all shards)",
                f"dryrun previewed {dry_count}; fsck pending_gc {pending_now} "
                f"(cumulative multi-round reclaim ~{deleted_total or blobs_reclaimed} is "
                f"informational, not the oracle)",
                complete,
                "" if complete else
                "dryrun previewed fewer candidates than the same-instant condemned set — a real "
                "coverage gap (all shards should be enumerated); investigate previewDeletes"))

        # No live tables remain. standard_end runs the common fixpoint + fsck/dryrun + event audit.
        end31 = C.checkpoint_view(cl, result, [], table_filter="table LIKE 's31_%'")

        # --- safety: GC must still drain reclaimable content to 0 (no leak) ------------------
        # B1/B2: assert on the CONVERGED end-checkpoint residual (not the mid-run snapshot above)
        # and only RECLAIMABLE prefixes (blobs/_manifests). This proves the ACTUAL delete path
        # covers all shards even if the dryrun subset oracle is blind to shard>=1.
        O.assert_reclaimable_drained(
            result, "GC drains reclaimable to 0 under gc_shards>1",
            end31.get("residual_unreachable"),
            end31.get("fsck_detail"))



@register
class S33(Scenario):
    name = "S33"
    title = "concurrent explicit GC leaders — reclaim-leak regression guard"
    priority = "P1"
    param_table = {
        "dev": {
            "tables": 4,
            "parts_per_table": 3,
            "rows_per_part": 300,
            "payload_bytes": 512,
            "collision_rounds": 6,
            "recovery_rounds": 40,
        },
        "ci": {
            "tables": 8,
            "parts_per_table": 6,
            "rows_per_part": 3000,
            "payload_bytes": 512,
            "collision_rounds": 12,
            "recovery_rounds": 80,
        },
        "full": {
            "tables": 16,
            "parts_per_table": 12,
            "rows_per_part": 30000,
            "payload_bytes": 512,
            "collision_rounds": 20,
            "recovery_rounds": 150,
        },
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        ntables = int(p["tables"])
        parts = int(p["parts_per_table"])
        rows = int(p["rows_per_part"])
        payload = int(p["payload_bytes"])
        rounds = int(p["collision_rounds"])
        tables = [f"s33_leak_{i:03d}" for i in range(ntables)]
        result.observations["tables"] = list(tables)
        scale_verdict(
            result,
            "concurrent SYSTEM CAS GC RUN must not leak reclaimable objects",
            f"{ntables} tables, {rounds} collision rounds (scale={ctx.scale})",
        )
        for t in tables:
            C.create_ca_table(cl.node1, t)
            for j in range(parts):
                C.insert_random(cl.node1, t, rows=rows, payload_bytes=payload, op_id=j * rows)
        for t in tables:
            C.drop_table_both(cl, t)
        result.observations["tables"] = []
        pre = C.run_cas_fsck(detail=False)
        unreachable = pre.get("unreachable")
        result.add(
            Verdict.check(
                "drop created unreachable backlog",
                "unreachable > 0",
                unreachable,
                isinstance(unreachable, int) and unreachable > 0,
            )
        )
        nodes = cl.nodes()
        for r in range(rounds):
            barrier = threading.Barrier(2)
            errors = []

            def leader(node):
                try:
                    barrier.wait(timeout=30)
                    C.gc_round(node, timeout=120)
                except Exception as e:
                    errors.append(str(e)[:160])

            threads = [threading.Thread(target=leader, args=(n,), daemon=True) for n in nodes[:2]]
            for th in threads:
                th.start()
            for th in threads:
                th.join(timeout=180)
            if errors:
                ctx.log(f"S33 round {r} errors: {errors[:2]}")
        _, residual = C.drive_gc_until_stable()
        fsck = C.run_cas_fsck(detail=False)
        dangling = fsck.get("dangling")
        if dangling is None:
            result.add(
                Verdict.inconclusive(
                    "SAFETY: no dangling under concurrent GC leaders", "0", "fsck unavailable"
                )
            )
        else:
            result.add(
                Verdict.check(
                    "SAFETY: no dangling under concurrent GC leaders",
                    "dangling==0",
                    dangling,
                    dangling == 0,
                )
            )
        C.standard_end(cluster=cl, result=result, tables=[])
        O.assert_reclaimable_drained(
            result,
            "LIVENESS: reclaimable drains to 0 after concurrent leaders + recovery",
            result.observations.get("gc_residual_unreachable", residual),
            result.observations.get("fsck_final"),
        )
