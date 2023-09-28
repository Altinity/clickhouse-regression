from clickhouse_keeper.tests.performance_files.performance_steps import *


@TestScenario
def standalone_one_node(
    self, number_clickhouse_cluster_nodes=9, number_of_clickhouse_keeper_nodes=1
):
    """Standalone ClickHouse Keeper 1-node configuration performance test."""

    configuration = f"Keeper_standalone_1_node_{'ssl_' if self.context.ssl == 'true' else ''}{self.context.clickhouse_version}"

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
        self.context.configurations_insert_time_values[
            configuration
        ] = performance_check()


@TestScenario
def mixed_one_node(
    self, number_clickhouse_cluster_nodes=9, number_of_clickhouse_keeper_nodes=1
):
    """Mixed ClickHouse Keeper 1-node configuration performance test."""

    configuration = f"Keeper_mixed_1_node_{'ssl_' if self.context.ssl == 'true' else ''}{self.context.clickhouse_version}"

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
        self.context.configurations_insert_time_values[
            configuration
        ] = performance_check()


@TestScenario
def standalone_three_node(
    self, number_clickhouse_cluster_nodes=9, number_of_clickhouse_keeper_nodes=3
):
    """Standalone ClickHouse Keeper 3-node configuration performance test."""

    configuration = f"Keeper_standalone_3_nodes_{'ssl_' if self.context.ssl == 'true' else ''}{self.context.clickhouse_version}"

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
        self.context.configurations_insert_time_values[
            configuration
        ] = performance_check()


@TestScenario
def mixed_three_node(
    self, number_clickhouse_cluster_nodes=9, number_of_clickhouse_keeper_nodes=3
):
    """Mixed Keeper 3-node configuration performance test."""

    configuration = f"Keeper_mixed_3_nodes_{'ssl_' if self.context.ssl == 'true' else ''}{self.context.clickhouse_version}"

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
        self.context.configurations_insert_time_values[
            configuration
        ] = performance_check()


@TestFeature
@Name("keeper")
def feature(self):
    """Performance tests of CLickHouse Keeper."""
    with Given("I choose Clickhouse cluster for tests"):
        self.context.cluster_name = "'Cluster_3shards_with_3replicas'"

    if self.context.one_node:
        Scenario(run=standalone_one_node)
        Scenario(run=mixed_one_node)
    elif self.context.three_node:
        Scenario(run=standalone_three_node)
        Scenario(run=mixed_three_node)
    else:
        for scenario in loads(current_module(), Scenario):
            scenario()
