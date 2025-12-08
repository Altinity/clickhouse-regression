#!/usr/bin/env python3

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.icebergS3 as icebergS3
import iceberg.tests.steps.iceberg_engine as iceberg_engine


@TestScenario
def sanity(self, minio_root_user, minio_root_password):
    """Test Iceberg table creation and reading data from ClickHouse using
    icebergS3 table function."""
    namespace = f"icebergS3_{getuid()}"
    table_name = f"table_{getuid()}"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"create {namespace}.{table_name} table with three columns"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
        )

    with And(
        "read data in clickhouse using icebergS3 table function and check if it's empty"
    ):
        result = icebergS3.read_data_with_icebergS3_table_function(
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
        result = icebergS3.read_data_with_icebergS3_table_function(
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
    namespace = f"icebergS3_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"database_{getuid()}"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

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

    with And("scan and display data with pyiceberg"):
        df = table.scan().to_pandas()
        note(df)

    with And("delete table and recreate it"):
        with By(f"delete table {namespace}.{table_name} if already exists"):
            catalog_steps.drop_iceberg_table(
                catalog=catalog, namespace=namespace, table_name=table_name
            )
        with And(f"recreate table {namespace}.{table_name}"):
            table = catalog_steps.create_iceberg_table_with_three_columns(
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
        result = icebergS3.read_data_with_icebergS3_table_function(
            storage_endpoint="http://minio:9000/warehouse/data",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        assert result.output == "", error()


@TestScenario
def recreate_table_and_insert_new_data(self, minio_root_user, minio_root_password):
    """Verify that when a table is recreated, ClickHouse reads data from the new table."""
    namespace = f"icebergS3_{getuid()}"
    table_name = f"table_{getuid()}"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

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

    with And("scan and display data with pyiceberg"):
        df = table.scan().to_pandas()
        note(df)

    with And("delete table and recreate it"):
        with By(f"delete table {namespace}.{table_name} if already exists"):
            catalog_steps.drop_iceberg_table(
                catalog=catalog, namespace=namespace, table_name=table_name
            )
        with And(f"recreate table {namespace}.{table_name}"):
            table = catalog_steps.create_iceberg_table_with_three_columns(
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

    with And("scan and display data with pyiceberg"):
        df = table.scan().to_pandas()
        note(df)

    with Then("verify that ClickHouse reads the new data (one row)"):
        for retry in retries(count=11, delay=2):
            with retry:
                result = icebergS3.read_data_with_icebergS3_table_function(
                    storage_endpoint="http://minio:9000/warehouse/data",
                    s3_access_key_id=minio_root_user,
                    s3_secret_access_key=minio_root_password,
                )
                assert "David	195.23	20" in result.output, error()


@TestScenario
def recreate_table_and_insert_new_data_multiple_times(
    self, minio_root_user, minio_root_password
):
    """Verify that when a table is recreated, ClickHouse reads data from the new table."""
    namespace = f"icebergS3_{getuid()}"
    table_name = f"new_data_{getuid()}"
    database_name = f"database_new_data_{getuid()}"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
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

    with And("scan and display data with pyiceberg"):
        df = table.scan().to_pandas()
        note(df)

    with And("delete table and recreate it"):
        with By(f"delete table {namespace}.{table_name} if already exists"):
            catalog_steps.drop_iceberg_table(
                catalog=catalog, namespace=namespace, table_name=table_name
            )
        with And(f"recreate table {namespace}.{table_name}"):
            table = catalog_steps.create_iceberg_table_with_three_columns(
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

    with And("scan and display data with pyiceberg, expect one row"):
        df = table.scan().to_pandas()
        note(df)

    with Then("verify that ClickHouse reads the new data (one row)"):
        for retry in retries(count=11, delay=2):
            with retry:
                result = icebergS3.read_data_with_icebergS3_table_function(
                    storage_endpoint="http://minio:9000/warehouse/data",
                    s3_access_key_id=minio_root_user,
                    s3_secret_access_key=minio_root_password,
                )
                assert "David	195.23	20" in result.output, error()


@TestFeature
@Name("icebergS3 table function")
def icebergS3_table_function(self, minio_root_user, minio_root_password):
    self.context.catalog = "rest"
    Scenario(test=sanity)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=recreate_table)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=recreate_table_and_insert_new_data)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=recreate_table_and_insert_new_data_multiple_times)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
