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

DOC_FORBIDDEN_PLAINTEXT_PORTS = frozenset({9000, 8123})
DOC_EPHEMERAL_PORT_THRESHOLD = 32768
DOC_SERVER_MINIMAL_PORTS = frozenset({FIPS_DOC_SECURE_TCP_PORT})
DOC_SERVER_FULL_PORTS = frozenset(
    {
        FIPS_DOC_SECURE_TCP_PORT,
        FIPS_DOC_SECURE_HTTP_PORT,
        FIPS_DOC_INTERSERVER_HTTPS_PORT,
    }
)


def fips_doc_fixture_path(relative_path):
    return os.path.normpath(os.path.join(FIPS_DOC_FIXTURES_DIR, relative_path))


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
def apply_fips_doc_server_fixtures(
    self,
    fixtures,
    restart=True,
    node=None,
    timeout=300,
):
    """Install one or more server fixtures, optionally restarting once at the end."""
    if node is None:
        node = self.context.node
    if isinstance(fixtures, str):
        fixtures = [fixtures]

    installed = getattr(self.context, "fips_doc_installed_server_fixtures", [])
    if installed is None:
        installed = []

    with When("I install doc server fixture files"):
        node.command("mkdir -p /etc/clickhouse-server/config.d", exitcode=0)
        for fixture in fixtures:
            dest_name = os.path.basename(fixture)
            dest = f"/etc/clickhouse-server/config.d/{dest_name}"
            source = fips_doc_fixture_path(fixture)
            with open(source, encoding="utf-8") as fixture_file:
                content = fixture_file.read()
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

    self.context.fips_doc_installed_server_fixtures = []


@TestStep(Given)
def apply_fips_doc_client_fixture(
    self,
    fixture,
    dest_name="fips.xml",
    node=None,
):
    """Install a clickhouse-client fixture from configs/fips_doc onto the node."""
    if node is None:
        node = self.context.node

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
def verify_server_listening_ports(self, allowed_ports, node=None):
    """Assert the server pid listens only on the configured ports."""
    if node is None:
        node = self.context.node

    if isinstance(allowed_ports, (list, tuple)):
        allowed_ports = frozenset(allowed_ports)

    listening_ports = get_server_listening_ports(node)
    missing_ports = set(allowed_ports) - listening_ports
    assert not missing_ports, error(
        f"expected listening ports {sorted(allowed_ports)}, "
        f"missing {sorted(missing_ports)}, got {sorted(listening_ports)}"
    )

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
