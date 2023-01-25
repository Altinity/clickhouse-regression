from testflows.core import *

from ssl_server.tests.common import *
from ssl_server.tests.ssl_context import enable_ssl
from ssl_server.requirements import *


@TestOutline
@Name("check connections")
def check_connections(
    self, openssl_options="", curl_options="", clickhouse_client_options=None
):
    """Check connections to the clickhouse-server using openssl s_client https and tcp, curl, and clickhouse-client."""

    with Then("I connect to clickhouse-server using openssl s_client http"):
        openssl_client_connection(
            port=self.context.secure_http_port, options=openssl_options
        )

    with And("I connect to clickhouse-server using openssl s_client tcp"):
        openssl_client_connection(
            port=self.context.secure_tcp_port, options=openssl_options
        )

    with And("I connect to clickhouse-server using clickhouse-client tcp"):
        clickhouse_client_connection(
            port=self.context.secure_tcp_port, options=clickhouse_client_options
        )

    with And("I connect to clickhouse-server using curl tcp"):
        curl_client_connection(port=self.context.secure_http_port, options=curl_options)


@TestFeature
@Name("none")
@Requirements(
    RQ_SRS_017_ClickHouse_SSL_Server_Certificates_VerificationMode_None("1.0")
)
def none(self):
    """Check connections to the clickhouse-server with `none` verification mode."""
    with Given("I set SSL server to `none` verification mode"):
        clickhouse_server_verification_mode(mode="none")

    Scenario("check connections", run=check_connections)


@TestSuite
@Name("once")
@Requirements(
    RQ_SRS_017_ClickHouse_SSL_Server_Certificates_VerificationMode_Once("1.0")
)
def once(self):
    """Check connections to the clickhouse-server with `once` verification mode."""
    with Given("I set SSL server to `once` verification mode"):
        clickhouse_server_verification_mode(mode="once")

    Scenario("check connections", run=check_connections)
    Scenario(
        "check connections with client certificate and key specified",
        test=check_connections,
    )(
        openssl_options="-cert /client.crt -key /client.key",
        curl_options="--cert /client.crt --key /client.key",
        clickhouse_client_options=self.context.clickhouse_client_entries,
    )


@TestSuite
@Name("relaxed")
@Requirements(
    RQ_SRS_017_ClickHouse_SSL_Server_Certificates_VerificationMode_Relaxed("1.0")
)
def relaxed(self):
    """Check connections to the clickhouse-server with `relaxed` verification mode."""
    with Given("I set SSL server to `relaxed` verification mode"):
        clickhouse_server_verification_mode(mode="relaxed")

    Scenario("check connections", run=check_connections)
    Scenario(
        "check connections with client certificate and key specified",
        test=check_connections,
    )(
        openssl_options="-cert /client.crt -key /client.key",
        curl_options="--cert /client.crt --key /client.key",
        clickhouse_client_options=self.context.clickhouse_client_entries,
    )


@TestSuite
@Name("strict")
@Requirements(
    RQ_SRS_017_ClickHouse_SSL_Server_Certificates_VerificationMode_Strict("1.0")
)
def strict(self):
    """Check connections to the clickhouse-server with `strict` verification mode."""
    with Given("I set SSL server to `strict` verification mode"):
        clickhouse_server_verification_mode(mode="strict")

    Scenario(
        "check connections with client certificate and key specified",
        test=check_connections,
    )(
        openssl_options="-cert /client.crt -key /client.key",
        curl_options="--cert /client.crt --key /client.key",
        clickhouse_client_options=self.context.clickhouse_client_entries,
    )


@TestFeature
@Name("verification modes")
@Requirements(RQ_SRS_017_ClickHouse_SSL_Server_Certificates_VerificationMode("1.0"))
def feature(self, node="clickhouse1"):
    """Check SSL connection to the clickhouse server with different verification modes."""
    self.context.node = self.context.cluster.node(node)

    with Given("I enable SSL"):
        enable_ssl(my_own_ca_key_passphrase="", server_key_passphrase="")

    with And("I generate client key"):
        client_key = create_rsa_private_key(outfile="client.key", passphrase="")

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
        validate_certificate(
            certificate=client_crt, ca_certificate=current().context.my_own_ca_crt
        )

    with And("I copy client certificate and key", description=f"{self.context.node}"):
        copy(dest_node=self.context.node, src_path=client_crt, dest_path="/client.crt")
        copy(dest_node=self.context.node, src_path=client_key, dest_path="/client.key")

    with And("I create the clickhouse-client config entries"):
        self.context.clickhouse_client_entries = {
            "certificateFile": "/client.crt",
            "privateKeyFile": "/client.key",
        }

    Suite(run=none)
    Suite(run=once)
    Suite(run=relaxed)
    Suite(run=strict)
    with Suite("fail cases"):
        xfail("not implemented.")
