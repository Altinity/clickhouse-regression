# QA-STP004 ClickHouse 22.8 Long-Term Support Release
# Software Test Plan

(c) 2022 Altinity Inc. All Rights Reserved.

**Document status:** Public

**Author:** vzakaznikov

**Date:** September 21, 2022

## Execution Summary

**Completed:** -

**Test Results:** -

**Test Coverage:** - 

**Summary:** 

Started to execute test plan on September 21, 2022.

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Timeline](#timeline)
* 4 [Human Resources And Assignments](#human-resources-and-assignments)
* 5 [End User Recomendations](#end-user-recomendations)
  * 5.1 [Settings](#settings)
    * 5.1.1 [local_filesystem_read_method = pread](#local_filesystem_read_method-pread)
* 6 [Known Issues](#known-issues)
  * 6.1 [Compatibility](#compatibility)
    * 6.1.1 [ODBC `clickhouse-odbc` (v1.1.10.20210822 and v1.2.1.20220905)](#odbc-clickhouse-odbc-v111020210822-and-v12120220905)
    * 6.1.2 [Superset (sqlalchemy < 1.4)](#superset-sqlalchemy-14)
  * 6.2 [Server](#server)
    * 6.2.1 [https://github.com/ClickHouse/ClickHouse/issues/41380](#httpsgithubcomclickhouseclickhouseissues41380)
    * 6.2.2 [https://github.com/ClickHouse/ClickHouse/issues/42669](#httpsgithubcomclickhouseclickhouseissues42669)
    * 6.2.3 [https://github.com/ClickHouse/ClickHouse/issues/43816](#httpsgithubcomclickhouseclickhouseissues43816)
    * 6.2.4 [https://github.com/ClickHouse/ClickHouse/issues/42596](#httpsgithubcomclickhouseclickhouseissues42596)
    * 6.2.5 [https://github.com/ClickHouse/ClickHouse/issues/44511](#httpsgithubcomclickhouseclickhouseissues44511)
    * 6.2.6 [https://github.com/ClickHouse/ClickHouse/issues/43140](#httpsgithubcomclickhouseclickhouseissues43140)
    * 6.2.7 [https://github.com/ClickHouse/ClickHouse/issues/44467](#httpsgithubcomclickhouseclickhouseissues44467)
* 7 [New Features](#new-features)
  * 7.1 [Altinity NRE Projects](#altinity-nre-projects)
  * 7.2 [Altinity Stable Backports](#altinity-stable-backports)
  * 7.3 [Changelog](#changelog)
    * 7.3.1 [New Feature](#new-feature)
    * 7.3.2 [Performance Improvement](#performance-improvement)
    * 7.3.3 [Improvement](#improvement)
    * 7.3.4 [Build/Testing/Packaging Improvement](#buildtestingpackaging-improvement)
    * 7.3.5 [Bug Fix (user-visible misbehavior in official stable or prestable release)](#bug-fix-user-visible-misbehavior-in-official-stable-or-prestable-release)
    * 7.3.6 [NO CL ENTRY](#no-cl-entry)
    * 7.3.7 [Bug Fix (user-visible misbehaviour in official stable or prestable release)](#bug-fix-user-visible-misbehaviour-in-official-stable-or-prestable-release)
* 8 [Test Results](#test-results)
  * 8.1 [Summary](#summary)
* 9 [Scope](#scope)
  * 9.1 [Automated Regression Tests](#automated-regression-tests)
    * 9.1.1 [Stateless](#stateless)
    * 9.1.2 [Stateful](#stateful)
    * 9.1.3 [Stress](#stress)
    * 9.1.4 [Integration](#integration)
    * 9.1.5 [Altinity Integration](#altinity-integration)
      * 9.1.5.1 [Tiered-storage](#tiered-storage)
      * 9.1.5.2 [S3](#s3)
      * 9.1.5.3 [Kafka](#kafka)
      * 9.1.5.4 [Kerberos](#kerberos)
      * 9.1.5.5 [DateTime64 Extended Range](#datetime64-extended-range)
      * 9.1.5.6 [Extended Precision Data Types](#extended-precision-data-types)
      * 9.1.5.7 [LDAP](#ldap)
      * 9.1.5.8 [RBAC](#rbac)
      * 9.1.5.9 [Window Functions](#window-functions)
      * 9.1.5.10 [SSL Server](#ssl-server)
      * 9.1.5.11 [Disk Level Encryption](#disk-level-encryption)
      * 9.1.5.12 [ClickHouse Keeper](#clickhouse-keeper)
      * 9.1.5.13 [Map Type](#map-type)
      * 9.1.5.14 [Part Moves Between Shards](#part-moves-between-shards)
      * 9.1.5.15 [Lightweight Delete](#lightweight-delete)
      * 9.1.5.16 [Base58](#base58)
      * 9.1.5.17 [Parquet](#parquet)
      * 9.1.5.18 [Atomic Insert](#atomic-insert)
      * 9.1.5.19 [Aggregate Functions](#aggregate-functions)
      * 9.1.5.20 [DNS](#dns)
  * 9.2 [Compatibility with Client Drivers](#compatibility-with-client-drivers)
    * 9.2.1 [Python `clickhouse_driver`](#python-clickhouse_driver)
    * 9.2.2 [ODBC `clickhouse-odbc`](#odbc-clickhouse-odbc)
    * 9.2.3 [SQLAlchemy](#sqlalchemy)
    * 9.2.4 [Java `clickhouse-jdbc`](#java-clickhouse-jdbc)
  * 9.3 [Backup `clickhouse-backup`](#backup-clickhouse-backup)
  * 9.4 [Compatibility With Operation on Kubernetes](#compatibility-with-operation-on-kubernetes)
    * 9.4.1 [Kubernetes `clickhouse-operator`](#kubernetes-clickhouse-operator)
    * 9.4.2 [Altinity.Cloud](#altinitycloud)
  * 9.5 [Production Cluster Operation](#production-cluster-operation)
  * 9.6 [Upgrade and Downgrade](#upgrade-and-downgrade)
    * 9.6.1 [Upgrade](#upgrade)
    * 9.6.2 [Downgrade](#downgrade)
  * 9.7 [Compatibility With BI Tools](#compatibility-with-bi-tools)
    * 9.7.1 [Grafana](#grafana)
    * 9.7.2 [Tableau](#tableau)
    * 9.7.3 [Superset](#superset)

## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitLab Repository].
All the updates are tracked using the [Revision History].

## Introduction

This test plan covers testing of ClickHouse 22.8 LTS (long-term support) release.

## Timeline

The testing of pre-stable binaries SHALL be started on September 21, 2022 and be completed
by December 31, 2022.

## Human Resources And Assignments

The following team members SHALL be dedicated to the release:

* Vitaliy Zakaznikov (manager, regression)
* Myroslav Tkachenko (S3, tiered-storage, regression)
* Andrey Antipov (clickhouse-operator)
* Vitalii Sviderskyi (clickhouse-backup, ACM, ACM backup)
* Ivan Sidorov (clickhouse-keeper, part-moves-between-shards)
* Andrey Antipov (disk level encryption, Python clickhouse-driver, JDBC driver, ODBC driver, clickhouse-sqlalchemy)
* Dima Borovstov (Tableau)
* Eugene Klimov (Grafana, Superset)
* Tatiana Saltykova (production cluster, upgrade and downgrade)

## End User Recomendations

### Settings

#### local_filesystem_read_method = pread

We recommend users to set `local_filesystem_read_method = pread`.

## Known Issues

### Compatibility

#### ODBC `clickhouse-odbc` (v1.1.10.20210822 and v1.2.1.20220905)

The `v1.1.10.20210822` and `v1.2.1.20220905` tests related to time zones fails (https://github.com/ClickHouse/clickhouse-odbc/issues/394).

#### Superset (sqlalchemy < 1.4)

Superset requires `sqlalchemy < 1.4` so with this conflict modern types like Map and Decimal fixes are not available.

### Server

#### https://github.com/ClickHouse/ClickHouse/issues/41380

Using LDAP user from a group with no matching ClickHouse role causes hangup.

#### https://github.com/ClickHouse/ClickHouse/issues/42669

Constant value 0(Int8) is regarded as positional argument and cause out-of-range exception.

#### https://github.com/ClickHouse/ClickHouse/issues/43816

Deadlock in ReplicatedMergeTreeQueue/MergeTreeBackgroundExecutor when waiting for concurrently executing entry.

#### https://github.com/ClickHouse/ClickHouse/issues/42596

Degrading performance queries of type select when updating CH version to 22.8 LTS.

#### https://github.com/ClickHouse/ClickHouse/issues/44511

welchTTest and studentTTest functions started to behave differently starting from 22.6 as compared to 22.3

#### https://github.com/ClickHouse/ClickHouse/issues/43140

singleValueOrNull() aggregate function does not work with Map, Array or Tuple data types

#### https://github.com/ClickHouse/ClickHouse/issues/44467

sparkbar aggregate function causes server to be killed with OOM

## New Features

### Altinity NRE Projects

* Support to Nullable(LowCardinality(String)) in Arrow format input	Jump Trading	P0	Support to Nullable(LowCardinality(String)) in Arrow format input https://altinity.zendesk.com/agent/tickets/4449	1	2	Merged		22.8.x		https://github.com/ClickHouse/ClickHouse/issues/39635	https://github.com/ClickHouse/ClickHouse/pull/39654 https://github.com/ClickHouse/ClickHouse/pull/40037
* Base58 encoding/decoding P2 perf optimization	Jump Trading	P0	Rewrite the implementation w/o using an external library that is too slow	5	2	Merged		22.8.x			https://github.com/ClickHouse/ClickHouse/pull/39292
* Support proper reverse DNS lookup	Multiple	P1	Clickhouse does not check host restrictions correctly when host_regexp is used			Merged		22.8.x		https://github.com/ClickHouse/ClickHouse/issues/17202	https://github.com/ClickHouse/ClickHouse/pull/37827
* Non-negative derivative function in SQL	Jump Trading	P1	https://support.altinity.com/hc/en-us/requests/3468	5	7.5	Merged		22.7.x		https://github.com/Vertamedia/clickhouse-grafana/issues/386	https://github.com/ClickHouse/ClickHouse/pull/37628
* Support GCP object storage for DiskS3	Altinity, Jump	P1	Fix S3 disk support for GCS	15		Merged	TestFlows	22.7.x			https://github.com/ClickHouse/ClickHouse/pull/37882
* Base58 encoding/decoding P1 functions	Jump Trading	P1	We need a fast, native Base58 encoding/decoding function in ClickHouse. Ideally as a Base58 type like there is for IPv4	5	3	Merged		22.7.x			https://github.com/ClickHouse/ClickHouse/pull/38159
* Optimize ORDER BY and window functions with PK	FeatureSpace	P1	Optimize ORDER BY and window functions with PK	25	60	Merged		22.7.x		https://github.com/ClickHouse/ClickHouse/issues/27511	https://github.com/ClickHouse/ClickHouse/pull/34632
* Window functions -- use storage order	Jump Trading	P1	Use storage sort order to avoid extra sorting when possible	25	60	Merged		22.7.x		https://github.com/ClickHouse/ClickHouse/issues/19289	https://github.com/ClickHouse/ClickHouse/pull/34632

### Altinity Stable Backports

* https://github.com/ClickHouse/ClickHouse/pull/40620 - Base58 fix handling leading 0 / '1'
* https://github.com/ClickHouse/ClickHouse/pull/42321 - Increase request_timeout_ms for s3 disks
* https://github.com/clickHouse/clickhouse/pull/43038 - fix of binary compatibility of aggregate function state serialization
* https://github.com/ClickHouse/ClickHouse/pull/43297 - Parquet fix by Arthur for DemandBase
* https://github.com/ClickHouse/ClickHouse/pull/42134 - Improve lost replica recovery (ReplicatedMergeTree) - LogRoket

### Changelog

#### New Feature

* Add setting to disable limit on kafka_num_consumers. Closes [#40331](https://github.com/ClickHouse/ClickHouse/issues/40331). [#40670](https://github.com/ClickHouse/ClickHouse/pull/40670) ([Kruglov Pavel](https://github.com/Avogar)).
* Added support for parallel distributed insert select into tables with Distributed and Replicated engine [#34670](https://github.com/ClickHouse/ClickHouse/issues/34670). [#39107](https://github.com/ClickHouse/ClickHouse/pull/39107) ([Nikita Mikhaylov](https://github.com/nikitamikhaylov)).
* Added `SYSTEM SYNC DATABASE REPLICA` query which allows to sync tables metadata inside Replicated database, because currently synchronisation is asynchronous. [#35944](https://github.com/ClickHouse/ClickHouse/pull/35944) ([Nikita Mikhaylov](https://github.com/nikitamikhaylov)).

#### Performance Improvement

* ColumnVector: optimize UInt8 index with AVX512VBMI. [#41247](https://github.com/ClickHouse/ClickHouse/pull/41247) ([Guo Wangyang](https://github.com/guowangy)).
* For systems with AVX512 VBMI2, this PR improves performance by ca. 6% for SSB benchmark queries queries 3.1, 3.2 and 3.3 (SF=100). Tested on Intel Icelake Xeon 8380 * 2 socket. [#40033](https://github.com/ClickHouse/ClickHouse/pull/40033) ([Robert Schulze](https://github.com/rschu1ze)).
* Increased parallelism of query plan steps executed after aggregation. [#38295](https://github.com/ClickHouse/ClickHouse/pull/38295) ([Nikita Taranov](https://github.com/nickitat)).
* Improves performance of file descriptor cache by narrowing mutex scopes. [#36682](https://github.com/ClickHouse/ClickHouse/pull/36682) ([Anton Kozlov](https://github.com/tonickkozlov)).
* Now we split data parts into layers and distribute them among threads instead of whole parts to make the execution of queries with `FINAL` more data-parallel. [#36396](https://github.com/ClickHouse/ClickHouse/pull/36396) ([Nikita Taranov](https://github.com/nickitat)).
* Rewrite 'select countDistinct(a) from t' to 'select count(1) from (select a from t groupBy a)'. [#35993](https://github.com/ClickHouse/ClickHouse/pull/35993) ([zhanglistar](https://github.com/zhanglistar)).
* Sizes of hash tables used during aggregation now collected and used in later queries to avoid hash tables resizes. [#33439](https://github.com/ClickHouse/ClickHouse/pull/33439) ([Nikita Taranov](https://github.com/nickitat)).

#### Improvement

* Fix incompatibility of cache after switching setting `do_no_evict_index_and_mark_files` from 1 to 0, 0 to 1. [#41330](https://github.com/ClickHouse/ClickHouse/pull/41330) ([Kseniia Sumarokova](https://github.com/kssenii)).
* Fix issue with passing MySQL timeouts for MySQL database engine and MySQL table function. Closes [#34168](https://github.com/ClickHouse/ClickHouse/issues/34168)?notification_referrer_id=NT_kwDOAzsV57MzMDMxNjAzNTY5OjU0MjAzODc5. [#40751](https://github.com/ClickHouse/ClickHouse/pull/40751) ([Kseniia Sumarokova](https://github.com/kssenii)).
* The setting `show_addresses_in_stack_traces` was accidentally disabled in default `config.xml`. It's removed from the config now, so the setting is enabled by default. [#40749](https://github.com/ClickHouse/ClickHouse/pull/40749) ([Alexander Tokmakov](https://github.com/tavplubix)).
* Improve schema inference cache, respect format settings that can change the schema. [#40414](https://github.com/ClickHouse/ClickHouse/pull/40414) ([Kruglov Pavel](https://github.com/Avogar)).
* Improve and fix dictionaries in Arrow format. [#40173](https://github.com/ClickHouse/ClickHouse/pull/40173) ([Kruglov Pavel](https://github.com/Avogar)).
* Parameters are now transferred in `Query` packets right after the query text in the same serialisation format as the settings. [#39906](https://github.com/ClickHouse/ClickHouse/pull/39906) ([Nikita Taranov](https://github.com/nickitat)).
* Fix building aggregate projections when external aggregation is on. Mark as improvement because the case is rare and there exists easy workaround to fix it via changing settings. This fixes [#39667](https://github.com/ClickHouse/ClickHouse/issues/39667) . [#39671](https://github.com/ClickHouse/ClickHouse/pull/39671) ([Amos Bird](https://github.com/amosbird)).
* Improved memory usage during memory efficient merging of aggregation results. [#39429](https://github.com/ClickHouse/ClickHouse/pull/39429) ([Nikita Taranov](https://github.com/nickitat)).
* Handling SIGTERM signals from k8s. [#39130](https://github.com/ClickHouse/ClickHouse/pull/39130) ([Timur Solodovnikov](https://github.com/tsolodov)).
* Now entrypoint.sh in docker image creates and executes chown for all folders it found in config for multidisk setup [#17717](https://github.com/ClickHouse/ClickHouse/issues/17717). [#39121](https://github.com/ClickHouse/ClickHouse/pull/39121) ([Nikita Mikhaylov](https://github.com/nikitamikhaylov)).
* Allow to specify globs `* or {expr1, expr2, expr3}` inside a key for `clickhouse-extract-from-config` tool. [#38966](https://github.com/ClickHouse/ClickHouse/pull/38966) ([Nikita Mikhaylov](https://github.com/nikitamikhaylov)).
* Add revision() function. [#38555](https://github.com/ClickHouse/ClickHouse/pull/38555) ([Azat Khuzhin](https://github.com/azat)).
* Add implicit grants with grant option too. For example `GRANT CREATE TABLE ON test.* TO A WITH GRANT OPTION` now allows `A` to execute `GRANT CREATE VIEW ON test.* TO B`. [#38017](https://github.com/ClickHouse/ClickHouse/pull/38017) ([Vitaly Baranov](https://github.com/vitlibar)).
* Now if a shard has local replica we create a local plan and a plan to read from all remote replicas. They have shared initiator which coordinates reading. [#37204](https://github.com/ClickHouse/ClickHouse/pull/37204) ([Nikita Mikhaylov](https://github.com/nikitamikhaylov)).
* Do not calculate an integral numerically but use CDF functions instead. This will speed up execution and will increase the precision. This fixes [#36714](https://github.com/ClickHouse/ClickHouse/issues/36714). [#36953](https://github.com/ClickHouse/ClickHouse/pull/36953) ([Nikita Mikhaylov](https://github.com/nikitamikhaylov)).
* After [#36425](https://github.com/ClickHouse/ClickHouse/issues/36425) settings like `background_fetches_pool_size` became obsolete and can appear in top level config, but clickhouse throws and exception like `Error updating configuration from '/etc/clickhouse-server/config.xml' config.: Code: 137. DB::Exception: A setting 'background_fetches_pool_size' appeared at top level in config /etc/clickhouse-server/config.xml.` This is fixed. [#36917](https://github.com/ClickHouse/ClickHouse/pull/36917) ([Nikita Mikhaylov](https://github.com/nikitamikhaylov)).
* We create a local interpreter if we want to execute query on localhost replica. But for when executing query on multiple replicas we rely on the fact that a connection exists so replicas can talk to coordinator. It is now improved and localhost replica can talk to coordinator directly in the same process. [#36281](https://github.com/ClickHouse/ClickHouse/pull/36281) ([Nikita Mikhaylov](https://github.com/nikitamikhaylov)).
* - Add branch to avoid unnecessary memcpy in readbig. [#36095](https://github.com/ClickHouse/ClickHouse/pull/36095) ([jasperzhu](https://github.com/jinjunzh)).
* `clickhouse-keeper` starts answering 4-letter commands before getting the quorum. [#35992](https://github.com/ClickHouse/ClickHouse/pull/35992) ([Antonio Andelic](https://github.com/antonio2368)).
* Added support for schema inference for `hdfsCluster`. [#35812](https://github.com/ClickHouse/ClickHouse/pull/35812) ([Nikita Mikhaylov](https://github.com/nikitamikhaylov)).
* - Improve the pipeline description for JOIN. [#35612](https://github.com/ClickHouse/ClickHouse/pull/35612) ([何李夫](https://github.com/helifu)).
* Added support for schema inference for `hdfsCluster`. [#35602](https://github.com/ClickHouse/ClickHouse/pull/35602) ([Nikita Mikhaylov](https://github.com/nikitamikhaylov)).
* Added a support for automatic schema inference to `s3Cluster` table function. Synced the signatures of `s3 ` and `s3Cluster`. [#35544](https://github.com/ClickHouse/ClickHouse/pull/35544) ([Nikita Mikhaylov](https://github.com/nikitamikhaylov)).
* fix INSERT INTO table FROM INFILE does not display progress bar. [#35429](https://github.com/ClickHouse/ClickHouse/pull/35429) ([chen](https://github.com/xiedeyantu)).
* Added an ability to specify cluster secret in replicated database. [#35333](https://github.com/ClickHouse/ClickHouse/pull/35333) ([Nikita Mikhaylov](https://github.com/nikitamikhaylov)).

#### Build/Testing/Packaging Improvement

* Add `source` field to deb packages, update `nfpm`. [#41531](https://github.com/ClickHouse/ClickHouse/pull/41531) ([Mikhail f. Shiryaev](https://github.com/Felixoid)).
* Add macOS binaries to GH release assets, it fixes [#37718](https://github.com/ClickHouse/ClickHouse/issues/37718). [#41088](https://github.com/ClickHouse/ClickHouse/pull/41088) ([Mikhail f. Shiryaev](https://github.com/Felixoid)).
* Fix TGZ packages. [#40681](https://github.com/ClickHouse/ClickHouse/pull/40681) ([Mikhail f. Shiryaev](https://github.com/Felixoid)).
* fix MacOS build compressor faild. [#38007](https://github.com/ClickHouse/ClickHouse/pull/38007) ([chen](https://github.com/xiedeyantu)).
* Fix failed tests in: https://s3.amazonaws.com/clickhouse-test-reports/35422/32348779fd0bac5276727cfc01e75c625ecc69b9/fuzzer_astfuzzerubsan,actions//report.html. [#35439](https://github.com/ClickHouse/ClickHouse/pull/35439) ([李扬](https://github.com/taiyang-li)).

#### Bug Fix (user-visible misbehavior in official stable or prestable release)

* Old versions of Replicated database doesn't have a special marker in [Zoo]Keeper. We need to check only whether the node contains come obscure data instead of special mark. [#41875](https://github.com/ClickHouse/ClickHouse/pull/41875) ([Nikita Mikhaylov](https://github.com/nikitamikhaylov)).
* Don't allow to create or alter merge tree tables with virtual column name _row_exists, which is reserved for lightweight delete. Fixed [#41716](https://github.com/ClickHouse/ClickHouse/issues/41716). [#41763](https://github.com/ClickHouse/ClickHouse/pull/41763) ([Jianmei Zhang](https://github.com/zhangjmruc)).
* Fix possible crash in `SELECT` from `Merge` table with enabled `optimize_monotonous_functions_in_order_by` setting. Fixes [#41269](https://github.com/ClickHouse/ClickHouse/issues/41269). [#41740](https://github.com/ClickHouse/ClickHouse/pull/41740) ([Nikolai Kochetov](https://github.com/KochetovNicolai)).
* Fix possible `pipeline stuck` exception for queries with `OFFSET`. The error was found with `enable_optimize_predicate_expression = 0` and always false condition in `WHERE`. Fixes [#41383](https://github.com/ClickHouse/ClickHouse/issues/41383). [#41588](https://github.com/ClickHouse/ClickHouse/pull/41588) ([Nikolai Kochetov](https://github.com/KochetovNicolai)).
* Fix possible hung/deadlock on query cancellation (`KILL QUERY` or server shutdown). [#41467](https://github.com/ClickHouse/ClickHouse/pull/41467) ([Azat Khuzhin](https://github.com/azat)).
* Writing data in Apache `ORC` format might lead to a buffer overrun. [#41458](https://github.com/ClickHouse/ClickHouse/pull/41458) ([Alexey Milovidov](https://github.com/alexey-milovidov)).
* The aggregate function `categorialInformationValue` was having incorrectly defined properties, which might cause a null pointer dereferencing at runtime. This closes [#41443](https://github.com/ClickHouse/ClickHouse/issues/41443). [#41449](https://github.com/ClickHouse/ClickHouse/pull/41449) ([Alexey Milovidov](https://github.com/alexey-milovidov)).
* Malicious data in Native format might cause a crash. [#41441](https://github.com/ClickHouse/ClickHouse/pull/41441) ([Alexey Milovidov](https://github.com/alexey-milovidov)).
* Since 22.8 `ON CLUSTER` clause is ignored if database is `Replicated` and cluster name and database name are the same. Because of this `DROP PARTITION ON CLUSTER` worked unexpected way with `Replicated`. It's fixed, now `ON CLUSTER` clause is ignored only for queries that are replicated on database level. Fixes [#41299](https://github.com/ClickHouse/ClickHouse/issues/41299). [#41390](https://github.com/ClickHouse/ClickHouse/pull/41390) ([Alexander Tokmakov](https://github.com/tavplubix)).
* Fix possible deadlock with async_socket_for_remote/use_hedged_requests and parallel KILL. [#41343](https://github.com/ClickHouse/ClickHouse/pull/41343) ([Azat Khuzhin](https://github.com/azat)).
* Add column type check before UUID insertion in MsgPack format. [#41309](https://github.com/ClickHouse/ClickHouse/pull/41309) ([Kruglov Pavel](https://github.com/Avogar)).
* Fix incorrect logical error `Expected relative path` in disk object storage. Related to [#41246](https://github.com/ClickHouse/ClickHouse/issues/41246). [#41297](https://github.com/ClickHouse/ClickHouse/pull/41297) ([Kseniia Sumarokova](https://github.com/kssenii)).
* Queries with `OFFSET` clause in subquery and `WHERE` clause in outer query might return incorrect result, it's fixed. Fixes [#40416](https://github.com/ClickHouse/ClickHouse/issues/40416). [#41280](https://github.com/ClickHouse/ClickHouse/pull/41280) ([Alexander Tokmakov](https://github.com/tavplubix)).
* Fix background clean up of broken detached parts. [#41190](https://github.com/ClickHouse/ClickHouse/pull/41190) ([Kseniia Sumarokova](https://github.com/kssenii)).
* Fixed "possible deadlock avoided" error on automatic conversion of database engine from Ordinary to Atomic. [#41146](https://github.com/ClickHouse/ClickHouse/pull/41146) ([Alexander Tokmakov](https://github.com/tavplubix)).
* Fix possible segfaults, use-heap-after-free and memory leak in aggregate function combinators. Closes [#40848](https://github.com/ClickHouse/ClickHouse/issues/40848). [#41083](https://github.com/ClickHouse/ClickHouse/pull/41083) ([Kruglov Pavel](https://github.com/Avogar)).
* Fix access rights for `DESCRIBE TABLE url()` and some other `DESCRIBE TABLE <table_function>()`. [#40975](https://github.com/ClickHouse/ClickHouse/pull/40975) ([Vitaly Baranov](https://github.com/vitlibar)).
* In [#40595](https://github.com/ClickHouse/ClickHouse/issues/40595) it was reported that the `host_regexp` functionality was not working properly with a name to address resolution in `/etc/hosts`. It's fixed. [#40769](https://github.com/ClickHouse/ClickHouse/pull/40769) ([Arthur Passos](https://github.com/arthurpassos)).
* Fix memory leak while pushing to MVs w/o query context (from Kafka/...). [#40732](https://github.com/ClickHouse/ClickHouse/pull/40732) ([Azat Khuzhin](https://github.com/azat)).
* During insertion of a new query to the `ProcessList` allocations happen. If we reach the memory limit during these allocations we can not use `OvercommitTracker`, because `ProcessList::mutex` is already acquired. Fixes [#40611](https://github.com/ClickHouse/ClickHouse/issues/40611). [#40677](https://github.com/ClickHouse/ClickHouse/pull/40677) ([Dmitry Novik](https://github.com/novikd)).
* Fix vertical merge of parts with lightweight deleted rows. [#40559](https://github.com/ClickHouse/ClickHouse/pull/40559) ([Alexander Gololobov](https://github.com/davenger)).
* Fix possible error 'Decimal math overflow' while parsing DateTime64. [#40546](https://github.com/ClickHouse/ClickHouse/pull/40546) ([Kruglov Pavel](https://github.com/Avogar)).
* Fix potential dataloss due to a bug in AWS SDK (https://github.com/aws/aws-sdk-cpp/issues/658). Bug can be triggered only when clickhouse is used over S3. [#40506](https://github.com/ClickHouse/ClickHouse/pull/40506) ([alesapin](https://github.com/alesapin)).
* - Fix crash while parsing values of type `Object` that contains arrays of variadic dimension. [#40483](https://github.com/ClickHouse/ClickHouse/pull/40483) ([Duc Canh Le](https://github.com/canhld94)).
* Fix incorrect fallback to skip cache which happened on very high concurrency level. [#40420](https://github.com/ClickHouse/ClickHouse/pull/40420) ([Kseniia Sumarokova](https://github.com/kssenii)).
* Proxy resolver stop on first successful request to endpoint. [#40353](https://github.com/ClickHouse/ClickHouse/pull/40353) ([Maksim Kita](https://github.com/kitaisreal)).
* Fix rare bug with column TTL for MergeTree engines family: In case of repeated vertical merge the error `Cannot unlink file ColumnName.bin ... No such file or directory.` could happen. [#40346](https://github.com/ClickHouse/ClickHouse/pull/40346) ([alesapin](https://github.com/alesapin)).
* Fix bug in collectFilesToSkip() by adding correct file extension(.idx or idx2) for indexes to be recalculated, avoid wrong hard links. Fixed [#39896](https://github.com/ClickHouse/ClickHouse/issues/39896). [#40095](https://github.com/ClickHouse/ClickHouse/pull/40095) ([Jianmei Zhang](https://github.com/zhangjmruc)).
* fix: expose new CH keeper port in Dockerfile clickhouse/clickhouse-keeper fix: use correct KEEPER_CONFIG filename in clickhouse/clickhouse-keeper docker image. [#38462](https://github.com/ClickHouse/ClickHouse/pull/38462) ([Evgeny Kruglov](https://github.com/nordluf)).
* Rewrite tuple functions as literals in backwards-compatibility mode. [#38096](https://github.com/ClickHouse/ClickHouse/pull/38096) ([Anton Kozlov](https://github.com/tonickkozlov)).
* The clickhouse-keeper setting `dead_session_check_period_ms` was transformed into microseconds (multiplied by 1000), which lead to dead sessions only being cleaned up after several minutes (instead of 500ms). [#37824](https://github.com/ClickHouse/ClickHouse/pull/37824) ([Michael Lex](https://github.com/mlex)).
* Fix LOGICAL_ERROR in getMaxSourcePartsSizeForMerge during merges (in case of non standard, greater, values of `background_pool_size`/`background_merges_mutations_concurrency_ratio` has been specified in `config.xml` (new way) not in `users.xml` (deprecated way)). [#37413](https://github.com/ClickHouse/ClickHouse/pull/37413) ([Azat Khuzhin](https://github.com/azat)).
* Fix `GROUP BY` `AggregateFunction` (i.e. you `GROUP BY` by the column that has `AggregateFunction` type). [#37093](https://github.com/ClickHouse/ClickHouse/pull/37093) ([Azat Khuzhin](https://github.com/azat)).

#### NO CL ENTRY

* NO CL ENTRY:  'Backport [#41281](https://github.com/ClickHouse/ClickHouse/issues/41281) to 22.8: Fix wrong literal name in KeyCondition using ActionsDAG.'. [#41685](https://github.com/ClickHouse/ClickHouse/pull/41685) ([robot-ch-test-poll2](https://github.com/robot-ch-test-poll2)).
* NO CL ENTRY:  'Backport [#41345](https://github.com/ClickHouse/ClickHouse/issues/41345) to 22.8: Increase open files limit'. [#41414](https://github.com/ClickHouse/ClickHouse/pull/41414) ([robot-ch-test-poll1](https://github.com/robot-ch-test-poll1)).
* NO CL ENTRY:  'Revert "Avx enablement"'. [#40462](https://github.com/ClickHouse/ClickHouse/pull/40462) ([Alexey Milovidov](https://github.com/alexey-milovidov)).

#### Bug Fix (user-visible misbehaviour in official stable or prestable release)

* Fix bug datetime64 parse from string '1969-12-31 23:59:59.123'. Close [#36994](https://github.com/ClickHouse/ClickHouse/issues/36994). [#37039](https://github.com/ClickHouse/ClickHouse/pull/37039) ([李扬](https://github.com/taiyang-li)).
* TTL merge may not be scheduled again if BackgroundExecutor is busy. --merges_with_ttl_counter is increased in selectPartsToMerge() --merge task will be ignored if BackgroundExecutor is busy --merges_with_ttl_counter will not be decrease. [#36387](https://github.com/ClickHouse/ClickHouse/pull/36387) ([lthaooo](https://github.com/lthaooo)).
* Accidentally ZSTD support for Arrow was not being built. This fixes [#35283](https://github.com/ClickHouse/ClickHouse/issues/35283). [#35486](https://github.com/ClickHouse/ClickHouse/pull/35486) ([Sean Lafferty](https://github.com/seanlaff)).
* Fix wrong result of datetime64 when negative. Close [#34831](https://github.com/ClickHouse/ClickHouse/issues/34831). [#35440](https://github.com/ClickHouse/ClickHouse/pull/35440) ([李扬](https://github.com/taiyang-li)).

## Test Results

Test results SHALL be accessible at https://altinity-test-reports.s3.amazonaws.com/index.html#reports/22.8-lts/.

### Summary

| Test Suite  | Result | Comments |
| --- | --- | --- |
| Stateless |  |   |
| Stateful |  |   |
| Stress |  |   |
| Integration |  |   |
| Tiered Storage (Local) |  |   |
| Tiered Storage (MinIO) |  |   |
| Tiered Storage (AWS) |  |   |
| S3 (AWS) |  |  |
| S3 (MinIO)  |   |
| S3 (GCS) |  |   |
| Kafka |  |   |
| Kerberos |  |   |
| DateTime64 Extended Range |  |   |
| Extended Precision Data Types |  |   |
| LDAP |  |   |
| RBAC |  |   |
| Window Functions |  |   |
| SSL Server |  |   |
| Disk Level Encryption |  |   |
| ClickHouse Keeper |  |   |
| Map Type |  |   |
| Part Moves Between Shards |  |   |
| Lightweight Delete |  |    |
| Aggregate functions | [Pass](#aggregate-functions) |  |
| Python `clickhouse_driver` | [Pass](#python-clickhouse_driver) |   |
| ODBC `clickhouse-odbc` | [Pass*](#odbc-clickhouse-odbc) | In `v1.1.10.20210822` and `v1.2.1.20220905` tests related to time zones fail |
| SQLAlchemy | [Pass](#sqlalchemy) |    |
| Java `clickhouse-jdbc` | [Pass](#java-clickhouse-jdbc) |   |
| Java `clickhouse-jdbc` (DBeaver) | [Pass](#java-clickhouse-jdbc) |   |
| Backup `clickhouse-backup` |  |   |
| Kubernetes `clickhouse-operator` | [Pass](#kubernetes-clickhouse-operator) |   |
| Altinity.Cloud |  |   |
| Production Cluster Operation |  |   |
| Upgrade And Downgrade |  |   |
| Grafana |  |   |
| Tableau |  |   |
| Superset |  |   |

## Scope

The scope of testing ClickHouse 22.8 LTS release SHALL be defined as follows.

### Automated Regression Tests

The following automated regression test suites SHALL be executed.

#### Stateless

Results:

The `stateless` suite consists of running SQL, python and bash scripts that check various features of the server.
The test suite can be found at https://github.com/ClickHouse/ClickHouse/tree/22.8/tests/queries/0_stateless

#### Stateful

Results:

The `stateful` suite consists of running SQL scripts executed against a predefined database schema.
The test suite can be found at https://github.com/ClickHouse/ClickHouse/tree/22.8/tests/queries/1_stateful

#### Stress

Results:

The `stress` suite consists of running tests from the `stateless` suite in parallel to check for server hang-up and crashes.

#### Integration

Results:

The `integration` suite of tests consists of various suites of automated tests that use [PyTest Framework](https://pytest.org) .
The test suite can be found at https://github.com/ClickHouse/ClickHouse/tree/22.8/tests/integration

#### Altinity Integration

##### Tiered-storage

Results: (Local) 

Results: (MinIO) 

Results: (AWS) 

The `tiered-storage` suite must be integrated to TestFlows check.

##### S3

Results: (AWS S3) 

Results: (MinIO) 

Results: (GCS) 

The `s3` suite must be integrated to TestFlows check. The following S3 backends SHALL be verified:

* MinIO
* AWS S3
* GCS

In addition to the following functionality SHALL be verified:

* Zero-copy replication
* Backup/Restore of S3 tables

##### Kafka

Results: 

Altinity Kafka integration tests that use docker-compose environment in addition to integration tests
in ClickHouse repo.

##### Kerberos

Results: /

Altinity Kerberos integration tests.

##### DateTime64 Extended Range

Results: 

Altinity DateTime64 extended range integration tests.

##### Extended Precision Data Types

Results: 

Altinity Extended Precision Data Types integration tests.

##### LDAP

Results: 

Altinity LDAP integration tests.

##### RBAC

Results: 

Altinity RBAC integration tests.

##### Window Functions

Results: 

Altinity Window Functions integration tests.

##### SSL Server

Results: 

Altinity basic SSL server integration tests.

##### Disk Level Encryption

Results: 

Altinity Disk Level Encryption integration tests.

##### ClickHouse Keeper

Results: 

Altinity ClickHouse Keeper integration tests.

##### Map Type

Results: 

Altinity Map data type integration tests.

##### Part Moves Between Shards

Results: 

Altinity Part Moves Between Shards integration tests.

##### Lightweight Delete

Results: 

Altinity Lightweight Delete (`DELETE`) integration tests.

##### Base58

Results: 

Altinity Base58 encode and decode functions integration tests.

##### Parquet

Results: 

Altinity Parquet format integration tests.

##### Atomic Insert

Results: 

Altinity Atomic Insert integration tests.

##### Aggregate Functions

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/22.8-lts/aggregate_functions/

Altinity Aggregate Functions integration tests.

##### DNS

Results: 

Altinity DNS integration tests.

### Compatibility with Client Drivers

The following client drivers SHALL be tested for compatibility:

#### Python `clickhouse_driver`

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/22.8-lts/clickhouse-driver/

The [clickhouse-driver](https://github.com/mymarilyn/clickhouse-driver) SHALL be verified to work correctly by
executing automated tests in https://github.com/mymarilyn/clickhouse-driver/tree/master/tests

The following versions SHALL be verified:

* 0.2.4
* 0.2.5

#### ODBC `clickhouse-odbc`

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/22.8-lts/clickhouse-odbc/

The operation of `clickhouse-odbc` driver SHALL be verified by executing automated tests in
https://github.com/ClickHouse/clickhouse-odbc/tree/master/test

The following versions SHALL be verified:

* https://github.com/ClickHouse/clickhouse-odbc/releases/tag/v1.1.9.20201226
* https://github.com/ClickHouse/clickhouse-odbc/releases/tag/v1.1.10.20210822
* https://github.com/ClickHouse/clickhouse-odbc/releases/tag/v1.2.1.20220905

#### SQLAlchemy

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/22.8-lts/clickhouse-sqlalchemy/

The https://github.com/xzkostyan/clickhouse-sqlalchemy ClickHouse dialect for SQLAlchemy SHALL be verified to work correctly
by executing automated tests in https://github.com/xzkostyan/clickhouse-sqlalchemy/tree/master/tests

The following versions SHALL be verified:

* https://github.com/xzkostyan/clickhouse-sqlalchemy/releases/tag/0.2.2
* https://github.com/xzkostyan/clickhouse-sqlalchemy/releases/tag/0.2.3

#### Java `clickhouse-jdbc`

Results (0.3.2): https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/22.8-lts/clickhouse-jdbc/v0.3.2/

Results (DBeaver): https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/22.8-lts/clickhouse-jdbc/DBeaver/

Basic functionality of https://github.com/ClickHouse/clickhouse-jdbc SHALL be verified.

The following versions SHALL be verified:

* https://github.com/ClickHouse/clickhouse-jdbc/releases/tag/v0.3.2

### Backup `clickhouse-backup`

Results: 
Results (ACM): 

The compatibility with [clickhouse-backup](https://github.com/altinity/clickhouse-backup) utility SHALL be verified.

### Compatibility With Operation on Kubernetes

#### Kubernetes `clickhouse-operator`

Results: https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/22.8-lts/clickhouse-operator/

Compatibility with `clickhouse-operator` in Kubernetes environment SHALL be verified.

#### Altinity.Cloud

Results: 

Compatibility with Altinity.Cloud SHALL be verified.

### Production Cluster Operation

Results: _manual testing to be performed by support team_

Operation on a production cluster SHALL be verified.

### Upgrade and Downgrade

Results: _manual testing to be performed by support team_

The upgrade and downgrade path SHALL be verified on the following combinations using ACM
and reference production like cluster

#### Upgrade

* from 22.3 to 22.8

#### Downgrade

* from 22.8 to 22.3

### Compatibility With BI Tools

Compatibility with the following BI tools SHALL be verified.

#### Grafana

Results: 

Compatibility with [Grafana] SHALL be verified using
https://grafana.com/grafana/plugins/vertamedia-clickhouse-datasource/ data source for the following versions:

* 2.4.3
* Grafana 8.4

#### Tableau

Results: 

Compatibility with [Tableau] SHALL be verified using the current version of
https://github.com/Altinity/clickhouse-tableau-connector-odbc connector.

#### Superset

Results: 

Compatibility with [Superset] SHALL be verified using the following pre-requisites:

* clickhouse-sqlalchemy==0.1.8
* latest clickhouse-sqlalchemy 0.2.0
* sqlalchemy >= 1.4, < 1.5

> Note: Superset requires sqlalchemy < 1.4 so with this conflict modern types like Map and Decimal fixes not available.

[Grafana]: https://grafana.com/
[Tableau]: https://www.tableau.com/
[Superset]: https://superset.apache.org/
[ClickHouse]: https://clickhouse.tech
[GitLab Repository]: https://gitlab.com/altinity-qa/documents/qa-stp004-clickhouse-22.8-long-term-support-release/
[Revision History]: https://gitlab.com/altinity-qa/documents/qa-stp004-clickhouse-22.8-long-term-support-release/-/commits/main/
[Git]: https://git-scm.com/
[GitLab]: https://gitlab.com
