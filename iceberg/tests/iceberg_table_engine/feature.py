from testflows.core import *


@TestFeature
@Name("iceberg table engine")
def feature(self, minio_root_user, minio_root_password):
    """Run iceberg table engine test."""
    Feature(
        test=load("iceberg.tests.iceberg_table_engine.row_policy", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
