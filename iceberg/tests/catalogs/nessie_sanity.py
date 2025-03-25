#!/usr/bin/env python3

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine


@TestScenario
def sanity_nessie(self, minio_root_user, minio_root_password):
    """Test Iceberg engine with Nessie."""
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_database_{getuid()}"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:19120/iceberg",
            catalog_type=catalog_steps.CATALOG_TYPE,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"define schema and create {namespace}.{table_name} table"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    # with And(f"insert data into {namespace}.{table_name} table"):
    #     df = pa.Table.from_pylist(
    #         [
    #             {"name": "Alice", "double": 195.23, "integer": 20},
    #             {"name": "Bob", "double": 123.45, "integer": 30},
    #             {"name": "Charlie", "double": 67.89, "integer": 40},
    #         ]
    #     )
    #     table.append(df)

    with And("scan and display data"):
        df = table.scan().to_pandas()
        note(df)

    with Then("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            namespace="warehouse",
            database_name=database_name,
            rest_catalog_url="http://nessie:19120/iceberg",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            catalog_type=catalog_steps.CATALOG_TYPE,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("list tables in the database"):
        self.context.node.query(f"SHOW TABLES FROM {database_name}")

    with And("check the tables in the database"):
        iceberg_engine.show_create_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )

    with And("read data in clickhouse from the previously created table"):
        # result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
        #     database_name=database_name, namespace=namespace, table_name=table_name
        # )
        pause()


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=sanity_nessie)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
