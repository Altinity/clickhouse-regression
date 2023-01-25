from testflows.core import *

from ssl_server.tests.common import *
from ssl_server.tests.ssl_context import enable_ssl
from ssl_server.requirements import *


@TestOutline
def server_connection_openssl_client(self, port, options=None):
    """Check that server accepts only FIPS compatible secure connections on a given port
    using openssl s_client utility."""
    self.context.connection_port = port
    options = options or ""

    openssl_client_connection(
        options=options,
        success=True
    )


@TestOutline
def tcp_connection_clickhouse_client(
    self, hostname="clickhouse1", port=None, options=None
):
    """Check that server accepts only FIPS compatible TCP connections using clickhouse-client"""
    if port is None:
        port = self.context.secure_tcp_port

    self.context.connection_port = port

    clickhouse_client_connection(
        options=options,
        success=True,
        hostname=hostname,
    )


@TestOutline
def server_https_connection_curl(self, port=None, options=None):
    """Check that server accepts only FIPS compatible HTTPS connections using curl."""
    options= options or ""
    if port is None:
        port = self.context.secure_http_port
    self.context.connection_port = port

    curl_client_connection(
        options=options,
        success=True,
    )

@TestFeature
@Name("tcp connection")
@Requirements()
def server_tcp_connection(self, ssl_options=None, clickhouse_client_options=None):
    """Check that server accepts only FIPS compatible secure TCP connections."""
    Scenario(name="openssl s_client", test=server_connection_openssl_client)(
        port=self.context.secure_tcp_port,
        options=ssl_options
    )

    Scenario(name="clickhouse client", test=tcp_connection_clickhouse_client)(
        port=self.context.secure_tcp_port,
        options=clickhouse_client_options
    )


@TestFeature
@Name("https connection")
@Requirements()
def server_https_connection(self, ssl_options=None, curl_options=None):
    """Check that server accepts only FIPS compatible HTTPS connections."""
    Scenario("openssl s_client", test=server_connection_openssl_client)(
        port=self.context.secure_http_port, options=ssl_options
    )

    Scenario("curl", test=server_https_connection_curl)(
        options=curl_options
    )


@TestFeature
@Name("none")
@Requirements(
    RQ_SRS_017_ClickHouse_SSL_Server_Certificates_VerificationMode_None("1.0")
)
def none(self):

    with Given("I set SSL server to `none` verification mode"):
        entries = define(
            "SSL settings",
            {
                "verificationMode": "none",
            },
        )

    with And("I apply SSL server configuration"):
        add_ssl_server_configuration_file(
            entries=entries, config_file="ssl_verification_mode.xml", restart=True
        )

    Feature(run=server_tcp_connection)
    Feature(run=server_https_connection)


@TestFeature
@Name("once")
@Requirements(
    RQ_SRS_017_ClickHouse_SSL_Server_Certificates_VerificationMode_Once("1.0")
)
def once(self):
    with Given("I set SSL server to `once` verification mode"):
        entries = define(
            "SSL settings",
            {
                "verificationMode": "once",
            },
        )

    with And("I apply SSL server configuration"):
        add_ssl_server_configuration_file(
            entries=entries, config_file="ssl_verification_mode.xml", restart=True
        )

    Feature(run=server_tcp_connection)
    Feature(run=server_https_connection)


@TestFeature
@Name("relaxed")
@Requirements(
    RQ_SRS_017_ClickHouse_SSL_Server_Certificates_VerificationMode_Relaxed("1.0")
)
def relaxed(self):
    with Given("I set SSL server to `relaxed verification mode"):
        entries = define(
            "SSL settings",
            {
                "verificationMode": "relaxed",
            },
        )

    with And("I apply SSL server configuration"):
        add_ssl_server_configuration_file(
            entries=entries, config_file="ssl_verification_mode.xml", restart=True
        )

    Feature(run=server_tcp_connection)
    Feature(run=server_https_connection)


@TestFeature
@Name("strict")
@Requirements(
    RQ_SRS_017_ClickHouse_SSL_Server_Certificates_VerificationMode_Strict("1.0")
)
def strict(self):
    node = self.context.node
    with Given("I set SSL server to `strict` verification mode"):
        entries = define(
            "SSL settings",
            {
                "verificationMode": "strict",
            },
        )

    with And("I apply SSL server configuration"):
        add_ssl_server_configuration_file(
            entries=entries, config_file="ssl_verification_mode.xml", restart=True
        )

    with And("I generate client key"):
        client_key = create_rsa_private_key(
            outfile="client.key", passphrase=""
        )

    with And("I generate client certificate signing request"):
        client_csr = create_certificate_signing_request(
            outfile="client.csr",
            common_name="",
            key=client_key,
            passphrase="",
        )

    with And("I sign client certificate with my own CA"):
        client_crt = sign_certificate(
            outfile="client.crt",
            csr=client_csr,
            ca_certificate=current().context.my_own_ca_crt,
            ca_key=current().context.my_own_ca_key,
            ca_passphrase="",
        )

    with And("I validate client certificate"):
        validate_certificate(certificate=client_crt, ca_certificate=current().context.my_own_ca_crt)

    with And("I copy client certificate and key", description=f"{node}"):
        copy(dest_node=node, src_path=client_crt, dest_path="/client.crt")
        copy(dest_node=node, src_path=client_key, dest_path="/client.key")

    with And("I create the clickhouse-client config entries"):
        entries = {
            "certificateFile": "/client.crt",
            "privateKeyFile": "/client.key",
        }

    Feature(test=server_tcp_connection)(
        ssl_options="-cert client.crt -key client.key",
        clickhouse_client_options=entries
    )
    Feature(test=server_https_connection)(
        ssl_options="-cert /client.crt -key /client.key",
        curl_options="--cert /client.crt --key /client.key"
    )


@TestFeature
@Name("verification modes")
@Requirements(RQ_SRS_017_ClickHouse_SSL_Server_Certificates_VerificationMode("1.0"))
def feature(self, node="clickhouse1"):
    """Check SSL connection to the clickhouse server with different verification modes."""
    self.context.node = self.context.cluster.node(node)

    with Given("I enable SSL"):
        enable_ssl(my_own_ca_key_passphrase="", server_key_passphrase="")

    Feature(run=none)
    Feature(run=once)
    Feature(run=relaxed)
    Feature(run=strict)
