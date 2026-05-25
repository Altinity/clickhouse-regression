import time

from ssl_keeper.requirements import *
from ssl_keeper.tests.steps import *
from helpers.common import *
from ssl_server.tests.common import fips_forbidden_primitive_tlsv1_2_cipher_suites

fips_140_3_compatible_tlsv1_2_cipher_suites = [
    "ECDHE-RSA-AES128-GCM-SHA256",
    "ECDHE-RSA-AES256-GCM-SHA384",
    # ECDSA ciphers require ECDSA server certificates
    # "ECDHE-ECDSA-AES128-GCM-SHA256",
    # "ECDHE-ECDSA-AES256-GCM-SHA384",
    "AES128-GCM-SHA256",
    "AES256-GCM-SHA384",
]

fips_140_3_compatible_tlsv1_3_cipher_suites = [
    "TLS_AES_128_GCM_SHA256",
    "TLS_AES_256_GCM_SHA384",
]

all_tlsv1_3_ciphers = [
    "TLS_AES_256_GCM_SHA384",
    "TLS_CHACHA20_POLY1305_SHA256",
    "TLS_AES_128_GCM_SHA256",
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

# Overlay merges after packaged `fips.xml`: omit server cipherList/cipherSuites so TLS stack
# uses defaults (permits probing client-offered DHE on otherwise FIPS deployments).
PERMISSIVE_FFDH_PROBE_SSL_ENTRIES = {
    "server": {
        "certificateFile": "/etc/clickhouse-server/config.d/server.crt",
        "privateKeyFile": "/etc/clickhouse-server/config.d/server.key",
        "dhParamsFile": "/etc/clickhouse-server/config.d/dhparam.pem",
        "caConfig": "/etc/clickhouse-server/config.d/altinity_blog_ca.crt",
        "loadDefaultCAFile": "false",
        "verificationMode": "none",
        "cacheSessions": "true",
        "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1",
        "preferServerCiphers": "true",
    },
    "client": {
        "certificateFile": "/etc/clickhouse-server/config.d/server.crt",
        "privateKeyFile": "/etc/clickhouse-server/config.d/server.key",
        "loadDefaultCAFile": "false",
        "caConfig": "/etc/clickhouse-server/config.d/altinity_blog_ca.crt",
        "cacheSessions": "true",
        "preferServerCiphers": "true",
        "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1",
        "verificationMode": "none",
        "invalidCertificateHandler": {"name": "AcceptCertificateHandler"},
    },
}

PERMISSIVE_FFDH_PROBE_CONFIG_FILE = "zz_ffdh_permissive_probe.xml"
# clickhouse_client_connection leaves this file unless removed; last cipherList (e.g. DHE-only)
# breaks later SELECT version() health checks with NO_CIPHERS_AVAILABLE against ECDHE-only server.
CLICKHOUSE_CLIENT_FIPS_TEST_OVERRIDE = (
    "/etc/clickhouse-client/config.d/fips_test_override.xml"
)


@TestScenario
@Requirements(RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Server_SSL_Keeper("1.0"))
def mixed_keepers_3(self):
    """Check that 3 nodes ClickHouse Keeper cluster works in write mode
    with 1 node down and in read mode only with 2 nodes down,
    using FIPS 140-3 compatible connections."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")
    try:
        with Given("Receive UID"):
            uid = getuid()

        with And("I create some replicated table"):
            table_name = f"test{uid}"
            retry(node.query, timeout=300, delay=10)(
                "SELECT 1", message="1", exitcode=0
            )

            create_simple_table(table_name=table_name)

        with And("I stop maximum available Keeper nodes for such configuration"):
            cluster.node("clickhouse3").stop_clickhouse()

        with And("I check that table in write mode"):
            retry(cluster.node("clickhouse1").query, timeout=500, delay=1)(
                f"insert into {table_name} values (1,1)", exitcode=0
            )

        with And("I stop one more Keeper node"):
            cluster.node("clickhouse2").stop_clickhouse()

        if check_clickhouse_version(">23")(self):
            with And("I check that table in read only mode"):
                retry(cluster.node("clickhouse1").query, timeout=300, delay=10)(
                    f"insert into {table_name} values (1,2)",
                    exitcode=242,
                    message="DB::Exception: Table is in readonly mode",
                    steps=False,
                    settings=[("insert_keeper_max_retries", 0)],
                )

        else:
            with And("I check that table in read only mode"):
                retry(cluster.node("clickhouse1").query, timeout=300, delay=10)(
                    f"insert into {table_name} values (1,2)",
                    exitcode=242,
                    message="DB::Exception: Table is in readonly mode",
                    steps=False,
                )

        with And("I start dropped nodes"):
            for name in cluster.nodes["clickhouse"][1:3]:
                cluster.node(name).start_clickhouse(wait_healthy=False)

        with And("I check that ruok returns imok"):
            for name in cluster.nodes["clickhouse"][0:3]:
                retry(cluster.node("bash-tools").command, timeout=500, delay=1)(
                    f"echo ruok | nc {name} 9281",
                    exitcode=0,
                    message="F",
                )

        with And("I check clean ability"):
            table_insert(table_name=table_name, node_name="clickhouse1")

    finally:
        with Finally("I clean up"):
            clean_coordination_on_all_nodes()


@TestScenario
@Requirements(RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Server_SSL_Keeper("1.0"))
def simple_check_clickhouse_connection_to_keeper(self, node=None, message="keeper"):
    """Check ClickHouse connection to ClickHouse Keeper."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    node.query(
        "SELECT * FROM system.zookeeper WHERE path = '/' FORMAT JSON", message=message
    )


@TestFeature
@Name("AWS-LC FFDH handshake probes (permissive server)")
@Requirements(
    RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Server_SSL_Keeper("1.0"),
    RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Server_SSL_TCP("1.0"),
    RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Clients_SSL_TCP_ClickHouseClient_FIPS(
        "1.0"
    ),
)
def keeper_permissive_ffdh_handshake_probes(self):
    """Finite-field DH TLS 1.2 suites against permissive listener configs.

    Packaged ``fips.xml`` locks ``cipherList``; this overlay drops that lockdown so
    openssl / clickhouse-client can mirror ``ssl_server`` FFDH probes on Keeper,
    interserver, HTTPS, and native secure TCP ports.

    Same service-indicator caveats as ``ssl_server`` ``server_default_config_algorithm_enforcement``.
    """
    cluster_nodes = ("clickhouse1", "clickhouse2", "clickhouse3")
    probe_path = (
        f"/etc/clickhouse-server/config.d/{PERMISSIVE_FFDH_PROBE_CONFIG_FILE}"
    )

    if not check_is_fips_clickhouse_build(self):
        skip("FFDH permissive-server probes apply only to FIPS builds")

    retry(self.context.cluster.node("clickhouse1").query, timeout=300, delay=10)(
        "SELECT 1", message="1", exitcode=0
    )

    try:
        with Given(
            "permissive openSSL overlay without cipherList/cipherSuites lockdown",
            description=(
                "Merge order loads this file after packaged fips.xml so defaults "
                "apply for cipher negotiation while certs and protocol floors stay."
            ),
        ):
            create_ssl_configuration(
                entries=PERMISSIVE_FFDH_PROBE_SSL_ENTRIES,
                config_file=PERMISSIVE_FFDH_PROBE_CONFIG_FILE,
                nodes=list(cluster_nodes),
                restart=True,
            )

        retry(self.context.cluster.node("clickhouse1").query, timeout=300, delay=10)(
            "SELECT 1", message="1", exitcode=0
        )

        bash_tools = self.context.cluster.node("bash-tools")
        target_host = "clickhouse1"

        for port in ("9281", "9444", "9010", "8443", "9440"):
            self.context.connection_port = port
            for cipher in fips_forbidden_primitive_tlsv1_2_cipher_suites:
                with Check(
                    f"openssl port {port} TLSv1.2 DHE suite {cipher} handshake should fail "
                    "(FFDH primitive unavailable in this FIPS stack)"
                ):
                    openssl_client_connection(
                        options=f'-cipher "{cipher}" -tls1_2',
                        success=False,
                        node=bash_tools,
                        hostname=target_host,
                        port=port,
                    )

        self.context.connection_port = 9440
        client_node = self.context.cluster.node("clickhouse1")
        for cipher in fips_forbidden_primitive_tlsv1_2_cipher_suites:
            with Check(
                f"clickhouse-client TLSv1.2 DHE suite {cipher} should fail without cipherList lockdown "
                "(FFDH primitive unavailable in this FIPS stack)"
            ):
                clickhouse_client_connection(
                    options={
                        "requireTLSv1_2": "true",
                        "cipherList": cipher,
                        "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
                    },
                    success=False,
                    node=client_node,
                    hostname=target_host,
                    port=9440,
                )

    finally:
        with Finally("remove permissive overlay and restore packaged SSL"):
            for name in cluster_nodes:
                self.context.cluster.node(name).command(
                    f"rm -f {probe_path}", exitcode=0
                )
            for name in cluster_nodes:
                self.context.cluster.node(name).command(
                    f"rm -f {CLICKHOUSE_CLIENT_FIPS_TEST_OVERRIDE}",
                    exitcode=0,
                )
            for name in cluster_nodes:
                self.context.cluster.node(name).restart_clickhouse()


@TestFeature
@Requirements(RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SSL_Server_Config("1.0"))
def openssl_check_simple(self, node=None, message="TLSv1."):
    """Check ClickHouse connection to ClickHouse Keeper on port is SSL."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)

    ports_list = ["9440", "9281", "9010", "9444", "8443"]

    for port in ports_list:
        with Check(f"port:{port}"):
            with Then("I make openssl check"):
                node.command(
                    f'openssl s_client -connect clickhouse1:{port} <<< "Q"',
                    message=message,
                )


@TestOutline
def server_connection_openssl_client(self, port, tls_enabled=True):
    """Check that server accepts only FIPS 140-3 compatible secure connections
    on a given port using openssl s_client utility."""
    self.context.connection_port = port
    tls_status = "work" if tls_enabled else "be rejected"

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
        )

    with Check(f"TLSv1.2 suite connection should {tls_status}"):
        openssl_client_connection(options="-tls1_2", success=tls_enabled)

    with Check(f"TLSv1.3 suite connection should {tls_status}"):
        openssl_client_connection(options="-tls1_3", success=tls_enabled)

    with Check("TLSv1 suite connection should be rejected"):
        openssl_client_connection(
            options="-tls1", success=False, message="no protocols available"
        )

    with Check("TLSv1.1 suite connection should be rejected"):
        openssl_client_connection(
            options="-tls1_1", success=False, message="no protocols available"
        )

    with Check("any DTLS suite connection should be rejected"):
        openssl_client_connection(options="-dtls", success=False)

    with Check("DTLSv1 suite connection should be rejected"):
        openssl_client_connection(options="-dtls1", success=False)

    with Check("DTLSv1.2 suite connection should be rejected"):
        openssl_client_connection(options="-dtls1.2", success=False)

    with Check(f"just disabling TLSv1 suite connection should {tls_status}"):
        openssl_client_connection(options="-no_tls1", success=tls_enabled)

    with Check(f"just disabling TLSv1.1 suite connection should {tls_status}"):
        openssl_client_connection(options="-no_tls1_1", success=tls_enabled)

    with Check(f"just disabling TLSv1.3 suite connection should {tls_status}"):
        openssl_client_connection(options="-no_tls1_3", success=tls_enabled)

    with Check(f"just disabling TLSv1.2 suite connection should {tls_status}"):
        openssl_client_connection(options="-no_tls1_2", success=tls_enabled)

    with Check("disabling both TLSv1.2 and TLSv1.3 suite connection should be rejected"):
        openssl_client_connection(
            options="-no_tls1_2 -no_tls1_3", success=False
        )

    for cipher in fips_140_3_compatible_tlsv1_2_cipher_suites:
        with Check(
            f"connection using FIPS compatible TLSv1.2 cipher {cipher} should {tls_status}"
        ):
            openssl_client_connection(
                options=f'-cipher "{cipher}" -tls1_2',
                success=tls_enabled,
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
                options=f'-cipher "{cipher}" -tls1_2', success=False
            )

    for cipher in fips_140_3_compatible_tlsv1_3_cipher_suites:
        with Check(
            f"connection using FIPS compatible TLSv1.3 cipher {cipher} should {tls_status}"
        ):
            openssl_client_connection(
                options=f'-ciphersuites "{cipher}" -tls1_3',
                success=tls_enabled,
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
            )


@TestFeature
@Requirements(
    RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SSL_Server_Config("1.0"),
    RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Server_SSL_TCP("1.0"),
    RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Server_SSL_HTTPS("1.0"),
    RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Server_SSL_Keeper("1.0"),
    RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Server_SSL_Interserver("1.0"),
)
def openssl_check(self, node=None):
    """Check ClickHouse connection on all ports is SSL with FIPS 140-3 ciphers."""

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
    self, hostname="clickhouse1", tls_enabled=True, port=None
):
    """Check that server accepts only FIPS 140-3 compatible TCP connections
    using clickhouse-client."""

    tls_status = "work" if tls_enabled else "be rejected"

    if port is None:
        port = self.context.secure_tcp_port

    with Given(
        "server is configured to accept only FIPS 140-3 compatible connections",
        description=f"on port {port}",
    ):
        self.context.connection_port = port

    with Check("Connection with no protocols should be rejected"):
        clickhouse_client_connection(
            options={
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_2,tlsv1_3",
            },
            success=False,
            hostname=hostname,
            message="NO_SUPPORTED_VERSIONS_ENABLED",
        )

    with Check(f"TLSv1.2 suite connection should {tls_status}"):
        clickhouse_client_connection(
            options={
                "requireTLSv1_2": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
            },
            success=tls_enabled,
            hostname=hostname,
        )

    with Check(f"TLSv1.3 suite connection should {tls_status}"):
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

    with Check("TLSv1.1 suite connection should be rejected"):
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

    with Check(f"just disabling TLSv1.1 suite connection should {tls_status}"):
        clickhouse_client_connection(
            options={"disableProtocols": "tlsv1_1"},
            success=tls_enabled,
            prefer_server_ciphers=True,
            hostname=hostname,
        )

    with Check(f"just disabling TLSv1.3 suite connection should {tls_status}"):
        clickhouse_client_connection(
            options={"disableProtocols": "tlsv1_3"},
            success=tls_enabled,
            prefer_server_ciphers=True,
            hostname=hostname,
        )

    with Check(f"just disabling TLSv1.2 suite connection should {tls_status}"):
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
            clickhouse_client_connection(
                options={
                    "cipherList": cipher,
                    "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
                },
                success=False,
                hostname=hostname,
            )

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


@TestFeature
@Requirements(
    RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Clients_SSL_TCP_ClickHouseClient_FIPS("1.0"),
    RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Server_SSL_TCP("1.0"),
)
def tcp_connection_check(self, node=None):
    """Check ClickHouse Keeper FIPS 140-3 compatible TCP connections."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)

    ports_list = define("All ports for testing", ["9440"])

    for port in ports_list:
        with Check(f"port:{port}"):
            tcp_connection_clickhouse_client(port=port)


@TestFeature
@Name("fips 140-3")
@Requirements(RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Server_SSL_Keeper("1.0"))
def feature(self):
    """Check ClickHouse Keeper with FIPS 140-3 compatible SSL connections
    using AWS-LC cryptographic module."""

    Feature(run=load("ssl_keeper.tests.fips_doc_config.feature", "feature"))

    with Pool(1) as executor:
        try:
            for scenario in loads(current_module(), Scenario):
                Feature(test=scenario, parallel=True, executor=executor)()
        finally:
            join()

    with Pool(1) as executor:
        try:
            for feature in loads(current_module(), Feature):
                if not feature.name.endswith("fips 140-3"):
                    Feature(test=feature, parallel=True, executor=executor)()
        finally:
            join()
