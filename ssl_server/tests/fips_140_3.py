from testflows.core import *

from ssl_server.tests.common import *
from ssl_server.tests.ssl_context import enable_ssl
from ssl_server.requirements import *
from clickhouse_keeper.tests.common import (
    flask_server,
    test_https_connection_with_url_table_function,
    test_https_connection_with_dictionary,
)


@TestOutline
def server_connection_openssl_client(self, port, tls_enabled=True):
    """Check that server accepts only FIPS 140-3 compatible secure connections on a given port
    using openssl s_client utility."""
    self.context.connection_port = port
    tls_status = "work" if tls_enabled else "be rejected"

    hostname = self.context.node.name
    bash_tools = self.context.cluster.node("bash-tools")

    with Given(
        "server is configured to accept only FIPS 140-3 compatible connections",
        description=f"on port {port}",
    ):
        pass

    with Check("Connection with no protocols should be rejected"):
        openssl_client_connection(
            options="-no_tls1 -no_tls1_1 -no_tls1_2 -no_tls1_3",
            success=False,
            message="no protocols available",
            node=bash_tools,
            hostname=hostname,
        )

    with Check(f"TLSv1_2 suite connection should {tls_status}"):
        openssl_client_connection(
            options="-tls1_2",
            success=tls_enabled,
            node=bash_tools,
            hostname=hostname,
        )

    with Check(f"TLSv1_3 suite connection should {tls_status}"):
        openssl_client_connection(
            options="-tls1_3",
            success=tls_enabled,
            node=bash_tools,
            hostname=hostname,
        )

    with Check("TLSv1 suite connection should be rejected"):
        openssl_client_connection(
            options="-tls1",
            success=False,
            message="no protocols available",
            node=bash_tools,
            hostname=hostname,
        )

    with Check("TLSv1_1 suite connection should be rejected"):
        openssl_client_connection(
            options="-tls1_1",
            success=False,
            message="no protocols available",
            node=bash_tools,
            hostname=hostname,
        )

    with Check("any DTLS suite connection should be rejected"):
        openssl_client_connection(
            options="-dtls", success=False, node=bash_tools, hostname=hostname
        )

    with Check("DTLSv1 suite connection should be rejected"):
        openssl_client_connection(
            options="-dtls1", success=False, node=bash_tools, hostname=hostname
        )

    with Check("DTLSv1_2 suite connection should be rejected"):
        openssl_client_connection(
            options="-dtls1.2", success=False, node=bash_tools, hostname=hostname
        )

    with Check("just disabling"):
        with Check(f"TLSv1, suite connection should {tls_status}"):
            openssl_client_connection(
                options="-no_tls1",
                success=tls_enabled,
                node=bash_tools,
                hostname=hostname,
            )

        with Check(f"TLSv1_1, suite connection should {tls_status}"):
            openssl_client_connection(
                options="-no_tls1_1",
                success=tls_enabled,
                node=bash_tools,
                hostname=hostname,
            )

        with Check(f"TLSv1_3 only, suite connection should {tls_status}"):
            openssl_client_connection(
                options="-no_tls1_3",
                success=tls_enabled,
                node=bash_tools,
                hostname=hostname,
            )

        with Check(f"TLSv1_2 only, suite connection should {tls_status}"):
            openssl_client_connection(
                options="-no_tls1_2",
                success=tls_enabled,
                node=bash_tools,
                hostname=hostname,
            )

    with Check(
        "disabling both TLSv1_2 and TLSv1_3 suite connection should be rejected"
    ):
        openssl_client_connection(
            options="-no_tls1_2 -no_tls1_3",
            success=False,
            node=bash_tools,
            hostname=hostname,
        )

    for cipher in fips_140_3_compatible_tlsv1_2_cipher_suites:
        with Check(
            f"connection using FIPS compatible TLSv1.2 cipher {cipher} should {tls_status}"
        ):
            openssl_client_connection(
                options=f'-cipher "{cipher}" -tls1_2',
                success=tls_enabled,
                node=bash_tools,
                hostname=hostname,
            )

    for cipher in all_ciphers:
        if cipher in fips_140_3_compatible_tlsv1_2_cipher_suites:
            continue
        if cipher.startswith("TLS_"):
            continue
        with Check(
            f"connection using non-FIPS compatible TLSv1.2 cipher {cipher} should be rejected"
        ):
            openssl_client_connection(
                options=f'-cipher "{cipher}" -tls1_2',
                success=False,
                node=bash_tools,
                hostname=hostname,
            )

    for cipher in fips_140_3_compatible_tlsv1_3_cipher_suites:
        with Check(
            f"connection using FIPS compatible TLSv1.3 cipher {cipher} should {tls_status}"
        ):
            openssl_client_connection(
                options=f'-ciphersuites "{cipher}" -tls1_3',
                success=tls_enabled,
                node=bash_tools,
                hostname=hostname,
            )

    for cipher in all_tlsv1_3_ciphers:
        if cipher in fips_140_3_compatible_tlsv1_3_cipher_suites:
            continue
        with Check(
            f"connection using non-FIPS compatible TLSv1.3 cipher {cipher} should be rejected"
        ):
            openssl_client_connection(
                options=f'-ciphersuites "{cipher}" -tls1_3',
                success=False,
                node=bash_tools,
                hostname=hostname,
            )


@TestOutline
def tcp_connection_clickhouse_client(
    self, node, hostname="clickhouse1", tls_enabled=True, port=None
):
    """Check that server accepts only FIPS 140-3 compatible TCP connections using clickhouse-client."""
    self.context.node = node
    tls_status = "work" if tls_enabled else "be rejected"

    if port is None:
        port = self.context.secure_tcp_port

    with Given(
        "server is configured to accept only FIPS 140-3 compatible connections",
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
            "NO_SUPPORTED_VERSIONS_ENABLED" in output
            or "TLSV1_ALERT_PROTOCOL_VERSION" in output
        ), error()

    with Check(f"TLSv1_2 suite connection should {tls_status}"):
        clickhouse_client_connection(
            options={
                "requireTLSv1_2": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
            },
            success=tls_enabled,
            hostname=hostname,
        )

    with Check(f"TLSv1_3 suite connection should {tls_status}"):
        clickhouse_client_connection(
            options={
                "requireTLSv1_3": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_2",
            },
            success=tls_enabled,
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

    with Check("TLSv1_1 suite connection should be rejected"):
        clickhouse_client_connection(
            options={
                "requireTLSv1_1": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_2,tlsv1_3",
            },
            success=False,
            hostname=hostname,
        )

    with Check(f"just disabling TLSv1 suite connection should {tls_status}"):
        clickhouse_client_connection(
            options={"disableProtocols": "tlsv1"},
            success=tls_enabled,
            prefer_server_ciphers=True,
            hostname=hostname,
        )

    with Check(f"just disabling TLSv1_1 suite connection should {tls_status}"):
        clickhouse_client_connection(
            options={"disableProtocols": "tlsv1_1"},
            success=tls_enabled,
            prefer_server_ciphers=True,
            hostname=hostname,
        )

    with Check(f"just disabling TLSv1_3 suite connection should {tls_status}"):
        clickhouse_client_connection(
            options={"disableProtocols": "tlsv1_3"},
            success=tls_enabled,
            prefer_server_ciphers=True,
            hostname=hostname,
        )

    with Check(f"just disabling TLSv1_2 suite connection should {tls_status}"):
        clickhouse_client_connection(
            options={"disableProtocols": "tlsv1_2"},
            success=tls_enabled,
            prefer_server_ciphers=True,
            hostname=hostname,
        )

    for cipher in fips_140_3_compatible_tlsv1_2_cipher_suites:
        with Check(
            f"connection using FIPS compatible cipher {cipher} should {tls_status}"
        ):
            clickhouse_client_connection(
                options={
                    "requireTLSv1_2": "true",
                    "cipherList": cipher,
                    "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
                },
                success=tls_enabled,
                hostname=hostname,
            )

    for cipher in all_ciphers:
        if cipher in fips_140_3_compatible_tlsv1_2_cipher_suites:
            continue
        if cipher.startswith("TLS_"):
            continue
        with Check(
            f"connection using non-FIPS compatible cipher {cipher} should be rejected"
        ):
            output = clickhouse_client_connection(
                options={
                    "cipherList": cipher,
                    "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
                },
                success=False,
                hostname=hostname,
            )
            assert (
                "NO_CIPHERS_AVAILABLE" in output
                or "SSLV3_ALERT_HANDSHAKE_FAILURE" in output
            ), error()

    for cipher in fips_140_3_compatible_tlsv1_3_cipher_suites:
        with Check(
            f"connection using FIPS compatible TLSv1.3 cipher {cipher} should {tls_status}"
        ):
            clickhouse_client_connection(
                options={
                    "requireTLSv1_3": "true",
                    "cipherSuites": cipher,
                    "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_2",
                },
                success=tls_enabled,
                hostname=hostname,
            )

    for cipher in all_tlsv1_3_ciphers:
        if cipher in fips_140_3_compatible_tlsv1_3_cipher_suites:
            continue
        with Check(
            f"connection using non-FIPS compatible TLSv1.3 cipher {cipher} should be rejected"
        ):
            clickhouse_client_connection(
                options={
                    "requireTLSv1_3": "true",
                    "cipherSuites": cipher,
                    "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_2",
                },
                success=False,
                hostname=hostname,
            )


@TestOutline
def server_https_connection_curl(self, port=None, tls_enabled=True):
    """Check that server accepts only FIPS 140-3 compatible HTTPS connections using curl."""
    tls_status = "work" if tls_enabled else "be rejected"
    if port is None:
        port = self.context.secure_http_port

    with Given(
        "server is configured to accept only FIPS 140-3 compatible connections",
        description=f"on port {port}",
    ):
        self.context.connection_port = port

    with Check(f"TLSv1_2 suite connection should {tls_status}"):
        curl_client_connection(
            options="--tls-max 1.2 --tlsv1.2",
            success=tls_enabled,
        )

    with Check(f"TLSv1_3 suite connection should {tls_status}"):
        curl_client_connection(
            options="--tls-max 1.3 --tlsv1.3",
            success=tls_enabled,
        )

    with Check("TLSv1 suite connection should be rejected"):
        curl_client_connection(
            options="--tls-max 1 --tlsv1",
            success=False,
        )

    with Check("TLSv1_1 suite connection should be rejected"):
        curl_client_connection(
            options="--tls-max 1.1 --tlsv1.1",
            success=False,
        )

    with Check("just disabling"):
        with Check(f"TLSv1, suite connection should {tls_status}"):
            curl_client_connection(options="--tlsv1.1", success=tls_enabled)

        with Check(f"TLSv1_1, suite connection should {tls_status}"):
            curl_client_connection(options="--tlsv1.2", success=tls_enabled)

        with Check(f"TLSv1_2 only, suite connection should {tls_status}"):
            curl_client_connection(
                options="--tls-max 1.2 --tlsv1.2", success=tls_enabled
            )

        with Check(f"TLSv1_3 only, suite connection should {tls_status}"):
            curl_client_connection(
                options="--tls-max 1.3 --tlsv1.3", success=tls_enabled
            )

    for cipher in fips_140_3_compatible_tlsv1_2_cipher_suites:
        with Check(
            f"connection using FIPS compatible cipher {cipher} should {tls_status}"
        ):
            curl_client_connection(
                options=f'--ciphers "{cipher}" --tls-max 1.2 --tlsv1.2',
                success=tls_enabled,
            )

    for cipher in all_ciphers:
        if cipher in fips_140_3_compatible_tlsv1_2_cipher_suites:
            continue
        if cipher.startswith("TLS_"):
            continue
        with Check(
            f"connection using non-FIPS compatible cipher {cipher} should be rejected"
        ):
            curl_client_connection(
                options=f'--ciphers "{cipher}" --tls-max 1.2', success=False
            )

    for cipher in fips_140_3_compatible_tlsv1_3_cipher_suites:
        with Check(
            f"connection using FIPS compatible TLSv1.3 cipher {cipher} should {tls_status}"
        ):
            curl_client_connection(
                options=f'--tls13-ciphers "{cipher}" --tls-max 1.3 --tlsv1.3',
                success=tls_enabled,
            )

    for cipher in all_tlsv1_3_ciphers:
        if cipher in fips_140_3_compatible_tlsv1_3_cipher_suites:
            continue
        with Check(
            f"connection using non-FIPS compatible TLSv1.3 cipher {cipher} should be rejected"
        ):
            curl_client_connection(
                options=f'--tls13-ciphers "{cipher}" --tls-max 1.3 --tlsv1.3',
                success=False,
            )


@TestOutline
def url_table_function(self):
    """Check that clickhouse server only makes FIPS 140-3 compatible HTTPS connections using url table function."""
    port = 5001
    default_ciphers = '"ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-GCM-SHA384"'
    server_file_path = "https_" + getuid() + ".py"
    bash_tools = self.context.cluster.node("bash-tools")

    tls_versions_supported = {
        "TLS": True,
        "TLSv1": False,
        "TLSv1.1": False,
        "TLSv1.2": True,
        "TLSv1.3": True,
    }

    with Given("I make a copy of the flask server file"):
        bash_tools.command(f"cp /https_app_file.py {server_file_path}")

    for tls_version, should_work in tls_versions_supported.items():
        with Check(
            f"Connection with Protocol={tls_version.replace('.', '_')} should be {'accepted' if should_work else 'rejected'}"
        ):
            flask_server(
                server_path=server_file_path,
                port=port,
                protocol=tls_version,
                ciphers=default_ciphers,
            )

            test_https_connection_with_url_table_function(
                port=port, success=should_work
            )

    for cipher in fips_140_3_compatible_tlsv1_2_cipher_suites:
        with Check(f"connection using FIPS compatible cipher {cipher} should work"):
            flask_server(
                server_path=server_file_path,
                port=port,
                protocol="TLSv1.2",
                ciphers=default_ciphers,
            )

            test_https_connection_with_url_table_function(port=port, success=True)

        for second_cipher in all_ciphers:
            if second_cipher.startswith("TLS_"):
                continue
            with Check(
                f"connection with at least one FIPS compatible cipher should work, ciphers: {cipher}, {second_cipher}",
                description=f"ciphers: {cipher}, {second_cipher}",
            ):
                flask_server(
                    server_path=server_file_path,
                    port=port,
                    protocol="TLSv1.2",
                    ciphers=f"{cipher}:{second_cipher}",
                )

                test_https_connection_with_url_table_function(port=port, success=True)

    for cipher in all_ciphers:
        if cipher in fips_140_3_compatible_tlsv1_2_cipher_suites:
            continue
        if cipher.startswith("TLS_"):
            continue
        with Check(
            f"connection using non-FIPS compatible cipher {cipher} should be rejected"
        ):
            flask_server(
                server_path=server_file_path,
                port=port,
                protocol="TLSv1.2",
                ciphers=cipher,
            )

            test_https_connection_with_url_table_function(port=port, success=False)

    with Finally("I remove the flask server file"):
        bash_tools.command(f"rm -f {server_file_path}")


@TestOutline
def dictionary(self):
    """Check that clickhouse server only makes FIPS 140-3 compatible HTTPS connections using a dictionary."""
    port = 5001
    default_ciphers = "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-GCM-SHA384"
    server_file_path = "https_" + getuid() + ".py"
    bash_tools = self.context.cluster.node("bash-tools")

    tls_versions_supported = {
        "TLS": True,
        "TLSv1": False,
        "TLSv1.1": False,
        "TLSv1.2": True,
        "TLSv1.3": True,
    }

    with Given("I make a copy of the flask server file"):
        bash_tools.command(f"cp /https_app_file.py {server_file_path}")

    for tls_version, should_work in tls_versions_supported.items():
        with Check(
            f"Connection with Protocol={tls_version.replace('.', '_')} should be {'accepted' if should_work else 'rejected'}"
        ):
            flask_server(
                server_path=server_file_path,
                port=port,
                protocol=tls_version,
                ciphers=default_ciphers,
            )

            test_https_connection_with_dictionary(port=port, success=should_work)

    for cipher in fips_140_3_compatible_tlsv1_2_cipher_suites:
        with Check(f"connection using FIPS compatible cipher {cipher} should work"):
            flask_server(
                server_path=server_file_path,
                port=port,
                protocol="TLSv1.2",
                ciphers=cipher,
            )

            test_https_connection_with_dictionary(port=port, success=True)

        for second_cipher in all_ciphers:
            if second_cipher.startswith("TLS_"):
                continue
            with Check(
                f"connection with at least one FIPS compatible cipher should work, ciphers: {cipher}, {second_cipher}",
                description=f"ciphers: {cipher}, {second_cipher}",
            ):
                flask_server(
                    server_path=server_file_path,
                    port=port,
                    protocol="TLSv1.2",
                    ciphers=f"{cipher}:{second_cipher}",
                )

                test_https_connection_with_dictionary(port=port, success=True)

    for cipher in all_ciphers:
        if cipher in fips_140_3_compatible_tlsv1_2_cipher_suites:
            continue
        if cipher.startswith("TLS_"):
            continue

        with Check(
            f"connection using non-FIPS compatible cipher {cipher} should be rejected"
        ):
            flask_server(
                server_path=server_file_path,
                port=port,
                protocol="TLSv1.2",
                ciphers=cipher,
            )

            test_https_connection_with_dictionary(port=port, success=False)

    with Finally("I remove the flask server file"):
        bash_tools.command(f"rm -f {server_file_path}")


@TestScenario
@Name("log check")
@Requirements(RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC("1.0"))
def log_check(self):
    """Check the server log to ensure ClickHouse is running in FIPS mode with AWS-LC."""
    exitcode = self.context.node.command(
        "cat /var/log/clickhouse-server/clickhouse-server.log"
        " | grep -i 'starting in fips mode' > /dev/null"
    ).exitcode
    assert exitcode == 0, error()


@TestScenario
@Name("check build options")
@Requirements(
    RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SystemTable_BuildOptions("1.0")
)
def build_options_check(self):
    """Check that system.build_options shows that ClickHouse was built using FIPS compliant AWS-LC library."""
    node = self.context.node
    with When("I read the system.build_options table"):
        output = node.query(
            "SELECT * FROM system.build_options FORMAT TabSeparated"
        ).output
        debug(output)

    with Then("I check that FIPS mode is present"):
        assert "fips" in output or "FIPS" in output, error()


@TestScenario
@Name("break hash")
@Requirements(RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SelfTest_IntegrityTest("1.0"))
def break_hash(self):
    """Check that when the HMAC integrity hash is broken, the module fails the integrity check."""
    xfail("Binary does not have the section necessary for break-hash")
    self.context.cluster.command(None, "ls")
    try:
        with Given("I apply break-hash to the clickhouse binary"):
            self.context.cluster.command(
                None,
                f"./test_files/break-hash '{self.context.cluster.clickhouse_path}' 'clickhouse-broken-binary'",
            )

        with When("I try to start the broken clickhouse binary"):
            output = self.context.cluster.command(
                None, "./clickhouse-broken-binary server"
            ).output
            assert "FIPS integrity test failed." in output, error()

    finally:
        with Finally("I remove the broken clickhouse binary"):
            self.context.cluster.command(None, "rm clickhouse-broken-binary")


@TestScenario
@Name("non fips clickhouse client")
@Requirements(
    RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Clients_SSL_TCP_ClickHouseClient_NonFIPS(
        "1.0"
    )
)
def non_fips_clickhouse_client(self, tls_enabled=True):
    """Check that clickhouse-client from a non-FIPS compliant build is able to connect
    to a clickhouse server using only FIPS 140-3 compliant protocols and ciphers."""
    node = self.context.cluster.node("non_fips_clickhouse")
    add_trusted_ca_certificate(node=node, certificate=current().context.my_own_ca_crt)
    tcp_connection_clickhouse_client(
        node=node, port=self.context.secure_tcp_port, tls_enabled=tls_enabled
    )


@TestScenario
@Name("fips clickhouse client")
@Requirements(
    RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Clients_SSL_TCP_ClickHouseClient_FIPS(
        "1.0"
    )
)
def fips_clickhouse_client(self, tls_enabled=True):
    """Check that clickhouse-client from a FIPS compliant build is able to connect
    to a clickhouse server using only FIPS 140-3 compliant protocols and ciphers."""
    node = self.context.cluster.node("clickhouse1")
    tcp_connection_clickhouse_client(
        node=node, port=self.context.secure_tcp_port, tls_enabled=tls_enabled
    )


@TestOutline
def clickhouse_client_tcp(self, tls_enabled=True):
    """Check clickhouse-client TCP using a client from a FIPS and a non FIPS build."""

    Scenario("fips clickhouse-client", test=fips_clickhouse_client)(
        tls_enabled=tls_enabled,
    )

    Scenario("non fips clickhouse-client", test=non_fips_clickhouse_client)(
        tls_enabled=tls_enabled,
    )


@TestFeature
@Name("tcp connection")
@Requirements()
def server_tcp_connection(self, tls_enabled=True):
    """Check that server accepts only FIPS 140-3 compatible secure TCP connections."""
    Scenario(name="openssl s_client", test=server_connection_openssl_client)(
        port=self.context.secure_tcp_port,
        tls_enabled=tls_enabled,
    )

    Feature(name="clickhouse-client", test=clickhouse_client_tcp)(
        tls_enabled=tls_enabled
    )


@TestFeature
@Name("https connection")
@Requirements()
def server_https_connection(self, tls_enabled=True):
    """Check that server accepts only FIPS 140-3 compatible HTTPS connections."""
    Scenario("openssl s_client", test=server_connection_openssl_client)(
        port=self.context.secure_http_port, tls_enabled=tls_enabled
    )
    Scenario("curl", test=server_https_connection_curl)(tls_enabled=tls_enabled)


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

    Feature(test=server_tcp_connection)(tls_enabled=False)
    Feature(test=server_https_connection)(tls_enabled=False)


@TestFeature
@Requirements()
def server(self, node=None):
    """Check forcing server to use only FIPS 140-3 compatible cipher suites."""
    if node is None:
        node = self.context.node

    with Given("I set SSL server to accept only FIPS 140-3 compatible connections"):
        entries = define(
            "SSL settings",
            {
                "cipherList": ":".join(fips_140_3_compatible_tlsv1_2_cipher_suites),
                "cipherSuites": ":".join(fips_140_3_compatible_tlsv1_3_cipher_suites),
                "preferServerCiphers": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1",
            },
        )

    with And("I apply SSL server configuration"):
        add_ssl_server_configuration_file(
            entries=entries, config_file="ssl_cipher_list.xml", restart=True
        )

    Feature(run=server_tcp_connection)
    Feature(run=server_https_connection)
    Feature(run=server_all_protocols_disabled)


@TestFeature
@Name("clickhouse client")
@Requirements()
def clickhouse_client(self):
    """Check forcing clickhouse-client to use only FIPS 140-3 compatible cipher suites
    to connect to server which is not configured to limit cipher suites."""
    Feature(
        name="clickhouse-client with non restricted server", run=clickhouse_client_tcp
    )

    with Given("I set SSL server to accept only FIPS 140-3 compatible connections"):
        entries = define(
            "SSL settings",
            {
                "cipherList": ":".join(fips_140_3_compatible_tlsv1_2_cipher_suites),
                "cipherSuites": ":".join(fips_140_3_compatible_tlsv1_3_cipher_suites),
                "preferServerCiphers": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1",
            },
        )

    with And("I apply SSL server configuration"):
        add_ssl_server_configuration_file(
            entries=entries, config_file="ssl_cipher_list.xml", restart=True
        )

    Feature(name="clickhouse-client with restricted server", run=clickhouse_client_tcp)


@TestFeature
@Name("fips check")
@Requirements()
def fips_check(self):
    """Run checks that ClickHouse is in FIPS 140-3 mode."""
    Scenario(run=log_check)
    Scenario(run=build_options_check)


@TestFeature
@Name("clickhouse server acting as a client")
@Requirements(RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SSL_Client_Config("1.0"))
def server_as_client(self):
    """Check connections from clickhouse-server when it is acting as a client
    and configured using openSSL client configs."""
    node = self.context.node

    with Given("I set SSL client to accept only FIPS 140-3 compatible connections"):
        entries = define(
            "SSL settings",
            {
                "cipherList": ":".join(fips_140_3_compatible_tlsv1_2_cipher_suites),
                "cipherSuites": ":".join(fips_140_3_compatible_tlsv1_3_cipher_suites),
                "preferServerCiphers": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1",
            },
        )

    with And("I apply SSL client configuration"):
        add_ssl_client_configuration_file(
            entries=entries, config_file="ssl_cipher_list.xml", restart=True
        )

    with Given("I generate private key and certificate for https server"):
        bash_tools = self.context.cluster.node("bash-tools")
        ca_cert = add_trusted_ca_certificate(
            node=bash_tools, certificate=self.context.my_own_ca_crt
        )
        create_crt_and_key(
            name="https_server",
            common_name="bash-tools",
            node=bash_tools,
            node_ca_crt=ca_cert,
        )

    Feature(run=url_table_function)
    Feature(run=dictionary)


@TestFeature
@Name("fips 140-3")
@Requirements()
def feature(self, node="clickhouse1"):
    """Check using SSL configuration to force only FIPS 140-3 compatible SSL connections
    using AWS-LC cryptographic module."""
    self.context.node = self.context.cluster.node(node)

    with Given("I enable SSL"):
        enable_ssl(my_own_ca_key_passphrase="", server_key_passphrase="")

    if self.context.fips_mode:
        Feature(run=fips_check)
        Scenario(run=break_hash)

    Feature(run=server)
    Feature(run=clickhouse_client)
    Feature(run=server_as_client)
