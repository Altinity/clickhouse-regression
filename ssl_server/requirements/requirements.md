# SRS017 ClickHouse SSL
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Terminology](#terminology)
  * 2.1 [SSL Protocol](#ssl-protocol)
  * 2.2 [TLS Protocol](#tls-protocol)
  * 2.3 [KAT](#kat)
  * 2.4 [FIPS](#fips)
  * 2.5 [ACVP](#acvp)
  * 2.6 [FIPS Compatible SSL Connection](#fips-compatible-ssl-connection)
* 3 [Requirements](#requirements)
  * 3.1 [Secure Connections](#secure-connections)
    * 3.1.1 [RQ.SRS-017.ClickHouse.SSL.Server.HTTPS.Port](#rqsrs-017clickhousesslserverhttpsport)
    * 3.1.2 [RQ.SRS-017.ClickHouse.SSL.Server.TCP.Port](#rqsrs-017clickhousesslservertcpport)
  * 3.2 [Protocols](#protocols)
    * 3.2.1 [Disabling](#disabling)
      * 3.2.1.1 [RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Disable](#rqsrs-017clickhousesslserverprotocolsdisable)
      * 3.2.1.2 [RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Disable.SSLv2](#rqsrs-017clickhousesslserverprotocolsdisablesslv2)
      * 3.2.1.3 [RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Disable.SSLv3](#rqsrs-017clickhousesslserverprotocolsdisablesslv3)
      * 3.2.1.4 [RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Disable.TLSv1](#rqsrs-017clickhousesslserverprotocolsdisabletlsv1)
      * 3.2.1.5 [RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Disable.TLSv1_1](#rqsrs-017clickhousesslserverprotocolsdisabletlsv1_1)
      * 3.2.1.6 [RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Disable.TLSv1_2](#rqsrs-017clickhousesslserverprotocolsdisabletlsv1_2)
      * 3.2.1.7 [RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Disable.TLSv1_3.NotAllowed](#rqsrs-017clickhousesslserverprotocolsdisabletlsv1_3notallowed)
    * 3.2.2 [Require TLS](#require-tls)
      * 3.2.2.1 [RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Require.TLS](#rqsrs-017clickhousesslserverprotocolsrequiretls)
      * 3.2.2.2 [RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Require.TLSv1](#rqsrs-017clickhousesslserverprotocolsrequiretlsv1)
      * 3.2.2.3 [RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Require.TLSv1_1](#rqsrs-017clickhousesslserverprotocolsrequiretlsv1_1)
      * 3.2.2.4 [RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Require.TLSv1_2](#rqsrs-017clickhousesslserverprotocolsrequiretlsv1_2)
      * 3.2.2.5 [RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Require.TLSv1_3](#rqsrs-017clickhousesslserverprotocolsrequiretlsv1_3)
  * 3.3 [Cipher Suites](#cipher-suites)
    * 3.3.1 [Cipher List](#cipher-list)
      * 3.3.1.1 [RQ.SRS-017.ClickHouse.SSL.Server.CipherSuites](#rqsrs-017clickhousesslserverciphersuites)
    * 3.3.2 [Prefer Server Ciphers](#prefer-server-ciphers)
      * 3.3.2.1 [RQ.SRS-017.ClickHouse.SSL.Server.CipherSuites.PreferServerCiphers](#rqsrs-017clickhousesslserverciphersuitespreferserverciphers)
    * 3.3.3 [ECDH Curve](#ecdh-curve)
      * 3.3.3.1 [RQ.SRS-017.ClickHouse.SSL.Server.CipherSuites.ECDHCurve](#rqsrs-017clickhousesslserverciphersuitesecdhcurve)
      * 3.3.3.2 [RQ.SRS-017.ClickHouse.SSL.Server.CipherSuites.ECDHCurve.DefaultValue](#rqsrs-017clickhousesslserverciphersuitesecdhcurvedefaultvalue)
  * 3.4 [FIPS Compatible Binary](#fips-compatible-binary)
    * 3.4.1 [RQ.SRS-017.ClickHouse.SSL.Server.FIPS.Compatible.LogMessage](#rqsrs-017clickhousesslserverfipscompatiblelogmessage)
    * 3.4.2 [RQ.SRS-017.ClickHouse.SSL.Server.FIPS.Compatible.ApprovedSecurityFunctions](#rqsrs-017clickhousesslserverfipscompatibleapprovedsecurityfunctions)
    * 3.4.3 [RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL](#rqsrs-034clickhousesslserverfipscompatibleboringssl)
    * 3.4.4 [BoringSSL Version](#boringssl-version)
      * 3.4.4.1 [RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.Version](#rqsrs-034clickhousesslserverfipscompatibleboringsslversion)
    * 3.4.5 [Power-On Self-Tests](#power-on-self-tests)
      * 3.4.5.1 [Integrity Test](#integrity-test)
        * 3.4.5.1.1 [RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.PowerOnSelfTest.IntegrityTest](#rqsrs-034clickhousesslserverfipscompatibleboringsslpoweronselftestintegritytest)
      * 3.4.5.2 [Known Answer Test](#known-answer-test)
        * 3.4.5.2.1 [RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.PowerOnSelfTest.KnownAnswerTest](#rqsrs-034clickhousesslserverfipscompatibleboringsslpoweronselftestknownanswertest)
    * 3.4.6 [Conditional Self-Tests](#conditional-self-tests)
      * 3.4.6.1 [RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.ConditionalSelfTests](#rqsrs-034clickhousesslserverfipscompatibleboringsslconditionalselftests)
    * 3.4.7 [SSL Tests](#ssl-tests)
      * 3.4.7.1 [RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.SSLTests](#rqsrs-034clickhousesslserverfipscompatibleboringsslssltests)
    * 3.4.8 [All-tests Utility](#all-tests-utility)
      * 3.4.8.1 [RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.AllTestsUtility](#rqsrs-034clickhousesslserverfipscompatibleboringsslalltestsutility)
    * 3.4.9 [ACVP Check Expected Tests](#acvp-check-expected-tests)
      * 3.4.9.1 [RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.ACVP.CheckExpectedTests](#rqsrs-034clickhousesslserverfipscompatibleboringsslacvpcheckexpectedtests)
    * 3.4.10 [Build Options System Table](#build-options-system-table)
      * 3.4.10.1 [RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.SystemTable.BuildOptions](#rqsrs-034clickhousesslserverfipscompatibleboringsslsystemtablebuildoptions)
    * 3.4.11 [MySQL FIPS Function](#mysql-fips-function)
      * 3.4.11.1 [RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.MySQLFunction](#rqsrs-034clickhousesslserverfipscompatibleboringsslmysqlfunction)
    * 3.4.12 [SSL Configuration](#ssl-configuration)
      * 3.4.12.1 [FIPS Setting](#fips-setting)
        * 3.4.12.1.1 [RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.SSL.Client.Config.Settings.FIPS](#rqsrs-034clickhousesslserverfipscompatibleboringsslsslclientconfigsettingsfips)
      * 3.4.12.2 [Server SSL Configuration](#server-ssl-configuration)
        * 3.4.12.2.1 [RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.SSL.Server.Config](#rqsrs-034clickhousesslserverfipscompatibleboringsslsslserverconfig)
      * 3.4.12.3 [Client SSL Configuration](#client-ssl-configuration)
        * 3.4.12.3.1 [RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.Client.Config](#rqsrs-034clickhousesslserverfipscompatibleboringsslclientconfig)
    * 3.4.13 [Server TCP Connections](#server-tcp-connections)
      * 3.4.13.1 [RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.Server.TCP](#rqsrs-034clickhousesslserverfipscompatibleboringsslservertcp)
    * 3.4.14 [Server HTTPS Connections](#server-https-connections)
      * 3.4.14.1 [RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.Server.HTTPS](#rqsrs-034clickhousesslserverfipscompatibleboringsslserverhttps)
    * 3.4.15 [TCP Clients](#tcp-clients)
      * 3.4.15.1 [clickhouse-client](#clickhouse-client)
        * 3.4.15.1.1 [RQ.SRS-034.ClickHouse.SSL.FIPS.Compatible.BoringSSL.Clients.TCP.ClickHouseClient.FIPS](#rqsrs-034clickhousesslfipscompatibleboringsslclientstcpclickhouseclientfips)
        * 3.4.15.1.2 [RQ.SRS-034.ClickHouse.SSL.FIPS.Compatible.BoringSSL.Clients.TCP.ClickHouseClient.NonFIPS](#rqsrs-034clickhousesslfipscompatibleboringsslclientstcpclickhouseclientnonfips)
      * 3.4.15.2 [Test Python Client](#test-python-client)
        * 3.4.15.2.1 [RQ.SRS-034.ClickHouse.SSL.FIPS.Compatible.BoringSSL.Clients.TCP.Python](#rqsrs-034clickhousesslfipscompatibleboringsslclientstcppython)
    * 3.4.16 [HTTPS Clients](#https-clients)
      * 3.4.16.1 [curl](#curl)
        * 3.4.16.1.1 [RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.Clients.HTTPS.Curl](#rqsrs-034clickhousesslserverfipscompatibleboringsslclientshttpscurl)
  * 3.5 [Diffie-Hellman (DH) Parameters](#diffie-hellman-dh-parameters)
    * 3.5.1 [RQ.SRS-017.ClickHouse.SSL.Server.DH.Parameters](#rqsrs-017clickhousesslserverdhparameters)
  * 3.6 [Certificates](#certificates)
    * 3.6.1 [Private Key](#private-key)
      * 3.6.1.1 [RQ.SRS-017.ClickHouse.SSL.Server.Certificates.PrivateKey](#rqsrs-017clickhousesslservercertificatesprivatekey)
      * 3.6.1.2 [Private Key Handler](#private-key-handler)
        * 3.6.1.2.1 [RQ.SRS-017.ClickHouse.SSL.Server.Certificates.PrivateKeyHandler](#rqsrs-017clickhousesslservercertificatesprivatekeyhandler)
        * 3.6.1.2.2 [RQ.SRS-017.ClickHouse.SSL.Server.Certificates.PrivateKeyHandler.Password](#rqsrs-017clickhousesslservercertificatesprivatekeyhandlerpassword)
    * 3.6.2 [Certificate](#certificate)
      * 3.6.2.1 [RQ.SRS-017.ClickHouse.SSL.Server.Certificates.Certificate](#rqsrs-017clickhousesslservercertificatescertificate)
    * 3.6.3 [CA Certificates](#ca-certificates)
      * 3.6.3.1 [Config](#config)
        * 3.6.3.1.1 [RQ.SRS-017.ClickHouse.SSL.Server.Certificates.CAConfig](#rqsrs-017clickhousesslservercertificatescaconfig)
      * 3.6.3.2 [Default](#default)
        * 3.6.3.2.1 [RQ.SRS-017.ClickHouse.SSL.Server.Certificates.LoadDefaultCAFile](#rqsrs-017clickhousesslservercertificatesloaddefaultcafile)
    * 3.6.4 [Verification](#verification)
      * 3.6.4.1 [Mode](#mode)
        * 3.6.4.1.1 [RQ.SRS-017.ClickHouse.SSL.Server.Certificates.VerificationMode](#rqsrs-017clickhousesslservercertificatesverificationmode)
        * 3.6.4.1.2 [RQ.SRS-017.ClickHouse.SSL.Server.Certificates.VerificationMode.None](#rqsrs-017clickhousesslservercertificatesverificationmodenone)
        * 3.6.4.1.3 [RQ.SRS-017.ClickHouse.SSL.Server.Certificates.VerificationMode.Relaxed](#rqsrs-017clickhousesslservercertificatesverificationmoderelaxed)
        * 3.6.4.1.4 [RQ.SRS-017.ClickHouse.SSL.Server.Certificates.VerificationMode.Strict](#rqsrs-017clickhousesslservercertificatesverificationmodestrict)
        * 3.6.4.1.5 [RQ.SRS-017.ClickHouse.SSL.Server.Certificates.VerificationMode.Once](#rqsrs-017clickhousesslservercertificatesverificationmodeonce)
      * 3.6.4.2 [Extended Mode](#extended-mode)
        * 3.6.4.2.1 [RQ.SRS-017.ClickHouse.SSL.Server.Certificates.VerificationExtended](#rqsrs-017clickhousesslservercertificatesverificationextended)
      * 3.6.4.3 [Depth](#depth)
        * 3.6.4.3.1 [RQ.SRS-017.ClickHouse.SSL.Server.Certificates.VerificationDepth](#rqsrs-017clickhousesslservercertificatesverificationdepth)
    * 3.6.5 [Invalid Certificate Handler](#invalid-certificate-handler)
      * 3.6.5.1 [RQ.SRS-017.ClickHouse.SSL.Server.Certificates.InvalidCertificateHandler](#rqsrs-017clickhousesslservercertificatesinvalidcertificatehandler)
    * 3.6.6 [User Authentication](#user-authentication)
      * 3.6.6.1 [RQ.SRS-017.ClickHouse.SSL.Server.Certificates.UserAuthentication](#rqsrs-017clickhousesslservercertificatesuserauthentication)
  * 3.7 [Session](#session)
    * 3.7.1 [RQ.SRS-017.ClickHouse.SSL.Server.Session.Cache](#rqsrs-017clickhousesslserversessioncache)
    * 3.7.2 [RQ.SRS-017.ClickHouse.SSL.Server.Session.CacheSize](#rqsrs-017clickhousesslserversessioncachesize)
    * 3.7.3 [RQ.SRS-017.ClickHouse.SSL.Server.Session.IdContext](#rqsrs-017clickhousesslserversessionidcontext)
    * 3.7.4 [RQ.SRS-017.ClickHouse.SSL.Server.Session.Timeout](#rqsrs-017clickhousesslserversessiontimeout)
  * 3.8 [Dynamic SSL Context](#dynamic-ssl-context)
      * 3.8.4.1 [RQ.SRS-017.ClickHouse.SSL.Server.DynamicContext.Reload](#rqsrs-017clickhousesslserverdynamiccontextreload)
    * 3.8.5 [Certificate Reload](#certificate-reload)
      * 3.8.5.1 [RQ.SRS-017.ClickHouse.SSL.Server.DynamicContext.Certificate.Reload](#rqsrs-017clickhousesslserverdynamiccontextcertificatereload)
    * 3.8.6 [Private Key Reload](#private-key-reload)
      * 3.8.6.1 [RQ.SRS-017.ClickHouse.SSL.Server.DynamicContext.PrivateKey.Reload](#rqsrs-017clickhousesslserverdynamiccontextprivatekeyreload)

## Introduction

This software requirements specification covers requirements related to [ClickHouse] acting as
a [SSL] server for secure [HTTPS] and [TCP] connections between a database
client and [ClickHouse] server.

## Terminology

### SSL Protocol

* Secure Sockets Layer ([SSL])

### TLS Protocol

* Transport Layer Security (successor to the [SSL Protocol])

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

### Secure Connections

#### RQ.SRS-017.ClickHouse.SSL.Server.HTTPS.Port
version: 1.0

[ClickHouse] SHALL support acting as a [SSL] server to provide secure client connections
over the [HTTPS] port.

#### RQ.SRS-017.ClickHouse.SSL.Server.TCP.Port
version: 1.0

[ClickHouse] SHALL support acting as a [SSL] server to provide secure client connections
over secure [TCP] port.

### Protocols

#### Disabling

##### RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Disable
version: 1.0

[ClickHouse] SHALL support disabling protocols using
the `<disbaleProtocols>` parameter in the `<clickhouse><openSSL><server>` section
of the config.xml. Multiple protocols SHALL be specified using the comma
`,` character as a separator. Any handshakes using one of the
disabled protocol SHALL fail and downgrading to these protocols SHALL not be allowed.

```xml
<clickhouse>
    <openSSL>
        <server>
            ...
            <disableProtocols>sslv2,sslv3</disableProtocols>
        </server>
    </openSSL>
</clickhouse>
```

##### RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Disable.SSLv2
version: 1.0

[ClickHouse] SHALL support disabling vulnerable `SSLv2`
using the `sslv2` as the protocol name in the `<disableProtocols>` parameter.

##### RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Disable.SSLv3
version: 1.0

[ClickHouse] SHALL support disabling vulnerable `SSLv3`
using the `sslv3` as the protocol name in the `<disableProtocols>` parameter.

##### RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Disable.TLSv1
version: 1.0

[ClickHouse] SHALL support disabling vulnerable `TLSv1`
using the `tlsv1` as the protocol name in the `<disableProtocols>` parameter.

##### RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Disable.TLSv1_1
version: 1.0

[ClickHouse] SHALL support disabling `TLSv1_1`
using the `tlsv1_1` as the protocol name in the `<disableProtocols>` parameter.

##### RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Disable.TLSv1_2
version: 1.0

[ClickHouse] SHALL support disabling `TLSv1_2`
using the `tlsv1_2` as the protocol name in the `<disableProtocols>` parameter.

##### RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Disable.TLSv1_3.NotAllowed
version: 1.0

[ClickHouse] SHALL not support disabling `TLSv1_3` protocol and if
the `tlsv1_3` is specified as the protocol name in the `<disableProtocols>` parameter
then an error SHALL be returned.

#### Require TLS

##### RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Require.TLS
version: 1.0

[ClickHouse] SHALL support requiring specific TLS protocol version
using parameters in the `<clickhouse><openSSL><server>` section
of the `config.xml` and when specified SHALL only establish
the connection if and only if the required protocol version will be used
without downgrading.

##### RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Require.TLSv1
version: 1.0

[ClickHouse] SHALL support requiring `TLSv1` connection
using the `<requireTLSv1>` parameter to boolean `true`.

##### RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Require.TLSv1_1
version: 1.0

[ClickHouse] SHALL support requiring `TLSv1.1` connection
using the `<requireTLSv1_1>` parameter to boolean `true`.

##### RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Require.TLSv1_2
version: 1.0

[ClickHouse] SHALL support requiring `TLSv1.2` connection
using the `<requireTLSv1_2>` parameter to boolean `true`.

##### RQ.SRS-017.ClickHouse.SSL.Server.Protocols.Require.TLSv1_3
version: 1.0

[ClickHouse] SHALL support requiring `TLSv1.3` connection
using the `<requireTLSv1_3>` parameter to boolean `true`.

### Cipher Suites

#### Cipher List

##### RQ.SRS-017.ClickHouse.SSL.Server.CipherSuites
version: 1.0

[ClickHouse] SHALL support specifying cipher suites to be used
for [SSL] connection using the `<cipherList>` parameter
in form of a string that SHALL use [OpenSSL cipher list format] notation
```
(e.g. "ALL:!ADH:!LOW:!EXP:!MD5:@STRENGTH")
```
in the `<clickhouse><openSSL><server>` section
of the `config.xml` and when specified the server SHALL only establish
the connection if and only if one of the specified cipher suites
will be used for the connection without downgrading.

```xml
<clickhouse>
    <openSSL>
        <server>
            ...
            <cipherList>ALL:!ADH:!LOW:!EXP:!MD5:@STRENGTH</cipherList>
        </server>
    </openSSL>
</clickhouse>
```

#### Prefer Server Ciphers

##### RQ.SRS-017.ClickHouse.SSL.Server.CipherSuites.PreferServerCiphers
version: 1.0

[ClickHouse] SHALL use own cipher suite preferences when
the `<preferServerCiphers>` in the `<clickhouse><openSSL><server>` section
of the `config.xml` is set to `true`.

```xml
<clickhouse>
    <openSSL>
        <server>
            ...
            <preferServerCiphers>true</preferServerCiphers>
        </server>
    </openSSL>
</clickhouse>
```

#### ECDH Curve

##### RQ.SRS-017.ClickHouse.SSL.Server.CipherSuites.ECDHCurve
version: 1.0

[ClickHouse] SHALL support specifying the curve to be used for [ECDH] key agreement protocol
using the `<ecdhCurve>` parameter in the `<clickhouse><openSSL><server>` section
of the `config.xml` that SHALL contain one of the name of the
the curves specified in the [RFC 4492].

```xml
<clickhouse>
    <openSSL>
        <server>
            ...
            <ecdhCurve>prime256v1</ecdhCurve>
        </server>
    </openSSL>
</clickhouse>
```

##### RQ.SRS-017.ClickHouse.SSL.Server.CipherSuites.ECDHCurve.DefaultValue
version: 1.0

[ClickHouse] SHALL use the `prime256v1` as the default value
for the `<ecdhCurve>` parameter in the `<clickhouse><openSSL><server>` section
of the `config.xml` that SHALL force the server to use the corresponding
curve for establishing [Shared Secret] using the [ECDH] key agreement protocol.

### FIPS Compatible Binary

#### RQ.SRS-017.ClickHouse.SSL.Server.FIPS.Compatible.LogMessage
version: 1.0

[ClickHouse] SHALL provide the following message in `/var/log/clickhouse-server/clickhouse-server.log`
when ClickHouse is started from a FIPS compatible binary:

```
<Information> Application: Starting in FIPS mode, KAT test result: 1
```

#### RQ.SRS-017.ClickHouse.SSL.Server.FIPS.Compatible.ApprovedSecurityFunctions
version: 1.0

[ClickHouse] SHALL only support the use of security functions
approved by [FIPS 140-2] when [FIPS Mode] is enabled.

* Symmetric Key Encryption and Decryption
  * AES
  * TDEA

* Digital Signatures
  * DSS

* Secure Hash Standard
  * SHA-1
  * SHA-224
  * SHA-256
  * SHA-384
  * SHA-512
  * SHA-512/224
  * SHA-512/256

* SHA-3 Standard
  * SHA3-224
  * SHA3-256
  * SHA3-384
  * SHA3-512
  * SHAKE128
  * SHAKE256
  * cSHAKE
  * KMAC
  * TupleHash
  * ParallelHash

* Message Authentication
  * Triple-DES
  * AES
  * HMAC

#### RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL
version: 1.0

[ClickHouse] SHALL support running with binary that is statically linked with a [FIPS] compatible [BoringSSL] library.

#### BoringSSL Version

##### RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.Version
version: 1.0

[ClickHouse] SHALL use [BoringSSL] static library build from source code with version `dcdc7bbc6e59ac0123407a9dc4d1f43dd0d117cd`
that includes [FIPS] validated [BoringCrypto] core library for Android that was issued the following
[FIPS 140-2] certificate https://csrc.nist.gov/Projects/Cryptographic-Module-Validation-Program/Certificate/4156
with the following security policy https://csrc.nist.gov/CSRC/media/projects/cryptographic-module-validation-program/documents/security-policies/140sp4156.pdf.

#### Power-On Self-Tests

##### Integrity Test

###### RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.PowerOnSelfTest.IntegrityTest
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS] compatible [BoringSSL] library that implements power-on integrity self test
using `HMAC-SHA-256` that SHALL verify the signature of the binary.

##### Known Answer Test

###### RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.PowerOnSelfTest.KnownAnswerTest
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

#### Conditional Self-Tests

##### RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.ConditionalSelfTests
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS] compatible [BoringSSL] library that implements the following conditional
self-tests:

Type | Test
--- | ---
Pair-wise Consistency Test | ECDSA Key Pair generation, RSA Key Pair generation
CRNGT | Performed on the passively received entropy
DRBG Health Tests | Performed on DRBG, per SP 800‐90A Section 11.3. Required per IG C.1. 

#### SSL Tests

##### RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.SSLTests
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

#### All-tests Utility

##### RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.AllTestsUtility
version: 1.0

[ClickHouse] SHALL be statically linked with [FIPS] compatible [BoringSSL] library that passes all
`util/all_tests.go` tests. 

For example,

```bash
go run util/all_tests.go
...
All tests passed!
```

#### ACVP Check Expected Tests

##### RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.ACVP.CheckExpectedTests
version: 1.0

[ClickHouse] SHALL be statically linked with a [FIPS] compatible [BoringSSL] library that passes all
`/util/fipstools/acvp/acvptool/test/check_expected.go` tests.

```bash
./boringssl/util/fipstools/acvp/acvptool/test$ go run check_expected.go -tool ../acvptool -module-wrappers modulewrapper:../../../../../build/util/fipstools/acvp/modulewrapper/modulewrapper,testmodulewrapper:../testmodulewrapper/testmodulewrapper -tests tests.json 
2022/12/14 20:57:26 32 ACVP tests matched expectations
```

#### Build Options System Table

##### RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.SystemTable.BuildOptions
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support
reporting that the binary was build with FIPS enabled [BoringSSL] library
in the `system.build_options` table.

#### MySQL FIPS Function

##### RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.MySQLFunction
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support
reporting that it is FIPS compliant in the MySQL FIPS function.

#### SSL Configuration

##### FIPS Setting

###### RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.SSL.Client.Config.Settings.FIPS
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

##### Server SSL Configuration

###### RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.SSL.Server.Config
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

##### Client SSL Configuration

###### RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.Client.Config
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

#### Server TCP Connections

##### RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.Server.TCP
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support configuring
server to accept only [FIPS Compatible SSL Connection]s native TCP connections.

#### Server HTTPS Connections

##### RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.Server.HTTPS
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support configuring
server to accept only [FIPS Compatible SSL Connection]s HTTPS connections.

#### TCP Clients

##### clickhouse-client

###### RQ.SRS-034.ClickHouse.SSL.FIPS.Compatible.BoringSSL.Clients.TCP.ClickHouseClient.FIPS
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support accepting
connections from FIPS compliant [clickhouse-client] which uses native TCP protocol
that is configured to establish only [FIPS Compatible SSL Connection]s.

###### RQ.SRS-034.ClickHouse.SSL.FIPS.Compatible.BoringSSL.Clients.TCP.ClickHouseClient.NonFIPS
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support accepting
connections from non FIPS compliant [clickhouse-client] which uses native TCP protocol
that is configured to establish only [FIPS Compatible SSL Connection]s.

##### Test Python Client

###### RQ.SRS-034.ClickHouse.SSL.FIPS.Compatible.BoringSSL.Clients.TCP.Python
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support accepting
connections from test Python client which uses native TCP protocol
that is configured to establish only [FIPS Compatible SSL Connection]s.

#### HTTPS Clients

##### curl

###### RQ.SRS-034.ClickHouse.SSL.Server.FIPS.Compatible.BoringSSL.Clients.HTTPS.Curl
version: 1.0

[ClickHouse] with statically linked [FIPS] compatible [BoringSSL] SHALL support accepting
connections from [curl] used as HTTPS protocol client that is configured to establish only [FIPS Compatible SSL Connection]s.

### Diffie-Hellman (DH) Parameters

#### RQ.SRS-017.ClickHouse.SSL.Server.DH.Parameters
version: 1.0

[ClickHouse] SHALL support specifying a file containing Diffie-Hellman (DH) parameters.
using a string as value for the `<dhParamsFile>` parameter in the
`<clickhouse><openSSL><server>` section of the `config.xml` and
if not specified or empty, the default parameters SHALL be used.

```xml
<clickhouse>
    <openSSL>
        <server>
            <dhParamsFile>dh.pem</dhParamsFile>
            ...
        </server>
    </openSSL>
</clickhouse>
```

### Certificates

#### Private Key

##### RQ.SRS-017.ClickHouse.SSL.Server.Certificates.PrivateKey
version: 1.0

[ClickHouse] SHALL support specifying private key as the path to the
file containing the private key for the certificate in the [PEM format]
or containing both the private key and the certificate using the
`<privateKeyFile>` parameter in the `<clickhouse><openSSL><server>` section
of the `config.xml`.

```xml
<clickhouse>
    <openSSL>
        <server>
           <privateKeyFile>/path/to/private/key</privateKeyFile>
           ...
        </server>
    </openSSL>
</clickhouse>
```

##### Private Key Handler

###### RQ.SRS-017.ClickHouse.SSL.Server.Certificates.PrivateKeyHandler
version: 1.0

[ClickHouse] SHALL support specifying the name of the class that is subclass of `PrivateKeyPassphraseHandler`
used for obtaining the passphrase for accessing the private key using a string as a value of the
`<privateKeyPassphraseHandler><name>` parameter in the `<clickhouse><openSSL><server>` section of the `config.xml`.

```xml
<clickhouse>
    <openSSL>
        <server>
            <privateKeyPassphraseHandler>
                <name>KeyFileHandler</name>
                ...
            </privateKeyPassphraseHandler>
            ...
        </server>
    </openSSL>
</clickhouse>
```

###### RQ.SRS-017.ClickHouse.SSL.Server.Certificates.PrivateKeyHandler.Password
version: 1.0

[ClickHouse] SHALL support specifying the password to be used by the private key handler using a string
as a value of the `<privateKeyPassphraseHandler><options><password>` parameter in the
`<clickhouse><openSSL><server>` section of the `config.xml`.

```xml
<clickhouse>
    <openSSL>
        <server>
            <privateKeyPassphraseHandler>
                <name>KeyFileHandler</name>
                <options>
                    <password>private key password</password>
                </options>
            </privateKeyPassphraseHandler>
            ...
        </server>
    </openSSL>
</clickhouse>
```

#### Certificate

##### RQ.SRS-017.ClickHouse.SSL.Server.Certificates.Certificate
version: 1.0

[ClickHouse] SHALL support specifying the path to the file containing the server's
certificate in the [PEM format] using the `<certificateFile>` parameter in the
`<clickhouse><openSSL><server>` section of the `config.xml`.
When the private key specified by the `<privateKeyFile>` parameter contains
the certificate then this parameter SHALL be ignored.

```xml
<clickhouse>
    <openSSL>
        <server>
           <certificateFile>/path/to/the/certificate</certificateFile>
           ...
        </server>
    </openSSL>
</clickhouse>
```

#### CA Certificates

##### Config

###### RQ.SRS-017.ClickHouse.SSL.Server.Certificates.CAConfig
version: 1.0

[ClickHouse] SHALL support specifying the path to the file or directory containing the trusted root certificates
using the `<caConfig>` parameter in the `<clickhouse><openSSL><server>` section of the `config.xml`.

```xml
<clickhouse>
    <openSSL>
        <server>
           <caConfig>/path/to/the/file/or/directory/containing/trusted/root/cerificates</caConfig>
           ...
        </server>
    </openSSL>
</clickhouse>
```

##### Default

###### RQ.SRS-017.ClickHouse.SSL.Server.Certificates.LoadDefaultCAFile
version: 1.0

[ClickHouse] SHALL support specifying whether the builtin CA certificates provided by the [SSL]
library SHALL be used using the `<loadDefaultCAFile>` parameter with a boolean value in the
`<clickhouse><openSSL><server>` section of the `config.xml`.

#### Verification

##### Mode

###### RQ.SRS-017.ClickHouse.SSL.Server.Certificates.VerificationMode
version: 1.0

[ClickHouse] SHALL support specifying whether and how client certificates are validated
using the `<verificationMode>` parameter in the `<clickhouse><openSSL><server>` section of the `config.xml`.

###### RQ.SRS-017.ClickHouse.SSL.Server.Certificates.VerificationMode.None
version: 1.0

[ClickHouse] SHALL not perform client certificate validation when the `<verificationMode>` parameter
in the `<clickhouse><openSSL><server>` section of the `config.xml` is set to `none`
by not sending a `client certificate request` to the client so that the client will not send a certificate.

###### RQ.SRS-017.ClickHouse.SSL.Server.Certificates.VerificationMode.Relaxed
version: 1.0

[ClickHouse] SHALL perform relaxed client certificate validation when the `<verificationMode>` parameter
in the `<clickhouse><openSSL><server>` section of the `config.xml` is set to `relaxed` by
sending a `client certificate request` to the client. The certificate SHALL only be checked if client sends it.
If the client certificate verification process fails, the TLS/SSL handshake SHALL be immediately
terminated with an alert message containing the reason for the verification failure.

###### RQ.SRS-017.ClickHouse.SSL.Server.Certificates.VerificationMode.Strict
version: 1.0

[ClickHouse] SHALL perform strict client certificate validation when the `<verificationMode>` parameter
in the `<clickhouse><openSSL><server>` section of the `config.xml` is set to `strict` by
immediately terminating TLS/SSL handshake if the client did not return a certificate or
certificate validation process fails with a handshake failure alert.

###### RQ.SRS-017.ClickHouse.SSL.Server.Certificates.VerificationMode.Once
version: 1.0

[ClickHouse] SHALL perform client certificate validation only once when the `<verificationMode>` parameter
in the `<clickhouse><openSSL><server>` section of the `config.xml` is set to `once`
by only requesting a client certificate on the initial [TLS/SSL handshake].
During renegotiation client certificate SHALL not be requested and verified again.

##### Extended Mode

###### RQ.SRS-017.ClickHouse.SSL.Server.Certificates.VerificationExtended
version: 1.0

[ClickHouse] SHALL support enabling or disabling automatic post-connection extended certificate verification
using a `boolean` as a value of the `<extendedVerification>` parameter in the
`<clickhouse><openSSL><server>` section of the `config.xml` and connection SHALL be aborted
if extended certificate verification is enabled and fails.

##### Depth

###### RQ.SRS-017.ClickHouse.SSL.Server.Certificates.VerificationDepth
version: 1.0

[ClickHouse] SHALL support specifying the upper limit for the client certificate verification chain size
using the `<verificationDepth>` parameter in the `<clickhouse><openSSL><server>` section of the `config.xml`.
Verification SHALL fail if a certificate chain is larger than the value specified by this parameter
is encountered.

#### Invalid Certificate Handler

##### RQ.SRS-017.ClickHouse.SSL.Server.Certificates.InvalidCertificateHandler
version: 1.0

[ClickHouse] SHALL support specifying the name of the class that is a subclass of `CertificateHandler`
that SHALL be used for confirming invalid certificates using a string as the value of the
`<invalidCertificateHandler><name>` parameter in the `<clickhouse><openSSL><server>` section of the `config.xml`.

```xml
<clickhouse>
    <openSSL>
        <server>
            <invalidCertificateHandler>
                <name>ConsoleCertificateHandler</name>
            </invalidCertificateHandler>
            ...
        </server>
    </openSSL>
</clickhouse>
```

#### User Authentication

##### RQ.SRS-017.ClickHouse.SSL.Server.Certificates.UserAuthentication
version: 1.0

[ClickHouse] SHALL support authenticating a user via SSL certificate given
that the user was created using `IDENTIFIED WITH ssl_certificate` clause.

### Session

#### RQ.SRS-017.ClickHouse.SSL.Server.Session.Cache
version: 1.0

[ClickHouse] SHALL support enabling or disabling session caching using a boolean as a value of the
`<cacheSessions>` parameter in the `<clickhouse><openSSL><server>` section of the `config.xml`.

```xml
<clickhouse>
    <openSSL>
        <server>
            cacheSessions>true|false</cacheSessions>
            ...
        </server>
    </openSSL>
</clickhouse>
```

#### RQ.SRS-017.ClickHouse.SSL.Server.Session.CacheSize
version: 1.0

[ClickHouse] SHALL support specifying the maximum size of the server session cache as the number of sessions
using an integer as a value of the `<sessionCacheSize>` parameter in the
`<clickhouse><openSSL><server>` section of the `config.xml`.

* The default size SHALL be `1024*20`.
* Specifying a size of 0 SHALL set an unlimited cache size.

```xml
<clickhouse>
    <openSSL>
        <server>
            <sessionCacheSize>0..n</sessionCacheSize>
            ...
        </server>
    </openSSL>
</clickhouse>
```

#### RQ.SRS-017.ClickHouse.SSL.Server.Session.IdContext
version: 1.0

[ClickHouse] SHALL support specifying unique session ID context, which SHALL become part of each
session identifier generated by the server using a string as a value of the `<sessionIdContext>` parameter
in the `<clickhouse><openSSL><server>` section of the `config.xml`.

* The value SHALL support an arbitrary sequence of bytes with a maximum length of `SSL_MAX_SSL_SESSION_ID_LENGTH`.
* This parameter SHALL be specified for a server to enable session caching.
* This parameter SHALL be specified even if session caching is disabled to avoid problems with clients that request
  session caching (e.g. Firefox 3.6).
* If not specified, the default value SHALL be set to `${application.name}`.

```xml
<clickhouse>
    <openSSL>
        <server>
            <sessionIdContext>someString</sessionIdContext>
            ...
        </server>
    </openSSL>
</clickhouse>
```

#### RQ.SRS-017.ClickHouse.SSL.Server.Session.Timeout
version: 1.0

[ClickHouse] SHALL support setting the timeout in seconds of sessions cached on the server
using an integer as a value of the <sessionTimeout>` parameter in the
`<clickhouse><openSSL><server>` section of the `config.xml`.

```xml
<clickhouse>
    <openSSL>
        <server>
            <sessionTimeout>0..n</sessionTimeout>
            ...
        </server>
    </openSSL>
</clickhouse>
```

### Dynamic SSL Context

##### RQ.SRS-017.ClickHouse.SSL.Server.DynamicContext.Reload

[ClickHouse] SHALL reload dynamic SSL context any time `config.xml` configuration file
or any of its parts defined inside the `/etc/clickhouse-server/configs.d/`
directory changes and causes `/var/lib/clickhouse/preprocessed_configs/config.xml`
configuration file generation and reload.

#### Certificate Reload

##### RQ.SRS-017.ClickHouse.SSL.Server.DynamicContext.Certificate.Reload
version: 1.0

[ClickHouse] SHALL reload server SSL certificate specified 
by the `<certificateFile>` parameter in the `<clickhouse><openSSL><server>`
section of the `config.xml` any time [Dynamic SSL Context] is reloaded. 
and the reloaded SSL server certificate SHALL be immediately applied
to any to new SSL connections made to the server.

#### Private Key Reload

##### RQ.SRS-017.ClickHouse.SSL.Server.DynamicContext.PrivateKey.Reload
version: 1.0

[ClickHouse] SHALL reload server SSL private key specified 
by the `<privateKeyFile>` parameter in the `<clickhouse><openSSL><server>` section
of the `config.xml` any time [Dynamic SSL Context] is reloaded  
and the reloaded SSL private key SHALL be immediately applied
to any new SSL connections made to the server.

[SRS]: #srs
[SSL Protocol]: #ssl-protocol
[TLS Protocol]: #tls-protocol
[J. Kalsi, D. Mossop]: https://www.contextis.com/en/blog/manually-testing-ssl-tls-weaknesses
[RSA]: https://en.wikipedia.org/wiki/RSA_(cryptosystem)
[MD5]: https://en.wikipedia.org/wiki/MD5
[SHA1]: https://en.wikipedia.org/wiki/SHA-1
[SHA2]: https://en.wikipedia.org/wiki/SHA-2
[TLS/SSL handshake]: https://en.wikipedia.org/wiki/Transport_Layer_Security#TLS_handshake
[PEM format]: https://en.wikipedia.org/wiki/Privacy-Enhanced_Mail#Format
[FIPS 140-2]: https://csrc.nist.gov/publications/detail/fips/140/2/final
[FIPS Mode]: https://wiki.openssl.org/index.php/FIPS_mode()
[RFC 4492]: https://www.ietf.org/rfc/rfc4492.txt
[Shared Secret]: https://en.wikipedia.org/wiki/Shared_secret
[ECDH]: https://en.wikipedia.org/wiki/Elliptic-curve_Diffie%E2%80%93Hellman
[OpenSSL cipher list format]: https://www.openssl.org/docs/man1.1.1/man1/ciphers.html
[HTTPS]: https://en.wikipedia.org/wiki/HTTPS
[TCP]: https://en.wikipedia.org/wiki/Transmission_Control_Protocol
[SSL]: https://www.ssl.com/faqs/faq-what-is-ssl/
[ClickHouse]: https://clickhouse.com
[Dynamic SSL Context]: #dynamic-ssl-context
[FIPS Compatible SSL Connection]: #fips_compatible_ssl_connection
[OpenSSL ciphers]: https://www.openssl.org/docs/man1.1.1/man1/ciphers.html
[curl]: https://curl.se/docs/manpage.html
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/tree/main/ssl_server/requirements/requirements_fips.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/ssl_server/requirements/requirements_fips.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
[FIPS]: https://csrc.nist.gov/publications/detail/fips/140/2/final
[FIPS 140-2]: https://csrc.nist.gov/publications/detail/fips/140/2/final
[BoringSSL]: https://github.com/google/boringssl/
[BoringCrypto]: https://github.com/google/boringssl/tree/master/crypto
[ACVP]: https://pages.nist.gov/ACVP/
