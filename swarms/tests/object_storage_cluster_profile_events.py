import random
import pyarrow as pa

import iceberg.tests.steps.iceberg_engine as iceberg_engine
import iceberg.tests.steps.catalog as catalog_steps

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid


def wait_for_metrics(log_comment, node):
    """Wait until QueryFinish event is logged and metrics are collected."""
    for retry in retries(count=10, delay=1):
        with retry:
            count = node.query(
                f"""
                    SELECT count()
                    FROM system.query_log
                    WHERE log_comment = '{log_comment}'
                    AND type = 'QueryFinish'
                    """
            )
            assert int(count.output) > 0


@TestStep(Given)
def setup_iceberg_table_with_large_file_first(
    self,
    minio_root_user,
    minio_root_password,
    large_file_rows=10000,
    small_files_count=50,
    small_file_rows=10,
    large_file_count=5,
    s3_endpoint="http://localhost:9002",
    location="s3://warehouse/data",
):
    """
    Create an Iceberg table with one large partition/file first, then many small ones.
    This ensures the large file is processed first, keeping one replica busy.
    """
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"

    with By("create catalog"):
        catalog = catalog_steps.create_catalog(
            s3_access_key_id=minio_root_user,
            s3_endpoint=s3_endpoint,
            s3_secret_access_key=minio_root_password,
        )

    with And(f"create namespace and create {namespace}.{table_name} table"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            location=location,
        )

    with And("insert several large partition first"):
        for i in range(large_file_count):
            large_partition_name = f"large_partition_{i}"
            data = []
            for j in range(large_file_rows):
                data.append(
                    {
                        "name": large_partition_name,
                        "double": random.uniform(0, 100),
                        "integer": random.randint(0, 10000),
                    }
                )
            df = pa.Table.from_pylist(data)
            table.append(df)

    with And(f"insert {small_files_count} small partitions"):
        for i in range(small_files_count):
            partition_name = f"small_partition_{i}"
            data = []
            for j in range(small_file_rows):
                data.append(
                    {
                        "name": partition_name,
                        "double": random.uniform(0, 100),
                        "integer": random.randint(0, 10000),
                    }
                )
            df = pa.Table.from_pylist(data)
            table.append(df)

    with And("scan and display data"):
        df = table.scan().to_pandas()
        note(f"Total rows inserted: {len(df)}")

    return table, table_name, namespace


@TestStep
def run_iceberg_query_with_cluster_max_threads_1(
    self,
    database_name,
    namespace,
    table_name,
    cluster_name,
    log_comment,
    node=None,
    lock_object_storage_task_distribution_ms=2,
    max_threads=1,
):
    """Run a query on Iceberg table with object storage cluster and max_threads=1."""
    if node is None:
        node = self.context.node

    query = f"""
        SELECT count(), hostName()
        FROM {database_name}.\\`{namespace}.{table_name}\\`
        GROUP BY hostName()
        SETTINGS 
            object_storage_cluster='{cluster_name}',
            log_comment='{log_comment}',
            max_threads={max_threads},
            lock_object_storage_task_distribution_ms={lock_object_storage_task_distribution_ms}
    """
    result = node.query(query)
    return result


@TestScenario
def object_storage_cluster_profile_events_with_overloaded_node(
    self, minio_root_user, minio_root_password
):
    """Test ObjectStorageClusterSentToNonMatchedReplica using large file strategy.

    Create a table with one large file first, then many small files.
    With max_threads=1, the replica processing the large file will be busy,
    so its other files will be sent to other replicas, causing
    ObjectStorageClusterSentToNonMatchedReplica to increase.
    """
    cluster_name = "replicated_cluster"
    database_name = "database_" + getuid()

    with Given("setup Iceberg table with one large file first, then many small files"):
        large_file_count = 4
        small_files_count = 100
        large_file_rows = 500000
        small_file_rows = 10
        table, table_name, namespace = setup_iceberg_table_with_large_file_first(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            large_file_rows=large_file_rows,
            small_files_count=small_files_count,
            small_file_rows=small_file_rows,
            large_file_count=large_file_count,
        )

    with And("create DataLakeCatalog database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("select from iceberg table with swarm cluster"):
        iceberg_engine.read_data_from_clickhouse_iceberg_table(
            columns="count(), hostName()",
            group_by="hostName()",
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            object_storage_cluster=cluster_name,
        )

    with When("select from iceberg table with swarm cluster using max_threads=1"):
        log_comment = "test_object_storage_cluster_overload_" + getuid()
        result = run_iceberg_query_with_cluster_max_threads_1(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            cluster_name=cluster_name,
            log_comment=log_comment,
            max_threads=1,
            lock_object_storage_task_distribution_ms=2,
        )

        with By("parse result and calculate total rows"):
            total_rows_returned = 0
            for line in result.output.strip().split("\n"):
                if line.strip():
                    parts = line.split("\t")
                    count = int(parts[0])
                    total_rows_returned += count

            expected_total = (large_file_count * large_file_rows) + (
                small_files_count * small_file_rows
            )
            assert total_rows_returned == expected_total, error(
                f"Expected {expected_total} total rows, but got {total_rows_returned}"
            )

    with And("flush logs on all nodes"):
        for node in [self.context.node, self.context.node2, self.context.node3]:
            node.query("SYSTEM FLUSH LOGS")

    with And("wait for metrics to be collected"):
        for node in [self.context.node, self.context.node2, self.context.node3]:
            wait_for_metrics(log_comment, node)

    with Then("check that ObjectStorageClusterSentToNonMatchedReplica > 0"):
        sent_to_non_matched_replica = self.context.node.query(
            f"""
            SELECT ProfileEvents['ObjectStorageClusterSentToNonMatchedReplica']
            FROM system.query_log
            WHERE type = 'QueryFinish' AND log_comment = '{log_comment}' AND is_initial_query='1'
            FORMAT TabSeparated
            """
        ).output.strip()
        assert int(sent_to_non_matched_replica) > 0, error()

    with And("check that ObjectStorageClusterSentToMatchedReplica > 0"):
        sent_to_matched_replica = self.context.node.query(
            f"""
            SELECT ProfileEvents['ObjectStorageClusterSentToMatchedReplica']
            FROM system.query_log
            WHERE type = 'QueryFinish' AND log_comment = '{log_comment}' AND is_initial_query='1'
            FORMAT TabSeparated
            """
        ).output.strip()
        assert int(sent_to_matched_replica) > 0, error()

    with And(
        "total files sent to matched replicas should be equal to the number total files"
    ):
        total_files = large_file_count + small_files_count
        assert (
            int(sent_to_matched_replica) + int(sent_to_non_matched_replica)
            == total_files
        ), error()

    with And("define variable for waiting time and processed tasks"):
        with By("at least one of nodes should have non zero waiting time"):
            has_waiting_time = False

        with By("total processed tasks should be equal to the number of files"):
            processed_tasks_total = 0

    with And(
        "check profile events on replica nodes for waiting time and processed tasks"
    ):
        replica_nodes = [self.context.node, self.context.node2, self.context.node3]
        for replica_node in replica_nodes:
            processed_tasks = replica_node.query(
                f"""
                SELECT ProfileEvents['ObjectStorageClusterProcessedTasks']
                FROM system.query_log
                WHERE type = 'QueryFinish' AND log_comment = '{log_comment}' AND hostname='{replica_node.name}' AND is_initial_query='0'
                FORMAT TabSeparated
                """
            ).output.strip()
            processed_tasks_total += int(processed_tasks)

            waiting_microseconds = replica_node.query(
                f"""
                SELECT ProfileEvents['ObjectStorageClusterWaitingMicroseconds']
                FROM system.query_log
                WHERE type = 'QueryFinish' AND log_comment = '{log_comment}' AND hostname='{replica_node.name}' AND is_initial_query='0'
                FORMAT TabSeparated
                """
            ).output.strip()
            if int(waiting_microseconds) > 0:
                has_waiting_time = True

    with And("check that waiting time and processed tasks are not zero"):
        assert has_waiting_time, error()
        assert processed_tasks_total == total_files, error()


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    """Test ObjectStorageCluster profile events.
    Verification of pr https://github.com/Altinity/ClickHouse/pull/1172

    This test verifies the following profile events:

    - ObjectStorageClusterSentToMatchedReplica: Count of tasks sent to replicas matched
    by the Rendezvous hashing algorithm. Calculated on the initiator node.

    - ObjectStorageClusterSentToNonMatchedReplica: Count of tasks sent to replicas that
    don't match the file (when the matched replica hasn't requested tasks recently
    and the lock has expired, or when lock_object_storage_task_distribution_ms=0).
    Calculated on the initiator node.

    - ObjectStorageClusterProcessedTasks: Count of tasks processed by replica nodes.
    Calculated on replica nodes.

    - ObjectStorageClusterWaitingMicroseconds: Total accumulated time spent waiting
    for tasks when retry commands are received. This accumulates across multiple retry
    attempts during task distribution. Calculated on replica nodes.
    """
    Scenario(
        test=object_storage_cluster_profile_events_with_overloaded_node,
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
