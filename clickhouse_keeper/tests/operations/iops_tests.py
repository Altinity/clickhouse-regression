from clickhouse_keeper.tests.operations.large_insert import *


@TestScenario
def iops_check_standalone_keeper(self):
    """
    Check IOPS on Standalone Keeper Process.
    """
    with Given("I start standalone ClickHouse Keepers"):
        start_stand_alone_keeper()

    When("I check IOPS every 1 sec for 79 times", test=iops_check, parallel=True)(
        sleep=1, check_points=80
    )

    with And("I make multi nodes insert and check insert time on every node"):
        multi_nodes_insert(
            nodes_list=["clickhouse1", "clickhouse4", "clickhouse7"],
            partitions_num=99,
            inserts_num=10,
            random_string_length=1000,
        )


@TestScenario
def crash_check_standalone_keeper(self):
    """
    Check ClickHouse with Standalone Keepers crashes with mass insert params.
    """
    with Given("I start Standalone Keepers"):
        start_stand_alone_keeper()

    with And("I make multi nodes insert with params for crash"):
        multi_nodes_insert(
            nodes_list=["clickhouse1", "clickhouse4", "clickhouse7"],
            partitions_num=99,
            inserts_num=100,
            random_string_length=1000,
        )


@TestScenario
def iops_check_mixed_keeper(self):
    """
    Check IOPS on mixed Keeper Process.
    """
    with Given("I start mixed ClickHouse Keepers"):
        start_mixed_keeper()

    When("I check IOPS every 1 sec for 79 sec", test=iops_check, parallel=True)(
        sleep=1, check_points=80
    )

    with And("I make multi nodes insert and check insert time on every node"):
        multi_nodes_insert(
            nodes_list=["clickhouse1", "clickhouse4", "clickhouse7"],
            partitions_num=99,
            inserts_num=10,
            random_string_length=1000,
        )


@TestScenario
def crash_check_mixed_keeper(self):
    """
    Check ClickHouse with Keepers crashes with mass insert params.
    """
    try:
        with Given("I start Keepers on CLickHouse server nodes"):
            start_mixed_keeper()

        with And("I make multi nodes insert with params for crash"):
            multi_nodes_insert(
                nodes_list=["clickhouse1", "clickhouse4", "clickhouse7"],
                partitions_num=99,
                inserts_num=100,
                random_string_length=1000,
            )

    finally:
        with Finally("Check"):
            pass


@TestScenario
def iops_check_zookeeper(self):
    """
    Check IOPS on ZooKeeper Process.
    """
    with Given("I start ZooKeepers"):
        connect_zookeeper()

    When("I check IOPS every 1 sec for 19 sec", test=iops_check, parallel=True)(sleep=1)

    with And("I make multi nodes insert and check insert time on every node"):
        multi_nodes_insert(
            nodes_list=["clickhouse1", "clickhouse4", "clickhouse7"],
            partitions_num=9,
            inserts_num=90,
            random_string_length=1000,
        )


@TestScenario
def crash_check_zookeeper(self):
    """
    Check ClickHouse with Zookeeper crashes with mass insert params.
    """
    try:
        with Given("I start ZooKeepers"):
            connect_zookeeper()

        with And("I make multi nodes insert with params for crash"):
            multi_nodes_insert(
                nodes_list=["clickhouse1", "clickhouse4", "clickhouse7"],
                partitions_num=99,
                inserts_num=100,
                random_string_length=1000,
            )
    finally:
        with Finally("Check"):
            pass


@TestScenario
def iops_check_mixed_keeper_1_3(self):
    """
    Check IOPS on mixed Keeper 1 keeper 3 clickhouse config.
    """
    cluster = self.context.cluster
    keeper_cluster_nodes = cluster.nodes["clickhouse"][0:1]
    clickhouse_cluster_nodes = cluster.nodes["clickhouse"][:3]

    with Given("I stop all unused nodes"):
        for name in cluster.nodes["zookeeper"][:4]:
            cluster.node(name).stop()
        for name in cluster.nodes["clickhouse"][3:13]:
            cluster.node(name).stop()

    with And("I create 1 keeper cluster configuration"):
        create_keeper_cluster_configuration(nodes=keeper_cluster_nodes)
        create_config_section(
            control_nodes=keeper_cluster_nodes, cluster_nodes=clickhouse_cluster_nodes
        )

    with And("I restart replica and keeper nodes"):
        for name in cluster.nodes["clickhouse"][:3]:
            cluster.node(name).restart_clickhouse()

    When("I check IOPS every 1 sec for 37 sec", test=iops_check, parallel=True)(
        sleep=1, check_points=37
    )

    with And(
        "I make multi nodes insert and check insert in simple table time on every node"
    ):
        multi_nodes_insert(
            nodes_list=["clickhouse1", "clickhouse2", "clickhouse3"],
            partitions_num=99,
            inserts_num=900,
            random_string_length=1000,
            cluster_name="'mixed_cluster_3replica_1shard'",
        )


@TestScenario
def iops_check_mixed_keeper_1_1(self):
    """
    Check IOPS on mixed Keeper 1 keeper 3 clickhouse config.
    """
    cluster = self.context.cluster
    keeper_cluster_nodes = cluster.nodes["clickhouse"][0:1]
    clickhouse_cluster_nodes = cluster.nodes["clickhouse"][:1]

    with Given("I stop all unused nodes"):
        for name in cluster.nodes["zookeeper"][:4]:
            cluster.node(name).stop()
        for name in cluster.nodes["clickhouse"][1:13]:
            cluster.node(name).stop()

    with And("I create 1 keeper cluster configuration"):
        create_keeper_cluster_configuration(nodes=keeper_cluster_nodes)
        create_config_section(
            control_nodes=keeper_cluster_nodes, cluster_nodes=clickhouse_cluster_nodes
        )

    with And("I restart replica and keeper nodes"):
        for name in cluster.nodes["clickhouse"][:1]:
            cluster.node(name).restart_clickhouse()

    # When("I check IOPS every 1 sec for 37 sec", test=iops_check, parallel=True)(sleep=1, check_points=37)

    with And(
        "I make multi nodes insert and check insert in simple table time on every node"
    ):
        multi_nodes_insert(
            nodes_list=["clickhouse1"],
            partitions_num=99,
            inserts_num=10,
            random_string_length=1000,
            cluster_name="'mixed_cluster_1replica_1shard'",
        )


@TestScenario
def iops_check_zookeeper_1_3(self):
    """
    Check IOPS on mixed Keeper 1 keeper 3 clickhouse config.
    """
    cluster = self.context.cluster
    keeper_cluster_nodes = cluster.nodes["zookeeper"][3:4]
    clickhouse_cluster_nodes = cluster.nodes["clickhouse"][:3]

    with Given("I stop all unused nodes"):
        for name in cluster.nodes["zookeeper"][:3]:
            cluster.node(name).stop()
        for name in cluster.nodes["clickhouse"][3:13]:
            cluster.node(name).stop()

    with And("I create 1 keeper cluster configuration"):
        create_config_section(
            control_nodes=keeper_cluster_nodes, cluster_nodes=clickhouse_cluster_nodes
        )

    with And("I restart replica and keeper nodes"):
        for name in cluster.nodes["clickhouse"][:3]:
            cluster.node(name).restart_clickhouse()

    When("I check IOPS every 1 sec for 37 sec", test=iops_check, parallel=True)(
        sleep=1, check_points=37
    )

    with And(
        "I make multi nodes insert and check insert in simple table time on every node"
    ):
        multi_nodes_insert(
            nodes_list=["clickhouse1", "clickhouse2", "clickhouse3"],
            partitions_num=9,
            inserts_num=90,
            random_string_length=1000,
            cluster_name="'mixed_cluster_3replica_1shard'",
        )


@TestScenario
def iops_check_standalone_keeper_1_3(self):
    """
    Check IOPS on mixed Keeper 1 keeper 3 clickhouse config.
    """
    cluster = self.context.cluster
    keeper_cluster_nodes = cluster.nodes["clickhouse"][3:4]
    clickhouse_cluster_nodes = cluster.nodes["clickhouse"][:3]

    with Given("I stop all unused nodes"):
        for name in cluster.nodes["zookeeper"][:4]:
            cluster.node(name).stop()
        for name in cluster.nodes["clickhouse"][4:13]:
            cluster.node(name).stop()

    with Given("I start standalone 1 nodes Keeper server"):
        create_keeper_cluster_configuration(nodes=keeper_cluster_nodes)

    with And("I add Keeper server configuration file"):
        create_config_section(
            control_nodes=keeper_cluster_nodes, cluster_nodes=clickhouse_cluster_nodes
        )

    with Given("I start all standalone Keepers nodes"):
        for name in keeper_cluster_nodes:
            cluster.node(name).stop_clickhouse()
        start_keepers(standalone_keeper_nodes=keeper_cluster_nodes)

    with And("I start ClickHouse server"):
        time.sleep(3)
        for name in cluster.nodes["clickhouse"][:3]:
            cluster.node(name).restart_clickhouse()

    When("I check IOPS every 1 sec for 37 sec", test=iops_check, parallel=True)(
        sleep=1, check_points=37
    )

    with And(
        "I make multi nodes insert and check insert in simple table time on every node"
    ):
        multi_nodes_insert(
            nodes_list=["clickhouse1", "clickhouse2", "clickhouse3"],
            partitions_num=9,
            inserts_num=90,
            random_string_length=1000,
            cluster_name="'mixed_cluster_3replica_1shard'",
        )


@TestFeature
@Name("iops_tests")
def feature(self):
    """Compare number of IOPS on a disk level per insert for Keeper vs ZooKeeper."""
    for scenario in loads(current_module(), Scenario):
        scenario()
