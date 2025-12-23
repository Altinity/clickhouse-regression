import time
import random

import swarms.tests.steps.swarm_steps as swarm_steps
import swarms.tests.steps.s3_steps as s3_steps
import swarms.tests.steps.swarm_node_actions as actions
import iceberg.tests.steps.iceberg_engine as iceberg_engine

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid


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
    expected_result=None,
    max_threads=1,
    lock_object_storage_task_distribution_ms=None,
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
                max_threads={max_threads}
                {f", lock_object_storage_task_distribution_ms={lock_object_storage_task_distribution_ms}" if lock_object_storage_task_distribution_ms else ""}
        """,
        exitcode=exitcode,
        message=message,
    )
    note(f"RESULT: \n{result.output}\n")

    if expected_result:
        assert result.output == expected_result, error(
            f"Expected result: {expected_result}, but got: {result.output}"
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
                "restart random swarm node",
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

    with Then(
        "run long select from iceberg table and restart clickhouse on random swarm node"
    ):
        with Pool() as pool:
            Step("run long query", test=run_long_query, parallel=True, executor=pool)(
                node=node,
                clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
                exitcode=32,
                message="DB::Exception: Attempt to read after eof",
                cluster_name=cluster_name,
            )
            Step(
                "restart clickhouse on random swarm node",
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

    with Then(
        "run long select from iceberg table and restart network of random swarm node"
    ):
        with Pool() as pool:
            Step("run long query", test=run_long_query, parallel=True, executor=pool)(
                node=node,
                clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
                cluster_name=cluster_name,
                exitcode=138,
                message="DB::Exception: Query was cancelled.",
            )
            Step(
                "restart network of random swarm node",
                test=actions.restart_network_on_random_swarm_node,
                parallel=True,
                executor=pool,
            )()
            join()


@TestScenario
def swarm_out_of_disk_space(
    self, clickhouse_iceberg_table_name, cluster_name="static_swarm_cluster", node=None
):
    """Check that swarm query does not fail if one of the swarm nodes is out of disk space."""
    if node is None:
        node = self.context.node

    with Given("fill up disks of random swarm node"):
        swarm_node = random.choice(self.context.swarm_nodes)
        actions.fill_clickhouse_disks(node=swarm_node)

    with Then("run long select from iceberg table"):
        run_long_query(
            node=node,
            clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
            cluster_name=cluster_name,
        )


@TestScenario
def initiator_out_of_disk_space(
    self,
    clickhouse_iceberg_table_name,
    database_name,
    minio_root_user,
    minio_root_password,
    cluster_name="static_swarm_cluster",
    node=None,
):
    """Check that swarm query does not fail if one of the swarm nodes is out of disk space."""
    if node is None:
        node = self.context.node

    with Given("fill up disks of initiator node"):
        actions.fill_clickhouse_disks(
            node=node,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            database_name=database_name,
        )

    with Then("run long select from iceberg table"):
        run_long_query(
            node=node,
            clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
            cluster_name=cluster_name,
        )


@TestScenario
def cpu_overload(
    self,
    clickhouse_iceberg_table_name,
    cluster_name="static_swarm_cluster",
    node=None,
    row_count=100,
):
    """Check that swarm query does not fail if one of the swarm nodes is
    under CPU overload. Query expected to be executed successfully on other swarm nodes.
    """
    if node is None:
        node = self.context.node

    overload_node = self.context.node3

    with Then("run long select from iceberg table and overload one swarm node"):
        with Pool() as pool:
            Step("run long query", test=run_long_query, parallel=True, executor=pool)(
                node=node,
                clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
                cluster_name=cluster_name,
                delay_before_execution=1,
                sleep_each_row=0.5,
                expected_result=f"{row_count}\tclickhouse2",
            )
            Step(
                "overload swarm node",
                test=actions.swarm_cpu_load_by_stop_clickhouse,
                parallel=True,
                executor=pool,
            )(node=overload_node)
            join()


@TestScenario
def cpu_overload_all_swarm_nodes(
    self, clickhouse_iceberg_table_name, cluster_name="static_swarm_cluster", node=None
):
    """Check that swarm query fails if all swarm nodes are under CPU overload."""
    if node is None:
        node = self.context.node

    with Then("run long select from iceberg table and overload all swarm nodes"):
        with Pool() as pool:
            Step("run long query", test=run_long_query, parallel=True, executor=pool)(
                node=node,
                clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
                cluster_name=cluster_name,
                delay_before_execution=5,
                sleep_each_row=0.1,
                exitcode=23,
                message="DB::Exception: Cannot connect to any replica for query execution.",
            )
            Step(
                "overload swarm node 1",
                test=actions.swarm_cpu_load_by_stop_clickhouse,
                parallel=True,
                executor=pool,
            )(node=self.context.swarm_nodes[0])
            Step(
                "overload swarm node 2",
                test=actions.swarm_cpu_load_by_stop_clickhouse,
                parallel=True,
                executor=pool,
            )(node=self.context.swarm_nodes[1])
            join()


@TestScenario
def cpu_overload_initiator_nodes(
    self, clickhouse_iceberg_table_name, cluster_name="static_swarm_cluster", node=None
):
    """Check that swarm query fails if initiator node is under CPU overload."""
    if node is None:
        node = self.context.node

    with Then("run long select from iceberg table and overload initiator node"):
        with Pool() as pool:
            Step("run long query", test=run_long_query, parallel=True, executor=pool)(
                node=node,
                clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
                cluster_name=cluster_name,
                delay_before_execution=5,
                sleep_each_row=0.1,
                exitcode=23,
                message="DB::Exception: Cannot connect to any replica for query execution.",
            )
            Step(
                "overload initiator node",
                test=actions.swarm_cpu_load_by_stop_clickhouse,
                parallel=True,
                executor=pool,
            )(node=self.context.node)
            join()


@TestScenario
def check_initiator_works_while_swarm_disconnect(self):
    """Check that queries on initianor node are not affected by swarm node connection or
    disconnection."""


@TestFeature
@Name("node failure")
def feature(self, minio_root_user, minio_root_password, node=None):
    """Check swarm query execution behavior in different failure scenarios."""
    if node is None:
        node = self.context.node

    database_name = f"datalakecatalog_db_{getuid()}"
    row_count = 100

    with Given("setup big iceberg table"):
        _, table_name, namespace = swarm_steps.setup_performance_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            row_count=row_count,
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
        assert "clickhouse2" in result.output or "clickhouse3" in result.output, error(
            "clickhouse2/clickhouse3 should be in `static_swarm_cluster`"
        )

    with When("create DataLakeCatalog database in ClickHouse"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    clickhouse_iceberg_table_name = f"{database_name}.\\`{namespace}.{table_name}\\`"

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
    Scenario(test=initiator_out_of_disk_space)(
        clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
        database_name=database_name,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=cpu_overload)(
        clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
        row_count=row_count,
    )
    Scenario(test=cpu_overload_all_swarm_nodes)(
        clickhouse_iceberg_table_name=clickhouse_iceberg_table_name,
    )
