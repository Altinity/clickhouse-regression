from testflows.core import *

from ssl_keeper.tests.fips_doc_config.common import *
from ssl_server.tests.common import check_is_fips_clickhouse_build


@TestScenario
@Name("keeper")
def keeper_doc_fixture(self):
    """ClickHouse Keeper fixture from docs/fips-config.md (embedded 3-node raft)."""
    cluster = self.context.cluster
    node = cluster.node("clickhouse1")
    self.context.node = node

    retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)

    with When("I replace bundled keeper config with the doc keeper fixture"):
        disable_builtin_keeper_configs(raft=True, zookeeper_client=False)
        apply_doc_keeper_fixture()
        retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)
        verify_doc_fixture_preprocessed(marker="<tcp_port_secure>9281</tcp_port_secure>")
        verify_doc_fixture_preprocessed(marker="<secure>true</secure>")
        verify_keeper_connection()


@TestScenario
@Name("zookeeper")
def zookeeper_doc_fixture(self):
    """Zookeeper client fixture from docs/fips-config.md (secure Keeper endpoints)."""
    cluster = self.context.cluster
    node = cluster.node("clickhouse1")
    self.context.node = node

    retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)

    with When("I replace bundled zookeeper config with the doc zookeeper fixture"):
        disable_builtin_keeper_configs(raft=False, zookeeper_client=True)
        apply_doc_zookeeper_fixture()
        retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)
        verify_doc_fixture_preprocessed(marker="<host>clickhouse1</host>")
        verify_doc_fixture_preprocessed(marker="<secure>1</secure>")
        verify_keeper_connection()


@TestFeature
@Name("doc config")
def feature(self):
    """Regression coverage for docs/fips-config.md keeper and zookeeper fixtures."""
    if not check_is_fips_clickhouse_build(self):
        skip("doc config keeper/zookeeper tests apply only to FIPS builds")

    Scenario(run=keeper_doc_fixture)
    Scenario(run=zookeeper_doc_fixture)
