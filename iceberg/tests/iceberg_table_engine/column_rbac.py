from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import combinations, product

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_table_engine as iceberg_table_engine

from helpers.common import create_user, getuid, create_role

import random
from datetime import date

random.seed(42)


@TestScenario
def check_column_rbac(
    self,
    minio_root_user,
    minio_root_password,
    table_columns,
    user_and_role_names,
    table_column_names_options,
    user_name1,
    user_name2,
    merge_tree_table_name,
    iceberg_table_name,
    node=None,
):
    """Check that specified restriction on column works the same for Iceberg and MergeTree tables."""
    if node is None:
        node = self.context.node

    namespace = "row_policy"
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
        table = catalog_steps.create_iceberg_table_with_five_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with Then("create table with Iceberg engine"):
        iceberg_table_engine.create_table_with_iceberg_engine(
            table_name=iceberg_table_name,
            url="http://minio:9000/warehouse/data",
            access_key_id=minio_root_user,
            secret_access_key=minio_root_password,
        )

    with And("create MergeTree table with same structure"):
        iceberg_table_engine.create_merge_tree_table(table_name=merge_tree_table_name)

    with And("insert data into Iceberg table"):
        df = pa.Table.from_pylist(
            [
                {
                    "boolean_col": True,
                    "long_col": 1000,
                    "double_col": 456.78,
                    "string_col": "Alice",
                    "date_col": date(2024, 1, 1),
                },
                {
                    "boolean_col": False,
                    "long_col": 2000,
                    "double_col": 456.78,
                    "string_col": "Bob",
                    "date_col": date(2023, 5, 15),
                },
                {
                    "boolean_col": True,
                    "long_col": 3000,
                    "double_col": 6.7,
                    "string_col": "Charlie",
                    "date_col": date(2022, 1, 1),
                },
                {
                    "boolean_col": False,
                    "long_col": 4000,
                    "double_col": 8.9,
                    "string_col": "David",
                    "date_col": date(2021, 1, 1),
                },
            ]
        )
        table.append(df)

    with And("insert the same data into MergeTree table"):
        node.query(
            f"""
            INSERT INTO {merge_tree_table_name} VALUES 
            (True, 1000, 456.78, 'Alice', '2024-01-01'),
            (False, 2000, 456.78, 'Bob', '2023-05-15'),
            (True, 3000, 6.7, 'Charlie', '2022-01-01'),
            (False, 4000, 8.9, 'David', '2021-01-01')
            """
        )

    with When("define grant statements for specified columns"):
        iceberg_table_engine.grant_select(
            table_name=merge_tree_table_name,
            table_columns=table_columns,
            user_and_role_names=user_and_role_names,
        )
        iceberg_table_engine.grant_select(
            table_name=iceberg_table_name,
            table_columns=table_columns,
            user_and_role_names=user_and_role_names,
        )

    with Then("check that selects for each user show the same rows for both tables"):
        for columns_combination_option in table_column_names_options:
            for user_name in [user_name1, user_name2]:
                merge_tree_result = iceberg_table_engine.get_select_query_result(
                    table_name=merge_tree_table_name,
                    user_name=user_name,
                    select_columns=columns_combination_option,
                )
                iceberg_result = iceberg_table_engine.get_select_query_result(
                    table_name=iceberg_table_name,
                    user_name=user_name,
                    select_columns=columns_combination_option,
                )
                iceberg_table_engine.compare_results(
                    result1=merge_tree_result, result2=iceberg_result
                )


@TestFeature
def column_rbac(self, minio_root_user, minio_root_password, node=None):
    """Combinatorial test for RBAC on Iceberg tables."""
    if node is None:
        node = self.context.node

    with Given("create users and roles that will be used in row policies"):
        user_name1 = f"user1_{getuid()}"
        user_name2 = f"user2_{getuid()}"
        role_name1 = f"role1_{getuid()}"
        role_name2 = f"role2_{getuid()}"
        create_user(name=user_name1)
        create_user(name=user_name2)
        create_role(role_name=role_name1)
        create_role(role_name=role_name2)
        all_roles_and_users = [user_name1, user_name2, role_name1, role_name2]

    with And("grant roles to users"):
        node.query(f"GRANT {role_name1} TO {user_name1}")
        node.query(f"GRANT {role_name2} TO {user_name2}")

    with And("define MergeTree and Iceberg table names"):
        merge_tree_table_name = define(
            "merge_tree_table_name", "merge_tree_table_" + getuid()
        )
        iceberg_table_name = define("iceberg_table_name", "iceberg_table_" + getuid())

    with When("define parameters for grant statement"):
        table_column_names = [
            "boolean_col",
            "long_col",
            "double_col",
            "string_col",
            "date_col",
            # "MISSING_COL",
        ]

        table_column_names_options = iceberg_table_engine.get_all_combinations(
            table_column_names
        )
        user_and_role_names_options = iceberg_table_engine.get_all_combinations(
            all_roles_and_users
        )

    all_combinations = product(table_column_names_options, user_and_role_names_options)

    for num, combination in enumerate(all_combinations):
        table_columns, user_and_role_names = combination
        Scenario(name=f"combination #{num}", test=check_column_rbac)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            table_columns=table_columns,
            user_and_role_names=user_and_role_names,
            table_column_names_options=table_column_names_options,
            user_name1=user_name1,
            user_name2=user_name2,
            merge_tree_table_name=merge_tree_table_name,
            iceberg_table_name=iceberg_table_name,
        )


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    """Test RBAC for Iceberg tables."""
    Feature(test=column_rbac)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
