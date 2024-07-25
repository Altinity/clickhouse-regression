from testflows.core import *

from clickhouse_keeper.tests.common import *
from clickhouse_keeper.tests.ssl_context import enable_ssl
from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *


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

    with Check("connection with no protocols should be rejected"):
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

    with Check("connection with no protocols should be rejected"):
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
            )

    for cipher in all_ciphers:
        if cipher in fips_compatible_tlsv1_2_cipher_suites:
            continue
        with Check(
            f"connection using non-FIPS compatible cipher {cipher} should be rejected"
        ):
            curl_client_connection(options=f'--ciphers "{cipher}"', success=False)


@TestOutline
def url_table_function(self):
    """Check that clickhouse server only makes FIPS compatible HTTPS connections using url table function."""
    port = 5001
    default_ciphers = '"ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-GCM-SHA384"'
    server_file_path = "https_" + getuid() + ".py"
    node = self.context.node

    tls_versions_supported = {
        "TLS": True,
        "TLSv1": False,
        "TLSv1.1": False,
        "TLSv1.2": True,
    }

    with Given("I make a copy of the flask server file"):
        node.command(f"cp /https_app_file.py {server_file_path}")

    for tls_version, should_work in tls_versions_supported.items():
        with Check(
            f"connection with Protocol={tls_version} should be {'accepted' if should_work else 'rejected'}"
        ):
            flask_server(
                server_path=server_file_path,
                port=port,
                protocol=tls_version,
                ciphers=default_ciphers,
            )

            test_https_connection_with_url_table_function(
                port=port, success=should_work, timeout=5
            )

    for cipher in fips_compatible_tlsv1_2_cipher_suites:
        with Check(f"connection using FIPS compatible cipher {cipher} should work"):
            flask_server(
                server_path=server_file_path,
                port=port,
                protocol="TLSv1.2",
                ciphers=default_ciphers,
            )

            test_https_connection_with_url_table_function(
                port=port, success=True, timeout=5
            )

        for second_cipher in all_ciphers:
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

                test_https_connection_with_url_table_function(
                    port=port, success=True, timeout=5
                )

    for cipher in all_ciphers:
        if cipher in fips_compatible_tlsv1_2_cipher_suites:
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
        node.command(f"rm -f {server_file_path}")


@TestOutline
def dictionary(self):
    """Check that clickhouse server only makes FIPS compatible HTTPS connections using a dictionary."""
    port = 5001
    default_ciphers = "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-GCM-SHA384"
    server_file_path = "https_" + getuid() + ".py"
    node = self.context.node

    tls_versions_supported = {
        "TLS": True,
        "TLSv1": False,
        "TLSv1.1": False,
        "TLSv1.2": True,
    }

    with Given("I make a copy of the flask server file"):
        node.command(f"cp /https_app_file.py {server_file_path}")

    for tls_version, should_work in tls_versions_supported.items():
        with Check(
            f"Connection with Protocol={tls_version} should be {'accepted' if should_work else 'rejected'}"
        ):
            flask_server(
                server_path=server_file_path,
                port=port,
                protocol=tls_version,
                ciphers=default_ciphers,
            )

            test_https_connection_with_dictionary(
                port=port, success=should_work, timeout=5
            )

    for cipher in fips_compatible_tlsv1_2_cipher_suites:
        with Check(f"connection using FIPS compatible cipher {cipher} should work"):
            flask_server(
                server_path=server_file_path,
                port=port,
                protocol="TLSv1.2",
                ciphers=cipher,
            )

            test_https_connection_with_dictionary(port=port, success=True, timeout=5)

        for second_cipher in all_ciphers:
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

                test_https_connection_with_dictionary(
                    port=port, success=True, timeout=5
                )

    for cipher in all_ciphers:
        if cipher in fips_compatible_tlsv1_2_cipher_suites:
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

            test_https_connection_with_dictionary(port=port, success=False, timeout=5)

    with Finally("I remove the flask server file"):
        node.command(f"rm -f {server_file_path}")


@TestScenario
@Name("log check")
def log_check(self):
    """Check the server log to ensure ClickHouse is running in FIPS mode."""
    exitcode = self.context.node.command(
        "cat /var/log/clickhouse-server/clickhouse-server.log | grep '<Information> Application: Starting in FIPS mode, KAT test result: 1' > /dev/null"
    ).exitcode
    assert exitcode == 0, error()


@TestScenario
@Name("check build options")
def build_options_check(self):
    """Check that system.build_options shows that ClickHouse was built using FIPs compliant BoringSSL library."""
    node = self.context.node
    with When("I read the system.build_options table"):
        output = node.query(
            "SELECT * FROM system.build_options FORMAT TabSeparated"
        ).output
        debug(output)

    with Then("I check that FIPS mode is present"):
        assert "fips" in output or "FIPS" in output, error()


@TestScenario
@Name("non fips clickhouse client")
def non_fips_clickhouse_client(self, tls1_2_enabled=True):
    """Check that clickhouse-client from a non-FIPS compliant build is able to connect to a clickhouse server using only FIPS compliant protocols and ciphers."""
    node = self.context.cluster.node("non_fips_clickhouse")
    add_trusted_ca_certificate(node=node, certificate=current().context.my_own_ca_crt)
    tcp_connection_clickhouse_client(
        node=node, port=self.context.secure_tcp_port, tls1_2_enabled=tls1_2_enabled
    )


@TestScenario
@Name("fips clickhouse client")
def fips_clickhouse_client(self, tls1_2_enabled=True):
    """Check that clickhouse-client from a FIPS compliant build is able to connect to a clickhouse server using only FIPS compliant protocols and ciphers."""
    node = self.context.cluster.node("clickhouse1")
    tcp_connection_clickhouse_client(
        node=node, port=self.context.secure_tcp_port, tls1_2_enabled=tls1_2_enabled
    )


@TestOutline
def clickhouse_client_tcp(self, tls1_2_enabled=True):
    """Check clickhouse-client TCP using a client from a FIPS and a non FIPS build."""
    Scenario("fips clickhouse-client", test=fips_clickhouse_client)(
        tls1_2_enabled=tls1_2_enabled,
    )

    Scenario("non fips clickhouse-client", test=non_fips_clickhouse_client)(
        tls1_2_enabled=tls1_2_enabled,
    )


@TestFeature
@Name("tcp connection")
@Requirements()
def server_tcp_connection(self, tls1_2_enabled=True):
    """Check that server accepts only FIPS compatible secure TCP connections."""
    Scenario(name="openssl s_client", test=server_connection_openssl_client)(
        port=self.context.secure_tcp_port,
        tls1_2_enabled=tls1_2_enabled,
    )

    Feature(name="clickhouse-client", test=clickhouse_client_tcp)(
        tls1_2_enabled=tls1_2_enabled
    )


@TestFeature
@Name("https connection")
@Requirements()
def server_https_connection(self, tls1_2_enabled=True):
    """Check that server accepts only FIPS compatible HTTPS connections."""
    Scenario("openssl s_client", test=server_connection_openssl_client)(
        port=self.context.secure_http_port, tls1_2_enabled=tls1_2_enabled
    )
    Scenario("curl", test=server_https_connection_curl)(tls1_2_enabled=tls1_2_enabled)


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


@TestFeature
@Name("clickhouse client")
@Requirements()
def clickhouse_client(self):
    """Check forcing clickhouse-client to use only FIPS compatible cipher suites to connect to server which is not configured to limit cipher suites."""
    Feature(
        name="clickhouse-client with non restricted server", run=clickhouse_client_tcp
    )

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

    Feature(name="clickhouse-client with restricted server", run=clickhouse_client_tcp)


@TestFeature
@Name("fips check")
@Requirements()
def fips_check(self):
    """Run checks that ClickHouse is in FIPS mode."""
    Scenario(run=log_check)
    Scenario(run=build_options_check)


@TestFeature
@Name("clickhouse server acting as a client")
def server_as_client(self):
    """Check connections from clickhouse-server when it is acting as a client and configured using openSSL client configs."""
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
        add_ssl_client_configuration_file(
            entries=entries, config_file="ssl_cipher_list.xml", restart=True
        )

    with And("I generate private key and certificate for https server"):
        create_crt_and_key(name="https_server", common_name="127.0.0.1")

    Feature(run=url_table_function)
    Feature(run=dictionary)


@TestFeature
@Name("fips")
@Requirements()
def feature(self, node="clickhouse1"):
    """Check using SSL configuration to force only FIPS compatible SSL connections."""
    cluster = self.context.cluster
    self.context.node = self.context.cluster.node(node)
    bash = self.context.cluster.bash(node=None)

    try:
        with Given("I start standalone keeper"):
            start_standalone_keeper(
                cluster_nodes=cluster.nodes["clickhouse"][0:1],
                control_nodes=cluster.nodes["clickhouse"][1:2],
            )

        with And("I stop all zookeepers"):
            for zookeeper_node in self.context.cluster.nodes["zookeeper"]:
                self.context.cluster.node(zookeeper_node).stop()

        with And("I check that all zookeepers containers were stopped"):
            for zookeeper_node in self.context.cluster.nodes["zookeeper"]:
                for retry in retries(timeout=10, delay=1):
                    with retry:
                        cmd = bash(
                            f"docker ps | grep clickhouse_keeper | grep {zookeeper_node}"
                        )
                        assert cmd.exitcode == 1

            assert self.context.node.query(
                f"select count() from system.zookeeper where path='/' FORMAT TabSeparated",
                retry_count=5,
                exitcode=0,
            )

        with And("I enable SSL"):
            enable_ssl(my_own_ca_key_passphrase="", server_key_passphrase="")

        if self.context.fips_mode:
            Feature(run=fips_check)

        Feature(run=server)
        Feature(run=clickhouse_client)
        Feature(run=server_as_client)
    finally:
        with Finally("I start all stopped all zookeepers"):
            for zookeeper_node in self.context.cluster.nodes["zookeeper"]:
                self.context.cluster.node(zookeeper_node).start()
