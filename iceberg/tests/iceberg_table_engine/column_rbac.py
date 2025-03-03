from testflows.core import *
from testflows.combinatorics import product

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_table_engine as iceberg_table_engine
import iceberg.tests.steps.common as common

from helpers.common import create_user, getuid, create_role

import random

random.seed(42)


@TestScenario
def check_column_rbac(
    self,
    table_columns,
    user_and_role_names,
    table_column_names_options,
    user_name1,
    user_name2,
    merge_tree_table_name,
    iceberg_table_name,
):
    """Check that specified restriction on columns works the same for Iceberg
    and MergeTree tables."""

    with Given(
        "grant same select privileges for specified columns and users on both tables"
    ):
        common.grant_select(
            table_name=merge_tree_table_name,
            table_columns=table_columns,
            user_and_role_names=user_and_role_names,
        )
        common.grant_select(
            table_name=iceberg_table_name,
            table_columns=table_columns,
            user_and_role_names=user_and_role_names,
        )

    with Then(
        "check that select query show the same output for each user for both tables"
    ):
        table_column_names_options = random.sample(table_column_names_options, 10) + [
            table_columns
        ]
        for num, columns_combination_option in enumerate(table_column_names_options):
            with By(f"select #{num}"):
                for user_name in [user_name1, user_name2]:
                    merge_tree_result = common.get_select_query_result(
                        table_name=merge_tree_table_name,
                        user_name=user_name,
                        select_columns=columns_combination_option,
                        order_by=columns_combination_option,
                    )
                    iceberg_result = common.get_select_query_result(
                        table_name=iceberg_table_name,
                        user_name=user_name,
                        select_columns=columns_combination_option,
                        order_by=columns_combination_option,
                    )
                    common.compare_results(
                        result1=merge_tree_result, result2=iceberg_result
                    )


@TestFeature
def column_rbac(self, minio_root_user, minio_root_password, node=None):
    """Run combinatorial tests for RBAC column-level restrictions on Iceberg tables."""
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

    with When(f"define schema and create {namespace}.{table_name} Iceberg table"):
        iceberg_table = catalog_steps.create_iceberg_table_with_five_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with Then("create ClickHouse table with Iceberg engine"):
        iceberg_table_name = "iceberg_table_" + getuid()
        iceberg_table_engine.create_table_with_iceberg_engine(
            table_name=iceberg_table_name,
            url="http://minio:9000/warehouse/data",
            access_key_id=minio_root_user,
            secret_access_key=minio_root_password,
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

    with And("define parameters for grant statement"):
        table_column_names = [
            "boolean_col",
            "long_col",
            "double_col",
            "string_col",
            "date_col",
        ]

        table_column_names_options = common.get_all_combinations(table_column_names)
        user_and_role_names_options = common.get_all_combinations(all_roles_and_users)

    all_combinations = product(table_column_names_options, user_and_role_names_options)

    if not self.context.stress:
        all_combinations = random.sample(list(all_combinations), 100)

    for num, combination in enumerate(all_combinations):
        table_columns, user_and_role_names = combination
        Scenario(name=f"combination #{num}", test=check_column_rbac)(
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
    """Test column RBAC for Iceberg tables."""
    Feature(test=column_rbac)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
