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
from swarms.tests.feature import feature


@TestCheck
@Name("read iceberg table with icebergS3 table function")
def read_iceberg_table_with_icebergS3_table_function(
    self,
    table_uuid,
    expected_result,
    minio_root_user,
    minio_root_password,
):
    with Then("read data with icebergS3 table function"):
        result = icebergS3.read_data_with_icebergS3_table_function(
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            order_by="tuple(*)",
            iceberg_metadata_table_uuid=table_uuid,
        )
        assert result.output.strip() == expected_result.strip(), error()


@TestCheck
@Name("read iceberg table with icebergS3Cluster table function")
def read_iceberg_table_with_icebergS3Cluster_table_function(
    self,
    table_uuid,
    expected_result,
    minio_root_user,
    minio_root_password,
    cluster_name="replicated_cluster",
):
    with Then("read data with icebergS3Cluster table function"):
        result = icebergS3.read_data_with_icebergS3Cluster_table_function(
            cluster_name=cluster_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            order_by="tuple(*)",
            iceberg_metadata_table_uuid=table_uuid,
        )
        assert result.output.strip() == expected_result.strip(), error()


@TestCheck
@Name("read with DataLakeCatalog database")
def read_iceberg_table_with_DataLakeCatalog_database(
    self,
    database_name,
    namespace,
    table_name,
    expected_result,
):
    with Then("read data with DataLakeCatalog database"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            order_by="tuple(*)",
        )
        assert result.output.strip() == expected_result.strip(), error()


@TestFeature
def check_several_iceberg_tables_in_one_dir(
    self, minio_root_user, minio_root_password, with_partitioning=False
):
    """Check that several iceberg tables in one directory can be read correctly using icebergS3,
    icebergS3Cluster table functions and DataLakeCatalog database."""

    database_name = f"database_{getuid()}"
    namespace = f"namespace_{getuid()}"

    number_of_rows = 10
    number_of_tables = 20
    table_names = [f"table_{getuid()}_{i}" for i in range(number_of_tables)]
    number_of_rows = 10

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"define schema and partition spec for tables"):
        schema = Schema(
            NestedField(
                field_id=1, name="name", field_type=StringType(), required=False
            ),
        )
        if with_partitioning:
            partition_spec = PartitionSpec(
                PartitionField(
                    source_id=1,
                    field_id=1001,
                    transform=IdentityTransform(),
                    name="name",
                ),
            )
        else:
            partition_spec = PartitionSpec()

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
                sort_order=SortOrder(),
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
            table.append(df)

            tables.append(table)

    with And("create DataLakeCatalog database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with When("construct expected result"):
        expected_results = []
        for table_number in range(number_of_tables):
            expected_result_list = [
                f"table_number_{table_number}_row_{i}" for i in range(number_of_rows)
            ] * 2
            expected_result_list.sort()
            expected_result = "\n".join(expected_result_list)
            expected_results.append(expected_result)

    # read with icebergS3 table function
    with Pool(5) as pool:
        for table_number, (table_name, table) in enumerate(zip(table_names, tables)):
            table_uuid = table.metadata.table_uuid
            Check(
                name=f"read data from table #{table_number}/{number_of_tables} with icebergS3",
                test=read_iceberg_table_with_icebergS3_table_function,
                parallel=True,
                executor=pool,
            )(
                table_uuid=table_uuid,
                expected_result=expected_results[table_number],
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
        join()

    # read with icebergS3Cluster table function
    with Pool(5) as pool:
        for table_number, (table_name, table) in enumerate(zip(table_names, tables)):
            table_uuid = table.metadata.table_uuid
            Check(
                name=f"read data from table #{table_number}/{number_of_tables} with icebergS3Cluster",
                test=read_iceberg_table_with_icebergS3Cluster_table_function,
                parallel=True,
                executor=pool,
            )(
                table_uuid=table_uuid,
                cluster_name="replicated_cluster",
                expected_result=expected_results[table_number],
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
        join()

    # read with DataLakeCatalog database
    with Pool(5) as pool:
        for table_number, (table_name, table) in enumerate(zip(table_names, tables)):
            table_uuid = table.metadata.table_uuid
            Check(
                name=f"read data from table #{table_number}/{number_of_tables} with DataLakeCatalog",
                test=read_iceberg_table_with_DataLakeCatalog_database,
                parallel=True,
                executor=pool,
            )(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                expected_result=expected_results[table_number],
            )
        join()


@TestFeature
@Name("several iceberg tables in one dir")
def several_iceberg_tables_in_one_dir(self, minio_root_user, minio_root_password):
    Feature(name="without partitioning", test=check_several_iceberg_tables_in_one_dir)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Feature(name="with partitioning", test=check_several_iceberg_tables_in_one_dir)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        with_partitioning=True,
    )
