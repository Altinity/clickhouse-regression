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
