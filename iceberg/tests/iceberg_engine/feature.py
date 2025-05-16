from testflows.core import *


@TestFeature
@Name("iceberg engine")
def feature(self, minio_root_user, minio_root_password):
    """Run iceberg engine test."""
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
        test=load("iceberg.tests.iceberg_engine.sanity", "feature"),
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
        test=load("iceberg.tests.iceberg_engine.overwrite_deletes", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("iceberg.tests.iceberg_engine.writes", "feature"),
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
