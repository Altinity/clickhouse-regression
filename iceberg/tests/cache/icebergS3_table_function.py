from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.icebergS3 as icebergS3
from parquet.tests.steps.metadata_caching import check_hits


@TestScenario
def cache(self, minio_root_user, minio_root_password):
    """
    Test caching when selecting data from iceberg table with IcebergS3
    table function.
    """
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"create {namespace}.{table_name} table with data"):
        table = catalog_steps.create_iceberg_table_with_five_columns(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            with_data=True,
            number_of_rows=10000,
        )

    with Then(
        "read data in clickhouse using icebergS3 table function for the first time"
    ):

        cold_execution_time, _ = (
            icebergS3.read_parquet_data_with_icebergS3_table_function(
                storage_endpoint="http://minio:9000/warehouse/data/",
                s3_access_key_id=minio_root_user,
                s3_secret_access_key=minio_root_password,
                cache_parquet_metadata=True,
                where_clause="date_col > '2030-01-01'",
            )
        )

    with And("read data in clickhouse using icebergS3 table function for 10 times"):
        for i in range(100):
            hot_execution_time, log_comment = (
                icebergS3.read_parquet_data_with_icebergS3_table_function(
                    storage_endpoint="http://minio:9000/warehouse/data/",
                    s3_access_key_id=minio_root_user,
                    s3_secret_access_key=minio_root_password,
                    cache_parquet_metadata=True,
                    where_clause="date_col > '2030-01-01'",
                )
            )

            note(
                f"hot_execution_time: {hot_execution_time} cold_execution_time: {cold_execution_time}"
            )
            assert hot_execution_time < cold_execution_time, error()

    with And("Check hits"):
        hits = check_hits(
            log_comment=log_comment, node=self.context.node, assertion=True
        )
        assert hits > 0, error("cache was not hit")


@TestFeature
@Name("icebergS3 table function")
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=cache)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
