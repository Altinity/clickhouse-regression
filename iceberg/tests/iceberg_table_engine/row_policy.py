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
def row_policy(
    self,
    minio_root_user,
    minio_root_password,
    table_column,
    condition,
    as_clause,
    to_clause,
    user_name1,
    user_name2,
    merge_tree_table_name,
    iceberg_table_name,
    node=None,
):
    """Check that specified row policy on iceberg table works the same as on MergeTree table."""
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

    with And(
        "check that table with Iceberg engine has the same data as MergeTree table"
    ):
        merge_tree_output = iceberg_table_engine.get_select_query_result(
            table_name=merge_tree_table_name
        ).output
        iceberg_output = iceberg_table_engine.get_select_query_result(
            table_name=iceberg_table_name
        ).output
        assert merge_tree_output == iceberg_output, error()

    with And("create same row policy for MergeTree and Iceberg tables"):
        policy_name = f"policy_{getuid()}"

        if condition:
            if "{values}" in condition:
                condition = condition.format(values="(1,2,3,4)")
            elif "{value}" in condition:
                condition = condition.format(value="1")
        else:
            condition = ""

        using_clause = f"{table_column} {condition}"

        iceberg_table_engine.create_row_policy(
            name=policy_name,
            on_clause=f"{merge_tree_table_name}, {iceberg_table_name}",
            using_clause=using_clause,
            as_clause=as_clause,
            to_clause=to_clause,
        )

    with Then("check that selects for each user show the same rows for both tables"):
        for user_name in [user_name1, user_name2]:
            merge_tree_result = iceberg_table_engine.get_select_query_result(
                table_name=merge_tree_table_name, user_name=user_name
            )
            iceberg_result = iceberg_table_engine.get_select_query_result(
                table_name=iceberg_table_name, user_name=user_name
            )
            iceberg_table_engine.compare_results(
                result1=merge_tree_result, result2=iceberg_result
            )


@TestFeature
def row_policies(self, minio_root_user, minio_root_password, node=None):
    """Combinatorial test for row policies on Iceberg tables."""
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

    with And("grant SELECT privilege to all users and roles"):
        node.query(
            f"GRANT SELECT ON {merge_tree_table_name} TO {user_name1}, {user_name2}, {role_name1}, {role_name2}"
        )
        node.query(
            f"GRANT SELECT ON {iceberg_table_name} TO {user_name1}, {user_name2}, {role_name1}, {role_name2}"
        )

    with When("define parameters for row policy"):
        table_column_names = [
            "boolean_col",
            "long_col",
            "float_col",
            "string_col",
            "date_col",
            "MISSING_COL",
        ]

        condition_options = [
            "not in {values}",
            "in {values}",
            "= {value}",
            ">= today() - 30",
            ">= today() - 3000",
            None,
        ]

        as_clause_options = ["PERMISSIVE", "RESTRICTIVE", None]

        to_clause_options = all_roles_and_users + [None] + ["ALL"]
        combinations_by_two = [
            ", ".join(roles) for roles in combinations(all_roles_and_users, 2)
        ]
        combinations_by_three = [
            ", ".join(roles) for roles in combinations(all_roles_and_users, 3)
        ]
        combinations_by_four = [
            ", ".join(roles) for roles in combinations(all_roles_and_users, 4)
        ]
        to_clause_options.extend(combinations_by_two)
        to_clause_options.extend(combinations_by_three)
        to_clause_options.extend(combinations_by_four)
        all_except = [
            f"ALL EXCEPT {role}"
            for role in all_roles_and_users
            + combinations_by_two
            + combinations_by_three
            + combinations_by_four
        ]
        to_clause_options.extend(all_except)

    if not self.context.stress:
        to_clause_options = random.sample(to_clause_options, 5)

    all_combinations = product(
        table_column_names, condition_options, as_clause_options, to_clause_options
    )

    for num, combination in enumerate(all_combinations):
        table_column, condition, as_clause, to_clause = combination
        Scenario(name=f"combination #{num}", test=row_policy)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            table_column=table_column,
            condition=condition,
            as_clause=as_clause,
            to_clause=to_clause,
            user_name1=user_name1,
            user_name2=user_name2,
            merge_tree_table_name=merge_tree_table_name,
            iceberg_table_name=iceberg_table_name,
        )


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    """Test row policies on Iceberg tables."""
    Feature(test=row_policies)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    # ToDo:
    # join conditions by or and and
    # run policy by two
