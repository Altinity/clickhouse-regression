from testflows.core import *


@TestFeature
@Name("iceberg engine")
def feature(self, minio_root_user, minio_root_password):
    """Run iceberg engine test."""
    Feature(
        test=load("iceberg.tests.iceberg_engine.sanity", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("iceberg.tests.iceberg_engine.rbac", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("iceberg.tests.iceberg_engine.named_collections", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("iceberg.tests.iceberg_engine.changing_schema", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
