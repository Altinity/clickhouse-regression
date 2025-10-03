#!/usr/bin/env python3

from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import product

from helpers.common import getuid
from iceberg.tests.steps.datatypes import *
from iceberg.tests.steps.iceberg_table_class import IcebergTestTable

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine


ALL_DATATYPES = [
    IcebergIntegerType(required=True),
    IcebergLongType(required=True),
    IcebergDoubleType(required=True),
    IcebergFloatType(required=True),
    IcebergBooleanType(required=True),
    IcebergTimestampType(),
    IcebergTimestamptzType(),
    IcebergDateType(),
    IcebergStringType(),
    IcebergFixedStringType(),
    # IcebergUUIDType(),
    IcebergBinaryType(),
    IcebergDecimalType(),
    IcebergTimeType(),
]

WHERE_CLAUSE_TYPES = [
    IcebergIntegerType(),
    IcebergLongType(),
    IcebergDoubleType(),
    IcebergBooleanType(),
    IcebergTimestampType(),
    IcebergTimestamptzType(),
    IcebergDateType(),
    IcebergStringType(),
    IcebergBinaryType(),
    IcebergDecimalType(),
    # IcebergFloatType(),
    # IcebergTimeType(),
    # IcebergFixedStringType(),
    # IcebergUUIDType(),
]

EXPLICIT_WHERE_OUTPUT_TYPES = [
    IcebergIntegerType(),
    IcebergLongType(),
    IcebergDoubleType(),
    IcebergBooleanType(),
    IcebergStringType(),
    IcebergBinaryType(),
    IcebergDecimalType(),
]

operators = [
    "=",
    "!=",
    ">",
    "<",
    ">=",
    "<=",
]


@TestScenario
def data_types_check_where(self, minio_root_user, minio_root_password):
    """Test that ClickHouse correctly reads all Iceberg data types with
    and without where clause."""
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_database_{getuid()}"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("create database with DataLakeCatalog engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("create iceberg test table with all datatypes"):
        iceberg_table = IcebergTestTable(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            datatypes=ALL_DATATYPES,
        )

    with When("insert 5 rows"):
        inserted_rows = iceberg_table.insert(rows_num=20)

    with Then("check data in clickhouse iceberg table"):
        iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns="*",
        )

    with And("query data with where clauses on different types"):
        for dt, operator in product(WHERE_CLAUSE_TYPES, operators):
            value = inserted_rows[0][dt.name]
            where_clause = dt.filter_clause(
                dt.name, value=value, comparison_operator=operator
            )
            note(
                f"dt: {dt.name}, operator: {operator}, value: {value}, where_clause: {where_clause}"
            )
            result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                columns="count()",
                where_clause=where_clause,
            )
            expected = iceberg_table.expected_where_count(dt.name, operator, value)
            assert result.output.strip() == str(expected), error()

    with And("query data with where clauses on different types and compare output"):
        for dt, operator in product(EXPLICIT_WHERE_OUTPUT_TYPES, operators):
            value = inserted_rows[0][dt.name]
            where_clause = dt.filter_clause(
                dt.name, value=value, comparison_operator=operator
            )
            note(
                f"dt: {dt.name}, operator: {operator}, value: {value}, where_clause: {where_clause}"
            )
            result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                columns=dt.name,
                where_clause=where_clause,
            )
            expected = iceberg_table.expected_where_result(dt.name, operator, value)
            assert result.output.strip() == str(expected), error()


@TestFeature
@Name("datatypes")
def feature(self, minio_root_user, minio_root_password):
    """Check that ClickHouse correctly reads all Iceberg data types."""
    Scenario(test=data_types_check_where)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
