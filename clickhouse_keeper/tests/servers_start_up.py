import time

from clickhouse_keeper.tests.steps import *
from clickhouse_keeper.requirements import *


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_Configurations_KeeperOnOneSharedShard("1.0"))
def mixed_start_up(
    self, control_nodes=None, cluster_nodes=None, rest_cluster_nodes=None
):
    """Start 9 nodes ClickHouse server with one shared 3 nodes shard Keeper  and simple synchronization."""
    cluster = self.context.cluster
    control_nodes = (
        cluster.nodes["clickhouse"][6:9] if control_nodes is None else control_nodes
    )
    cluster_nodes = (
        cluster.nodes["clickhouse"][0:9] if cluster_nodes is None else cluster_nodes
    )
    rest_cluster_nodes = (
        cluster.nodes["clickhouse"][0:6]
        if rest_cluster_nodes is None
        else rest_cluster_nodes
    )
    try:
        with Given("I stop all ClickHouse server nodes"):
            for name in cluster_nodes:
                cluster.node(name).stop_clickhouse(safe=False)

        with And("I clean ClickHouse Keeper server nodes"):
            clean_coordination_on_all_nodes()

        with And("I create server Keeper config"):
            create_config_section(
                control_nodes=control_nodes,
                cluster_nodes=cluster_nodes,
                check_preprocessed=False,
                restart=False,
                modify=False,
            )

        with And("I create mixed 3 nodes Keeper server config file"):
            create_keeper_cluster_configuration(
                nodes=control_nodes,
                check_preprocessed=False,
                restart=False,
                modify=False,
            )

        with And("I start mixed ClickHouse server nodes"):
            for name in control_nodes:
                cluster.node(name).start_clickhouse(wait_healthy=False)

        with And("I start rest ClickHouse server nodes"):
            for name in rest_cluster_nodes:
                retry(cluster.node(name).start_clickhouse, timeout=100, delay=1)()

        with And("I create simple table"):
            create_simple_table()

        with And("I make simple synchronization check"):
            simple_synchronization_check()

    finally:
        with Finally("I clean up"):
            clean_coordination_on_all_nodes()


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Configurations_StandaloneKeeperCluster("1.0")
)
def standalone_start_up(self):
    """Check 9 nodes ClickHouse server and standalone 3 nodes Keeper start up and simple synchronization"""
    clean_coordination_on_all_nodes()
    cluster = self.context.cluster
    try:
        with Given("I create config 3 nodes Keeper server"):
            create_keeper_cluster_configuration(nodes=cluster.nodes["clickhouse"][9:12])

        with Given("I start all standalone Keepers nodes"):
            for name in cluster.nodes["clickhouse"][:12]:
                cluster.node(name).stop_clickhouse()
            start_keepers(
                standalone_keeper_nodes=cluster.nodes["clickhouse"][9:12],
                manual_cleanup=True,
            )

        with And("I add Keeper server configuration file"):
            create_config_section(
                control_nodes=cluster.nodes["clickhouse"][9:12],
                cluster_nodes=cluster.nodes["clickhouse"][:12],
                check_preprocessed=False,
            )

        with And("I start ClickHouse server"):
            time.sleep(3)
            for name in cluster.nodes["clickhouse"][:9]:
                cluster.node(name).start_clickhouse()

        with And("I create simple table"):
            create_simple_table(manual_cleanup=True)

        with And("I make simple synchronization check"):
            simple_synchronization_check()

    finally:
        with Finally("I clean up"):
            with By("Dropping table if exists", flags=TE):
                self.context.cluster.node("clickhouse1").query(
                    f"DROP TABLE IF EXISTS test ON CLUSTER "
                    "'Cluster_3shards_with_3replicas' SYNC"
                )

            with By("I start clickhouse servers", flags=TE):
                stop_keepers(cluster_nodes=cluster.nodes["clickhouse"][9:12])
                for name in cluster.nodes["clickhouse"][9:12]:
                    self.context.cluster.node(name).start_clickhouse(wait_healthy=False)
                    time.sleep(5)

            clean_coordination_on_all_nodes()


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Configurations_DifferentKeeperClustersForEachShard(
        "1.0"
    )
)
def different_start_up(self):
    """Check 9 nodes ClickHouse server with different 3 nodes Keeper for each shard start up and simple synchronization"""
    cluster = self.context.cluster
    try:
        with Given("I create 3 nodes Keeper server config section for nodes 1-3"):
            start_mixed_keeper(
                control_nodes=cluster.nodes["clickhouse"][:3],
                cluster_nodes=cluster.nodes["clickhouse"][:3],
                rest_cluster_nodes="no_rest_nodes",
            )
        with And("I create 3 nodes Keeper server config section for nodes 4-6"):
            start_mixed_keeper(
                control_nodes=cluster.nodes["clickhouse"][3:6],
                cluster_nodes=cluster.nodes["clickhouse"][3:6],
                rest_cluster_nodes="no_rest_nodes",
            )
        with And("I create 3 nodes Keeper server config section for nodes 4-6"):
            start_mixed_keeper(
                control_nodes=cluster.nodes["clickhouse"][6:9],
                cluster_nodes=cluster.nodes["clickhouse"][6:9],
                rest_cluster_nodes="no_rest_nodes",
            )
    finally:
        with Finally("I clean up"):
            clean_coordination_on_all_nodes()


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Configurations_DifferentKeeperClustersForEachShardsWithOneShared(
        "1.0"
    )
)
def different_shared_start_up(self):
    """Check 9 nodes ClickHouse server with different 3 nodes Keeper clusters for each shard with one shared start up
    and synchronization"""
    cluster = self.context.cluster
    cluster_nodes = cluster.nodes["clickhouse"][:9]
    control_nodes = cluster.nodes["clickhouse"][6:9]
    try:
        with Given("I stop all ClickHouse server nodes"):
            for name in cluster_nodes:
                cluster.node(name).stop_clickhouse(safe=False)

        with And("I clean ClickHouse Keeper server nodes"):
            clean_coordination_on_all_nodes()

        with And("I create server Keeper config"):
            create_config_section(
                control_nodes=control_nodes,
                cluster_nodes=cluster_nodes,
                check_preprocessed=False,
                restart=False,
                modify=False,
            )

        with And("I create main mixed 3 nodes Keeper server config file"):
            create_keeper_cluster_configuration(
                nodes=control_nodes,
                check_preprocessed=False,
                restart=False,
                modify=False,
            )

        with And("I create first sub mixed 3 nodes Keeper server config file"):
            create_keeper_cluster_configuration(
                nodes=cluster.nodes["clickhouse"][:3],
                check_preprocessed=False,
                restart=False,
                modify=False,
            )

        with And("I create second sub mixed 3 nodes Keeper server config file"):
            create_keeper_cluster_configuration(
                nodes=cluster.nodes["clickhouse"][3:6],
                check_preprocessed=False,
                restart=False,
                modify=False,
            )

        with And("I start mixed ClickHouse server nodes"):
            for name in control_nodes:
                cluster.node(name).start_clickhouse(wait_healthy=False)

        with And("I start first 3 ClickHouse server nodes"):
            for name in cluster.nodes["clickhouse"][:3]:
                retry(cluster.node(name).start_clickhouse, timeout=100, delay=1)()

        with And("I start second 3 ClickHouse server nodes"):
            for name in cluster.nodes["clickhouse"][3:6]:
                retry(cluster.node(name).start_clickhouse, timeout=100, delay=1)()

    finally:
        with Finally("I clean up"):
            clean_coordination_on_all_nodes()


# @TestScenario
# @Requirements(RQ_SRS_024_ClickHouse_Keeper_CommandLineOptions_NoDaemon("1.0"))
# def standalone_start_up_no_daemon(self):
#     """Check standalone 3 nodes Keeper cluster start up and synchronization
#     when one node in no daemon mode
#     """
#     cluster = self.context.cluster
#     time.sleep(30)
#     try:
#         with Given("I create 3 nodes Keeper server config section"):
#             create_keeper_cluster_configuration(nodes=cluster.nodes["clickhouse"][9:12])
#             for name in cluster.nodes["clickhouse"][9:12]:
#                 cluster.node(name).stop_clickhouse()
#
#         with Given(
#             "I start stanalone keeper servers except the last on in daemon mode"
#         ):
#             for name in cluster.nodes["clickhouse"][9:11]:
#                 node = cluster.node(name)
#                 with When(f"I start keeper {name} in daemon mode"):
#                     with By("starting keeper process"):
#                         node.cmd("rm -rf /tmp/clickhouse-keeper.pid")
#                         node.cmd(
#                             "clickhouse keeper --config /etc/clickhouse-server/config.xml"
#                             " --pidfile=/tmp/clickhouse-keeper.pid --daemon",
#                             exitcode=0,
#                         )
#
#                     with And("checking that keeper pid file was created"):
#                         node.cmd(
#                             "ls /tmp/clickhouse-keeper.pid",
#                             exitcode=0,
#                             message="/tmp/clickhouse-keeper.pid",
#                         )
#
#         with Then(f"I check that I can start last keeper {name} in no daemon mode"):
#             name = cluster.nodes["clickhouse"][11]
#             node = cluster.node(name)
#             node.cmd("rm -rf /tmp/clickhouse-keeper.pid")
#             with node.cmd(
#                 "clickhouse keeper --config /etc/clickhouse-server/config.xml"
#                 " --pidfile=/tmp/clickhouse-keeper.pid",
#                 no_checks=True,
#                 asynchronous=True,
#             ) as keeper_process:
#                 keeper_process.app.expect("Quorum initialized")
#     finally:
#         with Finally("I clean up"):
#             stop_keepers(cluster_nodes=cluster.nodes["clickhouse"][9:11])
#             time.sleep(20)
#             for name in cluster.nodes["clickhouse"][9:12]:
#                 cluster.node(name).start_clickhouse(wait_healthy=False)
#             clean_coordination_on_all_nodes()


@TestFeature
@Requirements(RQ_SRS_024_ClickHouse_Keeper_Configurations("1.0"))
@Name("servers_start_up")
def feature(self):
    """Check different ClickHouse server configurations"""
    for scenario in loads(current_module(), Scenario):
        scenario()
