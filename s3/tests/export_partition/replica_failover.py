from testflows.core import *
from testflows.asserts import error
from s3.tests.export_partition.steps import *
from helpers.common import getuid
from helpers.create import *
from helpers.queries import *
from s3.requirements.export_partition import *
from alter.stress.tests.tc_netem import network_packet_rate_limit
import time


@TestStep(Given)
def create_source_and_destination_tables(
    self, source_table_name=None, cluster="replicated_cluster"
):
    """Create a populated source table and empty S3 destination table."""
    if source_table_name is None:
        source_table_name = f"source_{getuid()}"

    with By("creating populated source table on replicated cluster"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table_name,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
            cluster=cluster,
            number_of_partitions=10,
            number_of_parts=30,
        )

    with And("creating empty S3 destination table"):
        s3_table = create_s3_table(table_name="s3", create_new_bucket=True)

    return source_table_name, s3_table


@TestStep(When)
def kill_node_during_export(self, node_name, delay=2):
    """Kill a ClickHouse node during export operation."""
    node = self.context.cluster.node(node_name)

    with By(f"waiting {delay} seconds before killing {node_name}"):
        time.sleep(delay)

    with And(f"killing {node_name} node"):
        node.stop_clickhouse(safe=False, signal="KILL")


@TestStep(When)
def kill_nodes_sequentially_during_export(
    self, nodes_to_kill, initial_delay=5, delay_increment=3
):
    """Kill multiple nodes sequentially during export with increasing delays."""
    with By("killing nodes one by one during export with delays"):
        for i, node_name in enumerate(nodes_to_kill):
            Step(test=kill_node_during_export, parallel=True)(
                node_name=node_name,
                delay=initial_delay + i * delay_increment,
            )


@TestStep(When)
def export_partition_with_node_failures(
    self,
    source_table,
    destination_table,
    node,
    nodes_to_kill,
):
    """Export partitions while killing nodes one by one."""

    with By("starting export partition operation and killing nodes in parallel"):
        Step(test=export_partitions, parallel=True)(
            source_table=source_table,
            destination_table=destination_table,
            node=node,
            partitions=None,
        )

        kill_nodes_sequentially_during_export(nodes_to_kill=nodes_to_kill)

        join()


@TestStep(When)
def restart_nodes(self, node_names):
    """Restart multiple ClickHouse nodes."""
    for node_name in node_names:
        node = self.context.cluster.node(node_name)
        with By(f"restarting {node_name}"):
            node.start_clickhouse()


@TestStep(Then)
def wait_for_nodes_to_be_ready(self, node_names, timeout=60, delay=2):
    """Wait for multiple nodes to be ready and responsive."""
    with By("waiting for all nodes to be ready"):
        for node_name in node_names:
            node = self.context.cluster.node(node_name)
            for attempt in retries(timeout=timeout, delay=delay):
                with attempt:
                    node.query("SELECT 1", exitcode=0)


@TestStep(Then)
def verify_export_success(
    self, source_table, destination_table, timeout=40, delay=5, partition=None
):
    """Verify that export completed successfully by checking source matches destination."""
    with By("checking that source matches destination"):
        for retry in retries(timeout=timeout, delay=delay):
            with retry:
                source_matches_destination(
                    source_table=source_table,
                    destination_table=destination_table,
                )


@TestStep(When)
def kill_and_restart_keeper_during_export(self, node, delay=5):
    """Kill keeper node during export, then restart it."""
    with By("waiting for export to start"):
        wait_for_export_to_start(node=node)

    with And("killing keeper node"):
        kill_keeper()

    with And("restarting keeper node"):
        start_keeper()


@TestStep(When)
def export_partition_with_keeper_failure(
    self,
    source_table,
    destination_table,
    node,
    delay_before_kill=5,
):
    """Export partitions while killing and restarting keeper in parallel."""

    with By(
        "starting export partition operation and killing/restarting keeper in parallel"
    ):
        Step(test=export_partitions, parallel=True)(
            source_table=source_table,
            destination_table=destination_table,
            node=node,
            partitions=None,
            retry_times=45,
        )

        Step(test=kill_and_restart_keeper_during_export, parallel=True)(
            node=node,
            delay=delay_before_kill,
        )

        join()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_NetworkResilience_NodeInterruption("1.0"))
def export_with_replica_failover(self):
    """Test that export partition continues successfully when replica nodes fail one by one."""

    source_table = None
    s3_table = None
    nodes_to_kill = ["clickhouse1", "clickhouse2", "clickhouse3"]

    with Given(
        "I create a populated source table on replicated_cluster and empty S3 table"
    ):
        source_table, s3_table = create_source_and_destination_tables(
            cluster="replicated_cluster"
        )

    with When("I export partitions while killing replica nodes one by one"):
        node = self.context.cluster.node("clickhouse1")
        export_partition_with_node_failures(
            source_table=source_table,
            destination_table=s3_table,
            node=node,
            nodes_to_kill=nodes_to_kill,
        )

    with And("I restart all killed nodes"):
        restart_nodes(node_names=nodes_to_kill)

    with And("I wait for export to complete after nodes restart"):
        any_node = self.context.cluster.node("clickhouse1")
        wait_for_export_to_complete(node=any_node)

    with Then("I verify that export partition completed successfully"):
        wait_for_nodes_to_be_ready(node_names=nodes_to_kill)
        verify_export_success(
            source_table=source_table,
            destination_table=s3_table,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_NetworkResilience_KeeperInterruption("1.0"))
def export_with_keeper_failover_and_network_delay(self):
    """Test that export partition continues successfully when keeper fails during export with network delay."""

    source_table = None
    s3_table = None

    with Given(
        "I create a populated source table on replicated_cluster and empty S3 table"
    ):
        source_table, s3_table = create_source_and_destination_tables(
            cluster="replicated_cluster"
        )

    with And("I add network delay to ClickHouse node"):
        node = self.context.cluster.node("clickhouse1")
        network_packet_rate_limit(node=node, rate_mbit=0.05)
    with When("I export partitions while killing and restarting keeper in parallel"):
        export_partition_with_keeper_failure(
            source_table=source_table,
            destination_table=s3_table,
            node=node,
            delay_before_kill=5,
        )

    with And("I wait for export to complete"):
        wait_for_export_to_complete(node=node)

    with Then("I verify that export partition completed successfully"):
        verify_export_success(
            source_table=source_table,
            destination_table=s3_table,
        )


@TestFeature
@Name("replica failover")
@Requirements(RQ_ClickHouse_ExportPartition_NetworkResilience_NodeInterruption("1.0"))
def feature(self):
    """Test export partition recovery when replica nodes fail during export."""

    Scenario(run=export_with_replica_failover)
    Scenario(run=export_with_keeper_failover_and_network_delay)
