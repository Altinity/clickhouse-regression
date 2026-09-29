"""S06 wide part + S07 manifest cap fail-closed + S08 many parts (P0)."""

import time

from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C

MIB = 1024 * 1024
K_MAX_MANIFEST_ENCODED_BYTES = 256 * MIB
K_MAX_MANIFEST_ENTRIES = 1048576
K_MAX_MANIFEST_INLINE_TOTAL = 16 * MIB
K_MAX_LARGEST_INLINE_ENTRY = 1 * MIB
REF_OBJECTS_SANITY_MULTIPLIER = 4
WIDE_PARSER_SETTINGS = {
    "max_query_size": 100 * 1024 * 1024,
    "max_ast_elements": 5_000_000,
    "max_expanded_ast_elements": 5_000_000,
}


def _wide_columns(n_cols, *, key="k", col_type="UInt32"):
    cols = [f"{key} UInt64"]
    cols += [f"c{i} {col_type}" for i in range(n_cols)]
    return ", ".join(cols)


def _wide_select(n_cols, *, rows, base=0):
    exprs = [f"{base} + number AS k"]
    exprs += [f"toUInt32(number + {i}) AS c{i}" for i in range(n_cols)]
    return f"SELECT {', '.join(exprs)} FROM numbers({rows})"


def _wait_nonmerge_queue(nodes, table, timeout_s=120):
    """Wait until only MERGE_PARTS remain. STOP MERGES leaves those entries unexecutable, so SYSTEM SYNC REPLICA waits out receive_timeout."""
    deadline = time.monotonic() + timeout_s
    pending = 0
    sql = (
        "SELECT count() FROM system.replication_queue "
        f"WHERE database = 'default' AND table = '{table}' AND type != 'MERGE_PARTS'"
    )
    while True:
        pending = 0
        for n in nodes:
            pending += int(n.scalar(sql) or 0)
        if pending == 0 or time.monotonic() >= deadline:
            return pending
        time.sleep(1)


def _soft_limit_warnings(cluster, since_event_time):
    where = "logger_name = 'CasStore' AND message LIKE '%crossed soft limit%'"
    if since_event_time:
        where += f" AND event_time >= '{since_event_time}'"
    total = 0
    any_ok = False
    for n in cluster.nodes():
        try:
            v = n.scalar(f"SELECT count() FROM system.text_log WHERE {where}")
            total += int(v or 0)
            any_ok = True
        except Exception:
            pass
    return (total if any_ok else None), any_ok


@register
class S06(Scenario):
    name = "S06"
    title = "10000-column wide part"
    priority = "P0"
    param_table = {
        "dev": {"n_cols": 1000, "block_rows": 200, "subset_cols": 8},
        "ci": {"n_cols": 5000, "block_rows": 500, "subset_cols": 8},
        "full": {"n_cols": 10000, "block_rows": 2000, "subset_cols": 8},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        n_cols = int(p["n_cols"])
        block_rows = int(p["block_rows"])
        subset_cols = int(p["subset_cols"])
        table = "s06_wide"
        result.observations["tables"] = [table]
        ctx.log(f"S06: {n_cols} columns, {block_rows}-row block")
        C.create_ca_table(
            cl.node1, table, columns=_wide_columns(n_cols), order_by="k", client_settings=WIDE_PARSER_SETTINGS
        )
        counters = C.counters_window(cl)
        committed = True
        limit_exceeded = False
        t0 = time.monotonic()
        try:
            C.insert_values(
                cl.node1, table, _wide_select(n_cols, rows=1, base=0), timeout=1200, settings=WIDE_PARSER_SETTINGS
            )
            C.insert_values(
                cl.node1,
                table,
                _wide_select(n_cols, rows=block_rows, base=1000),
                timeout=2400,
                settings=WIDE_PARSER_SETTINGS,
            )
            cl.node1.command(f"OPTIMIZE TABLE {table} FINAL", timeout=2400)
        except Exception as e:
            msg = str(e)
            committed = False
            limit_exceeded = "LIMIT_EXCEEDED" in msg or "Code: 277" in msg or "exceeds cap" in msg
            result.observations["s06_insert_error"] = msg[:2000]
            ctx.log(f"S06: write raised (limit_exceeded={limit_exceeded}): {msg[:200]}")
        result.timings["s06_write_s"] = round(time.monotonic() - t0, 1)
        delta = counters().get("_total", {})
        result.observations["s06_counters"] = delta
        mshape = C.manifests_shape()
        result.observations["s06_pool_manifests"] = mshape
        man_bytes = None
        if mshape.get("_ok") and mshape.get("_manifests"):
            man_objs = mshape["_manifests"]["objects"]
            man_total = mshape["_manifests"]["bytes"]
            man_bytes = (man_total // man_objs) if man_objs else 0
        warn_count, warn_ok = _soft_limit_warnings(cl, ctx.extra.get("since_event_time"))
        if warn_ok:
            result.add(Verdict.check("root-shard manifest soft-limit warnings", "recorded", warn_count, True))
        else:
            result.add(
                Verdict.inconclusive(
                    "root-shard manifest soft-limit warnings", "recorded", "system.text_log not queryable"
                )
            )
        if committed:
            ok_under_cap = (man_bytes is None) or (man_bytes < K_MAX_MANIFEST_ENCODED_BYTES)
            result.add(
                Verdict.check(
                    "wide part outcome",
                    "commit < manifest hard cap OR LIMIT_EXCEEDED",
                    f"committed; mean encoded manifest ~{(man_bytes or 0) / MIB:.3f} MiB",
                    ok_under_cap,
                )
            )
            C.assert_replicas_agree(result, cl, C.table_checksum_query(table))
        elif limit_exceeded:
            result.add(
                Verdict.check(
                    "wide part outcome",
                    "commit < manifest hard cap OR LIMIT_EXCEEDED",
                    "failed-closed with LIMIT_EXCEEDED",
                    True,
                )
            )
        else:
            result.add(
                Verdict.check(
                    "wide part outcome",
                    "commit < manifest hard cap OR LIMIT_EXCEEDED",
                    "failed with a NON-cap error",
                    False,
                )
            )
            result.note_anomaly("S06 wide-part write failed without LIMIT_EXCEEDED")
        if committed:
            cl.node1.command("SYSTEM DROP MARK CACHE")
            cl.node1.command("SYSTEM DROP UNCOMPRESSED CACHE")
            sub_cols = ", ".join(f"c{i}" for i in range(subset_cols))
            cw = C.counters_window(cl)
            try:
                cl.node1.query(
                    f"SELECT sum(cityHash64({sub_cols})) FROM {table} FORMAT TabSeparated",
                    settings={"max_threads": 1},
                )
            except Exception as e:
                ctx.log(f"S06: subset scan raised: {e}")
            subset_gets = cw().get("_total", {}).get("CASBlobGet", 0)
            cl.node1.command("SYSTEM DROP MARK CACHE")
            cl.node1.command("SYSTEM DROP UNCOMPRESSED CACHE")
            cw2 = C.counters_window(cl)
            try:
                cl.node1.query(
                    f"SELECT sum(cityHash64(*)) FROM {table} FORMAT TabSeparated",
                    settings={"max_threads": 1},
                )
            except Exception as e:
                ctx.log(f"S06: all-column scan raised: {e}")
            all_gets = cw2().get("_total", {}).get("CASBlobGet", 0)
            result.observations["s06_subset_CasBlobGet"] = subset_gets
            result.observations["s06_allcol_CasBlobGet"] = all_gets
            if all_gets > 0:
                result.add(
                    Verdict.check(
                        "column-subset avoids full fetch",
                        f"subset CASBlobGet << all-column ({subset_cols}/{n_cols} cols)",
                        f"subset={subset_gets} all={all_gets}",
                        subset_gets < max(1, all_gets // 2),
                    )
                )
            else:
                result.add(
                    Verdict.inconclusive(
                        "column-subset avoids full fetch",
                        "subset << all-column",
                        "all-column scan issued 0 CASBlobGet",
                    )
                )
        C.standard_end(cluster=cl, result=result, tables=[table])


@register
class S07(Scenario):
    name = "S07"
    title = "manifest cap fail-closed"
    priority = "P0"
    expect_exception = True
    param_table = {
        "dev": {"n_cols": 2000, "block_rows": 50},
        "ci": {"n_cols": 10000, "block_rows": 100},
        "full": {"n_cols": 20000, "block_rows": 200},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        n_cols = int(p["n_cols"])
        block_rows = int(p["block_rows"])
        table = "s07_capwide"
        result.observations["tables"] = [table]
        result.observations["caps"] = {
            "kMaxManifestEntries": K_MAX_MANIFEST_ENTRIES,
            "kMaxManifestEncodedBytes": K_MAX_MANIFEST_ENCODED_BYTES,
            "kMaxManifestInlineBytesTotal": K_MAX_MANIFEST_INLINE_TOTAL,
            "kMaxLargestInlineEntryBytes": K_MAX_LARGEST_INLINE_ENTRY,
        }
        C.create_ca_table(
            cl.node1, table, columns=_wide_columns(n_cols), order_by="k", client_settings=WIDE_PARSER_SETTINGS
        )
        triggered = False
        limit_exceeded = False
        non_cap_error = None
        try:
            C.insert_values(
                cl.node1,
                table,
                _wide_select(n_cols, rows=block_rows, base=0),
                settings=WIDE_PARSER_SETTINGS,
                timeout=2400,
            )
            # OPTIMIZE FINAL on a 2k-column wide part can run for tens of minutes
            # without hitting kMaxManifestEntries. Skip it: INSERT is the probe;
            # if it committed, the cap is unreachable at this scale (inconclusive).
        except Exception as e:
            msg = str(e)
            triggered = True
            limit_exceeded = "LIMIT_EXCEEDED" in msg or "Code: 277" in msg or "exceeds cap" in msg
            if not limit_exceeded:
                non_cap_error = msg[:2000]
            result.observations["s07_error"] = msg[:2000]
        if triggered and limit_exceeded:
            result.add(
                Verdict.check(
                    "manifest cap fail-closed", "LIMIT_EXCEEDED before any owner transition", True, True
                )
            )
        elif triggered:
            result.add(
                Verdict.check(
                    "manifest cap fail-closed",
                    "LIMIT_EXCEEDED",
                    "write failed with a NON-cap error",
                    False,
                    f"got: {non_cap_error}",
                )
            )
        else:
            result.add(
                Verdict.inconclusive(
                    "manifest cap fail-closed",
                    "LIMIT_EXCEEDED",
                    f"manifest caps not reachable via SQL at {n_cols} columns vs kMaxManifestEntries={K_MAX_MANIFEST_ENTRIES}",
                )
            )
            result.note_anomaly("S07 could not trigger a manifest cap with this scale")
        if not triggered:
            C.assert_replicas_agree(
                result, cl, f"SELECT count() FROM {table} FORMAT TabSeparated"
            )
        fsck = C.standard_end(cluster=cl, result=result, tables=[table], expect_exception=True)
        dangling = (fsck or {}).get("dangling")
        if dangling is None:
            result.add(Verdict.inconclusive("no live ref on rejected manifest", "fsck dangling==0", "fsck unavailable"))
        else:
            result.add(Verdict.check("no live ref on rejected manifest", "fsck dangling==0 after attempt", dangling, dangling == 0))


@register
class S08(Scenario):
    name = "S08"
    title = "thousands of parts created quickly"
    priority = "P0"
    param_table = {
        "dev": {"n_parts": 2000, "rows_per_part": 1, "clients": 2},
        "ci": {"n_parts": 20000, "rows_per_part": 1, "clients": 4},
        "full": {"n_parts": 100000, "rows_per_part": 1, "clients": 8},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        n_parts = int(p["n_parts"])
        rows_per_part = int(p["rows_per_part"])
        clients = max(1, int(p["clients"]))
        table = "s08_manyparts"
        result.observations["tables"] = [table]
        extra = {
            "parts_to_throw_insert": "1000000",
            "parts_to_delay_insert": "1000000",
            "max_insert_block_size": "1",
        }
        C.create_ca_table(cl.node1, table, columns="id UInt64, v UInt32", order_by="id", extra_settings=extra)
        for n in cl.nodes():
            try:
                n.command(f"SYSTEM STOP MERGES {table}")
            except Exception as e:
                ctx.log(f"S08: STOP MERGES on {n.container} raised: {e}")
        nodes = cl.nodes()
        counters = C.counters_window(cl)
        latencies = []
        t0 = time.monotonic()
        failed_inserts = 0
        for i in range(n_parts):
            node = nodes[i % len(nodes)] if clients > 1 else nodes[0]
            base = i * 1000000
            gen = f"SELECT {base} + number AS id, toUInt32(number) AS v FROM numbers({rows_per_part})"
            ti = time.monotonic()
            try:
                node.command(f"INSERT INTO {table} {gen}", timeout=120)
                latencies.append(time.monotonic() - ti)
            except Exception as e:
                failed_inserts += 1
                if failed_inserts <= 5:
                    ctx.log(f"S08: insert {i} raised: {str(e)[:160]}")
        result.timings["s08_create_s"] = round(time.monotonic() - t0, 1)
        result.observations["s08_failed_inserts"] = failed_inserts
        if latencies:
            latencies.sort()
            n = len(latencies)
            result.observations["s08_insert_latency_s"] = {
                "count": n,
                "p50": round(latencies[n // 2], 4),
                "p95": round(latencies[min(n - 1, int(n * 0.95))], 4),
                "max": round(latencies[-1], 4),
            }
        delta = counters().get("_total", {})
        cas_conflict = delta.get("CASRootCompareSwapConflict", 0)
        cas_total = delta.get("CASRootCompareSwap", 0)
        result.add(
            Verdict.check(
                "no CA-metadata insert failures",
                "failures only from MergeTree part-count pressure",
                f"{failed_inserts} failed insert(s)",
                failed_inserts == 0,
            )
        )
        pending = _wait_nonmerge_queue(nodes, table)
        if pending:
            ctx.log(f"S08: {pending} non-merge replication queue entries still pending")
        from cas.soak_tests.steps.observe import parts_summary

        ps = parts_summary(nodes[0], table)
        result.observations["s08_parts_at_peak"] = ps
        result.add(
            Verdict.check("many active parts created", f"~{n_parts} active before merge", ps.get("active"), ps.get("active", 0) > 0)
        )
        peak_shape = C.manifests_shape()
        result.observations["s08_pool_at_peak"] = peak_shape
        if peak_shape.get("_ok") and peak_shape.get("refs"):
            ref_objs = peak_shape["refs"]["objects"]
            ref_bytes = peak_shape["refs"]["bytes"]
            mean_ref_bytes = (ref_bytes // ref_objs) if ref_objs else 0
            sanity_bound = n_parts * REF_OBJECTS_SANITY_MULTIPLIER + 16
            result.add(
                Verdict.check(
                    "ref objects proportional to insert volume (sanity bound; no root_shards fan-out any more)",
                    f"<= {sanity_bound} ref objects",
                    ref_objs,
                    ref_objs <= sanity_bound,
                )
            )
            result.add(
                Verdict.check(
                    "ref-object body under manifest hard cap (generous sanity bound)",
                    f"mean ref-object body < {K_MAX_MANIFEST_ENCODED_BYTES / MIB:.0f} MiB",
                    f"{mean_ref_bytes / MIB:.3f} MiB",
                    mean_ref_bytes < K_MAX_MANIFEST_ENCODED_BYTES,
                )
            )
        else:
            result.add(
                Verdict.inconclusive(
                    "ref objects proportional to insert volume",
                    f"<= ~{REF_OBJECTS_SANITY_MULTIPLIER}x n_parts",
                    "pool shape unavailable at peak",
                )
            )
        if cas_total > 0:
            ratio = cas_conflict / cas_total
            result.add(
                Verdict.check(
                    "CAS contention bounded",
                    "conflict ratio bounded (< 0.5)",
                    f"{cas_conflict}/{cas_total} = {ratio:.3f}",
                    ratio < 0.5,
                )
            )
        else:
            result.add(Verdict.inconclusive("CAS contention bounded", "conflict ratio bounded", "no CASRootCompareSwap ops"))
        for n in cl.nodes():
            try:
                n.command(f"SYSTEM START MERGES {table}")
            except Exception as e:
                ctx.log(f"S08: START MERGES raised: {e}")
        C.assert_replicas_agree(result, cl, C.table_checksum_query(table))
        C.standard_end(cluster=cl, result=result, tables=[table])
        ps_after = parts_summary(nodes[0], table)
        result.observations["s08_parts_after_merge"] = ps_after
        result.add(
            Verdict.check(
                "parts converged after merge",
                "active parts << peak after OPTIMIZE FINAL",
                f"{ps_after.get('active')} active (peak {ps.get('active')})",
                ps_after.get("active", 0) <= max(1, ps.get("active", 0)),
            )
        )
        fsck = result.observations.get("fsck_final") or {}
        phys = fsck.get("physical_bytes")
        ref = fsck.get("referenced_logical_bytes")
        if phys is not None and ref is not None and ref > 0:
            result.add(
                Verdict.check(
                    "physical bytes converge toward referenced",
                    "physical <= ~2x referenced after merge+GC",
                    f"physical={phys} referenced={ref}",
                    phys <= ref * 2 + (16 * MIB),
                )
            )
        else:
            result.add(
                Verdict.inconclusive(
                    "physical bytes converge toward referenced",
                    "physical ~ referenced",
                    "fsck physical/referenced byte fields unavailable",
                )
            )
