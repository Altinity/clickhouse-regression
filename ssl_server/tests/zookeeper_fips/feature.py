import ssl_server.tests.zookeeper.feature

from ssl_server.tests.common import fips_compatible_tlsv1_2_cipher_suites
from ssl_server.tests.zookeeper.steps import *


@TestScenario
def secure_connection(self):
    """Check secure ZooKeeper connection using client certificate and
    strict verification mode. Connection is expected to succeed."""

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

    with And("I update zookeeper configuration to use secure connection"):
        entries = {
            "clientPort": None,
            "secureClientPort": "2281",
            "serverCnxnFactory": "org.apache.zookeeper.server.NettyServerCnxnFactory",
            "ssl.keyStore.location": "/keystore.bcfks",
            "ssl.keyStore.password": "keystore",
            "ssl.keyStore.type": "BCFKS",
            "ssl.trustStore.location": "/truststore.bcfks",
            "ssl.trustStore.password": "truststore",
            "ssl.trustStore.type": "BCFKS",
        }
        add_zookeeper_config_file(entries=entries)

    with And("I add to ClickHouse secure zookeeper configuration"):
        add_to_clickhouse_secure_zookeeper_config_file(restart=True)

    with Then("I check ClickHouse connection to zookeeper"):
        check_clickhouse_connection_to_zookeeper()


@TestScenario
def secure_connection_without_client_certificate(self):
    """Check secure ZooKeeper connection without using client certificate.
    Connection is expected to fail with bad certificate error as ZooKeeper
    is expecting the client to present a valid certificate.
    """
    with Given(
        "I add ClickHouse server openSSL client configuration without client certificate"
    ):
        entries = {
            "loadDefaultCAFile": "true",
            "cacheSessions": "false",
            "disableProtocols": "sslv2,sslv3",
            "preferServerCiphers": "true",
            "verificationMode": "strict",
            "invalidCertificateHandler": {"name": "RejectCertificateHandler"},
        }
        add_ssl_client_configuration_file(entries=entries)

    with And("I update zookeeper configuration to use secure connection"):
        entries = {
            "clientPort": None,
            "secureClientPort": "2281",
            "serverCnxnFactory": "org.apache.zookeeper.server.NettyServerCnxnFactory",
            "ssl.keyStore.location": "/keystore.bcfks",
            "ssl.keyStore.password": "keystore",
            "ssl.keyStore.type": "BCFKS",
            "ssl.trustStore.location": "/truststore.bcfks",
            "ssl.trustStore.password": "truststore",
            "ssl.trustStore.type": "BCFKS",
        }
        add_zookeeper_config_file(entries=entries)

    with And("I add to ClickHouse secure zookeeper configuration"):
        add_to_clickhouse_secure_zookeeper_config_file(restart=True)

    with Then("I check ClickHouse connection to zookeeper fails with an error"):
        check_clickhouse_connection_to_zookeeper(
            # message="Exception: error:10000412:SSL routines:OPENSSL_internal:SSLV3_ALERT_BAD_CERTIFICATE"
            message="Exception: error:10000410:SSL routines:OPENSSL_internal:SSLV3_ALERT_HANDSHAKE_FAILURE"
        )


@TestScenario
def secure_connection_with_unsigned_client_certificate(self):
    """Check secure ZooKeeper connection using unsigned client certificate.
    Connection is expected to fail with unknown certificate error."""

    with Given("I generate new clickhouse client private key and unsigned certificate"):
        create_crt_and_key(name="unsigned_client", node=self.context.node, signed=False)

    with And(
        "I add ClickHouse server openSSL client configuration that uses unsigned client certificate"
    ):
        entries = {
            "certificateFile": "/unsigned_client.crt",
            "privateKeyFile": "/unsigned_client.key",
            "loadDefaultCAFile": "true",
            "cacheSessions": "false",
            "disableProtocols": "sslv2,sslv3",
            "preferServerCiphers": "true",
            "verificationMode": "strict",
            "invalidCertificateHandler": {"name": "RejectCertificateHandler"},
        }
        add_ssl_client_configuration_file(entries=entries)

    with And("I update zookeeper configuration to use secure connection"):
        entries = {
            "clientPort": None,
            "secureClientPort": "2281",
            "serverCnxnFactory": "org.apache.zookeeper.server.NettyServerCnxnFactory",
            "ssl.keyStore.location": "/keystore.bcfks",
            "ssl.keyStore.password": "keystore",
            "ssl.keyStore.type": "BCFKS",
            "ssl.trustStore.location": "/truststore.bcfks",
            "ssl.trustStore.password": "truststore",
            "ssl.trustStore.type": "BCFKS",
        }
        add_zookeeper_config_file(entries=entries)

    with And("I add secure zookeeper configuration"):
        add_to_clickhouse_secure_zookeeper_config_file(restart=True)

    with Then(
        "I check ClickHouse connection to zookeeper fails with unknown certificate error"
    ):
        check_clickhouse_connection_to_zookeeper(
            message="Exception: error:10000416:SSL routines:OPENSSL_internal:SSLV3_ALERT_CERTIFICATE_UNKNOWN",
        )


@TestScenario
def secure_connection_with_empty_truststore(self):
    """Check secure ZooKeeper connection when ClickHouse uses client certificate and
    strict verification mode but ZooKeeper truststore is empty and does not contain CA.
    Connection is expected to fail with all connection tries failed error.
    """

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

    with And("I create empty zookeeper truststore"):
        with By("creating truststore with dummy certificate"):
            add_certificate_to_zookeeper_truststore(
                alias="dummy",
                certificate=self.context.zookeeper_node_ca_crt,
                keystore="/empty_truststore.pkcs12",
                storepass="truststore",
                storetype="PKCS12",
            )

        with And("then deleting the dummy certificate from that truststore"):
            delete_certificate_from_zookeeper_truststore(
                alias="dummy",
                keystore="/empty_truststore.pkcs12",
                storepass="truststore",
                storetype="PKCS12",
            )

        with And("I convert empty truststore from PKCS12 type to BCFKS"):
            convert_zookeeper_truststore(
                srckeystore="/empty_truststore.pkcs12",
                srcstorepass="truststore",
                srcstoretype="PKCS12",
                destkeystore="/empty_truststore.bcfks",
                deststoretype=self.context.storetype,
                deststorepass="truststore",
                storeprovidername=self.context.providername,
                storeproviderclass=self.context.providerclass,
                storeproviderpath=self.context.providerpath,
            )

        with And("I list truststore contents"):
            list_zookeeper_truststore(
                keystore="/empty_truststore.bcfks",
                storepass="truststore",
                storetype=self.context.storetype,
                storeprovidername=self.context.providername,
                storeproviderclass=self.context.providerclass,
                storeproviderpath=self.context.providerpath,
            )

    with And(
        "I update zookeeper configuration to use secure connection but with empty truststore"
    ):
        entries = {
            "clientPort": None,
            "secureClientPort": "2281",
            "serverCnxnFactory": "org.apache.zookeeper.server.NettyServerCnxnFactory",
            "ssl.keyStore.location": "/keystore.bcfks",
            "ssl.keyStore.password": "keystore",
            "ssl.keyStore.type": "BCFKS",
            "ssl.trustStore.location": "/empty_truststore.bcfks",
            "ssl.trustStore.password": "truststore",
            "ssl.trustStore.type": "BCFKS",
        }
        add_zookeeper_config_file(entries=entries)

    with And("I add to ClickHouse secure zookeeper configuration"):
        add_to_clickhouse_secure_zookeeper_config_file(restart=True)

    with Then(
        "I check ClickHouse connection to zookeeper fails with all connection tries failed"
    ):
        check_clickhouse_connection_to_zookeeper(
            message="Exception: "
        )


@TestScenario
def secure_connection_to_invalid_zookeeper_port(self):
    """Check that secure ZooKeeper connection fails when trying to connect to invalid zookeeper port."""

    with Given(
        "I add ClickHouse server openSSL client configuration without client certificate"
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

    with And("I update zookeeper configuration to use secure connection"):
        entries = {
            "clientPort": None,
            "secureClientPort": "2281",
            "serverCnxnFactory": "org.apache.zookeeper.server.NettyServerCnxnFactory",
            "ssl.keyStore.location": "/keystore.bcfks",
            "ssl.keyStore.password": "keystore",
            "ssl.keyStore.type": "BCFKS",
            "ssl.trustStore.location": "/truststore.bcfks",
            "ssl.trustStore.password": "truststore",
            "ssl.trustStore.type": "BCFKS",
        }
        add_zookeeper_config_file(entries=entries)

    with And(
        "I add to ClickHouse secure zookeeper configuration that uses invalid zookeeper port"
    ):
        add_to_clickhouse_secure_zookeeper_config_file(port=2280, restart=True)

    with Then("I check ClickHouse connection to zookeeper fails"):
        check_clickhouse_connection_to_zookeeper(
            message="Exception: "
        )


@TestOutline
def fips_connection(self, cipher_list):
    """Check secure connection from ClickHouse when ClickHouse wants to use only specific FIPS
    compatible ciphers.
    """
    with Given(
        "ClickHouse is configured to connect to ZooKeeper only using FIPS compatible connections",
    ):
        entries = {
            "certificateFile": "/client.crt",
            "privateKeyFile": "/client.key",
            "loadDefaultCAFile": "true",
            "cacheSessions": "false",
            "verificationMode": "strict",
            "invalidCertificateHandler": {"name": "RejectCertificateHandler"},
            "cipherList": cipher_list,
            "preferServerCiphers": "false",
            "requireTLSv1_2": "true",
            "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
        }
        add_ssl_client_configuration_file(entries=entries)

    with And("I update zookeeper configuration to use secure connection"):
        entries = {
            "clientPort": None,
            "secureClientPort": "2281",
            "serverCnxnFactory": "org.apache.zookeeper.server.NettyServerCnxnFactory",
            "ssl.keyStore.location": "/keystore.bcfks",
            "ssl.keyStore.password": "keystore",
            "ssl.keyStore.type": "BCFKS",
            "ssl.trustStore.location": "/truststore.bcfks",
            "ssl.trustStore.password": "truststore",
            "ssl.trustStore.type": "BCFKS",
        }
        add_zookeeper_config_file(entries=entries)

    with And("I add to ClickHouse secure zookeeper configuration"):
        add_to_clickhouse_secure_zookeeper_config_file(restart=True)

    with Then("I check ClickHouse connection to zookeeper works"):
        check_clickhouse_connection_to_zookeeper()


@TestFeature
def fips(self):
    """Check secure connection from ClickHouse when ClickHouse wants
    to use any or only some specific FIPS compatible ciphers."""

    for cipher_suite in fips_compatible_tlsv1_2_cipher_suites:
        with Feature(f"{cipher_suite}"):
            fips_connection(cipher_list=cipher_suite)

    with Feature("any compatible"):
        fips_connection(
            cipher_list=":".join([v for v in fips_compatible_tlsv1_2_cipher_suites])
        )


@TestFeature
@Name("zookeeper fips")
def feature(self, node="clickhouse1", zookeeper_node="zookeeper-fips"):
    """Check configuring and using secure connection to ZooKeeper FIPs compatible server."""

    self.context.node = self.context.cluster.node(node)
    self.context.zookeeper_node = self.context.cluster.node(zookeeper_node)

    self.context.storetype = "BCFKS"
    self.context.providername = "BCFIPS"
    self.context.providerclass = (
        "org.bouncycastle.jcajce.provider.BouncyCastleFipsProvider"
    )
    self.context.providerpath = "$ZOOKEEPER_HOME/lib/bc-fips-1.0.2.3.jar"
    self.context.zookeeper_node.SERVER_ENV = 'SERVER_JVMFLAGS="-Dfips.enabled=true -Dorg.bouncycastle.fips.approved_only=true -Djava.security.properties=/conf/fips.java.security" '

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
            name="zookeeper",
            node=self.context.zookeeper_node,
            validate_option="",
            keystore="/keystore.pkcs12",
            storepass="keystore",
            storetype="PKCS12",
        )

    with And("I convert keystore from PKCS12 type to BCFKS"):
        convert_zookeeper_truststore(
            srckeystore="/keystore.pkcs12",
            srcstorepass="keystore",
            srcstoretype="PKCS12",
            destkeystore="/keystore.bcfks",
            deststoretype=self.context.storetype,
            deststorepass="keystore",
            storeprovidername=self.context.providername,
            storeproviderclass=self.context.providerclass,
            storeproviderpath=self.context.providerpath,
        )

    with And("I list keystore contents"):
        list_zookeeper_truststore(
            keystore="/keystore.bcfks",
            storepass="keystore",
            storetype=self.context.storetype,
            storeprovidername=self.context.providername,
            storeproviderclass=self.context.providerclass,
            storeproviderpath=self.context.providerpath,
        )

    with And("I add CA certificate to zookeeper truststore"):
        add_certificate_to_zookeeper_truststore(
            alias="my_own_ca",
            certificate=self.context.zookeeper_node_ca_crt,
            keystore="/truststore.pkcs12",
            storepass="truststore",
            storetype="PKCS12",
        )

    with And("I convert truststore from PKCS12 type to BCFKS"):
        convert_zookeeper_truststore(
            srckeystore="/truststore.pkcs12",
            srcstorepass="truststore",
            srcstoretype="PKCS12",
            destkeystore="/truststore.bcfks",
            deststoretype=self.context.storetype,
            deststorepass="truststore",
            storeprovidername=self.context.providername,
            storeproviderclass=self.context.providerclass,
            storeproviderpath=self.context.providerpath,
        )

    with And("I list truststore contents"):
        list_zookeeper_truststore(
            keystore="/truststore.bcfks",
            storepass="truststore",
            storetype=self.context.storetype,
            storeprovidername=self.context.providername,
            storeproviderclass=self.context.providerclass,
            storeproviderpath=self.context.providerpath,
        )

    for scenario in loads(current_module(), Scenario):
        scenario()

    Feature(run=fips)
