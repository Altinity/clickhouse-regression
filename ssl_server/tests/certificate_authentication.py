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
        with Given("I generate CA's private key and self-signed certificate"):
            node.command(f"openssl req -newkey rsa:4096 -x509 -days 3650 -nodes -batch -keyout ca-key.pem -out ca-cert.pem -subj '/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=ca'")

        with And("I generate server's private key and csr"):
            node.command(f"openssl req -newkey rsa:4096 -nodes -batch -keyout server-key.pem -out server-req.pem -subj '/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=server'")

        with And("I create a file with the alternate subject name"):
            node.command("echo 'subjectAltName=DNS:clickhouse1' > server-ext.cnf")

        with And("I sign the server csr with the CA"):
            node.command(f"openssl x509 -req -days 3650 -in server-req.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -extfile server-ext.cnf -out server-cert.pem")

        with And("I generate client's private key and certificate signing request (CSR)"):
            node.command(f"openssl req -newkey rsa:4096 -nodes -batch -keyout client1-key.pem -out client1-req.pem -subj '/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=client1'")

        with And("I use the CA to sign the client's CSR"):
            node.command(f"openssl x509 -req -days 3650 -in client1-req.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out client1-cert.pem")

        with Given("I add SSL server configuration file"):
            entries = {
                "certificateFile": "/server-cert.pem",
                "privateKeyFile": "/server-key.pem",
                "caConfig": "/ca-cert.pem",
                "verificationMode": "none",
            }
            add_ssl_server_configuration_file(entries=entries)

        with And("I add SSL ports configuration file"):
            add_secure_ports_configuration_file(restart=True, timeout=100)

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
            node.command(f"rm -f ca-key.pem")
            node.command(f"rm -f ca-cert.pem")
            node.command(f"rm -f server-cert.pem")
            node.command(f"rm -f server-key.pem")
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
        with Given("I generate CA's private key and self-signed certificate"):
            node.command(f"openssl req -newkey rsa:4096 -x509 -days 3650 -nodes -batch -keyout ca-key.pem -out ca-cert.pem -subj '/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=ca'")

        with And("I generate server's private key and csr"):
            node.command(f"openssl req -newkey rsa:4096 -nodes -batch -keyout server-key.pem -out server-req.pem -subj '/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=server'")

        with And("I create a file with the alternate subject name"):
            node.command("echo 'subjectAltName=DNS:clickhouse1' > server-ext.cnf")

        with And("I sign the server csr with the CA"):
            node.command(f"openssl x509 -req -days 3650 -in server-req.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -extfile server-ext.cnf -out server-cert.pem")

        with And("I generate client's private key and certificate signing request (CSR)"):
            node.command(f"openssl req -newkey rsa:4096 -nodes -batch -keyout client1-key.pem -out client1-req.pem -subj '/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=clickhouse1:client1'")

        with And("I use the CA to sign the client's CSR"):
            node.command(f"openssl x509 -req -days 3650 -in client1-req.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out client1-cert.pem")

        with Given("I add SSL server configuration file"):
            entries = {
                "certificateFile": "/server-cert.pem",
                "privateKeyFile": "/server-key.pem",
                "caConfig": "/ca-cert.pem",
                "verificationMode": "none",
            }
            add_ssl_server_configuration_file(entries=entries)

        with And("I add SSL ports configuration file"):
            add_secure_ports_configuration_file(restart=True, timeout=100)

        with When("I create a user identified by the certificate"):
            node.query(
                f"CREATE USER john IDENTIFIED WITH ssl_certificate CN 'clickhouse1:client1'"
            )

        with Then("I login as the user using the certificate"):
            output = node.command(
                f"echo 'SELECT currentUser()' | curl https://clickhouse1:{self.context.secure_http_port} --cert client1-cert.pem --key client1-key.pem --cacert ca-cert.pem -H 'X-ClickHouse-SSL-Certificate-Auth: on' -H 'X-ClickHouse-User: john' --data-binary @-"
            ).output
            assert output == "john", error()

    finally:
        with Finally("I remove the certificates and keys"):
            node.command(f"rm -f ca-key.pem")
            node.command(f"rm -f ca-cert.pem")
            node.command(f"rm -f server-cert.pem")
            node.command(f"rm -f server-key.pem")
            node.command(f"rm -f client1-key.pem")
            node.command(f"rm -f client1-cert.pem")
            node.command(f"rm -f client1-req.pem")

        with And("I remove the user"):
            node.query(f"DROP USER IF EXISTS john")


@TestScenario
def config_user_no_hostname(self):
    """User defined in users.xml with no hostname in the Common Name of the certificate."""
    node = self.context.node

    try:
        with Given("I generate CA's private key and self-signed certificate"):
            node.command(f"openssl req -newkey rsa:4096 -x509 -days 3650 -nodes -batch -keyout ca-key.pem -out ca-cert.pem -subj '/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=ca'")

        with And("I generate server's private key and csr"):
            node.command(f"openssl req -newkey rsa:4096 -nodes -batch -keyout server-key.pem -out server-req.pem -subj '/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=server'")

        with And("I create a file with the alternate subject name"):
            node.command("echo 'subjectAltName=DNS:clickhouse1' > server-ext.cnf")

        with And("I sign the server csr with the CA"):
            node.command(f"openssl x509 -req -days 3650 -in server-req.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -extfile server-ext.cnf -out server-cert.pem")

        with And("I generate client's private key and certificate signing request (CSR)"):
            node.command(f"openssl req -newkey rsa:4096 -nodes -batch -keyout client2-key.pem -out client2-req.pem -subj '/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=client2'")

        with And("I use the CA to sign the client's CSR"):
            node.command(f"openssl x509 -req -days 3650 -in client2-req.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out client2-cert.pem")

        with Given("I add SSL server configuration file"):
            entries = {
                "certificateFile": "/server-cert.pem",
                "privateKeyFile": "/server-key.pem",
                "caConfig": "/ca-cert.pem",
                "verificationMode": "none",
            }
            add_ssl_server_configuration_file(entries=entries)

        with And("I add SSL ports configuration file"):
            add_secure_ports_configuration_file(restart=True, timeout=100)

        with Then("I login as the user using the certificate"):
            output = node.command(
                f"echo 'SELECT currentUser()' | curl https://clickhouse1:{self.context.secure_http_port} --cert client2-cert.pem --key client2-key.pem --cacert ca-cert.pem -H 'X-ClickHouse-SSL-Certificate-Auth: on' -H 'X-ClickHouse-User: CN_user' --data-binary @-"
            ).output
            assert output == "CN_user", error()

    finally:
        with Finally("I remove the certificates and keys"):
            node.command(f"rm -f ca-key.pem")
            node.command(f"rm -f ca-cert.pem")
            node.command(f"rm -f server-cert.pem")
            node.command(f"rm -f server-key.pem")
            node.command(f"rm -f client2-key.pem")
            node.command(f"rm -f client2-cert.pem")
            node.command(f"rm -f client2-req.pem")


@TestScenario
def config_user_hostname(self):
    """User defined in users.xml with a hostname in the Common Name of the certificate."""
    node = self.context.node

    try:
        with Given("I generate CA's private key and self-signed certificate"):
            node.command(f"openssl req -newkey rsa:4096 -x509 -days 3650 -nodes -batch -keyout ca-key.pem -out ca-cert.pem -subj '/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=ca'")

        with And("I generate server's private key and csr"):
            node.command(f"openssl req -newkey rsa:4096 -nodes -batch -keyout server-key.pem -out server-req.pem -subj '/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=server'")

        with And("I create a file with the alternate subject name"):
            node.command("echo 'subjectAltName=DNS:clickhouse1' > server-ext.cnf")

        with And("I sign the server csr with the CA"):
            node.command(f"openssl x509 -req -days 3650 -in server-req.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -extfile server-ext.cnf -out server-cert.pem")

        with And("I generate client's private key and certificate signing request (CSR)"):
            node.command(f"openssl req -newkey rsa:4096 -nodes -batch -keyout client3-key.pem -out client3-req.pem -subj '/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=clickhouse1:client3'")

        with And("I use the CA to sign the client's CSR"):
            node.command(f"openssl x509 -req -days 3650 -in client3-req.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out client3-cert.pem")

        with Given("I add SSL server configuration file"):
            entries = {
                "certificateFile": "/server-cert.pem",
                "privateKeyFile": "/server-key.pem",
                "caConfig": "/ca-cert.pem",
                "verificationMode": "none",
            }
            add_ssl_server_configuration_file(entries=entries)

        with And("I add SSL ports configuration file"):
            add_secure_ports_configuration_file(restart=True, timeout=100)

        with Then("I login as the user using the certificate"):
            output = node.command(
                f"echo 'SELECT currentUser()' | curl https://clickhouse1:{self.context.secure_http_port} --cert client3-cert.pem --key client3-key.pem --cacert ca-cert.pem -H 'X-ClickHouse-SSL-Certificate-Auth: on' -H 'X-ClickHouse-User: CN_hostname_user' --data-binary @-"
            ).output
            assert output == "CN_hostname_user", error()

    finally:
        with Finally("I remove the certificates and keys"):
            node.command(f"rm -f ca-key.pem")
            node.command(f"rm -f ca-cert.pem")
            node.command(f"rm -f server-cert.pem")
            node.command(f"rm -f server-key.pem")
            node.command(f"rm -f client3-key.pem")
            node.command(f"rm -f client3-cert.pem")
            node.command(f"rm -f client3-req.pem")


@TestFeature
@Name("certificate authentication")
@Requirements(RQ_SRS_017_ClickHouse_SSL_Server_Certificates_UserAuthentication("1.0"))
def feature(self, node="clickhouse1"):
    """Check using SSL certificate for user authentication instead of a password."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=rbac_user_no_hostname)
    Scenario(run=rbac_user_hostname)
    Scenario(run=config_user_no_hostname)
    Scenario(run=config_user_hostname)

