import swarms.tests.steps.swarm_node_actions as actions

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid


@TestStep(Given)
def create_parquet_with_many_row_groups(
    self,
    node,
    s3_access_key_id,
    s3_secret_access_key,
    rows=200000,
    row_group_size=1000,
):
    """Create one Parquet file with many row groups in MinIO."""
    file_name = f"task_reschedule_{getuid()}.parquet"
    file_url = f"http://minio:9000/warehouse/data/{file_name}"

    node.query(
        f"""
            INSERT INTO FUNCTION s3(
                '{file_url}',
                '{s3_access_key_id}',
                '{s3_secret_access_key}',
                'Parquet',
                'id UInt64'
            )
            SELECT number
            FROM numbers({rows})
            SETTINGS
                output_format_parquet_row_group_size={row_group_size},
                output_format_parquet_row_group_size_bytes=1048576
        """
    )

    return file_url


@TestStep(Given)
def run_long_query(
    self,
    node,
    clickhouse_iceberg_table_name,
    cluster_name="static_swarm_cluster",
    sleep_each_row=1,
    exitcode=None,
    message=None,
    delay_before_execution=None,
    expected_total=None,
    max_threads=1,
    lock_object_storage_task_distribution_ms=None,
    cluster_table_function_split_granularity=None,
    cluster_table_function_buckets_batch_size=None,
    log_comment=None,
):
    """Run a long select from an iceberg table and optionally verify row count."""
    if delay_before_execution:
        import time

        time.sleep(delay_before_execution)

    extra_settings = ""
    if lock_object_storage_task_distribution_ms is not None:
        extra_settings += f", lock_object_storage_task_distribution_ms={lock_object_storage_task_distribution_ms}"
    if cluster_table_function_split_granularity is not None:
        extra_settings += f", cluster_table_function_split_granularity='{cluster_table_function_split_granularity}'"
    if cluster_table_function_buckets_batch_size is not None:
        extra_settings += f", cluster_table_function_buckets_batch_size={cluster_table_function_buckets_batch_size}"
    if log_comment is not None:
        extra_settings += f", log_comment='{log_comment}'"

    result = node.query(
        f"""
            SELECT count()
            FROM {clickhouse_iceberg_table_name}
            WHERE NOT ignore(sleepEachRow({sleep_each_row}))
            SETTINGS
                object_storage_cluster='{cluster_name}',
                max_threads={max_threads}
                {extra_settings}
        """,
        exitcode=exitcode,
        message=message,
    )
    note(f"RESULT: \n{result.output}\n")

    if expected_total is not None:
        total_rows_returned = int(result.output.strip())
        assert total_rows_returned == expected_total, error(
            f"Expected {expected_total} total rows, but got {total_rows_returned}"
        )

    return result


@TestScenario
def rescheduling_with_bucket_granularity(
    self,
    minio_root_user,
    minio_root_password,
    cluster_name="static_swarm_cluster",
    node=None,
):
    """Check bucket-split task rescheduling after replica kill.

    This is the core regression scenario for #1486: one file is split into many bucket
    tasks. If rescheduling uses getPath() instead of getIdentifier(), tasks can collide
    and rows can be lost after replica failure.
    """
    if node is None:
        node = self.context.node

    expected_total = 200000
    row_group_size = 1000
    log_comment = f"bucket_reschedule_{getuid()}"

    with Given("create one parquet file with many row groups"):
        parquet_url = create_parquet_with_many_row_groups(
            node=node,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            rows=expected_total,
            row_group_size=row_group_size,
        )

    table_expression = (
        f"s3('{parquet_url}', '{minio_root_user}', '{minio_root_password}', 'Parquet')"
    )

    with Then(
        "run select with bucket granularity and kill clickhouse on a swarm node"
    ):
        with Pool() as pool:
            Step(
                "run long query", test=run_long_query, parallel=True, executor=pool
            )(
                node=node,
                clickhouse_iceberg_table_name=table_expression,
                cluster_name=cluster_name,
                sleep_each_row=0.00005,
                max_threads=1,
                lock_object_storage_task_distribution_ms=2,
                cluster_table_function_split_granularity="bucket",
                cluster_table_function_buckets_batch_size=1,
                log_comment=log_comment,
                expected_total=expected_total,
            )
            Step(
                "kill clickhouse on random swarm node",
                test=actions.restart_clickhouse_on_random_swarm_node,
                parallel=True,
                executor=pool,
            )(delay=20, signal="KILL", delay_before_execution=2)
            join()

    with And("verify bucket split was active in query profile events"):
        for log_node in (self.context.node, self.context.node2, self.context.node3):
            log_node.query("SYSTEM FLUSH LOGS")

        metrics = node.query(
            f"""
                SELECT
                    sumIf(ProfileEvents['ObjectStorageClusterSentToMatchedReplica'], is_initial_query = 1),
                    sumIf(ProfileEvents['ObjectStorageClusterSentToNonMatchedReplica'], is_initial_query = 1)
                FROM system.query_log
                WHERE log_comment = '{log_comment}'
                  AND type = 'QueryFinish'
                FORMAT TabSeparated
            """
        ).output.strip()

        sent_to_matched, sent_to_non_matched = [
            int(v) for v in metrics.split("\t")
        ]

        processed_tasks_total = 0
        for replica_node in (self.context.node2, self.context.node3):
            processed_tasks = replica_node.query(
                f"""
                    SELECT sum(ProfileEvents['ObjectStorageClusterProcessedTasks'])
                    FROM system.query_log
                    WHERE log_comment = '{log_comment}'
                      AND type = 'QueryFinish'
                      AND is_initial_query = 0
                    FORMAT TabSeparated
                """
            ).output.strip()
            processed_tasks_total += int(processed_tasks or "0")

        # With one source file, values > 1 indicate bucket-level splitting.
        assert sent_to_matched + sent_to_non_matched > 1, error(
            "Bucket split was not active: expected more than one distributed task."
        )
        assert processed_tasks_total > 1, error(
            "Expected more than one processed task with bucket granularity."
        )


@TestFeature
@Name("task rescheduling")
def feature(self, minio_root_user, minio_root_password, node=None):
    """Check that task rescheduling works correctly when swarm replicas fail,
    verifying data completeness after recovery."""
    if node is None:
        node = self.context.node

    Scenario(test=rescheduling_with_bucket_granularity)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
