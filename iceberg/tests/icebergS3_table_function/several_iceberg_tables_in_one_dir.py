#!/usr/bin/env python3

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

import pyarrow as pa
import random

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.icebergS3 as icebergS3
import iceberg.tests.steps.iceberg_engine as iceberg_engine

from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema, NestedField
from pyiceberg.types import (
    StringType,
    IntegerType,
    LongType,
    FloatType,
    DoubleType,
    TimestampType,
    BooleanType,
    TimestamptzType,
    DateType,
    TimeType,
    UUIDType,
    BinaryType,
    DecimalType,
    StructType,
    ListType,
    MapType,
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.table.sorting import SortOrder, SortField
from pyiceberg.transforms import IdentityTransform

from iceberg.tests.steps.catalog import create_iceberg_table, random_name


@TestScenario
def sanity(self, minio_root_user, minio_root_password):
    """Test Iceberg table creation and reading data from ClickHouse using
    icebergS3 table function."""
    namespace = f"icebergS3_{getuid()}"
    number_of_tables = 4
    table_names = [f"table_{getuid()}_{i}" for i in range(number_of_tables)]
    number_of_rows = 10

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"define schema for tables"):
        schema = Schema(
            NestedField(
                field_id=1, name="name", field_type=StringType(), required=False
            ),
        )
        sort_order = SortOrder(SortField(source_id=1, transform=IdentityTransform()))
        partition_spec = PartitionSpec(
            PartitionField(
                source_id=1,
                field_id=1001,
                transform=IdentityTransform(),
                name="name",
            ),
        )

    with And(f"create {number_of_tables} tables and populate them with data"):
        tables = []
        for table_number, table_name in enumerate(table_names):
            table = create_iceberg_table(
                catalog=catalog,
                namespace=namespace,
                table_name=table_name,
                schema=schema,
                location="s3://warehouse/data",
                partition_spec=partition_spec,
                sort_order=sort_order,
            )
            data = []
            for i in range(number_of_rows):
                data.append(
                    {
                        "name": f"table_number_{table_number}_row_{i}",
                    }
                )
            df = pa.Table.from_pylist(data)
            table.append(df)
            tables.append(table)

    with And("constract expected result"):
        expected_results = []
        for table_number in range(number_of_tables):
            for i in range(number_of_rows):
                expected_result_list = [
                    f"table_number_{table_number}_row_{i}"
                    for i in range(number_of_rows)
                ]
                expected_result = "\n".join(expected_result_list)
                expected_results.append(expected_result)

    with And(
        "read data in clickhouse using icebergS3 table function and check if it's correct"
    ):
        note(table_names)
        for table_number, (table_name, table) in enumerate(zip(table_names, tables)):
            with By(f"read data from table number {table_number}"):
                # Retrieve the table UUID from the PyIceberg table metadata
                table_uuid = table.metadata.table_uuid
                note(f"Table {table_number} UUID: {table_uuid}")
                
                result = icebergS3.read_data_with_icebergS3_table_function(
                    storage_endpoint="http://minio:9000/warehouse/data",
                    s3_access_key_id=minio_root_user,
                    s3_secret_access_key=minio_root_password,
                    format="TabSeparated",
                    order_by="tuple(*)",
                    iceberg_metadata_table_uuid=table_uuid,
                )
                note(f"table number {table_number}")
                note("expected results")
                note(expected_results[table_number])
                assert result.output.strip() == expected_results[table_number], error()


@TestFeature
@Name("several iceberg tables in one dir")
def several_iceberg_tables_in_one_dir(self, minio_root_user, minio_root_password):
    self.context.catalog = "rest"
    Scenario(test=sanity)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
