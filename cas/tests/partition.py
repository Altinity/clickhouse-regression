from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from cas.requirements.requirements import *
from cas.tests.steps import (
    active_part_names,
    assert_active_parts_on_disk,
    assert_check_table,
    attach_part,
    attach_partition,
    attach_partition_from,
    collect_garbage,
    create_cas_merge_tree_table,
    detach_part,
    detach_partition,
    detached_part_names,
    drop_detached_part,
    drop_detached_partition,
    drop_part,
    drop_partition,
    insert_cas_partitions,
    insert_cas_payload_rows,
    move_partition_to_table,
    partition_checksum,
    replace_partition_from,
    restart_server,
    settled_pool_snapshot,
    stop_garbage_collection,
    stop_merges,
    table_checksum,
)
from cas.tests.steps.materialized_view import payload_blob_count

# Reclamation is staged, so one SYSTEM CAS GC RUN does not finish a delete.
GC_ROUNDS = 4
PAYLOAD_COLUMNS = "p UInt8, i UInt64, payload String"


def _row_count(node, table_name, partition=None):
    where = "" if partition is None else f" WHERE p = {partition}"
    return node.query(f"SELECT count() FROM {table_name}{where}").output.strip()


def _assert_readable(node, table_name, disk_name):
    """Active parts are intact and still on the disk the table was created on."""
    assert_active_parts_on_disk(
        table_name=table_name, disk_name=disk_name, node=node
    )
    assert_check_table(table_name=table_name, node=node)


def _payload_blobs(pool_prefix):
    count = payload_blob_count(settled_pool_snapshot(pool_prefix=pool_prefix))
    note(f"{pool_prefix} payload blobs: {count}")
    return count


def _payload_partition_checksum(node, table_name, partition):
    return node.query(
        "SELECT count(), sum(i), groupBitXor(cityHash64(payload)) "
        f"FROM {table_name} WHERE p = {partition}"
    ).output.strip()


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Transparency("1.0"),
    RQ_SRS_048_CAS_Partition_AlterAllowList("1.1"),
    RQ_SRS_048_CAS_Partition_Replace("1.0"),
)
def replace_partition_same_cas_disk(self):
    """REPLACE PARTITION between two MergeTree tables on the same CAS pool."""
    node = self.context.node
    run_id = getuid()
    pool_prefix = f"cas_replace_{run_id}"
    disk_name = f"cas_replace_{run_id}"
    source = f"src_replace_{run_id}"
    destination = f"dst_replace_{run_id}"

    with Given("two partitioned tables on one CAS pool"):
        create_cas_merge_tree_table(
            table_name=source, pool_prefix=pool_prefix, disk_name=disk_name
        )
        create_cas_merge_tree_table(
            table_name=destination, pool_prefix=pool_prefix, disk_name=disk_name
        )

    with When("I fill both tables with overlapping partitions"):
        insert_cas_partitions(
            table_name=source, partitions=(1, 2), rows_per_partition=5
        )
        insert_cas_partitions(
            table_name=destination, partitions=(1, 2), rows_per_partition=7
        )

    with And("the source and destination copies of partition 1 differ"):
        source_p1 = partition_checksum(node, source, 1)
        source_p2 = partition_checksum(node, source, 2)
        destination_p1 = partition_checksum(node, destination, 1)
        destination_p2 = partition_checksum(node, destination, 2)
        assert source_p1 != destination_p1, error(
            "REPLACE would pass even if it did nothing"
        )

    with Then("REPLACE PARTITION copies source partition 1 onto destination"):
        replace_partition_from(
            destination=destination, source=source, partition=1, node=node
        )
        assert partition_checksum(node, destination, 1) == source_p1, error()
        assert partition_checksum(node, destination, 2) == destination_p2, error()
        assert partition_checksum(node, source, 1) == source_p1, error(
            "REPLACE must not delete data from the source table"
        )
        assert partition_checksum(node, source, 2) == source_p2, error()
        for table_name in (source, destination):
            _assert_readable(node, table_name, disk_name)


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Transparency("1.0"),
    RQ_SRS_048_CAS_Partition_AlterAllowList("1.1"),
    RQ_SRS_048_CAS_Partition_AttachFrom("1.0"),
)
def attach_partition_from_same_cas_disk(self):
    """ATTACH PARTITION FROM between two MergeTree tables on the same CAS pool."""
    node = self.context.node
    run_id = getuid()
    pool_prefix = f"cas_attach_{run_id}"
    disk_name = f"cas_attach_{run_id}"
    source = f"src_attach_{run_id}"
    destination = f"dst_attach_{run_id}"

    with Given("source table with data and a destination that holds another partition"):
        create_cas_merge_tree_table(
            table_name=source, pool_prefix=pool_prefix, disk_name=disk_name
        )
        create_cas_merge_tree_table(
            table_name=destination, pool_prefix=pool_prefix, disk_name=disk_name
        )
        insert_cas_partitions(
            table_name=source, partitions=(1, 2), rows_per_partition=5
        )
        insert_cas_partitions(
            table_name=destination, partitions=(3,), rows_per_partition=4
        )

    with When("I ATTACH PARTITION 1 FROM the source"):
        source_p1 = partition_checksum(node, source, 1)
        source_p2 = partition_checksum(node, source, 2)
        destination_p3 = partition_checksum(node, destination, 3)
        attach_partition_from(
            destination=destination, source=source, partition=1, node=node
        )

    with Then("destination gains that partition and both tables keep the rest"):
        assert partition_checksum(node, destination, 1) == source_p1, error()
        assert partition_checksum(node, source, 1) == source_p1, error()
        assert partition_checksum(node, source, 2) == source_p2, error()
        assert partition_checksum(node, destination, 3) == destination_p3, error()
        assert _row_count(node, destination, 2) == "0", error()
        for table_name in (source, destination):
            _assert_readable(node, table_name, disk_name)


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Transparency("1.0"),
    RQ_SRS_048_CAS_Partition_AlterAllowList("1.1"),
    RQ_SRS_048_CAS_Partition_MoveToTable("1.0"),
)
def move_partition_to_table_same_cas_disk(self):
    """MOVE PARTITION TO TABLE between two MergeTree tables on the same CAS pool."""
    node = self.context.node
    run_id = getuid()
    pool_prefix = f"cas_move_{run_id}"
    disk_name = f"cas_move_{run_id}"
    source = f"src_move_{run_id}"
    destination = f"dst_move_{run_id}"

    with Given("two partitioned tables on one CAS pool"):
        create_cas_merge_tree_table(
            table_name=source, pool_prefix=pool_prefix, disk_name=disk_name
        )
        create_cas_merge_tree_table(
            table_name=destination, pool_prefix=pool_prefix, disk_name=disk_name
        )
        insert_cas_partitions(
            table_name=source, partitions=(1, 2), rows_per_partition=5
        )
        insert_cas_partitions(
            table_name=destination, partitions=(3,), rows_per_partition=4
        )

    with When("I MOVE PARTITION 1 from source to destination"):
        moved = partition_checksum(node, source, 1)
        kept = partition_checksum(node, source, 2)
        destination_p3 = partition_checksum(node, destination, 3)
        move_partition_to_table(
            source=source, destination=destination, partition=1, node=node
        )

    with Then("partition leaves the source and lands on the destination"):
        assert _row_count(node, source, 1) == "0", error()
        assert partition_checksum(node, source, 2) == kept, error()
        assert partition_checksum(node, destination, 1) == moved, error()
        assert partition_checksum(node, destination, 3) == destination_p3, error()
        assert _row_count(node, destination, 2) == "0", error()
        for table_name in (source, destination):
            _assert_readable(node, table_name, disk_name)


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Transparency("1.0"),
    RQ_SRS_048_CAS_Partition_AlterAllowList("1.1"),
    RQ_SRS_048_CAS_Partition_Detach("1.0"),
    RQ_SRS_048_CAS_Partition_Attach("1.0"),
    RQ_SRS_048_CAS_Partition_DetachAttach("1.0"),
)
def detach_attach_partition_same_cas_disk(self):
    """DETACH and ATTACH, by partition and by part, round-trip and survive restart.

    Each partition is two parts, so DETACH PARTITION and DETACH PART are
    different operations.
    """
    node = self.context.node
    run_id = getuid()
    pool_prefix = f"cas_detach_{run_id}"
    disk_name = f"cas_detach_{run_id}"
    table = f"detach_{run_id}"

    with Given("a partitioned CAS table with two parts in each partition"):
        create_cas_merge_tree_table(
            table_name=table, pool_prefix=pool_prefix, disk_name=disk_name
        )
        stop_merges(table_name=table, node=node)
        insert_cas_partitions(table_name=table, partitions=(1, 2), rows_per_partition=5)
        insert_cas_partitions(table_name=table, partitions=(1, 2), rows_per_partition=5)
        partition_one_parts = active_part_names(node, table, partition=1)
        partition_two_parts = active_part_names(node, table, partition=2)
        assert len(partition_one_parts) == 2, error(partition_one_parts)
        assert len(partition_two_parts) == 2, error(partition_two_parts)
        before = table_checksum(node, table)
        partition_one = partition_checksum(node, table, 1)
        partition_two = partition_checksum(node, table, 2)

    with When("I DETACH PARTITION 1"):
        detach_partition(table_name=table, partition=1, node=node)

    with Then("partition 1 is detached and partition 2 is untouched"):
        assert _row_count(node, table, 1) == "0", error()
        assert active_part_names(node, table, partition=1) == [], error()
        assert partition_checksum(node, table, 2) == partition_two, error()
        detached = detached_part_names(node, table, "1")
        assert sorted(detached) == sorted(partition_one_parts), error(
            f"detached {detached}, had {partition_one_parts}"
        )

    with When("I ATTACH PARTITION 1"):
        attach_partition(table_name=table, partition=1, node=node)

    with Then("the partition is active again and no longer detached"):
        assert partition_checksum(node, table, 1) == partition_one, error()
        assert table_checksum(node, table) == before, error()
        assert detached_part_names(node, table, "1") == [], error()

    with When("I DETACH one part of partition 2"):
        victim = partition_two_parts[0]
        survivor = partition_two_parts[1]
        detach_part(table_name=table, part_name=victim, node=node)

    with Then("the other part of partition 2 stays active"):
        assert active_part_names(node, table, partition=2) == [survivor], error()
        detached = detached_part_names(node, table, "2")
        assert detached == [victim], error(detached)
        assert _row_count(node, table, 2) == "5", error()

    with Then("ATTACH PART puts that part back"):
        attach_part(table_name=table, part_name=victim, node=node)
        assert partition_checksum(node, table, 2) == partition_two, error()
        assert detached_part_names(node, table, "2") == [], error()
        assert table_checksum(node, table) == before, error()

    with When("I restart the server"):
        restart_server(node=node)

    with Then("the attached data is still readable on the CAS disk"):
        assert table_checksum(node, table) == before, error()
        assert partition_checksum(node, table, 1) == partition_one, error()
        assert partition_checksum(node, table, 2) == partition_two, error()
        _assert_readable(node, table, disk_name)


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Transparency("1.0"),
    RQ_SRS_048_CAS_Partition_AlterAllowList("1.1"),
    RQ_SRS_048_CAS_Partition_Drop("1.0"),
    RQ_SRS_048_CAS_Partition_DropDetached("1.0"),
)
def drop_part_partition_and_detached(self):
    """DROP PART, DROP PARTITION, DROP DETACHED PART and DROP DETACHED PARTITION."""
    node = self.context.node
    run_id = getuid()
    pool_prefix = f"cas_drop_{run_id}"
    disk_name = f"cas_drop_{run_id}"
    table = f"drop_{run_id}"

    with Given("a CAS table with two parts in partition 1"):
        create_cas_merge_tree_table(
            table_name=table, pool_prefix=pool_prefix, disk_name=disk_name
        )
        stop_merges(table_name=table, node=node)
        insert_cas_partitions(table_name=table, partitions=(1,), rows_per_partition=5)
        insert_cas_partitions(table_name=table, partitions=(1,), rows_per_partition=5)
        insert_cas_partitions(table_name=table, partitions=(2,), rows_per_partition=5)
        parts = active_part_names(node, table, partition=1)
        assert len(parts) == 2, error(parts)
        partition_two = partition_checksum(node, table, 2)

    with When("I DROP one part of partition 1"):
        drop_part(table_name=table, part_name=parts[0], node=node)

    with Then("that part is gone and was not left detached"):
        assert active_part_names(node, table, partition=1) == [parts[1]], error()
        assert parts[0] not in detached_part_names(node, table), error()
        assert _row_count(node, table, 1) == "5", error()
        assert partition_checksum(node, table, 2) == partition_two, error()

    with When("I DROP PARTITION 1"):
        drop_partition(table_name=table, partition=1, node=node)

    with Then("partition 1 is gone and partition 2 remains"):
        assert _row_count(node, table, 1) == "0", error()
        assert active_part_names(node, table, partition=1) == [], error()
        assert partition_checksum(node, table, 2) == partition_two, error()

    with When("I detach two new parts and drop them from the detached namespace"):
        insert_cas_partitions(table_name=table, partitions=(1,), rows_per_partition=5)
        insert_cas_partitions(table_name=table, partitions=(1,), rows_per_partition=5)
        detached_before = active_part_names(node, table, partition=1)
        assert len(detached_before) == 2, error(detached_before)
        detach_partition(table_name=table, partition=1, node=node)
        assert sorted(detached_part_names(node, table, "1")) == sorted(
            detached_before
        ), error()
        drop_detached_part(table_name=table, part_name=detached_before[0], node=node)
        still_detached = detached_part_names(node, table, "1")
        assert still_detached == [detached_before[1]], error(still_detached)
        drop_detached_partition(table_name=table, partition=1, node=node)

    with Then("nothing of partition 1 remains to attach"):
        assert detached_part_names(node, table, "1") == [], error()
        # An empty ATTACH PARTITION is a no-op on current MergeTree. It must
        # not bring partition 1 back.
        attach_partition(table_name=table, partition=1, node=node, no_checks=True)
        assert detached_part_names(node, table, "1") == [], error()
        assert _row_count(node, table, 1) == "0", error()
        assert partition_checksum(node, table, 2) == partition_two, error()
        _assert_readable(node, table, disk_name)


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Transparency("1.0"),
    RQ_SRS_048_CAS_Partition_Drop("1.0"),
    RQ_SRS_048_CAS_GC_NoLoss("1.0"),
    RQ_SRS_048_CAS_GC_ReclaimAfterDrop("1.0"),
)
def drop_partition_eligible_for_gc(self):
    """DROP PARTITION removes the partition and leaves its blobs for GC.

    Partition 2 still owns its blob, so collection must not take it. After
    that partition is dropped too, collection reclaims the payload blobs.
    """
    node = self.context.node
    run_id = getuid()
    pool_prefix = f"cas_drop_gc_{run_id}"
    disk_name = f"cas_drop_gc_{run_id}"
    table = f"drop_gc_{run_id}"

    with Given("a CAS table with one incompressible part in each of two partitions"):
        create_cas_merge_tree_table(
            table_name=table,
            pool_prefix=pool_prefix,
            disk_name=disk_name,
            columns=PAYLOAD_COLUMNS,
        )
        stop_garbage_collection(disk=disk_name, nodes=[node])
        insert_cas_payload_rows(table_name=table, partition=1, node=node)
        insert_cas_payload_rows(table_name=table, partition=2, node=node)
        kept = _payload_partition_checksum(node, table, 2)
        blobs_before = _payload_blobs(pool_prefix)
        assert blobs_before >= 2, error(
            f"the two inserts published {blobs_before} payload blobs"
        )

    with When("I DROP PARTITION 1"):
        drop_partition(table_name=table, partition=1, node=node)

    with Then("the drop does not delete payload blobs itself"):
        assert _row_count(node, table, 1) == "0", error()
        assert _payload_partition_checksum(node, table, 2) == kept, error()
        blobs_after_drop = _payload_blobs(pool_prefix)
        assert blobs_after_drop == blobs_before, error(
            f"DROP PARTITION deleted payload blobs: {blobs_before} -> "
            f"{blobs_after_drop}"
        )

    with When("I collect garbage"):
        collect_garbage(disk=disk_name, nodes=[node], rounds=GC_ROUNDS)

    with Then("partition 2 is still readable and its blob is still in the pool"):
        assert _payload_partition_checksum(node, table, 2) == kept, error()
        blobs_after_gc = _payload_blobs(pool_prefix)
        assert 0 < blobs_after_gc < blobs_before, error(
            f"GC left {blobs_after_gc} payload blobs from {blobs_before}"
        )
        _assert_readable(node, table, disk_name)

    with When("I DROP PARTITION 2 and collect garbage again"):
        drop_partition(table_name=table, partition=2, node=node)
        assert _row_count(node, table) == "0", error()
        collect_garbage(disk=disk_name, nodes=[node], rounds=GC_ROUNDS)

    with Then("no payload blob remains"):
        assert _payload_blobs(pool_prefix) == 0, error()


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Transparency("1.0"),
    RQ_SRS_048_CAS_Partition_AlterAllowList("1.1"),
    RQ_SRS_048_CAS_Partition_DetachAttach("1.0"),
    RQ_SRS_048_CAS_Partition_AttachFrom("1.0"),
    RQ_SRS_048_CAS_Partition_Drop("1.0"),
)
def partition_all_same_cas_disk(self):
    """DROP, DETACH, ATTACH and ATTACH FROM accept PARTITION ALL."""
    node = self.context.node
    run_id = getuid()
    pool_prefix = f"cas_all_{run_id}"
    disk_name = f"cas_all_{run_id}"
    source = f"src_all_{run_id}"
    destination = f"dst_all_{run_id}"

    with Given("a partitioned CAS table and an empty table on the same disk"):
        create_cas_merge_tree_table(
            table_name=source, pool_prefix=pool_prefix, disk_name=disk_name
        )
        create_cas_merge_tree_table(
            table_name=destination, pool_prefix=pool_prefix, disk_name=disk_name
        )
        insert_cas_partitions(
            table_name=source, partitions=(1, 2), rows_per_partition=5
        )
        before = table_checksum(node, source)
        active = active_part_names(node, source)
        assert len(active) >= 2, error(active)

    with When("I DETACH PARTITION ALL"):
        detach_partition(table_name=source, partition="ALL", node=node)

    with Then("every part is detached and the table is empty"):
        assert _row_count(node, source) == "0", error()
        assert active_part_names(node, source) == [], error()
        assert sorted(detached_part_names(node, source)) == sorted(active), error(
            detached_part_names(node, source)
        )

    with When("I ATTACH PARTITION ALL"):
        attach_partition(table_name=source, partition="ALL", node=node)

    with Then("the table is restored and nothing stays detached"):
        assert table_checksum(node, source) == before, error()
        assert detached_part_names(node, source) == [], error()
        _assert_readable(node, source, disk_name)

    with When("I ATTACH PARTITION ALL FROM the source into the empty table"):
        attach_partition_from(
            destination=destination, source=source, partition="ALL", node=node
        )

    with Then("the destination matches the source and the source is unchanged"):
        assert table_checksum(node, destination) == before, error()
        assert table_checksum(node, source) == before, error()
        for table_name in (source, destination):
            _assert_readable(node, table_name, disk_name)

    with When("I DROP PARTITION ALL on the destination"):
        drop_partition(table_name=destination, partition="ALL", node=node)

    with Then("the destination is empty and the source is unchanged"):
        assert _row_count(node, destination) == "0", error()
        assert active_part_names(node, destination) == [], error()
        assert table_checksum(node, source) == before, error()
        _assert_readable(node, source, disk_name)


@TestFeature
@Name("partition")
def feature(self):
    """Same-disk partition operations on content-addressed storage."""
    Scenario(test=replace_partition_same_cas_disk)()
    Scenario(test=attach_partition_from_same_cas_disk)()
    Scenario(test=move_partition_to_table_same_cas_disk)()
    Scenario(test=detach_attach_partition_same_cas_disk)()
    Scenario(test=drop_part_partition_and_detached)()
    Scenario(test=drop_partition_eligible_for_gc)()
    Scenario(test=partition_all_same_cas_disk)()
