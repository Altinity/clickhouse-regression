from testflows.core import *
import os

from helpers.common import getuid
from helpers.tables import create_table_as_select
from swarms.requirements.requirements import *


import swarms.tests.steps.swarm_steps as swarm_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine
import ice.steps.hybrid as hybrid_steps


def load_queries_from_sql_file(sql_file_path):
    """Load SQL queries from a file and split them by blank lines."""
    with open(sql_file_path, "r") as f:
        content = f.read()
    queries = []
    for query_block in content.split("\n\n"):
        lines = [
            line
            for line in query_block.split("\n")
            if line.strip() and not line.strip().startswith("--")
        ]
        if lines:
            query = "\n".join(lines).strip()
            if query:
                queries.append(query)
    return queries


def substitute_table_names(query, substitutions):
    """Substitute placeholders in SQL query with actual table names."""
    result = query
    for placeholder, value in substitutions.items():
        result = result.replace(placeholder, value)
    return result


@TestFeature
@Flags(TE)
def hybrid_query_fuzzing(self, minio_root_user, minio_root_password, node=None):
    """Run many pregenerated queries with hybrid tables."""
    ice_node = self.context.ice_node
    if node is None:
        node = self.context.node

    node.query("drop table if exists default.hybrid_table")

    database_name = f"database_{getuid()}"
    location = f"s3://warehouse/data_hybrid"
    url = f"http://minio:9000/warehouse/data_hybrid"

    with Given("create iceberg tables in different locations"):
        _, table_name, namespace = (
            swarm_steps.performance_iceberg_table_with_all_basic_data_types(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                location=location,
                row_count=100,
            )
        )

    with And("create DataLakeCatalog database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create merge tree tables from iceberg tables with same schema and data"):
        clickhouse_iceberg_table_name = (
            f"{database_name}.\\`{namespace}.{table_name}\\`"
        )
        merge_tree_table_name = f"merge_tree_table_{getuid()}"
        create_table_as_select(
            as_select_from=clickhouse_iceberg_table_name,
            table_name=merge_tree_table_name,
            partition_by="string_col",
        )

    with And("select random eventDate from MergeTree table"):
        date_value = node.query(
            f"SELECT date_col FROM {merge_tree_table_name} ORDER BY rand() LIMIT 1;"
        ).output.strip()

    with And("create Hybrid table"):
        # node.query(
        #     f"SET allow_experimental_hybrid_table = 1;"
        #     f"CREATE OR REPLACE TABLE default.hybrid_table\n"
        #     f"ENGINE = Hybrid(remote('localhost', currentDatabase(), {merge_tree_table_name}), date_col <= '{date_value}',\n"
        #     f"icebergCluster('replicated_cluster', 'http://minio:9000/warehouse/data_hybrid', '{minio_root_user}', '{minio_root_password}'), date_col > '{date_value}')"
        # )
        hybrid_table_name = f"hybrid_table_{getuid()}"
        hybrid_steps.create_hybrid_table(
            table_name=hybrid_table_name,
            left_table_name=f"remote('localhost', currentDatabase(), {merge_tree_table_name})",
            left_predicate=f"date_col <= '{date_value}'",
            right_table_name=f"icebergCluster('replicated_cluster', 'http://minio:9000/warehouse/data_hybrid', '{minio_root_user}', '{minio_root_password}')",
            right_predicate=f"date_col > '{date_value}'",
        )

    with And("execute queries from SQL file"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sql_file_path = os.path.join(
            current_dir, "tests", "hybrid_query_fuzzing_queries.sql"
        )

        if os.path.exists(sql_file_path):
            queries = load_queries_from_sql_file(sql_file_path)
            # Can be set to empty string or "SETTINGS object_storage_cluster_join_mode = 'local'"
            join_settings = "SETTINGS object_storage_cluster_join_mode = 'local'"  # Change to "SETTINGS object_storage_cluster_join_mode = 'local'" if needed
            substitutions = {
                "{hybrid_table}": hybrid_table_name,
                "{merge_tree_table}": merge_tree_table_name,
                "{clickhouse_iceberg_table_name}": clickhouse_iceberg_table_name,
                "{join_settings}": join_settings,
            }
            pause()

            with By(f"executing {len(queries)} queries"):
                for i, query_template in enumerate(queries, 1):
                    with By(f"query {i}/{len(queries)}"):
                        try:
                            query = substitute_table_names(
                                query_template, substitutions
                            )
                            node.query(query)
                        except Exception as e:
                            note(f"Query {i} failed: {str(e)}")


@TestFeature
@Name("hybrid query fuzzing")
def feature(self, minio_root_user, minio_root_password):
    """Run many pregenerated queries with hybrid tables."""

    Feature(test=hybrid_query_fuzzing)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    pause()
