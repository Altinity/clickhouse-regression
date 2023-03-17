import json

from testflows.core import *

from ssl_server.tests.common import *
from ssl_server.tests.ssl_context import enable_ssl


@TestScenario
@Requirements()
def system_certificates(self):
    """Check that the added ssl certificate is in the system.certificates table."""
    node = self.context.node

    for retry in retries(timeout=60):
        with retry:
            with When("I get the serial number of my certificate"):
                serial_number = node.command(
                    f"openssl x509 -text -in /etc/ssl/certs/{current().context.my_own_ca_crt.split('/')[-1]}.pem -serial | grep serial= --color=never"
                ).output[7:]

            with Then("I check that system.certificates has the serial number"):
                output = node.query(
                    f"SELECT count() FROM system.certificates WHERE serial_number = '{serial_number.lower()}'"
                ).output
                assert output == "1", error()


@TestScenario
@Requirements()
def show_certificate(self):
    """Check that the added ssl certificate is in the showCertificate function."""
    node = self.context.node

    with When("I get the serial number of my certificate"):
        serial_number = (
            node.command(
                f"openssl x509 -text -in /etc/clickhouse-server/server.crt -serial | grep serial=  --color=never"
            )
            .output[7:]
            .lstrip("0")
        )

    with Then(
        "I check that it matches the serial number in the showCertificate() function"
    ):
        output = node.query(f"SELECT showCertificate() FORMAT JSON").output
        output = json.loads(output)
        assert (
            output["data"][0]["showCertificate()"]["serial_number"]
            == serial_number.lower()
        ), error()


@TestFeature
@Name("check certificate")
def feature(self, node="clickhouse1"):
    """Check that the added ssl certificate appears in ClickHouse."""
    self.context.node = self.context.cluster.node(node)

    with Given("I enable SSL"):
        enable_ssl(my_own_ca_key_passphrase="", server_key_passphrase="")

    Scenario(run=system_certificates)
    Scenario(run=show_certificate)
