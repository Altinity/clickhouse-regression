from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *
from clickhouse_keeper.tests.common import *
from clickhouse_keeper.tests.fips import (
    server_connection_openssl_client,
    tcp_connection_clickhouse_client,
)
from helpers.common import *


@TestScenario
def check_clickhouse_connection_to_keeper(self, node=None, message="keeper"):
    """Check ClickHouse's connection to ClickHouse Keeper."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Given("I check that ClickHouse is connected to Keeper"):
        node.query(
            "SELECT * FROM system.zookeeper WHERE path = '/' FORMAT JSON",
            message=message,
        )


@TestFeature
def openssl_check(self, node=None, message="New, TLSv1.2, Cipher is "):
    """Check that ClickHouse's connection to ClickHouse Keeper on all ports is SSL."""

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
def server_connection_openssl_client_check(self, node=None):
    """Check that ClickHouse's SSL connection on all ports is working correctly with different protocols and cypher combinations."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)

    ports_list = define(
        "All ports for testing", ["9440", "9281", "9010", "9444", "8443"]
    )

    for port in ports_list:
        with Check(f"port:{port}"):
            server_connection_openssl_client(port=port)


@TestFeature
def tcp_connection_check(self, node=None):
    """Check Clickhouse Keeper FIPS compatible TCP connections for all ports available for TCP connection."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)

    ports_list = define("All ports for testing", ["9440"])

    for port in ports_list:
        with Check(f"port:{port}"):
            tcp_connection_clickhouse_client(
                node=self.context.cluster.node("clickhouse1"), port=port
            )


@TestFeature
@Name("ports ssl fips")
def feature(self):
    """Different checks for FIPS SSL connections on ports for Clickhouse Keeper."""
    cluster = self.context.cluster
    self.context.node = self.context.cluster.node("clickhouse1")

    start_mixed_keeper_ssl(
        cluster_nodes=cluster.nodes["clickhouse"][:9],
        control_nodes=cluster.nodes["clickhouse"][0:3],
        rest_cluster_nodes=cluster.nodes["clickhouse"][3:9],
    )

    with Pool(1) as executor:
        try:
            for scenario in loads(current_module(), Scenario):
                Feature(test=scenario, parallel=True, executor=executor)()
        finally:
            join()

    with Pool(1) as executor:
        try:
            for feature in loads(current_module(), Feature):
                if not feature.name.endswith("ports ssl fips"):
                    Feature(test=feature, parallel=True, executor=executor)()
        finally:
            join()
