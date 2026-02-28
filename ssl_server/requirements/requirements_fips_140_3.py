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

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SelfTest_IntegrityTest = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SelfTest.IntegrityTest",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that implements\n"
        "a pre-operational integrity self-test using `HMAC-SHA-256` (per 140sp4816 Table 21) that SHALL verify\n"
        "the integrity of the `bcm.o` module by comparing a runtime-computed HMAC value against the build-time\n"
        "HMAC value stored within the module.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.1.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SelfTest_CryptographicAlgorithm = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SelfTest.CryptographicAlgorithm",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that implements\n"
        "the following cryptographic algorithm self-tests (CASTs) as listed in 140sp4816 Table 22:\n"
        "\n"
        "Test | Trigger\n"
        "--- | ---\n"
        "AES-CBC KAT (encryption and decryption. Key size: 128-bits) | Power up\n"
        "AES-GCM KAT (encryption and decryption. Key size: 128-bits) | Power up\n"
        "SHA-1 KAT | Power up\n"
        "SHA2-256 KAT | Power up\n"
        "SHA2-512 KAT | Power up\n"
        "HMAC-SHA2-256 KAT | Power up\n"
        "SP 800-90A CTR_DRBG KAT (AES-256) | Power up\n"
        "DRBG Health Test (SP 800-90Ar1 Section 11.3) | Power up\n"
        "ECDSA SigGen KAT (P-256 curve, SHA2-256) | Signature generation or key generation service request\n"
        "ECDSA SigVer KAT (P-256 curve, SHA2-256) | Signature verification or key generation service request\n"
        "KAS-ECC-SSC KAT (P-256 curve) | Shared secret computation request\n"
        "KDF TLS v1.2 KAT (SHA2-256) | Power up\n"
        "KDA HKDF KAT (HMAC-SHA2-256) | Power up\n"
        "PBKDF2 KAT (HMAC-SHA2-256) | Power up\n"
        "RSA SigGen KAT (PKCS#1 v1.5, 2048-bit key, SHA2-256) | Signature generation or key generation service request\n"
        "RSA SigVer KAT (PKCS#1 v1.5, 2048-bit key, SHA2-256) | Signature verification or key generation service request\n"
        "\n"
        "All CASTs can also be invoked on-demand by calling `BORINGSSL_self_test()`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.2.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SelfTest_Conditional = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SelfTest.Conditional",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that implements the following conditional\n"
        "self-tests (per 140sp4816 Table 22):\n"
        "\n"
        "Type | Test | Trigger\n"
        "--- | --- | ---\n"
        "Pair-wise Consistency Test | ECDSA Key Pair generation (sign and verify) | Key generation\n"
        "Pair-wise Consistency Test | RSA Key Pair generation (sign and verify) | Key generation\n"
        "\n"
        "If any self-test fails the module SHALL transition to an error state and abort with `SIGABRT`\n"
        "as described in 140sp4816 Table 25.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.3.1",
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
        "a service indicator as described in 140sp4816 Section 4.3. The service indicator SHALL be used\n"
        "via the following invocation sequence:\n"
        "\n"
        "1. Call `FIPS_service_indicator_before_call()` before invoking the cryptographic service.\n"
        "2. Invoke the cryptographic service.\n"
        "3. Call `FIPS_service_indicator_after_call()` after the service returns.\n"
        "4. Call `FIPS_service_indicator_check_approved(before, after)`.\n"
        "\n"
        "A return value of `1` from `FIPS_service_indicator_check_approved()` SHALL indicate that the invoked\n"
        "cryptographic service is an approved FIPS service.\n"
        "\n"
        "Alternatively, the macro `CALL_SERVICE_AND_CHECK_APPROVED(approved, func)` MAY be used\n"
        "to perform all the above steps in a single call.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.4.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_StartupVerification_FIPSModeCheck = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.StartupVerification.FIPSModeCheck",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL verify that the module\n"
        "is operating in FIPS-approved mode. Per 140sp4816 Section 11.1, running `bssl isfips` SHALL\n"
        "return `1` to confirm the module is installed and configured in a FIPS-compliant manner.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.5.1.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_StartupVerification_VersionString = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.StartupVerification.VersionString",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL verify that the module\n"
        "reports the correct version. Calling the `awslc_version_string()` function SHALL return\n"
        "`AWS-LC FIPS 2.0.0` which confirms the module identity and operational mode as described in\n"
        "140sp4816 Section 11.1.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.5.2.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_StartupVerification_StaticLinking = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.StartupVerification.StaticLinking",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL verify that the module\n"
        "is statically linked into the binary. Running `nm <clickhouse_binary> | grep awslc_version_string`\n"
        "SHALL show a `T` flag in the output, confirming the symbol is present in the text (code) section\n"
        "of the binary rather than being dynamically loaded, as described in 140sp4816 Section 11.1.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.5.3.1",
)

RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_OperationalEnvironment = Requirement(
    name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.OperationalEnvironment",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL NOT be run in an environment\n"
        "where instrumentation tools such as `ptrace`, `gdb`, `strace`, `ftrace`, `systemtap`, or userspace live patching\n"
        "are active, as per 140sp4816 Section 6.2. The use of any such tools SHALL be considered as running\n"
        "the cryptographic module in a non-validated operational environment.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.1",
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
        "SSL tests as defined by the [AWS-LC] source tree at tag `AWS-LC-FIPS-2.0.0`\n"
        "(https://github.com/aws/aws-lc/tree/AWS-LC-FIPS-2.0.0/ssl/test).\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.7.1",
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
        "ACVP validation tests using the `acvptool` and `modulewrapper` utilities provided by [AWS-LC]\n"
        "at tag `AWS-LC-FIPS-2.0.0`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.8.1",
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
    num="4.9.1",
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
    num="4.10.1",
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
    num="4.11.1.1",
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
    num="4.11.2.1",
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
    num="4.11.3.1",
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
    num="4.12.1",
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
    num="4.13.1",
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
    num="4.14.1.1",
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
    num="4.14.1.2",
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
    num="4.14.2.1",
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
        "[140sp4816]: https://csrc.nist.gov/CSRC/media/projects/cryptographic-module-validation-program/documents/security-policies/140sp4816.pdf\n"
    ),
    link=None,
    level=4,
    num="4.15.1.1",
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
        Heading(name="Self-Tests", level=2, num="4.3"),
        Heading(name="Pre-Operational Integrity Test", level=3, num="4.3.1"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SelfTest.IntegrityTest",
            level=4,
            num="4.3.1.1",
        ),
        Heading(name="Cryptographic Algorithm Self-Tests", level=3, num="4.3.2"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SelfTest.CryptographicAlgorithm",
            level=4,
            num="4.3.2.1",
        ),
        Heading(name="Conditional Self-Tests", level=3, num="4.3.3"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SelfTest.Conditional",
            level=4,
            num="4.3.3.1",
        ),
        Heading(name="Service Indicator", level=2, num="4.4"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ServiceIndicator",
            level=3,
            num="4.4.1",
        ),
        Heading(name="Startup Verification", level=2, num="4.5"),
        Heading(name="FIPS Mode Check", level=3, num="4.5.1"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.StartupVerification.FIPSModeCheck",
            level=4,
            num="4.5.1.1",
        ),
        Heading(name="Version String", level=3, num="4.5.2"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.StartupVerification.VersionString",
            level=4,
            num="4.5.2.1",
        ),
        Heading(name="Static Linking Verification", level=3, num="4.5.3"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.StartupVerification.StaticLinking",
            level=4,
            num="4.5.3.1",
        ),
        Heading(name="Operational Environment", level=2, num="4.6"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.OperationalEnvironment",
            level=3,
            num="4.6.1",
        ),
        Heading(name="SSL Tests", level=2, num="4.7"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSLTests",
            level=3,
            num="4.7.1",
        ),
        Heading(name="ACVP Check Expected Tests", level=2, num="4.8"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ACVP.CheckExpectedTests",
            level=3,
            num="4.8.1",
        ),
        Heading(name="Build Options System Table", level=2, num="4.9"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SystemTable.BuildOptions",
            level=3,
            num="4.9.1",
        ),
        Heading(name="MySQL FIPS Function", level=2, num="4.10"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.MySQLFunction",
            level=3,
            num="4.10.1",
        ),
        Heading(name="SSL Configuration", level=2, num="4.11"),
        Heading(name="FIPS Setting", level=3, num="4.11.1"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Client.Config.Settings.FIPS",
            level=4,
            num="4.11.1.1",
        ),
        Heading(name="Server SSL Configuration", level=3, num="4.11.2"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Server.Config",
            level=4,
            num="4.11.2.1",
        ),
        Heading(name="Client SSL Configuration", level=3, num="4.11.3"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Client.Config",
            level=4,
            num="4.11.3.1",
        ),
        Heading(name="Server TCP Connections", level=2, num="4.12"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Server.SSL.TCP",
            level=3,
            num="4.12.1",
        ),
        Heading(name="Server HTTPS Connections", level=2, num="4.13"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Server.SSL.HTTPS",
            level=3,
            num="4.13.1",
        ),
        Heading(name="TCP Clients", level=2, num="4.14"),
        Heading(name="clickhouse-client", level=3, num="4.14.1"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.ClickHouseClient.FIPS",
            level=4,
            num="4.14.1.1",
        ),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.ClickHouseClient.NonFIPS",
            level=4,
            num="4.14.1.2",
        ),
        Heading(name="Test Python Client", level=3, num="4.14.2"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.Python",
            level=4,
            num="4.14.2.1",
        ),
        Heading(name="HTTPS Clients", level=2, num="4.15"),
        Heading(name="curl", level=3, num="4.15.1"),
        Heading(
            name="RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.HTTPS.Curl",
            level=4,
            num="4.15.1.1",
        ),
    ),
    requirements=(
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_Version,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SelfTest_IntegrityTest,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SelfTest_CryptographicAlgorithm,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_SelfTest_Conditional,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_ServiceIndicator,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_StartupVerification_FIPSModeCheck,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_StartupVerification_VersionString,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_StartupVerification_StaticLinking,
        RQ_SRS_035_ClickHouse_FIPS_Compatible_AWSLC_OperationalEnvironment,
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
    * 4.3 [Self-Tests](#self-tests)
        * 4.3.1 [Pre-Operational Integrity Test](#pre-operational-integrity-test)
            * 4.3.1.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SelfTest.IntegrityTest](#rqsrs-035clickhousefipscompatibleawslcselftestintegritytest)
        * 4.3.2 [Cryptographic Algorithm Self-Tests](#cryptographic-algorithm-self-tests)
            * 4.3.2.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SelfTest.CryptographicAlgorithm](#rqsrs-035clickhousefipscompatibleawslcselftestcryptographicalgorithm)
        * 4.3.3 [Conditional Self-Tests](#conditional-self-tests)
            * 4.3.3.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SelfTest.Conditional](#rqsrs-035clickhousefipscompatibleawslcselftestconditional)
    * 4.4 [Service Indicator](#service-indicator)
        * 4.4.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ServiceIndicator](#rqsrs-035clickhousefipscompatibleawslcserviceindicator)
    * 4.5 [Startup Verification](#startup-verification)
        * 4.5.1 [FIPS Mode Check](#fips-mode-check)
            * 4.5.1.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.StartupVerification.FIPSModeCheck](#rqsrs-035clickhousefipscompatibleawslcstartupverificationfipsmodecheck)
        * 4.5.2 [Version String](#version-string)
            * 4.5.2.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.StartupVerification.VersionString](#rqsrs-035clickhousefipscompatibleawslcstartupverificationversionstring)
        * 4.5.3 [Static Linking Verification](#static-linking-verification)
            * 4.5.3.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.StartupVerification.StaticLinking](#rqsrs-035clickhousefipscompatibleawslcstartupverificationstaticlinking)
    * 4.6 [Operational Environment](#operational-environment)
        * 4.6.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.OperationalEnvironment](#rqsrs-035clickhousefipscompatibleawslcoperationalenvironment)
    * 4.7 [SSL Tests](#ssl-tests)
        * 4.7.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSLTests](#rqsrs-035clickhousefipscompatibleawslcssltests)
    * 4.8 [ACVP Check Expected Tests](#acvp-check-expected-tests)
        * 4.8.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ACVP.CheckExpectedTests](#rqsrs-035clickhousefipscompatibleawslcacvpcheckexpectedtests)
    * 4.9 [Build Options System Table](#build-options-system-table)
        * 4.9.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SystemTable.BuildOptions](#rqsrs-035clickhousefipscompatibleawslcsystemtablebuildoptions)
    * 4.10 [MySQL FIPS Function](#mysql-fips-function)
        * 4.10.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.MySQLFunction](#rqsrs-035clickhousefipscompatibleawslcmysqlfunction)
    * 4.11 [SSL Configuration](#ssl-configuration)
        * 4.11.1 [FIPS Setting](#fips-setting)
            * 4.11.1.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Client.Config.Settings.FIPS](#rqsrs-035clickhousefipscompatibleawslcsslclientconfigsettingsfips)
        * 4.11.2 [Server SSL Configuration](#server-ssl-configuration)
            * 4.11.2.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Server.Config](#rqsrs-035clickhousefipscompatibleawslcsslserverconfig)
        * 4.11.3 [Client SSL Configuration](#client-ssl-configuration)
            * 4.11.3.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSL.Client.Config](#rqsrs-035clickhousefipscompatibleawslcsslclientconfig)
    * 4.12 [Server TCP Connections](#server-tcp-connections)
        * 4.12.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Server.SSL.TCP](#rqsrs-035clickhousefipscompatibleawslcserverssltcp)
    * 4.13 [Server HTTPS Connections](#server-https-connections)
        * 4.13.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Server.SSL.HTTPS](#rqsrs-035clickhousefipscompatibleawslcserversslhttps)
    * 4.14 [TCP Clients](#tcp-clients)
        * 4.14.1 [clickhouse-client](#clickhouse-client)
            * 4.14.1.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.ClickHouseClient.FIPS](#rqsrs-035clickhousefipscompatibleawslcclientsssltcpclickhouseclientfips)
            * 4.14.1.2 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.ClickHouseClient.NonFIPS](#rqsrs-035clickhousefipscompatibleawslcclientsssltcpclickhouseclientnonfips)
        * 4.14.2 [Test Python Client](#test-python-client)
            * 4.14.2.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.TCP.Python](#rqsrs-035clickhousefipscompatibleawslcclientsssltcppython)
    * 4.15 [HTTPS Clients](#https-clients)
        * 4.15.1 [curl](#curl)
            * 4.15.1.1 [RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.Clients.SSL.HTTPS.Curl](#rqsrs-035clickhousefipscompatibleawslcclientssslhttpscurl)


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

Note: ECDSA cipher suites (`TLS_ECDHE_ECDSA_WITH_*`) are applicable when the server certificate
and key pair use ECDSA. RSA cipher suites (`TLS_ECDHE_RSA_WITH_*`, `TLS_RSA_WITH_*`)
are applicable when the server certificate and key pair use RSA.

Which, when required, need to be mapped to the corresponding [OpenSSL ciphers] suites.

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

### Self-Tests

The self-tests described in this section correspond to the requirements of 140sp4816 Section 10
(Tables 21, 22). Under [FIPS 140-3], CASTs replace the power-on KATs from [FIPS 140-2].

#### Pre-Operational Integrity Test

##### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SelfTest.IntegrityTest
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that implements
a pre-operational integrity self-test using `HMAC-SHA-256` (per 140sp4816 Table 21) that SHALL verify
the integrity of the `bcm.o` module by comparing a runtime-computed HMAC value against the build-time
HMAC value stored within the module.

#### Cryptographic Algorithm Self-Tests

##### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SelfTest.CryptographicAlgorithm
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that implements
the following cryptographic algorithm self-tests (CASTs) as listed in 140sp4816 Table 22:

Test | Trigger
--- | ---
AES-CBC KAT (encryption and decryption. Key size: 128-bits) | Power up
AES-GCM KAT (encryption and decryption. Key size: 128-bits) | Power up
SHA-1 KAT | Power up
SHA2-256 KAT | Power up
SHA2-512 KAT | Power up
HMAC-SHA2-256 KAT | Power up
SP 800-90A CTR_DRBG KAT (AES-256) | Power up
DRBG Health Test (SP 800-90Ar1 Section 11.3) | Power up
ECDSA SigGen KAT (P-256 curve, SHA2-256) | Signature generation or key generation service request
ECDSA SigVer KAT (P-256 curve, SHA2-256) | Signature verification or key generation service request
KAS-ECC-SSC KAT (P-256 curve) | Shared secret computation request
KDF TLS v1.2 KAT (SHA2-256) | Power up
KDA HKDF KAT (HMAC-SHA2-256) | Power up
PBKDF2 KAT (HMAC-SHA2-256) | Power up
RSA SigGen KAT (PKCS#1 v1.5, 2048-bit key, SHA2-256) | Signature generation or key generation service request
RSA SigVer KAT (PKCS#1 v1.5, 2048-bit key, SHA2-256) | Signature verification or key generation service request

All CASTs can also be invoked on-demand by calling `BORINGSSL_self_test()`.

#### Conditional Self-Tests

##### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SelfTest.Conditional
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that implements the following conditional
self-tests (per 140sp4816 Table 22):

Type | Test | Trigger
--- | --- | ---
Pair-wise Consistency Test | ECDSA Key Pair generation (sign and verify) | Key generation
Pair-wise Consistency Test | RSA Key Pair generation (sign and verify) | Key generation

If any self-test fails the module SHALL transition to an error state and abort with `SIGABRT`
as described in 140sp4816 Table 25.

### Service Indicator

#### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ServiceIndicator
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that provides
a service indicator as described in 140sp4816 Section 4.3. The service indicator SHALL be used
via the following invocation sequence:

1. Call `FIPS_service_indicator_before_call()` before invoking the cryptographic service.
2. Invoke the cryptographic service.
3. Call `FIPS_service_indicator_after_call()` after the service returns.
4. Call `FIPS_service_indicator_check_approved(before, after)`.

A return value of `1` from `FIPS_service_indicator_check_approved()` SHALL indicate that the invoked
cryptographic service is an approved FIPS service.

Alternatively, the macro `CALL_SERVICE_AND_CHECK_APPROVED(approved, func)` MAY be used
to perform all the above steps in a single call.

### Startup Verification

#### FIPS Mode Check

##### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.StartupVerification.FIPSModeCheck
version: 1.0

[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL verify that the module
is operating in FIPS-approved mode. Per 140sp4816 Section 11.1, running `bssl isfips` SHALL
return `1` to confirm the module is installed and configured in a FIPS-compliant manner.

#### Version String

##### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.StartupVerification.VersionString
version: 1.0

[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL verify that the module
reports the correct version. Calling the `awslc_version_string()` function SHALL return
`AWS-LC FIPS 2.0.0` which confirms the module identity and operational mode as described in
140sp4816 Section 11.1.

#### Static Linking Verification

##### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.StartupVerification.StaticLinking
version: 1.0

[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL verify that the module
is statically linked into the binary. Running `nm <clickhouse_binary> | grep awslc_version_string`
SHALL show a `T` flag in the output, confirming the symbol is present in the text (code) section
of the binary rather than being dynamically loaded, as described in 140sp4816 Section 11.1.

### Operational Environment

#### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.OperationalEnvironment
version: 1.0

[ClickHouse] with statically linked [FIPS 140-3] compatible [AWS-LC] SHALL NOT be run in an environment
where instrumentation tools such as `ptrace`, `gdb`, `strace`, `ftrace`, `systemtap`, or userspace live patching
are active, as per 140sp4816 Section 6.2. The use of any such tools SHALL be considered as running
the cryptographic module in a non-validated operational environment.

### SSL Tests

#### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.SSLTests
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that passes all
SSL tests as defined by the [AWS-LC] source tree at tag `AWS-LC-FIPS-2.0.0`
(https://github.com/aws/aws-lc/tree/AWS-LC-FIPS-2.0.0/ssl/test).

### ACVP Check Expected Tests

#### RQ.SRS-035.ClickHouse.FIPS.Compatible.AWSLC.ACVP.CheckExpectedTests
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS 140-3] compatible [AWS-LC] library that passes all
ACVP validation tests using the `acvptool` and `modulewrapper` utilities provided by [AWS-LC]
at tag `AWS-LC-FIPS-2.0.0`.

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
[140sp4816]: https://csrc.nist.gov/CSRC/media/projects/cryptographic-module-validation-program/documents/security-policies/140sp4816.pdf
""",
)
