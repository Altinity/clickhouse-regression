from ssl_server.tests.zookeeper.steps import *


@TestScenario
def secure_connection(self):
    """Check secure ZooKeeper connection using client certificate and
    strict verification mode."""

    with Given(
        "I add ClickHouse server openSSL client configuration that uses client certificate"
    ):
        entries = {
            "certificateFile": "/client.crt",
            "privateKeyFile": "/client.key",
            "loadDefaultCAFile": "true",
            "cacheSessions": "false",
            "disableProtocols": "sslv2,sslv3",
            "preferServerCiphers": "true",
            "verificationMode": "strict",
            "invalidCertificateHandler": {"name": "RejectCertificateHandler"},
        }
        add_ssl_client_configuration_file(entries=entries)

    with And("I update zookeeper configuration to use encryption"):
        entries = {
            "clientPort": None,
            "secureClientPort": "2281",
            "serverCnxnFactory": "org.apache.zookeeper.server.NettyServerCnxnFactory",
            "ssl.keyStore.location": "/keystore.jks",
            "ssl.keyStore.password": "keystore",
            "ssl.trustStore.location": "/truststore.jks",
            "ssl.trustStore.password": "truststore",
        }
        add_zookeeper_configuration_file(entries=entries)

    with And("I add secure zookeeper configuration"):
        add_secure_zookeeper_configuration_file(restart=True)

    with Then("I check ClickHouse connection to zookeeper"):
        check_clickhouse_connection_to_zookeeper()


@TestFeature
@Name("zookeeper")
def feature(self, node="clickhouse1", zookeeper_node="zookeeper"):
    """Check configuring and using secure connection to ZooKeeper."""

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
        create_zookeeper_crt_and_key(name="server", node=self.context.zookeeper_node)

    with And("I add CA certificate to zookeeper truststore"):
        add_certificate_to_zookeeper_truststore(
            alias="my_own_ca", certificate=self.context.zookeeper_node_ca_crt
        )

    for scenario in loads(current_module(), Scenario):
        scenario()
