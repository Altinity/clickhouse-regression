import os
import tempfile
import textwrap

from testflows.core import *
from testflows.asserts import error
from testflows.stash import stashed
from helpers.common import *
from ssl_server.test_files.https_app_file import ciphers
from ssl_server.test_files.https_app_file import https_protocol


fips_compatible_tlsv1_2_cipher_suites = [
    "ECDHE-RSA-AES128-GCM-SHA256",
    "ECDHE-RSA-AES256-GCM-SHA384",
    "ECDHE-ECDSA-AES128-GCM-SHA256",
    "ECDHE-ECDSA-AES256-GCM-SHA384",
    "AES128-GCM-SHA256",
    "AES256-GCM-SHA384",
]

all_ciphers = [
    "TLS_AES_256_GCM_SHA384",
    "TLS_CHACHA20_POLY1305_SHA256",
    "TLS_AES_128_GCM_SHA256",
    "ECDHE-ECDSA-AES256-GCM-SHA384",
    "ECDHE-RSA-AES256-GCM-SHA384",
    "DHE-RSA-AES256-GCM-SHA384",
    "ECDHE-ECDSA-CHACHA20-POLY1305",
    "ECDHE-RSA-CHACHA20-POLY1305",
    "DHE-RSA-CHACHA20-POLY1305",
    "ECDHE-ECDSA-AES128-GCM-SHA256",
    "ECDHE-RSA-AES128-GCM-SHA256",
    "DHE-RSA-AES128-GCM-SHA256",
    "ECDHE-ECDSA-AES256-SHA384",
    "ECDHE-RSA-AES256-SHA384",
    "DHE-RSA-AES256-SHA256",
    "ECDHE-ECDSA-AES128-SHA256",
    "ECDHE-RSA-AES128-SHA256",
    "DHE-RSA-AES128-SHA256",
    "ECDHE-ECDSA-AES256-SHA",
    "ECDHE-RSA-AES256-SHA",
    "DHE-RSA-AES256-SHA",
    "ECDHE-ECDSA-AES128-SHA",
    "ECDHE-RSA-AES128-SHA",
    "DHE-RSA-AES128-SHA",
    "RSA-PSK-AES256-GCM-SHA384",
    "DHE-PSK-AES256-GCM-SHA384",
    "RSA-PSK-CHACHA20-POLY1305",
    "DHE-PSK-CHACHA20-POLY1305",
    "ECDHE-PSK-CHACHA20-POLY1305",
    "AES256-GCM-SHA384",
    "PSK-AES256-GCM-SHA384",
    "PSK-CHACHA20-POLY1305",
    "RSA-PSK-AES128-GCM-SHA256",
    "DHE-PSK-AES128-GCM-SHA256",
    "AES128-GCM-SHA256",
    "PSK-AES128-GCM-SHA256",
    "AES256-SHA256",
    "AES128-SHA256",
    "ECDHE-PSK-AES256-CBC-SHA384",
    "ECDHE-PSK-AES256-CBC-SHA",
    "SRP-RSA-AES-256-CBC-SHA",
    "SRP-AES-256-CBC-SHA",
    "RSA-PSK-AES256-CBC-SHA384",
    "DHE-PSK-AES256-CBC-SHA384",
    "RSA-PSK-AES256-CBC-SHA",
    "DHE-PSK-AES256-CBC-SHA",
    "AES256-SHA",
    "PSK-AES256-CBC-SHA384",
    "PSK-AES256-CBC-SHA",
    "ECDHE-PSK-AES128-CBC-SHA256",
    "ECDHE-PSK-AES128-CBC-SHA",
    "SRP-RSA-AES-128-CBC-SHA",
    "SRP-AES-128-CBC-SHA",
    "RSA-PSK-AES128-CBC-SHA256",
    "DHE-PSK-AES128-CBC-SHA256",
    "RSA-PSK-AES128-CBC-SHA",
    "DHE-PSK-AES128-CBC-SHA",
    "AES128-SHA",
    "PSK-AES128-CBC-SHA256",
    "PSK-AES128-CBC-SHA",
]


@TestStep(Given)
def add_ssl_server_configuration_file(
    self,
    entries,
    config=None,
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file="ssl_server.xml",
    timeout=300,
    restart=False,
    node=None,
):
    """Add SSL server configuration to config.xml.

    Example parameters that are available for the server
    (https://github.com/ClickHouse-Extras/poco/blob/master/NetSSL_OpenSSL/include/Poco/Net/SSLManager.h#L71)

    <privateKeyFile>mycert.key</privateKeyFile>
        <certificateFile>mycert.crt</certificateFile>
        <caConfig>rootcert.pem</caConfig>
        <verificationMode>none|relaxed|strict|once</verificationMode>
        <verificationDepth>1..9</verificationDepth>
        <loadDefaultCAFile>true|false</loadDefaultCAFile>
        <cipherList>ALL:!ADH:!LOW:!EXP:!MD5:@STRENGTH</cipherList>
        <preferServerCiphers>true|false</preferServerCiphers>
        <privateKeyPassphraseHandler>
            <name>KeyFileHandler</name>
            <options>
                <password>test</password>
            </options>
        </privateKeyPassphraseHandler>
        <invalidCertificateHandler>
             <name>ConsoleCertificateHandler</name>
        </invalidCertificateHandler>
        <cacheSessions>true|false</cacheSessions>
        <sessionIdContext>someString</sessionIdContext> <!-- server only -->
        <sessionCacheSize>0..n</sessionCacheSize>       <!-- server only -->
        <sessionTimeout>0..n</sessionTimeout>           <!-- server only -->
        <extendedVerification>true|false</extendedVerification>
        <requireTLSv1>true|false</requireTLSv1>
        <requireTLSv1_1>true|false</requireTLSv1_1>
        <requireTLSv1_2>true|false</requireTLSv1_2>
        <disableProtocols>sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_2</disableProtocols>
        <dhParamsFile>dh.pem</dhParamsFile>
        <ecdhCurve>prime256v1</ecdhCurve>
    """
    _entries = {"openSSL": {"server": entries}}

    if config is None:
        config = create_xml_config_content(
            _entries, config_file=config_file, config_d_dir=config_d_dir
        )

    return add_config(config, timeout=timeout, restart=restart, node=node)


@TestStep(Given)
def add_ssl_client_configuration_file(
    self,
    entries,
    config=None,
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file="ssl_client.xml",
    timeout=300,
    restart=False,
    node=None,
):
    """Add SSL client configuration to config.xml.

    Example parameters that are available for the server
    (https://github.com/ClickHouse-Extras/poco/blob/master/NetSSL_OpenSSL/include/Poco/Net/SSLManager.h#L71)

    <privateKeyFile>mycert.key</privateKeyFile>
        <certificateFile>mycert.crt</certificateFile>
        <caConfig>rootcert.pem</caConfig>
        <verificationMode>none|relaxed|strict|once</verificationMode>
        <verificationDepth>1..9</verificationDepth>
        <loadDefaultCAFile>true|false</loadDefaultCAFile>
        <cipherList>ALL:!ADH:!LOW:!EXP:!MD5:@STRENGTH</cipherList>
        <preferServerCiphers>true|false</preferServerCiphers>
        <privateKeyPassphraseHandler>
            <name>KeyFileHandler</name>
            <options>
                <password>test</password>
            </options>
        </privateKeyPassphraseHandler>
        <invalidCertificateHandler>
             <name>ConsoleCertificateHandler</name>
        </invalidCertificateHandler>
        <cacheSessions>true|false</cacheSessions>
        <extendedVerification>true|false</extendedVerification>
        <requireTLSv1>true|false</requireTLSv1>
        <requireTLSv1_1>true|false</requireTLSv1_1>
        <requireTLSv1_2>true|false</requireTLSv1_2>
        <disableProtocols>sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_2</disableProtocols>
        <dhParamsFile>dh.pem</dhParamsFile>
        <ecdhCurve>prime256v1</ecdhCurve>
    """
    _entries = {"openSSL": {"client": entries}}
    if config is None:
        config = create_xml_config_content(
            _entries, config_file=config_file, config_d_dir=config_d_dir
        )

    return add_config(config, timeout=timeout, restart=restart, node=node)


@TestStep(Given)
def add_ssl_fips_configuration_file(
    self,
    value,
    config=None,
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file="ssl_fips.xml",
    timeout=300,
    restart=False,
    node=None,
):
    """Add SSL fips configuration to config.xml.

    <yandex>
        <openSSL>
            <fips>false</fips>
        </openSSL>
    </yandex>

    :param value: either "true", or "false"
    """
    assert value in ("true", "false")

    entries = {"openSSL": {"fips": f"{value}"}}
    if config is None:
        config = create_xml_config_content(
            entries, config_file=config_file, config_d_dir=config_d_dir
        )

    return add_config(config, timeout=timeout, restart=restart, node=node)


@TestStep(Given)
def add_secure_ports_configuration_file(
    self,
    https="8443",
    tcp="9440",
    interserver_https="9010",
    config=None,
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file="ssl_ports.xml",
    timeout=300,
    restart=False,
    node=None,
):
    """Add SSL secure ports to config.xml."""
    self.context.secure_http_port = https
    self.context.secure_tcp_port = tcp

    entries = {
        "https_port": f"{https}",
        "tcp_port_secure": f"{tcp}",
        "interserver_https_port": f"{interserver_https}",
    }
    if config is None:
        config = create_xml_config_content(
            entries, config_file=config_file, config_d_dir=config_d_dir
        )

    return add_config(config, timeout=timeout, restart=restart, node=node)


@TestStep(Given)
def add_ssl_clickhouse_client_configuration_file(
    self,
    entries,
    config=None,
    config_d_dir="/etc/clickhouse-client/",
    config_file="config.xml",
    timeout=300,
    restart=False,
    node=None,
):
    """Add clickhouse-client SSL configuration file.

    <config>
        <openSSL>
            <client> <!-- Used for connection to server's secure tcp port -->
                <loadDefaultCAFile>true</loadDefaultCAFile>
                <cacheSessions>true</cacheSessions>
                <disableProtocols>sslv2,sslv3</disableProtocols>
                <preferServerCiphers>true</preferServerCiphers>
                <!-- Use for self-signed: <verificationMode>none</verificationMode> -->
                <invalidCertificateHandler>
                    <!-- Use for self-signed: <name>AcceptCertificateHandler</name> -->
                    <name>RejectCertificateHandler</name>
                </invalidCertificateHandler>
            </client>
        </openSSL>
    </config>
    """
    if node is None:
        node = self.context.node

    entries = {"openSSL": {"client": entries}}
    if config is None:
        config = create_xml_config_content(
            entries, config_file=config_file, config_d_dir=config_d_dir, root="config"
        )

    try:
        with When("I add the config", description=config.path):
            node.command(f"mkdir -p {config_d_dir}", exitcode=0)
            command = f"cat <<HEREDOC > {config.path}\n{config.content}\nHEREDOC"
            node.command(command, steps=False, exitcode=0)

        yield
    finally:
        with Finally(f"I remove {config.name} on {node.name}"):
            with By("deleting the config file", description=config.path):
                node.command(f"rm -rf {config.path}", exitcode=0)


@TestStep(Given)
def create_rsa_private_key(
    self, outfile, passphrase, algorithm="aes256", length=2048, use_stash=True
):
    """Generate RSA private key."""
    bash = self.context.cluster.bash(node=None)

    if algorithm:
        algorithm = f"-{algorithm} "
    else:
        algorithm = ""

    if not passphrase:
        algorithm = ""

    with stashed.filepath(
        outfile, id=stashed.hash(algorithm, length, passphrase), use_stash=use_stash
    ) as stash:
        try:
            with bash(
                f"openssl genrsa {algorithm}-out {outfile} {length}",
                name="openssl",
                asynchronous=True,
            ) as cmd:
                choice = cmd.app.expect(
                    f"(Enter( PEM)? pass phrase( for)?.*?:)|({bash.prompt})"
                )
                if choice.group(4) is None:
                    cmd.app.send(passphrase)
                    cmd.app.expect("Verifying - Enter( PEM)? pass phrase( for)?.*?:")
                    cmd.app.send(passphrase)
            stash(outfile)
        finally:
            if stash.is_used:
                bash(f'rm -rf "{outfile}"')
    yield stash.value


@TestStep(Given)
def create_local_tmpdir(self):
    """Create local (host) temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            with By("creating temporary directory", description=f"{tmpdir}"):
                yield tmpdir
        finally:
            with Finally("deleting temporary directory", description=f"{tmpdir}"):
                pass


@TestStep(Given)
def create_ca_store_dir(self, path, name, config=None):
    """Create certificate authority store folder."""

    if config is None:
        config = textwrap.dedent(
            f"""
        [ ca ]
        default_ca = ca_default

        [ ca_default ]
        dir = {path}/{name}
        certs = \\$dir
        new_certs_dir = \\$dir/certs
        database = \\$dir/index
        serial = \\$dir/serial
        certificate = \\$dir/ca.crt
        private_key = \\$dir/ca.key
        default_days = 365
        default_crl_days = 30
        default_md = md5
        preserve = no
        policy = generic_policy

        [ generic_policy ]
        countryName = optional
        stateOrProvinceName = optional
        localityName = optional
        organizationName = optional
        organizationalUnitName = optional
        commonName = supplied
        emailAddress = optional

        [ v3_intermediate_ca ]
        subjectKeyIdentifier = hash
        authorityKeyIdentifier = keyid:always,issuer
        basicConstraints = critical, CA:true, pathlen:1
        keyUsage = critical, digitalSignature, cRLSign, keyCertSign
        """
        )

    bash = self.context.cluster.bash(node=None)

    with By("creating CA store directory"):
        store_dir = define("store directory", os.path.join(path, name))
        cmd = bash(f"mkdir {store_dir}")
        assert cmd.exitcode == 0, error()

    with And("creating store configuration file"):
        cmd = bash(
            f"cat <<HEREDOC > {os.path.join(store_dir, 'ca.cnf')}\n{config}\nHEREDOC"
        )
        assert cmd.exitcode == 0, error()

    with And("creating certs subdirectory"):
        cmd = bash(f"mkdir {os.path.join(store_dir, 'certs')}")
        assert cmd.exitcode == 0, error()

    with And("creating index file"):
        cmd = bash(f"touch {os.path.join(store_dir, 'index')}")
        assert cmd.exitcode == 0, error()

    with And("creating serial file"):
        cmd = bash(f"echo 01 > {os.path.join(store_dir, 'serial')}")
        assert cmd.exitcode == 0, error()

    with And("creating serial file"):
        cmd = bash(f"echo 01 > {os.path.join(store_dir, 'crlnumber')}")
        assert cmd.exitcode == 0, error()

    with And("listing store directory contents"):
        cmd = bash(f"ls -la {store_dir}")
        assert cmd.exitcode == 0, error()

    return store_dir


@TestStep(Given)
def create_root_ca_store(self, path, name="root", passphrase=""):
    """Create root CA store at the given path."""
    with By("create store directory"):
        store_dir = create_ca_store_dir(path=path, name=name)

    with And("creating CA key"):
        create_rsa_private_key(
            outfile=os.path.join(store_dir, "ca.key"),
            passphrase=passphrase,
            use_stash=False,
        )

    with And("creating self-signed CA certificate"):
        create_ca_certificate(
            outfile=os.path.join(store_dir, "ca.crt"),
            key=os.path.join(store_dir, "ca.key"),
            passphrase=passphrase,
            common_name=name,
            use_stash=False,
        )

    return store_dir


@TestStep(Given)
def create_intermediate_ca_store(
    self, path, name, root_store, root_store_passphrase="", passphrase=""
):
    """Create intermediate CA store at the given path signed using the key of the specified root store."""
    with By("create store directory"):
        store_dir = create_ca_store_dir(path=path, name=name)

    with And("creating intermediate CA key"):
        create_rsa_private_key(
            outfile=os.path.join(store_dir, "ca.key"),
            passphrase=passphrase,
            use_stash=False,
        )

    with And("creating intermediate CA certificate signing request"):
        create_certificate_signing_request(
            outfile=os.path.join(store_dir, "ca.csr"),
            key=os.path.join(store_dir, "ca.key"),
            passphrase=passphrase,
            common_name=name,
            use_stash=False,
        )

    with And("signing intermediate CA certificate using root store"):
        sign_intermediate_ca_certificate(
            outfile=os.path.join(store_dir, "ca.crt"),
            csr=os.path.join(store_dir, "ca.csr"),
            ca_config=os.path.join(root_store, "ca.cnf"),
            ca_passphrase=root_store_passphrase,
            use_stash=False,
        )

    return store_dir


@TestStep(Given)
def create_chain_certificate(self, outfile, certificates):
    """Create chain certificate file."""
    bash = self.context.cluster.bash(node=None)

    with By("creating chain file"):
        if not certificates:
            cmd = bash(f"touch {outfile}")
        else:
            cmd = bash(f"cat {' '.join(certificates)}  > {outfile}")
        assert cmd.exitcode == 0, error()

    return outfile


@TestStep(Given)
def create_ca_certificate(
    self,
    key,
    passphrase,
    common_name,
    outfile,
    type="x509",
    days="3650",
    hash="sha256",
    extensions="v3_ca",
    country_name="CA",
    state_or_province="ON",
    locality_name="Ottawa",
    organization_name="Altinity",
    organization_unit_name="QA",
    email_address="qa@altinity.com",
    use_stash=True,
):
    """Generate CA certificate."""
    bash = self.context.cluster.bash(node=None)

    with stashed.filepath(
        outfile,
        id=stashed.hash(
            key,
            passphrase,
            common_name,
            type,
            days,
            hash,
            extensions,
            country_name,
            state_or_province,
            locality_name,
            organization_name,
            organization_unit_name,
            email_address,
        ),
        use_stash=use_stash,
    ) as stash:
        try:
            with bash(
                f"openssl req -new -{type} -days {days} -key {key} "
                f"-{hash} -extensions {extensions} -out {outfile}",
                name="openssl",
                asynchronous=True,
            ) as cmd:
                if passphrase:
                    cmd.app.expect("Enter pass phrase for.*?:")
                    cmd.app.send(passphrase)
                cmd.app.expect("Country Name.*?:")
                cmd.app.send(country_name)
                cmd.app.expect("State or Province Name.*?:")
                cmd.app.send(state_or_province)
                cmd.app.expect("Locality Name.*?:")
                cmd.app.send(locality_name)
                cmd.app.expect("Organization Name.*?:")
                cmd.app.send(organization_name)
                cmd.app.expect("Organizational Unit Name.*?:")
                cmd.app.send(organization_unit_name)
                cmd.app.expect("Common Name.*?:")
                cmd.app.send(common_name)
                cmd.app.expect("Email Address.*?:")
                cmd.app.send(email_address)
            stash(outfile)
        finally:
            if stash.is_used:
                bash(f'rm -rf "{outfile}"')
    yield stash.value


@TestStep(Given)
def create_certificate_signing_request(
    self,
    outfile,
    key,
    passphrase,
    common_name,
    hash="sha256",
    country_name="CA",
    state_or_province="ON",
    locality_name="Ottawa",
    organization_name="Altinity",
    organization_unit_name="QA",
    email_address="qa@altinity.com",
    challenge_password="",
    company_name="Altinity",
    use_stash=True,
):
    """Generate certificate signing request."""
    bash = self.context.cluster.bash(node=None)

    with stashed.filepath(
        outfile,
        id=stashed.hash(
            key,
            passphrase,
            common_name,
            hash,
            country_name,
            state_or_province,
            locality_name,
            organization_name,
            organization_unit_name,
            email_address,
            challenge_password,
            company_name,
        ),
        use_stash=use_stash,
    ) as stash:
        try:
            with bash(
                f"openssl req -{hash} -new -key {key} -out {outfile}",
                name="openssl",
                asynchronous=True,
            ) as cmd:
                choice = cmd.app.expect(
                    "(Enter pass phrase for.*?:)|(Country Name.*?:)"
                )
                if choice.group(1):
                    cmd.app.send(passphrase)
                    cmd.app.expect("Country Name.*?:")
                cmd.app.send(country_name)
                cmd.app.expect("State or Province Name.*?:")
                cmd.app.send(state_or_province)
                cmd.app.expect("Locality Name.*?:")
                cmd.app.send(locality_name)
                cmd.app.expect("Organization Name.*?:")
                cmd.app.send(organization_name)
                cmd.app.expect("Organizational Unit Name.*?:")
                cmd.app.send(organization_unit_name)
                cmd.app.expect("Common Name.*?:")
                cmd.app.send(common_name)
                cmd.app.expect("Email Address.*?:")
                cmd.app.send(email_address)
                cmd.app.expect("A challenge password.*?:")
                cmd.app.send(challenge_password)
                cmd.app.expect("An optional company name.*?:")
                cmd.app.send(company_name)
            stash(outfile)
        finally:
            if stash.is_used:
                bash(f'rm -rf "{outfile}"')
    yield stash.value


@TestStep(Given)
def sign_intermediate_ca_certificate(
    self,
    outfile,
    csr,
    ca_config,
    ca_passphrase,
    type="ca",
    days="365",
    extensions="v3_intermediate_ca",
    node=None,
    use_stash=True,
):
    """Sign intermediate CA certificate."""
    bash = self.context.cluster.bash(node=node)

    with stashed.filepath(
        outfile,
        id=stashed.hash(csr, ca_config, ca_passphrase, type, hash, days),
        use_stash=use_stash,
    ) as stash:
        try:
            command = (
                f"openssl {type} -config {ca_config} -extensions {extensions} "
                f"-in {csr} -out {outfile} -days {days} -notext"
            )

            with bash(
                command,
                name="openssl",
                asynchronous=True,
            ) as cmd:
                if ca_passphrase:
                    cmd.app.expect("Enter pass phrase for.*?:")
                    cmd.app.send(ca_passphrase)
                cmd.app.expect("Sign the certificate\?")
                cmd.app.send("y")
                cmd.app.expect("certificate requests certified, commit\?")
                cmd.app.send("y")
                cmd.app.expect("Data Base Updated")
            assert cmd.exitcode == 0, error()
            stash(outfile)
        finally:
            if stash.is_used:
                bash(f'rm -rf "{outfile}"')
    yield stash.value


@TestStep(Given)
def sign_certificate(
    self,
    outfile,
    csr,
    ca_certificate,
    ca_key,
    ca_passphrase,
    type="x509",
    hash="sha256",
    days="365",
    node=None,
    use_stash=True,
):
    """Sign certificate using CA certificate."""
    bash = self.context.cluster.bash(node=node)

    with stashed.filepath(
        outfile,
        id=stashed.hash(csr, ca_certificate, ca_key, ca_passphrase, type, hash, days),
        use_stash=use_stash,
    ) as stash:
        try:
            if ca_certificate is not None:
                command = (
                    f"openssl {type} -{hash} -req -in {csr} -CA {ca_certificate} "
                    f"-CAkey {ca_key} -CAcreateserial -out {outfile} -days {days}"
                )
            else:
                command = (
                    f"openssl {type} -{hash} -req -in {csr} "
                    f"-signkey {ca_key} -out {outfile} -days {days}"
                )

            with bash(
                command,
                name="openssl",
                asynchronous=True,
            ) as cmd:
                if ca_passphrase:
                    cmd.app.expect("Enter pass phrase for.*?:")
                    cmd.app.send(ca_passphrase)
            assert cmd.exitcode == 0, error()
            stash(outfile)
        finally:
            if stash.is_used:
                bash(f'rm -rf "{outfile}"')
    yield stash.value


@TestStep(Given)
def create_dh_params(self, outfile, length=512, use_stash=True):
    """Generate Diffie-Hellman parameters file for the server."""
    bash = self.context.cluster.bash(node=None)

    with stashed.filepath(
        outfile, id=stashed.hash(length), use_stash=use_stash
    ) as stash:
        try:
            cmd = bash(f"openssl dhparam -out {outfile} {length}")

            with Then("checking exitcode 0"):
                assert cmd.exitcode == 0, error()

            stash(outfile)
        finally:
            if stash.is_used:
                bash(f'rm -rf "{outfile}"')

    yield stash.value


@TestStep(Then)
def validate_certificate(
    self, certificate, ca_certificate, option="-x509_strict", node=None
):
    """Validate certificate using CA certificate."""
    if node is None:
        node = self.context.node

    cmd = node.command(
        f"openssl verify {option} -CAfile {ca_certificate} {certificate}"
    )

    with By("checking certificate was validated"):
        assert "OK" in cmd.output, error()

    with And("exitcode is 0"):
        assert cmd.exitcode == 0, error()


@TestStep(Given)
def add_trusted_ca_certificate(
    self,
    node,
    certificate,
    name=None,
    path=None,
    directory="/usr/local/share/ca-certificates/",
    eof="EOF",
    certificate_node=None,
):
    """Add CA certificate as trusted by the system."""
    bash = self.context.cluster.bash(node=certificate_node)

    if path is None:
        if name is None:
            name = os.path.basename(certificate)
        path = os.path.join(directory, name)

    if not path.endswith(".crt"):
        path += ".crt"

    try:
        with By("copying certificate to node", description=f"{node}:{path}"):
            copy(
                dest_node=node, src_path=certificate, dest_path=path, bash=bash, eof=eof
            )

        with And("updating system certificates"):
            cmd = node.command("update-ca-certificates")

        with Then("checking certificate was added"):
            assert (
                "Adding " in cmd.output
                or "Replacing " in cmd.output
                or "Updating " in cmd.output
            ), error()

        with And("exitcode is 0"):
            assert cmd.exitcode == 0, error()

        yield path
    finally:
        with Finally("I remove CA certificate from being trusted by the system"):
            node.command(f"rm -rf {path}")
            node.command("update-ca-certificates -f", exitcode=0)


@TestStep(Then)
def openssl_client_connection(
    self,
    options="",
    port=None,
    node=None,
    hostname=None,
    success=True,
    message=None,
    messages=None,
    exitcode=None,
):
    """Check SSL connection using openssl s_client utility."""
    if node is None:
        node = self.context.node

    if port is None:
        port = self.context.connection_port

    if hostname is None:
        hostname = node.name

    if exitcode is None:
        if success:
            exitcode = 0
        else:
            exitcode = "!= 0"

    node.command(
        f'openssl s_client -brief {options} -connect {hostname}:{port} <<< "Q"',
        message=message,
        messages=messages,
        exitcode=exitcode,
    )


@TestStep(Then)
def curl_client_connection(
    self,
    options="",
    port=None,
    node=None,
    hostname=None,
    success=True,
    message=None,
    messages=None,
    exitcode=None,
    insecure=True,
):
    """Check SSL HTTP connection using curl utility.

    curl options:
        --tlsv1 and --tlsv1.1, --tlsv1.2, --tlsv1.3, --sslv2, --sslv3
        --ciphers
    """
    if node is None:
        node = self.context.node

    if port is None:
        port = self.context.connection_port

    if hostname is None:
        hostname = node.name

    if exitcode is None:
        if success:
            exitcode = 0
        else:
            exitcode = "!= 0"

    node.command(
        f'curl {"--insecure" if insecure else ""} https://{hostname}:{port} {options} -v',
        message=message,
        messages=messages,
        exitcode=exitcode,
    )


@TestStep(Then)
def clickhouse_client_connection(
    self,
    options=None,
    port=None,
    node=None,
    hostname=None,
    success=True,
    message=None,
    messages=None,
    exitcode=None,
    insecure=True,
    prefer_server_ciphers=False,
):
    """Check SSL TCP connection using clickhouse-client utility.

    supported configuration options:
        <verificationMode>none|relaxed|strict|once</verificationMode>
        <cipherList>ALL:!ADH:!LOW:!EXP:!MD5:@STRENGTH</cipherList>
        <preferServerCiphers>true|false</preferServerCiphers>
        <requireTLSv1>true|false</requireTLSv1>
        <requireTLSv1_1>true|false</requireTLSv1_1>
        <requireTLSv1_2>true|false</requireTLSv1_2>
        <requireTLSv1_3>true|false</requireTLSv1_3>
        <disableProtocols>sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_2,tlsv1_3</disableProtocols>
    """
    if node is None:
        node = self.context.node

    if port is None:
        port = self.context.connection_port

    if hostname is None:
        hostname = node.name

    if options is None:
        options = {}

    if exitcode is None:
        if success:
            exitcode = 0
        else:
            exitcode = "!= 0"

    if insecure:
        options["verificationMode"] = "none"

    options["preferServerCiphers"] = "true" if prefer_server_ciphers else "false"

    with Given("custom clickhouse-client SSL configuration"):
        add_ssl_clickhouse_client_configuration_file(entries=options)

    output = node.command(
        f'clickhouse client -s --verbose --host {hostname} --port {port} -q "SELECT 1"',
        message=message,
        messages=messages,
        exitcode=exitcode,
    ).output

    return output


@TestStep(Given)
def clickhouse_server_verification_mode(self, mode):
    """Update clickhouse-server openssl configs to use specified verification mode."""

    with Given(f"I set SSL server to `{mode}` verification mode"):
        entries = define(
            "SSL settings",
            {
                "verificationMode": mode,
            },
        )

    with And("I apply SSL server configuration"):
        add_ssl_server_configuration_file(
            entries=entries, config_file="ssl_verification_mode.xml", restart=True
        )

    return


@TestStep(Given)
def create_crt_and_key(
    self, name, node=None, common_name="", node_ca_crt=None, signed=True
):
    """Create certificate and private key with specified name."""
    if node is None:
        node = self.context.node

    if node_ca_crt is None:
        node_ca_crt = self.context.node_ca_crt

    with Given("I generate private key"):
        private_key = create_rsa_private_key(outfile=f"{name}.key", passphrase="")

    with And("I generate the certificate signing request"):
        csr = create_certificate_signing_request(
            outfile=f"{name}.csr",
            common_name=common_name,
            key=private_key,
            passphrase="",
        )

    with And("I sign the certificate with my own CA"):
        crt = sign_certificate(
            outfile=f"{name}.crt",
            csr=csr,
            ca_certificate=current().context.my_own_ca_crt if signed else None,
            ca_key=current().context.my_own_ca_key if signed else private_key,
            ca_passphrase="",
        )

    with And("I copy the certificate and key", description=f"{node}"):
        copy(dest_node=node, src_path=crt, dest_path=f"/{name}.crt")
        copy(dest_node=node, src_path=private_key, dest_path=f"/{name}.key")

    if signed:
        with And("I validate the certificate"):
            validate_certificate(
                certificate=f"/{name}.crt", ca_certificate=node_ca_crt, node=node
            )


@TestStep(Given)
def flask_server(self, server_path, port):
    """Run specified flask server"""
    with self.context.cluster.shell(self.context.node.name) as bash:
        cmd = f"python3 {server_path}"

        try:
            with Given(
                f"I launch the flask server",
            ):
                bash.send(cmd)
                bash.expect(cmd, escape=True)
                bash.expect("\n")
                bash.expect(f"Serving Flask app 'flask server'", escape=True)

            yield

        finally:
            while True:
                try:
                    bash.expect("\n")
                except Exception:
                    break

            with Finally("I kill the flask server"):
                bash.send(
                    f"ss -ltnup | grep '{port}' | awk -F',' '/pid=/{{print $2}}' | awk -F'=' '{{print $2}}' | xargs kill"
                )


@TestStep(Then)
def https_server_url_function_connection(
    self, success=True, options=None, node=None, port=None
):
    """Check reading data from an https server with specified clickhouse-server config."""
    if node is None:
        node = self.context.node

    if port is None:
        port = 5001

    if success:
        message = "12345"
    else:
        message = "Exception:"

    if options is not None:
        with When("I update the clickhouse-server configs"):
            add_ssl_client_configuration_file(entries=options, restart=True)

    with Then("I read data from the server using `url` table function"):
        node.query(
            f"SELECT * FROM url('https://127.0.0.1:{port}/data', 'CSV') FORMAT CSV",
            message=message,
        )


@TestStep(Given)
def https_server_https_dictionary_connection(
    self, name=None, node=None, success=True, options=None, port=None
):
    """Check reading data from a dictionary sourced from an https server"""
    if node is None:
        node = self.context.node

    if name is None:
        name = "dictionary_" + getuid()

    if port is None:
        port = 5001

    if success:
        message = "12345"
    else:
        message = "Exception:"

    if options is not None:
        with When("I update the clickhouse-server configs"):
            add_ssl_client_configuration_file(entries=options, restart=True)

    try:
        with When("I create a dictionary using an https source"):
            node.query(
                f"CREATE DICTIONARY {name} (c1 Int64) PRIMARY KEY c1 SOURCE(HTTP(URL 'https://127.0.0.1:{port}/data' FORMAT 'CSV')) LIFETIME(MIN 0 MAX 0) LAYOUT(FLAT())"
            )

        with Then("I select data from the dictionary"):
            node.query(f"SELECT * FROM {name} FORMAT CSV", message=message)

    finally:
        with Finally("I remove the dictionary"):
            node.query(f"DROP DICTIONARY IF EXISTS {name}")


@TestStep(When)
def update_https_server_config(
    self, server_file_path, options=None, node=None, port=None
):
    """Change the https server config"""
    if node is None:
        node = self.context.node

    if port is None:
        port = 5001

    try:
        with When(f"I change the server protocol to {options['protocol']}"):
            node.command(
                f"sed -i 's/https_protocol = ssl.PROTOCOL_TLSv1_2/https_protocol = {options['protocol']}/g' {server_file_path}"
            )

        with And(
            "I change the server ciphers",
            description=f"ciphers={options['ciphers']}",
        ):
            node.command(
                'sed -i \'s/ciphers = "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-GCM-SHA384"'
                f"/ciphers = {options['ciphers']}/g' {server_file_path}"
            )

        with And(f"I change the port to {port}"):
            node.command(f"sed -i 's/port=5001/port={port}/g' {server_file_path}")
            debug(node.command(f"cat {server_file_path}").output)
        yield

    finally:
        with Finally("I change the config back to the original"):
            node.command(f"cat /https_app_file.py > {server_file_path}")


@TestStep(Then)
def configured_https_server_http_dictionary_connection(
    self, https_server_options, success=True, port=None
):
    """Check connection from clickhouse server to configured HTTPS server using dictionary with HTTP source."""

    with When("I change the HTTPS server"):
        update_https_server_config(options=https_server_options, port=port)

    with Then("I check the connection using a dictionary"):
        https_server_https_dictionary_connection(port=port, success=success)


@TestStep(Then)
def configured_https_server_url_function_connection(
    self, https_server_options, server_file_path, success=True, port=None
):
    """Check connection from clickhouse server to configured HTTPS server using url table function."""

    with When("I change the HTTPS server"):
        update_https_server_config(
            options=https_server_options, port=port, server_file_path=server_file_path
        )

    for retry in retries(count=10, delay=0.5):
        with retry:
            with Then("I check the connection using a dictionary"):
                https_server_url_function_connection(port=port, success=success)


@TestStep(Then)
def configured_https_server_dictionary_connection(
    self, https_server_options, server_file_path, success=True, port=None
):
    """Check connection from clickhouse server to configured HTTPS server using a dictionary."""

    with When("I change the HTTPS server"):
        update_https_server_config(
            options=https_server_options, port=port, server_file_path=server_file_path
        )

    for retry in retries(count=10, delay=0.5):
        with retry:
            with Then("I check the connection using a dictionary"):
                https_server_https_dictionary_connection(port=port, success=success)
