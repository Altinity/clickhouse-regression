from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from cas.requirements.requirements import (
    RQ_SRS_048_CAS,
    RQ_SRS_048_CAS_GC_ReclaimAfterDrop,
    RQ_SRS_048_CAS_GC_Run,
    RQ_SRS_048_CAS_GC_StopStart,
    RQ_SRS_048_CAS_MergeTree,
    RQ_SRS_048_CAS_MergeTree_InsertSelect,
    RQ_SRS_048_CAS_NotATableEngine,
    RQ_SRS_048_CAS_ObjectModel,
    RQ_SRS_048_CAS_ObjectModel_Blobs,
    RQ_SRS_048_CAS_ObjectModel_Manifests,
    RQ_SRS_048_CAS_ObjectModel_Refs,
    RQ_SRS_048_CAS_Policy,
)
from cas.tests.steps import (
    CAS_POLICY,
    active_part_disk,
    collect_garbage,
    create_cas_merge_tree_table,
    insert_cas_partitions,
    insert_cas_payload_rows,
    pool_snapshot,
    pool_size_bytes,
    stop_garbage_collection,
    table_engine_and_policy,
)

RECLAIM_ROWS = 64
RECLAIM_PAYLOAD_BYTES = 16384


@TestScenario
@Name("insert and select on cas_policy")
@Requirements(
    RQ_SRS_048_CAS_NotATableEngine("1.0"),
    RQ_SRS_048_CAS_Policy("1.0"),
    RQ_SRS_048_CAS_MergeTree("1.0"),
    RQ_SRS_048_CAS_MergeTree_InsertSelect("1.0"),
)
def insert_select_on_cas(self):
    """Check that ordinary MergeTree insert/select on the named CAS storage policy works."""
    node = self.context.node
    table = f"cas_sanity_insert_select_{getuid()}"

    with Given("create a MergeTree on cas_policy"):
        create_cas_merge_tree_table(table_name=table)

    with And("check that the table is ordinary MergeTree on the named CAS policy"):
        engine, policy = table_engine_and_policy(node, table)
        assert engine == "MergeTree", error(engine)
        assert policy == CAS_POLICY, error(policy)

    with When("insert a small part"):
        insert_cas_partitions(table_name=table, partitions=(1,), rows_per_partition=10)

    with Then("check that the rows can be read back"):
        result = node.query(f"SELECT count(), sum(i) FROM {table}")
        assert result.output.strip() == "10\t45", error(result.output)

    with And("the active parts landed on the CAS policy disk"):
        disk = active_part_disk(node, table)
        assert disk == self.context.cas_disk_name, error(disk)


@TestScenario
@Name("gc reclaims an isolated pool after drop")
@Requirements(
    RQ_SRS_048_CAS_GC_ReclaimAfterDrop("1.0"),
    RQ_SRS_048_CAS_GC_Run("1.0"),
    RQ_SRS_048_CAS_GC_StopStart("1.0"),
)
def gc_reclaim_after_drop(self):
    """Drop a table on its own pool and check manual GC frees the part bytes.

    The inline disk exists only on this node, so GC verbs run there only.
    """
    node = self.context.node
    table = f"cas_sanity_gc_reclaim_{getuid()}"
    pool_prefix = f"data/{table}"
    disk = f"cas_{table}"

    with Given("create a MergeTree on an isolated CAS pool"):
        create_cas_merge_tree_table(
            table_name=table,
            columns="p UInt8, i UInt64, payload String",
            pool_prefix=pool_prefix,
            disk_name=disk,
        )

    with And("stop background garbage collection"):
        stop_garbage_collection(disk=disk, nodes=[node])

    with And("measure the empty pool"):
        sizes = {}
        size_before = pool_size_bytes(pool_prefix=pool_prefix)
        sizes["before_insert"] = size_before
        note(f"{pool_prefix} before insert: {size_before} bytes")

    with When("insert an incompressible part"):
        insert_cas_payload_rows(
            table_name=table,
            rows=RECLAIM_ROWS,
            payload_bytes=RECLAIM_PAYLOAD_BYTES,
        )

    with Then("the pool grew"):
        size_after_insert = pool_size_bytes(pool_prefix=pool_prefix)
        sizes["after_insert"] = size_after_insert
        note(f"{pool_prefix} after insert: {size_after_insert} bytes")
        assert size_after_insert > size_before, error(
            f"insert did not grow the pool: before={size_before} "
            f"after={size_after_insert}"
        )

    with And("drop the table and run 3 rounds of GC"):
        node.query(f"DROP TABLE IF EXISTS {table} SYNC")
        collect_garbage(disk=disk, nodes=[node], rounds=1)
        size_after_gc = pool_size_bytes(pool_prefix=pool_prefix)
        sizes["after_first_gc"] = size_after_gc
        note(f"{pool_prefix} after first GC: {size_after_gc} bytes")
        collect_garbage(disk=disk, nodes=[node], rounds=1)
        size_after_gc = pool_size_bytes(pool_prefix=pool_prefix)
        sizes["after_second_gc"] = size_after_gc
        note(f"{pool_prefix} after second GC: {size_after_gc} bytes")
        collect_garbage(disk=disk, nodes=[node], rounds=1)
        size_after_gc = pool_size_bytes(pool_prefix=pool_prefix)
        sizes["after_third_gc"] = size_after_gc
        note(f"{pool_prefix} after third GC: {size_after_gc} bytes")
        assert sizes["after_third_gc"] < sizes["after_insert"], error(
            f"third GC did not shrink the pool: after insert={sizes['after_insert']} "
            f"after third GC={sizes['after_third_gc']}"
        )
        note(f"sizes: {sizes}")

    with And("check that gc rounds after third gc are no-ops"):
        collect_garbage(disk=disk, nodes=[node], rounds=1)
        size_after_gc = pool_size_bytes(pool_prefix=pool_prefix)
        sizes["after_fourth_gc"] = size_after_gc
        note(f"{pool_prefix} after fourth GC: {size_after_gc} bytes")
        assert sizes["after_fourth_gc"] == sizes["after_third_gc"], error(
            f"fourth GC changed the pool: after third GC={sizes['after_third_gc']} "
            f"after fourth GC={sizes['after_fourth_gc']}"
        )


@TestScenario
@Name("pool layout after a small write")
@Requirements(
    RQ_SRS_048_CAS_ObjectModel("1.0"),
    RQ_SRS_048_CAS_ObjectModel_Blobs("1.0"),
    RQ_SRS_048_CAS_ObjectModel_Manifests("1.0"),
    RQ_SRS_048_CAS_ObjectModel_Refs("1.0"),
)
def pool_layout(self):
    """Check that a small write publishes blobs, manifests, and refs."""
    table = f"cas_sanity_layout_{getuid()}"
    pool_prefix = f"data/{table}"

    with Given("create a MergeTree on an isolated CAS pool"):
        create_cas_merge_tree_table(table_name=table, pool_prefix=pool_prefix)

    with When("insert one small part"):
        insert_cas_partitions(table_name=table, partitions=(1,), rows_per_partition=10)

    with Then("check that the pool has blobs, manifests, and refs"):
        keys = sorted(pool_snapshot(pool_prefix=pool_prefix))
        blob = "blobs/ch128/af/af5b2979a0cd3076c30a45df649102e2"
        assert blob in keys, error(keys)
        assert f"{blob}.meta" in keys, error(keys)
        assert any(
            k.startswith("cas/manifests/")
            and k.endswith("/0000000000000001-0000000000000001/000001.zst")
            for k in keys
        ), error(keys)
        assert any(k.startswith("cas/ns/stream/") for k in keys), error(keys)


@TestFeature
@Name("sanity")
@Requirements(RQ_SRS_048_CAS("1.0"))
def feature(self):
    """Basic content-addressed MergeTree checks."""
    Scenario(run=insert_select_on_cas)
    Scenario(run=gc_reclaim_after_drop)
    Scenario(run=pool_layout)
