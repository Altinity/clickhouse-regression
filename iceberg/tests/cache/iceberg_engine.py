from testflows.core import *
from helpers.common import getuid

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine


@TestScenario
def cache(self, minio_root_user, minio_root_password):
    """
    Test caching when selecting from a table from the database
    with the Iceberg engine.
    """
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_database_{getuid()}"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:8182/",
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"define schema and create {namespace}.{table_name} table"):
        table = catalog_steps.create_iceberg_table_with_five_columns(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            with_data=True,
            number_of_rows=100,
        )

    with Then("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            namespace=namespace,
            database_name=database_name,
            rest_catalog_url="http://rest:8181/v1",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("read data in clickhouse from the previously created table"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=cache)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
