import time

from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps_ssl_fips import *
from clickhouse_keeper.tests.steps import *
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
            retry(node.query, timeout=300, delay=10)(
                "SELECT 1", message="1", exitcode=0
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

    finally:
        with Finally("I clean up"):
            clean_coordination_on_all_nodes()


@TestScenario
def check_clickhouse_connection_to_keeper(self, node=None, message="keeper"):
    """Check ClickHouse connection to Clickhouse Keeper."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    node.query(
        "SELECT * FROM system.zookeeper WHERE path = '/' FORMAT JSON", message=message
    )


@TestFeature
def openssl_check(self, node=None, message="New, TLSv1.2, Cipher is "):
    """Check ClickHouse connection to Clickhouse Keeper on port is ssl."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)

    ports_list = ["9440", "9281", "9010", "9444", "8443"]

    for port in ports_list:
        with Check(f"port:{port}"):
            with Then(f"I make openssl check"):
                with node.cmd(
                    f"openssl s_client -connect clickhouse1:{port}",
                    no_checks=True,
                    asynchronous=True,
                ) as openssl_process:
                    openssl_process.app.expect(message)


@TestFeature
def openssl_check_v2(self, node=None, message="New, TLSv1.2, Cipher is "):
    """Check ClickHouse connection to Clickhouse Keeper on port is ssl."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)

    ports_list = ["9440", "9281", "9010", "9444", "8443"]

    for port in ports_list:
        with Check(f"port:{port}"):
            with Then(f"I make openssl check"):
                node.cmd(
                    f'openssl s_client -connect clickhouse1:{port} <<< "Q"',
                    message=message,
                )


@TestFeature
@Name("FIPS SSL")
def feature(self):
    """Check 2N+1 cluster configurations for
    clickhouse-keeper and zookeeper.
    """
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

    with Pool(1) as executor:
        try:
            for feature in loads(current_module(), Feature):
                if not feature.name.endswith("FIPS SSL"):
                    Feature(test=feature, parallel=True, executor=executor)()
        finally:
            join()

    with Pool(1) as executor:
        try:
            for scenario in loads(current_module(), Scenario):
                Feature(test=scenario, parallel=True, executor=executor)()
        finally:
            join()
