from testflows.core import *

from iceberg.requirements.hybrid import (
    RQ_ClickHouse_Hybrid_Segment_IcebergCatalogs,
)

from iceberg.tests.hybrid.core.common import (
    PREFER_LOCALHOST,
    FORCE_REMOTE,
    assert_hybrid_matches_reference,
)
from iceberg.tests.hybrid.storage.common import (
    create_cluster_mt_iceberg_catalog_hybrid,
)


CATALOG_MODES = ("no", "ice", "glue")


@TestScenario
@Name("full scan prefer localhost")
def full_scan_prefer_localhost(self, minio_root_user, minio_root_password):
    """Fingerprint Hybrid vs UNION ALL with prefer_localhost_replica=1."""
    with Given("cluster(MT) + catalog Iceberg Hybrid"):
        ctx = create_cluster_mt_iceberg_catalog_hybrid(
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


@TestScenario
@Name("full scan force remote")
def full_scan_force_remote(self, minio_root_user, minio_root_password):
    """Fingerprint with prefer_localhost_replica=0."""
    with Given("cluster(MT) + catalog Iceberg Hybrid"):
        ctx = create_cluster_mt_iceberg_catalog_hybrid(
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
@Name("hot and cold filters")
def hot_and_cold_filters(self, minio_root_user, minio_root_password):
    """Hard-assert hot-only and cold-only WHERE results."""
    with Given("cluster(MT) + catalog Iceberg Hybrid"):
        ctx = create_cluster_mt_iceberg_catalog_hybrid(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("hot-only filter"):
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


@TestFeature
@Requirements(
    RQ_ClickHouse_Hybrid_Segment_IcebergCatalogs("1.0"),
)
@Name("mergetree iceberg catalog")
def feature(self, minio_root_user, minio_root_password):
    """cluster(MT) + Iceberg cold segment across no / ice / glue catalogs."""
    for mode in CATALOG_MODES:
        with Feature(f"{mode} catalog"):
            self.context.catalog = mode
            for scenario in (
                full_scan_prefer_localhost,
                full_scan_force_remote,
                hot_and_cold_filters,
            ):
                Scenario(test=scenario)(
                    minio_root_user=minio_root_user,
                    minio_root_password=minio_root_password,
                )
