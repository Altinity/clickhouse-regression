#!/usr/bin/env python3

from testflows.core import *
from testflows.asserts import error

import pyarrow as pa

import iceberg.tests.common_steps as common_steps
import iceberg.tests.iceberg_engine.steps as steps


@TestScenario
def sanity(self):
    """Test the Iceberg engine in ClickHouse."""
    s3_access_key_id = "minio"
    s3_secret_access_key = "minio123"
    catalog_type = "rest"
    namespace = "iceberg"
    table_name = "name"

    with Given("create catalog"):
        catalog = common_steps.create_catalog(
            uri="http://localhost:8182/",
            catalog_type=catalog_type,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=s3_access_key_id,
            s3_secret_access_key=s3_secret_access_key,
        )

    with And("create namespace"):
        common_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"delete table {namespace}.{table_name} if already exists"):
        common_steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with When(f"define schema and create {namespace}.{table_name} table"):
        table = common_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with Then("create database with Iceberg engine"):
        database_name = "datalake"
        steps.drop_database(database_name=database_name)
        steps.create_experimental_iceberg_database(
            namespace=namespace,
            database_name=database_name,
            rest_catalog_url="http://rest:8181/v1",
            s3_access_key_id=s3_access_key_id,
            s3_secret_access_key=s3_secret_access_key,
            catalog_type=catalog_type,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("check the tables in the database"):
        steps.show_create_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )

    with And("read data in clickhouse from the previously created table"):
        result = steps.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )
        assert "" in result.output, error()

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

    with And("read data in clickhouse from the previously created table"):
        result = steps.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )
        assert "Alice	195.23	20" in result.output, error()
        assert "Bob	123.45	30" in result.output, error()
        assert "Charlie	67.89	40" in result.output, error()


@TestScenario
def recreate_table(self):
    """Test the Iceberg engine in ClickHouse."""
    node = self.context.node
    s3_access_key_id = "minio"
    s3_secret_access_key = "minio123"
    catalog_type = "rest"
    namespace = "iceberg"
    table_name = "name"

    with Given("create catalog"):
        catalog = common_steps.create_catalog(
            uri="http://localhost:8182/",
            catalog_type=catalog_type,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=s3_access_key_id,
            s3_secret_access_key=s3_secret_access_key,
        )

    with And("create namespace"):
        common_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"delete table {namespace}.{table_name} if already exists"):
        common_steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with When(f"define schema and create {namespace}.{table_name} table"):
        table = common_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
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

    with Then("create database with Iceberg engine"):
        database_name = "datalake"
        steps.drop_database(database_name=database_name)
        steps.create_experimental_iceberg_database(
            namespace=namespace,
            database_name=database_name,
            rest_catalog_url="http://rest:8181/v1",
            s3_access_key_id=s3_access_key_id,
            s3_secret_access_key=s3_secret_access_key,
            catalog_type=catalog_type,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And(f"delete table {namespace}.{table_name} if already exists"):
        common_steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And("check the tables in the database after deleting the table"):
        result = node.query("SHOW TABLES from datalake")
        assert table_name not in result.output, error()

    with And("recreate table with same name"):
        table = common_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And("insert one row to recreated table"):
        df = pa.Table.from_pylist(
            [
                {"name": "David", "double": 20.0, "integer": 27},
            ]
        )
        table.append(df)

    with When("restart the node and drop filesystem cache"):
        node.restart()
        node.query(f"SYSTEM DROP FILESYSTEM CACHE")

    with And("read data in clickhouse from recreated table"):
        steps.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )

    with And("scan and display data"):
        df = table.scan().to_pandas()
        note(df)

    with And("read data in clickhouse from recreated table"):
        result = steps.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )

    with Then("verify that ClickHouse reads the new data （one row）"):
        for retry in retries(count=11, delay=1):
            with retry:
                result = steps.read_data_from_clickhouse_iceberg_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                )
                assert "David\t20\t27" in result.output, error()


@TestFeature
def feature(self):
    Scenario(run=sanity)
    Scenario(run=recreate_table)
