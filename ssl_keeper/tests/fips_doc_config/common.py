import os

from testflows.core import *

from ssl_server.tests.fips_doc_config.common import verify_doc_fixture_preprocessed

FIPS_DOC_FIXTURES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "configs", "fips_doc"
)
KEEPER_CLUSTER_NODES = ("clickhouse1", "clickhouse2", "clickhouse3")
BUILTIN_RAFT_CONFIG = "/etc/clickhouse-server/config.d/raft_keeper.xml"
BUILTIN_ZK_CONFIG = "/etc/clickhouse-server/config.d/secure_keeper.xml"
DOC_KEEPER_CONFIG = "/etc/clickhouse-server/config.d/keeper-doc.xml"
DOC_ZOOKEEPER_CONFIG = "/etc/clickhouse-server/config.d/zookeeper-doc.xml"


def fips_doc_fixture_path(relative_path):
    return os.path.normpath(os.path.join(FIPS_DOC_FIXTURES_DIR, relative_path))


def read_fips_doc_fixture(relative_path):
    with open(fips_doc_fixture_path(relative_path), encoding="utf-8") as fixture_file:
        return fixture_file.read()


def _restart_cluster_nodes(cluster, nodes, timeout=300):
    for name in nodes:
        cluster.node(name).restart_clickhouse(timeout=timeout)


@TestStep(Given)
def disable_builtin_keeper_configs(
    self,
    nodes=None,
    raft=True,
    zookeeper_client=True,
    restart=False,
    timeout=300,
):
    """Move bundled raft and/or zookeeper client configs aside for doc fixtures."""
    if nodes is None:
        nodes = KEEPER_CLUSTER_NODES

    cluster = self.context.cluster
    disabled = []
    paths = []
    if raft:
        paths.append(BUILTIN_RAFT_CONFIG)
    if zookeeper_client:
        paths.append(BUILTIN_ZK_CONFIG)

    try:
        with When("I disable bundled keeper and zookeeper config files"):
            for name in nodes:
                node = cluster.node(name)
                for path in paths:
                    backup = f"{path}.bak"
                    node.command(
                        f"test -f '{path}' && mv '{path}' '{backup}' || true",
                        exitcode=0,
                    )
                    disabled.append((node, path, backup))

            if restart:
                _restart_cluster_nodes(cluster, nodes, timeout=timeout)

        yield disabled
    finally:
        with Finally("I restore bundled keeper and zookeeper config files"):
            for node, path, backup in reversed(disabled):
                node.command(
                    f"test -f '{backup}' && mv '{backup}' '{path}' || true",
                    no_checks=True,
                )
            for name in nodes:
                cluster.node(name).command(f"rm -f {DOC_KEEPER_CONFIG}", no_checks=True)
                cluster.node(name).command(
                    f"rm -f {DOC_ZOOKEEPER_CONFIG}", no_checks=True
                )
            if disabled:
                _restart_cluster_nodes(cluster, nodes, timeout=timeout)


@TestStep(Given)
def apply_doc_keeper_fixture(self, nodes=None, restart=True, timeout=300):
    """Install docs/fips-config.md keeper.xml on each raft node."""
    if nodes is None:
        nodes = KEEPER_CLUSTER_NODES

    cluster = self.context.cluster
    template = read_fips_doc_fixture("server/keeper.xml")

    try:
        with When("I install the doc keeper fixture on all keeper nodes"):
            for index, name in enumerate(nodes, start=1):
                node = cluster.node(name)
                content = template.format(server_id=index)
                node.command(
                    f"cat <<'FIPS_DOC_KEEPER' > {DOC_KEEPER_CONFIG}\n{content}\nFIPS_DOC_KEEPER",
                    exitcode=0,
                )

            if restart:
                _restart_cluster_nodes(cluster, nodes, timeout=timeout)

        yield DOC_KEEPER_CONFIG
    finally:
        with Finally("I remove the doc keeper fixture"):
            for name in nodes:
                cluster.node(name).command(f"rm -f {DOC_KEEPER_CONFIG}", no_checks=True)
            if restart:
                _restart_cluster_nodes(cluster, nodes, timeout=timeout)


@TestStep(Given)
def apply_doc_zookeeper_fixture(self, nodes=None, restart=True, timeout=300):
    """Install docs/fips-config.md zookeeper.xml on all ClickHouse nodes."""
    if nodes is None:
        nodes = KEEPER_CLUSTER_NODES

    cluster = self.context.cluster
    content = read_fips_doc_fixture("server/zookeeper.xml")

    try:
        with When("I install the doc zookeeper fixture on all nodes"):
            for name in nodes:
                node = cluster.node(name)
                node.command(
                    f"cat <<'FIPS_DOC_ZK' > {DOC_ZOOKEEPER_CONFIG}\n{content}\nFIPS_DOC_ZK",
                    exitcode=0,
                )

            if restart:
                _restart_cluster_nodes(cluster, nodes, timeout=timeout)

        yield DOC_ZOOKEEPER_CONFIG
    finally:
        with Finally("I remove the doc zookeeper fixture"):
            for name in nodes:
                cluster.node(name).command(
                    f"rm -f {DOC_ZOOKEEPER_CONFIG}", no_checks=True
                )
            if restart:
                _restart_cluster_nodes(cluster, nodes, timeout=timeout)


@TestStep(Then)
def verify_keeper_connection(self, node=None, message="keeper"):
    """Verify ClickHouse can query embedded Keeper over secure coordination."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    node.query(
        "SELECT * FROM system.zookeeper WHERE path = '/' FORMAT JSON",
        message=message,
    )
