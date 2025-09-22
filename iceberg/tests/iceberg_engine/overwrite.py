#!/usr/bin/env python3

from testflows.core import *
from testflows.asserts import error

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine

from helpers.common import getuid


@TestScenario
def overwrite(self, minio_root_user, minio_root_password):
    """Test that ClickHouse correctly read data after
    it was overwritten in Iceberg table."""
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

    with When(f"define schema and create {namespace}.{table_name} table"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with Then("create database with Iceberg engine"):
        database_name = f"iceberg_database_{getuid()}"
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
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

    with And("scan and display data using PyIceberg"):
        df = table.scan().to_pandas()
        note(df)

    with And("read data in clickhouse from the previously created table"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )
        assert "Alice	195.23	20" in result.output, error()
        assert "Bob	123.45	30" in result.output, error()
        assert "Charlie	67.89	40" in result.output, error()

    with And("define another set of rows and overwrite Iceberg table data"):
        data = [
            {"name": "David", "double": 195.23, "integer": 20},
            {"name": "Eve", "double": 123.45, "integer": 30},
            {"name": "Frank", "double": 67.89, "integer": 40},
        ]
        df = pa.Table.from_pylist(data)
        table.overwrite(df)

    with And("scan and display data using PyIceberg"):
        df = table.scan().to_pandas()
        note(df)

    with And("check that ClickHouse reads new rows only"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )
        count = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns="count()",
        )
        assert "David	195.23	20" in result.output, error()
        assert "Eve	123.45	30" in result.output, error()
        assert "Frank	67.89	40" in result.output, error()
        assert count.output.strip() == "3", error()


@TestScenario
def append(self, minio_root_user, minio_root_password):
    """Test that ClickHouse correctly read data after
    it was appended to Iceberg table."""
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

    with When(f"define schema and create {namespace}.{table_name} table"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with Then("create database with Iceberg engine"):
        database_name = f"iceberg_database_{getuid()}"
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
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

    with And("scan and display data using PyIceberg"):
        df = table.scan().to_pandas()
        note(df)

    with And("read data in clickhouse from the previously created table"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )
        assert "Alice	195.23	20" in result.output, error()
        assert "Bob	123.45	30" in result.output, error()
        assert "Charlie	67.89	40" in result.output, error()

    with And("define another set of rows and append to Iceberg table data"):
        data = [
            {"name": "David", "double": 195.23, "integer": 20},
            {"name": "Eve", "double": 123.45, "integer": 30},
            {"name": "Frank", "double": 67.89, "integer": 40},
        ]
        df = pa.Table.from_pylist(data)
        table.append(df)

    with And("scan and display data using PyIceberg"):
        df = table.scan().to_pandas()
        note(df)

    with And("check that ClickHouse reads all rows"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )
        count = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns="count()",
        )
        assert "David	195.23	20" in result.output, error()
        assert "Eve	123.45	30" in result.output, error()
        assert "Frank	67.89	40" in result.output, error()
        assert "Alice	195.23	20" in result.output, error()
        assert "Bob	123.45	30" in result.output, error()
        assert "Charlie	67.89	40" in result.output, error()
        assert count.output.strip() == "6", error()


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=overwrite)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=append)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
