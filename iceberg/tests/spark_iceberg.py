#!/usr/bin/env python3

import sys

from testflows.core import *

import pyarrow as pa

import pyiceberg
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    DoubleType,
    StringType,
    NestedField,
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.table.sorting import SortOrder, SortField
from pyiceberg.transforms import IdentityTransform

import time


@TestScenario
def test_iceberg(self):
    """Test Iceberg table creation and data insertion."""
    node = self.context.node
    with Given("create catalog"):
        catalog = load_catalog(
            "rest",
            **{
                "uri": "http://localhost:8182/",  # REST server URL
                "type": "rest",
                "s3.endpoint": f"http://localhost:9002",  # Minio URI and credentials
                "s3.access-key-id": "minio",
                "s3.secret-access-key": "minio123",
            },
        )

    with And("create namespace and list namespaces"):
        namespace_name = "iceberg"
        try:
            catalog.create_namespace(namespace_name)
        except pyiceberg.exceptions.NamespaceAlreadyExistsError:
            note("Already exists")

        ns_list = catalog.list_namespaces()
        for ns in ns_list:
            note(ns)

    with And("delete table iceberg.bids if already exists"):
        table_list = catalog.list_tables("iceberg")
        for table in table_list:
            note(f"{table}, {type(table)}")
            if table[0] == "iceberg" and table[1] == "bids":
                note("Dropping bids table")
                catalog.drop_table("iceberg.bids")

    with When("define schema and create iceberg.bids table"):
        schema = Schema(
            NestedField(
                field_id=1, name="symbol", field_type=StringType(), required=False
            ),
            NestedField(
                field_id=2, name="bid", field_type=DoubleType(), required=False
            ),
            NestedField(
                field_id=3, name="ask", field_type=DoubleType(), required=False
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
        time.sleep(20)
        table = catalog.create_table(
            identifier="iceberg.bids",
            schema=schema,
            location="s3://warehouse/data",
            sort_order=sort_order,
            partition_spec=partition_spec,
        )

    with And("insert data into iceberg.bids table"):
        df = pa.Table.from_pylist(
            [
                {"symbol": "AAPL", "bid": 195.23, "ask": 195.28},
                {"symbol": "AAPL", "bid": 195.22, "ask": 195.28},
                {"symbol": "AAPL", "bid": 195.25, "ask": 195.30},
                {"symbol": "AAPL", "bid": 195.24, "ask": 195.31},
            ],
        )
        table.append(df)

    with And("scan and display data"):
        df = table.scan().to_pandas()
        note(df)

    with Then("read data from clickhouse using table function"):
        node.query(
            f"""
            SELECT * FROM s3('http://minio:9000/warehouse/data/data/**/**.parquet', 'minio', 'minio123')
        """
        )

    with Then("read data from clickhouse using iceberg table engine"):
        node.query(
            f"""
            DROP DATABASE IF EXISTS datalake;
            SET allow_experimental_database_iceberg=true;
            CREATE DATABASE datalake
            ENGINE = Iceberg('http://rest:8181/v1', 'minio', 'minio123')
            SETTINGS catalog_type = 'rest', storage_endpoint = 'http://minio:9000/warehouse', warehouse = 'iceberg';
        """
        )
        node.query("SHOW TABLES from datalake")
        node.query(f"SELECT * FROM datalake.\`iceberg.bids\`")


@TestFeature
def feature(self):
    Scenario(run=test_iceberg)
