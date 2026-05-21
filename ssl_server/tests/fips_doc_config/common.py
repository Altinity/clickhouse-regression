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

    installed = []

    try:
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
                installed.append(dest)

            if restart:
                node.restart_clickhouse(timeout=timeout)

        yield installed
    finally:
        with Finally("I remove doc server fixture files"):
            for dest in installed:
                node.command(f"rm -f {dest}", no_checks=True)
            if restart and installed:
                node.restart_clickhouse(timeout=timeout)


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

    try:
        with When(f"I install client {dest_name} from the doc fixture"):
            node.command("mkdir -p /etc/clickhouse-client/config.d", exitcode=0)
            node.command(
                f"cat <<'FIPS_DOC_FIXTURE' > {dest}\n{content}\nFIPS_DOC_FIXTURE",
                exitcode=0,
            )

        yield dest
    finally:
        with Finally(f"I remove client {dest_name}"):
            node.command(f"rm -f {dest}", no_checks=True)


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
    result = node.query("SELECT 1 FORMAT TabSeparated", secure=True)
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
