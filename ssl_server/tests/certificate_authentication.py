from testflows.core import *

from ssl_server.tests.common import *
from ssl_server.tests.ssl_context import enable_ssl
from ssl_server.requirements import *


@TestFeature
@Name("certificate authentication")
@Requirements(RQ_SRS_017_ClickHouse_SSL_Server_Certificates_UserAuthentication("1.0"))
def feature(self, node="clickhouse1"):
    """Check using SSL certificate for user authentication instead of a password."""
    self.context.node = self.context.cluster.node(node)
    node = self.context.node
    user_name = "user_" + getuid()

    with Given("I enable SSL"):
        enable_ssl(my_own_ca_key_passphrase="", server_key_passphrase="")

    try:
        with Given("I have a csr and key"):
            node.command(
                f"openssl req -newkey rsa:2048 -nodes -subj '/CN=clickhouse1:{user_name}' -keyout {user_name}_cert.key -out {user_name}_cert.csr"
            )

        with And("I generate a key that will be used for CA"):
            node.command(f"openssl genrsa -out {user_name}_ca.key 2048")

        with And("I generate a self-signed CA certfificate"):
            node.command(
                f"openssl req -x509 -subj '/CN=clickhouse1 CA' -nodes -key {user_name}_ca.key -days 1095 -out {user_name}_ca.crt"
            )

        with And("I generate and sign the new user certificate"):
            node.command(
                f"openssl x509 -req -in {user_name}_cert.csr -out {user_name}_cert.crt -CAcreateserial -CA {user_name}_ca.crt -CAkey {user_name}_ca.key -days 365"
            )

        with When("I create a user identified by the certificate"):
            node.query(
                f"CREATE USER {user_name} IDENTIFIED WITH ssl_certificate CN 'clickhouse1:{user_name}'"
            )

        with Then("I login as the user using the certificate"):
            output = node.command(
                f"echo 'SELECT 1' | curl https://clickhouse1:{self.context.secure_http_port} --cert {user_name}_cert.crt --key {user_name}_cert.key --cacert {user_name}_ca.crt -H 'X-ClickHouse-SSL-Certificate-Auth: on' -H 'X-ClickHouse-User: {user_name}' --data-binary @-"
            ).output
            assert output == "1", error()

    finally:
        with Finally("I remove the certificates and keys"):
            node.command(f"rm -f {user_name}_ca.crt")
            node.command(f"rm -f {user_name}_ca.key")
            node.command(f"rm -f {user_name}_cert.crt")
            node.command(f"rm -f {user_name}_cert.key")
