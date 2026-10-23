"""Dedicated CAS tests for ReplicatedMergeTree (Phase 1 + Phase 2).

Phase 1 — converge
  R1 create RMT on cas_policy across 3 replicas
  R2 insert on replica A → sync → agreement
  R3 insert on B, then C → agreement
  R4 OPTIMIZE FINAL → agreement

Phase 2 — CAS-specific value
  R5 lagging follower catches up via relink (no blob re-upload)
  R6 active replication fetch of parts (covered by R5 sync path)
  R7 FETCH PART / FETCH PARTITION into detached (same pool)
  R8 cross-pool fetch falls back to bytes, data still correct
  R9 ATTACH PARTITION FROM — same pool and different pools
  R10 REPLACE PARTITION into non-empty dest — same pool and different pools
  R11 DETACH / ATTACH / DROP DETACHED
  R12 MOVE PARTITION between RMT tables (same pool)
  R13 FORGET PARTITION after DROP PARTITION
"""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from cas.requirements.requirements import *
from cas.tests.steps import *


PAYLOAD_COLUMNS = "p UInt8, i UInt64, payload String"


@TestScenario
@Name("R1-R4 replicated converge on shared CAS pool")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Replicated("1.0"),
    RQ_SRS_048_CAS_MergeTree_InsertSelect("1.0"),
    RQ_SRS_048_CAS_MergeTree_Merge("1.0"),
    RQ_SRS_048_CAS_SharedPool("1.0"),
)
def replicated_converge(self):
    """Create RMT on cas_policy, write from multiple replicas, merge, and agree."""
    nodes = self.context.nodes
    run_id = getuid()
    table = f"rmt_converge_{run_id}"

    with Given("a ReplicatedMergeTree on cas_policy on all three replicas"):
        create_replicated_cas_table(table_name=table)

    with When("I insert partitions on the first replica"):
        insert_cas_partitions(
            table_name=table,
            partitions=(1, 2),
            rows_per_partition=5,
            node=nodes[0],
        )

    with Then("all replicas converge on the first write"):
        assert_replicas_agree(table_name=table)
        assert (
            table_row_count(nodes[0], table) == 10
        ), error("expected 10 rows after first insert")

    with When("I insert more rows from the second and third replicas"):
        insert_cas_partitions(
            table_name=table,
            partitions=(3,),
            rows_per_partition=4,
            node=nodes[1],
        )
        insert_cas_partitions(
            table_name=table,
            partitions=(4,),
            rows_per_partition=3,
            node=nodes[2],
        )

    with Then("all replicas converge after multi-replica inserts"):
        checksum = assert_replicas_agree(table_name=table)
        assert table_row_count(nodes[0], table) == 17, error(
            f"expected 17 rows, checksum={checksum}"
        )

    with When("I OPTIMIZE FINAL on the first replica"):
        optimize_final(table_name=table, node=nodes[0])

    with Then("replicas still agree after the merge"):
        assert_replicas_agree(table_name=table)
        assert_replication_queue_healthy(table_name=table)


@TestScenario
@Name("R5 follower fetch relinks without re-uploading blobs")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Replicated("1.0"),
    RQ_SRS_048_CAS_Relink("1.0"),
    RQ_SRS_048_CAS_Relink_HappyPath("1.0"),
    RQ_SRS_048_CAS_SharedPool("1.0"),
)
def replicated_fetch_relink(self):
    """Pause fetches on a follower, insert on the leader, then prove relink."""
    nodes = self.context.nodes
    leader, follower = nodes[0], nodes[1]
    run_id = getuid()
    table = f"rmt_relink_{run_id}"
    pool = f"cas_relink_{run_id}"

    with Given("a ReplicatedMergeTree on a dedicated shared CAS pool"):
        create_replicated_cas_table(
            table_name=table,
            pool_prefix=pool,
            columns=PAYLOAD_COLUMNS,
        )

    try:
        with When("I pause fetches on the follower"):
            stop_fetches(table_name=table, node=follower)

        with And("I snapshot CAS counters on both nodes"):
            leader_before = cas_events_snapshot(leader)
            follower_before = cas_events_snapshot(follower)

        with And("I insert large incompressible parts on the leader"):
            for partition in (1, 2):
                insert_cas_payload_rows(
                    table_name=table,
                    rows=64,
                    payload_bytes=16384,
                    partition=partition,
                    id_offset=partition * 1000,
                    node=leader,
                )

        with Then("the leader really uploaded blob bodies"):
            leader_delta = cas_events_delta(leader_before, cas_events_snapshot(leader))
            leader_puts = assert_blob_bodies_were_uploaded(delta=leader_delta)

        with When("I resume fetches and let the follower catch up"):
            start_fetches(table_name=table, node=follower)
            sync_replica(table_name=table, node=follower)

        with Then("follower data matches the leader down to the payload bytes"):
            assert_replicas_agree(
                table_name=table, checksum_fn=payload_table_checksum
            )

        with And("the follower relinked instead of re-uploading the blob bodies"):
            follower_delta = cas_events_delta(
                follower_before, cas_events_snapshot(follower)
            )
            assert_no_blob_reupload_on_fetch(
                delta=follower_delta, writer_puts=leader_puts
            )
    finally:
        with Finally("ensure follower fetches are resumed"):
            follower.query(f"SYSTEM START FETCHES {table}", no_checks=True)


@TestScenario
@Name("R7 FETCH PART and FETCH PARTITION into detached relink on same pool")
@Requirements(
    RQ_SRS_048_CAS_Partition_Fetch("1.0"),
    RQ_SRS_048_CAS_Relink_DetachedFetch("1.0"),
)
def replicated_detached_fetch(self):
    """FETCH into detached on a second RMT table from the source ZK path."""
    nodes = self.context.nodes
    leader = nodes[0]
    run_id = getuid()
    source = f"rmt_fetch_src_{run_id}"
    destination = f"rmt_fetch_dst_{run_id}"
    pool = f"cas_fetch_{run_id}"
    source_path = f"/clickhouse/tables/{source}"

    with Given("a source ReplicatedMergeTree on a shared CAS pool"):
        create_replicated_cas_table(
            table_name=source,
            pool_prefix=pool,
            columns=PAYLOAD_COLUMNS,
            replication_path=source_path,
        )

    with And("an empty replicated destination on the same CAS pool"):
        create_replicated_cas_table(
            table_name=destination,
            pool_prefix=pool,
            columns=PAYLOAD_COLUMNS,
            replication_path=f"/clickhouse/tables/{destination}",
        )

    with When("I fill the source with large incompressible parts"):
        before_insert = cas_events_snapshot(leader)
        for partition in (1, 2):
            insert_cas_payload_rows(
                table_name=source,
                rows=64,
                payload_bytes=16384,
                partition=partition,
                id_offset=partition * 1000,
                node=leader,
            )
        sync_replicas(table_name=source)
        source_p1 = partition_checksum(leader, source, 1)

    with Then("the source insert really uploaded blob bodies"):
        insert_delta = cas_events_delta(before_insert, cas_events_snapshot(leader))
        writer_puts = assert_blob_bodies_were_uploaded(delta=insert_delta)

    with When("I FETCH PARTITION 1 into detached on the destination"):
        before_fetch = cas_events_snapshot(leader)
        fetch_partition(
            table_name=destination,
            partition=1,
            from_path=source_path,
            node=leader,
        )

    with And("I ATTACH the fetched partition"):
        attach_partition(table_name=destination, partition=1, node=leader)

    with Then("destination replicas hold partition 1"):
        assert_replicas_agree(
            table_name=destination, checksum_fn=payload_table_checksum
        )
        for node in nodes:
            assert partition_checksum(node, destination, 1) == source_p1, error(
                f"{node.name} does not hold the fetched partition"
            )

    with And("the detached fetch relinked instead of copying bytes"):
        fetch_delta = cas_events_delta(before_fetch, cas_events_snapshot(leader))
        assert_no_blob_reupload_on_fetch(
            delta=fetch_delta, writer_puts=writer_puts
        )

    with When("I FETCH a single PART for partition 2 into detached"):
        parts = active_part_names(leader, source, partition=2)
        assert parts, error("source has no active parts in partition 2")
        fetch_part(
            table_name=destination,
            part_name=parts[0],
            from_path=source_path,
            node=leader,
        )
        attach_partition(table_name=destination, partition=2, node=leader)

    with Then("destination now matches the source on every replica"):
        assert_replicas_agree(
            table_name=destination, checksum_fn=payload_table_checksum
        )
        assert payload_table_checksum(leader, destination) == payload_table_checksum(
            leader, source
        ), error("destination does not match the source after FETCH PART")


@TestScenario
@Name("R8 cross-pool fetch falls back to bytes")
@Requirements(
    RQ_SRS_048_CAS_Relink_CrossPool_ByteFallback("1.0"),
    RQ_SRS_048_CAS_MergeTree_Replicated("1.0"),
)
def replicated_cross_pool_byte_fallback(self):
    """Replicas on different CAS pools converge, and the receiver copies bytes.

    Each replica owns its own pool, so no manifest can be adopted by reference.
    The receiving replica must therefore publish its own blob bodies — the
    opposite of the same-pool relink case.
    """
    nodes = self.context.nodes
    leader, follower = nodes[0], nodes[1]
    run_id = getuid()
    table = f"rmt_cross_pool_{run_id}"
    pools = [f"cas_cross_a_{run_id}", f"cas_cross_b_{run_id}", f"cas_cross_c_{run_id}"]

    with Given("a ReplicatedMergeTree whose replicas mount distinct CAS pools"):
        create_replicated_cas_table_cross_pool(
            table_name=table,
            pool_prefixes=pools,
            columns=PAYLOAD_COLUMNS,
        )

    with When("I insert large incompressible rows on the first replica"):
        follower_before = cas_events_snapshot(follower)
        insert_cas_payload_rows(
            table_name=table,
            rows=64,
            payload_bytes=16384,
            partition=1,
            node=leader,
        )

    with Then("all replicas converge on identical payload bytes"):
        assert_replicas_agree(table_name=table, checksum_fn=payload_table_checksum)
        assert_replication_queue_healthy(table_name=table)

    with And("the cross-pool receiver published its own blob bodies"):
        follower_delta = cas_events_delta(
            follower_before, cas_events_snapshot(follower)
        )
        assert_blob_bodies_were_uploaded(delta=follower_delta)


@TestScenario
@Name("R9 ATTACH PARTITION FROM same pool and different pools")
@Requirements(
    RQ_SRS_048_CAS_Partition_AttachFrom("1.0"),
    RQ_SRS_048_CAS_Relink_AttachPartitionFrom("1.0"),
)
def replicated_attach_partition_from(self):
    """ATTACH PARTITION FROM into an RMT destination — same pool and cross-pool.

    The cross-pool half is the interesting one: the initiator cannot adopt the
    source manifest by reference, so it must materialise the part into the
    destination pool before the replication queue hands it to the other
    replicas. Two CAS pools is only the cheapest way to reach that generic
    non-relink clone path — the same path carries every attach from a foreign
    disk into CAS, which is how a staging table or a restore lands there. It is
    also the shape that produced the CAS-020 unique-ref collision reproduced in
    ``cas/tests/ref_collision.py``.
    """
    nodes = self.context.nodes
    run_id = getuid()
    foreign_pool = f"cas_attach_foreign_{run_id}"

    src_same = f"src_same_{run_id}"
    dst_same = f"dst_same_{run_id}"
    src_cross = f"src_cross_{run_id}"
    dst_cross = f"dst_cross_{run_id}"

    with Given("source and replicated destination on the shared cas_policy pool"):
        create_cas_merge_tree_table(table_name=src_same)
        create_replicated_cas_table(table_name=dst_same)
        insert_cas_partitions(
            table_name=src_same, partitions=(1, 2), rows_per_partition=5
        )
        source_p1 = partition_checksum(nodes[0], src_same, 1)

    with When("I ATTACH PARTITION 1 FROM the same-pool source"):
        attach_partition_from(
            destination=dst_same, source=src_same, partition=1, node=nodes[0]
        )

    with Then("all replicas receive the attached partition"):
        assert_replicas_agree(table_name=dst_same)
        for node in nodes:
            assert partition_checksum(node, dst_same, 1) == source_p1, error(
                f"{node.name} same-pool attach checksum mismatch"
            )
        assert partition_checksum(nodes[0], src_same, 1) == source_p1, error(
            "ATTACH FROM must not remove data from the source"
        )

    with And("the destination did not leave failing replication queue entries"):
        assert_replication_queue_healthy(table_name=dst_same)

    with Given("a source on a separate CAS pool and a cas_policy destination"):
        create_cas_merge_tree_table(
            table_name=src_cross, pool_prefix=foreign_pool
        )
        create_replicated_cas_table(table_name=dst_cross)
        insert_cas_partitions(
            table_name=src_cross, partitions=(1, 2), rows_per_partition=5
        )
        cross_p1 = partition_checksum(nodes[0], src_cross, 1)

    with When("I ATTACH PARTITION 1 FROM the cross-pool source"):
        attach_partition_from(
            destination=dst_cross, source=src_cross, partition=1, node=nodes[0]
        )

    with Then("cross-pool attach converges with correct data on all replicas"):
        assert_replicas_agree(table_name=dst_cross)
        for node in nodes:
            assert partition_checksum(node, dst_cross, 1) == cross_p1, error(
                f"{node.name} cross-pool attach checksum mismatch"
            )

    with And("the cross-pool attach left no failing replication queue entries"):
        assert_replication_queue_healthy(table_name=dst_cross)


@TestScenario
@Name("R10 REPLACE PARTITION same pool and different pools")
@Requirements(
    RQ_SRS_048_CAS_Partition_Replace("1.0"),
    RQ_SRS_048_CAS_Relink_ReplacePartition("1.0"),
)
def replicated_replace_partition(self):
    """REPLACE PARTITION into a non-empty RMT destination — same pool and cross-pool.

    REPLACE and ATTACH PARTITION FROM share a clone path, but they enter it with
    opposite disk rules: REPLACE requires the source part to live on the
    destination's storage policy, while ATTACH permits a cross-disk copy. So the
    cross-pool half asserts a clean ``BAD_ARGUMENTS`` rejection rather than
    success — and, because REPLACE is destructive, that the rejected statement
    leaves the destination partition fully intact.
    """
    nodes = self.context.nodes
    run_id = getuid()
    source = f"src_replace_{run_id}"
    destination = f"dst_replace_{run_id}"

    with Given("source and non-empty replicated destination on one CAS pool"):
        create_cas_merge_tree_table(table_name=source)
        create_replicated_cas_table(table_name=destination)
        insert_cas_partitions(
            table_name=source, partitions=(1, 2), rows_per_partition=5
        )
        insert_cas_partitions(
            table_name=destination,
            partitions=(1, 2),
            rows_per_partition=7,
            node=nodes[0],
        )
        sync_replicas(table_name=destination)
        source_p1 = partition_checksum(nodes[0], source, 1)
        destination_p2 = partition_checksum(nodes[0], destination, 2)

    with When("I REPLACE PARTITION 1 on the replicated destination"):
        replace_partition_from(
            destination=destination, source=source, partition=1, node=nodes[0]
        )

    with Then("all replicas see the replaced partition and keep the other"):
        assert_replicas_agree(table_name=destination)
        for node in nodes:
            assert partition_checksum(node, destination, 1) == source_p1, error()
            assert partition_checksum(node, destination, 2) == destination_p2, error()

    foreign_pool = f"cas_replace_foreign_{run_id}"
    src_cross = f"src_replace_cross_{run_id}"
    dst_cross = f"dst_replace_cross_{run_id}"

    with Given("a source on a separate CAS pool and a non-empty cas_policy destination"):
        create_cas_merge_tree_table(table_name=src_cross, pool_prefix=foreign_pool)
        create_replicated_cas_table(table_name=dst_cross)
        insert_cas_partitions(
            table_name=src_cross, partitions=(1, 2), rows_per_partition=5
        )
        insert_cas_partitions(
            table_name=dst_cross,
            partitions=(1, 2),
            rows_per_partition=7,
            node=nodes[0],
        )
        sync_replicas(table_name=dst_cross)
        cross_source_p1 = partition_checksum(nodes[0], src_cross, 1)
        cross_original_p1 = partition_checksum(nodes[0], dst_cross, 1)
        cross_original_p2 = partition_checksum(nodes[0], dst_cross, 2)

    with When("I REPLACE PARTITION 1 from the cross-pool source"):
        result = replace_partition_from(
            destination=dst_cross,
            source=src_cross,
            partition=1,
            node=nodes[0],
            no_checks=True,
        )

    with Then("the cross-pool REPLACE is rejected with the generic disk contract"):
        assert result.exitcode != 0, error(
            "cross-pool REPLACE PARTITION was expected to be rejected because "
            "REPLACE requires the source part to sit on the destination's "
            "storage policy"
        )
        assert "Code: 36" in result.output, error(
            f"expected BAD_ARGUMENTS, got: {result.output}"
        )
        assert "does not belong to storage policy" in result.output, error(
            f"expected the generic cross-disk rejection, got: {result.output}"
        )

    with And("the rejected REPLACE left the destination untouched"):
        sync_replicas(table_name=dst_cross)
        assert_replicas_agree(table_name=dst_cross)
        for node in nodes:
            assert partition_checksum(node, dst_cross, 1) == cross_original_p1, error(
                f"{node.name} lost or half-wrote partition 1 on a rejected REPLACE"
            )
            assert partition_checksum(node, dst_cross, 2) == cross_original_p2, error(
                f"{node.name} cross-pool REPLACE disturbed the untouched partition"
            )
        assert partition_checksum(nodes[0], src_cross, 1) == cross_source_p1, error(
            "a rejected REPLACE must not disturb the source"
        )

    with And("the cross-pool REPLACE left no failing replication queue entries"):
        assert_replication_queue_healthy(table_name=dst_cross)


@TestScenario
@Name("R11 DETACH ATTACH and DROP DETACHED on replicated CAS")
@Requirements(
    RQ_SRS_048_CAS_Partition_DetachAttach("1.0"),
    RQ_SRS_048_CAS_Partition_Detach("1.0"),
    RQ_SRS_048_CAS_Partition_Attach("1.0"),
    RQ_SRS_048_CAS_Partition_DropDetached("1.0"),
)
def replicated_detach_attach_drop_detached(self):
    """DETACH / ATTACH round-trip, then DROP DETACHED, with replica agreement."""
    nodes = self.context.nodes
    run_id = getuid()
    table = f"rmt_detach_{run_id}"

    with Given("a replicated CAS table with two partitions"):
        create_replicated_cas_table(table_name=table)
        insert_cas_partitions(
            table_name=table, partitions=(1, 2), rows_per_partition=5, node=nodes[0]
        )
        sync_replicas(table_name=table)
        before = table_checksum(nodes[0], table)
        partition_one = partition_checksum(nodes[0], table, 1)

    with When("I DETACH PARTITION 1 on the first replica"):
        detach_partition(table_name=table, partition=1, node=nodes[0])

    with Then("active data loses partition 1 on all replicas after sync"):
        sync_replicas(table_name=table)
        for node in nodes:
            assert (
                node.query(
                    f"SELECT count() FROM {table} WHERE p = 1"
                ).output.strip()
                == "0"
            ), error()
            assert (
                node.query(
                    f"SELECT count() FROM {table} WHERE p = 2"
                ).output.strip()
                == "5"
            ), error()
            detached = detached_part_names(node, table, "1")
            assert detached, error(
                f"{node.name} detached partition 1 without leaving a part "
                "in system.detached_parts"
            )

    with When("I ATTACH PARTITION 1 back"):
        attach_partition(table_name=table, partition=1, node=nodes[0])

    with Then("the table is restored on all replicas"):
        assert_replicas_agree(table_name=table)
        assert table_checksum(nodes[0], table) == before, error()
        assert partition_checksum(nodes[0], table, 1) == partition_one, error()

    with When("I DETACH PARTITION 1 again and DROP DETACHED on every replica"):
        detach_partition(table_name=table, partition=1, node=nodes[0])
        sync_replicas(table_name=table)
        for node in nodes:
            drop_detached_partition(table_name=table, partition=1, node=node)

    with Then("partition 1 is gone from the table and from the detached namespace"):
        assert_replicas_agree(table_name=table)
        assert (
            nodes[0]
            .query(f"SELECT count() FROM {table} WHERE p = 1")
            .output.strip()
            == "0"
        ), error()
        for node in nodes:
            left = detached_part_names(node, table, "1")
            assert not left, error(
                f"{node.name} still lists partition 1 after DROP DETACHED: {left}"
            )


@TestScenario
@Name("R12 MOVE PARTITION between replicated CAS tables")
@Requirements(
    RQ_SRS_048_CAS_Partition_MoveToTable("1.0"),
)
def replicated_move_partition(self):
    """MOVE PARTITION between two RMT tables on the same CAS pool."""
    nodes = self.context.nodes
    run_id = getuid()
    source = f"src_move_{run_id}"
    destination = f"dst_move_{run_id}"

    with Given("two replicated tables on the shared cas_policy pool"):
        create_replicated_cas_table(table_name=source)
        create_replicated_cas_table(table_name=destination)
        insert_cas_partitions(
            table_name=source, partitions=(1, 2), rows_per_partition=5, node=nodes[0]
        )
        insert_cas_partitions(
            table_name=destination,
            partitions=(3,),
            rows_per_partition=4,
            node=nodes[0],
        )
        sync_replicas(table_name=source)
        sync_replicas(table_name=destination)
        moved = partition_checksum(nodes[0], source, 1)
        kept = partition_checksum(nodes[0], source, 2)

    with When("I MOVE PARTITION 1 from source to destination"):
        move_partition_to_table(
            source=source, destination=destination, partition=1, node=nodes[0]
        )

    with Then("source lost the partition and destination gained it on all replicas"):
        assert_replicas_agree(table_name=source)
        assert_replicas_agree(table_name=destination)
        for node in nodes:
            assert (
                node.query(
                    f"SELECT count() FROM {source} WHERE p = 1"
                ).output.strip()
                == "0"
            ), error()
            assert partition_checksum(node, source, 2) == kept, error()
            assert partition_checksum(node, destination, 1) == moved, error()


@TestScenario
@Name("R13 FORGET PARTITION on replicated CAS")
@Requirements(
    RQ_SRS_048_CAS_Partition_Forget("1.0"),
    RQ_SRS_048_CAS_Partition_Drop("1.0"),
)
def replicated_forget_partition(self):
    """DROP PARTITION then FORGET PARTITION; replicas stay consistent."""
    nodes = self.context.nodes
    run_id = getuid()
    table = f"rmt_forget_{run_id}"

    with Given("a replicated CAS table with two partitions"):
        create_replicated_cas_table(table_name=table)
        insert_cas_partitions(
            table_name=table, partitions=(1, 2), rows_per_partition=5, node=nodes[0]
        )
        sync_replicas(table_name=table)

    with When("I DROP PARTITION 1 and FORGET PARTITION 1"):
        drop_partition(table_name=table, partition=1, node=nodes[0])
        sync_replicas(table_name=table)
        forget_partition(table_name=table, partition=1, node=nodes[0])

    with Then("partition 1 is gone and replicas agree on the remainder"):
        assert_replicas_agree(table_name=table)
        assert (
            nodes[0]
            .query(f"SELECT count() FROM {table} WHERE p = 1")
            .output.strip()
            == "0"
        ), error()
        assert (
            nodes[0]
            .query(f"SELECT count() FROM {table} WHERE p = 2")
            .output.strip()
            == "5"
        ), error()
        assert_replication_queue_healthy(table_name=table)


@TestFeature
@Name("replicated")
def feature(self):
    """ReplicatedMergeTree on content-addressed storage."""
    Scenario(run=replicated_converge)
    Scenario(run=replicated_fetch_relink)
    Scenario(run=replicated_detached_fetch)
    Scenario(run=replicated_cross_pool_byte_fallback)
    Scenario(run=replicated_attach_partition_from)
    Scenario(run=replicated_replace_partition)
    Scenario(run=replicated_detach_attach_drop_detached)
    Scenario(run=replicated_move_partition)
    Scenario(run=replicated_forget_partition)
