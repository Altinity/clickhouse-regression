#!/usr/bin/env python3

from testflows.core import *

import pyarrow as pa

from pyiceberg.schema import Schema
from pyiceberg.types import (
    DoubleType,
    StringType,
    NestedField,
    LongType,
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.table.sorting import SortOrder, SortField
from pyiceberg.transforms import IdentityTransform

import iceberg.tests.steps as steps


@TestScenario
def sanity(self):
    """Test Iceberg table creation and reading data from ClickHouse using
    icebergS3 table function."""

    namespace = "iceberg"
    table_name = "bids"

    with Given("create catalog"):
        catalog = steps.create_catalog(
            uri="http://localhost:8182/",
            catalog_type=steps.CATALOG_TYPE,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=steps.S3_ACCESS_KEY_ID,
            s3_secret_access_key=steps.S3_SECRET_ACCESS_KEY,
        )

    with And("create namespace"):
        steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"delete table {namespace}.{table_name} if already exists"):
        steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with When(f"define schema and create {namespace}.{table_name} table"):
        schema = Schema(
            NestedField(
                field_id=1, name="name", field_type=StringType(), required=False
            ),
            NestedField(
                field_id=2, name="double", field_type=DoubleType(), required=False
            ),
            NestedField(
                field_id=3, name="integer", field_type=LongType(), required=False
            ),
        )
        partition_spec = PartitionSpec(
            PartitionField(
                source_id=1,
                field_id=1001,
                transform=IdentityTransform(),
                name="symbol_partition",
            ),
        )
        sort_order = SortOrder(SortField(source_id=1, transform=IdentityTransform()))
        table = steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location="s3://warehouse/data",
            partition_spec=partition_spec,
            sort_order=sort_order,
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

    with And("read data in clickhouse using icebergS3 table function"):
        steps.read_data_with_icebergS3_table_function(
            storage_endpoint="http://minio:9000/warehouse/data",
            s3_access_key_id=steps.S3_ACCESS_KEY_ID,
            s3_secret_access_key=steps.S3_SECRET_ACCESS_KEY,
        )


@TestScenario
def recreate_table(self):
    """Check that if table is recreated, the data from new table
    is being read in Clickhouse."""

    namespace = "iceberg"
    table_name = "bids"

    with Given("create catalog"):
        catalog = steps.create_catalog(
            uri="http://localhost:8182/",
            catalog_type=steps.CATALOG_TYPE,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=steps.S3_ACCESS_KEY_ID,
            s3_secret_access_key=steps.S3_SECRET_ACCESS_KEY,
        )

    with And("create namespace"):
        steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"delete table {namespace}.{table_name} if already exists"):
        steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with When(f"define schema and create {namespace}.{table_name} table"):
        schema = Schema(
            NestedField(
                field_id=1, name="name", field_type=StringType(), required=False
            ),
            NestedField(
                field_id=2, name="double", field_type=DoubleType(), required=False
            ),
            NestedField(
                field_id=3, name="integer", field_type=LongType(), required=False
            ),
        )
        partition_spec = PartitionSpec(
            PartitionField(
                source_id=1,
                field_id=1001,
                transform=IdentityTransform(),
                name="symbol_partition",
            ),
        )
        sort_order = SortOrder(SortField(source_id=1, transform=IdentityTransform()))
        table = steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location="s3://warehouse/data",
            partition_spec=partition_spec,
            sort_order=sort_order,
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
            steps.drop_iceberg_table(
                catalog=catalog, namespace=namespace, table_name=table_name
            )
        with And(f"recreate table {namespace}.{table_name}"):
            table = steps.create_iceberg_table(
                catalog=catalog,
                namespace=namespace,
                table_name=table_name,
                schema=schema,
                location="s3://warehouse/data",
                partition_spec=partition_spec,
                sort_order=sort_order,
            )

    with And("scan and display data with pyiceberg, expect empty table"):
        df = table.scan().to_pandas()
        note(df)

    with And("read data in clickhouse using icebergS3 table function"):
        result = steps.read_data_with_icebergS3_table_function(
            storage_endpoint="http://minio:9000/warehouse/data",
            s3_access_key_id=steps.S3_ACCESS_KEY_ID,
            s3_secret_access_key=steps.S3_SECRET_ACCESS_KEY,
        )

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
        note(f"Table Name: {table.name()}")
        note(f"Schema: {table.schema()}")
        note(f"Location: {table.location()}")

    with And("read data in clickhouse using icebergS3 table function"):
        result = steps.read_data_with_icebergS3_table_function(
            storage_endpoint="http://minio:9000/warehouse/data",
            s3_access_key_id=steps.S3_ACCESS_KEY_ID,
            s3_secret_access_key=steps.S3_SECRET_ACCESS_KEY,
        )
        note(result.output)

    with And("create table with iceberg engine"):
        self.context.node.query(
            f"CREATE TABLE iceberg_table ENGINE=IcebergS3('http://minio:9000/warehouse/data', 'minio', 'minio123')"
        )
        self.context.node.query(f"SELECT * FROM iceberg_table")
        self.context.node.query(f"SELECT count() FROM iceberg_table")
        self.context.node.query(f"SHOW CREATE TABLE iceberg_table")

    with And("create table with s3 engine"):
        self.context.node.query(
            f"""
                CREATE TABLE p
                (
                    name Nullable(String), double Nullable(Float64), integer Nullable(Int64)  
                )
                ENGINE = S3(
                        'http://minio:9000/warehouse/data/data/*/*.parquet',
                        'minio',
                        'minio123',
                        'Parquet')
                ORDER BY ();
                """
        )
        self.context.node.query(f"SELECT * FROM p")
        self.context.node.query(f"SELECT count() FROM p")

    with Then("read data in clickhouse using s3 table function"):
        steps.read_data_with_s3_table_function(
            endpoint="http://minio:9000/warehouse/data/data/**/**.parquet",
            s3_access_key_id=steps.S3_ACCESS_KEY_ID,
            s3_secret_access_key=steps.S3_SECRET_ACCESS_KEY,
        )


@TestFeature
def icebergS3_table_function(self):
    Scenario(run=sanity)
    Scenario(run=recreate_table)
