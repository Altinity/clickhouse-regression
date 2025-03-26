from testflows.core import *


@TestFeature
@Name("iceberg engine")
def feature(self, minio_root_user, minio_root_password):
    """Run cache test for Iceberg table engine, database engine and table functions."""
    Feature(
        test=load("iceberg.tests.cache.iceberg_engine", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
