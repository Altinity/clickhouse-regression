from clickhouse_keeper.tests.steps import *
from clickhouse_keeper.tests.steps_ssl_fips import *
from clickhouse_keeper.tests.performance_steps import *


@TestScenario
def standalone_one_node(
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
def mixed_one_node(
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
def standalone_three_node(
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
def mixed_three_node(
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


@TestFeature
@Name("performance keeper")
def feature(self):
    """Performance tests of CLickHouse Keeper."""
    with Given("I choose Clickhouse cluster for tests"):
        self.context.cluster_name = "'Cluster_3shards_with_3replicas'"

    for scenario in loads(current_module(), Scenario):
        scenario()
