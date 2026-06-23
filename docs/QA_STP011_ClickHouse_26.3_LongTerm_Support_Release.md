# QA-STP011 ClickHouse 26.3 Long-Term Support Release  
# Software Test Plan

(c) 2026 Altinity Inc. All Rights Reserved.

**Author:** vzakaznikov

**Date:** June 17, 2026

## Execution Summary

**Completed:** TBD

**Test Results:**

* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/26.3.13-lts/

**Build Report:**

* https://s3.amazonaws.com/altinity-build-artifacts/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/27626627067/ci_run_report.html


**Summary:**

**In progress.**

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Timeline](#timeline)
* 3 [Human Resources And Assignments](#human-resources-and-assignments)
* 4 [Release Notes](#release-notes)
* 5 [Known Issues](#known-issues)
    * 5.1 [Open Issues](#open-issues)
    * 5.2 [Summary](#summary)
* 6 [Scope](#scope)
    * 6.1 [Automated Regression Tests](#automated-regression-tests)
        * 6.1.1 [Stateless](#stateless)
        * 6.1.2 [Stress](#stress)
        * 6.1.3 [Integration](#integration)
        * 6.1.4 [Altinity TestFlows Integration](#altinity-testflows-integration)
            * 6.1.4.1 [AES Encryption](#aes-encryption)
            * 6.1.4.2 [Aggregate Functions](#aggregate-functions)
            * 6.1.4.3 [Alter](#alter)
            * 6.1.4.4 [Atomic Insert](#atomic-insert)
            * 6.1.4.5 [Attach](#attach)
            * 6.1.4.6 [Base58](#base58)
            * 6.1.4.7 [Ontime Benchmark](#ontime-benchmark)
            * 6.1.4.8 [ClickHouse Keeper](#clickhouse-keeper)
            * 6.1.4.9 [ClickHouse Keeper Failover](#clickhouse-keeper-failover)
            * 6.1.4.10 [Data Types](#data-types)
            * 6.1.4.11 [DateTime64 Extended Range](#datetime64-extended-range)
            * 6.1.4.12 [Disk Level Encryption](#disk-level-encryption)
            * 6.1.4.13 [DNS](#dns)
            * 6.1.4.14 [Engines](#engines)
            * 6.1.4.15 [Example](#example)
            * 6.1.4.16 [Extended Precision Data Types](#extended-precision-data-types)
            * 6.1.4.17 [Functions](#functions)
            * 6.1.4.18 [Iceberg](#iceberg)
            * 6.1.4.19 [JWT Authentication](#jwt-authentication)
            * 6.1.4.20 [Kafka](#kafka)
            * 6.1.4.21 [Kerberos](#kerberos)
            * 6.1.4.22 [Key Value](#key-value)
            * 6.1.4.23 [LDAP](#ldap)
            * 6.1.4.24 [Lightweight Delete](#lightweight-delete)
            * 6.1.4.25 [Memory](#memory)
            * 6.1.4.26 [Parquet](#parquet)
            * 6.1.4.27 [Part Moves Between Shards](#part-moves-between-shards)
            * 6.1.4.28 [RBAC](#rbac)
            * 6.1.4.29 [S3](#s3)
            * 6.1.4.30 [Selects](#selects)
            * 6.1.4.31 [Session Timezone](#session-timezone)
            * 6.1.4.32 [Settings](#settings)
            * 6.1.4.33 [SSL Server](#ssl-server)
            * 6.1.4.34 [Swarms](#swarms)
            * 6.1.4.35 [Tiered Storage](#tiered-storage)
            * 6.1.4.36 [Version](#version)
            * 6.1.4.37 [Window Functions](#window-functions)
    * 6.2 [Regression Tests with Sanitizers](#regression-tests-with-sanitizers)
        * 6.2.1 [ASAN](#asan)
        * 6.2.2 [MSAN](#msan)
        * 6.2.3 [UBSAN](#ubsan)
        * 6.2.4 [TSAN](#tsan)
        * 6.2.5 [Sanitizer Test Results Summary](#sanitizer-test-results-summary)
        * 6.2.6 [Identified Issues](#identified-issues)
        * 6.2.7 [Failure Justification](#failure-justification)
        * 6.2.8 [Conclusion](#conclusion)
    * 6.3 [Compatibility with Client Drivers](#compatibility-with-client-drivers)
        * 6.3.1 [Python `clickhouse_driver`](#python-clickhouse_driver)
        * 6.3.2 [ODBC `clickhouse-odbc`](#odbc-clickhouse-odbc)
        * 6.3.3 [SQLAlchemy](#sqlalchemy)
        * 6.3.4 [Java `clickhouse-jdbc`](#java-clickhouse-jdbc)
    * 6.4 [Backup `clickhouse-backup`](#backup-clickhouse-backup)
    * 6.5 [Compatibility With Operation on Kubernetes](#compatibility-with-operation-on-kubernetes)
        * 6.5.1 [Kubernetes `clickhouse-operator`](#kubernetes-clickhouse-operator)
        * 6.5.2 [Altinity.Cloud](#altinitycloud)
    * 6.6 [Production Cluster Operation](#production-cluster-operation)
    * 6.7 [Upgrade and Downgrade](#upgrade-and-downgrade)
        * 6.7.1 [Upgrade](#upgrade)
        * 6.7.2 [Downgrade](#downgrade)
    * 6.8 [Compatibility With BI Tools](#compatibility-with-bi-tools)
        * 6.8.1 [Grafana](#grafana)
        * 6.8.2 [Tableau](#tableau)
        * 6.8.3 [Superset](#superset)
    * 6.9 [Docker Image Vulnerability Scanning](#docker-image-vulnerability-scanning)
        * 6.9.1 [Grype](#grype)


## Introduction

This test plan covers testing of ClickHouse 26.3 LTS (long-term support) Altinity Stable release.

Test results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/26.3.13-lts/

## Timeline

The testing of 26.3.13 binaries SHALL be started on June 17, 2026 and be completed by June 26, 2026.

## Human Resources And Assignments

The following team members SHALL be dedicated to the release:

* Vitaliy Zakaznikov (manager)
* Davit Mnatobishvili (clickhouse-odbc, grafana, superset, DBeaver)
* Alsu Giliazova (regression, clickhouse-jdbc, sqlalchemy, clickhouse-driver)
* Carlos Raymundo (regression)
* Saba Momtselidze (clickhouse-)
* Vitalii Sviderskyi (clickhouse-backup, ACM, ACM backup, ACM upgrade and downgrade)
* Julian Huang (Tableau)
* Mikhail Filimonov (production clusters, support team feedback)

## Release Notes

* [TBD]

## Known Issues

* [FIXED] [distributed_ddl replicas_path mismatch causing ON CLUSTER DDL to hang](https://github.com/Altinity/ClickHouse/issues/1391) - results in 12 scenario failures

### Open Issues

* [clickhouse-driver] [`use_client_time_zone` ignored for string datetime literals in INSERT when `async_insert` is enabled](https://github.com/ClickHouse/ClickHouse/issues/108038) — 2 failing timezone tests on 26.3; passes on 25.8; workaround: `SETTINGS async_insert=0`

### Summary
Build report: https://s3.amazonaws.com/altinity-build-artifacts/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/27626627067/ci_run_report.html

> [!NOTE]
> **\*Pass** - tests passed with known fails

| Test Suite | Result | Comments |
| --- |-----------------------------------------------| --- |
| Stateless | [Pass](#stateless) | |
| Stress | [Pass](#stress) | |
| Integration | [Pass](#integration) | |
| AES Encryption | [Pass](#aes-encryption) | |
| Aggregate Functions | [Pass](#aggregate-functions) | |
| Alter | [Pass](#alter) | |
| Atomic Insert | [Pass](#atomic-insert) | |
| Attach | [Pass](#attach) | |
| Base58 | [Pass](#base58) | |
| Ontime Benchmark | [Pass](#ontime-benchmark) | |
| ClickHouse Keeper | [Pass](#clickhouse-keeper) | |
| ClickHouse Keeper Failover | [Pass](#clickhouse-keeper-failover) | |
| Data Types | [Pass](#data-types) | |
| DateTime64 Extended Range | [Pass](#datetime64-extended-range) | |
| Disk Level Encryption | [Pass](#disk-level-encryption) | |
| DNS | [Pass](#dns) | |
| Engines | [Pass](#engines) | |
| Example | [Pass](#example) | |
| Extended Precision Data Types | [Pass](#extended-precision-data-types) | |
| Functions | [Pass](#functions) | |
| Iceberg | [Pass](#iceberg) | |
| JWT Authentication | [Pass](#jwt-authentication) | |
| Kafka | [Pass](#kafka) | |
| Kerberos | [Pass](#kerberos) | |
| Key Value | [Pass](#key-value) | |
| LDAP | [Pass](#ldap) | |
| Lightweight Delete | [Pass](#lightweight-delete) | |
| Memory | [Pass](#memory) | |
| Parquet | [Pass](#parquet) | |
| Part Moves Between Shards | [Pass](#part-moves-between-shards) | |
| RBAC | [Pass](#rbac) | |
| S3 | [Pass](#s3) | |
| Selects | [Pass](#selects) | |
| Session Timezone | [Pass](#session-timezone) | |
| Settings | [Pass](#settings) | |
| SSL Server | [Pass](#ssl-server) | |
| Swarms | [Pass](#swarms) | |
| Tiered Storage | [Pass](#tiered-storage) | |
| Version | [Pass](#version) | |
| Window Functions | [Pass](#window-functions) | |
| Python `clickhouse_driver` | [*Pass](#python-clickhouse_driver) | 371 passed, 113 skipped, 2 failed (expected). JSON tests skipped; datetime fails tracked in [#108038](https://github.com/ClickHouse/ClickHouse/issues/108038) |
| ODBC `clickhouse-odbc` | [Pass](#odbc-clickhouse-odbc) | |
| SQLAlchemy | [Pass](#sqlalchemy) | 388 passed, 27 warnings |
| Java `clickhouse-jdbc` | [Pass](#java-clickhouse-jdbc) | Tests run: 231, Failures: 0, Errors: 0, Skipped: 0 |
| Java `clickhouse-jdbc` (DBeaver) | [Pass](#java-clickhouse-jdbc) | |
| Backup `clickhouse-backup` | [Pass](#backup-clickhouse-backup) | |
| Kubernetes `clickhouse-operator` | [Pass](#kubernetes-clickhouse-operator) | Tests run: 111, 6 XFail|
| Altinity.Cloud | [Pass](#altinitycloud) | |
| Production Cluster Operation | [Pass](#production-cluster-operation) | |
| Upgrade And Downgrade | [Pass](#upgrade-and-downgrade) | |
| Grafana | [Pass](#grafana) | |
| Tableau | [*Pass](#tableau) | 849 passed, 24 failed (97%). Expected fails. |
| Superset | [Pass](#superset) | |
| Grype | [Pass](#grype) | |

## Scope

The scope of testing ClickHouse 26.3 Altinity Stable LTS release SHALL be defined as follows.


### Automated Regression Tests

The following automated regression test suites SHALL be executed.

#### Stateless

Results:

* ARM Binary
 * [Stateless tests (arm_binary, parallel)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28arm%5Fbinary%2C%20parallel%29)
 * [Stateless tests (arm_binary, sequential)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28arm%5Fbinary%2C%20sequential%29)

* ARM ASan (Azure)
 * [Stateless tests (arm_asan, azure, parallel, 1/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28arm%5Fasan%2C%20azure%2C%20parallel%2C%201%2F4%29)
 * [Stateless tests (arm_asan, azure, parallel, 2/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28arm%5Fasan%2C%20azure%2C%20parallel%2C%202%2F4%29)
 * [Stateless tests (arm_asan, azure, parallel, 3/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28arm%5Fasan%2C%20azure%2C%20parallel%2C%203%2F4%29)
 * [Stateless tests (arm_asan, azure, parallel, 4/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28arm%5Fasan%2C%20azure%2C%20parallel%2C%204%2F4%29)
 * [Stateless tests (arm_asan, azure, sequential, 1/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28arm%5Fasan%2C%20azure%2C%20sequential%2C%201%2F2%29)
 * [Stateless tests (arm_asan, azure, sequential, 2/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28arm%5Fasan%2C%20azure%2C%20sequential%2C%202%2F2%29)

* AMD Debug
 * [Stateless tests (amd_debug, parallel)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fdebug%2C%20parallel%29)
 * [Stateless tests (amd_debug, sequential)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fdebug%2C%20sequential%29)
 * [Stateless tests (amd_debug, distributed plan, s3 storage, parallel)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fdebug%2C%20distributed%20plan%2C%20s3%20storage%2C%20parallel%29)
 * [Stateless tests (amd_debug, distributed plan, s3 storage, sequential)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fdebug%2C%20distributed%20plan%2C%20s3%20storage%2C%20sequential%29)

* AMD Coverage
 * [Stateless tests (amd_coverage, 1/8)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fcoverage%2C%201%2F8%29)
 * [Stateless tests (amd_coverage, 2/8)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fcoverage%2C%202%2F8%29)
 * [Stateless tests (amd_coverage, 3/8)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fcoverage%2C%203%2F8%29)
 * [Stateless tests (amd_coverage, 4/8)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fcoverage%2C%204%2F8%29)
 * [Stateless tests (amd_coverage, 5/8)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fcoverage%2C%205%2F8%29)
 * [Stateless tests (amd_coverage, 6/8)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fcoverage%2C%206%2F8%29)
 * [Stateless tests (amd_coverage, 7/8)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fcoverage%2C%207%2F8%29)
 * [Stateless tests (amd_coverage, 8/8)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fcoverage%2C%208%2F8%29)

* AMD UBSan
 * [Stateless tests (amd_ubsan, parallel)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fubsan%2C%20parallel%29)
 * [Stateless tests (amd_ubsan, sequential)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fubsan%2C%20sequential%29)

* AMD ASan
 * [Stateless tests (amd_asan, distributed plan, parallel, 1/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fasan%2C%20distributed%20plan%2C%20parallel%2C%201%2F4%29)
 * [Stateless tests (amd_asan, distributed plan, parallel, 2/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fasan%2C%20distributed%20plan%2C%20parallel%2C%202%2F4%29)
 * [Stateless tests (amd_asan, distributed plan, parallel, 3/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fasan%2C%20distributed%20plan%2C%20parallel%2C%203%2F4%29)
 * [Stateless tests (amd_asan, distributed plan, parallel, 4/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fasan%2C%20distributed%20plan%2C%20parallel%2C%204%2F4%29)
 * [Stateless tests (amd_asan, db disk, distributed plan, sequential)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fasan%2C%20db%20disk%2C%20distributed%20plan%2C%20sequential%29)

* AMD MSan
 * [Stateless tests (amd_msan, WasmEdge, parallel, 1/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fmsan%2C%20WasmEdge%2C%20parallel%2C%201%2F4%29)
 * [Stateless tests (amd_msan, WasmEdge, parallel, 2/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fmsan%2C%20WasmEdge%2C%20parallel%2C%202%2F4%29)
 * [Stateless tests (amd_msan, WasmEdge, parallel, 3/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fmsan%2C%20WasmEdge%2C%20parallel%2C%203%2F4%29)
 * [Stateless tests (amd_msan, WasmEdge, parallel, 4/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fmsan%2C%20WasmEdge%2C%20parallel%2C%204%2F4%29)
 * [Stateless tests (amd_msan, WasmEdge, sequential, 1/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fmsan%2C%20WasmEdge%2C%20sequential%2C%201%2F2%29)
 * [Stateless tests (amd_msan, WasmEdge, sequential, 2/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Fmsan%2C%20WasmEdge%2C%20sequential%2C%202%2F2%29)

* AMD TSan
 * [Stateless tests (amd_tsan, parallel, 1/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Ftsan%2C%20parallel%2C%201%2F2%29)
 * [Stateless tests (amd_tsan, parallel, 2/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Ftsan%2C%20parallel%2C%202%2F2%29)
 * [Stateless tests (amd_tsan, sequential, 1/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Ftsan%2C%20sequential%2C%201%2F2%29)
 * [Stateless tests (amd_tsan, sequential, 2/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Ftsan%2C%20sequential%2C%202%2F2%29)
 * [Stateless tests (amd_tsan, s3 storage, parallel, 1/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Ftsan%2C%20s3%20storage%2C%20parallel%2C%201%2F2%29)
 * [Stateless tests (amd_tsan, s3 storage, parallel, 2/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Ftsan%2C%20s3%20storage%2C%20parallel%2C%202%2F2%29)
 * [Stateless tests (amd_tsan, s3 storage, sequential, 1/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Ftsan%2C%20s3%20storage%2C%20sequential%2C%201%2F2%29)
 * [Stateless tests (amd_tsan, s3 storage, sequential, 2/2)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stateless%20tests%20%28amd%5Ftsan%2C%20s3%20storage%2C%20sequential%2C%202%2F2%29)


The standard `stateless` suite that consists of running SQL, python and bash scripts that check various features of the server.

#### Stress

Results:

* [Stress test (amd_debug)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stress%20test%20%28amd%5Fdebug%29)
* [Stress test (amd_msan)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stress%20test%20%28amd%5Fmsan%29)
* [Stress test (amd_release)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stress%20test%20%28amd%5Frelease%29)
* [Stress test (amd_tsan)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stress%20test%20%28amd%5Ftsan%29)
* [Stress test (amd_ubsan)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stress%20test%20%28amd%5Fubsan%29)
* [Stress test (arm_asan)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stress%20test%20%28arm%5Fasan%29)
* [Stress test (arm_asan, s3)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stress%20test%20%28arm%5Fasan%2C%20s3%29)
* [Stress test (azure, amd_msan)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stress%20test%20%28azure%2C%20amd%5Fmsan%29)
* [Stress test (azure, amd_tsan)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Stress%20test%20%28azure%2C%20amd%5Ftsan%29)


The standard `stress` suite that consists of running tests from the `stateless` suite in parallel to check for server hang-up and crashes.

#### Integration

Results:

* ARM Binary
 * [Integration tests (arm_binary, distributed plan, 1/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28arm%5Fbinary%2C%20distributed%20plan%2C%201%2F4%29)
 * [Integration tests (arm_binary, distributed plan, 3/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28arm%5Fbinary%2C%20distributed%20plan%2C%203%2F4%29)
 * [Integration tests (arm_binary, distributed plan, 4/4)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28arm%5Fbinary%2C%20distributed%20plan%2C%204%2F4%29)

* AMD Binary
 * [Integration tests (amd_binary, 1/5)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Fbinary%2C%201%2F5%29)
 * [Integration tests (amd_binary, 2/5)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Fbinary%2C%202%2F5%29)
 * [Integration tests (amd_binary, 3/5)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Fbinary%2C%203%2F5%29)
 * [Integration tests (amd_binary, 4/5)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Fbinary%2C%204%2F5%29)
 * [Integration tests (amd_binary, 5/5)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Fbinary%2C%205%2F5%29)

* AMD ASan
 * [Integration tests (amd_asan, db disk, old analyzer, 1/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Fasan%2C%20db%20disk%2C%20old%20analyzer%2C%201%2F6%29)
 * [Integration tests (amd_asan, db disk, old analyzer, 2/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Fasan%2C%20db%20disk%2C%20old%20analyzer%2C%202%2F6%29)
 * [Integration tests (amd_asan, db disk, old analyzer, 3/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Fasan%2C%20db%20disk%2C%20old%20analyzer%2C%203%2F6%29)
 * [Integration tests (amd_asan, db disk, old analyzer, 4/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Fasan%2C%20db%20disk%2C%20old%20analyzer%2C%204%2F6%29)
 * [Integration tests (amd_asan, db disk, old analyzer, 5/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Fasan%2C%20db%20disk%2C%20old%20analyzer%2C%205%2F6%29)
 * [Integration tests (amd_asan, db disk, old analyzer, 6/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Fasan%2C%20db%20disk%2C%20old%20analyzer%2C%206%2F6%29)

* AMD MSan
 * [Integration tests (amd_msan, 1/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Fmsan%2C%201%2F6%29)
 * [Integration tests (amd_msan, 2/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Fmsan%2C%202%2F6%29)
 * [Integration tests (amd_msan, 3/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Fmsan%2C%203%2F6%29)
 * [Integration tests (amd_msan, 4/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Fmsan%2C%204%2F6%29)
 * [Integration tests (amd_msan, 5/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Fmsan%2C%205%2F6%29)
 * [Integration tests (amd_msan, 6/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Fmsan%2C%206%2F6%29)

* AMD TSan
 * [Integration tests (amd_tsan, 1/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Ftsan%2C%201%2F6%29)
 * [Integration tests (amd_tsan, 2/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Ftsan%2C%202%2F6%29)
 * [Integration tests (amd_tsan, 3/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Ftsan%2C%203%2F6%29)
 * [Integration tests (amd_tsan, 4/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Ftsan%2C%204%2F6%29)
 * [Integration tests (amd_tsan, 5/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Ftsan%2C%205%2F6%29)
 * [Integration tests (amd_tsan, 6/6)](https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=stable-26.3&sha=f8d4966ea4c372d9f538642cef144cf3f66d46d9&name%5F0=MasterCI&name%5F1=Integration%20tests%20%28amd%5Ftsan%2C%206%2F6%29)


The standard `integration` suite of tests consists of various suites of automated tests that use [PyTest Framework](https://pytest.org) .

#### Altinity TestFlows Integration

##### AES Encryption

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/aes_encryption/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/aes_encryption/report.html

Altinity AES Encryption tests.

##### Aggregate Functions

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/aggregate_functions1/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/aggregate_functions2/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/aggregate_functions3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/aggregate_functions1/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/aggregate_functions2/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/aggregate_functions3/report.html
 
Altinity Aggregate Functions integration tests.

##### Alter

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/alter1/attach_partition/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/alter2/attach_partition/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/alter/move_partition/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/alter/replace_partition/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/alter1/attach_partition/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/alter2/attach_partition/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/alter/move_partition/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/alter/replace_partition/report.html

Altinity Alter tests.

##### Atomic Insert

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/atomic_insert/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/atomic_insert/report.html

Altinity Atomic Insert integration tests.

##### Attach

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with%5Fanalyzer/zookeeper/without%5Fthread%5Ffuzzer/attach/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86%5F64/with%5Fanalyzer/zookeeper/without%5Fthread%5Ffuzzer/attach/report.html

Altinity Attach tests.

##### Base58

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/base_58/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/base_58/report.html

Altinity Base58 encode and decode functions integration tests.

##### Ontime Benchmark

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/aws_s3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/gcs/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/aws_s3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/gcs/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ontime_benchmark/minio/report.html

Altinity OnTime Benchmark tests.

##### ClickHouse Keeper

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper1/no_ssl/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper1/ssl/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper2/no_ssl/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper2/ssl/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper1/no_ssl/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper1/ssl/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper2/no_ssl/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/clickhouse_keeper2/ssl/report.html

Altinity ClickHouse Keeper integration tests.

##### ClickHouse Keeper Failover

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with%5Fanalyzer/zookeeper/without%5Fthread%5Ffuzzer/clickhouse%5Fkeeper%5Ffailover/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86%5F64/with%5Fanalyzer/zookeeper/without%5Fthread%5Ffuzzer/clickhouse%5Fkeeper%5Ffailover/report.html

Altinity ClickHouse Keeper Failover integration tests.

##### Data Types

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/data_types/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/data_types/report.html

Altinity data types integration tests.

##### DateTime64 Extended Range

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/datetime64_extended_range/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/datetime64_extended_range/report.html

Altinity DateTime64 extended range integration tests.

##### Disk Level Encryption

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/disk_level_encryption/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/disk_level_encryption/report.html

Altinity Disk Level Encryption integration tests.

##### DNS

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/dns/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/dns/report.html

Altinity DNS integration tests.

##### Engines

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/engines/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/engines/report.html

Altinity Engines tests.

##### Example

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/example/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/example/report.html

Altinity Example tests.

##### Extended Precision Data Types

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/extended_precision_data_types/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/extended_precision_data_types/report.html

Altinity Extended Precision Data Types integration tests.

##### Functions

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/functions/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/functions/report.html

Altinity Functions tests.

##### Iceberg

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/iceberg1/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/iceberg2/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/iceberg1/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/iceberg2/report.html

Altinity Iceberg tests.

##### JWT Authentication

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with%5Fanalyzer/zookeeper/without%5Fthread%5Ffuzzer/jwt%5Fauthentication/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86%5F64/with%5Fanalyzer/zookeeper/without%5Fthread%5Ffuzzer/jwt%5Fauthentication/report.html

Altinity JWT Authentication tests.

##### Kafka

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/kafka/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/kafka/report.html

Altinity Kafka integration tests.

##### Kerberos

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/kerberos/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/kerberos/report.html

Altinity Kerberos integration tests.

##### Key Value

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/key_value/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/key_value/report.html

Altinity Key Value function tests.

##### LDAP

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/authentication/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/external_user_directory/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/role_mapping/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/authentication/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/external_user_directory/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ldap/role_mapping/report.html

Altinity LDAP integration tests.

##### Lightweight Delete

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/lightweight_delete/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/lightweight_delete/report.html

Altinity Lightweight Delete integration tests.

##### Memory

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/memory/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/memory/report.html

Altinity Memory tests.

##### Parquet

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/parquet/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/parquetaws_s3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/parquetminio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/parquet/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/parquetaws_s3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/parquetminio/report.html

Altinity Parquet format integration tests.

##### Part Moves Between Shards

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/part_moves_between_shards/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/part_moves_between_shards/report.html

Altinity Part Moves Between Shards integration tests.

##### RBAC

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/rbac1/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/rbac2/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/rbac3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/rbac1/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/rbac2/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/rbac3/report.html

Altinity RBAC integration tests.

##### S3

AWS Results:
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s31/aws_s3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s32/aws_s3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s31/aws_s3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s32/aws_s3/report.html

Azure Results:
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s31/azure/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s32/azure/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s31/azure/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s32/azure/report.html

GCS Results:
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s31/gcs/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s32/gcs/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s31/gcs/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s32/gcs/report.html

MinIO Results:
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s31/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s32/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s33/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s31/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s32/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s33/minio/report.html

Export Parts Results:
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s3part/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s3part/minio/report.html

Export Partition Results:
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/s3partition/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/s3partition/minio/report.html

Altinity S3 integration tests.

##### Selects

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/selects/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/selects/report.html

Altinity Selects tests.

##### Session Timezone

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/session_timezone/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/session_timezone/report.html

Altinity Session Timezone tests.

##### Settings

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with%5Fanalyzer/zookeeper/without%5Fthread%5Ffuzzer/settings/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86%5F64/with%5Fanalyzer/zookeeper/without%5Fthread%5Ffuzzer/settings/report.html

Altinity Settings tests.

##### SSL Server

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ssl_server1/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ssl_server2/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/ssl_server3/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ssl_server1/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ssl_server2/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/ssl_server3/report.html

Altinity basic SSL server integration tests.

##### Swarms

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/swarms/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/swarms/report.html

Altinity Swarms tests.

##### Tiered Storage

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/local/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/s3amazon/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/s3gcs/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/local/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/minio/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/s3amazon/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/tiered_storage/s3gcs/report.html

Altinity Tiered-Storage tests.

##### Version

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/version/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/version/report.html

Altinity Version tests.

##### Window Functions

Results:

* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/aarch64/with_analyzer/zookeeper/without_thread_fuzzer/window_functions/report.html
* https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/regression/x86_64/with_analyzer/zookeeper/without_thread_fuzzer/window_functions/report.html

Altinity Window Functions integration tests.

### Regression Tests with Sanitizers

#### ASAN
Results:
* https://github.com/Altinity/clickhouse-regression/actions/runs/21962416400

#### MSAN
Results:
* https://github.com/Altinity/clickhouse-regression/actions/runs/21962390306

#### UBSAN
Results:
* https://github.com/Altinity/clickhouse-regression/actions/runs/21962441034

#### TSAN
Results:
* https://github.com/Altinity/clickhouse-regression/actions/runs/21962462044

#### Sanitizer Test Results Summary
| Sanitizer | Total Jobs | Failed | Timeouts | Primary Failure Mode |
|-----------|------------|--------|----------|---------------------|
| **UBSAN** | 65 | 7 | 1 | CPU overload (SERVER_OVERLOADED), test timeouts |
| **ASAN** | 65 | 10 | 4 | Server startup delays, data corruption errors |
| **TSAN** | 65 | 14 | 8 | Server startup failures due to TSAN overhead |
| **MSAN** | 65 | 16 | 10 | Server startup failures due to MSAN overhead |

#### Identified Issues
| Issue | UBSAN | ASAN | TSAN | MSAN | Type | GitHub Issue |
|-------|:-----:|:----:|:----:|:----:|------|--------------|
| UNKNOWN_CODEC (Code 432) - Data corruption in partition operations | ✓ | ✓ | ✓ | ✓ | **Bug** | Under investigation |
| Merge Part UINT32_MAX overflow (`Source part 0_101_101_4294967295`) | - | ✓ | ✓ | ✓ | **Bug** | [#69001](https://github.com/ClickHouse/ClickHouse/issues/69001) |
| Iceberg Metadata Not Initialized (server crash on ALTER TABLE) | ✓ | - | ✓ | ✓ | **Bug** | [#86024](https://github.com/ClickHouse/ClickHouse/issues/86024) |
| Server startup failures (Connection refused) | Rare | Moderate | Severe | Severe | Infra | Expected with sanitizers |
| Settings snapshot assertion failures | ✓ | ✓ | ✓ | ✓ | Test | Test environment issue |

#### Failure Justification
The majority of sanitizer test failures fall into two categories:

**1. Infrastructure/Performance Issues (~80% of failures)** 
Sanitizers add significant runtime overhead (TSAN/MSAN: 5–15x, ASAN: 2x). This causes server startup timeouts, query timeouts, and job timeouts (3-hour limit) before test completion. 
These failures are expected behavior for sanitizer builds.

**2. Real Bugs Found (~20% of failures)** 
Three bugs were identified across multiple sanitizers:

| Bug | Description | Status |
|-----|-------------|--------|
| **UNKNOWN_CODEC** | Data corruption during ALTER ATTACH/REPLACE PARTITION operations causing invalid codec family codes | Under investigation |
| **Merge Part Overflow** | Integer overflow (UINT32_MAX) in part numbering during OPTIMIZE TABLE - [#69001](https://github.com/ClickHouse/ClickHouse/issues/69001) | Open since Aug 2024 |
| **Iceberg Metadata** | Uninitialized metadata during ALTER TABLE on Iceberg tables with DataLakeCatalog - [#86024](https://github.com/ClickHouse/ClickHouse/issues/86024) | Open, assigned |

#### Conclusion
The sanitizer tests successfully identified real bugs in ClickHouse. Two of the three bugs are already tracked in upstream ClickHouse. The high failure count is primarily due to 
expected sanitizer performance overhead, not quality issues with ClickHouse 26.3.

### Compatibility with Client Drivers

The following client drivers SHALL be tested for compatibility:

#### Python `clickhouse_driver`

clickhouse-driver version: 
* 0.2.10

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/26.3.13-lts/clickhouse-driver/

**Results:** 371 passed, 113 skipped, 2 failed (on 26.3.13; for comparison, 25.8: 377 passed, 109 skipped, 0 failed).

Two distinct compatibility problems were found on 26.3.13. They have different root causes and are tracked separately:

**Problem 1 — JSON type (driver compatibility gap, 4 tests skipped)**

clickhouse-driver 0.2.10 supports `Object('json')`, but ClickHouse removed that type in 25.11 in favor of native `JSON`:

* ClickHouse: [#85718](https://github.com/ClickHouse/ClickHouse/pull/85718) — removed `Object('json')`
* clickhouse-driver: [#478](https://github.com/mymarilyn/clickhouse-driver/pull/478) — native `JSON` type support (not yet released in 0.2.10)

Without a patch, JSON tests fail on both sides: with the old `Object('json')` syntax the server returns `Unknown data type family: Object`; with native `JSON` syntax the driver returns `Unknown type JSON`. Tests are skipped on 26.3+ via [`diff-26.3.patch`](https://github.com/Altinity/clickhouse-regression/blob/main/container-images/test/clickhouse-driver-runner/diff-26.3.patch) until the driver supports native JSON.

**Problem 2 — DateTime timezone (ClickHouse server bug, 2 tests failed)**

`DateTimeTimezonesTestCase.test_use_client_timezone` and `DateTime64TimezonesTestCase.test_use_client_timezone` fail on 26.3. The driver sends binary timestamps correctly; the failure is in the CLI string-literal insert path when `async_insert` is enabled by default on 26.3+.

* ClickHouse issue filed: [#108038](https://github.com/ClickHouse/ClickHouse/issues/108038) — `use_client_time_zone` ignored for string datetime literals in INSERT when `async_insert` is enabled




The [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) driver.

Compatibility with the [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) driver.

#### ODBC `clickhouse-odbc`

clickhouse-odbc version: 
* v1.3.0.20241018

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/clickhouse-odbc/

The operation of [clickhouse-odbc](https://github.com/ClickHouse/clickhouse-odbc) driver.

#### SQLAlchemy

clickhouse-sqlalchemy version: 
* 0.3.2

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/26.3.13-lts/clickhouse-sqlalchemy/

The [clickhouse-sqlalchemy](https://github.com/xzkostyan/clickhouse-sqlalchemy) ClickHouse dialect for SQLAlchemy.

#### Java `clickhouse-jdbc`

clickhouse-jdbc version: 
* 0.9.0

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/26.3.13-lts/clickhouse-jdbc/v0.9.0/

**Results:** Tests run: 231, Failures: 0, Errors: 0, Skipped: 0 (clickhouse-jdbc 0.9.0 against ClickHouse 26.3.13.10001).

Results (DBeaver): 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/DBeaver/

The [clickhouse-jdbc](https://github.com/ClickHouse/clickhouse-jdbc) driver.

### Backup `clickhouse-backup`

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/26.3.13-lts/clickhouse-backup/

Results (ACM):
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/26.3.13-lts/clickhouse-backup-acm/

Compatibility with the [clickhouse-backup](https://github.com/altinity/clickhouse-backup) utility.

### Compatibility With Operation on Kubernetes

#### Kubernetes `clickhouse-operator`

clickhouse-operator version: 
* 0.27.2

Results: 
* reports.s3.amazonaws.com/index.html#reports/26.3.13-lts/clickhouse-operator/

Compatibility with [clickhouse-operator](https://github.com/altinity/clickhouse-operator).

#### Altinity.Cloud

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/26.3.13-lts/acm-launch-and-upgrade/launch_with_26.3.13.10001.altinitytest/

Compatibility with Altinity.Cloud.

### Production Cluster Operation

Results: OK

Approved by Mikhail Filimonov. 

### Upgrade and Downgrade

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/26.3.13-lts/acm-launch-and-upgrade/upgrade_downgrade_from_25.8.16.10002.altinitystable_to_26.3.13.10001.altinitytest/


The upgrade and downgrade.

#### Upgrade

* from 25.8 to 26.3

#### Downgrade

* From 26.3 to 25.8

### Compatibility With BI Tools

Compatibility with the following BI tools.

#### Grafana

Results: 
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/grafana/

Compatibility with [Grafana].

#### Tableau

Results:
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/26.3.13-lts/tableau/

Compatibility with [Tableau].

**TDVT results:** 849/873 passed, 24 failed (97% pass rate). All failures are expected and attributable to ClickHouse or connector limitations, not data loading issues.

**Failure breakdown:**

1. **`time0`/`time1` as String (2 failures)**: calcs_data.time tests. ClickHouse returns quoted strings like `"1899-12-30 21:07:32"` but TDVT expects datetime-formatted values like `#21:07:32#`. This is because time0/time1 are Nullable(String); ClickHouse has no TIME type and time0 has pre-1900 timestamps.
2. **`datetime0 - time0` operations (3 failures)**: operator.datetime.minus_time. Cannot subtract a String from a DateTime. Same root cause as above.
3. **DATETIME cast of pre-1900 dates (3 failures)**: cast.str.datetime. Parsing `'1900-01-01 01:00:00'` etc. returns `#1970-01-01#` instead of the correct value. ClickHouse's DateTime type cannot represent pre-1970 timestamps.
4. **`Date32 - Date32` arithmetic (7 failures)**: date.math.date_minus_date and date.B639952. ClickHouse does not support the minus operator between two Date32 values (known ClickHouse limitation).
5. **`DATE(num4)` cast (1 failure)**: date.cast.num_to_date. Off by one day (`#1970-01-01#` vs `#1969-12-31#`), likely an epoch rounding issue.
6. **Filter.datetime_fractional (1 failure)**: ClickHouse DateTime has no sub-second precision, so .123 is lost.
7. **NULL join tests (6 failures)**: join.null.bool/date/datetime/int/real/str. The connector's INNER JOIN does not match NULL keys, so rows with NULL join columns are excluded (connector behavior).
8. **BUGS.B641638 (1 failure)**: `$IN_SET$` with mixed time0 types. Tableau's IN filter combines SUM with time0; time0 is Nullable(String), so the connector errors ("No such function `$IN_SET$` that takes arguments of type (str, datetime, ...)"). Same root cause as 1 and 2 — no native TIME type in ClickHouse.

**TDVT version comparison:** All three builds produced identical results:

| Version | Failures |
|----------------------------------|----------|
| Latest LTS (Altinity 26.3) | 24 |
| Previous LTS (Altinity 25.8) | 24 |
| Upstream (ClickHouse 26.3.12.3) | 24 |

All 24 failures are the exact same set across all three builds. They are pre-existing ClickHouse/JDBC connector limitations, not version-specific regressions.

#### Superset

Results:
* https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/25.8.16-lts/superset/

Compatibility with [Superset].

The tests were run against Superset version `4.1.1`. Currently, there is an issue with establishing a connection to ClickHouse in Superset `5.0.0 (latest)`, due to the absence of the `clickhouse-connect` library in the default setup. This default setup follows the same test procedure we used previously with version `4.1.1`.

### Docker Image Vulnerability Scanning

#### Grype

Results:

https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/grype/altinityinfra_clickhouse-keeper_0-26.3.13.10001.altinitytest/results.html
https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/grype/altinityinfra_clickhouse-server_0-26.3.13.10001.altinitytest-alpine/results.html
https://altinity-build-artifacts.s3.amazonaws.com/REFs/stable-26.3/f8d4966ea4c372d9f538642cef144cf3f66d46d9/grype/altinityinfra_clickhouse-server_0-26.3.13.10001.altinitytest/results.html

[Grype](https://github.com/anchore/grype) Docker image vulnerability scanner.

[Grafana]: https://grafana.com/
[Tableau]: https://www.tableau.com/
[Superset]: https://superset.apache.org/
[ClickHouse]: https://clickhouse.tech
[Git]: https://git-scm.com/
[GitHub]: https://github.com
