import ssl_server.tests.zookeeper.feature

from ssl_server.tests.common import fips_compatible_tlsv1_2_cipher_suites
from ssl_server.tests.zookeeper.steps import *


@TestScenario
def secure_connection(self):
    """Check secure ZooKeeper connection using client certificate and
    strict verification mode. Connection is expected to succeed."""
    ssl_server.tests.zookeeper.feature.secure_connection()


@TestScenario
def secure_connection_without_client_certificate(self):
    """Check secure ZooKeeper connection without using client certificate.
    Connection is expected to fail with bad certificate error as ZooKeeper
    is expecting the client to present a valid certificate.
    """
    ssl_server.tests.zookeeper.feature.secure_connection_without_client_certificate(
        message="Exception: error:10000410:SSL routines:OPENSSL_internal:SSLV3_ALERT_HANDSHAKE_FAILURE"
    )


@TestScenario
def secure_connection_with_unsigned_client_certificate(self):
    """Check secure ZooKeeper connection using unsigned client certificate.
    Connection is expected to fail with unknown certificate error."""
    ssl_server.tests.zookeeper.feature.secure_connection_with_unsigned_client_certificate()


@TestScenario
def secure_connection_with_empty_truststore(self):
    """Check secure ZooKeeper connection when ClickHouse uses client certificate and
    strict verification mode but ZooKeeper truststore is empty and does not contain CA.
    Connection is expected to fail with all connection tries failed error.
    """
    ssl_server.tests.zookeeper.feature.secure_connection_with_empty_truststore()


@TestScenario
def secure_connection_to_invalid_zookeeper_port(self):
    """Check that secure ZooKeeper connection fails when trying to connect to invalid zookeeper port."""
    ssl_server.tests.zookeeper.feature.secure_connection_to_invalid_zookeeper_port()


@TestOutline
def fips_connection(self, cipher_list):
    """Check secure connection from ClickHouse when ClickHouse wants to use only specific FIPS
    compatible ciphers.
    """
    ssl_server.tests.zookeeper.feature.fips_connection()


@TestFeature
def fips(self):
    """Check secure connection from ClickHouse when ClickHouse wants
    to use any or only some specific FIPS compatible ciphers."""
    ssl_server.tests.zookeeper.feature.fips()


@TestFeature
@Name("zookeeper fips")
def feature(self, node="clickhouse1", zookeeper_node="zookeeper-fips"):
    """Check configuring and using secure connection to ZooKeeper FIPs compatible server."""

    self.context.node = self.context.cluster.node(node)
    self.context.zookeeper_node = self.context.cluster.node(zookeeper_node)

    with Given("I enable SSL on clickhouse"):
        enable_ssl(my_own_ca_key_passphrase="", server_key_passphrase="")

    with And("I generate clickhouse client private key and certificate"):
        create_crt_and_key(name="client", node=self.context.node)

    with And("I add CA certificate to zookeeper node"):
        zookeeper_node_ca_crt = add_trusted_ca_certificate(
            node=self.context.zookeeper_node, certificate=self.context.my_own_ca_crt
        )
        self.context.zookeeper_node_ca_crt = zookeeper_node_ca_crt

    with And(
        "I copy the CA key to zookeeper for signing zookeeper's server certificate",
        description=f"{self.context.zookeeper_node}",
    ):
        self.context.zookeeper_node_ca_key = "/my_own_ca.key"
        copy(
            dest_node=self.context.zookeeper_node,
            src_path=self.context.my_own_ca_key,
            dest_path=self.context.zookeeper_node_ca_key,
        )

    with And("I generate zookeeper server private key and CA signed certificate"):
        create_zookeeper_crt_and_key(
            name="server", node=self.context.zookeeper_node, validate_option=""
        )

    with And("I add CA certificate to zookeeper truststore"):
        add_certificate_to_zookeeper_truststore(
            alias="my_own_ca", certificate=self.context.zookeeper_node_ca_crt
        )

    for scenario in loads(current_module(), Scenario):
        scenario()

    Feature(run=fips)
