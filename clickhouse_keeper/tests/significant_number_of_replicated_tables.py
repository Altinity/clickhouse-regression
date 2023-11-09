import time

from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *
from helpers.common import *


@TestScenario
def mixed_keepers_3(self, number_of_tables=100):
    """Check Clickhouse Keeper Cluster performance in case of insert into significant number of replicated tables."""
    cluster = self.context.cluster

    if self.context.ssl == "true":
        start_mixed_keeper_ssl(
            cluster_nodes=cluster.nodes["clickhouse"][:9],
            control_nodes=cluster.nodes["clickhouse"][0:3],
            rest_cluster_nodes=cluster.nodes["clickhouse"][3:9],
        )
    else:
        start_mixed_keeper(
            cluster_nodes=cluster.nodes["clickhouse"][:9],
            control_nodes=cluster.nodes["clickhouse"][0:3],
            rest_cluster_nodes=cluster.nodes["clickhouse"][3:9],
        )

    list_of_tables = []

    try:
        with And("I create some replicated table"):
            for i in range(0, number_of_tables):
                table_name = f"test{getuid()}"
                with When({table_name}):
                    create_simple_table(table_name=table_name)
                    list_of_tables.append(table_name)

        with And("I make insert into table"):
            for table_name in list_of_tables:
                with When({table_name}):
                    retry(cluster.node("clickhouse1").query, timeout=250, delay=1)(
                        f"insert into {table_name} values (1,1)", exitcode=0
                    )

    finally:
        with Finally("I clean up"):
            clean_coordination_on_all_nodes()
            self.context.cluster.node("clickhouse1").command(f"rm -rf /share/")


@TestScenario
def zookeepers_3(self, number_of_tables=100):
    """Check ZooKeeper Cluster performance in case of insert into significant number of replicated tables."""

    cluster = self.context.cluster
    zookeeper_cluster_nodes = cluster.nodes["zookeeper"][:3]
    clickhouse_cluster_nodes = cluster.nodes["clickhouse"][:9]

    if self.context.ssl == "true":
        xfail("zookeeper ssl is not supported by tests")

    with Given("I add ZooKeeper server configuration file to ClickHouse servers"):
        create_config_section(
            control_nodes=zookeeper_cluster_nodes,
            cluster_nodes=clickhouse_cluster_nodes,
        )
    list_of_tables = []

    try:
        with And("I create some replicated tables"):
            for i in range(0, number_of_tables):
                table_name = f"test{getuid()}"
                with When({table_name}):
                    create_simple_table(table_name=table_name)
                    list_of_tables.append(table_name)

        with And("I make insert into tables"):
            for table_name in list_of_tables:
                with When({table_name}):
                    retry(cluster.node("clickhouse1").query, timeout=250, delay=1)(
                        f"insert into {table_name} values (1,1)", exitcode=0
                    )

    finally:
        with Finally("I clean up files"):
            clean_coordination_on_all_nodes()
            self.context.cluster.node("clickhouse1").command(f"rm -rf /share/")


@TestFeature
@Name("significant number of replicated tables")
def feature(self):
    """Check ZK/Clickhouse Keeper performance in case of insert into significant number of replicated tables."""
    for scenario in loads(current_module(), Scenario):
        scenario()
