import os

from testflows.core import *

from ssl_server.tests.fips_doc_config.common import (
    DOC_SERVER_PORTS,
    FIPS_DOC_KEEPER_CLIENT_PORT,
    FIPS_DOC_KEEPER_RAFT_PORT,
    FIPS_DOC_SERVER_FIXTURE,
    verify_doc_fixture_preprocessed,
    verify_keeper_http_readiness_not_exposed,
    verify_server_listening_ports,
)

FIPS_DOC_FIXTURES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "configs", "fips_doc"
)
SSL_SERVER_FIPS_DOC_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "ssl_server", "configs", "fips_doc")
)
KEEPER_CLUSTER_NODES = ("clickhouse1", "clickhouse2", "clickhouse3")
KEEPER_DOC_KEEPER_LISTEN_PORTS = frozenset(
    {FIPS_DOC_KEEPER_CLIENT_PORT, FIPS_DOC_KEEPER_RAFT_PORT}
)
KEEPER_DOC_CLUSTER_LISTEN_PORTS = DOC_SERVER_PORTS | KEEPER_DOC_KEEPER_LISTEN_PORTS
BUILTIN_RAFT_CONFIG = "/etc/clickhouse-server/config.d/raft_keeper.xml"
BUILTIN_ZK_CONFIG = "/etc/clickhouse-server/config.d/secure_keeper.xml"
BUILTIN_FIPS_CONFIG = "/etc/clickhouse-server/config.d/fips.xml"
DOC_KEEPER_CONFIG = "/etc/clickhouse-server/config.d/keeper.xml"
EMPTY_CONFIG = "<clickhouse></clickhouse>\n"
KEEPER_BUNDLED_CONFIG_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "configs", "clickhouse", "config.d")
)
MOUNTED_BUNDLED_CONFIGS = {
    BUILTIN_FIPS_CONFIG: "fips.xml",
    BUILTIN_ZK_CONFIG: "secure_keeper.xml",
}
MOUNTED_RAFT_CONFIGS = {
    BUILTIN_RAFT_CONFIG: "raft_keeper.xml",
}
DOC_PORT_REMOVALS = (
    '<tcp_port remove="1" />',
    '<http_port remove="1" />',
    '<interserver_http_port remove="1" />',
)


def fips_doc_fixture_path(relative_path):
    return os.path.normpath(os.path.join(FIPS_DOC_FIXTURES_DIR, relative_path))


def ssl_server_fips_doc_fixture_path(relative_path):
    return os.path.normpath(os.path.join(SSL_SERVER_FIPS_DOC_DIR, relative_path))


def read_fips_doc_fixture(relative_path):
    with open(fips_doc_fixture_path(relative_path), encoding="utf-8") as fixture_file:
        return fixture_file.read()


def read_ssl_server_fips_doc_fixture(relative_path):
    with open(ssl_server_fips_doc_fixture_path(relative_path), encoding="utf-8") as fixture_file:
        return fixture_file.read()


def read_bundled_keeper_config(filename):
    with open(os.path.join(KEEPER_BUNDLED_CONFIG_DIR, filename), encoding="utf-8") as config_file:
        return config_file.read()


def read_bundled_raft_config(node_name):
    path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "configs",
        node_name,
        "config.d",
        "raft_keeper.xml",
    )
    with open(os.path.normpath(path), encoding="utf-8") as config_file:
        return config_file.read()


def build_keeper_doc_fips_content():
    """Apply doc fips.xml port removals on top of the bundled cluster fips."""
    bundled = read_bundled_keeper_config("fips.xml")
    doc = read_ssl_server_fips_doc_fixture(FIPS_DOC_SERVER_FIXTURE)

    for removal in DOC_PORT_REMOVALS:
        if removal not in bundled and removal in doc:
            bundled = bundled.replace("<clickhouse>", f"<clickhouse>\n    {removal}", 1)

    return bundled


def _write_node_config(node, dest, content):
    node.command(
        f"cat <<'FIPS_DOC_CONFIG' > {dest}\n{content}\nFIPS_DOC_CONFIG",
        exitcode=0,
    )


def _restore_mounted_configs(cluster, nodes, configs, raft=False):
    for name in nodes:
        node = cluster.node(name)
        for dest, filename in configs.items():
            if raft:
                content = read_bundled_raft_config(name)
            else:
                content = read_bundled_keeper_config(filename)
            _write_node_config(node, dest, content)


def _restart_cluster_nodes(cluster, nodes, timeout=300):
    for name in nodes:
        cluster.node(name).stop_clickhouse(timeout=timeout, safe=False)
    for name in nodes:
        cluster.node(name).start_clickhouse(timeout=timeout, wait_healthy=False)


def _wait_cluster_healthy(cluster, nodes, timeout=300):
    for name in nodes:
        node = cluster.node(name)
        retry(node.command, timeout=timeout, delay=10)(
            'clickhouse client --secure --host 127.0.0.1 --port 9440 -q "SELECT 1"',
            message="1",
            exitcode=0,
        )


@TestStep(Given)
def disable_builtin_keeper_configs(
    self,
    nodes=None,
    raft=True,
    zookeeper_client=True,
    fips=False,
):
    """Track bundled configs that doc fixtures replace on bind-mounted paths."""
    if nodes is None:
        nodes = KEEPER_CLUSTER_NODES

    cluster = self.context.cluster
    disabled = getattr(self.context, "fips_doc_disabled_configs", [])
    if disabled is None:
        disabled = []

    paths = []
    if raft:
        paths.append(BUILTIN_RAFT_CONFIG)
    if zookeeper_client:
        paths.append(BUILTIN_ZK_CONFIG)
    if fips:
        paths.append(BUILTIN_FIPS_CONFIG)

    with When("I disable bundled keeper and server config files"):
        for name in nodes:
            node = cluster.node(name)
            for path in paths:
                disabled.append((node, path, None))

    self.context.fips_doc_disabled_configs = disabled
    return disabled


@TestStep(Finally)
def restore_builtin_keeper_configs(
    self,
    nodes=None,
    restart=True,
    timeout=300,
):
    """Restore bind-mounted configs from the repo after doc fixture tests."""
    disabled = getattr(self.context, "fips_doc_disabled_configs", []) or []
    if (
        not disabled
        and not getattr(self.context, "fips_doc_server_installed", False)
        and not getattr(self.context, "fips_doc_keeper_installed", False)
    ):
        return

    if nodes is None:
        nodes = KEEPER_CLUSTER_NODES

    cluster = self.context.cluster
    with By("I restore bundled keeper and server config files"):
        _restore_mounted_configs(cluster, nodes, MOUNTED_BUNDLED_CONFIGS)
        _restore_mounted_configs(cluster, nodes, MOUNTED_RAFT_CONFIGS, raft=True)
        for name in nodes:
            cluster.node(name).command(f"rm -f {DOC_KEEPER_CONFIG}", no_checks=True)

        if restart:
            _restart_cluster_nodes(cluster, nodes, timeout=timeout)
            _wait_cluster_healthy(cluster, nodes, timeout=timeout)

    self.context.fips_doc_disabled_configs = []
    self.context.fips_doc_server_installed = False
    self.context.fips_doc_keeper_installed = False


@TestStep(Given)
def apply_doc_fips_server_fixture(
    self,
    nodes=None,
    restart=True,
    timeout=300,
):
    """Install doc fips.xml and zookeeper.xml on all nodes."""
    if nodes is None:
        nodes = KEEPER_CLUSTER_NODES

    cluster = self.context.cluster
    fips_content = build_keeper_doc_fips_content()
    zookeeper_content = read_fips_doc_fixture("server/zookeeper.xml")

    with When("I install the doc fips and zookeeper fixtures on all nodes"):
        disable_builtin_keeper_configs(
            nodes=nodes, raft=False, zookeeper_client=True, fips=True
        )
        for name in nodes:
            node = cluster.node(name)
            node.command("mkdir -p /etc/clickhouse-server/config.d", exitcode=0)
            _write_node_config(node, BUILTIN_FIPS_CONFIG, fips_content)
            _write_node_config(node, BUILTIN_ZK_CONFIG, zookeeper_content)

        if restart:
            _restart_cluster_nodes(cluster, nodes, timeout=timeout)
            _wait_cluster_healthy(cluster, nodes, timeout=timeout)

    self.context.fips_doc_server_installed = True
    return BUILTIN_FIPS_CONFIG


@TestStep(Given)
def apply_doc_keeper_fixture(self, nodes=None, restart=True, timeout=300):
    """Install docs/fips-config.md keeper.xml on each raft node."""
    if nodes is None:
        nodes = KEEPER_CLUSTER_NODES

    cluster = self.context.cluster
    template = read_fips_doc_fixture("server/keeper.xml")

    with When("I install the doc keeper fixture on all keeper nodes"):
        disable_builtin_keeper_configs(
            nodes=nodes, raft=True, zookeeper_client=False, fips=False
        )
        for index, name in enumerate(nodes, start=1):
            node = cluster.node(name)
            content = template.format(server_id=index)
            _write_node_config(node, BUILTIN_RAFT_CONFIG, EMPTY_CONFIG)
            _write_node_config(node, DOC_KEEPER_CONFIG, content)

        if restart:
            _restart_cluster_nodes(cluster, nodes, timeout=timeout)
            _wait_cluster_healthy(cluster, nodes, timeout=timeout)

    self.context.fips_doc_keeper_installed = True
    return DOC_KEEPER_CONFIG


@TestStep(Then)
def verify_cluster_listening_ports(self, allowed_ports, nodes=None, forbid_plaintext=False):
    """Assert each node listens on the expected secure ports."""
    if nodes is None:
        nodes = KEEPER_CLUSTER_NODES

    cluster = self.context.cluster
    for name in nodes:
        verify_server_listening_ports(
            allowed_ports=allowed_ports,
            node=cluster.node(name),
            forbid_plaintext=forbid_plaintext,
        )


@TestStep(Then)
def verify_cluster_keeper_http_readiness_not_exposed(self, nodes=None):
    """Assert Keeper HTTP /ready is not exposed on any cluster node."""
    if nodes is None:
        nodes = KEEPER_CLUSTER_NODES

    cluster = self.context.cluster
    for name in nodes:
        verify_keeper_http_readiness_not_exposed(node=cluster.node(name))


@TestStep(Then)
def verify_keeper_connection(self, node=None, message="keeper"):
    """Verify ClickHouse can query embedded Keeper over secure coordination."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    node.query(
        "SELECT * FROM system.zookeeper WHERE path = '/' FORMAT JSON",
        message=message,
    )
