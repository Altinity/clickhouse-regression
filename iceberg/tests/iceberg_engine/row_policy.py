from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import combinations, product


import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine
import iceberg.tests.steps.common as common

from helpers.common import create_user, getuid, create_role

import random

random.seed(42)


@TestScenario
def check_row_policy(
    self,
    column_condition_combination,
    conditions_join_option,
    as_clause,
    to_clause,
    user_name1,
    user_name2,
    merge_tree_table_name,
    iceberg_table_name,
):
    """Check that specified row policy on table from Iceberg database engine works as
    on MergeTree table."""

    with Given("check that there is no row policy on tables"):
        n = self.context.node.query(f"SELECT count() FROM system.row_policies").output
        assert n.strip() == "0", error()

    with And("create same row policy for MergeTree and Iceberg tables"):
        using_clause = f" {conditions_join_option} ".join(
            j for j in column_condition_combination
        )
        common.create_row_policy(
            on_clause=f"{merge_tree_table_name}, {iceberg_table_name}",
            using_clause=using_clause,
            as_clause=as_clause,
            to_clause=to_clause,
        )

    with Then("check that selects for each user show the same rows for both tables"):
        for user_name in [user_name1, user_name2]:
            merge_tree_result = common.get_select_query_result(
                table_name=merge_tree_table_name, user_name=user_name
            )
            iceberg_result = common.get_select_query_result(
                table_name=iceberg_table_name, user_name=user_name
            )
            common.compare_results(result1=merge_tree_result, result2=iceberg_result)


@TestFeature
def row_policies(self, minio_root_user, minio_root_password, node=None):
    """Run combinatorial tests for row policies on tables from Iceberg database engine."""
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

    with And(f"define schema and create {namespace}.{table_name} table"):
        iceberg_table = catalog_steps.create_iceberg_table_with_five_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And("create database with Iceberg engine"):
        database_name = "row_policy"
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
        common.insert_same_data_to_iceberg_and_merge_tree_tables(
            iceberg_table=iceberg_table, merge_tree_table_name=merge_tree_table_name
        )

    with And("create users and roles that will be used in row policies"):
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

    with And("grant SELECT privilege to all users and roles"):
        node.query(
            f"GRANT SELECT ON {merge_tree_table_name} TO {user_name1}, {user_name2}, {role_name1}, {role_name2}"
        )
        node.query(
            f"GRANT SELECT ON {database_name}.\\`{namespace}.{table_name}\\` TO {user_name1}, {user_name2}, {role_name1}, {role_name2}"
        )

    with And("define parameters for row policy"):
        table_column_names = [
            "boolean_col",
            "long_col",
            "double_col",
            "string_col",
            "date_col",
            "MISSING_COL",
        ]
        condition_options = [
            "not in [1,2,3,4]",
            "in range(1, 100)",
            "between 1 and 100",
            "= 1",
            ">= today() - 30",
            ">= today() - 3000",
            "",
        ]
        conditions_join_options = ["OR", "AND"]

        column_condition_pairs = [
            f"{table_column} {condition}"
            for table_column in table_column_names
            for condition in condition_options
        ]
        column_condition_pairs_combinations = combinations(column_condition_pairs, 2)

        as_clause_options = ["PERMISSIVE", "RESTRICTIVE", None]

        user_and_role_names_options = common.get_all_combinations(all_roles_and_users)
        all_except = [f"ALL EXCEPT {role}" for role in user_and_role_names_options]
        to_clause_options = user_and_role_names_options + all_except + [None] + ["ALL"]

    all_combinations = product(
        column_condition_pairs_combinations,
        conditions_join_options,
        as_clause_options,
        to_clause_options,
    )

    if not self.context.stress:
        all_combinations = random.sample(list(all_combinations), 100)

    for num, combination in enumerate(all_combinations):
        column_condition_combination, conditions_join_option, as_clause, to_clause = (
            combination
        )
        Scenario(name=f"combination #{num}", test=check_row_policy)(
            column_condition_combination=column_condition_combination,
            conditions_join_option=conditions_join_option,
            as_clause=as_clause,
            to_clause=to_clause,
            user_name1=user_name1,
            user_name2=user_name2,
            merge_tree_table_name=merge_tree_table_name,
            iceberg_table_name=f"{database_name}.\\`{namespace}.{table_name}\\`",
        )


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    """Test row policies on tables from Iceberg database engine."""
    Feature(test=row_policies)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
