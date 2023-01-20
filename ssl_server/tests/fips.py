from testflows.core import *

from ssl_server.tests.common import *
from ssl_server.tests.ssl_context import enable_ssl
from ssl_server.requirements import *

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


@TestOutline
def server_connection_openssl_client(self, port, tls1_2_enabled=True):
    """Check that server accepts only FIPS compatible secure connections on a given port
    using openssl s_client utility."""
    self.context.connection_port = port
    tls1_2_status = "work" if tls1_2_enabled else "be rejected"

    with Given(
        "server is configured to accept only FIPS compatible connections",
        description=f"on port {port}",
    ):
        pass

    with Check("Connection with no protocols should be rejected"):
        openssl_client_connection(
            options="-no_tls1 -no_tls1_1 -no_tls1_2 -no_tls1_3",
            success=False,
            message="no protocols available",
        )

    with Check(f"TLSv1.2 suite connection should {tls1_2_status}"):
        openssl_client_connection(options="-tls1_2", success=tls1_2_enabled)

    with Check("TLSv1 suite connection should be rejected"):
        openssl_client_connection(
            options="-tls1", success=False, message="no protocols available"
        )

    with Check("TLSv1.1 suite connection should be rejected"):
        openssl_client_connection(
            options="-tls1_1", success=False, message="no protocols available"
        )

    with Check("TLSv1.3 suite connection should be rejected"):
        openssl_client_connection(
            options="-tls1_3", success=False, message="tlsv1 alert protocol version"
        )

    with Check("any DTLS suite connection should be rejected"):
        openssl_client_connection(options="-dtls", success=False)

    with Check("DTLSv1 suite connection should be rejected"):
        openssl_client_connection(options="-dtls1", success=False)

    with Check("DTLSv1.2 suite connection should be rejected"):
        openssl_client_connection(options="-dtls1.2", success=False)

    with Check(f"just disabling TLSv1 suite connection should {tls1_2_status}"):
        openssl_client_connection(options="-no_tls1", success=tls1_2_enabled)

    with Check(f"just disabling TLSv1.1 suite connection should {tls1_2_status}"):
        openssl_client_connection(options="-no_tls1_1", success=tls1_2_enabled)

    with Check(f"just disabling TLSv1.3 suite connection should {tls1_2_status}"):
        openssl_client_connection(options="-no_tls1_3", success=tls1_2_enabled)

    with Check("disabling TLSv1.2 suite connection should be rejected"):
        openssl_client_connection(options="-no_tls1_2", success=False)

    for cipher in fips_compatible_tlsv1_2_cipher_suites:
        with Check(
            f"connection using FIPS compatible cipher {cipher} should {tls1_2_status}"
        ):
            openssl_client_connection(
                options=f'-cipher "{cipher}"',
                success=tls1_2_enabled,
                message=f"{cipher}",
            )

    for cipher in all_ciphers:
        if cipher in fips_compatible_tlsv1_2_cipher_suites:
            continue
        with Check(
            f"connection using non-FIPS compatible cipher {cipher} should be rejected"
        ):
            openssl_client_connection(options=f'-cipher "{cipher}"', success=False)


@TestOutline
def tcp_connection_clickhouse_client(
    self, node, hostname="clickhouse1", tls1_2_enabled=True, port=None
):
    """Check that server accepts only FIPS compatible TCP connections using clickhouse-client"""
    self.context.node = node
    tls1_2_status = "work" if tls1_2_enabled else "be rejected"

    if port is None:
        port = self.context.secure_tcp_port

    with Given(
        "server is configured to accept only FIPS compatible connections",
        description=f"on port {port}",
    ):
        self.context.connection_port = port

    with Check("Connection with no protocols should be rejected"):
        output = clickhouse_client_connection(
            options={
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_2,tlsv1_3",
            },
            success=False,
            hostname=hostname,
        )
        assert (
            "NO_SUPPORTED_VERSIONS_ENABLED" or "TLSV1_ALERT_PROTOCOL_VERSION" in output
        ), error()

    with Check(f"TLSv1.2 suite connection should {tls1_2_status}"):
        clickhouse_client_connection(
            options={
                "requireTLSv1_2": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
            },
            success=tls1_2_enabled,
            hostname=hostname,
        )

    with Check("TLSv1 suite connection should be rejected"):
        clickhouse_client_connection(
            options={
                "requireTLSv1": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1_1,tlsv1_2,tlsv1_3",
            },
            success=False,
            message="TLSV1_ALERT_PROTOCOL_VERSION",
            hostname=hostname,
        )

    with Check("TLSv1.1 suite connection should be rejected"):
        clickhouse_client_connection(
            options={
                "requireTLSv1_1": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_2,tlsv1_3",
            },
            success=False,
            message="TLSV1_ALERT_PROTOCOL_VERSION",
            hostname=hostname,
        )

    with Check("TLSv1.3 suite connection should be rejected"):
        output = clickhouse_client_connection(
            options={
                "requireTLSv1_3": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_2",
            },
            success=False,
            hostname=hostname,
        )
        assert (
            "NO_SUPPORTED_VERSIONS_ENABLED" or "TLSV1_ALERT_PROTOCOL_VERSION" in output
        ), error()

    with Check(f"just disabling TLSv1 suite connection should {tls1_2_status}"):
        clickhouse_client_connection(
            options={"disableProtocols": "tlsv1"},
            success=tls1_2_enabled,
            prefer_server_ciphers=True,
            hostname=hostname,
        )

    with Check(f"just disabling TLSv1.1 suite connection should {tls1_2_status}"):
        clickhouse_client_connection(
            options={"disableProtocols": "tlsv1_1"},
            success=tls1_2_enabled,
            prefer_server_ciphers=True,
            hostname=hostname,
        )

    with Check(f"just disabling TLSv1.3 suite connection should {tls1_2_status}"):
        clickhouse_client_connection(
            options={"disableProtocols": "tlsv1_3"},
            success=tls1_2_enabled,
            prefer_server_ciphers=True,
            hostname=hostname,
        )

    for cipher in fips_compatible_tlsv1_2_cipher_suites:
        with Check(
            f"connection using FIPS compatible cipher {cipher} should {tls1_2_status}"
        ):
            clickhouse_client_connection(
                options={
                    "requireTLSv1_2": "true",
                    "cipherList": cipher,
                    "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
                },
                success=tls1_2_enabled,
                hostname=hostname,
            )

    for cipher in all_ciphers:
        if cipher in fips_compatible_tlsv1_2_cipher_suites:
            continue
        with Check(
            f"connection using non-FIPS compatible cipher {cipher} should be rejected"
        ):
            output = clickhouse_client_connection(
                options={"cipherList": cipher, "disableProtocols": ""},
                success=False,
                hostname=hostname,
            )
            assert (
                "NO_CIPHERS_AVAILABLE" or "SSLV3_ALERT_HANDSHAKE_FAILURE" in output
            ), error()


@TestOutline
def server_https_connection_curl(self, port=None, tls1_2_enabled=True):
    """Check that server accepts only FIPS compatible HTTPS connections using curl."""
    tls1_2_status = "work" if tls1_2_enabled else "be rejected"
    if port is None:
        port = self.context.secure_http_port

    with Given(
        "server is configured to accept only FIPS compatible connections",
        description=f"on port {port}",
    ):
        self.context.connection_port = port

    with Check(f"TLSv1.2 suite connection should {tls1_2_status}"):
        curl_client_connection(
            options="--tls-max 1.2 --tlsv1.2",
            success=tls1_2_enabled,
            message="SSL connection using TLSv1.2 / ECDHE-RSA-AES128-GCM-SHA256",
        )

    with Check("TLSv1 suite connection should be rejected"):
        curl_client_connection(
            options="--tls-max 1 --tlsv1",
            success=False,
        )

    with Check("TLSv1.1 suite connection should be rejected"):
        curl_client_connection(
            options="--tls-max 1.1 --tlsv1.1",
            success=False,
        )

    with Check("TLSv1.3 suite connection should be rejected"):
        curl_client_connection(
            options="--tls-max 1.3 --tlsv1.3",
            success=False,
        )

    with Check(f"just disabling TLSv1 suite connection should {tls1_2_status}"):
        curl_client_connection(options="--tlsv1.1", success=tls1_2_enabled)

    with Check(f"just disabling TLSv1.1 suite connection should {tls1_2_status}"):
        curl_client_connection(options="--tlsv1.2", success=tls1_2_enabled)

    with Check(f"just disabling TLSv1.3 suite connection should {tls1_2_status}"):
        curl_client_connection(options="--tls-max 1.2", success=tls1_2_enabled)

    for cipher in fips_compatible_tlsv1_2_cipher_suites:
        with Check(
            f"connection using FIPS compatible cipher {cipher} should {tls1_2_status}"
        ):
            curl_client_connection(
                options=f'--ciphers "{cipher}" --tls-max 1.2 --tlsv1.2',
                success=tls1_2_enabled,
                message=f"{cipher}",
            )

    for cipher in all_ciphers:
        if cipher in fips_compatible_tlsv1_2_cipher_suites:
            continue
        with Check(
            f"connection using non-FIPS compatible cipher {cipher} should be rejected"
        ):
            curl_client_connection(options=f'--ciphers "{cipher}"', success=False)


@TestScenario
@Name("log check")
@Requirements(RQ_SRS_017_ClickHouse_SSL_Server_FIPS_Mode_LogMessage("1.0"))
def log_check(self):
    """Check the server log to ensure ClickHouse is running in FIPS mode."""
    exitcode = self.context.node.command(
        "cat /var/log/clickhouse-server/clickhouse-server.log | grep '<Information> Application: Starting in FIPS mode, KAT test result: 1' > /dev/null"
    ).exitcode
    assert exitcode == 0, error()


@TestScenario
@Name("check build options")
@Requirements(
    RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_SystemTable_BuildOptions("1.0")
)
def build_options_check(self):
    """Check that system.build_options shows that ClickHouse was built using FIPs compliant BoringSSL library."""
    xfail("No mention of FIPS mode in build options")

    with When("I read the system.build_options table"):
        output = node.query("SELECT * FROM system.build_options").output

    with Then("I check that FIPS mode is present"):
        assert "FIPS" in output, error()


@TestScenario
@Name("break hash")
def break_hash(self):
    """Check that when break_hash.go is run on the binary, it fails the integrity check."""
    xfail("Binary does not have the section necessary for break-hash")
    self.context.cluster.command(None, "ls")
    try:
        with Given("I apply break-hash to the clickhouse binary"):
            self.context.cluster.command(
                None,
                f"./test_files/break-hash '{self.context.cluster.clickhouse_binary_path}' 'clickhouse-broken-binary'",
            )

        with When(f"I try to start the broken clickhouse binary"):
            output = self.context.cluster.command(
                None, f"./clickhouse-broken-binary server"
            ).output
            assert "FIPS integrity test failed." in output, error()

    finally:
        with Finally("I remove the broken clickhouse binary"):
            self.context.cluster.command(None, "rm clickhouse-broken-binary")


@TestScenario
def user_certificate_authentication(self, node=None):
    """Check that user is able to be authenticated using certificate rather than password."""
    if node is None:
        node = self.context.node
    user_name = "user_" + getuid()

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


@TestFeature
@Name("tcp connection")
@Requirements()
def server_tcp_connection(self, tls1_2_enabled=True):
    """Check that server accepts only FIPS compatible secure TCP connections."""
    # FIXME: don't use inline scenarios
    with Scenario("openssl s_client"):
        server_connection_openssl_client(
            port=self.context.secure_tcp_port, tls1_2_enabled=tls1_2_enabled
        )

    with Scenario(
        name="fips clickhouse client",
        requirements=[
            RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_Clients_SSL_TCP_ClickHouseClient_FIPS(
                "1.0"
            )
        ],
    ):
        tcp_connection_clickhouse_client(
            node=self.context.cluster.node("clickhouse1"),
            port=self.context.secure_tcp_port,
            tls1_2_enabled=tls1_2_enabled,
        )

    with Scenario(
        name="non fips clickhouse client",
        requirements=[
            RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_Clients_SSL_TCP_ClickHouseClient_NonFIPS(
                "1.0"
            )
        ],
    ):
        node = self.context.cluster.node("non_fips_clickhouse")
        add_trusted_ca_certificate(
            node=node, certificate=current().context.my_own_ca_crt
        )
        tcp_connection_clickhouse_client(
            node=node, port=self.context.secure_tcp_port, tls1_2_enabled=tls1_2_enabled
        )


@TestFeature
@Name("https connection")
@Requirements()
def server_https_connection(self, tls1_2_enabled=True):
    """Check that server accepts only FIPS compatible HTTPS connections."""
    with Scenario("openssl s_client"):
        server_connection_openssl_client(
            port=self.context.secure_http_port, tls1_2_enabled=tls1_2_enabled
        )

    with Scenario("curl"):
        server_https_connection_curl(tls1_2_enabled=tls1_2_enabled)


@TestFeature
@Name("all protocols disabled")
@Requirements()
def server_all_protocols_disabled(self):
    """Check that the server accepts no connections."""
    with Given("I set SSL server to not accept any connections"):
        entries = define(
            "SSL settings",
            {"disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_2,tlsv1_3"},
        )

    with And("I apply SSL server configuration"):
        add_ssl_server_configuration_file(
            entries=entries, config_file="ssl_disable_connections.xml", restart=True
        )

    Feature(test=server_tcp_connection)(tls1_2_enabled=False)
    Feature(test=server_https_connection)(tls1_2_enabled=False)


@TestOutline
def server_verification_mode(self, mode):
    """Check that server runs correctly with different verification modes"""
    with Given("I set SSL server to accept only FIPS compatible connections"):
        entries = define(
            "SSL settings",
            {"verificationMode": mode},
        )

    with And("I apply SSL server configuration"):
        add_ssl_server_configuration_file(
            entries=entries, config_file="ssl_verification_mode.xml", restart=True
        )

    Feature(run=server_tcp_connection)
    Feature(run=server_https_connection)


@TestFeature
@Requirements()
def server(self, node=None):
    """Check forcing server to use only FIPS compatible cipher suites."""
    if node is None:
        node = self.context.node

    with Given("I set SSL server to accept only FIPS compatible connections"):
        entries = define(
            "SSL settings",
            {
                "cipherList": ":".join(
                    [v for v in fips_compatible_tlsv1_2_cipher_suites]
                ),
                "preferServerCiphers": "true",
                "requireTLSv1_2": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
            },
        )

    with And("I apply SSL server configuration"):
        add_ssl_server_configuration_file(
            entries=entries, config_file="ssl_cipher_list.xml", restart=True
        )

    Feature(run=server_tcp_connection)
    Feature(run=server_https_connection)
    Feature(run=server_all_protocols_disabled)

    for mode in ["relaxed", "strict", "once"]:
        with Feature(f"{mode} verification mode"):
            server_verification_mode(mode=mode)


@TestFeature
@Requirements()
def clickhouse_client(self):
    """Check forcing client to use only FIPS compatible cipher suites to connect to non FIPS server."""
    # FIXME: two features one running against locked-down server and one that is not locked down.
    # FIXME: features when using non-fips client
    Scenario("fips clickhouse client", test=tcp_connection_clickhouse_client)(
        node=self.context.cluster.node("clickhouse1"),
        port=self.context.secure_tcp_port,
    )

    Scenario("user authentication using certificate", run=user_certificate_authentication):
        

@TestFeature
@Name("fips check")
@Requirements()
def fips_check(self):
    """Run checks that ClickHouse is in FIPS mode."""
    Scenario(run=log_check)
    Scenario(run=build_options_check)


@TestFeature
@Name("fips")
@Requirements()
def feature(self, node="clickhouse1"):
    """Check using SSL configuration to force only FIPS compatible SSL connections."""
    self.context.node = self.context.cluster.node(node)

    with Given("I enable SSL"):
        enable_ssl(my_own_ca_key_passphrase="", server_key_passphrase="")

    if self.context.fips_mode:
        Feature(run=fips_check)
        Scenario(run=break_hash)

    Feature(run=server)
    Feature(run=clickhouse_client)
