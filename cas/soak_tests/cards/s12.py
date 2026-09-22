"""S12 ten-replica shared pool (P0).

The body is the original card. A 2-node env fails the replica-count check until
the ten-replica compose is wired; that harness work is separate from this port.
"""

import threading

from cas.soak_tests.oracle.events import cluster_events_delta
from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C
from cas.soak_tests.steps import observe as O

@register
class S12(Scenario):
    name = "S12"
    title = "ten replicas, shared pool, parallel inserts"
    priority = "P0"
    # Runs on the 10-replica compose (docker-compose-10replicas.yml: ch1..ch10 over ONE shared CA
    # pool + RustFS + Keeper). The runner brings this variant up and builds a 10-node Cluster
    # (soak/cluster.py Cluster(node_count=10)); no needs_infra skip.
    compose_variant = "tenreplicas"

    param_table = {
        "dev": {"replicas": 10, "rows_per_replica": 1000, "duplicate_fraction": 0.5},
        "ci": {"replicas": 10, "rows_per_replica": 100000, "duplicate_fraction": 0.5},
        "full": {"replicas": 10, "rows_per_replica": 1000000, "duplicate_fraction": 0.5},
    }

    def run(self, ctx, result):
        """Ten ReplicatedMergeTree replicas of one table, all over ONE shared content-addressed pool.
        All 10 write CONCURRENTLY: each inserts a SHARED block (identical ids+payload on every replica
        → must dedup to a single logical/physical copy under a 10-way concurrent race) plus its own
        UNIQUE block (distinct ids). Asserts: all 10 replicas converge to a byte-identical checksum;
        the shared block is stored once (row count == shared + N*unique); CA dedup fired under
        concurrency; and the shared pool is GC-safe (dangling=0, reclaimable drains, no Failed rounds,
        no bad CA-log events)."""
        cl = ctx.cluster
        p = ctx.params
        nodes = cl.nodes()
        n_rep = len(nodes)
        rpr = int(p["rows_per_replica"])
        dup_frac = float(p["duplicate_fraction"])
        shared_rows = int(rpr * dup_frac)
        unique_n = rpr - shared_rows
        table = "s12_shared"

        result.observations["scale"] = {
            "replicas": n_rep, "rows_per_replica": rpr, "duplicate_fraction": dup_frac,
            "shared_rows": shared_rows, "unique_per_replica": unique_n}
        result.add(Verdict.check(
            "replica count matches 10-replica compose",
            f"{p['replicas']} replicas", f"{n_rep} live replicas",
            n_rep == int(p["replicas"]),
            "" if n_rep == int(p["replicas"]) else
            f"cluster has {n_rep}, expected {p['replicas']} — check docker-compose-10replicas.yml / node_count"))

        # Replicated CA table on ALL replicas (shared ZK path → they replicate each other's inserts).
        for n in nodes:
            C.create_ca_table(n, table, columns="id UInt64, payload String", order_by="id", wide=True)

        before = C.counters_window(cl)

        # 10-way CONCURRENT inserts. Shared block: identical ids+payload on every replica (payload is
        # deterministic in id → same bytes everywhere) so RMT block-dedup + CA content-addressing must
        # collapse the 10 concurrent copies to one. Unique block: distinct ids per replica.
        errors = []

        def _writer(i, node):
            try:
                if shared_rows > 0:
                    C.insert_values(
                        node, table,
                        f"SELECT number AS id, leftPad(toString(number), 256, 'x') AS payload "
                        f"FROM numbers({shared_rows})")
                if unique_n > 0:
                    base = shared_rows + i * unique_n
                    C.insert_values(
                        node, table,
                        f"SELECT {base} + number AS id, randomString(256) AS payload "
                        f"FROM numbers({unique_n})")
            except Exception as e:
                errors.append({"replica": node.container, "err": str(e)[:200]})

        threads = [threading.Thread(target=_writer, args=(i, n)) for i, n in enumerate(nodes)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        delta = before()
        result.observations["insert_errors"] = errors
        result.add(Verdict.check(
            "no errors during 10-way concurrent inserts", "0 errors",
            f"{len(errors)} errors", not errors, "" if not errors else f"{errors[:3]}"))

        # Converge: SYNC every replica so the agreement check sees the fully-replicated state.
        for n in nodes:
            try:
                n.command(f"SYSTEM SYNC REPLICA {table}", timeout=300)
            except Exception as e:
                ctx.log(f"S12 SYNC {n.container}: {e}")

        # CORE: all ten replicas byte-identical (count + row-hash). This is the shared-pool +
        # 10-way-replication correctness gate.
        C.assert_replicas_agree(
            result, cl, C.table_checksum_query(table),
            name="S12 all-replica agreement (10-way)")

        # 10-way replication convergence: every replica's insert replicates to all others, so the
        # converged table is the FULL union = N * rows_per_replica. RMT does NOT row-dedup identical
        # INSERT...SELECT here (verified against a local-disk RMT oracle: CA and local both keep all
        # copies — this is stock ClickHouse behavior, NOT a CA property). All replicas must agree on
        # this count (the agreement checksum above already gates equality).
        expected = n_rep * rpr
        try:
            cnt = int(nodes[0].scalar(f"SELECT count() FROM {table}"))
        except Exception as e:
            cnt = -1
            ctx.log(f"S12 count read failed: {e}")
        result.add(Verdict.check(
            "10-way replication converges to full union (count == N*rows_per_replica)",
            f"{expected}", f"{cnt}", cnt == expected,
            "" if cnt == expected else
            f"expected {expected} ({n_rep}*{rpr}); got {cnt} — 10-way replication lost/duplicated rows"))

        # CA CONTENT dedup across writers (the real shared-pool property, distinct from RMT row-dedup):
        # the SHARED block's payload content is byte-identical on all N replicas, so content-addressing
        # stores it ONCE physically and the redundant body-PUTs are avoided (CASBlobBodyPutAvoided>0).
        # This is what "shared pool" buys: N writers of identical content pay one physical copy.
        tot = delta.get("_total", {})
        result.observations["dedup_counters"] = {
            k: int(tot.get(k, 0)) for k in
            ("CASBlobBodyPutAvoided", "CASBlobDeduplicationCacheHit", "CASBlobHeadFirst", "CASManifestPut")}
        avoided = int(tot.get("CASBlobBodyPutAvoided", 0))
        dedup_expected = shared_rows > 0
        result.add(Verdict.check(
            "CA content dedup across 10 writers (shared payload stored once)",
            ">0 body-puts avoided" if dedup_expected else "n/a (no shared block)",
            f"CASBlobBodyPutAvoided={avoided}",
            (avoided > 0) if dedup_expected else True,
            "" if (avoided > 0 or not dedup_expected) else
            "shared identical content across 10 writers was NOT physically deduped in the pool"))

        # Shared-pool GC safety: dangling=0, reclaimable drains, no Failed GC rounds, no bad CA events.
        C.checkpoint_view(cl, result, [table], table_filter="table LIKE 's12_%'")
