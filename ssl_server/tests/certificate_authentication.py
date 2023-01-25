from testflows.core import *

from ssl_server.tests.common import *
from ssl_server.tests.ssl_context import enable_ssl
from ssl_server.requirements import *


@TestScenario
def rbac_user_no_hostname(self):
    """User defined by RBAC with no hostname in the Common Name of the certificate.
    """
    node = self.context.node

    try:
        with Given("I generate client's private key and certificate signing request (CSR)"):
            node.command(f"openssl req -newkey rsa:4096 -nodes -batch -keyout client1-key.pem -out client1-req.pem -subj '/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=client1'")

        with And("I use the CA to sign the client's CSR"):
            node.command(f"openssl x509 -req -days 3650 -in client1-req.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out client1-cert.pem")

        with When("I create a user identified by the certificate"):
            node.query(
                f"CREATE USER steve IDENTIFIED WITH ssl_certificate CN 'client1'"
            )

        with Then("I login as the user using the certificate"):
            output = node.command(
                f"echo 'SELECT currentUser()' | curl https://clickhouse1:{self.context.secure_http_port} --cert client1-cert.pem --key client1-key.pem --cacert ca-cert.pem -H 'X-ClickHouse-SSL-Certificate-Auth: on' -H 'X-ClickHouse-User: steve' --data-binary @-"
            ).output
            assert output == "steve", error()

    finally:
        with Finally("I remove the certificates and keys"):
            node.command(f"rm -f client1-key.pem")
            node.command(f"rm -f client1-cert.pem")
            node.command(f"rm -f client1-req.pem")

        with And("I remove the user"):
            node.query(f"DROP USER IF EXISTS steve")


@TestScenario
def rbac_user_hostname(self):
    """User defined by RBAC with hostname in the Common Name of the certificate.
    """
    node = self.context.node

    try:
        with Given("I generate client's private key and certificate signing request (CSR)"):
            node.command(f"openssl req -newkey rsa:4096 -nodes -batch -keyout client4-key.pem -out client4-req.pem -subj '/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=clickhouse1:client4'")

        with And("I use the CA to sign the client's CSR"):
            node.command(f"openssl x509 -req -days 3650 -in client4-req.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out client4-cert.pem")

        with When("I create a user identified by the certificate"):
            node.query(
                f"CREATE USER john IDENTIFIED WITH ssl_certificate CN 'clickhouse1:client4'"
            )

        with Then("I login as the user using the certificate"):
            output = node.command(
                f"echo 'SELECT currentUser()' | curl https://clickhouse1:{self.context.secure_http_port} --cert client4-cert.pem --key client4-key.pem --cacert ca-cert.pem -H 'X-ClickHouse-SSL-Certificate-Auth: on' -H 'X-ClickHouse-User: john' --data-binary @-"
            ).output
            assert output == "john", error()

    finally:
        with Finally("I remove the certificates and keys"):
            node.command(f"rm -f client4-key.pem")
            node.command(f"rm -f client4-cert.pem")
            node.command(f"rm -f client4-req.pem")

        with And("I remove the user"):
            node.query(f"DROP USER IF EXISTS john")


@TestScenario
def config_user_no_hostname(self):
    """User defined in users.xml with no hostname in the Common Name of the certificate."""
    node = self.context.node

    try:
        with Given("I generate client's private key and certificate signing request (CSR)"):
            node.command(f"openssl req -newkey rsa:4096 -nodes -batch -keyout client2-key.pem -out client2-req.pem -subj '/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=client2'")

        with And("I use the CA to sign the client's CSR"):
            node.command(f"openssl x509 -req -days 3650 -in client2-req.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out client2-cert.pem")

        with Then("I login as the user using the certificate"):
            output = node.command(
                f"echo 'SELECT currentUser()' | curl https://clickhouse1:{self.context.secure_http_port} --cert client2-cert.pem --key client2-key.pem --cacert ca-cert.pem -H 'X-ClickHouse-SSL-Certificate-Auth: on' -H 'X-ClickHouse-User: CN_user' --data-binary @-"
            ).output
            assert output == "CN_user", error()

    finally:
        with Finally("I remove the certificates and keys"):
            node.command(f"rm -f client2-key.pem")
            node.command(f"rm -f client2-cert.pem")
            node.command(f"rm -f client2-req.pem")


@TestScenario
def config_user_hostname(self):
    """User defined in users.xml with a hostname in the Common Name of the certificate."""
    node = self.context.node

    try:
        with Given("I generate client's private key and certificate signing request (CSR)"):
            node.command(f"openssl req -newkey rsa:4096 -nodes -batch -keyout client3-key.pem -out client3-req.pem -subj '/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=clickhouse1:client3'")

        with And("I use the CA to sign the client's CSR"):
            node.command(f"openssl x509 -req -days 3650 -in client3-req.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out client3-cert.pem")

        with Then("I login as the user using the certificate"):
            output = node.command(
                f"echo 'SELECT currentUser()' | curl https://clickhouse1:{self.context.secure_http_port} --cert client3-cert.pem --key client3-key.pem --cacert ca-cert.pem -H 'X-ClickHouse-SSL-Certificate-Auth: on' -H 'X-ClickHouse-User: CN_hostname_user' --data-binary @-"
            ).output
            assert output == "CN_hostname_user", error()

    finally:
        with Finally("I remove the certificates and keys"):
            node.command(f"rm -f client3-key.pem")
            node.command(f"rm -f client3-cert.pem")
            node.command(f"rm -f client3-req.pem")


@TestFeature
@Name("certificate authentication")
@Requirements(RQ_SRS_017_ClickHouse_SSL_Server_Certificates_UserAuthentication("1.0"))
def feature(self, node="clickhouse1"):
    """Check using SSL certificate for user authentication instead of a password."""
    self.context.node = self.context.cluster.node(node)
    node = self.context.node

    with Given("I enable SSL"):
        enable_ssl(my_own_ca_key_passphrase="", server_key_passphrase="")

    with And("I set SSL server to `relaxed` verification mode"):
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

    try:
        with Given("I generate CA's private key and self-signed certificate"):
            node.command(f"openssl req -newkey rsa:4096 -x509 -days 3650 -nodes -batch -keyout ca-key.pem -out ca-cert.pem -subj '/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=ca'")

        with And("I set the caConfig"):
            entries = define(
                "SSL settings",
                {
                    "caConfig": "/ca-cert.pem",
                },
            )

        with And("I apply SSL server configuration"):
            add_ssl_server_configuration_file(
                entries=entries, config_file="ssl_caconfig_certificate_auth.xml", restart=True
            )

        Scenario(run=rbac_user_no_hostname)
        Scenario(run=rbac_user_hostname)
        Scenario(run=config_user_no_hostname)
        Scenario(run=config_user_hostname)

    finally:
        with Finally("I remove the certificates and keys"):
            node.command(f"rm -f ca-key.pem")
            node.command(f"rm -f ca-cert.pem")
