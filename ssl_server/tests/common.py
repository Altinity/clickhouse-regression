import os
from testflows.core import *
from testflows.asserts import error
from testflows.stash import stashed
from helpers.common import *


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

    entries = {"https_port": f"{https}", "tcp_port_secure": f"{tcp}"}
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
def create_rsa_private_key(self, outfile, passphrase, algorithm="aes256", length=2048):
    """Generate RSA private key."""
    bash = self.context.cluster.bash(node=None)

    if algorithm:
        algorithm = f"-{algorithm} "
    else:
        algorithm = ""

    if not passphrase:
        algorithm = ""

    with stashed.filepath(
        outfile, id=stashed.hash(algorithm, length, passphrase)
    ) as stash:
        try:
            with bash(
                f"openssl genrsa {algorithm}-out {outfile} {length}",
                name="openssl",
                asynchronous=True,
            ) as cmd:
                choice = cmd.app.expect(f"(Enter pass phrase for.*?:)|({bash.prompt})")
                if choice.group(2) is None:
                    cmd.app.send(passphrase)
                    cmd.app.expect("Verifying - Enter pass phrase for .*?:")
                    cmd.app.send(passphrase)
            stash(outfile)
        finally:
            bash(f'rm -rf "{outfile}"')
    yield stash.value


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
    country_name="",
    state_or_province="",
    locality_name="",
    organization_name="",
    organization_unit_name="",
    email_address="",
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
    country_name="",
    state_or_province="",
    locality_name="",
    organization_name="",
    organization_unit_name="",
    email_address="",
    challenge_password="",
    company_name="",
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
):
    """Sign certificate using CA certificate."""
    bash = self.context.cluster.bash(node=None)

    with stashed.filepath(
        outfile,
        id=stashed.hash(csr, ca_certificate, ca_key, ca_passphrase, type, hash, days),
    ) as stash:
        try:
            with bash(
                f"openssl {type} -{hash} -req -in {csr} -CA {ca_certificate} "
                f"-CAkey {ca_key} -CAcreateserial -out {outfile} -days {days}",
                name="openssl",
                asynchronous=True,
            ) as cmd:
                if ca_passphrase:
                    cmd.app.expect("Enter pass phrase for.*?:")
                    cmd.app.send(ca_passphrase)
            stash(outfile)
        finally:
            bash(f'rm -rf "{outfile}"')
    yield stash.value


@TestStep(Given)
def create_dh_params(self, outfile, length=256):
    """Generate Diffie-Hellman parameters file for the server."""
    bash = self.context.cluster.bash(node=None)

    with stashed.filepath(outfile, id=stashed.hash(length)) as stash:
        try:
            cmd = bash(f"openssl dhparam -out {outfile} {length}")

            with Then("checking exitcode 0"):
                assert cmd.exitcode == 0, error()

            stash(outfile)
        finally:
            bash(f'rm -rf "{outfile}"')
    yield stash.value


@TestStep(Then)
def validate_certificate(self, certificate, ca_certificate, node=None):
    """Validate certificate using CA certificate."""
    bash = self.context.cluster.bash(node=node)

    cmd = bash(f"openssl verify -x509_strict -CAfile {ca_certificate} {certificate}")

    with By("checking certificate was validated"):
        assert "OK" in cmd.output, error()

    with And("exitcode is 0"):
        assert cmd.exitcode == 0, error()


@TestStep(Given)
def add_trusted_ca_certificate(
    self,
    node,
    certificate,
    path=None,
    directory="/usr/local/share/ca-certificates/",
    eof="EOF",
    certificate_node=None,
):
    """Add CA certificate as trusted by the system."""
    bash = self.context.cluster.bash(node=certificate_node)

    if path is None:
        path = os.path.join(directory, os.path.basename(certificate))

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
def create_crt_and_key(self, name, node=None, common_name=""):
    """Create certificate and private key with specified name."""
    if node is None:
        node = self.context.node

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
            ca_certificate=current().context.my_own_ca_crt,
            ca_key=current().context.my_own_ca_key,
            ca_passphrase="",
        )

    with And("I validate the certificate"):
        validate_certificate(
            certificate=crt, ca_certificate=current().context.my_own_ca_crt
        )

    with And("I copy the certificate and key", description=f"{node}"):
        copy(dest_node=node, src_path=crt, dest_path=f"/{name}.crt")
        copy(dest_node=node, src_path=private_key, dest_path=f"/{name}.key")


@TestStep(Given)
def flask_server(self, protocol="https"):
    """Run specified flask server"""
    assert protocol == "https" or protocol == "http", error("invalid protocol")

    with self.context.cluster.shell(self.context.node.name) as bash:
        cmd = f"python3 /{protocol}_app_file.py"
        port = "5001" if protocol == "https" else "5000"

        try:
            with Given("I launch the flask server"):
                bash.send(cmd)
                bash.expect(cmd, escape=True)
                bash.expect("\n")
                bash.expect(f"Serving Flask app '{protocol} server'", escape=True)

            yield

        finally:
            while True:
                try:
                    bash.expect("\n")
                except Exception:
                    break

            with Finally("I kill the flask server"):
                bash.send(
                    f"ss -ltnup | grep '{port}' | awk -F',' '/pid=/{{print $2}}' | awk -F'=' '{{print $2}}'"
                )


@TestStep(Then)
def https_server_connection(self, success=True, options=None, node=None):
    """Check reading data from an https server with specified clickhouse-server config."""
    if node is None:
        node = self.context.node

    if success:
        message = "12345"
    else:
        message = "Exception:"

    if options is not None:
        with When("I update the clickhouse-server configs"):
            add_ssl_client_configuration_file(entries=options)

    with Then("I read data from the server using `url` table function"):
        node.query(
            "SELECT * FROM url('https://127.0.0.1:5001/data', 'CSV') FORMAT CSV",
            message=message,
        )
