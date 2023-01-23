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
def server_connection_openssl_client(self, port):
    """Check that server accepts only FIPS compatible secure connections on a given port
    using openssl s_client utility."""
    self.context.connection_port = port

    with Given(
        "server is configured to accept only FIPS compatible connections",
        description=f"on port {port}",
    ):
        pass

    with Check("Connection with no protocols should be rejected"):
        openssl_client_connection(
            options="-no_tls1 -no_tls1_1 -no_tls1_2 -no_tls1_3",
            success=False,
        )

    with Check(f"TLSv1.2 suite connection should work"):
        openssl_client_connection(options="-tls1_2", success=True)

    with Check("TLSv1 suite connection should be rejected"):
        openssl_client_connection(
            options="-tls1", success=False
        )

    with Check("TLSv1.1 suite connection should be rejected"):
        openssl_client_connection(
            options="-tls1_1", success=False
        )

    with Check("TLSv1.3 suite connection should be rejected"):
        openssl_client_connection(
            options="-tls1_3", success=False
        )

    with Check("any DTLS suite connection should be rejected"):
        openssl_client_connection(options="-dtls", success=False)

    with Check("DTLSv1 suite connection should be rejected"):
        openssl_client_connection(options="-dtls1", success=False)

    with Check("DTLSv1.2 suite connection should be rejected"):
        openssl_client_connection(options="-dtls1.2", success=False)

    with Check(f"just disabling TLSv1 suite connection should work"):
        openssl_client_connection(options="-no_tls1", success=True)

    with Check(f"just disabling TLSv1.1 suite connection should work"):
        openssl_client_connection(options="-no_tls1_1", success=True)

    with Check(f"just disabling TLSv1.3 suite connection should work"):
        openssl_client_connection(options="-no_tls1_3", success=True)

    with Check("disabling TLSv1.2 suite connection should be rejected"):
        openssl_client_connection(options="-no_tls1_2", success=False)

    for cipher in fips_compatible_tlsv1_2_cipher_suites:
        with Check(
            f"connection using FIPS compatible cipher {cipher} should work"
        ):
            openssl_client_connection(
                options=f'-cipher "{cipher}"',
                success=True,
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
    self, hostname="clickhouse1", port=None
):
    """Check that server accepts only FIPS compatible TCP connections using clickhouse-client"""
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

    with Check(f"TLSv1.2 suite connection should work"):
        clickhouse_client_connection(
            options={
                "requireTLSv1_2": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
            },
            success=True,
            hostname=hostname,
        )

    with Check("TLSv1 suite connection should be rejected"):
        clickhouse_client_connection(
            options={
                "requireTLSv1": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1_1,tlsv1_2,tlsv1_3",
            },
            success=False,
            hostname=hostname,
        )

    with Check("TLSv1.1 suite connection should be rejected"):
        clickhouse_client_connection(
            options={
                "requireTLSv1_1": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_2,tlsv1_3",
            },
            success=False,
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

    with Check(f"just disabling TLSv1 suite connection should work"):
        clickhouse_client_connection(
            options={"disableProtocols": "tlsv1"},
            success=True,
            prefer_server_ciphers=True,
            hostname=hostname,
        )

    with Check(f"just disabling TLSv1.1 suite connection should work"):
        clickhouse_client_connection(
            options={"disableProtocols": "tlsv1_1"},
            success=True,
            prefer_server_ciphers=True,
            hostname=hostname,
        )

    with Check(f"just disabling TLSv1.3 suite connection should work"):
        clickhouse_client_connection(
            options={"disableProtocols": "tlsv1_3"},
            success=True,
            prefer_server_ciphers=True,
            hostname=hostname,
        )

    for cipher in fips_compatible_tlsv1_2_cipher_suites:
        with Check(
            f"connection using FIPS compatible cipher {cipher} should work"
        ):
            clickhouse_client_connection(
                options={
                    "requireTLSv1_2": "true",
                    "cipherList": cipher,
                    "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
                },
                success=True,
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
def server_https_connection_curl(self, port=None):
    """Check that server accepts only FIPS compatible HTTPS connections using curl."""
    if port is None:
        port = self.context.secure_http_port

    with Given(
        "server is configured to accept only FIPS compatible connections",
        description=f"on port {port}",
    ):
        self.context.connection_port = port

    with Check(f"TLSv1.2 suite connection should work"):
        curl_client_connection(
            options="--tls-max 1.2 --tlsv1.2",
            success=True,
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

    with Check(f"just disabling TLSv1 suite connection should work"):
        curl_client_connection(options="--tlsv1.1", success=True)

    with Check(f"just disabling TLSv1.1 suite connection should work"):
        curl_client_connection(options="--tlsv1.2", success=True)

    with Check(f"just disabling TLSv1.3 suite connection should work"):
        curl_client_connection(options="--tls-max 1.2", success=True)

    for cipher in fips_compatible_tlsv1_2_cipher_suites:
        with Check(
            f"connection using FIPS compatible cipher {cipher} should work"
        ):
            curl_client_connection(
                options=f'--ciphers "{cipher}" --tls-max 1.2 --tlsv1.2',
                success=True,
            )

    for cipher in all_ciphers:
        if cipher in fips_compatible_tlsv1_2_cipher_suites:
            continue
        with Check(
            f"connection using non-FIPS compatible cipher {cipher} should be rejected"
        ):
            curl_client_connection(options=f'--ciphers "{cipher}"', success=False)


@TestFeature
@Name("tcp connection")
@Requirements()
def server_tcp_connection(self):
    """Check that server accepts only FIPS compatible secure TCP connections."""
    Scenario(name="openssl s_client", test=server_connection_openssl_client)(
        port=self.context.secure_tcp_port,
    )

    Scenario(name="clickhouse client", test=tcp_connection_clickhouse_client)(
        port=self.context.secure_tcp_port,
    )


@TestFeature
@Name("https connection")
@Requirements()
def server_https_connection(self):
    """Check that server accepts only FIPS compatible HTTPS connections."""
    Scenario("openssl s_client", test=server_connection_openssl_client)(
        port=self.context.secure_http_port,
    )

    Scenario("curl", run=server_https_connection_curl)


@TestFeature
@Name("none")
@Requirements(
    RQ_SRS_017_ClickHouse_SSL_Server_Certificates_VerificationMode_None("1.0")
)
def none(self):

    with Given("I set SSL server to accept only FIPS compatible connections"):
        entries = define(
            "SSL settings",
            {
                "verificationMode": "none",
            },
        )

    with And("I apply SSL server configuration"):
        add_ssl_server_configuration_file(
            entries=entries, config_file="ssl_verification_mode.xml", restart=True
        )

    Feature(run=server_tcp_connection)
    Feature(run=server_https_connection)


@TestFeature
@Name("once")
@Requirements(
    RQ_SRS_017_ClickHouse_SSL_Server_Certificates_VerificationMode_Once("1.0")
)
def once(self):
    with Given("I set SSL server to accept only FIPS compatible connections"):
        entries = define(
            "SSL settings",
            {
                "verificationMode": "once",
            },
        )

    with And("I apply SSL server configuration"):
        add_ssl_server_configuration_file(
            entries=entries, config_file="ssl_verification_mode.xml", restart=True
        )

    Feature(run=server_tcp_connection)
    Feature(run=server_https_connection)


@TestFeature
@Name("relaxed")
@Requirements(
    RQ_SRS_017_ClickHouse_SSL_Server_Certificates_VerificationMode_Relaxed("1.0")
)
def relaxed(self):
    with Given("I set SSL server to accept only FIPS compatible connections"):
        entries = define(
            "SSL settings",
            {
                "verificationMode": "relaxed",
            },
        )

    with And("I apply SSL server configuration"):
        add_ssl_server_configuration_file(
            entries=entries, config_file="ssl_verification_mode.xml", restart=True
        )

    Feature(run=server_tcp_connection)
    Feature(run=server_https_connection)


@TestFeature
@Name("strict")
@Requirements(
    RQ_SRS_017_ClickHouse_SSL_Server_Certificates_VerificationMode_Strict("1.0")
)
def strict(self):
    with Given("I set SSL server to accept only FIPS compatible connections"):
        entries = define(
            "SSL settings",
            {
                "verificationMode": "strict",
            },
        )

    with And("I apply SSL server configuration"):
        add_ssl_server_configuration_file(
            entries=entries, config_file="ssl_verification_mode.xml", restart=True
        )

    Feature(run=server_tcp_connection)
    Feature(run=server_https_connection)


@TestFeature
@Name("verification modes")
@Requirements(RQ_SRS_017_ClickHouse_SSL_Server_Certificates_VerificationMode("1.0"))
def feature(self, node="clickhouse1"):
    """Check SSL connection to the clickhouse server with different verification modes."""
    self.context.node = self.context.cluster.node(node)

    with Given("I enable SSL"):
        enable_ssl(my_own_ca_key_passphrase="", server_key_passphrase="")

    Feature(run=none)
    Feature(run=once)
    Feature(run=relaxed)
    Feature(run=strict)
