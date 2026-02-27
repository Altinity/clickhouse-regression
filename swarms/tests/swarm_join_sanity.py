from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.tables import create_table_as_select
from swarms.requirements.requirements import *

import swarms.tests.steps.swarm_steps as swarm_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine
from swarms.tests.joins import JoinTable


@TestScenario
def join_subquery(
    self, minio_root_user, minio_root_password, node=None, join_clauses=None
):
    """Check join operation with subquery."""
    if node is None:
        node = self.context.node

    database_name = f"database_{getuid()}"
    location1 = "s3://warehouse/data1"
    location2 = "s3://warehouse/data2"

    with Given("create DataLakeCatalog database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create iceberg tables"):
        _, table_name1, namespace1 = (
            swarm_steps.iceberg_table_with_all_basic_data_types(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                location=location1,
            )
        )
        _, table_name2, namespace2 = (
            swarm_steps.iceberg_table_with_all_basic_data_types(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                location=location2,
            )
        )

        left_table = JoinTable.create_iceberg_table(
            database_name=database_name,
            namespace=namespace1,
            table_name=table_name1,
        )
        right_table = JoinTable.create_iceberg_table(
            database_name=database_name,
            namespace=namespace2,
            table_name=table_name2,
        )

    with And("create merge tree tables for expected result"):
        left_merge_tree_table = create_table_as_select(as_select_from=left_table)
        right_merge_tree_table = create_table_as_select(as_select_from=right_table)

    with Then("run queries with different join clauses"):
        for join_clause in join_clauses:
            with By("get expected result from joining merge tree tables with subquery"):
                expected_query = f"""
                    SELECT *
                    FROM {left_merge_tree_table} AS t1
                    {join_clause} (
                        SELECT * FROM {right_merge_tree_table}
                    ) AS t2
                    ON t1.string_col = t2.string_col
                    ORDER BY tuple(*)
                    FORMAT Values
                """
                expected_result = node.query(expected_query)

            with By("check join with subquery on iceberg tables"):
                query = f"""
                    SELECT *
                    FROM {left_table} AS t1
                    {join_clause} (
                        SELECT * FROM {right_table}
                    ) AS t2
                    ON t1.string_col = t2.string_col
                    ORDER BY tuple(*)
                    SETTINGS object_storage_cluster='replicated_cluster', object_storage_cluster_join_mode='local'
                    FORMAT Values
                """
                result = node.query(query)
                assert result.output == expected_result.output, error(
                    f"Join clause: {join_clause} failed"
                )


@TestScenario
def join_with_clause(
    self, minio_root_user, minio_root_password, node=None, join_clauses=None
):
    """Check join operation with WITH clause."""
    if node is None:
        node = self.context.node

    database_name = f"database_{getuid()}"
    location1 = "s3://warehouse/data1"
    location2 = "s3://warehouse/data2"

    with Given("create DataLakeCatalog database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create iceberg tables"):
        _, table_name1, namespace1 = (
            swarm_steps.iceberg_table_with_all_basic_data_types(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                location=location1,
            )
        )
        _, table_name2, namespace2 = (
            swarm_steps.iceberg_table_with_all_basic_data_types(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                location=location2,
            )
        )

        left_table = JoinTable.create_iceberg_table(
            database_name=database_name,
            namespace=namespace1,
            table_name=table_name1,
        )
        right_table = JoinTable.create_iceberg_table(
            database_name=database_name,
            namespace=namespace2,
            table_name=table_name2,
        )

    with And("create merge tree tables for expected result"):
        left_merge_tree_table = create_table_as_select(as_select_from=left_table)
        right_merge_tree_table = create_table_as_select(as_select_from=right_table)

    with Then("run queries with different join clauses"):
        for join_clause in join_clauses:
            with By(
                "get expected result from joining merge tree tables with WITH clause"
            ):
                expected_query = f"""
                    WITH
                        left_data AS (SELECT * FROM {left_merge_tree_table}),
                        right_data AS (SELECT * FROM {right_merge_tree_table})
                    SELECT *
                    FROM left_data AS t1
                    {join_clause} right_data AS t2
                    ON t1.string_col = t2.string_col
                    ORDER BY tuple(*)
                    FORMAT Values
                """
                expected_result = node.query(expected_query)

            with By("check join with WITH clause on iceberg tables"):
                query = f"""
                    WITH
                        left_data AS (SELECT * FROM {left_table}),
                        right_data AS (SELECT * FROM {right_table})
                    SELECT *
                    FROM left_data AS t1
                    {join_clause} right_data AS t2
                    ON t1.string_col = t2.string_col
                    ORDER BY tuple(*)
                    SETTINGS object_storage_cluster='replicated_cluster', object_storage_cluster_join_mode='local'
                    FORMAT Values
                """
                result = node.query(query)
                assert result.output == expected_result.output, error(
                    f"Join clause: {join_clause} failed"
                )


@TestFeature
@Name("swarm join sanity")
def feature(self, minio_root_user, minio_root_password):
    """Run swarm cluster join sanity checks."""
    join_clauses = [
        "INNER JOIN",
        "INNER ANY JOIN",
        "RIGHT OUTER JOIN",
        "RIGHT SEMI JOIN",
        "RIGHT ANTI JOIN",
        "RIGHT ANY JOIN",
        "LEFT OUTER JOIN",
        "LEFT SEMI JOIN",
        "LEFT ANTI JOIN",
        "LEFT ANY JOIN",
        "FULL OUTER JOIN",
    ]
    Scenario(test=join_subquery)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        join_clauses=join_clauses,
    )
    Scenario(test=join_with_clause)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        join_clauses=join_clauses,
    )
