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
def iceberg_engine(self):
    """Test Iceberg table creation and data insertion."""
    node = self.context.node
    s3_access_key_id = "minio"
    s3_secret_access_key = "minio123"
    catalog_type = "rest"

    with Given("create catalog"):
        catalog = steps.create_catalog(
            uri="http://localhost:8182/",
            catalog_type=catalog_type,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=s3_access_key_id,
            s3_secret_access_key=s3_secret_access_key,
        )

    with And("create namespace"):
        namespace = "iceberg"
        steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("delete table iceberg.bids if already exists"):
        table_name = "bids"
        steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with When("define schema and create iceberg.bids table"):
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

    with And("insert data into iceberg.bids table"):
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

    with Then("read data from clickhouse using iceberg table engine"):
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
        node.query("SHOW TABLES from datalake")
        steps.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )
        steps.show_create_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )


@TestFeature
def feature(self):
    Scenario(run=iceberg_engine)
