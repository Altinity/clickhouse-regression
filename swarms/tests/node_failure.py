from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from swarms.tests.steps.swarm_node_actions import (
    interrupt_node,
    interrupt_clickhouse,
    interrupt_network,
)

import swarms.tests.steps.swarm_steps as swarm_steps
import swarms.tests.steps.s3_steps as s3_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine


# @TestStep(Given)
# def run_long_query(self, node):
#     """Run a long query on the given node."""
#     result = node.query(
#         f"""
#             SELECT hostName(), sum(avg_d_kbps), count()
#             FROM icebergS3('https://datasets-documentation.s3.eu-west-3.amazonaws.com/ookla/iceberg/')
#             GROUP BY hostName()
#             SETTINGS object_storage_cluster='static_swarm'
#             FORMAT Pretty
#             """,
#         no_checks=True,
#     )

#     assert result.exitcode == 32 or result.exitcode == 138, error()
#     assert (
#         "DB::Exception: Attempt to read after eof: while receiving packet from clickhouse2"
#         in result.output
#         or "DB::Exception: Received from clickhouse2:9000. DB::Exception: Query was cancelled."
#         in result.output
#     ), error()


@TestStep(Given)
def run_long_query(self, node, table_name, namespace, database_name):
    """Run a long query on the given node."""
    result = node.query(
        f"""
            SELECT count() FROM {database_name}.\\`{namespace}.{table_name}\\` CROSS JOIN numbers(20_000_000) AS n SETTINGS max_threads = 1
        """
    )


@TestScenario
def check_node_failure(
    self, minio_root_user, minio_root_password, namespace, table_name, node=None
):
    """Check that query fails if one of the swarm nodes is down during the query execution."""
    if node is None:
        node = self.context.node

    database_name = f"iceberg_db_{getuid()}"

    with Given("create swarm cluster by adding first node"):
        cluster_name = "swarm_cluster" + getuid()
        swarm_steps.add_node_to_swarm(node=node, cluster_name=cluster_name)

    with And("add second and third nodes to the cluster"):
        swarm_steps.add_node_to_swarm(
            node=self.context.node2, cluster_name=cluster_name
        )
        swarm_steps.add_node_to_swarm(
            node=self.context.node3, cluster_name=cluster_name
        )

    with And("read data with iceberg table function and swarm cluster"):
        result = s3_steps.read_data_with_s3Cluster_table_function(
            cluster_name=cluster_name,
            columns="hostName() AS host, count()",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            group_by="host",
        )

    with And("create Iceberg database in ClickHouse"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("test long query"):
        run_long_query(
            node=node,
            table_name=table_name,
            namespace=namespace,
            database_name=database_name,
        )
        pause()

    with Then("run long query and stop node in parallel"):
        with Pool() as pool:
            Step("run long query", test=run_long_query, parallel=True, executor=pool)(
                node=node,
                table_name=table_name,
                namespace=namespace,
                database_name=database_name,
            )
            Step("stop node", test=interrupt_clickhouse, parallel=True, executor=pool)(
                node=node, safe=False
            )
            join()


@TestFeature
@Name("node failure")
def feature(self, minio_root_user, minio_root_password, node=None):
    """Check that query fails if one of the swarm nodes is down during the query execution."""
    if node is None:
        node = self.context.node

    with Given("setup big iceberg table"):
        table, table_name, namespace = swarm_steps.setup_performance_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            batch_size=1000,
            row_count=1_000,
        )

    Scenario(test=check_node_failure)(
        table_name=table_name,
        namespace=namespace,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
