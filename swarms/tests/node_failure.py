from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

import time

import swarms.tests.steps.swarm_steps as swarm_steps
import swarms.tests.steps.s3_steps as s3_steps
import swarms.tests.steps.swarm_node_actions as actions

import iceberg.tests.steps.iceberg_engine as iceberg_engine


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
):
    """Run a long select from an iceberg table."""
    if delay_before_execution:
        time.sleep(delay_before_execution)
    result = node.query(
        f"""
            SELECT count(), hostName() 
            FROM {clickhouse_iceberg_table_name} 
            WHERE NOT ignore(sleepEachRow({sleep_each_row})) 
            GROUP BY hostName()
            SETTINGS 
                object_storage_cluster='{cluster_name}', 
                max_threads=1
        """,
        exitcode=exitcode,
        message=message,
    )
    return result


@TestScenario
def check_restart_swarm_node(
    self, clickhouse_iceberg_table_name, cluster_name="static_swarm_cluster", node=None
):
    """Check that swarm query fails if one of the swarm nodes is down during the query execution."""
    if node is None:
        node = self.context.node

    with Then("run long select from iceberg table and restart random swarm node"):
        with Pool() as pool:
            Step("run long query", test=run_long_query, parallel=True, executor=pool)(
                node=node,
                clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
                exitcode=138,
                message="DB::Exception: Query was cancelled.",
                cluster_name=cluster_name,
            )
            Step(
                "stop node",
                test=actions.restart_random_swarm_node,
                parallel=True,
                executor=pool,
            )(delay=0.0)
            join()


@TestScenario
def check_restart_clickhouse_on_swarm_node(
    self, clickhouse_iceberg_table_name, cluster_name="static_swarm_cluster", node=None
):
    """Check that swarm query fails if clickhouse is down on one of the swarm nodes."""
    if node is None:
        node = self.context.node

    with Then("run long select from iceberg table and restart random swarm node"):
        with Pool() as pool:
            Step("run long query", test=run_long_query, parallel=True, executor=pool)(
                node=node,
                clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
                exitcode=32,
                message="DB::Exception: Attempt to read after eof",
                cluster_name=cluster_name,
            )
            Step(
                "stop node",
                test=actions.restart_clickhouse_on_random_swarm_node,
                parallel=True,
                executor=pool,
            )(delay=0.0)
            join()


@TestScenario
def network_failure(
    self,
    clickhouse_iceberg_table_name,
    cluster_name="static_swarm_cluster",
    node=None,
):
    """Check that swarm query fails if one of the swarm nodes is down due to network failure."""
    if node is None:
        node = self.context.node

    with Then("run long select from iceberg table and restart random swarm node"):
        with Pool() as pool:
            Step("run long query", test=run_long_query, parallel=True, executor=pool)(
                node=node,
                clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
                cluster_name=cluster_name,
                exitcode=138,
                message="DB::Exception: Query was cancelled.",
            )
            Step(
                "stop node",
                test=actions.restart_network_on_random_swarm_node,
                parallel=True,
                executor=pool,
            )()
            join()


@TestScenario
def swarm_out_of_disk_space(
    self, clickhouse_iceberg_table_name, cluster_name="static_swarm_cluster", node=None
):
    """Check that swarm query fails if one of the swarm nodes is out of disk space."""
    if node is None:
        node = self.context.node

    with Given("fill clickhouse disks"):
        actions.fill_clickhouse_disks()

    with Then("run long select from iceberg table"):
        run_long_query(
            node=node,
            clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
            cluster_name=cluster_name,
        )


@TestFeature
@Name("node failure")
def feature(self, minio_root_user, minio_root_password, node=None):
    """Check swarm query execution behavior in different failure scenarios."""
    if node is None:
        node = self.context.node

    database_name = f"datalakecatalog_db_{getuid()}"

    with Given("setup big iceberg table"):
        _, table_name, namespace = swarm_steps.setup_performance_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            row_count=100,
            batch_size=100,
        )

    with And("check that cluster is functional"):
        cluster_name = "static_swarm_cluster"
        result = s3_steps.read_data_with_s3Cluster_table_function(
            cluster_name=cluster_name,
            columns="hostName() AS host, count()",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            group_by="host",
        )
        assert "clickhouse2" in result.output, error(
            "clickhouse2 should be in `static_swarm_cluster`"
        )
        assert "clickhouse3" in result.output, error(
            "clickhouse3 should be in `static_swarm_cluster`"
        )

    with When("create DataLakeCatalog database in ClickHouse"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        clickhouse_iceberg_table_name = (
            f"{database_name}.\\`{namespace}.{table_name}\\`"
        )

    Scenario(test=check_restart_swarm_node)(
        clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
    )
    Scenario(test=check_restart_clickhouse_on_swarm_node)(
        clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
    )
    Scenario(test=network_failure)(
        clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
    )
    Scenario(test=swarm_out_of_disk_space)(
        clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
    )
