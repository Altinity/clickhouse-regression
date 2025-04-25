import time
from testflows.core import *
from helpers.common import getuid

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine
from parquet.tests.steps.metadata_caching import check_hits


@TestStep(Given)
def setup_iceberg_environment(self, minio_root_user, minio_root_password):
    """Set up the Iceberg environment with catalog, namespace, table and database."""
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_database_{getuid()}"
    log_comment = "log_" + getuid()

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:5000/",
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
            number_of_rows=100,
        )

    with When("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            rest_catalog_url="http://ice-rest-catalog:5000",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )

    return namespace, table_name, database_name, log_comment


@TestStep(When)
def run_query_with_timing(
    self,
    database_name,
    namespace,
    table_name,
    cache_parquet_metadata=True,
    log_comment=None,
):
    """Run a query and return the execution time and result."""
    start_time = time.time()
    result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        cache_parquet_metadata=cache_parquet_metadata,
        log_comment=log_comment,
    )
    execution_time = time.time() - start_time
    return result, execution_time


@TestScenario
def cache(self, minio_root_user, minio_root_password):
    """
    Test caching when selecting from a table from the database
    with the Iceberg engine.
    """

    with Given("I setup the iceberg environment"):
        namespace, table_name, database_name, log_comment = setup_iceberg_environment(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )

    with Then(
        "read data in clickhouse from the previously created table with cold run"
    ):
        _, cold_run_time = run_query_with_timing(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            cache_parquet_metadata=True,
        )

    with And("read data in clickhouse from the previously created table with warm run"):
        for _ in range(10):
            _, warm_run_time = run_query_with_timing(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                cache_parquet_metadata=True,
                log_comment=log_comment,
            )
        assert (
            warm_run_time < cold_run_time
        ), f"query ran slower with caching cold_run_time={cold_run_time}s warm_run_time={warm_run_time}s"

    with And("I check that the cache was hit"):
        hits = check_hits(
            log_comment=log_comment, node=self.context.node, assertion=True
        )
        assert hits > 0, "cache was not hit"


@TestFeature
@Name("iceberg database engine")
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=cache)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
