from testflows.core import *

from ssl_keeper.tests.fips_doc_config.common import *


def _run_doc_fixture_scenario(apply_steps, verify_steps, cleanup_steps):
    """Apply fixtures, run checks, then tear fixtures down explicitly."""
    try:
        apply_steps()
        verify_steps()
    finally:
        cleanup_steps()


@TestScenario
@Name("keeper")
def keeper_doc_fixture(self):
    """ClickHouse Keeper fixture from docs/fips-config.md (embedded 3-node raft)."""
    cluster = self.context.cluster
    node = cluster.node("clickhouse1")
    self.context.node = node

    with Given("cluster is healthy before applying the doc keeper fixture"):
        retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)

    def apply_steps():
        with When("I replace bundled keeper config with the doc keeper fixture"):
            disable_builtin_keeper_configs(raft=True, zookeeper_client=False)
            apply_doc_keeper_fixture()

    def verify_steps():
        retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)

        with Then("preprocessed config should reflect the fixture"):
            verify_doc_fixture_preprocessed(marker="<tcp_port_secure>9281</tcp_port_secure>")
            verify_doc_fixture_preprocessed(marker="<secure>true</secure>")

        with And("only configured listener ports should be open"):
            verify_cluster_listening_ports(allowed_ports=KEEPER_DOC_CLUSTER_LISTEN_PORTS)

        with And("ClickHouse should reach Keeper over secure coordination"):
            verify_keeper_connection()

    def cleanup_steps():
        remove_doc_keeper_fixture(restart=False)
        restore_builtin_keeper_configs()

    _run_doc_fixture_scenario(apply_steps, verify_steps, cleanup_steps)


@TestScenario
@Name("zookeeper")
def zookeeper_doc_fixture(self):
    """Zookeeper client fixture from docs/fips-config.md (secure Keeper endpoints)."""
    cluster = self.context.cluster
    node = cluster.node("clickhouse1")
    self.context.node = node

    with Given("cluster is healthy before applying the doc zookeeper fixture"):
        retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)

    def apply_steps():
        with When("I replace bundled zookeeper config with the doc zookeeper fixture"):
            disable_builtin_keeper_configs(raft=False, zookeeper_client=True)
            apply_doc_zookeeper_fixture()

    def verify_steps():
        retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)

        with Then("preprocessed config should reflect the fixture"):
            verify_doc_fixture_preprocessed(marker="<host>clickhouse1</host>")
            verify_doc_fixture_preprocessed(marker="<secure>1</secure>")

        with And("only configured listener ports should be open"):
            verify_cluster_listening_ports(allowed_ports=KEEPER_DOC_CLUSTER_LISTEN_PORTS)

        with And("ClickHouse should reach Keeper over secure coordination"):
            verify_keeper_connection()

    def cleanup_steps():
        remove_doc_zookeeper_fixture(restart=False)
        restore_builtin_keeper_configs()

    _run_doc_fixture_scenario(apply_steps, verify_steps, cleanup_steps)


@TestFeature
@Name("doc config")
def feature(self):
    """Regression coverage for fips doc configs."""
    Scenario(run=keeper_doc_fixture)
    Scenario(run=zookeeper_doc_fixture)
