#!/usr/bin/env python3

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid, check_clickhouse_version

from decimal import Decimal
from pyiceberg.schema import Schema
from pyiceberg.types import (
    BooleanType,
    StringType,
    LongType,
    DoubleType,
    DecimalType,
    StructType,
    NestedField,
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.table.sorting import SortOrder, SortField
from pyiceberg.transforms import IdentityTransform

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine


@TestScenario
def sanity(self, minio_root_user, minio_root_password):
    """Test the Iceberg engine in ClickHouse."""
    namespace = "iceberg"
    table_name = "name"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:8182/",
            catalog_type=catalog_steps.CATALOG_TYPE,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"delete table {namespace}.{table_name} if already exists"):
        catalog_steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with When(f"define schema and create {namespace}.{table_name} table"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with Then("create database with Iceberg engine"):
        database_name = "datalake"
        iceberg_engine.drop_database(database_name=database_name)
        iceberg_engine.create_experimental_iceberg_database(
            namespace=namespace,
            database_name=database_name,
            rest_catalog_url="http://rest:8181/v1",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            catalog_type=catalog_steps.CATALOG_TYPE,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("check the tables in the database"):
        iceberg_engine.show_create_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )

    with And("read data in clickhouse from the previously created table"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
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
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )
        assert "Alice	195.23	20" in result.output, error()
        assert "Bob	123.45	30" in result.output, error()
        assert "Charlie	67.89	40" in result.output, error()


@TestScenario
def recreate_table(self, minio_root_user, minio_root_password):
    """Test the Iceberg engine in ClickHouse."""
    node = self.context.node
    namespace = "iceberg"
    table_name = "name"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:8182/",
            catalog_type=catalog_steps.CATALOG_TYPE,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"delete table {namespace}.{table_name} if already exists"):
        catalog_steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with When(f"define schema and create {namespace}.{table_name} table"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
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
        iceberg_engine.drop_database(database_name=database_name)
        iceberg_engine.create_experimental_iceberg_database(
            namespace=namespace,
            database_name=database_name,
            rest_catalog_url="http://rest:8181/v1",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            catalog_type=catalog_steps.CATALOG_TYPE,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And(f"delete table {namespace}.{table_name} if already exists"):
        catalog_steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And("check the tables in the database after deleting the table"):
        result = node.query("SHOW TABLES from datalake")
        assert table_name not in result.output, error()

    with And("recreate table with same name"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
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

    with And("scan and display data"):
        df = table.scan().to_pandas()
        note(df)

    with Then("verify that ClickHouse reads the new data （one row）"):
        for retry in retries(count=11, delay=1):
            with retry:
                result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                )
                assert "David\t20\t27" in result.output, error()


@TestScenario
def recreate_table_multiple_times(self, minio_root_user, minio_root_password):
    """Test the Iceberg engine in ClickHouse."""
    node = self.context.node
    namespace = "iceberg"
    table_name = "name"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:8182/",
            catalog_type=catalog_steps.CATALOG_TYPE,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"delete table {namespace}.{table_name} if already exists"):
        catalog_steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with When(f"define schema and create {namespace}.{table_name} table"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
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
        iceberg_engine.drop_database(database_name=database_name)
        iceberg_engine.create_experimental_iceberg_database(
            namespace=namespace,
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("read data in clickhouse from the previously created table"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )
        assert "Alice\t195.23\t20" in result.output, error()
        assert "Bob\t123.45\t30" in result.output, error()
        assert "Charlie\t67.89\t40" in result.output, error()

    with And(f"delete table {namespace}.{table_name} if already exists"):
        catalog_steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And("check the tables in the database after deleting the table"):
        result = node.query("SHOW TABLES from datalake")
        assert table_name not in result.output, error()

    with And("recreate table with same name"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And("insert one row to recreated table"):
        df = pa.Table.from_pylist(
            [
                {"name": "David", "double": 20.0, "integer": 27},
            ]
        )
        table.append(df)

    with And("scan and display data"):
        df = table.scan().to_pandas()
        note(df)

    with Then("verify that ClickHouse reads the new data （one row）"):
        for retry in retries(count=11, delay=1):
            with retry:
                result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                )
                assert "David\t20\t27" in result.output, error()

    with Then("recreate database with Iceberg engine"):
        database_name = "datalake"
        iceberg_engine.drop_database(database_name=database_name)
        iceberg_engine.create_experimental_iceberg_database(
            namespace=namespace,
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with Then("verify that ClickHouse reads the new data （one row）"):
        for retry in retries(count=11, delay=1):
            with retry:
                result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                )
                assert "David\t20\t27" in result.output, error()

    with Then("recreate database with Iceberg engine"):
        database_name = "datalake"
        iceberg_engine.drop_database(database_name=database_name)
        iceberg_engine.create_experimental_iceberg_database(
            namespace=namespace,
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with Then("verify that ClickHouse reads the new data （one row）"):
        for retry in retries(count=11, delay=1):
            with retry:
                result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                )
                assert "David\t20\t27" in result.output, error()


@TestScenario
def rename_database(self, minio_root_user, minio_root_password):
    """Test renaming the database with Iceberg engine in ClickHouse."""
    namespace = f"iceberg_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_database_{getuid()}"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:8182/",
            catalog_type=catalog_steps.CATALOG_TYPE,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"define schema and create {namespace}.{table_name} table"):
        catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with Then("create database with Iceberg engine"):
        iceberg_engine.drop_database(database_name=database_name)
        iceberg_engine.create_experimental_iceberg_database(
            namespace=namespace,
            database_name=database_name,
            rest_catalog_url="http://rest:8181/v1",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            catalog_type=catalog_steps.CATALOG_TYPE,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("check that rename Iceberg database is not supported"):
        new_database_name = f"new_iceberg_database_{getuid()}"
        exitcode = 48
        database_engine_name = (
            "Iceberg" if check_clickhouse_version("<25.3")(self) else "DataLakeCatalog"
        )
        message = f"DB::Exception: {database_engine_name}: RENAME DATABASE is not supported. (NOT_IMPLEMENTED)"
        rename_query = f"RENAME DATABASE {database_name} TO {new_database_name}"
        self.context.node.query(
            rename_query,
            exitcode=exitcode,
            message=message,
        )


@TestScenario
def rename_table_from_iceberg_database(self, minio_root_user, minio_root_password):
    """Test renaming the database with Iceberg engine in ClickHouse."""
    namespace = f"iceberg_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_database_{getuid()}"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:8182/",
            catalog_type=catalog_steps.CATALOG_TYPE,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"define schema and create {namespace}.{table_name} table"):
        catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with Then("create database with Iceberg engine"):
        iceberg_engine.drop_database(database_name=database_name)
        iceberg_engine.create_experimental_iceberg_database(
            namespace=namespace,
            database_name=database_name,
            rest_catalog_url="http://rest:8181/v1",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            catalog_type=catalog_steps.CATALOG_TYPE,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("check that rename table from Iceberg database is not supported"):
        new_table_name = f"new_table_{getuid()}"
        exitcode = 48
        database_engine_name = (
            "Iceberg" if check_clickhouse_version("<25.3")(self) else "DataLakeCatalog"
        )
        message = f"DB::Exception: {database_engine_name}: renameTable() is not supported. (NOT_IMPLEMENTED)"
        rename_query = f"RENAME TABLE {database_name}.\\`{namespace}.{table_name}\\` TO {new_table_name}"
        self.context.node.query(
            rename_query,
            exitcode=exitcode,
            message=message,
        )


@TestScenario
def use_database(self, minio_root_user, minio_root_password, node=None):
    """Test using the database with Iceberg engine in ClickHouse."""
    if node is None:
        node = self.context.node

    namespace = f"iceberg_{getuid()}"
    table_name = f"table_{getuid()}"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:8182/",
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

    with Then("create database with Iceberg engine"):
        database_name = f"iceberg_database_{getuid()}"
        iceberg_engine.drop_database(database_name=database_name)
        iceberg_engine.create_experimental_iceberg_database(
            namespace=namespace,
            database_name=database_name,
            rest_catalog_url="http://rest:8181/v1",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            catalog_type=catalog_steps.CATALOG_TYPE,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("use the database"):
        result = node.query(
            f"USE {database_name}; SELECT currentDatabase(); SHOW TABLES;"
        )
        assert f"{namespace}.{table_name}" in result.output, error()

    with And("check the current database"):
        result = node.query(f"USE {database_name}; SELECT currentDatabase()")
        assert result.output.strip() == f"{database_name}", error()


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=sanity)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=recreate_table)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=recreate_table_multiple_times)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=rename_database)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=use_database)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=rename_table_from_iceberg_database)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
