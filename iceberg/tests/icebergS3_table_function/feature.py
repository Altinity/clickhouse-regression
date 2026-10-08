from testflows.core import *

from helpers.common import check_clickhouse_version


@TestFeature
@Name("icebergS3 table function")
def feature(self, minio_root_user, minio_root_password):
    """Run icebergS3/icebergS3Cluster table function tests."""
    with Feature("rest catalog"):
        self.context.catalog = "rest"
        Feature(
            test=load(
                "iceberg.tests.icebergS3_table_function.icebergS3_table_function",
                "icebergS3_table_function",
            ),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load(
                "iceberg.tests.icebergS3_table_function.several_iceberg_tables_in_one_dir",
                "several_iceberg_tables_in_one_dir",
            ),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        # Feature(
        #     test=load(
        #         "iceberg.tests.icebergS3_table_function.iceberg_local",
        #         "icebergLocal",
        #     ),
        # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    with Feature("glue catalog"):
        self.context.catalog = "glue"
        Feature(
            test=load(
                "iceberg.tests.icebergS3_table_function.icebergS3_table_function",
                "icebergS3_table_function",
            ),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
        Feature(
            test=load(
                "iceberg.tests.icebergS3_table_function.several_iceberg_tables_in_one_dir",
                "several_iceberg_tables_in_one_dir",
            ),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    if check_clickhouse_version(">=26.10")(self):
        with Feature("unity catalog"):
            self.context.catalog = "unity"
            Feature(
                test=load(
                    "iceberg.tests.icebergS3_table_function.icebergS3_table_function",
                    "icebergS3_table_function",
                ),
            )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
            Feature(
                test=load(
                    "iceberg.tests.icebergS3_table_function.several_iceberg_tables_in_one_dir",
                    "several_iceberg_tables_in_one_dir",
                ),
            )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
