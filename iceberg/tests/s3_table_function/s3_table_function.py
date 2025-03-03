#!/usr/bin/env python3

from testflows.core import *

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.s3 as s3_steps


@TestScenario
def s3_table_function(self, minio_root_user, minio_root_password):
    """Test Iceberg table creation and reading data from ClickHouse using
    s3 table function."""

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:8182/",
            catalog_type=catalog_steps.CATALOG_TYPE,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        namespace = "iceberg"
        table_name = "names"
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"delete table {namespace}.{table_name} if already exists"):
        catalog_steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with When(f"create {namespace}.{table_name} table with three columns"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
        )

    with And(f"insert data into {namespace}.{table_name} table"):
        df = pa.Table.from_pylist(
            [
                {"name": "Alice", "double": 195.23, "integer": 20},
                {"name": "Bob", "double": 123.45, "integer": 30},
                {"name": "Charlie", "double": 67.89, "integer": 40},
            ]
        )
        table.append(df)

    with And("scan and display data"):
        df = table.scan().to_pandas()
        note(df)

    with Then("read data in clickhouse using s3 table function"):
        s3_steps.read_data_with_s3_table_function(
            endpoint="http://minio:9000/warehouse/data/data/**/**.parquet",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )


@TestFeature
@Name("s3 table function")
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=s3_table_function)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
