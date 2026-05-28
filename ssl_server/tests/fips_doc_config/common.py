import os

from testflows.core import *

from ssl_server.tests.common import *

FIPS_DOC_FIXTURES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "configs", "fips_doc"
)
FIPS_DOC_CERT_DIR = "/etc/clickhouse-server/config.d"
FIPS_DOC_SERVER_CRT = f"{FIPS_DOC_CERT_DIR}/server.crt"
FIPS_DOC_SERVER_KEY = f"{FIPS_DOC_CERT_DIR}/server.key"
FIPS_DOC_CA_CRT = f"{FIPS_DOC_CERT_DIR}/ca.crt"
FIPS_DOC_SECURE_TCP_PORT = 9440
FIPS_DOC_SECURE_HTTP_PORT = 8443
FIPS_DOC_INTERSERVER_HTTPS_PORT = 9010
FIPS_DOC_METRICS_PATH = "/metrics_all"
FIPS_DOC_KEEPER_CLIENT_PORT = 2281
FIPS_DOC_KEEPER_RAFT_PORT = 9444
FIPS_DOC_KEEPER_HTTP_CONTROL_PORT = 9182
FIPS_DOC_KEEPER_READINESS_PATH = "/ready"

DOC_FORBIDDEN_PLAINTEXT_PORTS = frozenset({9000, 8123})
DOC_EPHEMERAL_PORT_THRESHOLD = 32768
DOC_SERVER_PORTS = frozenset(
    {
        FIPS_DOC_SECURE_TCP_PORT,
        FIPS_DOC_SECURE_HTTP_PORT,
        FIPS_DOC_INTERSERVER_HTTPS_PORT,
    }
)
BUILTIN_ZOOKEEPER_CONFIG = "/etc/clickhouse-server/config.d/zookeeper.xml"
FIPS_DOC_SERVER_FIXTURE = "server/fips.xml"
FIPS_DOC_CLIENT_FIXTURE = "client/fips.xml"
FIPS_DOC_BYOC_METRICS_SIM_FIXTURE = "test/byoc_metrics_simulation.xml"
FIPS_DOC_BYOC_METRICS_SIM_DEST = (
    "/etc/clickhouse-server/config.d/byoc_metrics_simulation.xml"
)
REGRESSION_CONFIG_DIR = os.path.normpath(
    os.path.join(FIPS_DOC_FIXTURES_DIR, "..", "clickhouse")
)
STOCK_FIPS_CONFIG_DIR = os.path.normpath(os.path.join(FIPS_DOC_FIXTURES_DIR, "stock"))
EMPTY_CLICKHOUSE_CONFIG = "<clickhouse>\n</clickhouse>\n"
MOUNTED_SERVER_CONFIG_FILES = (
    ("/etc/clickhouse-server/config.xml", "config.xml", REGRESSION_CONFIG_DIR),
    ("/etc/clickhouse-server/users.xml", "users.xml", REGRESSION_CONFIG_DIR),
    (
        "/etc/clickhouse-server/config.d/logs.xml",
        "logs.xml",
        os.path.join(REGRESSION_CONFIG_DIR, "config.d"),
    ),
    (
        "/etc/clickhouse-server/config.d/remote.xml",
        "remote.xml",
        os.path.join(REGRESSION_CONFIG_DIR, "config.d"),
    ),
    (
        "/etc/clickhouse-server/config.d/zookeeper.xml",
        "zookeeper.xml",
        os.path.join(REGRESSION_CONFIG_DIR, "config.d"),
    ),
)


def fips_doc_fixture_path(relative_path):
    return os.path.normpath(os.path.join(FIPS_DOC_FIXTURES_DIR, relative_path))


def read_fips_doc_fixture(relative_path):
    with open(fips_doc_fixture_path(relative_path), encoding="utf-8") as fixture_file:
        return fixture_file.read()


def read_local_config_file(base_dir, filename):
    path = os.path.join(base_dir, filename)
    with open(path, encoding="utf-8") as config_file:
        return config_file.read()


def write_node_config(node, dest, content):
    node.command(
        f"cat <<'FIPS_DOC_CONFIG' > {dest}\n{content}\nFIPS_DOC_CONFIG",
        exitcode=0,
    )


def snapshot_regression_server_configs(context):
    """Capture bind-mounted regression configs before overwriting them in-container.

    Container paths are bind-mounted to ssl_server/configs/clickhouse/ on the host,
    so writes through the node mutate the repo files. Restore must use this snapshot,
    not re-read from disk after the swap.
    """
    backup = getattr(context, "fips_doc_regression_config_backup", None)
    if backup:
        return backup

    backup = {}
    for dest, filename, base_dir in MOUNTED_SERVER_CONFIG_FILES:
        backup[dest] = read_local_config_file(base_dir, filename)

    context.fips_doc_regression_config_backup = backup
    return backup


@TestStep(Given)
def use_stock_fips_server_config(self, node=None, timeout=300):
    """Use stock Altinity FIPS image configs instead of regression overrides.

    Regression bind-mounts a trimmed config.xml (no mysql/postgresql ports) and
    test-only drop-ins. Doc-config tests must layer fips.xml on the same base
    config as production deployments.

    Regression-only drop-ins (logs, remote, zookeeper) are cleared because the
    stock image does not ship them; this happens only inside the container via
    bind mounts and must be restored before other ssl_server tests run.
    """
    if node is None:
        node = self.context.node

    with When("I switch to the stock Altinity FIPS server configuration"):
        snapshot_regression_server_configs(self.context)
        node.stop_clickhouse(timeout=timeout, safe=False)
        write_node_config(
            node,
            "/etc/clickhouse-server/config.xml",
            read_local_config_file(STOCK_FIPS_CONFIG_DIR, "config.xml"),
        )
        write_node_config(
            node,
            "/etc/clickhouse-server/users.xml",
            read_local_config_file(STOCK_FIPS_CONFIG_DIR, "users.xml"),
        )
        for dest, _, _ in MOUNTED_SERVER_CONFIG_FILES[2:]:
            write_node_config(node, dest, EMPTY_CLICKHOUSE_CONFIG)
        node.start_clickhouse(timeout=timeout, wait_healthy=True)

    self.context.fips_doc_stock_config_applied = True


@TestStep(Finally)
def restore_regression_server_config(self, node=None, timeout=300):
    """Restore regression bind-mounted configs after doc fixture tests."""
    if not getattr(self.context, "fips_doc_stock_config_applied", False):
        return
    if node is None:
        node = self.context.node

    backup = getattr(self.context, "fips_doc_regression_config_backup", None)
    if not backup:
        raise RuntimeError(
            "regression config snapshot missing; bind-mounted configs may be corrupted"
        )

    with By("I restore regression server configuration"):
        node.stop_clickhouse(timeout=timeout, safe=False)
        for dest, content in backup.items():
            write_node_config(node, dest, content)
        node.start_clickhouse(timeout=timeout, wait_healthy=True)

    self.context.fips_doc_stock_config_applied = False
    self.context.fips_doc_regression_config_backup = None


def strip_zookeeper_section(content):
    """Remove embedded zookeeper block when testing server-only doc config."""
    start = content.find("<zookeeper>")
    if start == -1:
        return content

    end = content.find("</zookeeper>", start)
    if end == -1:
        return content

    end += len("</zookeeper>")
    return content[:start] + content[end:]


@TestStep(Given)
def setup_fips_doc_certificates(self, node=None):
    """Generate a lab CA and server cert at standardized config.d paths."""
    if node is None:
        node = self.context.node

    my_own_ca_key = "fips_doc_ca.key"
    my_own_ca_crt = "fips_doc_ca.crt"
    server_key = "fips_doc_server.key"
    server_csr = "fips_doc_server.csr"
    server_crt = "fips_doc_server.crt"

    ca_key = create_rsa_private_key(outfile=my_own_ca_key, passphrase="")
    ca_crt = create_ca_certificate(
        outfile=my_own_ca_crt,
        key=ca_key,
        passphrase="",
        common_name="fips-doc-ca",
    )
    key = create_rsa_private_key(outfile=server_key, passphrase="")
    csr = create_certificate_signing_request(
        outfile=server_csr,
        common_name=node.name,
        key=key,
        passphrase="",
    )
    crt = sign_certificate(
        outfile=server_crt,
        csr=csr,
        ca_certificate=ca_crt,
        ca_key=ca_key,
        ca_passphrase="",
    )

    node.command(f"mkdir -p {FIPS_DOC_CERT_DIR}", exitcode=0)
    copy(dest_node=node, src_path=crt, dest_path=FIPS_DOC_SERVER_CRT)
    copy(dest_node=node, src_path=key, dest_path=FIPS_DOC_SERVER_KEY)
    copy(dest_node=node, src_path=ca_crt, dest_path=FIPS_DOC_CA_CRT)
    node.command(f'chmod 600 "{FIPS_DOC_SERVER_KEY}"', exitcode=0)
    add_trusted_ca_certificate(node=node, certificate=ca_crt)

    self.context.fips_doc_ca_crt = FIPS_DOC_CA_CRT
    self.context.fips_doc_server_crt = FIPS_DOC_SERVER_CRT
    self.context.fips_doc_server_key = FIPS_DOC_SERVER_KEY


def get_server_listening_ports_ss(node):
    """Return ss output and parsed ports for the ClickHouse server pid."""
    pid = node.clickhouse_pid()
    if not pid:
        return "", set(), "clickhouse server pid not found"

    ss_check = node.command("command -v ss", no_checks=True)
    if ss_check.exitcode != 0:
        node.command(
            "apt-get update -qq && apt-get install -y -qq iproute2",
            no_checks=True,
        )
        ss_check = node.command("command -v ss", no_checks=True)
        if ss_check.exitcode != 0:
            return "", set(), "ss is not available"

    output = node.command(
        f'ss -ltnp | grep "pid={pid},"',
        no_checks=True,
    ).output

    ports = set()
    for line in output.splitlines():
        parts = line.split()
        if len(parts) < 4 or parts[0] != "LISTEN":
            continue
        local = parts[3]
        if ":" not in local:
            continue
        port_text = local.rsplit(":", 1)[-1]
        if port_text.isdigit():
            ports.add(int(port_text))

    return output.strip(), ports, None


def get_server_listening_ports(node):
    """Return TCP ports in LISTEN state for the ClickHouse server process."""
    pid = node.clickhouse_pid()
    assert pid, error("clickhouse server pid not found")

    output = node.command(
        f"for proc_net in /proc/{pid}/net/tcp /proc/{pid}/net/tcp6; do "
        f'  [ -r "$proc_net" ] || continue; '
        f"  while read -r _ local _ state _; do "
        f'    [ "$state" = 0A ] || continue; '
        f'    port=$((16#${{local##*:}})); '
        f'    echo "$port"; '
        f'  done < "$proc_net"; '
        f"done | sort -un",
        no_checks=True,
    ).output

    return {int(port) for port in output.split() if port.strip().isdigit()}


@TestStep(Given)
def restart_fips_doc_server(self, node=None, timeout=300):
    """Restart ClickHouse after doc fixtures that disable plaintext ports."""
    if node is None:
        node = self.context.node

    with When("I restart ClickHouse with the doc fixture active"):
        node.stop_clickhouse(timeout=timeout, safe=False)
        node.start_clickhouse(timeout=timeout, wait_healthy=False)

    with Then("ClickHouse should be healthy on the secure port"):
        retry(node.command, timeout=timeout, delay=10)(
            f'clickhouse client --secure --host 127.0.0.1 --port {FIPS_DOC_SECURE_TCP_PORT} -q "SELECT 1"',
            message="1",
            exitcode=0,
        )


@TestStep(Given)
def disable_bundled_zookeeper_config(self, node=None):
    """Move bundled zookeeper.xml aside so doc fips.xml zookeeper section applies."""
    if node is None:
        node = self.context.node

    backup = f"{BUILTIN_ZOOKEEPER_CONFIG}.bak"
    node.command(
        f"test -f '{BUILTIN_ZOOKEEPER_CONFIG}' && mv '{BUILTIN_ZOOKEEPER_CONFIG}' '{backup}' || true",
        exitcode=0,
    )
    self.context.fips_doc_zookeeper_config_backup = backup


@TestStep(Finally)
def restore_bundled_zookeeper_config(self, node=None):
    """Restore bundled zookeeper.xml after doc fixture tests."""
    if node is None:
        node = self.context.node

    backup = getattr(self.context, "fips_doc_zookeeper_config_backup", None)
    if not backup:
        return

    with By("I restore bundled zookeeper config"):
        node.command(
            f"test -f '{backup}' && mv '{backup}' '{BUILTIN_ZOOKEEPER_CONFIG}' || true",
            no_checks=True,
        )

    self.context.fips_doc_zookeeper_config_backup = None


@TestStep(Given)
def apply_fips_doc_server_fixtures(
    self,
    fixtures=None,
    restart=True,
    node=None,
    timeout=300,
    disable_bundled_zookeeper=None,
    include_zookeeper=False,
):
    """Install doc server fips.xml, optionally restarting once at the end."""
    if node is None:
        node = self.context.node
    if disable_bundled_zookeeper is None:
        disable_bundled_zookeeper = include_zookeeper
    if fixtures is None:
        fixtures = [FIPS_DOC_SERVER_FIXTURE]
    elif isinstance(fixtures, str):
        fixtures = [fixtures]

    installed = getattr(self.context, "fips_doc_installed_server_fixtures", [])
    if installed is None:
        installed = []

    with When("I install doc server fixture files"):
        if disable_bundled_zookeeper:
            disable_bundled_zookeeper_config(node=node)

        node.command("mkdir -p /etc/clickhouse-server/config.d", exitcode=0)
        for fixture in fixtures:
            dest_name = os.path.basename(fixture)
            dest = f"/etc/clickhouse-server/config.d/{dest_name}"
            source = fips_doc_fixture_path(fixture)
            content = read_fips_doc_fixture(fixture)
            if not include_zookeeper:
                content = strip_zookeeper_section(content)
            node.command(
                f"cat <<'FIPS_DOC_FIXTURE' > {dest}\n{content}\nFIPS_DOC_FIXTURE",
                exitcode=0,
            )
            if dest not in installed:
                installed.append(dest)

        if restart:
            restart_fips_doc_server(node=node, timeout=timeout)

    self.context.fips_doc_installed_server_fixtures = installed
    return installed


@TestStep(Finally)
def remove_fips_doc_server_fixtures(self, node=None, timeout=300, restart=True):
    """Remove server fixtures installed by apply_fips_doc_server_fixtures."""
    if node is None:
        node = self.context.node

    installed = getattr(self.context, "fips_doc_installed_server_fixtures", []) or []
    if not installed:
        return

    with By("I remove doc server fixture files"):
        for dest in installed:
            node.command(f"rm -f {dest}", no_checks=True)

        if restart:
            node.stop_clickhouse(timeout=timeout, safe=False)
            node.start_clickhouse(timeout=timeout, wait_healthy=True)

    restore_bundled_zookeeper_config(node=node)

    self.context.fips_doc_installed_server_fixtures = []


@TestStep(Given)
def apply_byoc_metrics_simulation(self, node=None, restart=True, timeout=300):
    """Install test-only config that simulates BYOC /metrics_all on HTTPS."""
    if node is None:
        node = self.context.node

    content = read_fips_doc_fixture(FIPS_DOC_BYOC_METRICS_SIM_FIXTURE)
    with When("I apply the BYOC metrics simulation fixture"):
        node.command(
            f"cat <<'BYOC_METRICS_SIM' > {FIPS_DOC_BYOC_METRICS_SIM_DEST}\n"
            f"{content}\n"
            f"BYOC_METRICS_SIM",
            exitcode=0,
        )
        if restart:
            restart_fips_doc_server(node=node, timeout=timeout)

    self.context.fips_doc_byoc_metrics_sim_applied = True


@TestStep(Finally)
def remove_byoc_metrics_simulation(self, node=None, restart=True, timeout=300):
    """Remove test-only BYOC metrics simulation if it was applied."""
    if node is None:
        node = self.context.node

    if not getattr(self.context, "fips_doc_byoc_metrics_sim_applied", False):
        return

    with By("I remove the BYOC metrics simulation fixture"):
        node.command(f"rm -f {FIPS_DOC_BYOC_METRICS_SIM_DEST}", no_checks=True)
        if restart:
            node.stop_clickhouse(timeout=timeout, safe=False)
            node.start_clickhouse(timeout=timeout, wait_healthy=True)

    self.context.fips_doc_byoc_metrics_sim_applied = False


@TestStep(Given)
def apply_fips_doc_client_fixture(
    self,
    fixture=None,
    dest_name="fips.xml",
    node=None,
):
    """Install a clickhouse-client fixture from configs/fips_doc onto the node."""
    if node is None:
        node = self.context.node
    if fixture is None:
        fixture = FIPS_DOC_CLIENT_FIXTURE

    source = fips_doc_fixture_path(fixture)
    dest = f"/etc/clickhouse-client/config.d/{dest_name}"

    with open(source, encoding="utf-8") as fixture_file:
        content = fixture_file.read()

    with When(f"I install client {dest_name} from the doc fixture"):
        node.command("mkdir -p /etc/clickhouse-client/config.d", exitcode=0)
        node.command(
            f"cat <<'FIPS_DOC_FIXTURE' > {dest}\n{content}\nFIPS_DOC_FIXTURE",
            exitcode=0,
        )

    self.context.fips_doc_installed_client_fixture = dest
    return dest


@TestStep(Finally)
def remove_fips_doc_client_fixture(self, node=None):
    """Remove client fixture installed by apply_fips_doc_client_fixture."""
    if node is None:
        node = self.context.node

    dest = getattr(self.context, "fips_doc_installed_client_fixture", None)
    if not dest:
        return

    with By(f"I remove client fixture {dest}"):
        node.command(f"rm -f {dest}", no_checks=True)

    self.context.fips_doc_installed_client_fixture = None


@TestStep(Then)
def verify_doc_fixture_installed(
    self,
    marker,
    fixture_path="/etc/clickhouse-server/config.d/fips.xml",
    node=None,
):
    """Confirm a fixture fragment is present in the installed drop-in file."""
    if node is None:
        node = self.context.node

    output = node.command(
        f"grep --color=never '{marker}' {fixture_path}",
        exitcode=0,
    ).output.strip()
    assert output, error(f"{marker} not found in {fixture_path}")


@TestStep(Then)
def verify_doc_fixture_preprocessed(self, marker, node=None):
    """Confirm a fixture fragment landed in preprocessed config."""
    if node is None:
        node = self.context.node

    preprocessed = "/var/lib/clickhouse/preprocessed_configs/config.xml"
    output = node.command(
        f"grep --color=never '{marker}' {preprocessed}",
        no_checks=True,
    ).output.strip()
    assert output, error(f"{marker} not found in {preprocessed}")


@TestStep(Then)
def verify_secure_native_tcp(self, port=FIPS_DOC_SECURE_TCP_PORT, node=None):
    """Verify clickhouse-client can query over secure native TCP."""
    if node is None:
        node = self.context.node

    self.context.secure_tcp_port = port
    result = node.command(
        f'clickhouse client --secure --host 127.0.0.1 --port {port} -q "SELECT 1 FORMAT TabSeparated"',
        exitcode=0,
    )
    assert result.output.strip() == "1", error(result.output)


@TestStep(Then)
def verify_secure_https(self, port=FIPS_DOC_SECURE_HTTP_PORT, node=None):
    """Verify HTTPS accepts a query when the fixture exposes https_port."""
    if node is None:
        node = self.context.node

    self.context.secure_http_port = port
    curl_client_connection(
        port=port,
        hostname="127.0.0.1",
        options='--data-binary "SELECT 1"',
        message="1",
    )


@TestStep(Then)
def verify_https_metrics_endpoint(
    self,
    path=FIPS_DOC_METRICS_PATH,
    port=FIPS_DOC_SECURE_HTTP_PORT,
    user="default",
    password="",
    node=None,
):
    """Verify BYOC-style HTTPS metrics scraping on port 8443.

    Applies a test-only simulation fixture first (BYOC provides /metrics_all
    on HTTPS without fips.xml changes), then GETs the endpoint with ClickHouse
    credentials and checks for a non-empty response.
    """
    if node is None:
        node = self.context.node

    apply_byoc_metrics_simulation(node=node)

    result = node.command(
        f'curl --insecure --silent --show-error --fail '
        f'--user "{user}:{password}" '
        f'"https://127.0.0.1:{port}{path}"',
        exitcode=0,
    )
    output = result.output.strip()
    assert output, error(f"{path} returned an empty response")


@TestStep(Then)
def verify_server_listening_ports(self, allowed_ports, node=None, forbid_plaintext=True):
    """Assert the server pid listens only on the configured ports."""
    if node is None:
        node = self.context.node

    if isinstance(allowed_ports, (list, tuple)):
        allowed_ports = frozenset(allowed_ports)

    ss_output, ss_ports, ss_error = get_server_listening_ports_ss(node)
    listening_ports = get_server_listening_ports(node)

    assert not ss_error, error(f"ss port probe failed: {ss_error}")
    note(f"ss -ltnp | grep pid={node.clickhouse_pid()}:\n{ss_output or '(no listeners matched)'}")
    if ss_ports != listening_ports:
        note(
            f"ss ports {sorted(ss_ports)} differ from /proc ports {sorted(listening_ports)}"
        )

    missing_ports = set(allowed_ports) - listening_ports
    assert not missing_ports, error(
        f"expected listening ports {sorted(allowed_ports)}, "
        f"missing {sorted(missing_ports)}, got {sorted(listening_ports)}"
    )

    if forbid_plaintext:
        forbidden_plaintext = listening_ports & DOC_FORBIDDEN_PLAINTEXT_PORTS
        assert not forbidden_plaintext, error(
            f"plaintext ports still listening: {sorted(forbidden_plaintext)}"
        )

    unexpected_ports = listening_ports - set(allowed_ports)
    unexpected_service_ports = {
        port
        for port in unexpected_ports
        if port < DOC_EPHEMERAL_PORT_THRESHOLD
    }
    assert not unexpected_service_ports, error(
        f"unexpected non-ephemeral listening ports {sorted(unexpected_service_ports)}, "
        f"allowed {sorted(allowed_ports)}, got {sorted(listening_ports)}"
    )


@TestStep(Then)
def verify_keeper_http_readiness_not_exposed(
    self,
    port=FIPS_DOC_KEEPER_HTTP_CONTROL_PORT,
    path=FIPS_DOC_KEEPER_READINESS_PATH,
    node=None,
):
    """Keeper HTTP /ready control must stay off unless http_control is configured.

    See https://clickhouse.com/docs/guides/sre/keeper/clickhouse-keeper#http-control
    """
    if node is None:
        node = self.context.node

    listening_ports = get_server_listening_ports(node)
    assert port not in listening_ports, error(
        f"keeper http_control port {port} must not listen without explicit config, "
        f"got {sorted(listening_ports)}"
    )

    preprocessed = "/var/lib/clickhouse/preprocessed_configs/config.xml"
    http_control = node.command(
        f"grep --color=never 'http_control' {preprocessed}",
        no_checks=True,
    ).output.strip()
    assert not http_control, error(
        f"keeper http_control must not be present in preprocessed config: "
        f"{http_control}"
    )

    curl_result = node.command(
        f'curl --silent --show-error --fail --connect-timeout 2 '
        f'"http://127.0.0.1:{port}{path}"',
        no_checks=True,
    )
    assert curl_result.exitcode != 0, error(
        f"GET http://127.0.0.1:{port}{path} should be unreachable without "
        f"http_control config, got exitcode {curl_result.exitcode}: "
        f"{curl_result.output}"
    )
