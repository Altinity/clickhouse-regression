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
