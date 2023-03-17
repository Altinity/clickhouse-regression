from testflows.core import *

from ssl_server.tests.common import *
from ssl_server.tests.ssl_context import enable_ssl


@TestStep(Given)
def add_certificate_to_zookeeper_truststore(
    self,
    alias,
    certificate,
    keystore="/truststore.jks",
    storepass="truststore",
    node=None,
):
    """Add certificate to ZooKeeper's truststore."""
    if node is None:
        node = self.context.zookeeper_node

    node.command(
        f"keytool -importcert -alias {alias} "
        f"-file {certificate} "
        f"-keystore {keystore} "
        f"-storepass {storepass} "
        f"-storetype JKS -noprompt",
        exitcode=0,
    )


@TestStep(Given)
def create_zookeeper_crt_and_key(
    self,
    name,
    node=None,
    keystore="/keystore.jks",
    keyalg="RSA",
    keysize=2048,
    storepass="keystore",
    keypass=None,
):
    """Create zookeeper certificate and key. Key is stored in the keystore."""
    if node is None:
        node = self.context.zookeeper_node

    with By("generating keypair"):
        command = (
            f"keytool -genkeypair -alias $(hostname -f)-{name} "
            f"-keyalg {keyalg} "
            f"-keystore {keystore} "
            f"-keysize {keysize} "
            f'-dname "CN=$(hostname -f),OU=Dept,O=Example.com,L=City,ST=State,C=US" '
            f"-storepass {storepass}"
        )

        if keypass is not None:
            command += f" -keypass {keypass}"

        node.command(command, exitcode=0)

    csr = f"/{name}.csr"

    with And("generating certificate signing request"):
        command = (
            f"keytool -certreq -alias $(hostname -f)-{name} "
            f"-keystore {keystore} "
            f"-file {csr} -storepass {storepass}"
        )

        if keypass is not None:
            command += f" -keypass {keypass}"

        node.command(command, exitcode=0)

    crt = f"/{name}.crt"

    with And("signing the certificate with CA"):
        crt = sign_certificate(
            outfile=crt,
            csr=csr,
            ca_certificate=self.context.zookeeper_node_ca_crt,
            ca_key=self.context.zookeeper_node_ca_key,
            ca_passphrase="",
            node=node.name,
            use_stash=False,
        )

    with And("validating the certificate"):
        validate_certificate(
            certificate=crt,
            ca_certificate=self.context.zookeeper_node_ca_crt,
            node=node,
        )

    with And("adding signed certificate to keystore"):
        add_certificate_to_zookeeper_truststore(
            alias="server", certificate=crt, keystore=keystore, storepass=storepass
        )


@TestFeature
@Name("zookeeper")
def feature(self, node="clickhouse1", zookeeper_node="zookeeper"):
    """Check configuring and using SSL connection to ZooKeeper."""
    self.context.node = self.context.cluster.node(node)
    self.context.zookeeper_node = self.context.cluster.node(zookeeper_node)

    pause()

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
        "I copy the CA key to zookeeper for certificate signing",
        description=f"{self.context.zookeeper_node}",
    ):
        self.context.zookeeper_node_ca_key = "/my_own_ca.key"
        copy(
            dest_node=self.context.zookeeper_node,
            src_path=self.context.my_own_ca_key,
            dest_path=self.context.zookeeper_node_ca_key,
        )

    with And("I generate zookeeper server private key and certificate"):
        create_zookeeper_crt_and_key(name="server", node=self.context.zookeeper_node)

    with And("I add CA certificate to zookeeper truststore"):
        add_certificate_to_zookeeper_truststore(
            alias="my_own_ca", certificate=self.context.zookeeper_node_ca_crt
        )

    pause()
