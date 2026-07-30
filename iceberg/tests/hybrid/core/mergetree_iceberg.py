from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.tables import create_table

from iceberg.tests.export_partition.steps.iceberg_destination import (
    create_iceberg_s3_destination,
)
from iceberg.tests.export_partition.steps.export_operations import (
    insert_into_iceberg_destination,
)

from iceberg.tests.hybrid.core.common import (
    ALL_ROWS,
    COLUMNS,
    COLUMNS_SQL,
    LEFT_PREDICATE,
    RIGHT_PREDICATE,
    PREFER_LOCALHOST,
    FORCE_REMOTE,
    assert_hybrid_matches_reference,
    cluster_all_tf,
    create_mergetree_segment,
    fingerprint_sql,
    settings_clause,
    values_sql,
)


@TestStep(Given)
def create_cluster_mt_iceberg_hybrid(
    self,
    minio_root_user,
    minio_root_password,
    left_pred=LEFT_PREDICATE,
    right_pred=RIGHT_PREDICATE,
):
    """cluster('all', MT) hot segment + IcebergS3 cold segment."""
    node = self.context.node

    with By("create MergeTree on all shards via ON CLUSTER (data on initiator only)"):
        left = create_mergetree_segment(
            cluster="all",
            seed_all_nodes=False,
            rows=ALL_ROWS,
        )

    with By("create IcebergS3 destination and seed cold+hot rows"):
        iceberg = create_iceberg_s3_destination(
            columns=COLUMNS_SQL,
            partition_by="",  # Iceberg does not support toYYYYMM(...) partitioning
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        insert_into_iceberg_destination(
            destination=iceberg,
            values=values_sql(ALL_ROWS),
        )

    hybrid = f"hybrid_{getuid()}"
    left_tf = cluster_all_tf(left)

    with By("create Hybrid cluster(MT) + IcebergS3"):
        create_table(
            name=hybrid,
            engine=f"Hybrid({left_tf}, {left_pred}, {iceberg}, {right_pred})",
            columns=COLUMNS,
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    return {
        "hybrid": hybrid,
        "left": left,
        "right": iceberg,
        "left_from": left_tf,
        "right_from": iceberg,
        "left_pred": left_pred,
        "right_pred": right_pred,
    }


@TestScenario
@Name("cluster MergeTree Iceberg prefer localhost")
def cluster_mergetree_iceberg_prefer_localhost(
    self, minio_root_user, minio_root_password
):
    """cluster(MT)+IcebergS3 fingerprint and filters with prefer_localhost_replica=1."""
    with Given("Hybrid cluster(MT) + IcebergS3"):
        ctx = create_cluster_mt_iceberg_hybrid(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("full scan fingerprint"):
        assert_hybrid_matches_reference(
            hybrid_table=ctx["hybrid"],
            left_from=ctx["left_from"],
            right_from=ctx["right_from"],
            left_pred=ctx["left_pred"],
            right_pred=ctx["right_pred"],
            settings_row=PREFER_LOCALHOST,
        )

    with And("hot-only filter"):
        assert_hybrid_matches_reference(
            hybrid_table=ctx["hybrid"],
            left_from=ctx["left_from"],
            right_from=ctx["right_from"],
            left_pred=ctx["left_pred"],
            right_pred=ctx["right_pred"],
            where="date_col >= '2025-06-01'",
            settings_row=PREFER_LOCALHOST,
        )

    with And("cold-only filter"):
        assert_hybrid_matches_reference(
            hybrid_table=ctx["hybrid"],
            left_from=ctx["left_from"],
            right_from=ctx["right_from"],
            left_pred=ctx["left_pred"],
            right_pred=ctx["right_pred"],
            where="date_col < '2025-01-01'",
            settings_row=PREFER_LOCALHOST,
        )


@TestScenario
@Name("cluster MergeTree Iceberg force remote")
def cluster_mergetree_iceberg_force_remote(self, minio_root_user, minio_root_password):
    """cluster(MT)+IcebergS3 with prefer_localhost_replica=0."""
    with Given("Hybrid cluster(MT) + IcebergS3"):
        ctx = create_cluster_mt_iceberg_hybrid(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("full scan fingerprint"):
        assert_hybrid_matches_reference(
            hybrid_table=ctx["hybrid"],
            left_from=ctx["left_from"],
            right_from=ctx["right_from"],
            left_pred=ctx["left_pred"],
            right_pred=ctx["right_pred"],
            settings_row=FORCE_REMOTE,
        )


@TestScenario
@Name("cluster MergeTree Iceberg aggregations")
def cluster_mergetree_iceberg_aggregations(self, minio_root_user, minio_root_password):
    """count / GROUP BY on cluster(MT)+Iceberg match UNION ALL reference."""
    node = self.context.node
    with Given("Hybrid cluster(MT) + IcebergS3"):
        ctx = create_cluster_mt_iceberg_hybrid(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    clause = settings_clause(PREFER_LOCALHOST)
    ref = (
        f"(SELECT id, value, date_col FROM {ctx['left_from']} WHERE {ctx['left_pred']} "
        f"UNION ALL "
        f"SELECT id, value, date_col FROM {ctx['right_from']} WHERE {ctx['right_pred']})"
    )

    with Then("count()"):
        h = node.query(f"SELECT count() FROM {ctx['hybrid']} {clause}").output.strip()
        r = node.query(f"SELECT count() FROM {ref} {clause}").output.strip()
        assert h == r, error()

    with And("GROUP BY date_col"):
        h = node.query(
            f"SELECT date_col, count() FROM {ctx['hybrid']} "
            f"GROUP BY date_col ORDER BY date_col {clause}"
        ).output.strip()
        r = node.query(
            f"SELECT date_col, count() FROM {ref} "
            f"GROUP BY date_col ORDER BY date_col {clause}"
        ).output.strip()
        assert h == r, error()

    with And("fingerprint helper agrees"):
        h = node.query(fingerprint_sql(ctx["hybrid"]) + f" {clause}").output.strip()
        r = node.query(fingerprint_sql(ref) + f" {clause}").output.strip()
        assert h == r, error()


@TestFeature
@Name("cluster MergeTree Iceberg")
def feature(self, minio_root_user, minio_root_password):
    """Hybrid over cluster(MergeTree) + IcebergS3."""
    self.context.catalog = "no"

    for scenario in (
        cluster_mergetree_iceberg_prefer_localhost,
        cluster_mergetree_iceberg_force_remote,
        cluster_mergetree_iceberg_aggregations,
    ):
        Scenario(test=scenario)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
