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
    """Doc fips.xml (server + zookeeper) and keeper.xml from docs/fips-config.md."""
    cluster = self.context.cluster
    node = cluster.node("clickhouse1")
    self.context.node = node

    with Given("cluster is healthy before applying the doc fixtures"):
        retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)

    def apply_steps():
        with When("I apply the doc fips and keeper fixtures"):
            apply_doc_fips_server_fixture(restart=False)
            apply_doc_keeper_fixture(restart=True)

    def verify_steps():
        with Then("preprocessed config should reflect the zookeeper fixture"):
            verify_doc_fixture_preprocessed(marker="<port>2281</port>")
            verify_doc_fixture_preprocessed(marker="<secure>1</secure>")

        with And("preprocessed config should reflect the keeper fixture"):
            verify_doc_fixture_preprocessed(
                marker=f"<tcp_port_secure>{FIPS_DOC_KEEPER_CLIENT_PORT}</tcp_port_secure>"
            )
            verify_doc_fixture_preprocessed(marker="<secure>true</secure>")

        with And("only configured listener ports should be open"):
            verify_cluster_listening_ports(allowed_ports=KEEPER_DOC_CLUSTER_LISTEN_PORTS)

        with And("Keeper HTTP readiness endpoint should not be exposed"):
            verify_cluster_keeper_http_readiness_not_exposed()

        with And("ClickHouse should reach Keeper over secure coordination"):
            verify_keeper_connection()

    def cleanup_steps():
        restore_builtin_keeper_configs()

    _run_doc_fixture_scenario(apply_steps, verify_steps, cleanup_steps)


@TestFeature
@Name("doc config")
def feature(self):
    """Regression coverage for fips doc configs."""
    Scenario(run=keeper_doc_fixture)
