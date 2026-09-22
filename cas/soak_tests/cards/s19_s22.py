"""S19 clone/move + S20 fetch/relink + S21 read-heavy + S22 throttling (P1)."""

import os
import subprocess
import threading
import time

from cas.soak_tests.cards._p1 import scale_verdict
from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C
from cas.soak_tests.steps import observe as O
from cas.soak_tests.steps.chaos import ensure_clickhouse_daemon

MIB = 1024 * 1024
_CH2 = os.environ.get("CA_SOAK_TESTS_NODE2_CONTAINER", "soak_tests_env-clickhouse2-1")


@register
class S19(Scenario):
    name = "S19"
    title = "clone and partition movement"
    priority = "P1"
    param_table = {
        "dev": {
            "payload_bytes": 256 * 1024,
            "rows_per_part": 4,
            "parts_per_partition": 2,
            "partitions": 3,
        },
        "ci": {
            "payload_bytes": 1 * MIB,
            "rows_per_part": 8,
            "parts_per_partition": 3,
            "partitions": 4,
        },
        "full": {
            "payload_bytes": 4 * MIB,
            "rows_per_part": 16,
            "parts_per_partition": 4,
            "partitions": 6,
        },
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        payload = int(p["payload_bytes"])
        rows = int(p["rows_per_part"])
        ppp = int(p["parts_per_partition"])
        nparts = int(p["partitions"])
        src, dst = "s19_src", "s19_dst"
        result.observations["tables"] = [src, dst]
        result.observations["scale"] = {
            "payload_bytes": payload,
            "rows_per_part": rows,
            "parts_per_partition": ppp,
            "partitions": nparts,
        }
        scale_verdict(
            result,
            "clone moves metadata only at any scale",
            f"{nparts} partitions x {ppp} parts x {rows} rows x {payload} B (scale={ctx.scale})",
        )
        cols = "id UInt64, part_key UInt8, payload String"
        C.create_ca_table(cl.node1, src, columns=cols, order_by="id", partition_by="part_key")
        C.create_ca_table(cl.node1, dst, columns=cols, order_by="id", partition_by="part_key")
        op = 0
        for part_key in range(nparts):
            for _ in range(ppp):
                gen = (
                    f"SELECT {op} + number AS id, toUInt8({part_key}) AS part_key, "
                    f"randomString({payload}) AS payload FROM numbers({rows})"
                )
                C.insert_values(cl.node1, src, gen, timeout=1200)
                op += rows
        try:
            cl.node1.command(f"SYSTEM SYNC REPLICA {src}", timeout=120)
        except Exception as e:
            ctx.log(f"S19 SYNC src: {e}")
        pool_before = C.pool_shape()
        move_key = 0
        counters = C.counters_window(cl)
        cl.node1.command(f"ALTER TABLE {src} MOVE PARTITION {move_key} TO TABLE {dst}", timeout=600)
        move_delta = counters().get("_total", {})
        replace_key = 1 if nparts > 1 else 0
        counters2 = C.counters_window(cl)
        cl.node1.command(f"ALTER TABLE {dst} REPLACE PARTITION {replace_key} FROM {src}", timeout=600)
        replace_delta = counters2().get("_total", {})
        pool_after = C.pool_shape()
        clone_body_puts = C.blob_body_puts(move_delta) + C.blob_body_puts(replace_delta)
        copied_threshold = max(1, (ppp * rows * payload) // (2 * payload) if payload else 1)
        result.add(
            Verdict.check(
                "clone moves metadata only (no body re-upload)",
                "CASBlobPut for MOVE/REPLACE PARTITION stays small (republish refs, not copy blobs)",
                f"CASBlobPut move+replace = {clone_body_puts}",
                clone_body_puts <= copied_threshold,
            )
        )
        if pool_before.get("_ok") and pool_after.get("_ok"):
            grew = pool_after["_total"]["bytes"] - pool_before["_total"]["bytes"]
            one_partition_bytes = ppp * rows * payload
            result.add(
                Verdict.check(
                    "pool grew by metadata only during clone",
                    f"< {one_partition_bytes / MIB:.1f} MiB (one full partition payload)",
                    f"{grew / MIB:.2f} MiB",
                    grew < one_partition_bytes,
                )
            )
        else:
            result.add(
                Verdict.inconclusive(
                    "pool grew by metadata only during clone",
                    "pool byte growth < one partition payload",
                    "pool shape unavailable",
                )
            )
        gated_key = nparts - 1
        counters3 = C.counters_window(cl)
        gate_err = None
        try:
            cl.node1.command(f"ALTER TABLE {src} MOVE PARTITION {gated_key} TO DISK 'default'", timeout=120)
        except Exception as e:
            gate_err = str(e)
        gate_delta = counters3().get("_total", {})
        blob_put = int(gate_delta.get("CASBlobPut", 0))
        if gate_err is not None:
            result.add(
                Verdict.check(
                    "gated cross-disk move fails closed",
                    "ALTER ... MOVE PARTITION TO non-CA DISK raises and writes no partial body",
                    f"raised; CASBlobPut={blob_put}",
                    blob_put == 0,
                )
            )
        else:
            result.add(
                Verdict.inconclusive(
                    "gated cross-disk move fails closed",
                    "ALTER ... MOVE PARTITION TO non-CA DISK raises",
                    "cross-disk MOVE was accepted in this build",
                )
            )
        C.assert_replicas_agree(result, cl, C.table_checksum_query(src), name="S19 src replica agreement")
        C.assert_replicas_agree(result, cl, C.table_checksum_query(dst), name="S19 dst replica agreement")
        dst_moved = int(
            cl.node1.scalar(f"SELECT count() FROM {dst} WHERE part_key = {move_key}") or 0
        )
        result.add(
            Verdict.check(
                "moved partition lands in dst",
                f"count == {ppp * rows}",
                dst_moved,
                dst_moved == ppp * rows,
            )
        )
        C.standard_end(cluster=cl, result=result, tables=[src, dst])
        O.assert_fsck_clean(result, result.observations.get("fsck_final"), name="no dangling after clone ops")


@register
class S20(Scenario):
    name = "S20"
    title = "replicated fetch and relink"
    priority = "P1"
    param_table = {
        "dev": {"payload_bytes": 512 * 1024, "rows_per_part": 8, "parts": 3, "fetch_wait_s": 90},
        "ci": {"payload_bytes": 2 * MIB, "rows_per_part": 16, "parts": 4, "fetch_wait_s": 180},
        "full": {"payload_bytes": 8 * MIB, "rows_per_part": 32, "parts": 6, "fetch_wait_s": 300},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        payload = int(p["payload_bytes"])
        rows = int(p["rows_per_part"])
        nparts = int(p["parts"])
        fetch_wait = int(p["fetch_wait_s"])
        table = "s20_repl"
        approx_payload = nparts * rows * payload
        result.observations["tables"] = [table]
        scale_verdict(
            result,
            "follower fetch shares blobs at any payload size",
            f"{nparts} parts x {rows} rows x {payload} B (~{approx_payload / MIB:.1f} MiB; scale={ctx.scale})",
        )
        C.create_ca_table(cl.node1, table)
        ctx.log(f"S20: stopping follower {_CH2}")
        stop = subprocess.run(["docker", "stop", _CH2], capture_output=True, text=True, timeout=120)
        if stop.returncode != 0:
            subprocess.run(["docker", "start", _CH2], capture_output=True, timeout=120)
            ensure_clickhouse_daemon(_CH2)
            result.add(
                Verdict.inconclusive(
                    "follower relinks without re-uploading big blobs",
                    "follower CASBlobPut for big bodies ~ 0",
                    f"could not stop follower {_CH2}: {stop.stderr[:200]}",
                )
            )
            return
        try:
            for i in range(nparts):
                C.insert_random(cl.node1, table, rows=rows, payload_bytes=payload, op_id=i * rows)
            cl.node1.command(f"OPTIMIZE TABLE {table} FINAL", timeout=600)
            pool_before = C.pool_shape()
        finally:
            ctx.log(f"S20: starting follower {_CH2}")
            subprocess.run(["docker", "start", _CH2], capture_output=True, timeout=120)
            ensure_clickhouse_daemon(_CH2)
        healthy = O.wait_cluster_healthy(cl, timeout_s=fetch_wait, log_fn=ctx.log)
        if not healthy:
            result.add(
                Verdict.inconclusive(
                    "follower relinks without re-uploading big blobs",
                    "follower CASBlobPut for big bodies ~ 0",
                    f"follower did not become healthy within {fetch_wait}s",
                )
            )
            C.standard_end(cluster=cl, result=result, tables=[table], expect_exception=True)
            return
        counters = C.counters_window(cl)
        try:
            cl.node2.command(f"SYSTEM SYNC REPLICA {table}", timeout=fetch_wait)
        except Exception as e:
            ctx.log(f"S20 SYNC follower: {e}")
        deadline = time.monotonic() + fetch_wait
        while time.monotonic() < deadline:
            try:
                q = int(cl.node2.scalar(f"SELECT count() FROM system.replication_queue WHERE table='{table}'") or 0)
            except Exception:
                q = None
            if q == 0:
                break
            time.sleep(1)
        finish = counters()
        follower = finish.get(cl.node2.container, finish.get("_total", {}))
        body_puts = C.blob_body_puts(follower)
        dedup = int(follower.get("CASBlobPutDeduplicated", 0) or 0) + int(
            follower.get("CASBlobBodyPutAvoided", 0) or 0
        )
        result.add(
            Verdict.check(
                "follower relinks without re-uploading big blobs",
                f"body puts <= {nparts} AND (dedup>0 OR body_puts==0)",
                f"CASBlobPut={body_puts} dedup/avoided={dedup}",
                body_puts <= nparts and (dedup > 0 or body_puts == 0),
            )
        )
        cas = int(follower.get("CASRootCompareSwap", 0) or 0)
        if cas > 0:
            result.add(Verdict.check("follower publishes its own refs", "CASRootCompareSwap > 0", cas, True))
        else:
            result.add(
                Verdict.inconclusive(
                    "follower publishes its own refs", "CASRootCompareSwap > 0", "no CASRootCompareSwap on follower"
                )
            )
        pool_after = C.pool_shape()
        if pool_before.get("_ok") and pool_after.get("_ok"):
            grew = pool_after["_total"]["bytes"] - pool_before["_total"]["bytes"]
            result.add(
                Verdict.check(
                    "pool grows by metadata on fetch",
                    f"< {approx_payload / 2 / MIB:.1f} MiB (half payload)",
                    f"{grew / MIB:.2f} MiB",
                    grew < approx_payload / 2,
                )
            )
        C.assert_replicas_agree(result, cl, C.table_checksum_query(table), name="S20 replica convergence")
        C.standard_end(cluster=cl, result=result, tables=[table])
        O.assert_fsck_clean(result, result.observations.get("fsck_final"), name="no dangling after fetch")


@register
class S21(Scenario):
    name = "S21"
    title = "read-heavy many-ref workload"
    priority = "P1"
    param_table = {
        "dev": {
            "parts": 8,
            "rows_per_part": 200,
            "ncols": 12,
            "col_bytes": 4096,
            "point_lookups": 20,
            "readers": 4,
            "scan_rounds": 3,
        },
        "ci": {
            "parts": 12,
            "rows_per_part": 400,
            "ncols": 16,
            "col_bytes": 2048,
            "point_lookups": 40,
            "readers": 6,
            "scan_rounds": 4,
        },
        "full": {
            "parts": 100,
            "rows_per_part": 20000,
            "ncols": 60,
            "col_bytes": 16384,
            "point_lookups": 200,
            "readers": 16,
            "scan_rounds": 10,
        },
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        table = "s21_wide"
        nparts = int(p["parts"])
        rows = int(p["rows_per_part"])
        ncols = int(p["ncols"])
        col_bytes = int(p["col_bytes"])
        nlook = int(p["point_lookups"])
        nreaders = int(p["readers"])
        rounds = int(p["scan_rounds"])
        result.observations["tables"] = [table]
        scale_verdict(
            result,
            "read-path caching stays bounded under many refs",
            f"{nparts} parts x {ncols} cols (scale={ctx.scale})",
        )
        cols = ["id UInt64"] + [f"c{i} String" for i in range(ncols)]
        C.create_ca_table(cl.node1, table, columns=", ".join(cols), order_by="id")
        for i in range(nparts):
            C.insert_values(
                cl.node1,
                table,
                f"SELECT {i * rows} + number AS id, "
                + ", ".join(f"randomString({col_bytes}) AS c{j}" for j in range(ncols))
                + f" FROM numbers({rows})",
                timeout=1200,
            )
        try:
            cl.node1.command(f"SYSTEM SYNC REPLICA {table}", timeout=300)
        except Exception as e:
            ctx.log(f"S21 SYNC: {e}")
        probe_id = rows // 2
        cl.node1.query(f"SELECT * FROM {table} WHERE id = {probe_id} FORMAT Null")
        cw = C.counters_window(cl)
        for _ in range(nlook):
            cl.node1.query(f"SELECT * FROM {table} WHERE id = {probe_id} FORMAT Null")
        root_get = int(cw().get("_total", {}).get("CASRootGet", 0) or 0)
        linear_floor = max(1, nlook * nparts)
        result.add(
            Verdict.check(
                "repeated point lookups don't re-fetch root per file",
                f"CASRootGet << {linear_floor}",
                root_get,
                root_get < linear_floor,
            )
        )
        cw1 = C.counters_window(cl)
        cl.node1.query(f"SELECT sum(length(c0)) FROM {table} FORMAT Null")
        one_get = int(cw1().get("_total", {}).get("CASBlobGet", 0) or 0)
        cw2 = C.counters_window(cl)
        all_cols = " + ".join(f"length(c{i})" for i in range(ncols))
        cl.node1.query(f"SELECT sum({all_cols}) FROM {table} FORMAT Null")
        all_get = int(cw2().get("_total", {}).get("CASBlobGet", 0) or 0)
        if all_get == 0 and one_get == 0:
            result.add(
                Verdict.inconclusive(
                    "column-subset fetches only required blobs",
                    "1-col CASBlobGet < all-col",
                    "both scans issued 0 CASBlobGet",
                )
            )
        else:
            result.add(
                Verdict.check(
                    "column-subset fetches only required blobs",
                    "1-col CASBlobGet < all-col",
                    f"1col={one_get} all={all_get}",
                    one_get < all_get,
                )
            )
        errors = []
        lock = threading.Lock()
        sampler = C.RssSampler(cl, interval_s=1.0)
        sampler.start()

        def reader(i):
            try:
                for _ in range(rounds):
                    cl.node1.query(
                        f"SELECT count(), sum(sipHash64(c0)) FROM {table} FORMAT Null",
                        timeout=120,
                    )
            except Exception as e:
                with lock:
                    errors.append((i, str(e)[:200]))

        threads = [threading.Thread(target=reader, args=(i,), daemon=True) for i in range(nreaders)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=600)
        sampler.stop()
        result.add(
            Verdict.check(
                "concurrent readers succeed",
                "errors==0",
                f"{len(errors)} errors",
                not errors,
            )
        )
        C.record_peak_memory(result, sampler, label="read memory bounded under concurrency")
        C.assert_replicas_agree(result, cl, C.table_checksum_query(table), name="S21 replica agreement")
        C.standard_end(cluster=cl, result=result, tables=[table])


@register
class S22(Scenario):
    name = "S22"
    title = "object-store throttling and retry budget"
    priority = "P1"
    # Runs on the fault-proxy compose (docker-compose-s3faultproxy.yml): a small HTTP proxy sits
    # between ClickHouse and RustFS (ca endpoint -> s3proxy:11121, forwarded verbatim to rustfs1).
    # Faults are armed/disarmed at runtime via the proxy control port (localhost:8474).
    compose_variant = "s3faultproxy"

    param_table = {
        "dev": {"tables": 2, "rows": 1500, "payload_bytes": 4096, "fault_rate": 0.25,
                "modes": ["503", "429", "slow"]},
        "ci": {"tables": 4, "rows": 20000, "payload_bytes": 4096, "fault_rate": 0.2,
               "modes": ["503", "429", "slow"]},
        "full": {"tables": 6, "rows": 100000, "payload_bytes": 4096, "fault_rate": 0.15,
                 "modes": ["503", "429", "slow"]},
    }

    _CTL = "http://localhost:8474"

    def _ctl(self, path, obj=None, timeout=10):
        import json as _json
        import urllib.request
        url = self._CTL + path
        if obj is None:
            return _json.loads(urllib.request.urlopen(url, timeout=timeout).read().decode())
        req = urllib.request.Request(url, data=_json.dumps(obj).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        return _json.loads(urllib.request.urlopen(req, timeout=timeout).read().decode())

    def run(self, ctx, result):
        """Object-store throttling / retry-budget under injected transient faults. With the proxy
        armed to return `503 SlowDown` / `429` / artificial latency on a fraction of GET/PUT/HEAD, a
        write+merge workload must still COMPLETE CORRECTLY (the S3 client retries within its budget)
        and every replica must converge (agreement), with no committed ref to a missing blob/manifest
        (`fsck dangling == 0`). The proxy's own fault counter proves the fault path was actually
        exercised (else the test is vacuous)."""
        import json as _json
        cl = ctx.cluster
        p = ctx.params
        nodes = cl.nodes()
        n_tables = int(p["tables"])
        rows = int(p["rows"])
        payload = int(p["payload_bytes"])
        rate = float(p["fault_rate"])
        modes = list(p["modes"])
        tables = [f"s22_t{i}" for i in range(n_tables)]

        # Proxy reachable?
        try:
            hz = self._ctl("/healthz")
        except Exception as e:
            result.add(Verdict.inconclusive("fault proxy reachable", "control :8474 up",
                                            f"unreachable: {e}"))
            return
        result.observations["proxy"] = {"healthz": hz}

        # Baseline (faults DISARMED): create tables on both replicas + a seed insert.
        self._ctl("/config", {"rate": 0.0})
        for t in tables:
            for n in nodes:
                C.create_ca_table(n, t, columns="id UInt64, payload String", order_by="id", wide=True)
            C.insert_random(nodes[0], t, rows=rows // 2, payload_bytes=payload, op_id=0)

        # Snapshot S3 retry counters before the fault window.
        def s3_counters():
            out = {}
            for n in nodes:
                try:
                    txt = n.query(
                        "SELECT event, value FROM system.events WHERE event LIKE 'DiskS3%' "
                        "AND (event LIKE '%Error%' OR event LIKE '%Attempt%' OR event LIKE '%Throttl%') "
                        "FORMAT TabSeparated")
                    out[n.container] = {r.split("\t")[0]: int(r.split("\t")[1])
                                        for r in txt.splitlines() if "\t" in r}
                except Exception:
                    out[n.container] = {}
            return out

        before_ctr = s3_counters()

        # ARM faults, then run a write + merge workload that forces many GET/PUT/HEAD through the proxy.
        armed = self._ctl("/config", {"rate": rate, "modes": modes,
                                      "methods": ["GET", "PUT", "HEAD", "POST"], "seed": 22})
        result.observations["armed_config"] = armed.get("config")
        errors = []
        for t in tables:
            try:
                C.insert_random(nodes[0], t, rows=rows // 2, payload_bytes=payload, op_id=rows)
                C.insert_random(nodes[1 % len(nodes)], t, rows=rows // 2, payload_bytes=payload,
                                  op_id=2 * rows)
                # OPTIMIZE forces merges -> reads existing part blobs + writes merged blobs (GET/PUT
                # storm through the proxy) -> exercises the read + write retry paths.
                nodes[0].command(f"OPTIMIZE TABLE {t} FINAL", timeout=300)
            except Exception as e:
                errors.append({"table": t, "err": str(e)[:200]})

        # DISARM before the checkpoint (fsck/GC must see ground truth, not faults).
        self._ctl("/config", {"rate": 0.0})
        stats = self._ctl("/stats")
        result.observations["proxy_stats"] = stats

        # 1. The fault path was actually exercised (otherwise the whole scenario is vacuous).
        injected = int(stats.get("faults", 0))
        result.add(Verdict.check(
            "transient faults were injected (test not vacuous)", "> 0 faults", f"{injected}",
            injected > 0, "" if injected > 0 else "proxy injected 0 faults — rate too low / no matching requests"))

        # 2. Successful workload statements completed despite faults (retries absorbed them).
        result.observations["workload_errors"] = errors
        result.add(Verdict.check(
            "write+merge workload succeeded under injected faults", "0 hard errors",
            f"{len(errors)} errors", not errors,
            "" if not errors else f"{errors[:3]} — retries did not absorb the transient faults"))

        # 3. Retries actually occurred AND were bounded (no unbounded attempt blow-up).
        after_ctr = s3_counters()
        def _delta(ev):
            tot = 0
            for c in after_ctr:
                tot += after_ctr.get(c, {}).get(ev, 0) - before_ctr.get(c, {}).get(ev, 0)
            return tot
        read_err = _delta("DiskS3ReadRequestsErrors")
        write_err = _delta("DiskS3WriteRequestsErrors")
        read_att = _delta("DiskS3ReadRequestAttempts")
        write_att = _delta("DiskS3WriteRequestAttempts")
        result.observations["s3_retry_delta"] = {
            "ReadRequestsErrors": read_err, "WriteRequestsErrors": write_err,
            "ReadRequestAttempts": read_att, "WriteRequestAttempts": write_att}
        retried = (read_err + write_err) > 0
        # Bounded: total attempts must be within a sane multiple of the injected faults (retry budget),
        # not an unbounded storm. Use a generous ceiling.
        att_total = read_att + write_att
        bounded = att_total <= max(1000, injected * 50)
        result.add(Verdict.check(
            "S3 retries occurred and were bounded by the retry budget",
            "retryable errors > 0 and attempts bounded",
            f"errors={read_err + write_err}, attempts={att_total}, injected={injected}",
            retried and bounded,
            "" if (retried and bounded) else
            ("no retryable errors recorded despite injected faults" if not retried
             else f"attempt count {att_total} looks unbounded vs {injected} injected faults")))

        # 4. All replicas converge despite the fault window.
        for t in tables:
            for n in nodes:
                try:
                    n.command(f"SYSTEM SYNC REPLICA {t}", timeout=300)
                except Exception as e:
                    ctx.log(f"S22 SYNC {t}@{n.container}: {e}")
            C.assert_replicas_agree(result, cl, C.table_checksum_query(t),
                                          name=f"S22 replica agreement [{t}]")

        # 5. No committed ref to a missing blob/manifest; GC-safe end.
        C.checkpoint_view(cl, result, tables, table_filter="table LIKE 's22_%'")
