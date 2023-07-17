from clickhouse_keeper.tests.performance_files.performance_steps import *


@TestScenario
def one_node(self, number_clickhouse_cluster_nodes=9):
    """ZooKeeper 1-node configuration performance test."""

    configuration = f"Zookeeper_1_node_{self.context.clickhouse_version}"

    keeper_cluster_nodes = self.context.cluster.nodes["zookeeper"][3:4]

    clickhouse_cluster_nodes = self.context.cluster.nodes["clickhouse"][
        :number_clickhouse_cluster_nodes
    ]

    try:
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
    configuration = f"Zookeeper_3_node_{self.context.clickhouse_version}"

    keeper_cluster_nodes = self.context.cluster.nodes["zookeeper"][0:3]

    clickhouse_cluster_nodes = self.context.cluster.nodes["clickhouse"][
        :number_clickhouse_cluster_nodes
    ]
    try:
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
    if (
        self.context.ssl == "true"
    ):
        xfail("ZooKeeper ssl is not supported by tests")

    with Given("I choose Clickhouse cluster for tests"):
        self.context.cluster_name = "'Cluster_3shards_with_3replicas'"

    if self.context.one_node:
        Scenario(run=one_node)
    elif self.context.one_node:
        Scenario(run=three_nodes)
    else:
        for scenario in loads(current_module(), Scenario):
            scenario()
