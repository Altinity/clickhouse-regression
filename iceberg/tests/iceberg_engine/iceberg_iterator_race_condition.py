import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine
import pyarrow as pa

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.tables import create_table_as_select


@TestStep
def wait_for_initial_query_finish(self, node, log_comment):
    """Wait until exactly one initial QueryFinish row is present for log_comment."""
    for retry in retries(count=20, delay=1):
        with retry:
            query_finish_count = int(
                node.query(
                    f"""
                    SELECT count()
                    FROM system.query_log
                    WHERE log_comment = '{log_comment}'
                      AND type = 'QueryFinish'
                      AND is_initial_query = 1
                    FORMAT TabSeparated
                    """
                ).output.strip()
            )
            assert query_finish_count == 1, error(
                f"Expected exactly 1 initial QueryFinish row, got {query_finish_count}"
            )


@TestStep
def wait_for_worker_query_finish(self, log_comment):
    """Wait until worker nodes have at least one QueryFinish row for log_comment."""
    for retry in retries(count=20, delay=1):
        with retry:
            worker_query_finish_count = 0
            for worker_node in (self.context.node2, self.context.node3):
                worker_query_finish_count += int(
                    worker_node.query(
                        f"""
                        SELECT count()
                        FROM system.query_log
                        WHERE log_comment = '{log_comment}'
                          AND type = 'QueryFinish'
                        FORMAT TabSeparated
                        """
                    ).output.strip()
                )

            assert worker_query_finish_count > 0, error(
                f"Expected worker QueryFinish rows for {log_comment}, got {worker_query_finish_count}"
            )


@TestStep
def collect_worker_metrics(self, log_comment):
    """Collect worker-side metrics from system.query_log profile events."""
    iterator_next_us_total = 0
    processed_tasks_total = 0
    thread_finish_rows_total = 0

    for worker_node in (self.context.node2, self.context.node3):
        metrics_line = worker_node.query(
            f"""
            SELECT
                sum(ProfileEvents['IcebergIteratorNextMicroseconds']),
                sum(ProfileEvents['ObjectStorageClusterProcessedTasks']),
                count()
            FROM system.query_log
            WHERE log_comment = '{log_comment}'
              AND type = 'QueryFinish'
              AND is_initial_query = 0
            FORMAT TabSeparated
            """
        ).output.strip()

        iterator_next_us, processed_tasks, thread_finish_rows = [
            int(v) for v in metrics_line.split("\t")
        ]
        iterator_next_us_total += iterator_next_us
        processed_tasks_total += processed_tasks
        thread_finish_rows_total += thread_finish_rows

    return iterator_next_us_total, processed_tasks_total, thread_finish_rows_total


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
    try:
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

        with And(
            "create merge tree as select from iceberg table for result comparison"
        ):
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

        with And(
            "run query with IN subquery multiple times with iceberg table function"
        ):
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

        with And(
            "run query with IN subquery multiple times with s3Cluster table function"
        ):
            for i in range(number_of_iterations):
                with By(
                    f"executing query iteration {i+1} with s3Cluster table function"
                ):
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
                        s3_table_function_result.output.strip()
                        == expected_mergetree_result
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

                    assert (
                        first_result == nested_in_query_result.output.strip()
                    ), error()

    finally:
        with Finally("drop local table"):
            node.query(f"DROP TABLE IF EXISTS {local_table_name}")


@TestScenario
def wrapped_iceberg_iterator_concurrency(self, minio_root_user, minio_root_password):
    """Reproduce wrapped IcebergIterator lock regression.

    Regression target:
    https://github.com/Altinity/ClickHouse/pull/1436#issuecomment-4023314660
    """
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_db_{getuid()}"
    clickhouse_iceberg_table_name = f"{database_name}.\\`{namespace}.{table_name}\\`"
    local_filter_table = f"local_filter_{getuid()}"
    node = self.context.node

    large_partitions = 100
    large_partition_rows = 2000
    small_partitions = 400
    small_partition_rows = 10
    iterations = 12
    max_query_duration_ms = 2000

    try:
        with Given("create catalog and namespace"):
            catalog = catalog_steps.create_catalog(
                s3_endpoint="http://localhost:9002",
                s3_access_key_id=minio_root_user,
                s3_secret_access_key=minio_root_password,
            )
            catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

        with And("create iceberg table with partition key"):
            table = catalog_steps.create_iceberg_table_with_three_columns(
                catalog=catalog,
                namespace=namespace,
                table_name=table_name,
            )

        with And("insert several large partitions first"):
            for i in range(large_partitions):
                partition_name = f"slow_partition_{i}"
                data = [
                    {"name": partition_name, "double": float(j), "integer": j}
                    for j in range(large_partition_rows)
                ]
                table.append(pa.Table.from_pylist(data))

        with And("insert many small partitions to enable pre-queueing"):
            for i in range(small_partitions):
                partition_name = f"fast_partition_{i}"
                data = [
                    {"name": partition_name, "double": float(j), "integer": j}
                    for j in range(small_partition_rows)
                ]
                table.append(pa.Table.from_pylist(data))

        with And("create DataLakeCatalog database"):
            iceberg_engine.create_experimental_iceberg_database(
                database_name=database_name,
                s3_access_key_id=minio_root_user,
                s3_secret_access_key=minio_root_password,
            )

        with Then("run wrapped iterator path multiple times and keep it responsive"):
            query_durations_ms = []
            iterator_next_us_initial_values = []
            iterator_next_us_leaf_values = []
            iterator_next_us_total_values = []
            worker_iterator_next_us_total_values = []
            worker_processed_tasks_total_values = []
            worker_query_finish_rows_total_values = []
            matched_replica_values = []
            non_matched_replica_values = []
            for i in range(iterations):
                with By(f"execute wrapped query iteration {i + 1}"):
                    log_comment = f"wrapped_iterator_{getuid()}_{i}"
                    result = node.query(
                        f"""
                        SELECT count(), sum(integer)
                        FROM {clickhouse_iceberg_table_name}
                        SETTINGS
                            object_storage_cluster = 'replicated_cluster',
                            log_comment = '{log_comment}'
                        """
                    )

                    count_value, sum_value = result.output.strip().split("\t")
                    assert int(count_value) > 0, error("Expected non-empty result set")
                    assert int(sum_value) > 0, error("Expected positive sum")

                    wait_for_initial_query_finish(node=node, log_comment=log_comment)
                    wait_for_worker_query_finish(log_comment=log_comment)
                    for log_node in (
                        self.context.node,
                        self.context.node2,
                        self.context.node3,
                    ):
                        log_node.query("SYSTEM FLUSH LOGS")

                    metrics_line = node.query(
                        f"""
                        SELECT
                            max(query_duration_ms),
                            sumIf(ProfileEvents['IcebergIteratorNextMicroseconds'], is_initial_query = 1),
                            sumIf(ProfileEvents['IcebergIteratorNextMicroseconds'], is_initial_query = 0),
                            sum(ProfileEvents['IcebergIteratorNextMicroseconds']),
                            sumIf(ProfileEvents['ObjectStorageClusterSentToMatchedReplica'], is_initial_query = 1),
                            sumIf(ProfileEvents['ObjectStorageClusterSentToNonMatchedReplica'], is_initial_query = 1)
                        FROM system.query_log
                        WHERE log_comment = '{log_comment}'
                          AND type = 'QueryFinish'
                        FORMAT TabSeparated
                        """
                    )

                    (
                        query_duration_ms,
                        iterator_next_us_initial,
                        iterator_next_us_leaf,
                        iterator_next_us_total,
                        sent_to_matched,
                        sent_to_non_matched,
                    ) = [int(v) for v in metrics_line.output.strip().split("\t")]

                    query_durations_ms.append(query_duration_ms)
                    iterator_next_us_initial_values.append(iterator_next_us_initial)
                    iterator_next_us_leaf_values.append(iterator_next_us_leaf)
                    iterator_next_us_total_values.append(iterator_next_us_total)
                    matched_replica_values.append(sent_to_matched)
                    non_matched_replica_values.append(sent_to_non_matched)
                    (
                        worker_iterator_next_us_total,
                        worker_processed_tasks_total,
                        worker_thread_finish_rows_total,
                    ) = collect_worker_metrics(log_comment=log_comment)
                    worker_iterator_next_us_total_values.append(
                        worker_iterator_next_us_total
                    )
                    worker_processed_tasks_total_values.append(
                        worker_processed_tasks_total
                    )
                    worker_query_finish_rows_total_values.append(
                        worker_thread_finish_rows_total
                    )

                    assert query_duration_ms < max_query_duration_ms, error(
                        f"Wrapped iterator query is too slow: {query_duration_ms}ms >= {max_query_duration_ms}ms"
                    )

            note(f"wrapped_iterator_durations_ms={query_durations_ms}")
            note(f"iceberg_iterator_next_us_initial={iterator_next_us_initial_values}")
            note(f"iceberg_iterator_next_us_leaf={iterator_next_us_leaf_values}")
            note(f"iceberg_iterator_next_us_total={iterator_next_us_total_values}")
            note(
                f"worker_iceberg_iterator_next_us_total={worker_iterator_next_us_total_values}"
            )
            note(
                f"worker_object_storage_cluster_processed_tasks_total={worker_processed_tasks_total_values}"
            )
            note(
                f"worker_thread_finish_rows_total={worker_query_finish_rows_total_values}"
            )
            note(f"object_storage_cluster_sent_to_matched={matched_replica_values}")
            note(
                f"object_storage_cluster_sent_to_non_matched={non_matched_replica_values}"
            )
            # assert max(worker_iterator_next_us_total_values) > 0, error(
            #     "Expected worker IcebergIteratorNextMicroseconds > 0 in at least one iteration"
            # )
            pause()
    finally:
        with Finally("drop local filter table"):
            node.query(f"DROP TABLE IF EXISTS {local_filter_table}")


@TestFeature
@Name("iceberg iterator race condition")
def feature(self, minio_root_user, minio_root_password):
    """Test to reproduce IcebergIterator race condition with IN subqueries.
    https://github.com/Altinity/ClickHouse/pull/1168
    """
    Scenario(test=iceberg_iterator_race_condition)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    # Scenario(test=wrapped_iceberg_iterator_concurrency)(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
