# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.230110.1184526.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support running with binary that is statically linked with a [FIPS] compatible [BoringSSL] library.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.1",
)

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_Version = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Version",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL use [BoringSSL] static library build from source code with version `dcdc7bbc6e59ac0123407a9dc4d1f43dd0d117cd`\n"
        "that includes [FIPS] validated [BoringCrypto] core library for Android that was issued the following\n"
        "[FIPS 140-2] certificate https://csrc.nist.gov/Projects/Cryptographic-Module-Validation-Program/Certificate/4156\n"
        "with the following security policy https://csrc.nist.gov/CSRC/media/projects/cryptographic-module-validation-program/documents/security-policies/140sp4156.pdf.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.2.1",
)

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_PowerOnSelfTest_IntegrityTest = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.PowerOnSelfTest.IntegrityTest",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be statically linked with a [FIPS] compatible [BoringSSL] library that implements power-on integrity self test\n"
        "using `HMAC-SHA-256` that SHALL verify the signature of the binary.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.1.1",
)

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_PowerOnSelfTest_KnownAnswerTest = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.PowerOnSelfTest.KnownAnswerTest",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be statically linked with a [FIPS] compatible [BoringSSL] library that implements power-on\n"
        "known answer test (KAT) which SHALL include the following:\n"
        "\n"
        "Test |\n"
        "--- |\n"
        "AES-CBC KAT (encryption and decryption. Key size: 128-bits)\n"
        "AES-GCM KAT (encryption and decryption. Key size: 128-bits)\n"
        "Triple-DES TCBC KAT (encryption and decryption. Key size: 168-bits)\n"
        "ECDSA KAT (signature generation/signature verification. Curve: P-256)\n"
        "HMAC KAT (HMAC-SHA-1, HMAC-SHA-512)\n"
        "SP 800-90A CTR_DRBG KAT (Key size: 256-bits)\n"
        "RSA KAT (signature generation/signature verification and encryption/decryption. Key size: 2048-bit)\n"
        "TLS v1.2 KDF KAT\n"
        "KAS-ECC-SSC primitive KAT Curve P-256)\n"
        "KAS-FFC-SSC primitive KAT (2048-bit)\n"
        "SHA KAT (SHA-1, SHA-256, SHA-512)\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.2.1",
)

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_ConditionalSelfTests = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.ConditionalSelfTests",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be statically linked with a [FIPS] compatible [BoringSSL] library that implements the following conditional\n"
        "self-tests:\n"
        "\n"
        "Type | Test\n"
        "--- | ---\n"
        "Pair-wise Consistency Test | ECDSA Key Pair generation, RSA Key Pair generation\n"
        "CRNGT | Performed on the passively received entropy\n"
        "DRBG Health Tests | Performed on DRBG, per SP 800‐90A Section 11.3. Required per IG C.1. \n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.4.1",
)

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_SSLTests = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SSLTests",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be statically linked with a [FIPS] compatible [BoringSSL] library that passes all\n"
        "SSL tests as defined by https://github.com/google/boringssl/blob/master/ssl/ssl_test.cc.\n"
        "\n"
        "For example,\n"
        "\n"
        "```bash\n"
        "./ssl/ssl_test\n"
        "...\n"
        "[==========] 330 tests from 6 test suites ran. (2410 ms total)\n"
        "[  PASSED  ] 330 tests.\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.5.1",
)

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_AllTestsUtility = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.AllTestsUtility",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be statically linked with [FIPS] compatible [BoringSSL] library that passes all\n"
        "`util/all_tests.go` tests. \n"
        "\n"
        "For example,\n"
        "\n"
        "```bash\n"
        "go run util/all_tests.go\n"
        "...\n"
        "All tests passed!\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.1",
)

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_ACVP_CheckExpectedTests = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.ACVP.CheckExpectedTests",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be statically linked with a [FIPS] compatible [BoringSSL] library that passes all\n"
        "`/util/fipstools/acvp/acvptool/test/check_expected.go` tests.\n"
        "\n"
        "```bash\n"
        "./boringssl/util/fipstools/acvp/acvptool/test$ go run check_expected.go -tool ../acvptool -module-wrappers modulewrapper:../../../../../build/util/fipstools/acvp/modulewrapper/modulewrapper,testmodulewrapper:../testmodulewrapper/testmodulewrapper -tests tests.json \n"
        "2022/12/14 20:57:26 32 ACVP tests matched expectations\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.7.1",
)

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_SystemTable_BuildOptions = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SystemTable.BuildOptions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support\n"
        "reporting that the binary was build with FIPS enabled [BoringSSL] library\n"
        "in the `system.build_options` table.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.8.1",
)

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_MySQLFunction = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.MySQLFunction",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support\n"
        "reporting that it is FIPS compliant in the MySQL FIPS function.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.9.1",
)

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_SSL_Client_Config_Settings_FIPS = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SSL.Client.Config.Settings.FIPS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support\n"
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

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_SSL_Server_Config = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SSL.Server.Config",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support configuring\n"
        "server SSL to accept only [FIPS Compatible SSL Connection]s\n"
        "using the `<clickhouse><openSSL><server>` section in the `config.xml` using the following\n"
        "settings:\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <openSSL>\n"
        "        <server> <!-- Used for https server AND secure tcp port -->\n"
        "            <cipherList>ALL:!ADH:!LOW:!EXP:!MD5:@STRENGTH</cipherList>\n"
        "            <requireTLSv1>true|false</requireTLSv1>\n"
        "            <requireTLSv1_1>true|false</requireTLSv1_1>\n"
        "            <requireTLSv1_2>true|false</requireTLSv1_2>\n"
        "            <disableProtocols>sslv2,sslv3</disableProtocols>\n"
        "            <preferServerCiphers>true</preferServerCiphers>\n"
        "        </server>\n"
        "    </openSSL>\n"
        "<clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.10.2.1",
)

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_SSL_Client_Config = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SSL.Client.Config",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support configuring\n"
        "SSL when server is acting as a client to establish only [FIPS Compatible SSL Connection]s\n"
        "using the `<clickhouse><openSSL><client>` section in the `config.xml` using the following\n"
        "settings:\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <openSSL>\n"
        "        <client> <!-- Used for connecting to https dictionary source and secured Zookeeper communication -->\n"
        "            <cipherList>ALL:!ADH:!LOW:!EXP:!MD5:@STRENGTH</cipherList>\n"
        "            <requireTLSv1>true|false</requireTLSv1>\n"
        "            <requireTLSv1_1>true|false</requireTLSv1_1>\n"
        "            <requireTLSv1_2>true|false</requireTLSv1_2>\n"
        "            <disableProtocols>sslv2,sslv3</disableProtocols>\n"
        "            <preferServerCiphers>true</preferServerCiphers>\n"
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

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_Server_SSL_TCP = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Server.SSL.TCP",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support configuring\n"
        "server to accept only [FIPS Compatible SSL Connection]s native TCP connections.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.11.1",
)

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_Server_SSL_HTTPS = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Server.SSL.HTTPS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support configuring\n"
        "server to accept only [FIPS Compatible SSL Connection]s HTTPS connections.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.12.1",
)

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_Clients_SSL_TCP_ClickHouseClient_FIPS = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Clients.SSL.TCP.ClickHouseClient.FIPS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support accepting\n"
        "connections from FIPS compliant [clickhouse-client] which uses native TCP protocol\n"
        "that is configured to establish only [FIPS Compatible SSL Connection]s.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.13.1.1",
)

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_Clients_SSL_TCP_ClickHouseClient_NonFIPS = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Clients.SSL.TCP.ClickHouseClient.NonFIPS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support accepting\n"
        "connections from non FIPS compliant [clickhouse-client] which uses native TCP protocol\n"
        "that is configured to establish only [FIPS Compatible SSL Connection]s.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.13.1.2",
)

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_Clients_SSL_TCP_Python = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Clients.SSL.TCP.Python",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support accepting\n"
        "connections from test Python client which uses native TCP protocol\n"
        "that is configured to establish only [FIPS Compatible SSL Connection]s.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.13.2.1",
)

RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_Clients_SSL_HTTPS_Curl = Requirement(
    name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Clients.SSL.HTTPS.Curl",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support accepting\n"
        "connections from [curl] used as HTTPS protocol client that is configured to establish only [FIPS Compatible SSL Connection]s.\n"
        "\n"
        "[FIPS Compatible SSL Connection]: #fips_compatible_ssl_connection\n"
        "[OpenSSL ciphers]: https://www.openssl.org/docs/man1.1.1/man1/ciphers.html\n"
        "[curl]: https://curl.se/docs/manpage.html\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/tree/main/ssl_server/requirements/requirements_fips.md\n"
        "[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/ssl_server/requirements/requirements_fips.md\n"
        "[Git]: https://git-scm.com/\n"
        "[GitHub]: https://github.com\n"
        "[FIPS]: https://csrc.nist.gov/publications/detail/fips/140/2/final\n"
        "[FIPS 140-2]: https://csrc.nist.gov/publications/detail/fips/140/2/final\n"
        "[BoringSSL]: https://github.com/google/boringssl/\n"
        "[BoringCrypto]: https://github.com/google/boringssl/tree/master/crypto\n"
        "[ACVP]: https://pages.nist.gov/ACVP/\n"
    ),
    link=None,
    level=4,
    num="4.14.1.1",
)

SRS_034_ClickHouse_With_FIPS_Compatible_BoringSSL = Specification(
    name="SRS-034 ClickHouse With FIPS Compatible BoringSSL",
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
        Heading(name="FIPS", level=2, num="3.2"),
        Heading(name="ACVP", level=2, num="3.3"),
        Heading(name="FIPS Compatible SSL Connection", level=2, num="3.4"),
        Heading(name="Requirements", level=1, num="4"),
        Heading(name="General", level=2, num="4.1"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL", level=3, num="4.1.1"
        ),
        Heading(name="BoringSSL Version", level=2, num="4.2"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Version",
            level=3,
            num="4.2.1",
        ),
        Heading(name="Power-On Self-Tests", level=2, num="4.3"),
        Heading(name="Integrity Test", level=3, num="4.3.1"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.PowerOnSelfTest.IntegrityTest",
            level=4,
            num="4.3.1.1",
        ),
        Heading(name="Known Answer Test", level=3, num="4.3.2"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.PowerOnSelfTest.KnownAnswerTest",
            level=4,
            num="4.3.2.1",
        ),
        Heading(name="Conditional Self-Tests", level=2, num="4.4"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.ConditionalSelfTests",
            level=3,
            num="4.4.1",
        ),
        Heading(name="SSL Tests", level=2, num="4.5"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SSLTests",
            level=3,
            num="4.5.1",
        ),
        Heading(name="All-tests Utility", level=2, num="4.6"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.AllTestsUtility",
            level=3,
            num="4.6.1",
        ),
        Heading(name="ACVP Check Expected Tests", level=2, num="4.7"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.ACVP.CheckExpectedTests",
            level=3,
            num="4.7.1",
        ),
        Heading(name="Build Options System Table", level=2, num="4.8"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SystemTable.BuildOptions",
            level=3,
            num="4.8.1",
        ),
        Heading(name="MySQL FIPS Function", level=2, num="4.9"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.MySQLFunction",
            level=3,
            num="4.9.1",
        ),
        Heading(name="SSL Configuration", level=2, num="4.10"),
        Heading(name="FIPS Setting", level=3, num="4.10.1"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SSL.Client.Config.Settings.FIPS",
            level=4,
            num="4.10.1.1",
        ),
        Heading(name="Server SSL Configuration", level=3, num="4.10.2"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SSL.Server.Config",
            level=4,
            num="4.10.2.1",
        ),
        Heading(name="Client SSL Configuration", level=3, num="4.10.3"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SSL.Client.Config",
            level=4,
            num="4.10.3.1",
        ),
        Heading(name="Server TCP Connections", level=2, num="4.11"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Server.SSL.TCP",
            level=3,
            num="4.11.1",
        ),
        Heading(name="Server HTTPS Connections", level=2, num="4.12"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Server.SSL.HTTPS",
            level=3,
            num="4.12.1",
        ),
        Heading(name="TCP Clients", level=2, num="4.13"),
        Heading(name="clickhouse-client", level=3, num="4.13.1"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Clients.SSL.TCP.ClickHouseClient.FIPS",
            level=4,
            num="4.13.1.1",
        ),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Clients.SSL.TCP.ClickHouseClient.NonFIPS",
            level=4,
            num="4.13.1.2",
        ),
        Heading(name="Test Python Client", level=3, num="4.13.2"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Clients.SSL.TCP.Python",
            level=4,
            num="4.13.2.1",
        ),
        Heading(name="HTTPS Clients", level=2, num="4.14"),
        Heading(name="curl", level=3, num="4.14.1"),
        Heading(
            name="RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Clients.SSL.HTTPS.Curl",
            level=4,
            num="4.14.1.1",
        ),
    ),
    requirements=(
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_Version,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_PowerOnSelfTest_IntegrityTest,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_PowerOnSelfTest_KnownAnswerTest,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_ConditionalSelfTests,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_SSLTests,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_AllTestsUtility,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_ACVP_CheckExpectedTests,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_SystemTable_BuildOptions,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_MySQLFunction,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_SSL_Client_Config_Settings_FIPS,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_SSL_Server_Config,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_SSL_Client_Config,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_Server_SSL_TCP,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_Server_SSL_HTTPS,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_Clients_SSL_TCP_ClickHouseClient_FIPS,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_Clients_SSL_TCP_ClickHouseClient_NonFIPS,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_Clients_SSL_TCP_Python,
        RQ_SRS_034_ClickHouse_FIPS_Compatible_BoringSSL_Clients_SSL_HTTPS_Curl,
    ),
    content="""
# SRS-034 ClickHouse With FIPS Compatible BoringSSL
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Terminology](#terminology)
  * 3.1 [KAT](#kat)
  * 3.2 [FIPS](#fips)
  * 3.3 [ACVP](#acvp)
  * 3.4 [FIPS Compatible SSL Connection](#fips-compatible-ssl-connection)
* 4 [Requirements](#requirements)
  * 4.1 [General](#general)
    * 4.1.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL](#rqsrs-034clickhousefipscompatibleboringssl)
  * 4.2 [BoringSSL Version](#boringssl-version)
    * 4.2.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Version](#rqsrs-034clickhousefipscompatibleboringsslversion)
  * 4.3 [Power-On Self-Tests](#power-on-self-tests)
    * 4.3.1 [Integrity Test](#integrity-test)
      * 4.3.1.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.PowerOnSelfTest.IntegrityTest](#rqsrs-034clickhousefipscompatibleboringsslpoweronselftestintegritytest)
    * 4.3.2 [Known Answer Test](#known-answer-test)
      * 4.3.2.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.PowerOnSelfTest.KnownAnswerTest](#rqsrs-034clickhousefipscompatibleboringsslpoweronselftestknownanswertest)
  * 4.4 [Conditional Self-Tests](#conditional-self-tests)
    * 4.4.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.ConditionalSelfTests](#rqsrs-034clickhousefipscompatibleboringsslconditionalselftests)
  * 4.5 [SSL Tests](#ssl-tests)
    * 4.5.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SSLTests](#rqsrs-034clickhousefipscompatibleboringsslssltests)
  * 4.6 [All-tests Utility](#all-tests-utility)
    * 4.6.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.AllTestsUtility](#rqsrs-034clickhousefipscompatibleboringsslalltestsutility)
  * 4.7 [ACVP Check Expected Tests](#acvp-check-expected-tests)
    * 4.7.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.ACVP.CheckExpectedTests](#rqsrs-034clickhousefipscompatibleboringsslacvpcheckexpectedtests)
  * 4.8 [Build Options System Table](#build-options-system-table)
    * 4.8.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SystemTable.BuildOptions](#rqsrs-034clickhousefipscompatibleboringsslsystemtablebuildoptions)
  * 4.9 [MySQL FIPS Function](#mysql-fips-function)
    * 4.9.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.MySQLFunction](#rqsrs-034clickhousefipscompatibleboringsslmysqlfunction)
  * 4.10 [SSL Configuration](#ssl-configuration)
    * 4.10.1 [FIPS Setting](#fips-setting)
      * 4.10.1.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SSL.Client.Config.Settings.FIPS](#rqsrs-034clickhousefipscompatibleboringsslsslclientconfigsettingsfips)
    * 4.10.2 [Server SSL Configuration](#server-ssl-configuration)
      * 4.10.2.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SSL.Server.Config](#rqsrs-034clickhousefipscompatibleboringsslsslserverconfig)
    * 4.10.3 [Client SSL Configuration](#client-ssl-configuration)
      * 4.10.3.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SSL.Client.Config](#rqsrs-034clickhousefipscompatibleboringsslsslclientconfig)
  * 4.11 [Server TCP Connections](#server-tcp-connections)
    * 4.11.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Server.SSL.TCP](#rqsrs-034clickhousefipscompatibleboringsslserverssltcp)
  * 4.12 [Server HTTPS Connections](#server-https-connections)
    * 4.12.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Server.SSL.HTTPS](#rqsrs-034clickhousefipscompatibleboringsslserversslhttps)
  * 4.13 [TCP Clients](#tcp-clients)
    * 4.13.1 [clickhouse-client](#clickhouse-client)
      * 4.13.1.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Clients.SSL.TCP.ClickHouseClient.FIPS](#rqsrs-034clickhousefipscompatibleboringsslclientsssltcpclickhouseclientfips)
      * 4.13.1.2 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Clients.SSL.TCP.ClickHouseClient.NonFIPS](#rqsrs-034clickhousefipscompatibleboringsslclientsssltcpclickhouseclientnonfips)
    * 4.13.2 [Test Python Client](#test-python-client)
      * 4.13.2.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Clients.SSL.TCP.Python](#rqsrs-034clickhousefipscompatibleboringsslclientsssltcppython)
  * 4.14 [HTTPS Clients](#https-clients)
    * 4.14.1 [curl](#curl)
      * 4.14.1.1 [RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Clients.SSL.HTTPS.Curl](#rqsrs-034clickhousefipscompatibleboringsslclientssslhttpscurl)


## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for [ClickHouse] binary that
is statically linked with a [FIPS] compatible [BoringSSL] library.

## Terminology

### KAT

Known Answer Test.

### FIPS

Federal Information Processing Standard.

### ACVP

Automated Cryptographic Validation Protocol.

### FIPS Compatible SSL Connection

[FIPS] compatible SSL connection SHALL be defined as follows:

TLS protocols

```
TLS v1.2
```

using FIPS preferred curves

```
CurveP256
CurveP384
CurveP521
```

and the following cipher suites

```
TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
TLS_RSA_WITH_AES_128_GCM_SHA256
TLS_RSA_WITH_AES_256_GCM_SHA384
```

which when required need to mapped to the corresponding [OpenSSL ciphers] suites.

## Requirements

### General

#### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL
version: 1.0

[ClickHouse] SHALL support running with binary that is statically linked with a [FIPS] compatible [BoringSSL] library.

### BoringSSL Version

#### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Version
version: 1.0

[ClickHouse] SHALL use [BoringSSL] static library build from source code with version `dcdc7bbc6e59ac0123407a9dc4d1f43dd0d117cd`
that includes [FIPS] validated [BoringCrypto] core library for Android that was issued the following
[FIPS 140-2] certificate https://csrc.nist.gov/Projects/Cryptographic-Module-Validation-Program/Certificate/4156
with the following security policy https://csrc.nist.gov/CSRC/media/projects/cryptographic-module-validation-program/documents/security-policies/140sp4156.pdf.

### Power-On Self-Tests

#### Integrity Test

##### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.PowerOnSelfTest.IntegrityTest
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS] compatible [BoringSSL] library that implements power-on integrity self test
using `HMAC-SHA-256` that SHALL verify the signature of the binary.

#### Known Answer Test

##### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.PowerOnSelfTest.KnownAnswerTest
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS] compatible [BoringSSL] library that implements power-on
known answer test (KAT) which SHALL include the following:

Test |
--- |
AES-CBC KAT (encryption and decryption. Key size: 128-bits)
AES-GCM KAT (encryption and decryption. Key size: 128-bits)
Triple-DES TCBC KAT (encryption and decryption. Key size: 168-bits)
ECDSA KAT (signature generation/signature verification. Curve: P-256)
HMAC KAT (HMAC-SHA-1, HMAC-SHA-512)
SP 800-90A CTR_DRBG KAT (Key size: 256-bits)
RSA KAT (signature generation/signature verification and encryption/decryption. Key size: 2048-bit)
TLS v1.2 KDF KAT
KAS-ECC-SSC primitive KAT Curve P-256)
KAS-FFC-SSC primitive KAT (2048-bit)
SHA KAT (SHA-1, SHA-256, SHA-512)

### Conditional Self-Tests

#### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.ConditionalSelfTests
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS] compatible [BoringSSL] library that implements the following conditional
self-tests:

Type | Test
--- | ---
Pair-wise Consistency Test | ECDSA Key Pair generation, RSA Key Pair generation
CRNGT | Performed on the passively received entropy
DRBG Health Tests | Performed on DRBG, per SP 800‐90A Section 11.3. Required per IG C.1. 


### SSL Tests

#### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SSLTests
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS] compatible [BoringSSL] library that passes all
SSL tests as defined by https://github.com/google/boringssl/blob/master/ssl/ssl_test.cc.

For example,

```bash
./ssl/ssl_test
...
[==========] 330 tests from 6 test suites ran. (2410 ms total)
[  PASSED  ] 330 tests.
```

### All-tests Utility

#### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.AllTestsUtility
version: 1.0

[ClickHouse] SHALL be statically linked with [FIPS] compatible [BoringSSL] library that passes all
`util/all_tests.go` tests. 

For example,

```bash
go run util/all_tests.go
...
All tests passed!
```

### ACVP Check Expected Tests

#### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.ACVP.CheckExpectedTests
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS] compatible [BoringSSL] library that passes all
`/util/fipstools/acvp/acvptool/test/check_expected.go` tests.

```bash
./boringssl/util/fipstools/acvp/acvptool/test$ go run check_expected.go -tool ../acvptool -module-wrappers modulewrapper:../../../../../build/util/fipstools/acvp/modulewrapper/modulewrapper,testmodulewrapper:../testmodulewrapper/testmodulewrapper -tests tests.json 
2022/12/14 20:57:26 32 ACVP tests matched expectations
```

### Build Options System Table

#### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SystemTable.BuildOptions
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support
reporting that the binary was build with FIPS enabled [BoringSSL] library
in the `system.build_options` table.

### MySQL FIPS Function

#### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.MySQLFunction
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support
reporting that it is FIPS compliant in the MySQL FIPS function.

### SSL Configuration

#### FIPS Setting

##### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SSL.Client.Config.Settings.FIPS
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support
`<clickhouse><openSSL><fips>` setting in the `config.xml`.

```xml
<clickhouse>
    <openSSL>
        <fips>true</fips>
    </openSSL>
</clickhouse>
```

#### Server SSL Configuration

##### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SSL.Server.Config
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support configuring
server SSL to accept only [FIPS Compatible SSL Connection]s
using the `<clickhouse><openSSL><server>` section in the `config.xml` using the following
settings:

```xml
<clickhouse>
    <openSSL>
        <server> <!-- Used for https server AND secure tcp port -->
            <cipherList>ALL:!ADH:!LOW:!EXP:!MD5:@STRENGTH</cipherList>
            <requireTLSv1>true|false</requireTLSv1>
            <requireTLSv1_1>true|false</requireTLSv1_1>
            <requireTLSv1_2>true|false</requireTLSv1_2>
            <disableProtocols>sslv2,sslv3</disableProtocols>
            <preferServerCiphers>true</preferServerCiphers>
        </server>
    </openSSL>
<clickhouse>
```

#### Client SSL Configuration

##### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.SSL.Client.Config
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support configuring
SSL when server is acting as a client to establish only [FIPS Compatible SSL Connection]s
using the `<clickhouse><openSSL><client>` section in the `config.xml` using the following
settings:

```xml
<clickhouse>
    <openSSL>
        <client> <!-- Used for connecting to https dictionary source and secured Zookeeper communication -->
            <cipherList>ALL:!ADH:!LOW:!EXP:!MD5:@STRENGTH</cipherList>
            <requireTLSv1>true|false</requireTLSv1>
            <requireTLSv1_1>true|false</requireTLSv1_1>
            <requireTLSv1_2>true|false</requireTLSv1_2>
            <disableProtocols>sslv2,sslv3</disableProtocols>
            <preferServerCiphers>true</preferServerCiphers>
        </client>
    </openSSL>
</clickhouse>
```

### Server TCP Connections

#### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Server.SSL.TCP
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support configuring
server to accept only [FIPS Compatible SSL Connection]s native TCP connections.

### Server HTTPS Connections

#### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Server.SSL.HTTPS
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support configuring
server to accept only [FIPS Compatible SSL Connection]s HTTPS connections.

### TCP Clients

#### clickhouse-client

##### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Clients.SSL.TCP.ClickHouseClient.FIPS
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support accepting
connections from FIPS compliant [clickhouse-client] which uses native TCP protocol
that is configured to establish only [FIPS Compatible SSL Connection]s.

##### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Clients.SSL.TCP.ClickHouseClient.NonFIPS
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support accepting
connections from non FIPS compliant [clickhouse-client] which uses native TCP protocol
that is configured to establish only [FIPS Compatible SSL Connection]s.

#### Test Python Client

##### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Clients.SSL.TCP.Python
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support accepting
connections from test Python client which uses native TCP protocol
that is configured to establish only [FIPS Compatible SSL Connection]s.

### HTTPS Clients

#### curl

##### RQ.SRS-034.ClickHouse.FIPS.Compatible.BoringSSL.Clients.SSL.HTTPS.Curl
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support accepting
connections from [curl] used as HTTPS protocol client that is configured to establish only [FIPS Compatible SSL Connection]s.

[FIPS Compatible SSL Connection]: #fips_compatible_ssl_connection
[OpenSSL ciphers]: https://www.openssl.org/docs/man1.1.1/man1/ciphers.html
[curl]: https://curl.se/docs/manpage.html
[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/tree/main/ssl_server/requirements/requirements_fips.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/ssl_server/requirements/requirements_fips.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
[FIPS]: https://csrc.nist.gov/publications/detail/fips/140/2/final
[FIPS 140-2]: https://csrc.nist.gov/publications/detail/fips/140/2/final
[BoringSSL]: https://github.com/google/boringssl/
[BoringCrypto]: https://github.com/google/boringssl/tree/master/crypto
[ACVP]: https://pages.nist.gov/ACVP/
""",
)
