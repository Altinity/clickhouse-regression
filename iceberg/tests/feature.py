from testflows.core import *

from iceberg.requirements import *


@TestFeature
@Name("iceberg integration")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Check different ways of reading (and writing later) data from/to Iceberg
    tables in Clickhouse."""

    Feature(
        name="s3 table function",
        test=load("iceberg.tests.s3_table_function.s3_table_function", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        name="icebergS3 table function",
        test=load(
            "iceberg.tests.icebergS3_table_function.icebergS3_table_function",
            "icebergS3_table_function",
        ),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        name="iceberg engine",
        test=load("iceberg.tests.iceberg_engine.iceberg_engine", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        name="iceberg engine",
        test=load("iceberg.tests.iceberg_engine.rbac", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
