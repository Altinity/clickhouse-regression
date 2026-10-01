"""Projection ALTER TABLE scenarios for CAS MergeTree."""

from testflows.asserts import error
from testflows.core import *

from helpers.common import getuid
from cas.requirements.requirements import *
from cas.tests.steps import *


def projection_table(self, suffix):
    """Create and fill an isolated table for one projection ALTER scenario."""
    table_name = f"cas_alter_projection_{suffix}_{getuid()}"
    create_filled_alter_table(table_name=table_name)
    return table_name


PAYLOAD_BLOB_BYTES = 512 * 1024


def blob_total_bytes(snapshot):
    """Sum unique content-blob sizes in a pool snapshot."""
    return sum(size_in_bytes(snapshot[key]) for key in blob_keys(snapshot))


def payload_blob_count(snapshot):
    """Count unique content blobs large enough to be a payload column copy."""
    return sum(
        1
        for key in blob_keys(snapshot)
        if size_in_bytes(snapshot[key]) >= PAYLOAD_BLOB_BYTES
    )


def payload_projection_table(self, suffix):
    """Wide CAS table with a large incompressible payload, on its own pool."""
    table_name = f"cas_alter_projection_{suffix}_{getuid()}"
    pool_prefix = f"data/{table_name}"
    create_cas_merge_tree_table(
        table_name=table_name,
        columns="p UInt8, i UInt64, payload String",
        order_by="(p, i)",
        pool_prefix=pool_prefix,
    )
    self.context.node.query(
        f"ALTER TABLE {table_name} MODIFY SETTING "
        "min_bytes_for_wide_part = 0, min_rows_for_wide_part = 0"
    )
    return table_name, pool_prefix


def part_bytes_on_disk(node, table_name):
    """Logical on-disk size ClickHouse reports for active parts, including projections."""
    return int(
        node.query(
            "SELECT sum(bytes_on_disk) FROM system.parts "
            f"WHERE database = currentDatabase() AND table = '{table_name}' "
            "AND active"
        ).output.strip()
        or "0"
    )


@TestScenario
@Requirements(RQ_SRS_048_CAS_MergeTree_Alter_Projection("1.0"))
def add_materialize_drop(self):
    """ADD / MATERIALIZE / DROP PROJECTION round-trip on CAS."""
    table = projection_table(self, "add_drop")

    with When("I add and materialize an aggregate projection"):
        add_projection(
            table_name=table,
            definition=(
                "sum_by_partition "
                "(SELECT partition_column, sum(value) GROUP BY partition_column)"
            ),
        )
        materialize_projection(
            table_name=table, projection_name="sum_by_partition"
        )

    with Then("the projection is present and queries still match"):
        create_query = show_create_table(self.context.node, table)
        assert "PROJECTION sum_by_partition" in create_query, error(create_query)
        result = self.context.node.query(
            f"SELECT partition_column, sum(value) FROM {table} "
            f"GROUP BY partition_column ORDER BY partition_column"
        ).output.strip()
        assert result == "1\t10\n2\t10", error(result)

    with When("I drop the projection"):
        drop_projection(table_name=table, projection_name="sum_by_partition")

    with Then("the projection is gone"):
        create_query = show_create_table(self.context.node, table)
        assert "PROJECTION sum_by_partition" not in create_query, error(create_query)


@TestScenario
@Requirements(RQ_SRS_048_CAS_MergeTree_Alter_Projection("1.0"))
def clear_in_partition(self):
    """CLEAR PROJECTION IN PARTITION keeps the projection definition."""
    table = projection_table(self, "clear_partition")

    with When("I add, materialize, then clear the projection in one partition"):
        add_projection(
            table_name=table,
            definition=(
                "sum_by_partition "
                "(SELECT partition_column, sum(value) GROUP BY partition_column)"
            ),
        )
        materialize_projection(
            table_name=table, projection_name="sum_by_partition"
        )
        clear_projection(
            table_name=table, projection_name="sum_by_partition", partition=1
        )

    with Then("the projection definition remains"):
        create_query = show_create_table(self.context.node, table)
        assert "PROJECTION sum_by_partition" in create_query, error(create_query)
        result = self.context.node.query(f"SELECT count() FROM {table}").output.strip()
        assert result == "10", error(result)


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Alter_Projection("1.0"),
    RQ_SRS_048_CAS_MergeTree_Projections("1.0"),
    RQ_SRS_048_CAS_SharedPool_Deduplication("1.0"),
)
def same_as_table_shares_blobs(self):
    """Identity projection must reuse parent column blobs, not store a second copy.

    A projection is a nested MergeTree part inside the parent
    (``<part>/<name>.proj/`` keys in the same CAS manifest). ClickHouse still
    writes those files; CAS addresses them by content. If the projection is
    ``SELECT * ORDER BY`` the table key, the wide-part column blobs are the
    same bytes as the parent, so unique pool blob bytes must not grow by the
    payload size. ``bytes_on_disk`` may still look doubled — that is the
    logical part view, not unique objects in the pool.
    """
    node = self.context.node
    table, pool_prefix = payload_projection_table(self, "same_as_table")

    with When("I insert one wide part with an incompressible payload"):
        before_insert = cas_events_snapshot(node)
        insert_cas_payload_rows(table_name=table)
        insert_delta = cas_events_delta(before_insert, cas_events_snapshot(node))
        insert_puts = assert_blob_bodies_were_uploaded(delta=insert_delta)

    with And("the pool has settled after the insert"):
        after_insert = settled_pool_snapshot(pool_prefix=pool_prefix)
        insert_blob_bytes = blob_total_bytes(after_insert)
        insert_payload_blobs = payload_blob_count(after_insert)
        logical_before = part_bytes_on_disk(node, table)
        note(
            f"after insert: unique blob bytes={insert_blob_bytes}, "
            f"payload-sized blobs={insert_payload_blobs}, "
            f"bytes_on_disk={logical_before}, CASBlobPut={insert_puts}"
        )
        assert insert_payload_blobs == 1, error(
            f"expected the insert to publish exactly one payload-sized blob in "
            f"pool {pool_prefix}, found {insert_payload_blobs}: "
            f"{blob_keys(after_insert)}"
        )

    with When("I add and materialize a projection that matches the table"):
        before_proj = cas_events_snapshot(node)
        add_projection(
            table_name=table,
            definition="same_as_table (SELECT p, i, payload ORDER BY p, i)",
        )
        materialize_projection(table_name=table, projection_name="same_as_table")
        proj_delta = cas_events_delta(before_proj, cas_events_snapshot(node))

    with Then("the projection is present and the payload checksum still matches"):
        create_query = show_create_table(node, table)
        assert "PROJECTION same_as_table" in create_query, error(create_query)
        checksum = payload_table_checksum(node, table)
        assert checksum.startswith("64\t"), error(checksum)

    with And("unique CAS blobs did not grow by a second payload copy"):
        after_proj = settled_pool_snapshot(pool_prefix=pool_prefix)
        added_blob_bytes = blob_total_bytes(after_proj) - insert_blob_bytes
        payload_blobs = payload_blob_count(after_proj)
        logical_after = part_bytes_on_disk(node, table)
        puts = blob_body_puts(proj_delta)
        avoided = blob_puts_avoided_or_deduped(proj_delta)
        note(
            f"after identity projection: unique blob bytes added={added_blob_bytes}, "
            f"payload-sized blobs={payload_blobs}, "
            f"bytes_on_disk {logical_before} -> {logical_after}, "
            f"CASBlobPut={puts}, avoided/deduped={avoided}, delta={proj_delta}"
        )
        assert payload_blobs == insert_payload_blobs, error(
            f"identity projection left {payload_blobs} payload-sized blobs in the "
            f"pool where the insert alone left {insert_payload_blobs}, adding "
            f"{added_blob_bytes} unique blob bytes; a projection over the same rows "
            f"in the same order writes the same column bytes, so CAS should reuse "
            f"the parent blob instead of storing a second copy. "
            f"CASBlobPut={puts}, avoided/deduped={avoided}, delta={proj_delta}"
        )


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Alter_Projection("1.0"),
    RQ_SRS_048_CAS_MergeTree_Projections("1.0"),
    RQ_SRS_048_CAS_SharedPool_Deduplication("1.0"),
)
def different_order_is_second_copy(self):
    """A projection that reorders rows writes different column bytes, so CAS stores them.

    This is the control for ``same_as_table_shares_blobs``: if both scenarios
    added a payload-sized blob, the identity case is not sharing either. If
    only this one does, the parent and the identity projection really folded.
    """
    node = self.context.node
    table, pool_prefix = payload_projection_table(self, "reordered")

    with When("I insert one wide part with an incompressible payload"):
        insert_cas_payload_rows(table_name=table)

    with And("the pool has settled after the insert"):
        after_insert = settled_pool_snapshot(pool_prefix=pool_prefix)
        insert_blob_bytes = blob_total_bytes(after_insert)
        insert_payload_blobs = payload_blob_count(after_insert)
        assert insert_payload_blobs == 1, error(
            f"expected the insert to publish exactly one payload-sized blob in "
            f"pool {pool_prefix}, found {insert_payload_blobs}: "
            f"{blob_keys(after_insert)}"
        )

    with When("I add and materialize a projection that reorders by payload"):
        before_proj = cas_events_snapshot(node)
        add_projection(
            table_name=table,
            definition="by_payload (SELECT p, i, payload ORDER BY payload)",
        )
        materialize_projection(table_name=table, projection_name="by_payload")
        proj_delta = cas_events_delta(before_proj, cas_events_snapshot(node))

    with Then("the projection exists and rows still match"):
        create_query = show_create_table(node, table)
        assert "PROJECTION by_payload" in create_query, error(create_query)
        result = node.query(f"SELECT count() FROM {table}").output.strip()
        assert result == "64", error(result)

    with And("the reordered column files are a new unique payload in the pool"):
        after_proj = settled_pool_snapshot(pool_prefix=pool_prefix)
        added_blob_bytes = blob_total_bytes(after_proj) - insert_blob_bytes
        payload_blobs = payload_blob_count(after_proj)
        puts = blob_body_puts(proj_delta)
        avoided = blob_puts_avoided_or_deduped(proj_delta)
        note(
            f"after reordered projection: unique blob bytes added={added_blob_bytes}, "
            f"payload-sized blobs {insert_payload_blobs} -> {payload_blobs}, "
            f"CASBlobPut={puts}, avoided/deduped={avoided}, delta={proj_delta}"
        )
        assert payload_blobs > insert_payload_blobs, error(
            f"reordered projection left {payload_blobs} payload-sized blobs in the "
            f"pool, the same as the insert alone ({insert_payload_blobs}), adding "
            f"{added_blob_bytes} unique blob bytes; a different row order must "
            f"produce different column bytes and therefore a second physical copy, "
            f"so this scenario is no longer a control for the identity case. "
            f"CASBlobPut={puts}, avoided/deduped={avoided}, delta={proj_delta}"
        )


@TestFeature
@Name("projection")
def feature(self):
    """Projection ALTER TABLE operations on CAS."""
    for scenario in loads(current_module(), Scenario):
        scenario()
