from testflows.core import *

from iceberg.requirements.hybrid import (
    RQ_ClickHouse_Hybrid_Segment_IcebergCluster,
)

from iceberg.tests.hybrid.core.common import (
    PREFER_LOCALHOST,
    FORCE_REMOTE,
    assert_hybrid_matches_reference,
)
from iceberg.tests.hybrid.storage.common import (
    JOIN_LOCAL,
    create_cluster_mt_iceberg_cluster_hybrid,
)


@TestScenario
@Name("icebergCluster prefer localhost")
def iceberg_cluster_prefer_localhost(self, minio_root_user, minio_root_password):
    """cluster(MT)+icebergCluster fingerprint with join_mode=local, localhost path."""
    with Given("Hybrid cluster(MT) + icebergCluster"):
        ctx = create_cluster_mt_iceberg_cluster_hybrid(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    settings = dict(PREFER_LOCALHOST)
    settings.update(JOIN_LOCAL)

    with Then("full scan fingerprint"):
        assert_hybrid_matches_reference(
            hybrid_table=ctx["hybrid"],
            left_from=ctx["left_from"],
            right_from=ctx["right_from"],
            left_pred=ctx["left_pred"],
            right_pred=ctx["right_pred"],
            settings_row=settings,
        )

    with And("hot-only filter"):
        assert_hybrid_matches_reference(
            hybrid_table=ctx["hybrid"],
            left_from=ctx["left_from"],
            right_from=ctx["right_from"],
            left_pred=ctx["left_pred"],
            right_pred=ctx["right_pred"],
            where="date_col >= '2025-06-01'",
            settings_row=settings,
        )


@TestScenario
@Name("icebergCluster force remote")
def iceberg_cluster_force_remote(self, minio_root_user, minio_root_password):
    """cluster(MT)+icebergCluster with prefer_localhost_replica=0."""
    with Given("Hybrid cluster(MT) + icebergCluster"):
        ctx = create_cluster_mt_iceberg_cluster_hybrid(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    settings = dict(FORCE_REMOTE)
    settings.update(JOIN_LOCAL)

    with Then("full scan fingerprint"):
        assert_hybrid_matches_reference(
            hybrid_table=ctx["hybrid"],
            left_from=ctx["left_from"],
            right_from=ctx["right_from"],
            left_pred=ctx["left_pred"],
            right_pred=ctx["right_pred"],
            settings_row=settings,
        )


@TestFeature
@Requirements(
    RQ_ClickHouse_Hybrid_Segment_IcebergCluster("1.0"),
)
@Name("mergetree iceberg cluster")
def feature(self, minio_root_user, minio_root_password):
    """cluster(MT) + icebergCluster cold path with object_storage_cluster_join_mode."""
    self.context.catalog = "no"

    for scenario in (
        iceberg_cluster_prefer_localhost,
        iceberg_cluster_force_remote,
    ):
        Scenario(test=scenario)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
