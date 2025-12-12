import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.tables import create_table_as_select


@TestScenario
def iceberg_iterator_race_condition(self, minio_root_user, minio_root_password):
    """Reproduce race condition in IcebergIterator when using IN subquery."""

    table_name = f"table_{getuid()}"
    namespace = f"namespace_{getuid()}"
    database_name = f"iceberg_db_{getuid()}"
    clickhouse_iceberg_table_name = f"{database_name}.\\`{namespace}.{table_name}\\`"

    local_table_name = f"local_table_{getuid()}"
    node = self.context.node

    number_of_iterations = 100

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("create iceberg table partitioned by name and insert 100 rows"):
        catalog_steps.create_iceberg_table_with_five_columns(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            with_data=True,
            number_of_rows=100,
        )

    with And("create database with DataLakeCatalog engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create merge tree as select from iceberg table for result comparison"):
        comparison_table_name = f"comparison_table_{getuid()}"
        create_table_as_select(
            as_select_from=clickhouse_iceberg_table_name,
            table_name=comparison_table_name,
        )

    with And("create local MergeTree table"):
        node.query(
            f"""
            CREATE TABLE {local_table_name} (
                string_col String,
                long_col Int64
            ) ENGINE = MergeTree()
            ORDER BY string_col
            """
        )

    with And("populate local table with values from iceberg table"):
        node.query(
            f"""
            INSERT INTO {local_table_name} (string_col, long_col)
            SELECT string_col, long_col
            FROM {clickhouse_iceberg_table_name}
            WHERE string_col IN (
                SELECT DISTINCT string_col 
                FROM {clickhouse_iceberg_table_name}
                LIMIT 5
            )
            """
        )

    with When("define query template"):
        query_template = """
            SELECT string_col, long_col
            FROM {table_name}
            WHERE string_col IN (SELECT string_col FROM {local_table_name})
            ORDER BY string_col
            SETTINGS use_iceberg_partition_pruning = 1,
                object_storage_cluster_join_mode = 'local',
                object_storage_cluster = 'replicated_cluster'
        """

    with And("define expected mergetree result for query template"):
        expected_mergetree_result = node.query(
            query_template.format(
                table_name=comparison_table_name,
                local_table_name=local_table_name,
            )
        ).output.strip()

    with Then(
        "run query with IN subquery multiple times with iceberg table from DataLakeCatalog database"
    ):
        for i in range(number_of_iterations):
            with By(f"executing query iteration {i+1} with iceberg table"):
                iceberg_result = node.query(
                    query_template.format(
                        table_name=clickhouse_iceberg_table_name,
                        local_table_name=local_table_name,
                    )
                )
                assert (
                    iceberg_result.output.strip() == expected_mergetree_result
                ), error()

    with And("run query with IN subquery multiple times with iceberg table function"):
        for i in range(number_of_iterations):
            with By(f"executing query iteration {i+1} with iceberg table function"):
                iceberg_table_function_result = node.query(
                    query_template.format(
                        table_name=f"iceberg('http://minio:9000/warehouse/data', '{minio_root_user}', '{minio_root_password}')",
                        local_table_name=local_table_name,
                    )
                )
                assert (
                    iceberg_table_function_result.output.strip()
                    == expected_mergetree_result
                ), error()

    with And(
        "run query with IN subquery multiple times with icebergS3Cluster table function"
    ):
        for i in range(number_of_iterations):
            with By(
                f"executing query iteration {i+1} with icebergS3Cluster table function"
            ):
                iceberg_s3_cluster_table_function_result = node.query(
                    query_template.format(
                        table_name=f"icebergS3Cluster('replicated_cluster', 'http://minio:9000/warehouse/data', '{minio_root_user}', '{minio_root_password}')",
                        local_table_name=local_table_name,
                    )
                )
                assert (
                    iceberg_s3_cluster_table_function_result.output.strip()
                    == expected_mergetree_result
                ), error()

    with And("run query with IN subquery multiple times with s3Cluster table function"):
        for i in range(number_of_iterations):
            with By(f"executing query iteration {i+1} with s3Cluster table function"):
                s3_cluster_table_function_result = node.query(
                    query_template.format(
                        table_name=f"s3Cluster('replicated_cluster', 'http://minio:9000/warehouse/data/data/**.parquet', '{minio_root_user}', '{minio_root_password}')",
                        local_table_name=local_table_name,
                    )
                )
                assert (
                    s3_cluster_table_function_result.output.strip()
                    == expected_mergetree_result
                ), error()

    with And("run query with IN subquery multiple times with s3 table function"):
        for i in range(number_of_iterations):
            with By(f"executing query iteration {i+1} with s3 table function"):
                s3_table_function_result = node.query(
                    query_template.format(
                        table_name=f"s3('http://minio:9000/warehouse/data/data/**.parquet', '{minio_root_user}', '{minio_root_password}')",
                        local_table_name=local_table_name,
                    )
                )
                assert (
                    s3_table_function_result.output.strip() == expected_mergetree_result
                ), error()

    with And(
        "run complex IN subquery multiple times with iceberg table from DataLakeCatalog"
    ):
        first_result = None
        for i in range(number_of_iterations):
            with By(f"executing complex query iteration {i+1}"):
                complex_query_result = node.query(
                    f"""
                    SELECT string_col, long_col, double_col, boolean_col
                    FROM {database_name}.`{namespace}.{table_name}`
                    WHERE string_col IN (
                        SELECT DISTINCT string_col
                        FROM {local_table_name}
                        WHERE long_col > (SELECT AVG(long_col) FROM {local_table_name})
                        AND string_col IS NOT NULL
                    )
                    AND long_col > 0
                    AND double_col BETWEEN 1.0 AND 500.0
                    AND boolean_col IS NOT NULL
                    ORDER BY string_col, long_col DESC, double_col
                    SETTINGS use_iceberg_partition_pruning = 1,
                        object_storage_cluster_join_mode = 'local',
                        object_storage_cluster = 'replicated_cluster'
                    """
                )
                if i == 0:
                    first_result = complex_query_result.output.strip()

                assert first_result == complex_query_result.output.strip(), error()

    with And(
        "run nested IN subquery multiple times with iceberg table from DataLakeCatalog"
    ):
        first_result = None
        for i in range(number_of_iterations):
            with By(f"executing nested IN query iteration {i+1}"):
                nested_in_query_result = node.query(
                    f"""
                    SELECT string_col, long_col, double_col, boolean_col
                    FROM {database_name}.`{namespace}.{table_name}`
                    WHERE string_col IN (
                        SELECT DISTINCT string_col 
                        FROM {local_table_name}
                        WHERE long_col > 0
                        AND string_col IN (
                            SELECT string_col 
                            FROM {database_name}.`{namespace}.{table_name}` 
                            WHERE long_col > (SELECT AVG(long_col) FROM {local_table_name}) AND string_col IS NOT NULL)
                        )
                    AND long_col > 0
                    AND double_col BETWEEN 1.0 AND 500.0
                    AND boolean_col IS NOT NULL
                    ORDER BY string_col, long_col DESC, double_col
                    SETTINGS use_iceberg_partition_pruning = 1,
                        object_storage_cluster_join_mode = 'local',
                        object_storage_cluster = 'replicated_cluster'
                    """
                )
                if i == 0:
                    first_result = nested_in_query_result.output.strip()

                assert first_result == nested_in_query_result.output.strip(), error()

    with Finally("drop local table"):
        node.query(f"DROP TABLE IF EXISTS {local_table_name}")


@TestFeature
@Name("iceberg iterator race condition")
def feature(self, minio_root_user, minio_root_password):
    """Test to reproduce IcebergIterator race condition with IN subqueries.
    https://github.com/Altinity/ClickHouse/pull/1168
    """
    Scenario(test=iceberg_iterator_race_condition)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
