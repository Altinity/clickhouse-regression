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
