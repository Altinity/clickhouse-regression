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
@Name("upstream-derived query fuzz")
def upstream_derived_query_fuzz(self, minio_root_user, minio_root_password):
    """Upstream-shaped SQL on the same MT + icebergCluster Hybrid topology."""
    with Given("MT + icebergCluster Hybrid fuzz topology"):
        ctx = create_mt_iceberg_cluster_fuzz_hybrid(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            location_suffix="fuzz_upstream",
        )

    with When("load upstream-derived fuzz SQL"):
        queries = load_queries_from_sql_file(sql_path("upstream_queries.sql"))
        assert queries, "upstream fuzz SQL file is empty"

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
@Name("upstream derived queries")
def feature(self, minio_root_user, minio_root_password):
    """Upstream-derived Hybrid query shapes (additive to curated fuzz SQL)."""
    Scenario(test=upstream_derived_query_fuzz)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
