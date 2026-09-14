from testflows.core import *

from iceberg.requirements.hybrid import (
    RQ_ClickHouse_Hybrid_QueryFuzzing,
)

from iceberg.tests.hybrid.fuzzing.common import (
    create_mt_iceberg_cluster_fuzz_hybrid,
    load_queries_from_sql_file,
    run_fuzz_queries,
    sql_path,
)


@TestScenario
@Name("hybrid curated query fuzz")
def hybrid_curated_query_fuzz(self, minio_root_user, minio_root_password):
    """Run curated Hybrid SQL against remote(MT) + icebergCluster."""
    with Given("MT + icebergCluster Hybrid fuzz topology"):
        ctx = create_mt_iceberg_cluster_fuzz_hybrid(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            location_suffix="fuzz",
        )

    with When("load curated Hybrid fuzz SQL"):
        queries = load_queries_from_sql_file(
            sql_path("hybrid_query_fuzzing_queries.sql")
        )
        assert queries, "curated fuzz SQL file is empty"

    substitutions = {
        "{hybrid_table}": ctx["hybrid"],
        "{merge_tree_table}": ctx["merge_tree"],
        "{clickhouse_iceberg_table_name}": ctx["iceberg"],
        "{join_settings}": "SETTINGS object_storage_cluster_join_mode = 'local'",
    }

    run_fuzz_queries(queries=queries, substitutions=substitutions)


@TestFeature
@Requirements(
    RQ_ClickHouse_Hybrid_QueryFuzzing("1.0"),
)
@Name("hybrid curated queries")
def feature(self, minio_root_user, minio_root_password):
    """Curated Hybrid query fuzz SQL (non-interactive)."""
    Scenario(test=hybrid_curated_query_fuzz)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
