from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps_ssl_fips import *
from clickhouse_keeper.tests.steps import *
from helpers.common import *

fips_compatible_tlsv1_2_cipher_suites = [
    "ECDHE-RSA-AES128-GCM-SHA256",
    "ECDHE-RSA-AES256-GCM-SHA384",
    # "ECDHE-ECDSA-AES128-GCM-SHA256",
    # "ECDHE-ECDSA-AES256-GCM-SHA384",
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
        openssl_client_connection(options="-tls1_3", success=False)

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
            )

    for cipher in all_ciphers:
        if cipher in fips_compatible_tlsv1_2_cipher_suites:
            continue
        with Check(
            f"connection using non-FIPS compatible cipher {cipher} should be rejected"
        ):
            openssl_client_connection(options=f'-cipher "{cipher}"', success=False)


@TestFeature
def openssl_check(self, node=None):
    """Check ClickHouse connection on all ports is ssl."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)

    ports_list = define(
        "All ports for testing", ["9440", "9281", "9010", "9444", "8443"]
    )

    for port in ports_list:
        with Check(f"port:{port}"):
            server_connection_openssl_client(port=port)


@TestOutline
def tcp_connection_clickhouse_client(
    self, hostname="clickhouse1", tls1_2_enabled=True, port=None
):
    """Check that server accepts only FIPS compatible TCP connections using clickhouse-client."""

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


@TestFeature
def tcp_connection_check(self, node=None):
    """Check Clickhouse Keeper FIPS compatible TCP connections."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)

    ports_list = define("All ports for testing", ["9440"])

    for port in ports_list:
        with Check(f"port:{port}"):
            tcp_connection_clickhouse_client(port=port)


@TestFeature
@Name("FIPS SSL server")
def feature(self):
    """Clickhouse Keeper FIPS is using the correct cyphers, and FIPS has compatible TCP connections."""
    cluster = self.context.cluster

    start_mixed_keeper_ssl(
        cluster_nodes=cluster.nodes["clickhouse"][:9],
        control_nodes=cluster.nodes["clickhouse"][0:3],
        rest_cluster_nodes=cluster.nodes["clickhouse"][3:9],
    )

    with Pool(1) as executor:
        try:
            for feature in loads(current_module(), Feature):
                if not feature.name.endswith("FIPS SSL server"):
                    Feature(test=feature, parallel=True, executor=executor)()
        finally:
            join()

    with Pool(1) as executor:
        try:
            for scenario in loads(current_module(), Scenario):
                Feature(test=scenario, parallel=True, executor=executor)()
        finally:
            join()
