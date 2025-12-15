from testflows.core import *


@TestFeature
@Name("iceberg table engine")
def feature(self, minio_root_user, minio_root_password):
    """Run iceberg table engine test."""
    self.context.catalog = "rest"
    Feature(
        test=load("iceberg.tests.iceberg_table_engine.row_policy", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("iceberg.tests.iceberg_table_engine.column_rbac", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("iceberg.tests.iceberg_table_engine.alter", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("iceberg.tests.iceberg_table_engine.rbac", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("iceberg.tests.iceberg_table_engine.named_collections", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load(
            "iceberg.tests.iceberg_table_engine.iceberg_writes_minmax", "feature"
        ),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
