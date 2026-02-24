# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support running with binary that is statically linked with a [FIPS 140-3] compatible [AWS-LC] library.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Version = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Version",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL use [AWS-LC] static library built from source code version `AWS-LC FIPS 2.0.0`\n"
        "available at https://github.com/aws/aws-lc/archive/refs/tags/AWS-LC-FIPS-2.0.0.zip\n"
        "(SHA-256: `6241EC2F13A5F80224EE9CD8592ED66A97D426481066FEAA4EFC6F24E60BBC96`)\n"
        "that includes [FIPS 140-3] validated cryptographic module `bcm.o`\n"
        "issued CMVP Certificate #4816\n"
        "with the following security policy https://csrc.nist.gov/CSRC/media/projects/cryptographic-module-validation-program/documents/security-policies/140sp4816.pdf.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.2.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_PowerOnSelfTest_IntegrityTest = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.PowerOnSelfTest.IntegrityTest",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that implements\n"
        "a pre-operational integrity self-test using `HMAC-SHA-256` that SHALL verify the integrity of the `bcm.o` module\n"
        "by comparing a runtime-computed HMAC value against the build-time HMAC value stored within the module.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.1.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_PowerOnSelfTest_KnownAnswerTest = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.PowerOnSelfTest.KnownAnswerTest",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that implements\n"
        "cryptographic algorithm self-tests (CASTs) which SHALL include the following:\n"
        "\n"
        "Test |\n"
        "--- |\n"
        "AES-CBC KAT (encryption and decryption. Key size: 128-bits)\n"
        "AES-GCM KAT (encryption and decryption. Key size: 128-bits)\n"
        "SHA-1 KAT\n"
        "SHA2-256 KAT\n"
        "SHA2-512 KAT\n"
        "HMAC-SHA2-256 KAT\n"
        "SP 800-90A CTR_DRBG KAT (AES-256)\n"
        "DRBG Health Test (SP 800-90Ar1 Section 11.3)\n"
        "ECDSA SigGen KAT (P-256 curve, SHA2-256)\n"
        "ECDSA SigVer KAT (P-256 curve, SHA2-256)\n"
        "KAS-ECC-SSC KAT (P-256 curve)\n"
        "KDF TLS v1.2 KAT (SHA2-256)\n"
        "KDA HKDF KAT (HMAC-SHA2-256)\n"
        "PBKDF2 KAT (HMAC-SHA2-256)\n"
        "RSA SigGen KAT (PKCS#1 v1.5, 2048-bit key, SHA2-256)\n"
        "RSA SigVer KAT (PKCS#1 v1.5, 2048-bit key, SHA2-256)\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.2.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_ConditionalSelfTests = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ConditionalSelfTests",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that implements the following conditional\n"
        "self-tests:\n"
        "\n"
        "Type | Test\n"
        "--- | ---\n"
        "Pair-wise Consistency Test | ECDSA Key Pair generation (sign and verify), RSA Key Pair generation (sign and verify)\n"
        "DRBG Health Tests | Performed on DRBG, per SP 800-90Ar1 Section 11.3\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.4.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_ServiceIndicator = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ServiceIndicator",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that provides\n"
        "a service indicator via the `FIPS_service_indicator_check_approved()` function.\n"
        "A return value of `1` SHALL indicate that the invoked cryptographic service is an approved FIPS service.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.5.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SSLTests = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSLTests",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that passes all\n"
        "SSL tests as defined by https://github.com/aws/aws-lc/tree/main/ssl/test.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_ACVP_CheckExpectedTests = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ACVP.CheckExpectedTests",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that passes all\n"
        "ACVP validation tests using the `acvptool` and `modulewrapper` utilities provided by [AWS-LC].\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.7.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SystemTable_BuildOptions = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SystemTable.BuildOptions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support\n"
        "reporting that the binary was built with FIPS enabled [AWS-LC] library\n"
        "in the `system.build_options` table.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.8.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_MySQLFunction = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.MySQLFunction",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support\n"
        "reporting that it is FIPS compliant in the MySQL FIPS function.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.9.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SSL_Client_Config_Settings_FIPS = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Client.Config.Settings.FIPS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support\n"
        "`<clickhouse><openSSL><fips>` setting in the `config.xml`.\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <openSSL>\n"
        "        <fips>true</fips>\n"
        "    </openSSL>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.10.1.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SSL_Server_Config = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Server.Config",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support configuring\n"
        "server SSL to accept only [FIPS 140-3 Compatible SSL Connection]s\n"
        "using the `<clickhouse><openSSL><server>` section in the `config.xml` using the following\n"
        "settings:\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <openSSL>\n"
        "        <server> <!-- Used for https server AND secure tcp port -->\n"
        "            <cipherList>ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-GCM-SHA384</cipherList>\n"
        "            <cipherSuites>TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384</cipherSuites>\n"
        "            <preferServerCiphers>true</preferServerCiphers>\n"
        "            <disableProtocols>sslv2,sslv3,tlsv1,tlsv1_1</disableProtocols>\n"
        "        </server>\n"
        "    </openSSL>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.10.2.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SSL_Client_Config = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Client.Config",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support configuring\n"
        "SSL when server is acting as a client to establish only [FIPS 140-3 Compatible SSL Connection]s\n"
        "using the `<clickhouse><openSSL><client>` section in the `config.xml` using the following\n"
        "settings:\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <openSSL>\n"
        "        <client> <!-- Used for connecting to https dictionary source and secured Zookeeper communication -->\n"
        "            <cipherList>ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-GCM-SHA384</cipherList>\n"
        "            <cipherSuites>TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384</cipherSuites>\n"
        "            <preferServerCiphers>true</preferServerCiphers>\n"
        "            <disableProtocols>sslv2,sslv3,tlsv1,tlsv1_1</disableProtocols>\n"
        "        </client>\n"
        "    </openSSL>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.10.3.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Server_SSL_TCP = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Server.SSL.TCP",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support configuring\n"
        "server to accept only [FIPS 140-3 Compatible SSL Connection]s native TCP connections.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.11.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Server_SSL_HTTPS = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Server.SSL.HTTPS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support configuring\n"
        "server to accept only [FIPS 140-3 Compatible SSL Connection]s HTTPS connections.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.12.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Clients_SSL_TCP_ClickHouseClient_FIPS = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.ClickHouseClient.FIPS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support accepting\n"
        "connections from FIPS compliant [clickhouse-client] which uses native TCP protocol\n"
        "that is configured to establish only [FIPS 140-3 Compatible SSL Connection]s.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.13.1.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Clients_SSL_TCP_ClickHouseClient_NonFIPS = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.ClickHouseClient.NonFIPS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support accepting\n"
        "connections from non FIPS compliant [clickhouse-client] which uses native TCP protocol\n"
        "that is configured to establish only [FIPS 140-3 Compatible SSL Connection]s.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.13.1.2",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Clients_SSL_TCP_Python = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.Python",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support accepting\n"
        "connections from test Python client which uses native TCP protocol\n"
        "that is configured to establish only [FIPS 140-3 Compatible SSL Connection]s.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.13.2.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Clients_SSL_HTTPS_Curl = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.HTTPS.Curl",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support accepting\n"
        "connections from [curl] used as HTTPS protocol client that is configured to establish only [FIPS 140-3 Compatible SSL Connection]s.\n"
        "\n"
        "[FIPS 140-3 Compatible SSL Connection]: #fips-140-3-compatible-ssl-connection\n"
        "[clickhouse-client]: https://clickhouse.com/docs/en/interfaces/cli\n"
        "[OpenSSL ciphers]: https://www.openssl.org/docs/man1.1.1/man1/ciphers.html\n"
        "[curl]: https://curl.se/docs/manpage.html\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/tree/main/ssl_server/requirements/requirements_fips_140_3.md\n"
        "[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/ssl_server/requirements/requirements_fips_140_3.md\n"
        "[Git]: https://git-scm.com/\n"
        "[GitHub]: https://github.com\n"
        "[FIPS]: https://csrc.nist.gov/publications/detail/fips/140/3/final\n"
        "[FIPS 140-2]: https://csrc.nist.gov/publications/detail/fips/140/2/final\n"
        "[FIPS 140-3]: https://csrc.nist.gov/publications/detail/fips/140/3/final\n"
        "[BoringSSL]: https://github.com/google/boringssl/\n"
        "[AWS-LC]: https://github.com/aws/aws-lc\n"
        "[SRS-034]: requirements_fips.md\n"
        "[ACVP]: https://pages.nist.gov/ACVP/\n"
    ),
    link=None,
    level=4,
    num="4.14.1.1",
)

SRS_035_ClickHouse_With_FIPS_140_3_Compatible_AWS_LC = Specification(
    name="SRS-035 ClickHouse With FIPS 140-3 Compatible AWS-LC",
    description=None,
    author=None,
    date=None,
    status=None,
    approved_by=None,
    approved_date=None,
    approved_version=None,
    version=None,
    group=None,
    type=None,
    link=None,
    uid=None,
    parent=None,
    children=None,
    headings=(
        Heading(name="Revision History", level=1, num="1"),
        Heading(name="Introduction", level=1, num="2"),
        Heading(name="Terminology", level=1, num="3"),
        Heading(name="KAT", level=2, num="3.1"),
        Heading(name="CAST", level=2, num="3.2"),
        Heading(name="FIPS", level=2, num="3.3"),
        Heading(name="FIPS 140-3", level=2, num="3.4"),
        Heading(name="AWS-LC", level=2, num="3.5"),
        Heading(name="ACVP", level=2, num="3.6"),
        Heading(name="FIPS 140-3 Compatible SSL Connection", level=2, num="3.7"),
        Heading(name="Requirements", level=1, num="4"),
        Heading(name="General", level=2, num="4.1"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC", level=3, num="4.1.1"
        ),
        Heading(name="AWS-LC Version", level=2, num="4.2"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Version",
            level=3,
            num="4.2.1",
        ),
        Heading(name="Power-On Self-Tests", level=2, num="4.3"),
        Heading(name="Integrity Test", level=3, num="4.3.1"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.PowerOnSelfTest.IntegrityTest",
            level=4,
            num="4.3.1.1",
        ),
        Heading(name="Known Answer Test", level=3, num="4.3.2"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.PowerOnSelfTest.KnownAnswerTest",
            level=4,
            num="4.3.2.1",
        ),
        Heading(name="Conditional Self-Tests", level=2, num="4.4"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ConditionalSelfTests",
            level=3,
            num="4.4.1",
        ),
        Heading(name="Service Indicator", level=2, num="4.5"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ServiceIndicator",
            level=3,
            num="4.5.1",
        ),
        Heading(name="SSL Tests", level=2, num="4.6"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSLTests",
            level=3,
            num="4.6.1",
        ),
        Heading(name="ACVP Check Expected Tests", level=2, num="4.7"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ACVP.CheckExpectedTests",
            level=3,
            num="4.7.1",
        ),
        Heading(name="Build Options System Table", level=2, num="4.8"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SystemTable.BuildOptions",
            level=3,
            num="4.8.1",
        ),
        Heading(name="MySQL FIPS Function", level=2, num="4.9"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.MySQLFunction",
            level=3,
            num="4.9.1",
        ),
        Heading(name="SSL Configuration", level=2, num="4.10"),
        Heading(name="FIPS Setting", level=3, num="4.10.1"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Client.Config.Settings.FIPS",
            level=4,
            num="4.10.1.1",
        ),
        Heading(name="Server SSL Configuration", level=3, num="4.10.2"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Server.Config",
            level=4,
            num="4.10.2.1",
        ),
        Heading(name="Client SSL Configuration", level=3, num="4.10.3"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Client.Config",
            level=4,
            num="4.10.3.1",
        ),
        Heading(name="Server TCP Connections", level=2, num="4.11"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Server.SSL.TCP",
            level=3,
            num="4.11.1",
        ),
        Heading(name="Server HTTPS Connections", level=2, num="4.12"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Server.SSL.HTTPS",
            level=3,
            num="4.12.1",
        ),
        Heading(name="TCP Clients", level=2, num="4.13"),
        Heading(name="clickhouse-client", level=3, num="4.13.1"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.ClickHouseClient.FIPS",
            level=4,
            num="4.13.1.1",
        ),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.ClickHouseClient.NonFIPS",
            level=4,
            num="4.13.1.2",
        ),
        Heading(name="Test Python Client", level=3, num="4.13.2"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.Python",
            level=4,
            num="4.13.2.1",
        ),
        Heading(name="HTTPS Clients", level=2, num="4.14"),
        Heading(name="curl", level=3, num="4.14.1"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.HTTPS.Curl",
            level=4,
            num="4.14.1.1",
        ),
    ),
    requirements=(
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Version,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_PowerOnSelfTest_IntegrityTest,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_PowerOnSelfTest_KnownAnswerTest,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_ConditionalSelfTests,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_ServiceIndicator,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SSLTests,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_ACVP_CheckExpectedTests,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SystemTable_BuildOptions,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_MySQLFunction,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SSL_Client_Config_Settings_FIPS,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SSL_Server_Config,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SSL_Client_Config,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Server_SSL_TCP,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Server_SSL_HTTPS,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Clients_SSL_TCP_ClickHouseClient_FIPS,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Clients_SSL_TCP_ClickHouseClient_NonFIPS,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Clients_SSL_TCP_Python,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Clients_SSL_HTTPS_Curl,
    ),
    content=r"""
# SRS-035 ClickHouse With FIPS 140-3 Compatible AWS-LC
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Terminology](#terminology)
    * 3.1 [KAT](#kat)
    * 3.2 [CAST](#cast)
    * 3.3 [FIPS](#fips)
    * 3.4 [FIPS 140-3](#fips-140-3)
    * 3.5 [AWS-LC](#aws-lc)
    * 3.6 [ACVP](#acvp)
    * 3.7 [FIPS 140-3 Compatible SSL Connection](#fips-140-3-compatible-ssl-connection)
* 4 [Requirements](#requirements)
    * 4.1 [General](#general)
        * 4.1.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC](#rqsrs-035clickhousefipscompatibleawslc)
    * 4.2 [AWS-LC Version](#aws-lc-version)
        * 4.2.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Version](#rqsrs-035clickhousefipscompatibleawslcversion)
    * 4.3 [Power-On Self-Tests](#power-on-self-tests)
        * 4.3.1 [Integrity Test](#integrity-test)
            * 4.3.1.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.PowerOnSelfTest.IntegrityTest](#rqsrs-035clickhousefipscompatibleawslcpoweronselftestintegritytest)
        * 4.3.2 [Known Answer Test](#known-answer-test)
            * 4.3.2.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.PowerOnSelfTest.KnownAnswerTest](#rqsrs-035clickhousefipscompatibleawslcpoweronselftestknownanswertest)
    * 4.4 [Conditional Self-Tests](#conditional-self-tests)
        * 4.4.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ConditionalSelfTests](#rqsrs-035clickhousefipscompatibleawslcconditionalselftests)
    * 4.5 [Service Indicator](#service-indicator)
        * 4.5.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ServiceIndicator](#rqsrs-035clickhousefipscompatibleawslcserviceindicator)
    * 4.6 [SSL Tests](#ssl-tests)
        * 4.6.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSLTests](#rqsrs-035clickhousefipscompatibleawslcssltests)
    * 4.7 [ACVP Check Expected Tests](#acvp-check-expected-tests)
        * 4.7.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ACVP.CheckExpectedTests](#rqsrs-035clickhousefipscompatibleawslcacvpcheckexpectedtests)
    * 4.8 [Build Options System Table](#build-options-system-table)
        * 4.8.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SystemTable.BuildOptions](#rqsrs-035clickhousefipscompatibleawslcsystemtablebuildoptions)
    * 4.9 [MySQL FIPS Function](#mysql-fips-function)
        * 4.9.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.MySQLFunction](#rqsrs-035clickhousefipscompatibleawslcmysqlfunction)
    * 4.10 [SSL Configuration](#ssl-configuration)
        * 4.10.1 [FIPS Setting](#fips-setting)
            * 4.10.1.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Client.Config.Settings.FIPS](#rqsrs-035clickhousefipscompatibleawslcsslclientconfigsettingsfips)
        * 4.10.2 [Server SSL Configuration](#server-ssl-configuration)
            * 4.10.2.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Server.Config](#rqsrs-035clickhousefipscompatibleawslcsslserverconfig)
        * 4.10.3 [Client SSL Configuration](#client-ssl-configuration)
            * 4.10.3.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Client.Config](#rqsrs-035clickhousefipscompatibleawslcsslclientconfig)
    * 4.11 [Server TCP Connections](#server-tcp-connections)
        * 4.11.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Server.SSL.TCP](#rqsrs-035clickhousefipscompatibleawslcserverssltcp)
    * 4.12 [Server HTTPS Connections](#server-https-connections)
        * 4.12.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Server.SSL.HTTPS](#rqsrs-035clickhousefipscompatibleawslcserversslhttps)
    * 4.13 [TCP Clients](#tcp-clients)
        * 4.13.1 [clickhouse-client](#clickhouse-client)
            * 4.13.1.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.ClickHouseClient.FIPS](#rqsrs-035clickhousefipscompatibleawslcclientsssltcpclickhouseclientfips)
            * 4.13.1.2 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.ClickHouseClient.NonFIPS](#rqsrs-035clickhousefipscompatibleawslcclientsssltcpclickhouseclientnonfips)
        * 4.13.2 [Test Python Client](#test-python-client)
            * 4.13.2.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.Python](#rqsrs-035clickhousefipscompatibleawslcclientsssltcppython)
    * 4.14 [HTTPS Clients](#https-clients)
        * 4.14.1 [curl](#curl)
            * 4.14.1.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.HTTPS.Curl](#rqsrs-035clickhousefipscompatibleawslcclientssslhttpscurl)


## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for [ClickHouse] binary that
is statically linked with a [FIPS 140-3] compatible [AWS-LC] cryptographic library.

This specification supersedes [SRS-034] for deployments using [AWS-LC] FIPS 2.0.0 instead of [BoringSSL].

## Terminology

### KAT

Known Answer Test.

### CAST

Cryptographic Algorithm Self-Test. In [FIPS 140-3] terminology, CASTs replace the
power-on KATs from [FIPS 140-2]. They are performed conditionally (on first use or power-on)
rather than solely at module load time.

### FIPS

Federal Information Processing Standard.

### FIPS 140-3

[FIPS] Publication 140-3, Security Requirements for Cryptographic Modules.
Supersedes [FIPS 140-2]. Aligns with ISO/IEC 19790:2012(E).

### AWS-LC

AWS libcrypto. Amazon's fork of [BoringSSL] that carries its own [FIPS 140-3] validation
(CMVP Certificate #4816). The validated cryptographic module is `bcm.o` (version AWS-LC FIPS 2.0.0),
which is statically linked into the consuming application.

### ACVP

Automated Cryptographic Validation Protocol.

### FIPS 140-3 Compatible SSL Connection

[FIPS 140-3] compatible SSL connection SHALL be defined as follows:

TLS protocols

```
TLS v1.2
TLS v1.3
```

using FIPS preferred curves

```
CurveP256
CurveP384
CurveP521
```

and the following TLS v1.2 cipher suites

```
TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
TLS_RSA_WITH_AES_128_GCM_SHA256
TLS_RSA_WITH_AES_256_GCM_SHA384
```

and the following TLS v1.3 cipher suites

```
TLS_AES_128_GCM_SHA256
TLS_AES_256_GCM_SHA384
```

Note: `TLS_CHACHA20_POLY1305_SHA256` is NOT FIPS-approved as ChaCha20 and Poly1305
are not listed in the [AWS-LC] approved algorithms.

Which when required need to be mapped to the corresponding [OpenSSL ciphers] suites.

## Requirements

### General

#### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC
version: 1.0

[ClickHouse] SHALL support running with binary that is statically linked with a [FIPS 140-3] compatible [AWS-LC] library.

### AWS-LC Version

#### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Version
version: 1.0

[ClickHouse] SHALL use [AWS-LC] static library built from source code version `AWS-LC FIPS 2.0.0`
available at https://github.com/aws/aws-lc/archive/refs/tags/AWS-LC-FIPS-2.0.0.zip
(SHA-256: `6241EC2F13A5F80224EE9CD8592ED66A97D426481066FEAA4EFC6F24E60BBC96`)
that includes [FIPS 140-3] validated cryptographic module `bcm.o`
issued CMVP Certificate #4816
with the following security policy https://csrc.nist.gov/CSRC/media/projects/cryptographic-module-validation-program/documents/security-policies/140sp4816.pdf.

### Power-On Self-Tests

#### Integrity Test

##### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.PowerOnSelfTest.IntegrityTest
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that implements
a pre-operational integrity self-test using `HMAC-SHA-256` that SHALL verify the integrity of the `bcm.o` module
by comparing a runtime-computed HMAC value against the build-time HMAC value stored within the module.

#### Known Answer Test

##### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.PowerOnSelfTest.KnownAnswerTest
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that implements
cryptographic algorithm self-tests (CASTs) which SHALL include the following:

Test |
--- |
AES-CBC KAT (encryption and decryption. Key size: 128-bits)
AES-GCM KAT (encryption and decryption. Key size: 128-bits)
SHA-1 KAT
SHA2-256 KAT
SHA2-512 KAT
HMAC-SHA2-256 KAT
SP 800-90A CTR_DRBG KAT (AES-256)
DRBG Health Test (SP 800-90Ar1 Section 11.3)
ECDSA SigGen KAT (P-256 curve, SHA2-256)
ECDSA SigVer KAT (P-256 curve, SHA2-256)
KAS-ECC-SSC KAT (P-256 curve)
KDF TLS v1.2 KAT (SHA2-256)
KDA HKDF KAT (HMAC-SHA2-256)
PBKDF2 KAT (HMAC-SHA2-256)
RSA SigGen KAT (PKCS#1 v1.5, 2048-bit key, SHA2-256)
RSA SigVer KAT (PKCS#1 v1.5, 2048-bit key, SHA2-256)

### Conditional Self-Tests

#### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ConditionalSelfTests
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that implements the following conditional
self-tests:

Type | Test
--- | ---
Pair-wise Consistency Test | ECDSA Key Pair generation (sign and verify), RSA Key Pair generation (sign and verify)
DRBG Health Tests | Performed on DRBG, per SP 800-90Ar1 Section 11.3

### Service Indicator

#### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ServiceIndicator
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that provides
a service indicator via the `FIPS_service_indicator_check_approved()` function.
A return value of `1` SHALL indicate that the invoked cryptographic service is an approved FIPS service.

### SSL Tests

#### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSLTests
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that passes all
SSL tests as defined by https://github.com/aws/aws-lc/tree/main/ssl/test.

### ACVP Check Expected Tests

#### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ACVP.CheckExpectedTests
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that passes all
ACVP validation tests using the `acvptool` and `modulewrapper` utilities provided by [AWS-LC].

### Build Options System Table

#### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SystemTable.BuildOptions
version: 1.0

[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support
reporting that the binary was built with FIPS enabled [AWS-LC] library
in the `system.build_options` table.

### MySQL FIPS Function

#### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.MySQLFunction
version: 1.0

[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support
reporting that it is FIPS compliant in the MySQL FIPS function.

### SSL Configuration

#### FIPS Setting

##### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Client.Config.Settings.FIPS
version: 1.0

[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support
`<clickhouse><openSSL><fips>` setting in the `config.xml`.

```xml
<clickhouse>
    <openSSL>
        <fips>true</fips>
    </openSSL>
</clickhouse>
```

#### Server SSL Configuration

##### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Server.Config
version: 1.0

[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support configuring
server SSL to accept only [FIPS 140-3 Compatible SSL Connection]s
using the `<clickhouse><openSSL><server>` section in the `config.xml` using the following
settings:

```xml
<clickhouse>
    <openSSL>
        <server> <!-- Used for https server AND secure tcp port -->
            <cipherList>ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-GCM-SHA384</cipherList>
            <cipherSuites>TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384</cipherSuites>
            <preferServerCiphers>true</preferServerCiphers>
            <disableProtocols>sslv2,sslv3,tlsv1,tlsv1_1</disableProtocols>
        </server>
    </openSSL>
</clickhouse>
```

#### Client SSL Configuration

##### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Client.Config
version: 1.0

[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support configuring
SSL when server is acting as a client to establish only [FIPS 140-3 Compatible SSL Connection]s
using the `<clickhouse><openSSL><client>` section in the `config.xml` using the following
settings:

```xml
<clickhouse>
    <openSSL>
        <client> <!-- Used for connecting to https dictionary source and secured Zookeeper communication -->
            <cipherList>ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-GCM-SHA384</cipherList>
            <cipherSuites>TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384</cipherSuites>
            <preferServerCiphers>true</preferServerCiphers>
            <disableProtocols>sslv2,sslv3,tlsv1,tlsv1_1</disableProtocols>
        </client>
    </openSSL>
</clickhouse>
```

### Server TCP Connections

#### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Server.SSL.TCP
version: 1.0

[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support configuring
server to accept only [FIPS 140-3 Compatible SSL Connection]s native TCP connections.

### Server HTTPS Connections

#### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Server.SSL.HTTPS
version: 1.0

[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support configuring
server to accept only [FIPS 140-3 Compatible SSL Connection]s HTTPS connections.

### TCP Clients

#### clickhouse-client

##### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.ClickHouseClient.FIPS
version: 1.0

[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support accepting
connections from FIPS compliant [clickhouse-client] which uses native TCP protocol
that is configured to establish only [FIPS 140-3 Compatible SSL Connection]s.

##### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.ClickHouseClient.NonFIPS
version: 1.0

[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support accepting
connections from non FIPS compliant [clickhouse-client] which uses native TCP protocol
that is configured to establish only [FIPS 140-3 Compatible SSL Connection]s.

#### Test Python Client

##### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.Python
version: 1.0

[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support accepting
connections from test Python client which uses native TCP protocol
that is configured to establish only [FIPS 140-3 Compatible SSL Connection]s.

### HTTPS Clients

#### curl

##### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.HTTPS.Curl
version: 1.0

[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL support accepting
connections from [curl] used as HTTPS protocol client that is configured to establish only [FIPS 140-3 Compatible SSL Connection]s.

[FIPS 140-3 Compatible SSL Connection]: #fips-140-3-compatible-ssl-connection
[clickhouse-client]: https://clickhouse.com/docs/en/interfaces/cli
[OpenSSL ciphers]: https://www.openssl.org/docs/man1.1.1/man1/ciphers.html
[curl]: https://curl.se/docs/manpage.html
[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/tree/main/ssl_server/requirements/requirements_fips_140_3.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/ssl_server/requirements/requirements_fips_140_3.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
[FIPS]: https://csrc.nist.gov/publications/detail/fips/140/3/final
[FIPS 140-2]: https://csrc.nist.gov/publications/detail/fips/140/2/final
[FIPS 140-3]: https://csrc.nist.gov/publications/detail/fips/140/3/final
[BoringSSL]: https://github.com/google/boringssl/
[AWS-LC]: https://github.com/aws/aws-lc
[SRS-034]: requirements_fips.md
[ACVP]: https://pages.nist.gov/ACVP/
""",
)
