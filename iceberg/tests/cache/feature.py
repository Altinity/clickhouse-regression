from testflows.core import *

from helpers.common import check_clickhouse_version


@TestFeature
@Name("iceberg cache")
def feature(self, minio_root_user, minio_root_password):
    """Run cache test for Iceberg table engine, database engine and table functions."""
    with Feature("rest catalog"):
        self.context.catalog = "rest"
        Feature(
            test=load("iceberg.tests.cache.iceberg_database_engine", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.cache.iceberg_table_engine", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.cache.icebergS3_table_function", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("glue catalog"):
        self.context.catalog = "glue"
        Feature(
            test=load("iceberg.tests.cache.iceberg_database_engine", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.cache.iceberg_table_engine", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load("iceberg.tests.cache.icebergS3_table_function", "feature"),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    if check_clickhouse_version(">=26.10")(self):
        with Feature("unity catalog"):
            self.context.catalog = "unity"
            Feature(
                test=load("iceberg.tests.cache.iceberg_database_engine", "feature"),
            )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
            Feature(
                test=load("iceberg.tests.cache.iceberg_table_engine", "feature"),
            )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
            Feature(
                test=load("iceberg.tests.cache.icebergS3_table_function", "feature"),
            )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
