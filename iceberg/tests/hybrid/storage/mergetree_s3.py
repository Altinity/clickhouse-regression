from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.tables import create_table

from iceberg.requirements.hybrid import (
    RQ_ClickHouse_Hybrid_Segment_S3Parquet,
)

from iceberg.tests.hybrid.core.common import (
    ALL_ROWS,
    COLUMNS,
    LEFT_PREDICATE,
    RIGHT_PREDICATE,
    PREFER_LOCALHOST,
    FORCE_REMOTE,
    assert_hybrid_matches_reference,
    create_mergetree_segment,
    remote_tf,
)
from iceberg.tests.hybrid.storage.common import (
    s3_parquet_tf,
    s3_cluster_parquet_tf,
    write_s3_parquet_rows,
)


@TestStep(Given)
def create_remote_mt_s3_hybrid(
    self,
    minio_root_user,
    minio_root_password,
    use_s3_cluster=False,
    left_pred=LEFT_PREDICATE,
    right_pred=RIGHT_PREDICATE,
):
    """remote(MT) hot + s3/s3Cluster Parquet cold segment."""
    with By("create local MergeTree hot segment"):
        left = create_mergetree_segment(rows=ALL_ROWS)

    with By("write Parquet cold segment to MinIO"):
        url = write_s3_parquet_rows(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            rows=ALL_ROWS,
        )

    if use_s3_cluster:
        right_tf = s3_cluster_parquet_tf(url, minio_root_user, minio_root_password)
    else:
        right_tf = s3_parquet_tf(url, minio_root_user, minio_root_password)

    hybrid = f"hybrid_{getuid()}"
    left_tf = remote_tf(left)

    with By("create Hybrid remote(MT) + s3 Parquet"):
        create_table(
            name=hybrid,
            engine=f"Hybrid({left_tf}, {left_pred}, {right_tf}, {right_pred})",
            columns=COLUMNS,
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    return {
        "hybrid": hybrid,
        "left": left,
        "url": url,
        "left_from": left_tf,
        # Reference cold side: same s3 TF (no local table for Parquet-only path).
        "right_from": right_tf,
        "left_pred": left_pred,
        "right_pred": right_pred,
    }


@TestScenario
@Name("s3 parquet prefer localhost")
def s3_parquet_prefer_localhost(self, minio_root_user, minio_root_password):
    """remote(MT)+s3 Parquet fingerprint and filters."""
    with Given("Hybrid remote(MT) + s3 Parquet"):
        ctx = create_remote_mt_s3_hybrid(
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
@Name("s3 parquet force remote")
def s3_parquet_force_remote(self, minio_root_user, minio_root_password):
    """remote(MT)+s3 Parquet with prefer_localhost_replica=0."""
    with Given("Hybrid remote(MT) + s3 Parquet"):
        ctx = create_remote_mt_s3_hybrid(
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
@Name("s3Cluster parquet smoke")
def s3_cluster_parquet_smoke(self, minio_root_user, minio_root_password):
    """remote(MT)+s3Cluster Parquet full-scan fingerprint."""
    with Given("Hybrid remote(MT) + s3Cluster Parquet"):
        ctx = create_remote_mt_s3_hybrid(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            use_s3_cluster=True,
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


@TestFeature
@Requirements(
    RQ_ClickHouse_Hybrid_Segment_S3Parquet("1.0"),
)
@Name("mergetree s3")
def feature(self, minio_root_user, minio_root_password):
    """remote(MT) + S3 Parquet cold segment (s3 and s3Cluster)."""
    for scenario in (
        s3_parquet_prefer_localhost,
        s3_parquet_force_remote,
        s3_cluster_parquet_smoke,
    ):
        Scenario(test=scenario)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
