from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *
from helpers.common import *


@TestScenario
def mixed_keepers_5(self):
    """Check that 5 nodes Clickhouse Keeper Cluster work in write mode
    with 2 nodes down and in read mode only with 3 nodes down.
    """
    cluster = self.context.cluster
    try:
        start_mixed_keeper(
            cluster_nodes=cluster.nodes["clickhouse"][:9],
            control_nodes=cluster.nodes["clickhouse"][0:5],
            rest_cluster_nodes=cluster.nodes["clickhouse"][5:9],
        )

        with Given("Receive UID"):
            uid = getuid()

        with And("I create some replicated table"):
            table_name = f"test{uid}"
            create_simple_table(table_name=table_name)

        with And("I stop maximum available Keeper nodes for such configuration"):
            for name in cluster.nodes["clickhouse"][3:5]:
                cluster.node(name).stop_clickhouse()

        with And("I check that table in write mode"):
            retry(cluster.node("clickhouse1").query, timeout=500, delay=1)(
                f"insert into {table_name} values (1,1)", exitcode=0
            )

        with And("I stop one more Keeper node"):
            cluster.node("clickhouse3").stop_clickhouse()

        with And("I check that table in read only mode"):
            node = self.context.cluster.node("clickhouse1")
            retry(node.query, timeout=100, delay=1)(
                f"INSERT INTO {table_name}(Id, partition) values (1,2)",
                exitcode=242,
                message="DB::Exception: Table is in readonly mode",
                steps=False,
            )

        with And("I start dropped nodes"):
            for name in cluster.nodes["clickhouse"][2:5]:
                cluster.node(name).start_clickhouse(wait_healthy=False)

        with And(f"I check that ruok returns imok"):
            for name in cluster.nodes["clickhouse"][0:5]:
                retry(cluster.node("bash-tools").cmd, timeout=500, delay=1)(
                    f"echo ruok | nc {name} 2181",
                    exitcode=0,
                    message="imok",
                )

        with And("I check clean ability"):
            table_insert(table_name=table_name, node_name="clickhouse1")

    finally:
        with Finally("I clean up"):
            clean_coordination_on_all_nodes()


@TestScenario
def mixed_keepers_4(self):
    """Check that 4 nodes Clickhouse Keeper Cluster work in write mode
    with 1 node down and in read mode only with 2 nodes down.
    """

    cluster = self.context.cluster
    try:
        start_mixed_keeper(
            cluster_nodes=cluster.nodes["clickhouse"][:9],
            control_nodes=cluster.nodes["clickhouse"][0:4],
            rest_cluster_nodes=cluster.nodes["clickhouse"][4:9],
        )

        with Given("Receive UID"):
            uid = getuid()

        with And("I create some replicated table"):
            table_name = f"test{uid}"
            create_simple_table(table_name=table_name)

        with And("I stop maximum available Keeper nodes for such configuration"):
            cluster.node("clickhouse4").stop_clickhouse()

        with And("I check that table in write mode"):
            retry(cluster.node("clickhouse1").query, timeout=500, delay=1)(
                f"insert into {table_name} values (1,1)", exitcode=0
            )

        with And("I stop one more Keeper node"):
            cluster.node("clickhouse3").stop_clickhouse()

        with And("I check that table in read only mode"):
            node = self.context.cluster.node("clickhouse1")
            retry(node.query, timeout=100, delay=1)(
                f"INSERT INTO {table_name}(Id, partition) values (1,2)",
                exitcode=242,
                message="DB::Exception: Table is in readonly mode",
                steps=False,
            )

        with And("I start dropped nodes"):
            for name in cluster.nodes["clickhouse"][2:4]:
                cluster.node(name).start_clickhouse(wait_healthy=False)

        with And(f"I check that ruok returns imok"):
            for name in cluster.nodes["clickhouse"][0:4]:
                retry(cluster.node("bash-tools").cmd, timeout=100, delay=1)(
                    f"echo ruok | nc {name} 2181",
                    exitcode=0,
                    message="imok",
                )

        with And("I check clean ability"):
            table_insert(table_name=table_name, node_name="clickhouse1")
    finally:
        with Finally("I clean up"):
            clean_coordination_on_all_nodes()


@TestScenario
def mixed_keepers_3(self):
    """Check that 3 nodes Clickhouse Keeper Cluster work in write mode
    with 1 node down and in read mode only with 2 nodes down.
    """
    cluster = self.context.cluster
    try:
        start_mixed_keeper(
            cluster_nodes=cluster.nodes["clickhouse"][:9],
            control_nodes=cluster.nodes["clickhouse"][0:3],
            rest_cluster_nodes=cluster.nodes["clickhouse"][3:9],
        )

        with Given("Receive UID"):
            uid = getuid()

        with And("I create some replicated table"):
            table_name = f"test{uid}"
            create_simple_table(table_name=table_name)

        with And("I stop maximum available Keeper nodes for such configuration"):
            cluster.node("clickhouse3").stop_clickhouse()

        with And("I check that table in write mode"):
            retry(cluster.node("clickhouse1").query, timeout=500, delay=1)(
                f"insert into {table_name} values (1,1)", exitcode=0
            )

        with And("I stop one more Keeper node"):
            cluster.node("clickhouse2").stop_clickhouse()

        with And("I check that table in read only mode"):
            self.context.cluster.node("clickhouse1").query(
                f"insert into {table_name}(Id, partition) values (1,2)",
                exitcode=242,
                message="DB::Exception: Table is in readonly mode",
            )

        with And("I start dropped nodes"):
            for name in cluster.nodes["clickhouse"][1:3]:
                cluster.node(name).start_clickhouse(wait_healthy=False)

        with And(f"I check that ruok returns imok"):
            for name in cluster.nodes["clickhouse"][0:3]:
                retry(cluster.node("bash-tools").cmd, timeout=500, delay=1)(
                    f"echo ruok | nc {name} 2181",
                    exitcode=0,
                    message="imok",
                )

        with And("I check clean ability"):
            table_insert(table_name=table_name, node_name="clickhouse1")

    finally:
        with Finally("I clean up"):
            clean_coordination_on_all_nodes()


@TestScenario
def mixed_keepers_2(self):
    """Check that 2 nodes Clickhouse Keeper Cluster work in write mode
    and goes in read mode only with 1 node down.
    """
    xfail("doesn't work on 22.3")
    cluster = self.context.cluster
    try:
        start_mixed_keeper(
            cluster_nodes=cluster.nodes["clickhouse"][:9],
            control_nodes=cluster.nodes["clickhouse"][0:2],
            rest_cluster_nodes=cluster.nodes["clickhouse"][2:9],
        )

        with Given("Receive UID"):
            uid = getuid()

        with And("I create some replicated table"):
            table_name = f"test{uid}"
            create_simple_table(table_name=table_name)

        with And("I check that table in write mode"):
            retry(cluster.node("clickhouse1").query, timeout=500, delay=1)(
                f"insert into {table_name} values (1,1)", exitcode=0
            )

        with And("I stop one Keeper node"):
            cluster.node("clickhouse2").stop_clickhouse()

        with And("I check that table in read only mode"):
            self.context.cluster.node("clickhouse1").query(
                f"insert into {table_name} values (1,2)",
                exitcode=242,
                message="DB::Exception: Table is in readonly mode",
            )

        with And("I start dropped nodes"):
            cluster.node("clickhouse2").start_clickhouse(wait_healthy=False)

        with And(f"I check that ruok returns imok"):
            for name in cluster.nodes["clickhouse"][0:2]:
                retry(cluster.node("bash-tools").cmd, timeout=500, delay=1)(
                    f"echo ruok | nc {name} 2181",
                    exitcode=0,
                    message="imok",
                )

        with And("I check clean ability"):
            table_insert(table_name=table_name, node_name="clickhouse1")

    finally:
        with Finally("I clean up"):
            clean_coordination_on_all_nodes()


@TestScenario
def mixed_keepers_1(self):
    """Check that 1 node Clickhouse Keeper Cluster work in write mode
    and goes in read mode only with 1 node down.
    """
    cluster = self.context.cluster
    try:
        start_mixed_keeper(
            cluster_nodes=cluster.nodes["clickhouse"][:9],
            control_nodes=cluster.nodes["clickhouse"][0:1],
            rest_cluster_nodes=cluster.nodes["clickhouse"][1:9],
        )

        with Given("Receive UID"):
            uid = getuid()

        with And("I create some replicated table"):
            table_name = f"test{uid}"
            create_simple_table(table_name=table_name)

        with And("I check that table in write mode"):
            retry(cluster.node("clickhouse2").query, timeout=250, delay=1)(
                f"insert into {table_name} values (1,1)", exitcode=0
            )

        with And("I stop one Keeper node"):
            cluster.node("clickhouse1").stop_clickhouse()

        with And("I check that table in read only mode"):
            self.context.cluster.node("clickhouse2").query(
                f"insert into {table_name} values (1,2)",
                exitcode=242,
                message="DB::Exception: Table is in readonly mode",
            )

        with And("I start dropped nodes"):
            cluster.node("clickhouse1").start_clickhouse(wait_healthy=False)

        with And(f"I check that ruok returns imok"):
            for name in cluster.nodes["clickhouse"][0:1]:
                retry(cluster.node("bash-tools").cmd, timeout=100, delay=1)(
                    f"echo ruok | nc {name} 2181",
                    exitcode=0,
                    message="imok",
                )

        with And("I check clean ability"):
            table_insert(table_name=table_name, node_name="clickhouse1")

    finally:
        with Finally("I clean up"):
            clean_coordination_on_all_nodes()


@TestScenario
def zookeepers_3(self):
    """Check that 3 nodes ZooKeeper Cluster work in write mode
    with 1 node down and in read mode only with 2 nodes down.
    """
    cluster = self.context.cluster
    zookeeper_cluster_nodes = cluster.nodes["zookeeper"][:3]
    clickhouse_cluster_nodes = cluster.nodes["clickhouse"][:9]

    with Given("I add ZooKeeper server configuration file to ClickHouse servers"):
        create_config_section(
            control_nodes=zookeeper_cluster_nodes,
            cluster_nodes=clickhouse_cluster_nodes,
        )

    with And("Receive UID"):
        uid = getuid()

    try:
        with And("I create some replicated table"):
            table_name = f"test{uid}"
            create_simple_table(table_name=table_name)

        with And("I stop maximum available ZooKeeper nodes for such configuration"):
            self.context.cluster.node("zookeeper1").stop()

        with And("I check that table in write mode"):
            retry(cluster.node("clickhouse1").query, timeout=250, delay=1)(
                f"insert into {table_name} values (1,1)", exitcode=0
            )

        with And("I stop one more ZooKeeper node"):
            self.context.cluster.node("zookeeper2").stop()

        with And("I check that table in read only mode"):
            self.context.cluster.node("clickhouse1").query(
                f"insert into {table_name}(Id, partition) values (1,2)",
                exitcode=242,
                message="DB::Exception: Table is in readonly mode",
            )

        with And("I start dropped nodes"):
            self.context.cluster.node("zookeeper1").start()
            self.context.cluster.node("zookeeper2").start()

        with And("I check clean ability"):
            table_insert(table_name=table_name, node_name="clickhouse1")

    finally:
        with Finally("I clean up files"):
            clean_coordination_on_all_nodes()
            self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")


#
#
# @TestScenario
# def standalone_keepers_3(self):
#     """Check that 3 nodes Standalone Keeper Cluster work in write mode
#     with 1 node down and in read mode only with 2 nodes down.
#     """
#     cluster = self.context.cluster
#     keeper_cluster_nodes = cluster.nodes["clickhouse"][9:12]
#     clickhouse_cluster_nodes = cluster.nodes["clickhouse"][:9]
#     cluster_name = '\'Cluster_3shards_with_3replicas\''
#
#     with Given("I create 3 keeper cluster configuration"):
#         create_keeper_cluster_configuration(nodes=keeper_cluster_nodes)
#         with And("I start all standalone Keepers nodes"):
#             time.sleep(10)
#             for name in keeper_cluster_nodes:
#                 cluster.node(name).stop_clickhouse()
#             start_keepers(standalone_keeper_nodes=keeper_cluster_nodes, manual_cleanup=True)
#         create_config_section(control_nodes=keeper_cluster_nodes,
#                               cluster_nodes=clickhouse_cluster_nodes)
#
#     with And("Receive UID"):
#         uid = getuid()
#
#     with And("I instrument logs on all keeper cluster nodes"):
#         instrument_cluster_nodes(test=self, cluster_nodes=keeper_cluster_nodes)
#
#     try:
#         with And("I create some replicated table"):
#             table_name = f"test{uid}"
#             create_simple_table(table_name=table_name, manual_cleanup=True)
#
#         with And("I stop maximum available Keeper nodes for such configuration"):
#             stop_keepers(cluster_nodes=cluster.nodes["clickhouse"][9:10])
#
#         with And("I check that table in write mode"):
#             self.context.cluster.node("clickhouse1").query(f"insert into {table_name} values (1,1)",
#                                                               exitcode=0)
#
#         with And("I stop one more Keeper node"):
#             stop_keepers(cluster_nodes=cluster.nodes["clickhouse"][10:11])
#
#         with And("I check that table in read only mode"):
#             self.context.cluster.node("clickhouse1").query(f"insert into {table_name} values (1,2)",
#                                                               exitcode=242,
#                                                               message="DB::Exception: Table is in readonly mode")
#
#         with And("I start stopped clickhouse keeper nodes"):
#             start_keepers(standalone_keeper_nodes=cluster.nodes["clickhouse"][9:11], manual_cleanup=True)
#
#         with And("I check clean ability"):
#             table_insert(table_name=table_name, node_name="clickhouse1")
#             cluster.node("clickhouse1").query(f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC")
#
#         with And("I start stopped clickhouse keeper nodes"):
#             stop_keepers(cluster_nodes=cluster.nodes["clickhouse"][9:12])
#             for name in keeper_cluster_nodes:
#                 cluster.node(name).start_clickhouse(wait_healthy=False)
#
#     finally:
#         with Finally("I start stopped clickhouses and clean up files"):
#             clean_coordination_on_all_nodes()
#
#
# @TestScenario
# def standalone_keepers_2(self):
#     """Check that 2 nodes Standalone Keeper Cluster work in write mode and
#     with 1 node down in read mode only.
#     """
#     cluster = self.context.cluster
#     keeper_cluster_nodes = cluster.nodes["clickhouse"][9:11]
#     clickhouse_cluster_nodes = cluster.nodes["clickhouse"][:9]
#
#     cluster_name = '\'Cluster_3shards_with_3replicas\''
#
#     with Given("I create 3 keeper cluster configuration"):
#         create_keeper_cluster_configuration(nodes=keeper_cluster_nodes)
#         with And("I start all standalone Keepers nodes"):
#             time.sleep(10)
#             for name in keeper_cluster_nodes:
#                 cluster.node(name).stop_clickhouse()
#             start_keepers(standalone_keeper_nodes=keeper_cluster_nodes, manual_cleanup=True)
#         create_config_section(control_nodes=keeper_cluster_nodes,
#                               cluster_nodes=clickhouse_cluster_nodes)
#
#     with And("Receive UID"):
#         uid = getuid()
#
#     with And("I instrument logs on all keeper cluster nodes"):
#         instrument_cluster_nodes(test=self, cluster_nodes=keeper_cluster_nodes)
#
#     try:
#         with And("I create some replicated table"):
#             table_name = f"test{uid}"
#             create_simple_table(table_name=table_name, manual_cleanup=True)
#
#         with And("I stop one Keeper node"):
#             stop_keepers(cluster_nodes=cluster.nodes["clickhouse"][9:10])
#
#         with And("I check that table in read only mode"):
#             self.context.cluster.node("clickhouse1").query(f"insert into {table_name}(id, partition) values (1,2)",
#                                                               exitcode=242,
#                                                               message="DB::Exception: Table is in readonly mode")
#
#         with And("I start stopped clickhouse keeper nodes"):
#             start_keepers(standalone_keeper_nodes=cluster.nodes["clickhouse"][9:10], manual_cleanup=True)
#
#         with And("I check clean ability"):
#
#             table_insert(table_name=table_name, node_name="clickhouse1")
#
#             cluster.node("clickhouse1").query(f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC")
#
#         with And("I stop clickhouse keeper nodes and start clickhouses"):
#
#             stop_keepers(cluster_nodes=cluster.nodes["clickhouse"][9:11])
#
#             for name in keeper_cluster_nodes:
#                 cluster.node(name).start_clickhouse(wait_healthy=False)
#     finally:
#         with Finally("I start stopped clickhouses and clean up files"):
#             clean_coordination_on_all_nodes()
#
#
# @TestScenario
# def standalone_keepers_1(self):
#     """Check that 1 node Standalone Keeper Cluster work in write mode and
#     when it goes down table in read mode only.
#     """
#     cluster = self.context.cluster
#     keeper_cluster_nodes = cluster.nodes["clickhouse"][9:10]
#     clickhouse_cluster_nodes = cluster.nodes["clickhouse"][:9]
#
#     cluster_name = '\'Cluster_3shards_with_3replicas\''
#
#     with Given("I create 3 keeper cluster configuration"):
#         create_keeper_cluster_configuration(nodes=keeper_cluster_nodes)
#         with And("I start all standalone Keepers nodes"):
#             time.sleep(10)
#             for name in keeper_cluster_nodes:
#                 cluster.node(name).stop_clickhouse()
#             start_keepers(standalone_keeper_nodes=keeper_cluster_nodes, manual_cleanup=True)
#         create_config_section(control_nodes=keeper_cluster_nodes,
#                               cluster_nodes=clickhouse_cluster_nodes)
#     with And("Receive UID"):
#         uid = getuid()
#
#     with And("I instrument logs on all keeper cluster nodes"):
#         instrument_cluster_nodes(test=self, cluster_nodes=keeper_cluster_nodes)
#
#     try:
#         with And("I create some replicated table"):
#             table_name = f"test{uid}"
#             create_simple_table(table_name=table_name, manual_cleanup=True)
#
#         with And("I stop one Keeper node"):
#             stop_keepers(cluster_nodes=keeper_cluster_nodes)
#
#         with And("I check that table in read only mode"):
#             self.context.cluster.node("clickhouse1cmd").query(f"insert into {table_name}(id, partition) values (1,2)",
#                                                               exitcode=242,
#                                                               message="DB::Exception: Table is in readonly mode")
#
#         with And("I start stopped clickhouse keeper nodes"):
#
#             start_keepers(standalone_keeper_nodes=keeper_cluster_nodes, manual_cleanup=True)
#
#         with And("I check clean ability"):
#
#             table_insert(table_name=table_name, node_name="clickhouse1")
#
#             cluster.node("clickhouse1").query(f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC")
#
#         with And("I stop clickhouse keeper nodes and start clickhouses"):
#
#             stop_keepers(cluster_nodes=keeper_cluster_nodes)
#
#             for name in keeper_cluster_nodes:
#                 cluster.node(name).start_clickhouse(wait_healthy=False)
#
#     finally:
#         with Finally("I start stopped clickhouses and clean up files"):
#             clean_coordination_on_all_nodes()


@TestFeature
@Requirements(RQ_SRS_024_ClickHouse_Keeper_WriteAvailability("1.0"))
@Name("keeper_cluster_tests")
def feature(self):
    """Check 2N+1 cluster configurations for
    clickhouse-keeper and zookeeper.
    """
    for scenario in loads(current_module(), Scenario):
        scenario()
