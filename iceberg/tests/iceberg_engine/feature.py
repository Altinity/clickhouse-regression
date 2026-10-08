from testflows.core import *

from helpers.common import check_clickhouse_version


UNITY_MODULES = (
    "sanity",
    "alter",
    "column_rbac",
    "predicate_push_down",
    "rbac",
    "row_policy",
    "sql_clauses",
    "equality_deletes",
    "position_delete_reads",
    "overwrite",
    "schema_evolution",
    "swarm_examples",
    "nested_datatypes",
    "partition_evolution",
    "use_iceberg_partition_pruning",
    "check_datatypes",
    "iceberg_iterator_race_condition",
    "dot_separated_column_names",
    "show_data_lake_catalogs_repro",
)




@TestFeature
@Name("iceberg engine")
def feature(self, minio_root_user, minio_root_password):
    """Run DataLakeCatalog database engine tests."""
    with Feature("rest catalog"):
        self.context.catalog = "rest"
        Feature(
            test=load("iceberg.tests.iceberg_engine.sanity", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.alter", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.column_rbac", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load(
                "iceberg.tests.iceberg_engine.predicate_push_down",
                "feature",
            ),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.rbac", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.row_policy", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.sql_clauses", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.equality_deletes", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.position_delete_reads", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        # Spark writes row lineage into the tabulario REST catalog, so row lineage
        # stays out of the glue loop below.
        # Feature(
        #     test=load("iceberg.tests.iceberg_engine.row_lineage", "feature"),
        # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.overwrite", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.schema_evolution", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.swarm_examples", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.nested_datatypes", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.partition_evolution", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load(
                "iceberg.tests.iceberg_engine.use_iceberg_partition_pruning", "feature"
            ),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        # Feature(
        #     test=load("iceberg.tests.iceberg_engine.timestamp_ns_pruning", "feature"),
        # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.check_datatypes", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load(
                "iceberg.tests.iceberg_engine.iceberg_iterator_race_condition",
                "feature",
            ),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load(
                "iceberg.tests.iceberg_engine.dot_separated_column_names", "feature"
            ),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.sort_key_timezone", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load(
                "iceberg.tests.iceberg_engine.show_data_lake_catalogs_repro", "feature"
            ),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        # Feature(
        #     test=load("iceberg.tests.iceberg_engine.alter_support", "feature"),
        # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    if check_clickhouse_version(">=26.10")(self):
        with Feature("unity catalog"):
            self.context.catalog = "unity"
            for module in UNITY_MODULES:
                Feature(
                    test=load(f"iceberg.tests.iceberg_engine.{module}", "feature"),
                )(
                    minio_root_user=minio_root_user,
                    minio_root_password=minio_root_password,
                )

    with Feature("glue catalog"):
        self.context.catalog = "glue"
        Feature(
            test=load("iceberg.tests.iceberg_engine.sanity", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.alter", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.column_rbac", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load(
                "iceberg.tests.iceberg_engine.predicate_push_down",
                "feature",
            ),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.rbac", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.row_policy", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.sql_clauses", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.equality_deletes", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.position_delete_reads", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.overwrite", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.schema_evolution", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.swarm_examples", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.nested_datatypes", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.partition_evolution", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load(
                "iceberg.tests.iceberg_engine.use_iceberg_partition_pruning", "feature"
            ),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        # Feature(
        #     test=load("iceberg.tests.iceberg_engine.timestamp_ns_pruning", "feature"),
        # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.iceberg_engine.check_datatypes", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load(
                "iceberg.tests.iceberg_engine.iceberg_iterator_race_condition",
                "feature",
            ),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load(
                "iceberg.tests.iceberg_engine.dot_separated_column_names", "feature"
            ),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load(
                "iceberg.tests.iceberg_engine.show_data_lake_catalogs_repro", "feature"
            ),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        # Feature(
        #     test=load("iceberg.tests.iceberg_engine.alter_support", "feature"),
        # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
