from clickhouse_keeper.tests.steps import *
from clickhouse_keeper.tests.steps_ssl_fips import *


@TestStep
def performance_check(
    self,
    timeout=30000,
):
    """Step creates a 'bad' table and make inserts. Every row generates ZooKeeper transaction.
    It checks insert time and zoo metrics from system.events before and after insert."""

    node = self.context.cluster.node("clickhouse1")

    insert_time_list = []

    table_name = f"performance_{getuid()}"

    for i in range(self.context.repeats):
        with When(f"I start performance scenario #{self.context.repeats}"):
            try:
                with Given("I create 'bad' table"):
                    retry(node.query, timeout=100, delay=1)(
                        f"CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {self.context.cluster_name}"
                        f" (p UInt64, x UInt64) "
                        "ENGINE = ReplicatedSummingMergeTree('/clickhouse/tables/replicated/{shard}"
                        f"/{table_name}'"
                        ", '{replica}') "
                        "ORDER BY tuple() PARTITION BY p "
                        "SETTINGS  in_memory_parts_enable_wal=0, "
                        "min_bytes_for_wide_part=104857600, "
                        "min_bytes_for_wide_part=104857600, "
                        "parts_to_delay_insert=1000000, "
                        "parts_to_throw_insert=1000000, "
                        "max_parts_in_total=1000000;",
                        steps=False,
                    )

                with And(
                    "I make insert into the table and collect its time into a list."
                ):
                    retry(node.query, timeout=1000, delay=1)(
                        f"insert into {table_name} select rand(1)%100,"
                        f" rand(2) from numbers({self.context.inserts}) "
                        f"settings max_block_size=100, "
                        f"min_insert_block_size_bytes=1, "
                        f"min_insert_block_size_rows=1, "
                        f"insert_deduplicate=0, "
                        f"max_threads=128, "
                        f"max_insert_threads=128;",
                        timeout=timeout,
                    )

                    metric(name="Time", value=current_time(), units="sec")

                    insert_time_list.append(float(current_time()))

            finally:
                with Finally("I drop table if exists and provide cleanup"):
                    node.query(
                        f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {self.context.cluster_name} SYNC"
                    )
                    clean_coordination_on_all_nodes()
                    self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")

    return min(insert_time_list)


@TestScenario
def standalone_1_node(
    self, number_clickhouse_cluster_nodes=9, number_of_clickhouse_keeper_nodes=1
):
    """Standalone ClickHouse Keeper 1-node configuration performance test."""
    configuration = f"Standalone_1_node_CH_keeper_{'ssl' if self.context.ssl == 'true' else ''}_{self.context.clickhouse_version}"

    control_nodes = self.context.cluster.nodes["clickhouse"][
        number_clickhouse_cluster_nodes : number_clickhouse_cluster_nodes
        + number_of_clickhouse_keeper_nodes
    ]

    cluster_nodes = self.context.cluster.nodes["clickhouse"][
        :number_clickhouse_cluster_nodes
    ]

    with Given("I start standalone ClickHouse Keeper cluster"):
        start_standalone_ch_keeper(
            control_nodes=control_nodes, cluster_nodes=cluster_nodes
        )

    with Then(
        "I collect the coordination cluster configuration and minimum insert time value from the performance test."
    ):

        self.context.configurations_minimum_insert_time_values[
            configuration
        ] = performance_check()


@TestScenario
def mixed_1_node(
    self, number_clickhouse_cluster_nodes=9, number_of_clickhouse_keeper_nodes=1
):
    """Mixed ClickHouse Keeper 1-node configuration performance test."""
    configuration = f"Mixed_1_node_CH_keeper_{'ssl' if self.context.ssl == 'true' else ''}_{self.context.clickhouse_version}"

    control_nodes = self.context.cluster.nodes["clickhouse"][
        number_clickhouse_cluster_nodes
        - number_of_clickhouse_keeper_nodes : number_clickhouse_cluster_nodes
    ]
    cluster_nodes = self.context.cluster.nodes["clickhouse"][
        :number_clickhouse_cluster_nodes
    ]
    rest_cluster_nodes = self.context.cluster.nodes["clickhouse"][
        : number_clickhouse_cluster_nodes - number_of_clickhouse_keeper_nodes
    ]

    with Given("I start mixed ClickHouse Keeper cluster"):
        start_mixed_ch_keeper(
            control_nodes=control_nodes,
            cluster_nodes=cluster_nodes,
            rest_cluster_nodes=rest_cluster_nodes,
        )

    with Then(
        "I collect the coordination cluster configuration and minimum insert time value from the performance test."
    ):

        self.context.configurations_minimum_insert_time_values[
            configuration
        ] = performance_check()


@TestScenario
def zookeeper_1_node(self, number_clickhouse_cluster_nodes=9):
    """ZooKeeper 1-node configuration performance test."""
    xfail("doesn't work on full run")

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
            self.context.configurations_minimum_insert_time_values[
                configuration
            ] = performance_check()

    finally:
        with Finally("I start all stopped ZooKeeper nodes"):
            for node_name in self.context.cluster.nodes["zookeeper"][:3]:
                self.context.cluster.node(node_name).start()
            self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")


@TestScenario
def standalone_3_node(
    self, number_clickhouse_cluster_nodes=9, number_of_clickhouse_keeper_nodes=3
):
    """Standalone ClickHouse Keeper 3-node configuration performance test."""
    configuration = f"Standalone_3_node_CH_keeper_{'ssl' if self.context.ssl == 'true' else ''}_{self.context.clickhouse_version}"

    control_nodes = self.context.cluster.nodes["clickhouse"][
        number_clickhouse_cluster_nodes : number_clickhouse_cluster_nodes
        + number_of_clickhouse_keeper_nodes
    ]

    cluster_nodes = self.context.cluster.nodes["clickhouse"][
        :number_clickhouse_cluster_nodes
    ]

    with Given("I start standalone ClickHouse Keeper cluster"):
        start_standalone_ch_keeper(
            control_nodes=control_nodes, cluster_nodes=cluster_nodes
        )

    with Then(
        "I collect the coordination cluster configuration and minimum insert time value from the performance test."
    ):

        self.context.configurations_minimum_insert_time_values[
            configuration
        ] = performance_check()


@TestScenario
def mixed_3_node(
    self, number_clickhouse_cluster_nodes=9, number_of_clickhouse_keeper_nodes=3
):
    """Mixed Keeper 3-node configuration performance test."""
    configuration = f"Mixed_3_node_CH_keeper_{'ssl' if self.context.ssl == 'true' else ''}_{self.context.clickhouse_version}"

    control_nodes = self.context.cluster.nodes["clickhouse"][
        number_clickhouse_cluster_nodes
        - number_of_clickhouse_keeper_nodes : number_clickhouse_cluster_nodes
    ]

    cluster_nodes = self.context.cluster.nodes["clickhouse"][
        :number_clickhouse_cluster_nodes
    ]

    rest_cluster_nodes = self.context.cluster.nodes["clickhouse"][
        : number_clickhouse_cluster_nodes - number_of_clickhouse_keeper_nodes
    ]

    with Given("I start mixed ClickHouse Keeper cluster"):
        start_mixed_ch_keeper(
            control_nodes=control_nodes,
            cluster_nodes=cluster_nodes,
            rest_cluster_nodes=rest_cluster_nodes,
        )

    with Then(
        "I collect the coordination cluster configuration and minimum insert time value from the performance test."
    ):

        self.context.configurations_minimum_insert_time_values[
            configuration
        ] = performance_check()


@TestScenario
def zookeeper_3_node(self, number_clickhouse_cluster_nodes=9):
    """Zookeeper 3-node configuration performance test."""
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
            self.context.configurations_minimum_insert_time_values[
                configuration
            ] = performance_check()
    finally:
        with Finally("I start all stopped zookeeper nodes"):
            for node_name in self.context.cluster.nodes["zookeeper"][3:4]:
                self.context.cluster.node(node_name).start()
            self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")


@TestFeature
@Name("performance")
def feature(self):
    """Performance tests of CLickHouse Keeper."""
    with Given("I choose Clickhouse cluster for tests"):
        self.context.cluster_name = "'Cluster_3shards_with_3replicas'"

    for scenario in loads(current_module(), Scenario):
        scenario()
