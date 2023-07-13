from clickhouse_keeper.tests.steps import *
from clickhouse_keeper.tests.steps_ssl_fips import *


@TestScenario
def standalone_one_node(
    self, number_clickhouse_cluster_nodes=4, number_of_clickhouse_keeper_nodes=1
):
    """Standalone ClickHouse Keeper 1-node configuration performance test."""
    coordination_cluster_configuration = f"Standalone_1_node_CH_keeper_{'ssl' if self.context.ssl == 'true' else ''}_{self.context.clickhouse_version}"

    control_nodes = self.context.cluster.nodes["clickhouse"][
        number_clickhouse_cluster_nodes : number_clickhouse_cluster_nodes
        + number_of_clickhouse_keeper_nodes
    ]

    cluster_nodes = self.context.cluster.nodes["clickhouse"][
        :number_clickhouse_cluster_nodes
    ]

    with Given("I start standalone ClickHouse Keeper cluster performance check"):
        performance_check_standalone(
            control_nodes=control_nodes,
            cluster_nodes=cluster_nodes,
            coordination_cluster_configuration=coordination_cluster_configuration,
        )

#
# @TestScenario
# def mixed_one_node(
#     self, number_clickhouse_cluster_nodes=9, number_of_clickhouse_keeper_nodes=1
# ):
#     """Mixed ClickHouse Keeper 1-node configuration performance test."""
#     coordination_cluster_configuration = f"Mixed_1_node_CH_keeper_{'ssl' if self.context.ssl == 'true' else ''}_{self.context.clickhouse_version}"
#
#     control_nodes = self.context.cluster.nodes["clickhouse"][
#         number_clickhouse_cluster_nodes
#         - number_of_clickhouse_keeper_nodes : number_clickhouse_cluster_nodes
#     ]
#     cluster_nodes = self.context.cluster.nodes["clickhouse"][
#         :number_clickhouse_cluster_nodes
#     ]
#     rest_cluster_nodes = self.context.cluster.nodes["clickhouse"][
#         : number_clickhouse_cluster_nodes - number_of_clickhouse_keeper_nodes
#     ]
#
#     with Given("I start mixed ClickHouse Keeper cluster performance check"):
#         performance_check_mixed(
#             control_nodes=control_nodes,
#             cluster_nodes=cluster_nodes,
#             rest_cluster_nodes=rest_cluster_nodes,
#             coordination_cluster_configuration=coordination_cluster_configuration,
#         )
#
#
# @TestScenario
# def standalone_three_node(
#     self, number_clickhouse_cluster_nodes=9, number_of_clickhouse_keeper_nodes=3
# ):
#     """Standalone ClickHouse Keeper 3-node configuration performance test."""
#     coordination_cluster_configuration = f"Standalone_3_node_CH_keeper_{'ssl' if self.context.ssl == 'true' else ''}_{self.context.clickhouse_version}"
#
#     control_nodes = self.context.cluster.nodes["clickhouse"][
#         number_clickhouse_cluster_nodes : number_clickhouse_cluster_nodes
#         + number_of_clickhouse_keeper_nodes
#     ]
#
#     cluster_nodes = self.context.cluster.nodes["clickhouse"][
#         :number_clickhouse_cluster_nodes
#     ]
#
#     with Given("I start standalone ClickHouse Keeper cluster performance check"):
#         performance_check_standalone(
#             control_nodes=control_nodes,
#             cluster_nodes=cluster_nodes,
#             coordination_cluster_configuration=coordination_cluster_configuration,
#         )
#
#
# @TestScenario
# def mixed_three_node(
#     self, number_clickhouse_cluster_nodes=9, number_of_clickhouse_keeper_nodes=3
# ):
#     """Mixed Keeper 3-node configuration performance test."""
#     coordination_cluster_configuration = f"Mixed_3_node_CH_keeper_{'ssl' if self.context.ssl == 'true' else ''}_{self.context.clickhouse_version}"
#
#     control_nodes = self.context.cluster.nodes["clickhouse"][
#         number_clickhouse_cluster_nodes
#         - number_of_clickhouse_keeper_nodes : number_clickhouse_cluster_nodes
#     ]
#
#     cluster_nodes = self.context.cluster.nodes["clickhouse"][
#         :number_clickhouse_cluster_nodes
#     ]
#
#     rest_cluster_nodes = self.context.cluster.nodes["clickhouse"][
#         : number_clickhouse_cluster_nodes - number_of_clickhouse_keeper_nodes
#     ]
#
#     with Given("I start mixed ClickHouse Keeper cluster performance check"):
#         performance_check_mixed(
#             control_nodes=control_nodes,
#             cluster_nodes=cluster_nodes,
#             rest_cluster_nodes=rest_cluster_nodes,
#             coordination_cluster_configuration=coordination_cluster_configuration,
#         )


@TestFeature
@Name("performance keeper")
def feature(self):
    """Performance tests of CLickHouse Keeper."""
    with Given("I choose Clickhouse cluster for tests"):
        self.context.cluster_name = "'Cluster_2shards_with_2replicas'"

    for scenario in loads(current_module(), Scenario):
        scenario()
