#!/usr/bin/env python3

from testflows.core import *
from testflows.asserts import error

import pyarrow as pa


import iceberg.tests.common_steps as common_steps
import iceberg.tests.icebergS3_table_function.steps as steps


@TestScenario
def sanity(self, minio_root_user, minio_root_password):
    """Test Iceberg table creation and reading data from ClickHouse using
    icebergS3 table function."""
    namespace = "icebergS3"
    table_name = "sanity"

    with Given("create catalog"):
        catalog = common_steps.create_catalog(
            uri="http://localhost:8182/",
            catalog_type=common_steps.CATALOG_TYPE,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        common_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"delete table {namespace}.{table_name} if already exists"):
        common_steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with When(f"create {namespace}.{table_name} table with three columns"):
        table = common_steps.create_iceberg_table_with_three_columns(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
        )

    with And(
        "read data in clickhouse using icebergS3 table function and check if it's empty"
    ):
        result = steps.read_data_with_icebergS3_table_function(
            storage_endpoint="http://minio:9000/warehouse/data",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        assert result.output == "", error()

    with And(f"insert data into {namespace}.{table_name} table"):
        df = pa.Table.from_pylist(
            [
                {"name": "Alice", "double": 195.23, "integer": 20},
                {"name": "Bob", "double": 123.45, "integer": 30},
                {"name": "Charlie", "double": 67.89, "integer": 40},
            ]
        )
        table.append(df)

    with And("scan and display data with pyiceberg"):
        df = table.scan().to_pandas()
        note(df)

    with And("read data in clickhouse using icebergS3 table function"):
        result = steps.read_data_with_icebergS3_table_function(
            storage_endpoint="http://minio:9000/warehouse/data",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        assert "Alice	195.23	20" in result.output, error()
        assert "Bob	123.45	30" in result.output, error()
        assert "Charlie	67.89	40" in result.output, error()


@TestScenario
def recreate_table(self, minio_root_user, minio_root_password):
    """Verify that when an iceberg table is recreated, ClickHouse sees empty table."""
    namespace = "icebergS3"
    table_name = "recreate"

    with Given("create catalog"):
        catalog = common_steps.create_catalog(
            uri="http://localhost:8182/",
            catalog_type=common_steps.CATALOG_TYPE,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        common_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"delete table {namespace}.{table_name} if already exists"):
        common_steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with When(f"create {namespace}.{table_name} table with three columns"):
        table = common_steps.create_iceberg_table_with_three_columns(
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

    with And("scan and display data with pyiceberg"):
        df = table.scan().to_pandas()
        note(df)

    with And("delete table and recreate it"):
        with By(f"delete table {namespace}.{table_name} if already exists"):
            common_steps.drop_iceberg_table(
                catalog=catalog, namespace=namespace, table_name=table_name
            )
        with And(f"recreate table {namespace}.{table_name}"):
            table = common_steps.create_iceberg_table_with_three_columns(
                catalog=catalog,
                namespace=namespace,
                table_name=table_name,
            )

    with And("scan and display data with pyiceberg, expect empty table"):
        df = table.scan().to_pandas()
        note(df)

    with And(
        "read data in clickhouse using icebergS3 table function, expect empty table"
    ):
        result = steps.read_data_with_icebergS3_table_function(
            storage_endpoint="http://minio:9000/warehouse/data",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        assert result.output == "", error()


@TestScenario
def recreate_table_and_insert_new_data(self, minio_root_user, minio_root_password):
    """Verify that when a table is recreated, ClickHouse reads data from the new table."""
    namespace = "icebergS3"
    table_name = "new_data"

    with Given("create catalog"):
        catalog = common_steps.create_catalog(
            uri="http://localhost:8182/",
            catalog_type=common_steps.CATALOG_TYPE,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        common_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"delete table {namespace}.{table_name} if already exists"):
        common_steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with When(f"create {namespace}.{table_name} table with three columns"):
        table = common_steps.create_iceberg_table_with_three_columns(
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

    with And("scan and display data with pyiceberg"):
        df = table.scan().to_pandas()
        note(df)

    with And("delete table and recreate it"):
        with By(f"delete table {namespace}.{table_name} if already exists"):
            common_steps.drop_iceberg_table(
                catalog=catalog, namespace=namespace, table_name=table_name
            )
        with And(f"recreate table {namespace}.{table_name}"):
            table = common_steps.create_iceberg_table_with_three_columns(
                catalog=catalog,
                namespace=namespace,
                table_name=table_name,
            )

    with And("scan and display data with pyiceberg, expect empty table"):
        df = table.scan().to_pandas()
        note(df)

    with And("insert one row into recreated table"):
        df = pa.Table.from_pylist(
            [
                {"name": "David", "double": 195.23, "integer": 20},
            ]
        )
        table.append(df)

    with And("display table information"):
        note(f"Table Name: {table.name()}")
        note(f"Location: {table.location()}")

    with And("scan and display data with pyiceberg"):
        df = table.scan().to_pandas()
        note(df)

    with And("read data in clickhouse using icebergS3 table function"):
        result = steps.read_data_with_icebergS3_table_function(
            storage_endpoint="http://minio:9000/warehouse/data",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with Then("verify that ClickHouse reads the new data (one row)"):
        for retry in retries(count=101, delay=2):
            with retry:
                result = steps.read_data_with_icebergS3_table_function(
                    storage_endpoint="http://minio:9000/warehouse/data",
                    s3_access_key_id=minio_root_user,
                    s3_secret_access_key=minio_root_password,
                )
                assert "David	195.23	20" in result.output, error()


@TestFeature
def icebergS3_table_function(self, minio_root_user, minio_root_password):
    Scenario(test=sanity)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=recreate_table)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=recreate_table_and_insert_new_data)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
