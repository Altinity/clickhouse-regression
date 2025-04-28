#!/usr/bin/env python3

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine


@TestScenario
def sanity_ice(self, minio_root_user, minio_root_password):
    """Test th Clickhouse Iceberg engine with Nessie catalog."""
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_database_{getuid()}"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:5000",
            catalog_type=catalog_steps.CATALOG_TYPE,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            auth_header="foo",
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"create {namespace}.{table_name} table"):
        table = catalog_steps.create_iceberg_table_with_five_columns(
            catalog=catalog, namespace=namespace, table_name=table_name, with_data=True
        )

    with And("scan and display data"):
        df = table.scan().to_pandas()
        note(df)

    with Then("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            rest_catalog_url="http://ice-rest-catalog:5000",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            catalog_type=catalog_steps.CATALOG_TYPE,
            storage_endpoint="http://minio:9000/warehouse",
            warehouse="s3://bucket1/",
        )

    with And("list tables in the database"):
        self.context.node.query(f"SHOW TABLES FROM {database_name}")

    with And("check SHOW CREATE DATABASE"):
        self.context.node.query(f"SHOW CREATE DATABASE {database_name}")

    with And("check the tables in the database"):
        iceberg_engine.show_create_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )

    with And("read data in clickhouse from the previously created table"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=sanity_ice)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
