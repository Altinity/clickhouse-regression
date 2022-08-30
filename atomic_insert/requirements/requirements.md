# SRS028 ClickHouse Atomic Inserts
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Related Resources](#related-resources)
* 3 [Terminology](#terminology)
  * 3.1 [SRS](#srs)
  * 3.2 [Atomic Inserts](#atomic-inserts)
* 4 [Requirements](#requirements)
  * 4.1 [RQ.SRS-028.ClickHouse.AtomicInserts](#rqsrs-028clickhouseatomicinserts)
  * 4.2 [Insert Settings](#insert-settings)
    * 4.2.1 [RQ.SRS-028.ClickHouse.AtomicInserts.InsertSettings](#rqsrs-028clickhouseatomicinsertsinsertsettings)
  * 4.3 [Blocks And Partitions](#blocks-and-partitions)
    * 4.3.1 [RQ.SRS-028.ClickHouse.AtomicInserts.BlocksAndPartitions](#rqsrs-028clickhouseatomicinsertsblocksandpartitions)
  * 4.4 [Supported Table Engines](#supported-table-engines)
    * 4.4.1 [Merge Tree](#merge-tree)
      * 4.4.1.1 [RQ.SRS-028.ClickHouse.AtomicInserts.SupportedTableEngines.MergeTree](#rqsrs-028clickhouseatomicinsertssupportedtableenginesmergetree)
    * 4.4.2 [Replicated Merge Tree](#replicated-merge-tree)
      * 4.4.2.1 [RQ.SRS-028.ClickHouse.AtomicInserts.SupportedTableEngines.ReplicatedMergeTree](#rqsrs-028clickhouseatomicinsertssupportedtableenginesreplicatedmergetree)
  * 4.5 [Dependent Tables](#dependent-tables)
    * 4.5.1 [RQ.SRS-028.ClickHouse.AtomicInserts.DependentTables](#rqsrs-028clickhouseatomicinsertsdependenttables)
  * 4.6 [Distributed Table](#distributed-table)
    * 4.6.1 [RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable](#rqsrs-028clickhouseatomicinsertsdistributedtable)
    * 4.6.2 [RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.ShardUnavailable](#rqsrs-028clickhouseatomicinsertsdistributedtableshardunavailable)
    * 4.6.3 [RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.ReplicaUnavailable](#rqsrs-028clickhouseatomicinsertsdistributedtablereplicaunavailable)
    * 4.6.4 [RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.KeeperReadOnly](#rqsrs-028clickhouseatomicinsertsdistributedtablekeeperreadonly)
  * 4.7 [Multiple Tables](#multiple-tables)
    * 4.7.1 [RQ.SRS-028.ClickHouse.AtomicInserts.MultipleTables](#rqsrs-028clickhouseatomicinsertsmultipletables)
  * 4.8 [Data Duplication](#data-duplication)
    * 4.8.1 [RQ.SRS-028.ClickHouse.AtomicInserts.DataDuplication](#rqsrs-028clickhouseatomicinsertsdataduplication)
  * 4.9 [Failure Modes](#failure-modes)
      * 4.9.1.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.OneOrMoreParts](#rqsrs-028clickhouseatomicinsertsfailuresoneormoreparts)
    * 4.9.2 [Syntax Error](#syntax-error)
      * 4.9.2.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.SyntaxError](#rqsrs-028clickhouseatomicinsertsfailuressyntaxerror)
    * 4.9.3 [Mismatched Table Structure](#mismatched-table-structure)
      * 4.9.3.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.MismatchedTableStructure](#rqsrs-028clickhouseatomicinsertsfailuresmismatchedtablestructure)
    * 4.9.4 [Circular Dependent Tables](#circular-dependent-tables)
      * 4.9.4.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.CircularDependentTables](#rqsrs-028clickhouseatomicinsertsfailurescirculardependenttables)
    * 4.9.5 [Emulated Error](#emulated-error)
      * 4.9.5.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.EmulatedUsingThrowIf](#rqsrs-028clickhouseatomicinsertsfailuresemulatedusingthrowif)
    * 4.9.6 [Disk Corruption](#disk-corruption)
      * 4.9.6.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.DiskCorruption](#rqsrs-028clickhouseatomicinsertsfailuresdiskcorruption)
    * 4.9.7 [Slow Disk](#slow-disk)
        * 4.9.7.1.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.SlowDisk](#rqsrs-028clickhouseatomicinsertsfailuresslowdisk)
    * 4.9.8 [User Rights](#user-rights)
      * 4.9.8.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.UserRights](#rqsrs-028clickhouseatomicinsertsfailuresuserrights)
    * 4.9.9 [Out of Sync Replicas](#out-of-sync-replicas)
      * 4.9.9.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.OutOfSyncReplicas](#rqsrs-028clickhouseatomicinsertsfailuresoutofsyncreplicas)



## Introduction

This software requirements specification covers requirements related to [ClickHouse] 
transaction support.

## Related Resources

* https://github.com/ClickHouse/ClickHouse/issues/22086
* https://github.com/ClickHouse/ClickHouse/pull/24258
* https://docs.google.com/presentation/d/17EOqJ3lAnwGDVhFLTmKHB6BXnnE-xLyd/edit#slide=id.p1

## Terminology

### SRS

Software Requirements Specification

### Atomic Inserts

Insert that either completely succeeds or fails in the target table and its any dependent tables.

## Requirements

### RQ.SRS-028.ClickHouse.AtomicInserts
version: 1.0

[ClickHouse] SHALL support [atomic inserts].

### Insert Settings

#### RQ.SRS-028.ClickHouse.AtomicInserts.InsertSettings
version: 1.0 priority: 1.0

[ClickHouse] SHALL support all `INSERT` settings with atomic inserts.

The settings include the following:

*  `max_insert_block_size` – split insert into chunks
*  `min_insert_block_size_rows` – merge input into bigger chunks based on rows
*  `min_insert_block_size_bytes` – merge input into bigger chunks based on bytes
*  `input_format_parallel_parsing` – splits text input into chunks
*  `max_insert_threads` – number of threads to use during insert

### Blocks And Partitions

#### RQ.SRS-028.ClickHouse.AtomicInserts.BlocksAndPartitions
version: 1.0 priority: 1.0

[ClickHouse] SHALL support [atomic inserts] for the following cases:

* single block, single partition
* single block, multiple partitions
* multiple blocks, single partition
* multiple blocks, multiple partitions 

### Supported Table Engines

#### Merge Tree

##### RQ.SRS-028.ClickHouse.AtomicInserts.SupportedTableEngines.MergeTree
version: 1.0

[ClickHouse] SHALL support [atomic inserts] for all MergeTree table engines and their variants:

* MergeTree
* SummingMergeTree
* ReplacingMergeTree
* AggregatingMergeTree
* CollapsingMergeTree
* VersionedCollapsingMergeTree
* GraphiteMergeTree

#### Replicated Merge Tree

##### RQ.SRS-028.ClickHouse.AtomicInserts.SupportedTableEngines.ReplicatedMergeTree
version: 1.0

[ClickHouse] SHALL support [atomic inserts] for all ReplicatedMergeTree table engines and their variants:

* ReplicatedMergeTree
* ReplicatedSummingMergeTree
* ReplicatedReplacingMergeTree
* ReplicatedAggregatingMergeTree
* ReplicatedCollapsingMergeTree
* ReplicatedVersionedCollapsingMergeTree
* ReplicatedGraphiteMergeTree

### Dependent Tables

#### RQ.SRS-028.ClickHouse.AtomicInserts.DependentTables
version: 1.0 priority: 1.0

[ClickHouse] SHALL support [atomic inserts] when the following dependent tables are present: 

* one or more normal views
* single or cascading materialized view
* single or cascading window view
* one or more live views
* materialized with normal view
* materialized with live view
* materialized with window view
* window with materialized view
* window with normal view
* window with live view

### Distributed Table

#### RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable
version: 1.0 priority: 2.0

[ClickHouse] SHALL support [atomic inserts] into distributed table
when `insert_distributed_sync` setting is enabled.

#### RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.ShardUnavailable
version: 1.0 priority: 2.0

[ClickHouse] SHALL abort [atomic inserts] if even one shard was not available.

#### RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.ReplicaUnavailable
version: 1.0, priority: 2.0

[ClickHouse] SHALL abort [atomic inserts] if even one replica was not available.

#### RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.KeeperReadOnly
version: 1.0 priority: 2.0

[ClickHouse] SHALL abort [atomic inserts] if ZooKeeper or Clickhouse Keeper has placed a table into 
a "read only" mode.

### Multiple Tables

#### RQ.SRS-028.ClickHouse.AtomicInserts.MultipleTables
version: 1.0 priority: 3.0

[ClickHouse] SHALL support [atomic inserts] into multiple tables as a single atomic transaction.

```sql
BEGIN TRANSACTION
INSERT INTO <table.a> ...
INSERT INTO <table.b> ...
...
COMMIT TRANSACTION
```

The insert into multiple tables SHALL only succeed if [atomic inserts] can succeed in all the tables.

### Data Duplication

#### RQ.SRS-028.ClickHouse.AtomicInserts.DataDuplication
version: 1.0 priority: 3.0

[ClickHouse] SHALL not allow data duplication when:

* user retries failed inserts
* presence of collisions in message bus (e.g. Kafka re-balances)

### Failure Modes

##### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.OneOrMoreParts
version: 1.0 priority: 3.0

[ClickHouse] SHALL support [atomic inserts] in presence of fails to insert our or more parts
into target table or any of its dependent tables.

#### Syntax Error

##### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.SyntaxError
version: 1.0

[ClickHouse] SHALL support [atomic inserts] in presence of a syntax error in the query.

#### Mismatched Table Structure

##### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.MismatchedTableStructure
version: 1.0

[ClickHouse] SHALL support [atomic inserts] in presence failure to insert due to
mismatch in table structure that occures in the target table or one or its dependent tables.

Examples:

* different column data type
* missing columns

#### Circular Dependent Tables

##### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.CircularDependentTables
version: 1.0

[ClickHouse] SHALL support [atomic inserts] in presence of circular dependent tables.

#### Emulated Error

##### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.EmulatedUsingThrowIf
version: 1.0

[ClickHouse] SHALL support [atomic inserts] in presence of an emulated failure 
using [throwif] on a particular partition.

#### Disk Corruption

##### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.DiskCorruption
version: 1.0

[ClickHouse] SHALL support [atomic inserts] in presence of disk critically corrupted and cannot receive all the data.

#### Slow Disk

###### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.SlowDisk
version: 1.0

[ClickHouse] SHALL support [atomic inserts] in presence of one or more slow disks.

#### User Rights

##### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.UserRights
version: 1.0

[ClickHouse] SHALL support [atomic inserts] in presence of a query issues by a user that does not have
enough rights either on the target table or one of its dependent tables.

#### Out of Sync Replicas

##### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.OutOfSyncReplicas
version: 1.0

[ClickHouse] SHALL support [atomic inserts] in presence of issues with data synchronicity on replicas.

[SRS]: #srs
[atomic inserts]: #attomic-inserts
[throwif]: https://clickhouse.com/docs/en/sql-reference/functions/other-functions/#throwifx-custom-message
[ClickHouse]: https://clickhouse.com

