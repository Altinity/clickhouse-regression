from testflows.core import *
from testflows.combinatorics import product

from helpers.common import getuid

from pyiceberg.expressions import (
    GreaterThan,
    LessThan,
    GreaterThanOrEqual,
    LessThanOrEqual,
    NotEqualTo,
    EqualTo,
    And as pyiceberg_And,
    Or,
    Not,
    IsNull,
    NotNull,
    In,
    NotIn,
    StartsWith,
    NotStartsWith,
)

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.common as common
import iceberg.tests.steps.iceberg_engine as iceberg_engine

import random

random.seed(42)


@TestStep(Given)
def delete_equal_to(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows from MergeTree and Iceberg tables where column is equal to value."""
    with By("get reference value"):
        value = common.get_random_value_from_table(
            column=column, table_name=merge_tree_table_name
        )
        if value is None:
            return

    with And("create delete condition for MergeTree table"):
        merge_tree_condition = f"{column} = '{value}'"

    with And("create delete condition for Iceberg table"):
        if column == "double_col":
            value = float(value)
        elif column == "long_col":
            value = int(value)

        iceberg_condition = EqualTo(column, value)

    with And("delete same rows from both tables"):
        common.delete_rows_from_merge_tree_table(
            table_name=merge_tree_table_name, condition=merge_tree_condition
        )
        catalog_steps.delete_transaction(
            iceberg_table=iceberg_table, condition=iceberg_condition
        )


@TestStep(Given)
def delete_not_equal_to(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows from MergeTree and Iceberg tables where column is not equal to value."""
    with By("get reference value"):
        value = common.get_random_value_from_table(
            column=column, table_name=merge_tree_table_name
        )
        if value is None:
            return

    with And("create delete condition for MergeTree table"):
        merge_tree_condition = f"{column} != '{value}'"

    with And("create delete condition for Iceberg table"):
        if column == "double_col":
            value = float(value)
        elif column == "long_col":
            value = int(value)

        iceberg_condition = NotEqualTo(column, value)

    with And("delete same rows from both tables"):
        common.delete_rows_from_merge_tree_table(
            table_name=merge_tree_table_name, condition=merge_tree_condition
        )
        catalog_steps.delete_transaction(
            iceberg_table=iceberg_table, condition=iceberg_condition
        )


@TestStep(Given)
def delete_greater_than(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows from MergeTree and Iceberg tables where column is greater than value."""
    with By("get reference value"):
        value = common.get_random_value_from_table(
            column=column, table_name=merge_tree_table_name
        )
        if value is None:
            return

    with And("create delete condition for MergeTree table"):
        merge_tree_condition = f"{column} > '{value}'"

    with And("create delete condition for Iceberg table"):
        if column == "double_col":
            value = float(value)
        elif column == "long_col":
            value = int(value)

        iceberg_condition = GreaterThan(column, value)

    with And("delete same rows from both tables"):
        common.delete_rows_from_merge_tree_table(
            table_name=merge_tree_table_name, condition=merge_tree_condition
        )
        catalog_steps.delete_transaction(
            iceberg_table=iceberg_table, condition=iceberg_condition
        )


@TestStep(Given)
def delete_less_than(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows from MergeTree and Iceberg tables where column is less than value."""
    with By("get reference value"):
        value = common.get_random_value_from_table(
            column=column, table_name=merge_tree_table_name
        )
        if value is None:
            return

    with And("create delete condition for MergeTree table"):
        merge_tree_condition = f"{column} < '{value}'"

    with And("create delete condition for Iceberg table"):
        if column == "double_col":
            value = float(value)
        elif column == "long_col":
            value = int(value)

        iceberg_condition = LessThan(column, value)

    with And("delete same rows from both tables"):
        common.delete_rows_from_merge_tree_table(
            table_name=merge_tree_table_name, condition=merge_tree_condition
        )
        catalog_steps.delete_transaction(
            iceberg_table=iceberg_table, condition=iceberg_condition
        )


@TestStep(Given)
def delete_greater_than_or_equal(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows from MergeTree and Iceberg tables where column is greater than or equal to value."""
    with By("get reference value"):
        value = common.get_random_value_from_table(
            column=column, table_name=merge_tree_table_name
        )
        if value is None:
            return

    with And("create delete condition for MergeTree table"):
        merge_tree_condition = f"{column} >= '{value}'"

    with And("create delete condition for Iceberg table"):
        if column == "double_col":
            value = float(value)
        elif column == "long_col":
            value = int(value)

        iceberg_condition = GreaterThanOrEqual(column, value)

    with And("delete same rows from both tables"):
        common.delete_rows_from_merge_tree_table(
            table_name=merge_tree_table_name, condition=merge_tree_condition
        )
        catalog_steps.delete_transaction(
            iceberg_table=iceberg_table, condition=iceberg_condition
        )


@TestStep(Given)
def delete_less_than_or_equal(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows from MergeTree and Iceberg tables where column is less than or equal to value."""
    with By("get reference value"):
        value = common.get_random_value_from_table(
            column=column, table_name=merge_tree_table_name
        )
        if value is None:
            return

    with And("create delete condition for MergeTree table"):
        merge_tree_condition = f"{column} <= '{value}'"

    with And("create delete condition for Iceberg table"):
        if column == "double_col":
            value = float(value)
        elif column == "long_col":
            value = int(value)

        iceberg_condition = LessThanOrEqual(column, value)

    with And("delete same rows from both tables"):
        common.delete_rows_from_merge_tree_table(
            table_name=merge_tree_table_name, condition=merge_tree_condition
        )
        catalog_steps.delete_transaction(
            iceberg_table=iceberg_table, condition=iceberg_condition
        )


@TestStep(Given)
def delete_is_null(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows from MergeTree and Iceberg tables where column is null."""
    with By("create delete condition for MergeTree table"):
        merge_tree_condition = f"{column} IS NULL"

    with And("create delete condition for Iceberg table"):
        iceberg_condition = IsNull(column)

    with And("delete same rows from both tables"):
        common.delete_rows_from_merge_tree_table(
            table_name=merge_tree_table_name, condition=merge_tree_condition
        )
        catalog_steps.delete_transaction(
            iceberg_table=iceberg_table, condition=iceberg_condition
        )


@TestStep(Given)
def delete_is_not_null(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows from MergeTree and Iceberg tables where column is not null."""
    with By("create delete condition for MergeTree table"):
        merge_tree_condition = f"{column} IS NOT NULL"

    with And("create delete condition for Iceberg table"):
        iceberg_condition = NotNull(column)

    with And("delete same rows from both tables"):
        common.delete_rows_from_merge_tree_table(
            table_name=merge_tree_table_name, condition=merge_tree_condition
        )
        catalog_steps.delete_transaction(
            iceberg_table=iceberg_table, condition=iceberg_condition
        )


@TestStep(Given)
def delete_in(self, merge_tree_table_name, iceberg_table, column, range_length=10):
    """Delete rows from MergeTree and Iceberg tables where column is in values."""
    with By("get reference values"):
        values_str = common.get_random_value_from_table(
            column=column, table_name=merge_tree_table_name, number=range_length
        )
        if values_str is None:
            return

        values = []
        for value in values_str:
            if column == "double_col":
                value = float(value)
            elif column == "long_col":
                value = int(value)
            values.append(value)

    with And("create delete condition for MergeTree table"):
        merge_tree_condition = (
            f"""{column} IN ({', '.join(f"'{value}'" for value in values_str)})"""
        )

    with And("create delete condition for Iceberg table"):
        iceberg_condition = In(column, values)

    with And("delete same rows from both tables"):
        common.delete_rows_from_merge_tree_table(
            table_name=merge_tree_table_name, condition=merge_tree_condition
        )
        catalog_steps.delete_transaction(
            iceberg_table=iceberg_table, condition=iceberg_condition
        )


@TestStep(Given)
def delete_not_in(self, merge_tree_table_name, iceberg_table, column, range_length=10):
    """Delete rows from MergeTree and Iceberg tables where column is not in values."""
    with By("get reference values"):
        values_str = common.get_random_value_from_table(
            column=column, table_name=merge_tree_table_name, number=range_length
        )
        if values_str is None:
            return

        values = []
        for value in values_str:
            if column == "double_col":
                value = float(value)
            elif column == "long_col":
                value = int(value)
            values.append(value)

    with And("create delete condition for MergeTree table"):
        merge_tree_condition = (
            f"""{column} NOT IN ({', '.join(f"'{value}'" for value in values_str)})"""
        )

    with And("create delete condition for Iceberg table"):
        iceberg_condition = NotIn(column, values)

    with And("delete same rows from both tables"):
        common.delete_rows_from_merge_tree_table(
            table_name=merge_tree_table_name, condition=merge_tree_condition
        )
        catalog_steps.delete_transaction(
            iceberg_table=iceberg_table, condition=iceberg_condition
        )


@TestStep(Given)
def delete_starts_with(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows from MergeTree and Iceberg tables where column starts with value."""
    if column != "string_col":
        return

    with By("get reference value"):
        value = common.get_random_value_from_table(
            column=column, table_name=merge_tree_table_name
        )
        if value is None:
            return

    with And("create delete condition for MergeTree table"):
        merge_tree_condition = f"{column} LIKE '{value}%'"

    with And("create delete condition for Iceberg table"):
        iceberg_condition = StartsWith(column, value)

    with And("delete same rows from both tables"):
        common.delete_rows_from_merge_tree_table(
            table_name=merge_tree_table_name, condition=merge_tree_condition
        )
        catalog_steps.delete_transaction(
            iceberg_table=iceberg_table, condition=iceberg_condition
        )


@TestStep(Given)
def delete_not_starts_with(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows from MergeTree and Iceberg tables where column does not start with value."""
    if column != "string_col":
        return

    with By("get reference value"):
        value = common.get_random_value_from_table(
            column=column, table_name=merge_tree_table_name
        )
        if value is None:
            return

    with And("create delete condition for MergeTree table"):
        merge_tree_condition = f"{column} NOT LIKE '{value}%'"

    with And("create delete condition for Iceberg table"):
        iceberg_condition = NotStartsWith(column, value)

    with And("delete same rows from both tables"):
        common.delete_rows_from_merge_tree_table(
            table_name=merge_tree_table_name, condition=merge_tree_condition
        )
        catalog_steps.delete_transaction(
            iceberg_table=iceberg_table, condition=iceberg_condition
        )


@TestStep(Given)
def add_data(self, merge_tree_table_name, iceberg_table, num_rows=10):
    """Add same data to MergeTree and Iceberg tables."""
    common.insert_same_data_to_iceberg_and_merge_tree_tables(
        iceberg_table=iceberg_table,
        merge_tree_table_name=merge_tree_table_name,
        num_rows=num_rows,
    )


@TestScenario
# @Flags(TE)
def equality_delete(self, minio_root_user, minio_root_password, actions, node=None):
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

    with When(
        f"create namespace, define schema and create {namespace}.{table_name} table"
    ):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)
        iceberg_table = catalog_steps.create_iceberg_table_with_five_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with Then("create database with Iceberg engine"):
        database_name = f"iceberg_database_{getuid()}"
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

    with And("perform delete actions"):
        for action in actions:
            action(
                merge_tree_table_name=merge_tree_table_name, iceberg_table=iceberg_table
            )

    with And("compare data from ClickHouse Iceberg and MergeTree tables"):
        iceberg_result = common.get_select_query_result(
            table_name=f"{database_name}.\\`{namespace}.{table_name}\\`",
            order_by="tuple(*)",
        )
        merge_tree_result = common.get_select_query_result(
            table_name=merge_tree_table_name, order_by="tuple(*)"
        )
        common.compare_results(iceberg_result.output, merge_tree_result.output)


@TestScenario
def run_equality_deletes_combinations(self, minio_root_user, minio_root_password):
    """Run all possible combinations of delete scenarios from Iceberg table.
    Compare results with same deletes from MergeTree table."""

    with Given("define set of columns and delete/insert actions"):
        columns = ["boolean_col", "long_col", "double_col", "string_col", "date_col"]
        actions = [
            delete_equal_to,
            delete_not_equal_to,
            delete_greater_than,
            delete_less_than,
            delete_greater_than_or_equal,
            delete_less_than_or_equal,
            delete_is_null,
            delete_is_not_null,
            delete_in,
            delete_not_in,
            delete_starts_with,
            delete_not_starts_with,
        ]

    with And("create partial functions for each action with every column"):
        actions_with_columns = []
        for action, column in product(actions, columns):
            actions_with_columns.append(partial(action, column=column))

    with And("add insert action"):
        actions_with_columns.append(add_data)

    for num in range(100):
        actions_list = random.sample(
            actions_with_columns, random.randint(1, len(actions_with_columns))
        )

        if not isinstance(actions_list, (tuple, list)):
            actions_list = (actions_list,)  # Make iterable

        Check(f"#{num}", test=equality_delete)(
            actions=actions_list,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=run_equality_deletes_combinations)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
