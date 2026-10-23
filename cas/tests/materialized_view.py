"""Materialized views whose source, destination, or inner table is on CAS."""

from collections import namedtuple

from testflows.asserts import error
from testflows.core import *

from helpers.common import getuid
from cas.requirements.requirements import *
from cas.tests.steps import *


PayloadView = namedtuple(
    "PayloadView",
    "src dst view src_pool dst_pool src_disk dst_disk",
)

DOUBLED = "1\t20\n2\t40"
GC_ROUNDS = 4


def expected_disk(self, where):
    """Disk active parts should use for a ``local`` or ``cas`` table."""
    if where == "local":
        return "default"
    if where == "cas":
        return self.context.cas_disk_name
    fail(f"unknown storage {where!r}")


def inner_id_engine(self):
    """Inner-table ``ENGINE`` clause for an ``id, v`` view on the CAS policy."""
    return "ENGINE = MergeTree PARTITION BY tuple() ORDER BY id " + storage_settings(
        self
    )


def assert_rows(table_name, expected, node=None, settings=None):
    """``SELECT * FROM table ORDER BY id`` returns ``expected``."""
    assert_query_result(
        query=f"SELECT * FROM {table_name} ORDER BY id",
        expected=expected,
        node=node,
        settings=settings,
    )


# A lightweight update stores a patch part. ``apply_patch_parts = 0`` reads the
# part that was inserted, without that patch.
BASE_PART = [("apply_patch_parts", 0)]
BLOCK_NUMBER = [
    "enable_block_number_column = 1",
    "enable_block_offset_column = 1",
]


def assert_patch(table_name, patched, base, node=None):
    """``table_name`` reads ``patched``, and without its patch parts reads ``base``."""
    assert_rows(table_name, patched, node=node)
    assert_rows(table_name, base, node=node, settings=BASE_PART)


def skip_without_table_exchange():
    """Skip a full-refresh scenario where EXCHANGE TABLES loses metadata files."""
    with Given("the metadata filesystem can exchange tables"):
        works = table_exchange_works()
    if not works:
        skip("EXCHANGE TABLES loses a metadata file on this filesystem")


def cross_disk(self, source_where, destination_where):
    """Insert through a ``TO`` view and check rows and disk placement."""
    uid = getuid()
    src, dst, view = f"mv_src_{uid}", f"mv_dst_{uid}", f"mv_{uid}"
    label = {"local": "local", "cas": "CAS"}

    with Given(
        f"a {label[source_where]} source, a {label[destination_where]} destination, and a view"
    ):
        create_id_table(table_name=src, where=source_where)
        create_id_table(table_name=dst, where=destination_where)
        create_materialized_view(
            view_name=view,
            to_table=dst,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )

    with When("I insert into the source"):
        insert_values(table_name=src, values="(1, 10), (2, 20)")

    with Then("the source kept its rows and the destination has the doubled values"):
        assert_query_result(
            query=f"SELECT * FROM {src} ORDER BY id",
            expected="1\t10\n2\t20",
        )
        assert_query_result(
            query=f"SELECT * FROM {dst} ORDER BY id",
            expected=DOUBLED,
        )

    with And("each table's parts stayed on its own disk"):
        assert_active_parts_on_disk(
            table_name=src, disk_name=expected_disk(self, source_where)
        )
        assert_active_parts_on_disk(
            table_name=dst, disk_name=expected_disk(self, destination_where)
        )


def open_payload_view(self, suffix, select, shared_pool, extra_settings=None):
    """Create a payload source, destination, and ``TO`` view.

    ``select`` is a format string with ``{source}``. ``shared_pool`` puts both
    tables on one inline disk. Otherwise each table gets its own pool.
    """
    uid = getuid()
    src = f"mv_src_{suffix}_{uid}"
    dst = f"mv_dst_{suffix}_{uid}"
    view = f"mv_{suffix}_{uid}"

    if shared_pool:
        pool = f"data/mv_{suffix}_{uid}"
        disk = f"mv_{suffix}_{uid}"
        create_payload_table(
            table_name=src, pool_prefix=pool, disk_name=disk, extra_settings=extra_settings
        )
        create_payload_table(
            table_name=dst, pool_prefix=pool, disk_name=disk, extra_settings=extra_settings
        )
        src_pool = dst_pool = pool
        src_disk = dst_disk = disk
    else:
        src_pool = f"data/mv_src_{suffix}_{uid}"
        dst_pool = f"data/mv_dst_{suffix}_{uid}"
        src_disk = f"mv_src_{suffix}_{uid}"
        dst_disk = f"mv_dst_{suffix}_{uid}"
        create_payload_table(
            table_name=src,
            pool_prefix=src_pool,
            disk_name=src_disk,
            extra_settings=extra_settings,
        )
        create_payload_table(
            table_name=dst,
            pool_prefix=dst_pool,
            disk_name=dst_disk,
            extra_settings=extra_settings,
        )

    create_materialized_view(
        view_name=view,
        to_table=dst,
        select=select.format(source=src),
    )
    return PayloadView(src, dst, view, src_pool, dst_pool, src_disk, dst_disk)


def reject_drop(table_name, view_name):
    """Dropping ``table_name`` fails while ``view_name`` still references it.

    The check is off by default. ``check_referential_table_dependencies = 1``
    is what makes ClickHouse reject the drop, on CAS and on a local disk.
    """
    result = drop_table_result(
        table_name=table_name,
        settings=[("check_referential_table_dependencies", 1)],
    )
    assert result.exitcode != 0, error(result.output)
    assert view_name in result.output, error(result.output)


@TestScenario
@Name("local source, CAS destination")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_NotATableEngine("1.0"),
    RQ_SRS_048_CAS_MergeTree_InsertSelect("1.0"),
)
def local_source_cas_destination(self):
    """INSERT into a local MergeTree populates a CAS destination through a view."""
    cross_disk(self, "local", "cas")


@TestScenario
@Name("CAS source, local destination")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_NotATableEngine("1.0"),
    RQ_SRS_048_CAS_MergeTree_InsertSelect("1.0"),
)
def cas_source_local_destination(self):
    """INSERT into a CAS MergeTree populates a local destination through a view."""
    cross_disk(self, "cas", "local")


@TestScenario
@Name("CAS source, CAS destination")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_NotATableEngine("1.0"),
    RQ_SRS_048_CAS_MergeTree_InsertSelect("1.0"),
)
def cas_source_cas_destination(self):
    """INSERT into a CAS MergeTree populates another CAS table through a view."""
    cross_disk(self, "cas", "cas")


@TestScenario
@Name("inner table on CAS")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_NotATableEngine("1.0"),
)
def inner_table_on_cas(self):
    """A view with its own MergeTree engine stores parts on the CAS policy."""
    node = self.context.node
    uid = getuid()
    src, view = f"mv_src_{uid}", f"mv_{uid}"

    with Given("a local source and an inner-engine view on cas_policy"):
        create_id_table(table_name=src, where="local")
        create_materialized_view(
            view_name=view,
            engine=inner_id_engine(self),
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )

    with When("I insert into the source"):
        insert_values(table_name=src, values="(1, 10), (2, 20)")

    with Then("the view returns the transformed rows"):
        assert_query_result(
            query=f"SELECT * FROM {view} ORDER BY id",
            expected=DOUBLED,
        )

    with And("the inner MergeTree is on the CAS policy disk"):
        inner = inner_table_name(view_name=view)
        engine, policy = table_engine_and_policy(node, inner)
        assert engine == "MergeTree", error(engine)
        assert policy == CAS_POLICY, error(policy)
        assert_active_parts_on_disk(
            table_name=inner, disk_name=self.context.cas_disk_name
        )


@TestScenario
@Name("populate, then insert")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_InsertSelect("1.0"),
)
def populate_then_insert(self):
    """POPULATE backfills an inner CAS MergeTree, and a later insert appends one row.

    ``TO`` and ``POPULATE`` together are a syntax error. The view has to own
    its engine.
    """
    uid = getuid()
    src, view = f"mv_src_{uid}", f"mv_{uid}"

    with Given("a CAS source that already has rows"):
        create_id_table(table_name=src, where="cas")
        insert_values(table_name=src, values="(1, 10), (2, 20)")

    with When("I create an inner-engine view with POPULATE"):
        create_materialized_view(
            view_name=view,
            engine=inner_id_engine(self),
            populate=True,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )

    with Then("the view has the backfill on the CAS disk"):
        assert_query_result(
            query=f"SELECT * FROM {view} ORDER BY id",
            expected=DOUBLED,
        )
        inner = inner_table_name(view_name=view)
        assert_active_parts_on_disk(
            table_name=inner, disk_name=self.context.cas_disk_name
        )

    with When("I insert another source row"):
        insert_values(table_name=src, values="(3, 30)")

    with Then("the view gains only that row"):
        assert_query_result(
            query=f"SELECT * FROM {src} ORDER BY id",
            expected="1\t10\n2\t20\n3\t30",
        )
        assert_query_result(
            query=f"SELECT * FROM {view} ORDER BY id",
            expected="1\t20\n2\t40\n3\t60",
        )


@TestScenario
@Name("filtered select")
@Requirements(RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"))
def filtered_select(self):
    """A WHERE view writes the matching rows to a CAS destination."""
    uid = getuid()
    src, dst, view = f"mv_src_{uid}", f"mv_dst_{uid}", f"mv_{uid}"

    with Given("a CAS source, a CAS destination, and a view that keeps odd ids"):
        create_id_table(table_name=src, where="cas")
        create_id_table(table_name=dst, where="cas")
        create_materialized_view(
            view_name=view,
            to_table=dst,
            select=f"SELECT id, v * 2 AS v FROM {src} WHERE id % 2 = 1",
        )

    with When("I insert three source rows"):
        insert_values(table_name=src, values="(1, 10), (2, 20), (3, 30)")

    with Then("the destination has the odd ids only"):
        assert_query_result(
            query=f"SELECT * FROM {src} ORDER BY id",
            expected="1\t10\n2\t20\n3\t30",
        )
        assert_query_result(
            query=f"SELECT * FROM {dst} ORDER BY id",
            expected="1\t20\n3\t60",
        )
        assert_active_parts_on_disk(
            table_name=dst, disk_name=self.context.cas_disk_name
        )


@TestScenario
@Name("aggregating destination")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_Engines("1.0"),
)
def aggregating_destination(self):
    """A GROUP BY view stores aggregate states on an AggregatingMergeTree on CAS."""
    uid = getuid()
    src, dst, view = f"mv_src_{uid}", f"mv_dst_{uid}", f"mv_{uid}"

    with Given("a CAS source and an AggregatingMergeTree destination on CAS"):
        create_id_table(table_name=src, where="cas")
        create_cas_merge_tree_table(
            table_name=dst,
            columns="id UInt64, v AggregateFunction(sum, UInt64)",
            partition_by="tuple()",
            order_by="id",
            engine="AggregatingMergeTree",
        )
        create_materialized_view(
            view_name=view,
            to_table=dst,
            select=f"SELECT id, sumState(v) AS v FROM {src} GROUP BY id",
        )

    with When("I insert two blocks that share an id"):
        insert_values(table_name=src, values="(1, 10), (2, 20)")
        insert_values(table_name=src, values="(1, 5)")

    with Then("sumMerge reads the combined states from CAS"):
        assert_query_result(
            query=f"SELECT id, sumMerge(v) FROM {dst} GROUP BY id ORDER BY id",
            expected="1\t15\n2\t20",
        )
        assert_active_parts_on_disk(
            table_name=dst, disk_name=self.context.cas_disk_name
        )


@TestScenario
@Name("merge on the destination")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_Merge("1.0"),
)
def merge_on_the_destination(self):
    """Two view-written parts merge on the CAS destination and the rows stay put."""
    uid = getuid()
    src, dst, view = f"mv_src_{uid}", f"mv_dst_{uid}", f"mv_{uid}"

    with Given("a view onto a CAS destination that will not merge on insert"):
        create_id_table(table_name=src, where="cas")
        create_id_table(
            table_name=dst,
            where="cas",
            extra_settings=["optimize_on_insert = 0"],
        )
        create_materialized_view(
            view_name=view,
            to_table=dst,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        stop_merges(table_name=dst)

    with When("I insert twice"):
        insert_values(table_name=src, values="(1, 10)")
        insert_values(table_name=src, values="(2, 20)")

    with Then("the destination has two parts on CAS"):
        assert_active_part_count(table_name=dst, count=2)
        assert_active_parts_on_disk(
            table_name=dst, disk_name=self.context.cas_disk_name
        )

    with When("I merge those parts"):
        start_merges(table_name=dst)
        optimize_final(table_name=dst)

    with Then("one part remains and the rows are unchanged"):
        assert_active_part_count(table_name=dst, count=1)
        assert_query_result(
            query=f"SELECT * FROM {dst} ORDER BY id",
            expected=DOUBLED,
        )
        assert_active_parts_on_disk(
            table_name=dst, disk_name=self.context.cas_disk_name
        )


@TestScenario
@Name("source mutation stays on the source")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_Transparency("1.0"),
    RQ_SRS_048_CAS_MergeTree_Mutations("1.0"),
    RQ_SRS_048_CAS_MergeTree_LightweightDelete("1.0"),
)
def source_mutation_stays_on_the_source(self):
    """UPDATE and lightweight DELETE on the source leave the destination rows."""
    uid = getuid()
    src, dst, view = f"mv_src_{uid}", f"mv_dst_{uid}", f"mv_{uid}"

    with Given("a view from a CAS source to a CAS destination, already filled"):
        create_id_table(table_name=src, where="cas")
        create_id_table(table_name=dst, where="cas")
        create_materialized_view(
            view_name=view,
            to_table=dst,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        insert_values(table_name=src, values="(1, 10), (2, 20)")

    with When("I update one source row"):
        alter_update(table_name=src, assignments="v = v + 1", condition="id = 1")

    with Then("the source changed and the destination still has the inserted values"):
        assert_query_result(
            query=f"SELECT * FROM {src} ORDER BY id",
            expected="1\t11\n2\t20",
        )
        assert_query_result(
            query=f"SELECT * FROM {dst} ORDER BY id",
            expected=DOUBLED,
        )

    with When("I lightweight-delete the other source row"):
        lightweight_delete(table_name=src, condition="id = 2")

    with Then("the destination still has both rows"):
        assert_query_result(
            query=f"SELECT * FROM {src} ORDER BY id",
            expected="1\t11",
        )
        assert_query_result(
            query=f"SELECT * FROM {dst} ORDER BY id",
            expected=DOUBLED,
        )


@TestScenario
@Name("drop view, then source")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_Transparency("1.0"),
)
def drop_view_then_source(self):
    """Dependency checks block dropping either table. After the view is gone, the destination remains."""
    uid = getuid()
    src, dst, view = f"mv_src_{uid}", f"mv_dst_{uid}", f"mv_{uid}"

    with Given("a filled view between two CAS tables"):
        create_id_table(table_name=src, where="cas")
        create_id_table(table_name=dst, where="cas")
        create_materialized_view(
            view_name=view,
            to_table=dst,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        insert_values(table_name=src, values="(1, 10), (2, 20)")

    with When("I drop either table with referential checks enabled"):
        reject_drop(dst, view)
        reject_drop(src, view)

    with And("I drop the view and insert another source row"):
        drop_table(table_name=view)
        insert_values(table_name=src, values="(3, 30)")

    with Then("the new row stays in the source"):
        assert_query_result(
            query=f"SELECT * FROM {src} ORDER BY id",
            expected="1\t10\n2\t20\n3\t30",
        )
        assert_query_result(
            query=f"SELECT * FROM {dst} ORDER BY id",
            expected=DOUBLED,
        )

    with When("I drop the source"):
        drop_table(table_name=src)

    with Then("the destination is still readable on CAS"):
        assert_query_result(
            query=f"SELECT * FROM {dst} ORDER BY id",
            expected=DOUBLED,
        )
        assert_active_parts_on_disk(
            table_name=dst, disk_name=self.context.cas_disk_name
        )


@TestScenario
@Name("identity copy shares a blob")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_ObjectModel_Blobs("1.0"),
    RQ_SRS_048_CAS_SharedPool_Deduplication("1.0"),
    RQ_SRS_048_CAS_GC_NoLoss("1.0"),
    RQ_SRS_048_CAS_GC_ReclaimAfterDrop("1.0"),
)
def identity_copy_shares_a_blob(self):
    """An identity view reuses the source payload blob.

    Dropping the source leaves that blob in place while the destination reads.
    Dropping the destination lets garbage collection reclaim it.
    """
    node = self.context.node

    with Given("an identity view between two tables on one private pool"):
        opened = open_payload_view(
            self,
            "identity",
            "SELECT p, i, payload FROM {source}",
            shared_pool=True,
        )
        stop_garbage_collection(disk=opened.src_disk, nodes=[node])

    with When("I insert one wide part into the source"):
        insert_cas_payload_rows(table_name=opened.src)

    with Then("both tables match and the pool has one payload blob"):
        checksum = assert_payload_checksums_match(left=opened.src, right=opened.dst)
        assert_payload_blob_count(pool_prefix=opened.src_pool, count=1)

    with When("I drop the view and the source, then collect garbage"):
        drop_table(table_name=opened.view)
        drop_table(table_name=opened.src)
        collect_garbage(disk=opened.src_disk, nodes=[node], rounds=GC_ROUNDS)

    with Then("the destination still reads and the payload blob is still there"):
        remaining = payload_table_checksum(node, opened.dst)
        assert remaining == checksum, error(
            f"destination checksum after GC is {remaining}, was {checksum}"
        )
        assert_payload_blob_count(pool_prefix=opened.src_pool, count=1)

    with When("I drop the destination and collect garbage again"):
        drop_table(table_name=opened.dst)
        collect_garbage(disk=opened.src_disk, nodes=[node], rounds=GC_ROUNDS)

    with Then("the payload blob is gone"):
        assert_payload_blob_count(pool_prefix=opened.src_pool, count=0)


@TestScenario
@Name("transformed copy stores a second blob")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_ObjectModel_Blobs("1.0"),
)
def transformed_copy_stores_a_second_blob(self):
    """Reversing the payload writes different bytes, so the pool gains a blob."""
    node = self.context.node

    with Given("a reversing view between two tables on one private pool"):
        opened = open_payload_view(
            self,
            "reverse",
            "SELECT p, i, reverse(payload) AS payload FROM {source}",
            shared_pool=True,
        )

    with When("I insert one wide part into the source"):
        insert_cas_payload_rows(table_name=opened.src)

    with Then("the destination has the reversed payload and its own blob"):
        source_checksum = payload_table_checksum(node, opened.src)
        dest_checksum = payload_table_checksum(node, opened.dst)
        assert source_checksum != dest_checksum, error(
            f"reverse view left the payload unchanged: {dest_checksum}"
        )
        expected = node.query(
            "SELECT count(), sum(i), groupBitXor(i), "
            f"groupBitXor(cityHash64(reverse(payload))) FROM {opened.src}"
        ).output.strip()
        assert dest_checksum == expected, error(
            f"destination {dest_checksum}, reversed source {expected}"
        )
        assert_payload_blob_count(pool_prefix=opened.src_pool, count=2)


@TestScenario
@Name("cross-pool publish")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_Write_Publish("1.1"),
    RQ_SRS_048_CAS_GC_NoLoss("1.0"),
    RQ_SRS_048_CAS_GC_ReclaimAfterDrop("1.0"),
)
def cross_pool_publish(self):
    """A view whose destination is another pool publishes the payload there.

    Reclaiming the source pool leaves the destination pool's copy alone.
    """
    node = self.context.node

    with Given("an identity view across two private pools"):
        opened = open_payload_view(
            self,
            "xpool",
            "SELECT p, i, payload FROM {source}",
            shared_pool=False,
        )

    with When("I insert one wide part into the source"):
        insert_cas_payload_rows(table_name=opened.src)

    with Then("each pool has the payload blob and the rows match"):
        checksum = assert_payload_checksums_match(left=opened.src, right=opened.dst)
        assert_payload_blob_count(pool_prefix=opened.src_pool, count=1)
        assert_payload_blob_count(pool_prefix=opened.dst_pool, count=1)

    with When("I drop the view and the source and collect garbage on both pools"):
        drop_table(table_name=opened.view)
        drop_table(table_name=opened.src)
        collect_garbage(disk=opened.src_disk, nodes=[node], rounds=GC_ROUNDS)
        collect_garbage(disk=opened.dst_disk, nodes=[node], rounds=GC_ROUNDS)

    with Then("only the source pool lost its blob"):
        assert_payload_blob_count(pool_prefix=opened.src_pool, count=0)
        assert_payload_blob_count(pool_prefix=opened.dst_pool, count=1)
        remaining = payload_table_checksum(node, opened.dst)
        assert remaining == checksum, error(
            f"destination checksum after GC is {remaining}, was {checksum}"
        )
        assert_check_table(table_name=opened.dst)


@TestScenario
@Name("replicated view on every replica")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_Replicated("1.0"),
)
def replicated_view_on_every_replica(self):
    """An insert on one replica shows up in the destination on every replica."""
    node = self.context.node
    uid = getuid()
    src, dst, view = f"mv_src_{uid}", f"mv_dst_{uid}", f"mv_{uid}"

    with Given("replicated CAS tables and the view on every replica"):
        create_replicated_cas_table_on_cluster(
            table_name=src,
            columns=ID_COLUMNS,
            partition_by="tuple()",
            order_by="id",
        )
        create_replicated_cas_table_on_cluster(
            table_name=dst,
            columns=ID_COLUMNS,
            partition_by="tuple()",
            order_by="id",
        )
        create_materialized_view(
            view_name=view,
            to_table=dst,
            on_cluster=REPLICATED_CLUSTER,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )

    with When("I insert on the first replica"):
        insert_values(table_name=src, values="(1, 10), (2, 20)", node=node)

    with Then("every replica's destination has the transformed rows"):
        sync_replicas(table_name=dst)
        for replica in self.context.nodes:
            assert_query_result(
                query=f"SELECT * FROM {dst} ORDER BY id",
                expected=DOUBLED,
                node=replica,
            )


@TestScenario
@Name("chained and fan-out views")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_NotATableEngine("1.0"),
)
def chained_and_fan_out_views(self):
    """One insert feeds two views and a view on a view, across CAS and local disks."""
    uid = getuid()
    src = f"mv_src_{uid}"
    doubled, plus_one, chained = f"mv_x2_{uid}", f"mv_p1_{uid}", f"mv_x20_{uid}"

    with Given("a CAS source, two views from it, and a view on the first destination"):
        create_id_table(table_name=src, where="cas")
        create_id_table(table_name=doubled, where="cas")
        create_id_table(table_name=plus_one, where="local")
        create_id_table(table_name=chained, where="cas")
        create_materialized_view(
            view_name=f"mv_to_x2_{uid}",
            to_table=doubled,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        create_materialized_view(
            view_name=f"mv_to_p1_{uid}",
            to_table=plus_one,
            select=f"SELECT id, v + 1 AS v FROM {src}",
        )
        create_materialized_view(
            view_name=f"mv_to_x20_{uid}",
            to_table=chained,
            select=f"SELECT id, v * 10 AS v FROM {doubled}",
        )

    with When("I insert into the source with parallel view processing"):
        insert_values(
            table_name=src,
            values="(1, 10), (2, 20)",
            settings=[("parallel_view_processing", 1)],
        )

    with Then("every destination has its own transformation"):
        assert_rows(doubled, DOUBLED)
        assert_rows(plus_one, "1\t11\n2\t21")
        assert_rows(chained, "1\t200\n2\t400")

    with And("each destination stayed on its own disk"):
        for table_name in (src, doubled, chained):
            assert_active_parts_on_disk(
                table_name=table_name, disk_name=self.context.cas_disk_name
            )
        assert_active_parts_on_disk(table_name=plus_one, disk_name="default")


@TestScenario
@Name("view joins a CAS table")
@Requirements(RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"))
def view_joins_a_cas_table(self):
    """The view reads a second CAS table while the insert runs."""
    uid = getuid()
    src, names, dst = f"mv_src_{uid}", f"mv_names_{uid}", f"mv_dst_{uid}"

    with Given("a CAS source, a CAS lookup table, and a joining view"):
        create_id_table(table_name=src, where="cas")
        for table_name in (names, dst):
            create_cas_merge_tree_table(
                table_name=table_name,
                columns="id UInt64, name String",
                partition_by="tuple()",
                order_by="id",
            )
        insert_values(table_name=names, values="(1, 'one'), (2, 'two')")
        create_materialized_view(
            view_name=f"mv_{uid}",
            to_table=dst,
            select=(
                f"SELECT s.id AS id, n.name AS name FROM {src} AS s "
                f"INNER JOIN {names} AS n ON s.id = n.id"
            ),
        )

    with When("I insert ids with and without a match"):
        insert_values(table_name=src, values="(1, 1), (2, 2), (9, 9)")

    with Then("the destination has the matched names only"):
        assert_rows(dst, "1\tone\n2\ttwo")
        assert_active_parts_on_disk(
            table_name=dst, disk_name=self.context.cas_disk_name
        )


@TestScenario
@Name("multi-block insert select")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_InsertSelect("1.0"),
)
def multi_block_insert_select(self):
    """A large INSERT SELECT writes one destination part per source block."""
    uid = getuid()
    src, dst = f"mv_src_{uid}", f"mv_dst_{uid}"
    rows, block = 200000, 20000

    with Given("a view between two CAS tables that do not merge"):
        create_id_table(table_name=src, where="cas")
        create_id_table(table_name=dst, where="cas")
        create_materialized_view(
            view_name=f"mv_{uid}",
            to_table=dst,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        stop_merges(table_name=src)
        stop_merges(table_name=dst)

    with When(f"I insert {rows} rows in blocks of {block}"):
        insert_select(
            table_name=src,
            select=f"SELECT number, number FROM numbers({rows})",
            settings=[
                ("max_block_size", block),
                ("max_insert_block_size", block),
                ("min_insert_block_size_rows", 0),
                ("min_insert_block_size_bytes", 0),
            ],
        )

    with Then("the destination has every row, doubled"):
        total = rows * (rows - 1) // 2
        assert_query_result(
            query=f"SELECT count(), sum(v), uniqExact(id) FROM {dst}",
            expected=f"{rows}\t{2 * total}\t{rows}",
        )

    with And("both tables wrote the same number of parts, more than one"):
        node = self.context.node
        parts = {
            table_name: node.query(
                "SELECT count() FROM system.parts WHERE database = currentDatabase() "
                f"AND table = '{table_name}' AND active"
            ).output.strip()
            for table_name in (src, dst)
        }
        assert parts[src] == parts[dst], error(parts)
        assert int(parts[dst]) > 1, error(parts)
        assert_check_table(table_name=dst)


@TestScenario
@Name("concurrent inserts")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_InsertSelect("1.0"),
)
def concurrent_inserts(self):
    """Parallel inserts into a CAS source all reach the CAS destination."""
    uid = getuid()
    src, dst = f"mv_src_{uid}", f"mv_dst_{uid}"
    workers, rows = 8, 1000

    with Given("a view between two CAS tables"):
        create_id_table(table_name=src, where="cas")
        create_id_table(table_name=dst, where="cas")
        create_materialized_view(
            view_name=f"mv_{uid}",
            to_table=dst,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )

    with When(f"{workers} clients insert disjoint id ranges at once"):
        with Pool(workers) as executor:
            for worker in range(workers):
                Step(
                    name=f"worker {worker}",
                    test=insert_select,
                    parallel=True,
                    executor=executor,
                )(
                    table_name=src,
                    select=f"SELECT number + {worker * rows}, 1 FROM numbers({rows})",
                )
            join()

    with Then("the destination has every row exactly once"):
        total = workers * rows
        assert_query_result(
            query=f"SELECT count(), sum(v), uniqExact(id) FROM {dst}",
            expected=f"{total}\t{2 * total}\t{total}",
        )
        assert_check_table(table_name=dst)


@TestScenario
@Name("error in the view select")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_Transparency("1.0"),
)
def error_in_the_view_select(self):
    """A view that throws fails the insert, and both CAS tables stay usable.

    ClickHouse commits the source block before the view runs, so the source
    keeps the row on a local disk as well. With
    ``materialized_views_ignore_errors`` the insert succeeds instead.
    """
    uid = getuid()
    src, dst = f"mv_src_{uid}", f"mv_dst_{uid}"

    with Given("a view that throws when v is 99"):
        create_id_table(table_name=src, where="cas")
        create_id_table(table_name=dst, where="cas")
        create_materialized_view(
            view_name=f"mv_{uid}",
            to_table=dst,
            select=f"SELECT id, v + throwIf(v = 99) AS v FROM {src}",
        )
        insert_values(table_name=src, values="(1, 10)")

    with When("I insert a row that makes the view throw"):
        insert_values(
            table_name=src,
            values="(2, 99)",
            exitcode=139,
            message="DB::Exception: Value passed to 'throwIf' function is non-zero",
        )

    with Then("the source has the row and the destination does not"):
        assert_rows(src, "1\t10\n2\t99")
        assert_rows(dst, "1\t10")

    with When("I insert the same kind of row with view errors ignored"):
        insert_values(
            table_name=src,
            values="(3, 99)",
            settings=[("materialized_views_ignore_errors", 1)],
        )

    with And("I insert a row the view accepts"):
        insert_values(table_name=src, values="(4, 40)")

    with Then("only the accepted rows reached the destination"):
        assert_rows(src, "1\t10\n2\t99\n3\t99\n4\t40")
        assert_rows(dst, "1\t10\n4\t40")
        assert_check_table(table_name=src)
        assert_check_table(table_name=dst)


@TestScenario
@Name("retried insert is deduplicated in the view")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_Transparency("1.0"),
)
def retried_insert_is_deduplicated(self):
    """A retry with the same deduplication token writes nothing to either table."""
    uid = getuid()
    src, dst = f"mv_src_{uid}", f"mv_dst_{uid}"
    window = ["non_replicated_deduplication_window = 100"]

    with Given("two CAS tables with a deduplication window and a view"):
        create_id_table(table_name=src, where="cas", extra_settings=window)
        create_id_table(table_name=dst, where="cas", extra_settings=window)
        create_materialized_view(
            view_name=f"mv_{uid}",
            to_table=dst,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )

    with When("I insert the same block twice with one token"):
        for _ in range(2):
            insert_values(
                table_name=src,
                values="(1, 10), (2, 20)",
                settings=[("insert_deduplication_token", f"mv_{uid}")],
            )

    with Then("each table has the block once"):
        assert_rows(src, "1\t10\n2\t20")
        assert_rows(dst, DOUBLED)
        assert_active_part_count(table_name=dst, count=1)


@TestScenario
@Name("modify query")
@Requirements(RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"))
def modify_query(self):
    """ALTER TABLE ... MODIFY QUERY changes what later inserts write to CAS."""
    uid = getuid()
    src, dst, view = f"mv_src_{uid}", f"mv_dst_{uid}", f"mv_{uid}"

    with Given("a doubling view between two CAS tables, already used once"):
        create_id_table(table_name=src, where="cas")
        create_id_table(table_name=dst, where="cas")
        create_materialized_view(
            view_name=view,
            to_table=dst,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        insert_values(table_name=src, values="(1, 10)")

    with When("I change the view to triple and insert again"):
        modify_view_query(view_name=view, select=f"SELECT id, v * 3 AS v FROM {src}")
        insert_values(table_name=src, values="(2, 20)")

    with Then("the old row keeps the old result and the new row uses the new query"):
        assert_rows(dst, "1\t20\n2\t60")


@TestScenario
@Name("detach and attach the view")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_RestartDurability("1.0"),
)
def detach_and_attach_the_view(self):
    """A detached view skips inserts. After ATTACH its CAS inner table reads back."""
    uid = getuid()
    src, view = f"mv_src_{uid}", f"mv_{uid}"

    with Given("an inner-engine view on CAS with one row"):
        create_id_table(table_name=src, where="cas")
        create_materialized_view(
            view_name=view,
            engine=inner_id_engine(self),
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        insert_values(table_name=src, values="(1, 10)")

    with When("I detach the view, insert, and attach it again"):
        detach_table(table_name=view)
        insert_values(table_name=src, values="(2, 20)")
        attach_table(table_name=view)

    with Then("the view has only the row from before the detach"):
        assert_rows(view, "1\t20")

    with When("I insert after the attach"):
        insert_values(table_name=src, values="(3, 30)")

    with Then("the view gains that row and its inner table is still on CAS"):
        assert_rows(view, "1\t20\n3\t60")
        inner = inner_table_name(view_name=view)
        assert_active_parts_on_disk(
            table_name=inner, disk_name=self.context.cas_disk_name
        )
        assert_check_table(table_name=inner)


@TestScenario
@Name("rename the view")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_Rename("1.0"),
)
def rename_the_view(self):
    """Renaming an inner-engine view keeps its CAS rows and keeps it running.

    Renaming the source or a ``TO`` table breaks the view on a local disk too,
    so only the view itself is renamed.
    """
    uid = getuid()
    src, view, renamed = f"mv_src_{uid}", f"mv_{uid}", f"mv_renamed_{uid}"

    with Given("an inner-engine view on CAS with one row"):
        create_id_table(table_name=src, where="cas")
        create_materialized_view(
            view_name=view,
            engine=inner_id_engine(self),
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        insert_values(table_name=src, values="(1, 10)")
        inner = inner_table_name(view_name=view)

    try:
        with When("I rename the view and insert again"):
            rename_table(table_name=view, new_name=renamed)
            insert_values(table_name=src, values="(2, 20)")

        with Then("the renamed view has both rows from the same CAS inner table"):
            assert_rows(renamed, DOUBLED)
            assert inner_table_name(view_name=renamed) == inner, error()
            assert_active_parts_on_disk(
                table_name=inner, disk_name=self.context.cas_disk_name
            )
            assert_check_table(table_name=inner)
    finally:
        with Finally("I drop the renamed view"):
            drop_table(table_name=renamed)


@TestScenario
@Name("restart keeps view data")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_RestartDurability("1.0"),
)
def restart_keeps_view_data(self):
    """Parts written by a TO view and an inner-engine view survive a restart."""
    uid = getuid()
    src, dst = f"mv_src_{uid}", f"mv_dst_{uid}"
    to_view, inner_view = f"mv_to_{uid}", f"mv_inner_{uid}"

    with Given("a CAS source feeding a CAS TO table and an inner-engine view"):
        create_id_table(table_name=src, where="cas")
        create_id_table(table_name=dst, where="cas")
        create_materialized_view(
            view_name=to_view,
            to_table=dst,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        create_materialized_view(
            view_name=inner_view,
            engine=inner_id_engine(self),
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        insert_values(table_name=src, values="(1, 10), (2, 20)")

    with When("I restart the server"):
        restart_server()

    with Then("both destinations read back from CAS"):
        assert_rows(dst, DOUBLED)
        assert_rows(inner_view, DOUBLED)
        inner = inner_table_name(view_name=inner_view)
        for table_name in (dst, inner):
            assert_active_parts_on_disk(
                table_name=table_name, disk_name=self.context.cas_disk_name
            )
            assert_check_table(table_name=table_name)

    with When("I insert after the restart"):
        insert_values(table_name=src, values="(3, 30)")

    with Then("both views still propagate"):
        assert_rows(dst, "1\t20\n2\t40\n3\t60")
        assert_rows(inner_view, "1\t20\n2\t40\n3\t60")


@TestScenario
@Name("shared blob survives restart and GC")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_RestartDurability("1.0"),
    RQ_SRS_048_CAS_GC_NoLoss("1.0"),
)
def shared_blob_survives_restart_and_gc(self):
    """After a restart, GC still sees the destination's reference to the shared blob."""
    node = self.context.node

    with Given("an identity view on one pool, filled with one wide part"):
        opened = open_payload_view(
            self,
            "restart",
            "SELECT p, i, payload FROM {source}",
            shared_pool=True,
        )
        insert_cas_payload_rows(table_name=opened.src)
        checksum = assert_payload_checksums_match(left=opened.src, right=opened.dst)

    with When("I restart the server, drop the view and the source, and collect garbage"):
        restart_server()
        drop_table(table_name=opened.view)
        drop_table(table_name=opened.src)
        collect_garbage(disk=opened.src_disk, nodes=[node], rounds=GC_ROUNDS)

    with Then("the destination still reads the payload from the one blob"):
        remaining = payload_table_checksum(node, opened.dst)
        assert remaining == checksum, error(
            f"destination checksum after restart and GC is {remaining}, was {checksum}"
        )
        assert_payload_blob_count(pool_prefix=opened.src_pool, count=1)
        assert_check_table(table_name=opened.dst)


@TestScenario
@Name("summing and replacing destinations")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_Engines("1.0"),
    RQ_SRS_048_CAS_MergeTree_Merge("1.0"),
)
def summing_and_replacing_destinations(self):
    """Merges collapse view-written rows in Summing and Replacing tables on CAS."""
    uid = getuid()
    src, summing, replacing = f"mv_src_{uid}", f"mv_sum_{uid}", f"mv_rep_{uid}"

    with Given("a CAS source with views into Summing and Replacing tables on CAS"):
        create_id_table(table_name=src, where="cas")
        create_id_table(table_name=summing, where="cas", engine="SummingMergeTree")
        create_id_table(
            table_name=replacing, where="cas", engine="ReplacingMergeTree(v)"
        )
        for dst in (summing, replacing):
            create_materialized_view(
                view_name=f"mv_to_{dst}",
                to_table=dst,
                select=f"SELECT id, v FROM {src}",
            )

    with When("I insert two blocks that share id 1 and merge"):
        insert_values(table_name=src, values="(1, 10), (2, 20)")
        insert_values(table_name=src, values="(1, 5)")
        optimize_final(table_name=summing)
        optimize_final(table_name=replacing)

    with Then("Summing added the values and Replacing kept the larger version"):
        assert_rows(summing, "1\t15\n2\t20")
        assert_rows(replacing, "1\t10\n2\t20")
        for dst in (summing, replacing):
            assert_active_part_count(table_name=dst, count=1)
            assert_active_parts_on_disk(
                table_name=dst, disk_name=self.context.cas_disk_name
            )


@TestScenario
@Name("projection on the destination")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_Projections("1.0"),
)
def projection_on_the_destination(self):
    """View-written parts build the destination projection, before and after a merge."""
    node = self.context.node
    uid = getuid()
    src, dst = f"mv_src_{uid}", f"mv_dst_{uid}"
    by_value = f"SELECT v, count() FROM {dst} GROUP BY v ORDER BY v"
    force = [("force_optimize_projection", 1)]

    with Given("a view into a CAS table with an aggregate projection"):
        create_id_table(table_name=src, where="cas")
        create_id_table(
            table_name=dst,
            where="cas",
            columns=f"{ID_COLUMNS}, PROJECTION by_v (SELECT v, count() GROUP BY v)",
        )
        create_materialized_view(
            view_name=f"mv_{uid}",
            to_table=dst,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )

    with When("I insert two blocks"):
        insert_values(table_name=src, values="(1, 10), (2, 10), (3, 20)")
        insert_values(table_name=src, values="(4, 20)")

    with Then("the projection answers the aggregate"):
        assert_query_result(query=by_value, expected="20\t2\n40\t2", settings=force)
        projections = node.query(
            "SELECT count() FROM system.projection_parts "
            f"WHERE database = currentDatabase() AND table = '{dst}' AND active"
        ).output.strip()
        assert projections == "2", error(projections)

    with When("I merge the destination"):
        optimize_final(table_name=dst)

    with Then("the merged part still answers through the projection"):
        assert_query_result(query=by_value, expected="20\t2\n40\t2", settings=force)
        assert_check_table(table_name=dst)


@TestScenario
@Name("partition operations on the destination")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_Partition_DetachAttach("1.0"),
    RQ_SRS_048_CAS_Partition_MoveToTable("1.0"),
    RQ_SRS_048_CAS_Partition_Drop("1.0"),
)
def partition_operations_on_the_destination(self):
    """DETACH, ATTACH, MOVE and DROP PARTITION on a CAS destination with a live view."""
    uid = getuid()
    src, dst, other = f"mv_src_{uid}", f"mv_dst_{uid}", f"mv_other_{uid}"

    with Given("a view into a CAS destination partitioned by id parity"):
        create_id_table(table_name=src, where="cas")
        for table_name in (dst, other):
            create_id_table(table_name=table_name, where="cas", partition_by="id % 2")
        create_materialized_view(
            view_name=f"mv_{uid}",
            to_table=dst,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        insert_values(table_name=src, values="(1, 10), (2, 20), (3, 30)")

    with When("I detach the odd partition and insert another odd row"):
        detach_partition(table_name=dst, partition=1)
        insert_values(table_name=src, values="(5, 50)")

    with Then("the destination has the even row and the new odd row"):
        assert_rows(dst, "2\t40\n5\t100")

    with When("I attach the odd partition back"):
        attach_partition(table_name=dst, partition=1)

    with Then("all rows are back"):
        assert_rows(dst, "1\t20\n2\t40\n3\t60\n5\t100")

    with When("I move the even partition to another CAS table"):
        move_partition_to_table(source=dst, destination=other, partition=0)

    with Then("the even row moved"):
        assert_rows(dst, "1\t20\n3\t60\n5\t100")
        assert_rows(other, "2\t40")

    with When("I drop the odd partition and insert again"):
        drop_partition(table_name=dst, partition=1)
        insert_values(table_name=src, values="(7, 70)")

    with Then("the destination has only the new row"):
        assert_rows(dst, "7\t140")
        for table_name in (dst, other):
            assert_active_parts_on_disk(
                table_name=table_name, disk_name=self.context.cas_disk_name
            )
            assert_check_table(table_name=table_name)


@TestScenario
@Name("refreshable view replaces the destination")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_Rename("1.0"),
)
def refreshable_view_replaces_the_destination(self):
    """A refresh rewrites the CAS TO table from the source. Inserts alone do not."""
    uid = getuid()
    src, dst, view = f"mv_src_{uid}", f"mv_dst_{uid}", f"mv_{uid}"

    skip_without_table_exchange()

    with Given("a CAS source with rows and a refreshable view onto a CAS table"):
        create_id_table(table_name=src, where="cas")
        create_id_table(table_name=dst, where="cas")
        insert_values(table_name=src, values="(1, 10), (2, 20)")
        create_materialized_view(
            view_name=view,
            refresh="REFRESH EVERY 1 HOUR",
            to_table=dst,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        wait_view(view_name=view)

    with Then("the first refresh filled the destination"):
        assert_rows(dst, DOUBLED)

    with When("I insert into the source without refreshing"):
        insert_values(table_name=src, values="(3, 30)")

    with Then("the destination is unchanged"):
        assert_rows(dst, DOUBLED)

    with When("I refresh twice"):
        refresh_view(view_name=view)
        refresh_view(view_name=view)

    with Then("the destination has each source row once"):
        assert_rows(dst, "1\t20\n2\t40\n3\t60")
        assert_active_parts_on_disk(
            table_name=dst, disk_name=self.context.cas_disk_name
        )
        assert_check_table(table_name=dst)


@TestScenario
@Name("refreshable view appends to the destination")
@Requirements(RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"))
def refreshable_view_appends(self):
    """An APPEND refresh adds the whole result to the CAS TO table each time."""
    uid = getuid()
    src, dst, view = f"mv_src_{uid}", f"mv_dst_{uid}", f"mv_{uid}"

    with Given("a CAS source with rows and an APPEND refreshable view"):
        create_id_table(table_name=src, where="cas")
        create_id_table(table_name=dst, where="cas")
        insert_values(table_name=src, values="(1, 10), (2, 20)")
        create_materialized_view(
            view_name=view,
            refresh="REFRESH EVERY 1 HOUR APPEND",
            to_table=dst,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        wait_view(view_name=view)

    with When("I refresh once more"):
        refresh_view(view_name=view)

    with Then("the destination holds the result twice"):
        assert_rows(dst, "1\t20\n1\t20\n2\t40\n2\t40")
        assert_active_parts_on_disk(
            table_name=dst, disk_name=self.context.cas_disk_name
        )


@TestScenario
@Name("refreshable view with an inner CAS table")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_Rename("1.0"),
)
def refreshable_view_with_inner_table(self):
    """A refresh swaps in a new inner table on CAS with the current source rows."""
    uid = getuid()
    src, view = f"mv_src_{uid}", f"mv_{uid}"

    skip_without_table_exchange()

    with Given("a CAS source and a refreshable inner-engine view on CAS"):
        create_id_table(table_name=src, where="cas")
        insert_values(table_name=src, values="(1, 10), (2, 20)")
        create_materialized_view(
            view_name=view,
            refresh="REFRESH EVERY 1 HOUR",
            engine=inner_id_engine(self),
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        wait_view(view_name=view)

    with When("I insert into the source and refresh"):
        insert_values(table_name=src, values="(3, 30)")
        refresh_view(view_name=view)

    with Then("the view has every row once on a CAS inner table"):
        assert_rows(view, "1\t20\n2\t40\n3\t60")
        inner = inner_table_name(view_name=view)
        assert_active_parts_on_disk(
            table_name=inner, disk_name=self.context.cas_disk_name
        )
        assert_check_table(table_name=inner)


@TestScenario
@Name("refresh keeps one blob")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_SharedPool_Deduplication("1.0"),
    RQ_SRS_048_CAS_GC_NoLoss("1.0"),
)
def refresh_keeps_one_blob(self):
    """Each full refresh rewrites identical bytes, and GC keeps the one blob they share."""
    node = self.context.node
    uid = getuid()
    src, dst, view = f"mv_src_rfr_{uid}", f"mv_dst_rfr_{uid}", f"mv_rfr_{uid}"
    pool, disk = f"data/mv_rfr_{uid}", f"mv_rfr_{uid}"

    skip_without_table_exchange()

    with Given("a payload source and destination on one pool"):
        create_payload_table(table_name=src, pool_prefix=pool, disk_name=disk)
        create_payload_table(table_name=dst, pool_prefix=pool, disk_name=disk)
        insert_cas_payload_rows(table_name=src)

    with And("a refreshable identity view that has refreshed once"):
        create_materialized_view(
            view_name=view,
            refresh="REFRESH EVERY 1 HOUR",
            to_table=dst,
            select=f"SELECT p, i, payload FROM {src}",
        )
        wait_view(view_name=view)

    with When("I refresh twice and collect garbage"):
        refresh_view(view_name=view)
        refresh_view(view_name=view)
        collect_garbage(disk=disk, nodes=[node], rounds=GC_ROUNDS)

    with Then("both tables still match and share one payload blob"):
        assert_payload_checksums_match(left=src, right=dst)
        assert_payload_blob_count(pool_prefix=pool, count=1)
        assert_check_table(table_name=dst)


@TestScenario
@Name("fan-out and chained identity copies share a blob")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_SharedPool_Deduplication("1.0"),
    RQ_SRS_048_CAS_ObjectModel_Blobs("1.0"),
)
def fan_out_identity_copies_share_a_blob(self):
    """Two identity views and a view on a view all reuse the source payload blob."""
    node = self.context.node
    uid = getuid()
    pool, disk = f"data/mv_fan_{uid}", f"mv_fan_{uid}"
    src = f"mv_src_fan_{uid}"
    first, second, chained = f"mv_a_{uid}", f"mv_b_{uid}", f"mv_c_{uid}"

    with Given("four payload tables on one pool and the identity views between them"):
        for table_name in (src, first, second, chained):
            create_payload_table(table_name=table_name, pool_prefix=pool, disk_name=disk)
        for origin, target in ((src, first), (src, second), (first, chained)):
            create_materialized_view(
                view_name=f"mv_{origin}_{target}",
                to_table=target,
                select=f"SELECT p, i, payload FROM {origin}",
            )
        stop_garbage_collection(disk=disk, nodes=[node])

    with When("I insert one wide part into the source"):
        insert_cas_payload_rows(table_name=src)

    with Then("all four tables match and the pool has one payload blob"):
        for target in (first, second, chained):
            assert_payload_checksums_match(left=src, right=target)
        assert_payload_blob_count(pool_prefix=pool, count=1)


@TestScenario
@Name("inner table is reclaimed with the view")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_GC_ReclaimAfterDrop("1.0"),
    RQ_SRS_048_CAS_GC_NoLoss("1.0"),
)
def inner_table_is_reclaimed_with_the_view(self):
    """DROP VIEW drops its CAS inner table, and GC reclaims that pool only."""
    node = self.context.node
    uid = getuid()
    src, view = f"mv_src_inner_{uid}", f"mv_inner_{uid}"
    src_pool, src_disk = f"data/mv_src_inner_{uid}", f"mv_src_inner_{uid}"
    view_pool, view_disk = f"data/mv_inner_{uid}", f"mv_inner_{uid}"

    with Given("a payload source and an inner-engine view, each on its own pool"):
        create_payload_table(table_name=src, pool_prefix=src_pool, disk_name=src_disk)
        create_materialized_view(
            view_name=view,
            engine=payload_engine(self, pool_prefix=view_pool, disk_name=view_disk),
            select=f"SELECT p, i, payload FROM {src}",
        )

    with When("I insert one wide part"):
        insert_cas_payload_rows(table_name=src)

    with Then("the view matches the source and its pool has the payload blob"):
        checksum = assert_payload_checksums_match(left=src, right=view)
        assert_payload_blob_count(pool_prefix=view_pool, count=1)
        inner = inner_table_name(view_name=view)

    with When("I drop the view and collect garbage on its pool"):
        drop_table(table_name=view)
        collect_garbage(disk=view_disk, nodes=[node], rounds=GC_ROUNDS)

    with Then("the inner table and its blob are gone, and the source is intact"):
        assert_query_result(
            query=(
                "SELECT count() FROM system.tables "
                f"WHERE database = currentDatabase() AND name = '{inner}'"
            ),
            expected="0",
        )
        assert_payload_blob_count(pool_prefix=view_pool, count=0)
        assert_payload_blob_count(pool_prefix=src_pool, count=1)
        remaining = payload_table_checksum(node, src)
        assert remaining == checksum, error(
            f"source checksum after GC is {remaining}, was {checksum}"
        )


@TestScenario
@Name("truncate, then write the same bytes again")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_GC_NoLoss("1.0"),
    RQ_SRS_048_CAS_GC_ReclaimAfterDrop("1.0"),
    RQ_SRS_048_CAS_SharedPool_Deduplication("1.0"),
)
def truncate_then_write_the_same_bytes(self):
    """A blob GC has condemned but not deleted is safe to reference again.

    Truncating the destination leaves the source's shared blob. Truncating
    both makes the blob unreachable, and one GC round condemns it. The view
    then writes the same bytes again, and later rounds must keep them.
    """
    node = self.context.node

    with Given("an identity view on one pool with background GC stopped"):
        opened = open_payload_view(
            self,
            "same",
            "SELECT p, i, payload FROM {source}",
            shared_pool=True,
        )
        stop_garbage_collection(disk=opened.src_disk, nodes=[node])

    with When("I insert a deterministic payload"):
        insert_cas_payload_rows(table_name=opened.src, seed=1)
        checksum = assert_payload_checksums_match(left=opened.src, right=opened.dst)

    with And("I truncate the destination and collect garbage"):
        truncate_table(table_name=opened.dst)
        collect_garbage(disk=opened.src_disk, nodes=[node], rounds=GC_ROUNDS)

    with Then("the source still reads its payload from the one blob"):
        remaining = payload_table_checksum(node, opened.src)
        assert remaining == checksum, error(f"source {remaining}, was {checksum}")
        assert_payload_blob_count(pool_prefix=opened.src_pool, count=1)

    with When("I truncate the source and run one GC round"):
        truncate_table(table_name=opened.src)
        run_garbage_collection(disk=opened.src_disk)

    with And("I insert the same payload again and finish collecting garbage"):
        insert_cas_payload_rows(table_name=opened.src, seed=1)
        collect_garbage(disk=opened.src_disk, nodes=[node], rounds=GC_ROUNDS)

    with Then("both tables read the original payload back"):
        again = assert_payload_checksums_match(left=opened.src, right=opened.dst)
        assert again == checksum, error(f"rewritten {again}, original {checksum}")
        assert_payload_blob_count(pool_prefix=opened.src_pool, count=1)
        assert_check_table(table_name=opened.src)
        assert_check_table(table_name=opened.dst)


@TestScenario
@Name("garbage collection during view inserts")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_GC_NoLoss("1.0"),
)
def garbage_collection_during_view_inserts(self):
    """GC rounds that overlap inserts through an identity view lose no payload."""
    node = self.context.node
    batches, rows = 6, 64

    with Given("an identity view on one pool"):
        opened = open_payload_view(
            self,
            "gcrace",
            "SELECT p, i, payload FROM {source}",
            shared_pool=True,
        )

    with When("inserts and GC rounds run at the same time"):
        with Pool(2) as executor:
            Step(
                name="insert payload batches",
                test=insert_cas_payload_batches,
                parallel=True,
                executor=executor,
            )(table_name=opened.src, batches=batches, rows=rows)
            Step(
                name="collect garbage",
                test=collect_garbage,
                parallel=True,
                executor=executor,
            )(disk=opened.src_disk, nodes=[node], rounds=batches)
            join()

    with And("I collect garbage again after the inserts"):
        collect_garbage(disk=opened.src_disk, nodes=[node], rounds=GC_ROUNDS)

    with Then("both tables have every row and read their payload"):
        checksum = assert_payload_checksums_match(left=opened.src, right=opened.dst)
        assert checksum.split("\t")[0] == str(batches * rows), error(checksum)
        assert_check_table(table_name=opened.src)
        assert_check_table(table_name=opened.dst)


@TestScenario
@Name("replicated insert retry is deduplicated in the view")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_Replicated("1.0"),
)
def replicated_insert_retry_is_deduplicated(self):
    """The same block inserted on two replicas lands in the destination once."""
    uid = getuid()
    src, dst = f"mv_src_{uid}", f"mv_dst_{uid}"

    with Given("replicated CAS tables and the view on every replica"):
        for table_name in (src, dst):
            create_replicated_cas_table_on_cluster(
                table_name=table_name,
                columns=ID_COLUMNS,
                partition_by="tuple()",
                order_by="id",
            )
        create_materialized_view(
            view_name=f"mv_{uid}",
            to_table=dst,
            on_cluster=REPLICATED_CLUSTER,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )

    with When("I insert one block on the first replica and retry it on the second"):
        insert_values(table_name=src, values="(1, 10), (2, 20)")
        insert_values(
            table_name=src, values="(1, 10), (2, 20)", node=self.context.node2
        )

    with Then("every replica has the block once in both tables"):
        sync_replicas(table_name=src)
        sync_replicas(table_name=dst)
        for replica in self.context.nodes:
            assert_rows(src, "1\t10\n2\t20", node=replica)
            assert_rows(dst, DOUBLED, node=replica)


@TestScenario
@Name("replicated inner table")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_Replicated("1.0"),
)
def replicated_inner_table(self):
    """A view whose inner ReplicatedMergeTree is on CAS replicates its rows."""
    uid = getuid()
    src, view = f"mv_src_{uid}", f"mv_{uid}"

    with Given("a replicated CAS source and a view with a replicated CAS inner table"):
        create_replicated_cas_table_on_cluster(
            table_name=src,
            columns=ID_COLUMNS,
            partition_by="tuple()",
            order_by="id",
        )
        create_materialized_view(
            view_name=view,
            on_cluster=REPLICATED_CLUSTER,
            engine=(
                f"ENGINE = ReplicatedMergeTree('/clickhouse/tables/{view}_inner', "
                "'{replica}') PARTITION BY tuple() ORDER BY id "
                + storage_settings(self)
            ),
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )

    with When("I insert on the first replica"):
        insert_values(table_name=src, values="(1, 10), (2, 20)")

    with Then("every replica's view has the rows on CAS"):
        for replica in self.context.nodes:
            inner = inner_table_name(view_name=view, node=replica)
            sync_replica(table_name=quote_identifier(inner), node=replica)
            assert_rows(view, DOUBLED, node=replica)
            assert_active_parts_on_disk(
                table_name=inner, disk_name=self.context.cas_disk_name, node=replica
            )


@TestScenario
@Name("lightweight update on the source")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_PatchParts("1.0"),
)
def lightweight_update_on_the_source(self):
    """A lightweight UPDATE patches the CAS source and leaves the destination."""
    uid = getuid()
    src, dst = f"mv_src_{uid}", f"mv_dst_{uid}"

    with Given("a view from a CAS source to a CAS destination, already filled"):
        create_id_table(table_name=src, where="cas", extra_settings=BLOCK_NUMBER)
        create_id_table(table_name=dst, where="cas", extra_settings=BLOCK_NUMBER)
        create_materialized_view(
            view_name=f"mv_{uid}",
            to_table=dst,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        insert_values(table_name=src, values="(1, 10), (2, 20)")

    with When("I lightweight-update one source row"):
        lightweight_update(table_name=src, assignments="v = v + 1", condition="id = 1")

    with Then("the source is patched and the destination still has the inserted values"):
        assert_patch(src, "1\t11\n2\t20", "1\t10\n2\t20")
        assert_rows(dst, DOUBLED)
        assert_patch_part_count(table_name=src, count=1)
        assert_patch_part_count(table_name=dst, count=0)
        assert_active_parts_on_disk(
            table_name=src, disk_name=self.context.cas_disk_name
        )

    with When("I insert another source row"):
        insert_values(table_name=src, values="(3, 30)")

    with Then("the view writes that row and the patch stays on the source"):
        assert_patch(src, "1\t11\n2\t20\n3\t30", "1\t10\n2\t20\n3\t30")
        assert_rows(dst, "1\t20\n2\t40\n3\t60")


@TestScenario
@Name("lightweight update on the destination")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_PatchParts("1.0"),
    RQ_SRS_048_CAS_MergeTree_Alter_ApplyPatches("1.0"),
)
def lightweight_update_on_the_destination(self):
    """A lightweight UPDATE patches the CAS destination. APPLY PATCHES folds it in."""
    uid = getuid()
    src, dst = f"mv_src_{uid}", f"mv_dst_{uid}"
    patched = "1\t21\n2\t40\n3\t60"

    with Given("a filled view between two CAS tables"):
        create_id_table(table_name=src, where="cas", extra_settings=BLOCK_NUMBER)
        create_id_table(table_name=dst, where="cas", extra_settings=BLOCK_NUMBER)
        create_materialized_view(
            view_name=f"mv_{uid}",
            to_table=dst,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        insert_values(table_name=src, values="(1, 10), (2, 20)")

    with When("I lightweight-update one destination row"):
        lightweight_update(table_name=dst, assignments="v = v + 1", condition="id = 1")

    with Then("the destination is patched and the source is unchanged"):
        assert_rows(src, "1\t10\n2\t20")
        assert_patch(dst, "1\t21\n2\t40", DOUBLED)
        assert_patch_part_count(table_name=dst, count=1)
        assert_active_parts_on_disk(
            table_name=dst, disk_name=self.context.cas_disk_name
        )

    with When("I insert another source row"):
        insert_values(table_name=src, values="(3, 30)")

    with Then("the new row arrives unpatched"):
        assert_patch(dst, patched, "1\t20\n2\t40\n3\t60")

    with When("I apply the patches"):
        apply_patches(table_name=dst)

    with Then("the patched values are in the data part"):
        assert_patch_part_count(table_name=dst, count=0)
        assert_rows(dst, patched, settings=BASE_PART)
        assert_active_parts_on_disk(
            table_name=dst, disk_name=self.context.cas_disk_name
        )
        assert_check_table(table_name=dst)


@TestScenario
@Name("lightweight update on the inner table")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_PatchParts("1.0"),
    RQ_SRS_048_CAS_MergeTree_Alter_ApplyPatches("1.0"),
)
def lightweight_update_on_the_inner_table(self):
    """A lightweight UPDATE patches the CAS inner table of a view."""
    uid = getuid()
    src, view = f"mv_src_{uid}", f"mv_{uid}"
    patched = "1\t21\n2\t40"

    with Given("an inner-engine view on CAS with two rows"):
        create_id_table(table_name=src, where="cas")
        create_materialized_view(
            view_name=view,
            engine=(
                inner_id_engine(self)
                + ", enable_block_number_column = 1, enable_block_offset_column = 1"
            ),
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        insert_values(table_name=src, values="(1, 10), (2, 20)")
        inner = inner_table_name(view_name=view)

    with When("I lightweight-update one row of the inner table"):
        lightweight_update(
            table_name=quote_identifier(inner),
            assignments="v = v + 1",
            condition="id = 1",
        )

    with Then("the view reads the patch and the inserted part is unchanged"):
        assert_patch(view, patched, DOUBLED)
        assert_patch_part_count(table_name=inner, count=1)
        assert_active_parts_on_disk(
            table_name=inner, disk_name=self.context.cas_disk_name
        )

    with When("I apply the patches"):
        apply_patches(table_name=quote_identifier(inner))

    with Then("the view reads the patched values from the data part"):
        assert_patch_part_count(table_name=inner, count=0)
        assert_rows(view, patched, settings=BASE_PART)
        assert_check_table(table_name=inner)


@TestScenario
@Name("patch leaves the shared blob")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_PatchParts("1.0"),
    RQ_SRS_048_CAS_MergeTree_Alter_ApplyPatches("1.0"),
    RQ_SRS_048_CAS_ObjectModel_Blobs("1.0"),
    RQ_SRS_048_CAS_GC_NoLoss("1.0"),
)
def patch_leaves_the_shared_blob(self):
    """Patching the destination does not rewrite the payload blob it shares.

    The inserted part still holds the original bytes. APPLY PATCHES writes
    the patched column as its own blob and leaves the source reading the
    original one.
    """
    node = self.context.node

    with Given("an identity view on one pool, with background GC stopped"):
        opened = open_payload_view(
            self,
            "patch",
            "SELECT p, i, payload FROM {source}",
            shared_pool=True,
            extra_settings=BLOCK_NUMBER,
        )
        stop_garbage_collection(disk=opened.src_disk, nodes=[node])

    with When("I insert one wide part"):
        insert_cas_payload_rows(table_name=opened.src, seed=1)

    with Then("both tables share one payload blob"):
        checksum = assert_payload_checksums_match(left=opened.src, right=opened.dst)
        assert_payload_blob_count(pool_prefix=opened.src_pool, count=1)

    with When("I lightweight-update one destination payload"):
        lightweight_update(
            table_name=opened.dst,
            assignments="payload = 'patched'",
            condition="i = 0",
        )

    with Then("the inserted part is untouched and the source still reads it"):
        base = payload_table_checksum(node, opened.dst, settings=BASE_PART)
        assert base == checksum, error(f"base part {base}, inserted {checksum}")
        source = payload_table_checksum(node, opened.src)
        assert source == checksum, error(f"source {source}, inserted {checksum}")
        patched = payload_table_checksum(node, opened.dst)
        assert patched != checksum, error("patch did not change the destination")
        assert_patch_part_count(table_name=opened.dst, count=1)
        assert_payload_blob_count(pool_prefix=opened.src_pool, count=1)

    with When("I collect garbage and apply the patches"):
        collect_garbage(disk=opened.src_disk, nodes=[node], rounds=GC_ROUNDS)
        apply_patches(table_name=opened.dst)
        collect_garbage(disk=opened.src_disk, nodes=[node], rounds=GC_ROUNDS)

    with Then("the source keeps the original blob and the destination has its own"):
        source = payload_table_checksum(node, opened.src)
        assert source == checksum, error(f"source after apply {source}, was {checksum}")
        materialized = payload_table_checksum(node, opened.dst, settings=BASE_PART)
        assert materialized == patched, error(
            f"materialized {materialized}, patched {patched}"
        )
        assert_patch_part_count(table_name=opened.dst, count=0)
        assert_payload_blob_count(pool_prefix=opened.src_pool, count=2)
        assert_check_table(table_name=opened.src)
        assert_check_table(table_name=opened.dst)


@TestScenario
@Name("patch survives restart")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_PatchParts("1.0"),
    RQ_SRS_048_CAS_MergeTree_RestartDurability("1.0"),
)
def patch_survives_restart(self):
    """A patch part written to a CAS destination is still applied after restart."""
    uid = getuid()
    src, dst = f"mv_src_{uid}", f"mv_dst_{uid}"

    with Given("a filled view and a lightweight update of the destination"):
        create_id_table(table_name=src, where="cas", extra_settings=BLOCK_NUMBER)
        create_id_table(table_name=dst, where="cas", extra_settings=BLOCK_NUMBER)
        create_materialized_view(
            view_name=f"mv_{uid}",
            to_table=dst,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        insert_values(table_name=src, values="(1, 10), (2, 20)")
        lightweight_update(table_name=dst, assignments="v = v + 1", condition="id = 1")

    with When("I restart the server"):
        restart_server()

    with Then("the patch is still there and the inserted part is unchanged"):
        assert_patch(dst, "1\t21\n2\t40", DOUBLED)
        assert_patch_part_count(table_name=dst, count=1)
        assert_active_parts_on_disk(
            table_name=dst, disk_name=self.context.cas_disk_name
        )
        assert_check_table(table_name=dst)

    with When("I apply the patches"):
        apply_patches(table_name=dst)

    with Then("the data part has the patched values"):
        assert_patch_part_count(table_name=dst, count=0)
        assert_rows(dst, "1\t21\n2\t40", settings=BASE_PART)


@TestScenario
@Name("replicated lightweight update")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_PatchParts("1.0"),
    RQ_SRS_048_CAS_MergeTree_Replicated("1.0"),
)
def replicated_lightweight_update(self):
    """A lightweight UPDATE on one replica is visible on every replica."""
    uid = getuid()
    src, dst = f"mv_src_{uid}", f"mv_dst_{uid}"

    with Given("replicated CAS tables, a view on every replica, and one insert"):
        for table_name in (src, dst):
            create_replicated_cas_table_on_cluster(
                table_name=table_name,
                columns=ID_COLUMNS,
                partition_by="tuple()",
                order_by="id",
                extra_settings=BLOCK_NUMBER,
            )
        create_materialized_view(
            view_name=f"mv_{uid}",
            to_table=dst,
            on_cluster=REPLICATED_CLUSTER,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        insert_values(table_name=src, values="(1, 10), (2, 20)")
        sync_replicas(table_name=dst)

    with When("I lightweight-update the destination on the first replica"):
        lightweight_update(table_name=dst, assignments="v = v + 1", condition="id = 1")
        sync_replicas(table_name=dst)

    with Then("every replica reads the patch and still has the inserted part"):
        for replica in self.context.nodes:
            assert_patch(dst, "1\t21\n2\t40", DOUBLED, node=replica)
            assert_patch_part_count(table_name=dst, count=1, node=replica)
            assert_active_parts_on_disk(
                table_name=dst, disk_name=self.context.cas_disk_name, node=replica
            )


@TestScenario
@Name("distributed insert feeds every shard's view")
@Requirements(
    RQ_SRS_048_CAS_MergeTree_MaterializedView("1.0"),
    RQ_SRS_048_CAS_MergeTree_InsertSelect("1.0"),
)
def distributed_insert_feeds_every_shard(self):
    """Rows routed by a Distributed table go through each shard's view onto CAS."""
    uid = getuid()
    src, dst, dist = f"mv_src_{uid}", f"mv_dst_{uid}", f"mv_dist_{uid}"
    rows = 30

    with Given("CAS source and destination on every shard, a view, and a Distributed table"):
        for table_name in (src, dst):
            create_sharded_local_cas_tables(
                table_name=table_name,
                columns=ID_COLUMNS,
                partition_by="tuple()",
                order_by="id",
            )
        create_materialized_view(
            view_name=f"mv_{uid}",
            to_table=dst,
            on_cluster=SHARDED_CLUSTER,
            select=f"SELECT id, v * 2 AS v FROM {src}",
        )
        create_distributed_over_cas(
            distributed_table_name=dist, local_table_name=src, sharding_key="id"
        )

    with When(f"I insert {rows} rows through the Distributed table"):
        insert_into_distributed(
            table_name=dist, select=f"SELECT number, number FROM numbers({rows})"
        )

    with Then("each shard's destination mirrors its own source"):
        for shard in self.context.nodes:
            source_rows = shard.query(
                f"SELECT count(), sum(v) * 2 FROM {src}"
            ).output.strip()
            assert not source_rows.startswith("0\t"), error(
                f"{shard.name} got no rows"
            )
            assert_query_result(
                query=f"SELECT count(), sum(v) FROM {dst}",
                expected=source_rows,
                node=shard,
            )
            assert_active_parts_on_disk(
                table_name=dst, disk_name=self.context.cas_disk_name, node=shard
            )

    with And("the shards together have every row"):
        assert_query_result(
            query=(
                f"SELECT count(), sum(v) FROM "
                f"cluster('{SHARDED_CLUSTER}', currentDatabase(), {dst})"
            ),
            expected=f"{rows}\t{rows * (rows - 1)}",
        )


@TestFeature
@Name("materialized view")
def feature(self):
    """Materialized views against content-addressed storage."""
    Scenario(run=local_source_cas_destination)
    Scenario(run=cas_source_local_destination)
    Scenario(run=cas_source_cas_destination)
    Scenario(run=inner_table_on_cas)
    Scenario(run=populate_then_insert)
    Scenario(run=filtered_select)
    Scenario(run=aggregating_destination)
    Scenario(run=merge_on_the_destination)
    Scenario(run=source_mutation_stays_on_the_source)
    Scenario(run=drop_view_then_source)
    Scenario(run=identity_copy_shares_a_blob)
    Scenario(run=transformed_copy_stores_a_second_blob)
    Scenario(run=cross_pool_publish)
    Scenario(run=replicated_view_on_every_replica)
    Scenario(run=chained_and_fan_out_views)
    Scenario(run=view_joins_a_cas_table)
    Scenario(run=multi_block_insert_select)
    Scenario(run=concurrent_inserts)
    Scenario(run=error_in_the_view_select)
    Scenario(run=retried_insert_is_deduplicated)
    Scenario(run=modify_query)
    Scenario(run=detach_and_attach_the_view)
    Scenario(run=rename_the_view)
    Scenario(run=restart_keeps_view_data)
    Scenario(run=shared_blob_survives_restart_and_gc)
    Scenario(run=summing_and_replacing_destinations)
    Scenario(run=projection_on_the_destination)
    Scenario(run=partition_operations_on_the_destination)
    Scenario(run=refreshable_view_replaces_the_destination)
    Scenario(run=refreshable_view_appends)
    Scenario(run=refreshable_view_with_inner_table)
    Scenario(run=refresh_keeps_one_blob)
    Scenario(run=fan_out_identity_copies_share_a_blob)
    Scenario(run=inner_table_is_reclaimed_with_the_view)
    Scenario(run=truncate_then_write_the_same_bytes)
    Scenario(run=garbage_collection_during_view_inserts)
    Scenario(run=replicated_insert_retry_is_deduplicated)
    Scenario(run=replicated_inner_table)
    Scenario(run=lightweight_update_on_the_source)
    Scenario(run=lightweight_update_on_the_destination)
    Scenario(run=lightweight_update_on_the_inner_table)
    Scenario(run=patch_leaves_the_shared_blob)
    Scenario(run=patch_survives_restart)
    Scenario(run=replicated_lightweight_update)
    Scenario(run=distributed_insert_feeds_every_shard)
