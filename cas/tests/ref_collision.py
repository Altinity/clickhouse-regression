"""CAS unique-ref collision: cross-disk ATTACH PARTITION FROM (alter #98).

Isolated, INSTRUMENTED reproduction of alter combination #98
(``alter/table/attach_partition/temporary_table.py``). When that combination is
run completely ALONE -- every other combination skipped, no concurrent features
-- it STILL fails on the very first ATTACH:

    Code: 210. DB::Exception: CAS write could not be committed
    (promote: ref 'tmp_replace_from_1_1_1_0' already names a different committed
    manifest - refusing to overwrite (unique-ref invariant; use republishRef for
    an intended repoint)); retrying later.

So the trigger is NOT churn and NOT cross-feature concurrency (both earlier
theories were wrong). It is inherent to a single ATTACH PARTITION FROM.

The load-bearing detail: which DISK each table lands on in the alter --cas run.

  * the destination is created through the table helper, which injects
    ``SETTINGS storage_policy = 'cas_policy'`` -> CAS disk;
  * the source is created with a RAW query (no policy). The
    ``zz_cas_default_policy.xml`` override that would remap the *default* disk to
    CAS is written and then immediately removed again by the
    ``enable_cas_default_storage`` step's ``finally`` -- it is called WITHOUT
    ``with`` in ``alter/regression.py`` (``with Given(...): enable_cas_default_storage()``),
    so the file is gone before the cluster even starts. The server default disk
    therefore stays the plain local ``default`` disk.

  => alter #98 is a CROSS-DISK attach: local-disk MergeTree source -> CAS
     ReplicatedMergeTree destination. Cloning across disks forces a byte
     ``IDisk::copyFile`` into CAS and a promote of the deterministic temp ref
     ``tmp_replace_from_1_1_1_0`` (prefix ``tmp_replace_from_`` +
     ``partition_1 _ block_1 _ block_1 _ level_0``), which trips the CAS-020
     unique-ref invariant (``CasPartWriteTxn.cpp`` ``promote`` BUG-1a guard: the
     committed ref table ALREADY has a row for that name naming a DIFFERENT
     manifest -> refuse to overwrite).

Earlier repros put BOTH tables on CAS (same pool -> relink / no forced byte
copy), so they never exercised the promote path and passed. This test contrasts
the two shapes and, on the failing cross-disk shape, dumps the exact stale
binding: ``system.parts`` / detached parts / replication queue / CAS
remote_data_paths and the CAS ref/text log for ``tmp_replace_from_1_1_1_0`` on
every replica.

IMPORTANT: run against the SAME binary as the failing alter run
(``PRs/2073/.../clickhouse-common-static_26.6.1.20000.altinityantalya_arm64.deb``).
"""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

CLUSTER = "replicated_cluster_secure"
REF = "tmp_replace_from_1_1_1_0"

COLUMNS = (
    "a UInt16, b UInt16, c UInt16, extra UInt64, "
    "Path String, Time DateTime, Value Float64, Timestamp Int64, sign Int8"
)

# Partitions produced by the standard 3-partition data fill (matches the alter
# suite's create_regular_partitioned_table_with_data, number_of_partitions=3).
PARTITIONS = ["1", "2", "3", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19"]


@TestStep(Given)
def create_source_with_data(self, table_name, node, disk_clause):
    """Create a regular MergeTree source and fill it exactly like the alter
    suite's ``create_regular_partitioned_table_with_data``.

    ``disk_clause`` chooses the source's disk:
      * ``SETTINGS disk = 'default'``               -> local disk (alter #98 shape)
      * ``SETTINGS storage_policy = 'cas_policy'``   -> CAS (same-pool control)
    """
    node.query(
        f"CREATE TABLE {table_name} ({COLUMNS}) "
        f"ENGINE = MergeTree PARTITION BY a ORDER BY a {disk_clause}"
    )
    for i in range(1, 4):
        node.query(
            f"INSERT INTO {table_name} (a, b, c, extra, sign) "
            f"SELECT {i}, {i + 4}, {i + 8}, number + 1000, 1 FROM numbers(4)"
        )
        node.query(
            f"INSERT INTO {table_name} (a, b, c, extra, sign) "
            f"SELECT number + 10, number + {i} + 14, number + {i} + 18, "
            f"number + 1001, 1 FROM numbers(10)"
        )


@TestStep(Given)
def create_cas_replicated_destination(self, table_name, node):
    """Create an empty ReplicatedMergeTree destination on the CAS disk on every
    replica, exactly like the alter helper: a BARE ReplicatedMergeTree (relies on
    the built-in ``default_replica_path``/``{uuid}``) plus
    ``SETTINGS storage_policy = 'cas_policy'``.
    """
    node.query(
        f"CREATE TABLE IF NOT EXISTS {table_name} ON CLUSTER {CLUSTER} ({COLUMNS}) "
        f"ENGINE = ReplicatedMergeTree PARTITION BY a ORDER BY a "
        f"SETTINGS storage_policy = 'cas_policy'"
    )


@TestStep(Given)
def create_cas_regular_destination(self, table_name, node):
    """Create an empty NON-replicated MergeTree destination on the CAS disk."""
    node.query(
        f"CREATE TABLE {table_name} ({COLUMNS}) "
        f"ENGINE = MergeTree PARTITION BY a ORDER BY a "
        f"SETTINGS storage_policy = 'cas_policy'"
    )


def drop_without_sync(node, table_name, on_cluster=False):
    """Drop a table the way the alter test does: no SYNC, so CAS reclaim of the
    dropped parts/refs stays GC-deferred."""
    cluster = f" ON CLUSTER {CLUSTER}" if on_cluster else ""
    node.query(f"DROP TABLE IF EXISTS {table_name}{cluster}")


@TestStep(Then)
def dump(self, node, title, sql):
    """Run a diagnostic query best-effort (never aborts) and record its output."""
    r = node.query(sql, no_checks=True, steps=False)
    note(f"===== [{node.name}] {title} =====\n{r.output}")


@TestStep(Then)
def dump_cas_state(self, dst, src, when):
    """Dump parts / detached parts / replication queue / CAS remote paths and the
    CAS ref+text log for ``tmp_replace_from_1_1_1_0`` on every replica.

    CAS introspection system tables are discovered at runtime (their exact names
    vary) rather than hard-coded.
    """
    with Then(f"dump CAS + replication state ({when})"):
        for node in self.context.nodes:
            node.query("SYSTEM FLUSH LOGS", no_checks=True, steps=False)

            dump(
                node=node,
                title="disks (type / metadata_type)",
                sql="SELECT name, type, object_storage_type, metadata_type, path "
                "FROM system.disks ORDER BY name FORMAT PrettyCompactNoEscapes",
            )
            dump(
                node=node,
                title=f"source active parts ({src})",
                sql=f"SELECT name, active, disk_name, part_type FROM system.parts "
                f"WHERE table = '{src}' AND active ORDER BY name FORMAT PrettyCompactNoEscapes",
            )
            dump(
                node=node,
                title=f"destination parts ({dst})",
                sql=f"SELECT name, active, disk_name, part_type FROM system.parts "
                f"WHERE table = '{dst}' ORDER BY name FORMAT PrettyCompactNoEscapes",
            )
            dump(
                node=node,
                title=f"destination detached parts ({dst})",
                sql=f"SELECT * FROM system.detached_parts WHERE table = '{dst}' "
                f"FORMAT PrettyCompactNoEscapes",
            )
            dump(
                node=node,
                title=f"replication queue ({dst})",
                sql=f"SELECT type, new_part_name, is_currently_executing, num_tries, "
                f"last_exception FROM system.replication_queue WHERE table = '{dst}' "
                f"FORMAT Vertical",
            )
            dump(
                node=node,
                title=f"CAS remote_data_paths naming {REF}",
                sql=f"SELECT disk_name, local_path, remote_path FROM system.remote_data_paths "
                f"WHERE local_path LIKE '%{REF}%' OR remote_path LIKE '%{REF}%' "
                f"FORMAT PrettyCompactNoEscapes",
            )
            dump(
                node=node,
                title="available CAS introspection system tables",
                sql="SELECT name FROM system.tables WHERE database = 'system' AND "
                "(name LIKE 'ln[_]%' OR name LIKE 'cas[_]%' OR name LIKE '%content_address%') "
                "ORDER BY name FORMAT TSV",
            )
            for cas_table in (
                "ln_log",
                "ln_mounts",
                "ln_events",
                "cas_log",
                "cas_mounts",
            ):
                dump(
                    node=node,
                    title=f"system.{cas_table} (best-effort, first 500 rows)",
                    sql=f"SELECT * FROM system.{cas_table} LIMIT 500 FORMAT Vertical",
                )
            dump(
                node=node,
                title=f"text_log messages naming {REF}",
                sql=f"SELECT event_time_microseconds, level, logger_name, message "
                f"FROM system.text_log WHERE message LIKE '%{REF}%' "
                f"ORDER BY event_time_microseconds FORMAT Vertical",
            )


@TestScenario
def cross_disk_source_to_cas_replicated(self):
    """alter #98 shape: local-disk MergeTree source -> CAS ReplicatedMergeTree
    destination. Instrumented: dump CAS + replication state before and after the
    (expected to fail) first ATTACH PARTITION 1 FROM, then assert the CAS-020
    unique-ref collision reproduced."""
    node = self.context.node
    run = getuid()
    src = f"src_{run}"
    dst = f"dst_{run}"

    try:
        with Given(
            "a local-disk source with 3-partition data and a CAS replicated destination"
        ):
            create_source_with_data(
                table_name=src, node=node, disk_clause="SETTINGS disk = 'default'"
            )
            create_cas_replicated_destination(table_name=dst, node=node)

        with And("baseline CAS + replication state before the attach"):
            dump_cas_state(dst=dst, src=src, when="before ATTACH PARTITION 1")

        with When(
            "I ATTACH PARTITION 1 FROM the local source into the CAS replicated destination"
        ):
            r = node.query(
                f"ALTER TABLE {dst} ATTACH PARTITION 1 FROM {src}",
                no_checks=True,
            )

        with And("CAS + replication state right after the attach"):
            dump_cas_state(dst=dst, src=src, when="after ATTACH PARTITION 1")

        with Then(
            "the CAS-020 unique-ref collision on tmp_replace_from_1_1_1_0 reproduced"
        ):
            assert "already names a different committed manifest" in r.output, error(
                f"expected CAS unique-ref collision on {REF}, got:\n{r.output}"
            )
            assert REF in r.output, error(r.output)
    finally:
        drop_without_sync(node, dst, on_cluster=True)
        drop_without_sync(node, src)


@TestScenario
def cross_disk_source_to_cas_regular(self):
    """Cross-disk into a NON-replicated CAS destination: local-disk MergeTree
    source -> CAS (non-replicated) MergeTree destination.

    Prediction: PASS. This is still a cross-disk byte copy into CAS, but a plain
    MergeTree runs the ATTACH synchronously exactly once, so it promotes
    ``tmp_replace_from_1_1_1_0`` a single time. The unique-ref collision needs a
    SECOND promote of the same deterministic temp ref (the replicated
    destination's replication-queue re-execution of REPLACE_RANGE racing the
    initiator's synchronous clone before the first binding is GC-reclaimed), which
    a non-replicated table never issues.
    """
    node = self.context.node
    run = getuid()
    src = f"src_{run}"
    dst = f"dst_{run}"

    try:
        with Given(
            "a local-disk source with 3-partition data and a CAS non-replicated destination"
        ):
            create_source_with_data(
                table_name=src, node=node, disk_clause="SETTINGS disk = 'default'"
            )
            create_cas_regular_destination(table_name=dst, node=node)

        with When("I ATTACH every partition FROM the local source"):
            for partition in PARTITIONS:
                node.query(f"ALTER TABLE {dst} ATTACH PARTITION {partition} FROM {src}")

        with Then("partition 1 landed in the non-replicated CAS destination"):
            count = node.query(f"SELECT count() FROM {dst} WHERE a = 1").output.strip()
            assert int(count) > 0, error(
                "cross-disk non-replicated attach lost partition 1"
            )
    finally:
        drop_without_sync(node, dst)
        drop_without_sync(node, src)


@TestScenario
def cas_source_to_cas_replicated(self):
    """Control: source AND destination both on CAS (same pool). Matches the
    earlier repros; expected to stay green (relink, no forced byte copy)."""
    node = self.context.node
    run = getuid()
    src = f"src_{run}"
    dst = f"dst_{run}"

    try:
        with Given(
            "a CAS source with 3-partition data and a CAS replicated destination"
        ):
            create_source_with_data(
                table_name=src,
                node=node,
                disk_clause="SETTINGS storage_policy = 'cas_policy'",
            )
            create_cas_replicated_destination(table_name=dst, node=node)

        with When("I ATTACH every partition FROM the CAS source"):
            for partition in PARTITIONS:
                node.query(f"ALTER TABLE {dst} ATTACH PARTITION {partition} FROM {src}")

        with Then("partition 1 landed on the initiator"):
            count = node.query(f"SELECT count() FROM {dst} WHERE a = 1").output.strip()
            assert int(count) > 0, error("same-pool control lost partition 1")
    finally:
        drop_without_sync(node, dst, on_cluster=True)
        drop_without_sync(node, src)


@TestFeature
@Name("ref collision")
def feature(self):
    """Isolated, instrumented cross-disk ATTACH PARTITION FROM CAS unique-ref
    (``tmp_replace_from_1_1_1_0``) reproduction for alter combination #98,
    contrasted against a same-pool control."""
    # Scenario(run=cross_disk_source_to_cas_replicated)
    Scenario(run=cross_disk_source_to_cas_regular)
    # Scenario(run=cas_source_to_cas_replicated)
