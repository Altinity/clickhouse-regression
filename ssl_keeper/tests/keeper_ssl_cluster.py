import time

from ssl_keeper.requirements import *
from ssl_keeper.tests.steps import *
from helpers.common import *


@TestScenario
def mixed_keepers_3(self):
    """Check that 3 nodes Clickhouse Keeper Cluster work in write mode
    with 1 node down and in read mode only with 2 nodes down.
    """
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")
    try:
        with Given("Receive UID"):
            uid = getuid()

        with And("I create some replicated table"):
            table_name = f"test{uid}"
            node.query(
                f"CREATE TABLE IF NOT EXISTS {table_name}_simple (d DateTime('UTC')) ENGINE = Memory AS SELECT "
                "toDateTime('2000-01-01 00:00:00', 'UTC');"
            )

            create_simple_table(table_name=table_name)

        with And("I stop maximum available Keeper nodes for such configuration"):
            cluster.node("clickhouse3").stop_clickhouse()


        with And("I check that table in write mode"):
            retry(cluster.node("clickhouse1").query, timeout=500, delay=1)(
                f"insert into {table_name} values (1,1)", exitcode=0
            )

        with And("I stop one more Keeper node"):
            cluster.node("clickhouse2").stop_clickhouse()

        if check_clickhouse_version(">23")(self):
            with And("I check that table in read only mode"):
                retry(cluster.node("clickhouse1").query, timeout=300, delay=10)(
                    f"insert into {table_name} values (1,2)",
                    exitcode=242,
                    message="DB::Exception: Table is in readonly mode",
                    steps=False,
                    settings=[("insert_keeper_max_retries", 0)],
                )

        else:
            with And("I check that table in read only mode"):
                retry(cluster.node("clickhouse1").query, timeout=300, delay=10)(
                    f"insert into {table_name} values (1,2)",
                    exitcode=242,
                    message="DB::Exception: Table is in readonly mode",
                    steps=False,
                )

        with And("I start dropped nodes"):
            for name in cluster.nodes["clickhouse"][1:3]:
                cluster.node(name).start_clickhouse(wait_healthy=False)

        with And(f"I check that ruok returns imok"):
            for name in cluster.nodes["clickhouse"][0:3]:
                retry(cluster.node("bash-tools").cmd, timeout=500, delay=1)(
                    f"echo ruok | nc {name} 9281",
                    exitcode=0,
                    message="F",
                )

        with And("I check clean ability"):
            table_insert(table_name=table_name, node_name="clickhouse1")

        pause()

    finally:
        with Finally("I clean up"):
            clean_coordination_on_all_nodes()


@TestScenario
def check_clickhouse_connection_to_keeper(self, node=None, message=None):
    """Check ClickHouse connection to Clickhouse Keeper."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    node.query(
        "SELECT * FROM system.zookeeper WHERE path = '/' FORMAT JSON", message=message
    )


@TestFeature
@Name("keeper_ssl_cluster")
def feature(self):
    """Check 2N+1 cluster configurations for
    clickhouse-keeper and zookeeper.
    """
    for scenario in loads(current_module(), Scenario):
        scenario()
