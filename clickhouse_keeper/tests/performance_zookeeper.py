from clickhouse_keeper.tests.steps import *
from clickhouse_keeper.tests.steps_ssl_fips import *
from clickhouse_keeper.tests.performance_steps import *


@TestScenario
def one_node(self, number_clickhouse_cluster_nodes=9):
    """ZooKeeper 1-node configuration performance test."""
    if self.context.three_nodes:
        xfail("three nodes mode applied")

    configuration = f"Zookeeper_1_node_{self.context.clickhouse_version}"

    keeper_cluster_nodes = self.context.cluster.nodes["zookeeper"][3:4]

    clickhouse_cluster_nodes = self.context.cluster.nodes["clickhouse"][
        :number_clickhouse_cluster_nodes
    ]

    try:
        if self.context.ssl == "true":
            xfail("ZooKeeper ssl is not supported by tests")

        with Given("I stop all unused zookeeper nodes"):
            for node_name in self.context.cluster.nodes["zookeeper"][:3]:
                self.context.cluster.node(node_name).stop()

        with And("I start Zookeeper cluster"):
            create_config_section(
                control_nodes=keeper_cluster_nodes,
                cluster_nodes=clickhouse_cluster_nodes,
            )

        with Then(
            "I collect the configuration and minimum insert time value from the performance test."
        ):
            self.context.configurations_insert_time_values[
                configuration
            ] = performance_check()

    finally:
        with Finally("I start all stopped ZooKeeper nodes"):
            for node_name in self.context.cluster.nodes["zookeeper"][:3]:
                self.context.cluster.node(node_name).start()
            self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")


@TestScenario
def three_nodes(self, number_clickhouse_cluster_nodes=9):
    """Zookeeper 3-node configuration performance test."""
    if self.context.one_node:
        xfail("one node mode applied")

    configuration = f"Zookeeper_3_node_{self.context.clickhouse_version}"

    keeper_cluster_nodes = self.context.cluster.nodes["zookeeper"][0:3]

    clickhouse_cluster_nodes = self.context.cluster.nodes["clickhouse"][
        :number_clickhouse_cluster_nodes
    ]
    try:
        if self.context.ssl == "true":
            xfail("ZooKeeper ssl is not supported by tests")

        with Given("I stop all unused zookeeper nodes"):
            for node_name in self.context.cluster.nodes["zookeeper"][3:4]:
                self.context.cluster.node(node_name).stop()

        with And("I start ZooKeeper cluster"):
            create_config_section(
                control_nodes=keeper_cluster_nodes,
                cluster_nodes=clickhouse_cluster_nodes,
            )

        with Then(
            "I collect the coordination cluster configuration and minimum insert time value from the performance test."
        ):
            self.context.configurations_insert_time_values[
                configuration
            ] = performance_check()
    finally:
        with Finally("I start all stopped zookeeper nodes"):
            for node_name in self.context.cluster.nodes["zookeeper"][3:4]:
                self.context.cluster.node(node_name).start()
            self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")


@TestFeature
@Name("performance zookeeper")
def feature(self):
    """Performance tests of ZooKeeper."""
    with Given("I choose Clickhouse cluster for tests"):
        self.context.cluster_name = "'Cluster_3shards_with_3replicas'"

    for scenario in loads(current_module(), Scenario):
        scenario()
