import time

from clickhouse_keeper.tests.steps import *
from clickhouse_keeper.requirements import *
from helpers.common import *


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
    if self.context.ssl == "true":
        try:
            start_mixed_keeper_ssl(
                cluster_nodes=cluster_nodes,
                control_nodes=control_nodes,
                rest_cluster_nodes=rest_cluster_nodes,
            )

            with And("I create simple table"):
                create_simple_table()

            with And("I make simple synchronization check"):
                simple_synchronization_check()
        finally:
            with Finally("I clean up"):
                clean_coordination_on_all_nodes()

    else:
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
                    modify=True,
                )

            with And("I create mixed 3 nodes Keeper server config file"):
                create_keeper_cluster_configuration(
                    nodes=control_nodes,
                    check_preprocessed=False,
                    restart=False,
                    modify=True,
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
    RQ_SRS_024_ClickHouse_Keeper_Configurations_DifferentKeeperClustersForEachShard(
        "1.0"
    )
)
def different_start_up(self):
    """Check 9 nodes ClickHouse server with different 3 nodes Keeper for each shard start up and simple synchronization"""
    if self.context.ssl == "true":
        cluster = self.context.cluster
        try:
            with Given("I create 3 nodes Keeper server config section for nodes 1-3"):
                start_mixed_keeper_ssl(
                    control_nodes=cluster.nodes["clickhouse"][:3],
                    cluster_nodes=cluster.nodes["clickhouse"][:3],
                    rest_cluster_nodes="no_rest_nodes",
                )
            with And("I create 3 nodes Keeper server config section for nodes 4-6"):
                start_mixed_keeper_ssl(
                    control_nodes=cluster.nodes["clickhouse"][3:6],
                    cluster_nodes=cluster.nodes["clickhouse"][3:6],
                    rest_cluster_nodes="no_rest_nodes",
                )
            with And("I create 3 nodes Keeper server config section for nodes 4-6"):
                start_mixed_keeper_ssl(
                    control_nodes=cluster.nodes["clickhouse"][6:9],
                    cluster_nodes=cluster.nodes["clickhouse"][6:9],
                    rest_cluster_nodes="no_rest_nodes",
                )
        finally:
            with Finally("I clean up"):
                clean_coordination_on_all_nodes()
    else:
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
    if check_clickhouse_version("<23.3")(self):
        if self.context.ssl == "true":
            xfail("was not created for the SSL configuration")
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
    else:
        xfail("test doesn't work from 23.3")



@TestFeature
@Requirements(RQ_SRS_024_ClickHouse_Keeper_Configurations("1.0"))
@Name("servers start up")
def feature(self):
    """Check different ClickHouse server configurations"""
    for scenario in loads(current_module(), Scenario):
        scenario()
