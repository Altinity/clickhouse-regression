from testflows.core import *
from testflows.asserts import error

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine
import iceberg.tests.steps.icebergS3 as icebergS3

from helpers.common import getuid
from iceberg.tests.iceberg_engine.alter_support import insert_random_rows_into_tables
from helpers.tables import Column, create_table
import iceberg.tests.steps.common as common
import pyarrow as pa

from helpers.datatypes import (
    Array,
    Date32,
    DateTime64,
    Float32,
    Float64,
    Int32,
    Int64,
    Map,
    Nullable,
    String,
    Tuple,
    UUID,
)

import time
import random


@TestScenario
def native_create_table(self, minio_root_user, minio_root_password):
    """Check that CREATE TABLE operation is supported for tables from
    DataLakeCatalog database."""
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    iceberg_table_name = f"iceberg_table_{getuid()}"

    with Given("create iceberg catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("create DataLakeCatalog database"):
        database_name = f"datalake_db_{getuid()}"
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create Iceberg table with three columns directly from ClickHouse"):
        columns = [
            Column(name="int32_col", datatype=Int32()),
            Column(name="float64_col", datatype=Float64()),
            Column(name="string_col", datatype=String()),
        ]
        clickhouse_iceberg_table_name = (
            f"{database_name}.\\`{namespace}.{iceberg_table_name}\\`"
        )
        iceberg_table = create_table(
            name=clickhouse_iceberg_table_name,
            engine=(
                f"IcebergS3('http://minio:9000/warehouse/data/{namespace}/{iceberg_table_name}/', "
                f"'{minio_root_user}', '{minio_root_password}')"
            ),
            columns=columns,
            query_settings=("write_full_path_in_iceberg_metadata = 1"),
            order_by=("int32_col"),
            partition_by=("int32_col"),
        )
        insert_random_rows_into_tables(
            tables=[iceberg_table],
            row_count=10,
        )

    with And("select data from table"):
        result_before = self.context.node.query(
            f"""
            SELECT * FROM {clickhouse_iceberg_table_name} 
            ORDER BY tuple(*) 
            FORMAT TabSeparated
            """
        )


@TestFeature
@Name("native create drop")
def feature(self, minio_root_user, minio_root_password):
    """Check that CREATE and DROP TABLE operations are supported for tables from
    DataLakeCatalog database."""
    Scenario(test=native_create_table)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
