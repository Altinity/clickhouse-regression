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


def perform_delete(
    merge_tree_table_name,
    iceberg_table,
    merge_tree_condition,
    iceberg_condition,
):
    """Helper function to delete rows from both given MergeTree and Iceberg tables."""
    common.delete_rows_from_merge_tree_table(
        table_name=merge_tree_table_name, condition=merge_tree_condition
    )
    catalog_steps.delete_transaction(
        iceberg_table=iceberg_table, condition=iceberg_condition
    )


def convert_value(column, value):
    """Convert value to appropriate numeric type for Iceberg."""
    if column == "double_col":
        return float(value)
    elif column == "long_col":
        return int(value)
    return value


def get_reference_value(column, merge_tree_table_name, range_length=1):
    """Get a random reference value(s) from given MergeTree table."""
    values = common.get_random_value_from_table(
        column=column,
        table_name=merge_tree_table_name,
        number=range_length,
    )
    if not values:
        return None

    if range_length > 1:
        return [convert_value(column, v) for v in values]

    return convert_value(column, values)


@TestStep(Given)
def delete_equal_to(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows where given column value is equal to some value."""
    if (value := get_reference_value(column, merge_tree_table_name)) is None:
        return

    perform_delete(
        merge_tree_table_name=merge_tree_table_name,
        merge_tree_condition=f"{column} = '{value}'",
        iceberg_table=iceberg_table,
        iceberg_condition=EqualTo(column, value),
    )


@TestStep(Given)
def delete_not_equal_to(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows where given column is not equal to some value."""
    if (value := get_reference_value(column, merge_tree_table_name)) is None:
        return

    perform_delete(
        merge_tree_table_name=merge_tree_table_name,
        merge_tree_condition=f"{column} != '{value}'",
        iceberg_table=iceberg_table,
        iceberg_condition=NotEqualTo(column, value),
    )


@TestStep(Given)
def delete_greater_than(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows where given column value is greater than some value."""
    if (value := get_reference_value(column, merge_tree_table_name)) is None:
        return

    perform_delete(
        merge_tree_table_name=merge_tree_table_name,
        merge_tree_condition=f"{column} > '{value}'",
        iceberg_table=iceberg_table,
        iceberg_condition=GreaterThan(column, value),
    )


@TestStep(Given)
def delete_less_than(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows where given column value is less than some value."""
    if (value := get_reference_value(column, merge_tree_table_name)) is None:
        return

    perform_delete(
        merge_tree_table_name=merge_tree_table_name,
        merge_tree_condition=f"{column} < '{value}'",
        iceberg_table=iceberg_table,
        iceberg_condition=LessThan(column, value),
    )


@TestStep(Given)
def delete_greater_than_or_equal(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows where given column value is greater than or equal to some value."""
    if (value := get_reference_value(column, merge_tree_table_name)) is None:
        return

    perform_delete(
        merge_tree_table_name=merge_tree_table_name,
        merge_tree_condition=f"{column} >= '{value}'",
        iceberg_table=iceberg_table,
        iceberg_condition=GreaterThanOrEqual(column, value),
    )


@TestStep(Given)
def delete_less_than_or_equal(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows where given column value is less than or equal to some value."""
    if (value := get_reference_value(column, merge_tree_table_name)) is None:
        return

    perform_delete(
        merge_tree_table_name=merge_tree_table_name,
        merge_tree_condition=f"{column} <= '{value}'",
        iceberg_table=iceberg_table,
        iceberg_condition=LessThanOrEqual(column, value),
    )


@TestStep(Given)
def delete_is_null(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows where given column value is null."""
    perform_delete(
        merge_tree_table_name=merge_tree_table_name,
        merge_tree_condition=f"{column} IS NULL",
        iceberg_table=iceberg_table,
        iceberg_condition=IsNull(column),
    )


@TestStep(Given)
def delete_is_not_null(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows where given column value is not null."""
    perform_delete(
        merge_tree_table_name=merge_tree_table_name,
        merge_tree_condition=f"{column} IS NOT NULL",
        iceberg_table=iceberg_table,
        iceberg_condition=NotNull(column),
    )


@TestStep(Given)
def delete_in(self, merge_tree_table_name, iceberg_table, column, range_length=10):
    """Delete rows where given column value is in a list of values."""
    if (
        values := get_reference_value(
            column, merge_tree_table_name, range_length=range_length
        )
    ) is None:
        return

    perform_delete(
        merge_tree_table_name=merge_tree_table_name,
        merge_tree_condition=f"""{column} IN ({', '.join(f"'{value}'" for value in values)})""",
        iceberg_table=iceberg_table,
        iceberg_condition=In(column, values),
    )


@TestStep(Given)
def delete_not_in(self, merge_tree_table_name, iceberg_table, column, range_length=10):
    """Delete rows where given column value is not in a list of values."""
    if (
        values := get_reference_value(
            column, merge_tree_table_name, range_length=range_length
        )
    ) is None:
        return

    perform_delete(
        merge_tree_table_name=merge_tree_table_name,
        merge_tree_condition=f"""{column} NOT IN ({', '.join(f"'{value}'" for value in values)})""",
        iceberg_table=iceberg_table,
        iceberg_condition=NotIn(column, values),
    )


@TestStep(Given)
def delete_starts_with(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows where given column starts with a value."""
    if column != "string_col":
        return

    if (value := get_reference_value(column, merge_tree_table_name)) is None:
        return

    perform_delete(
        merge_tree_table_name=merge_tree_table_name,
        merge_tree_condition=f"{column} LIKE '{value}%'",
        iceberg_table=iceberg_table,
        iceberg_condition=StartsWith(column, value),
    )


@TestStep(Given)
def delete_not_starts_with(self, merge_tree_table_name, iceberg_table, column):
    """Delete rows where given column does not start with a value."""
    if column != "string_col":
        return

    if (value := get_reference_value(column, merge_tree_table_name)) is None:
        return

    perform_delete(
        merge_tree_table_name=merge_tree_table_name,
        merge_tree_condition=f"{column} NOT LIKE '{value}%'",
        iceberg_table=iceberg_table,
        iceberg_condition=NotStartsWith(column, value),
    )


@TestStep(Given)
def add_data(self, merge_tree_table_name, iceberg_table, num_rows=10):
    """Add same data to the MergeTree and Iceberg tables."""
    common.insert_same_data_to_iceberg_and_merge_tree_tables(
        iceberg_table=iceberg_table,
        merge_tree_table_name=merge_tree_table_name,
        num_rows=num_rows,
    )


@TestCheck
def equality_delete(self, minio_root_user, minio_root_password, actions, node=None):
    """Test that ClickHouse can read data from Iceberg table after
    deleting some rows from Iceberg table."""
    database_name = f"iceberg_database_{getuid()}"
    namespace = f"iceberg_{getuid()}"
    iceberg_table_name = f"table_{getuid()}"
    clickhouse_iceberg_table_name = (
        f"{database_name}.\\`{namespace}.{iceberg_table_name}\\`"
    )

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:8182/",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with When(
        f"create namespace, define schema and create {namespace}.{iceberg_table_name} table"
    ):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)
        iceberg_table = catalog_steps.create_iceberg_table_with_five_columns(
            catalog=catalog, namespace=namespace, table_name=iceberg_table_name
        )

    with Then("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            namespace=namespace,
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
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

    with And("perform delete actions and compare results"):
        for action in actions:
            action(
                merge_tree_table_name=merge_tree_table_name, iceberg_table=iceberg_table
            )
            common.compare_data_in_two_tables(
                table_name1=merge_tree_table_name,
                table_name2=clickhouse_iceberg_table_name,
            )


@TestScenario
def run_equality_deletes_combinations(self, minio_root_user, minio_root_password):
    """Run different combinations of delete/insert rows actions from/to Iceberg table.
    Compare results with same delete/insert action from/to MergeTree table."""

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

    with And("add the same number of add_data actions as delete actions"):
        for _ in range(len(actions_with_columns)):
            actions_with_columns.append(add_data)

    length_of_action_list = 10
    number_of_combinations = 100
    for num in range(number_of_combinations):
        actions_list = random.sample(actions_with_columns, length_of_action_list)

        if not isinstance(actions_list, (tuple, list)):
            actions_list = (actions_list,)

        Check(name=f"#{num}", test=equality_delete)(
            actions=actions_list,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=run_equality_deletes_combinations)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
