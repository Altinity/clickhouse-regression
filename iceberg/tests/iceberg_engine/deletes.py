#!/usr/bin/env python3

from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import product

import pyarrow as pa

import math

from helpers.common import getuid

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.common as common
import iceberg.tests.steps.iceberg_engine as iceberg_engine

from pyiceberg.expressions import (
    GreaterThan,
    LessThan,
    GreaterThanOrEqual,
    LessThanOrEqual,
    NotEqualTo,
    EqualTo,
)


def parse_table_output(output):
    """Parses a tab-separated string output into a list of lists with appropriate types."""
    rows = output.strip().split("\n")
    parsed_data = []

    for row in rows:
        values = row.split("\t")
        parsed_row = []
        for value in values:
            # Try to convert to int, then float, otherwise keep as string
            if value.isdigit():
                parsed_row.append(int(value))
            else:
                try:
                    parsed_row.append(float(value))
                except ValueError:
                    parsed_row.append(value)
        parsed_data.append(parsed_row)

    return parsed_data


def compare_results(iceberg_output, merge_tree_output, rel_tol=1e-3, abs_tol=1e-3):
    iceberg_data = parse_table_output(iceberg_output)
    merge_tree_data = parse_table_output(merge_tree_output)

    if len(iceberg_data) != len(merge_tree_data):
        return False

    for row1, row2 in zip(iceberg_data, merge_tree_data):
        if len(row1) != len(row2):
            return False

        for val1, val2 in zip(row1, row2):
            if isinstance(val1, float) and isinstance(val2, float):
                if not math.isclose(val1, val2, rel_tol=rel_tol, abs_tol=abs_tol):
                    return False
            elif val1 != val2:
                return False
    return True


@TestScenario
# @Flags(TE)
def delete_sanity(
    self, minio_root_user, minio_root_password, column, expression, node=None
):
    """Test that ClickHouse can read data from Iceberg table after
    deleting some rows from Iceberg table."""
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

    with And(f"delete table {namespace}.{table_name} if already exists"):
        catalog_steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with When(f"define schema and create {namespace}.{table_name} table"):
        iceberg_table = catalog_steps.create_iceberg_table_with_five_columns(
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

    with And("create MergeTree table with same structure"):
        merge_tree_table_name = "merge_tree_table_" + getuid()
        common.create_merge_tree_table(table_name=merge_tree_table_name)

    with And("insert same data into both tables"):
        num_rows = 100
        common.insert_same_data_to_iceberg_and_merge_tree_tables(
            iceberg_table=iceberg_table,
            merge_tree_table_name=merge_tree_table_name,
            num_rows=num_rows,
        )

    with And("compare data from ClickHouse Iceberg and MergeTree tables"):
        iceberg_result = common.get_select_query_result(
            table_name=f"{database_name}.\\`{namespace}.{table_name}\\`",
            order_by="tuple(*)",
        )
        merge_tree_result = common.get_select_query_result(
            table_name=merge_tree_table_name, order_by="tuple(*)"
        )
        compare_results(iceberg_result.output, merge_tree_result.output)

    with And("create delete condition for MergeTree table"):
        value = common.get_random_value_from_table(
            column=column, table_name=merge_tree_table_name
        )
        merge_tree_condition = f"{column} {expression[0]} '{value}'"

    with And("create delete condition for Iceberg table"):
        if column == "double_col":
            value = float(value)
        elif column == "long_col":
            value = int(value)

        iceberg_condition = expression[1](column, value)

    with And("delete same rows from both tables"):
        common.delete_rows_from_merge_tree_table(
            table_name=merge_tree_table_name, condition=merge_tree_condition
        )
        note(merge_tree_condition)
        catalog_steps.delete_transaction(
            iceberg_table=iceberg_table, condition=iceberg_condition
        )

    with And("compare data from ClickHouse Iceberg and MergeTree tables"):
        iceberg_result = common.get_select_query_result(
            table_name=f"{database_name}.\\`{namespace}.{table_name}\\`",
            order_by="tuple(*)",
        )
        merge_tree_result = common.get_select_query_result(
            table_name=merge_tree_table_name, order_by="tuple(*)"
        )
        compare_results(iceberg_result.output, merge_tree_result.output)


@TestScenario
def run_deletes_combinations(self, minio_root_user, minio_root_password):
    """Run all possible combinations of delete scenarios from Iceberg table.
    Compare results with same deletes from MergeTree table."""

    columns = ["boolean_col", "long_col", "double_col", "string_col", "date_col"]
    expressions = [
        ("=", EqualTo),
        (">", GreaterThan),
        ("<", LessThan),
        (">=", GreaterThanOrEqual),
        ("<=", LessThanOrEqual),
        ("!=", NotEqualTo),
    ]
    for num, combination in enumerate(product(columns, expressions)):
        column, expression = combination
        Check(f"#{num}", test=delete_sanity)(
            column=column,
            expression=expression,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=run_deletes_combinations)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
