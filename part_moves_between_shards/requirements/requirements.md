# SRS027 ClickHouse Part Moves Between Shards
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Requirements](#requirements)
  * 2.1 [General](#general)
    * 2.1.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards](#rqsrs-027clickhousepartmovesbetweenshards)
  * 2.2 [Move Part](#move-part)
    * 2.2.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.OnePartMove](#rqsrs-027clickhousepartmovesbetweenshardsonepartmove)
  * 2.3 [Return Part](#return-part)
    * 2.3.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.OnePartReturn](#rqsrs-027clickhousepartmovesbetweenshardsonepartreturn)
  * 2.4 [Zero Part](#zero-part)
    * 2.4.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ZeroPart](#rqsrs-027clickhousepartmovesbetweenshardszeropart)
  * 2.5 [Move Part With Incorrect Name](#move-part-with-incorrect-name)
    * 2.5.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.MovePartWithIncorrectName](#rqsrs-027clickhousepartmovesbetweenshardsmovepartwithincorrectname)
  * 2.6 [Same Shard](#same-shard)
    * 2.6.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SameShard](#rqsrs-027clickhousepartmovesbetweenshardssameshard)
  * 2.7 [Different Local Structure](#different-local-structure)
    * 2.7.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DifferentLocalStructure](#rqsrs-027clickhousepartmovesbetweenshardsdifferentlocalstructure)
  * 2.8 [Different Partition Key](#different-partition-key)
    * 2.8.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DifferentPartitionKey](#rqsrs-027clickhousepartmovesbetweenshardsdifferentpartitionkey)
  * 2.9 [Part Not Exist](#part-not-exist)
    * 2.9.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.PartNotExist](#rqsrs-027clickhousepartmovesbetweenshardspartnotexist)
  * 2.10 [Supported Table Engines](#supported-table-engines)
    * 2.10.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SupportedTableEngines](#rqsrs-027clickhousepartmovesbetweenshardssupportedtableengines)
  * 2.11 [Not Supported Table Engines](#not-supported-table-engines)
    * 2.11.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.NotSupportedTableEngines](#rqsrs-027clickhousepartmovesbetweenshardsnotsupportedtableengines)
  * 2.12 [Concurrent Part Moves](#concurrent-part-moves)
    * 2.12.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves](#rqsrs-027clickhousepartmovesbetweenshardsconcurrentpartmoves)
    * 2.12.2 [Same Part](#same-part)
      * 2.12.2.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.SamePart](#rqsrs-027clickhousepartmovesbetweenshardsconcurrentpartmovessamepart)
    * 2.12.3 [Insert Data](#insert-data)
      * 2.12.3.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.InsertDataOnSourceNodeSamePartition](#rqsrs-027clickhousepartmovesbetweenshardsconcurrentpartmovesinsertdataonsourcenodesamepartition)
      * 2.12.3.2 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.InsertDataOnDestinationNodeSamePartition](#rqsrs-027clickhousepartmovesbetweenshardsconcurrentpartmovesinsertdataondestinationnodesamepartition)
  * 2.13 [Data Deduplication](#data-deduplication)
    * 2.13.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication](#rqsrs-027clickhousepartmovesbetweenshardsdatadeduplication)
    * 2.13.2 [Destination Replica Stopped](#destination-replica-stopped)
      * 2.13.2.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DestinationReplicaStopped](#rqsrs-027clickhousepartmovesbetweenshardsdatadeduplicationdestinationreplicastopped)
    * 2.13.3 [Source Replica Stopped](#source-replica-stopped)
      * 2.13.3.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.SourceReplicaStopped](#rqsrs-027clickhousepartmovesbetweenshardsdatadeduplicationsourcereplicastopped)
    * 2.13.4 [Distributed Table Data](#distributed-table-data)
      * 2.13.4.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DistributedTable](#rqsrs-027clickhousepartmovesbetweenshardsdatadeduplicationdistributedtable)
      * 2.13.4.2 [Replica Stopped](#replica-stopped)
        * 2.13.4.2.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DistributedTable.ReplicaStopped](#rqsrs-027clickhousepartmovesbetweenshardsdatadeduplicationdistributedtablereplicastopped)
  * 2.14 [System Table](#system-table)
    * 2.14.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable](#rqsrs-027clickhousepartmovesbetweenshardssystemtable)
    * 2.14.2 [Sync Fail Source](#sync-fail-source)
      * 2.14.2.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable.SyncFailSource](#rqsrs-027clickhousepartmovesbetweenshardssystemtablesyncfailsource)
    * 2.14.3 [Sync Fail Destination](#sync-fail-destination)
      * 2.14.3.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable.SyncFailDestination](#rqsrs-027clickhousepartmovesbetweenshardssystemtablesyncfaildestination)
* 3 [References](#references)



## Introduction

[ClickHouse] feature to allow part uuid pinning and movement between shards.

## Requirements

### General

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards
version: 1.0

[ClickHouse] SHALL support moving parts between shards using the following command syntax:

```sql
ALTER TABLE <table_name> MOVE PART <part_name> TO SHARD 'ZooKeeper path'
```

### Move Part

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.OnePartMove
version: 1.0

[ClickHouse] SHALL support a single part movement from one shard to another when
`MOVE PART TO SHARD` query is used.

### Return Part

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.OnePartReturn
version: 1.0

[ClickHouse] SHALL support a single part movement from one shard to another and back when `MOVE PART TO SHARD` query is used.

### Zero Part

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ZeroPart
version: 1.0

[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries
to move a part with an empty name.

### Move Part With Incorrect Name

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.MovePartWithIncorrectName
version: 1.0

[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries
to move a part with an incorrect name.

### Same Shard

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SameShard
version: 1.0

[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries 
to move a part to the same shard where it is currently present.

### Different Local Structure

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DifferentLocalStructure
version: 1.0

[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries to move a part to the shard
which has different local column structures.

For example,

* where column name was changed with `ALTER RENAME COLUMN` query

### Different Partition Key

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DifferentPartitionKey
version: 1.0

[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries to move a part to the shard
which differs in partition key expression.

### Part Not Exist

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.PartNotExist
version: 1.0

[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries to move a part 
that doesn't exist.

### Supported Table Engines

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SupportedTableEngines
version: 1.0

[ClickHouse] SHALL support using the `MOVE PART TO SHARD`  statement on 
sharded tables for all ReplicatedMergeTree table engines:

* ReplicatedMergeTree
* ReplicatedSummingMergeTree
* ReplicatedReplacingMergeTree
* ReplicatedAggregatingMergeTree
* ReplicatedCollapsingMergeTree
* ReplicatedVersionedCollapsingMergeTree
* ReplicatedGraphiteMergeTree

### Not Supported Table Engines

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.NotSupportedTableEngines
version: 1.0

[ClickHouse] SHALL not support using the `MOVE PART TO SHARD` statement on 
sharded tables for non replicated MergeTree table engines.

### Concurrent Part Moves

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL perform correctly when
there are multiple concurrent `MOVE PART TO SHARD` operations.

#### Same Part

##### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.SamePart
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL perform correctly when there are
multiple concurrent `MOVE PART TO SHARD` operations targeting the same part.

#### Insert Data

##### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.InsertDataOnSourceNodeSamePartition
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL perform correctly when it is concurrent with
`INSERT` statement that inserts data on the source node in the same partition as the one being moved.

##### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.InsertDataOnDestinationNodeSamePartition
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL perform correctly when it is concurrent with
`INSERT` statement on the same destination node that writes data into the same partition as the one being moved.

### Data Deduplication

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL not duplicate data when parts are moved.

#### Destination Replica Stopped

##### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DestinationReplicaStopped
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL allow moving part from a shard when even one
of its destination replicas is down and SHALL finish part move query when replicas return.

#### Source Replica Stopped

##### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.SourceReplicaStopped
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL allow moving part from a shard when even one
of its source replicas is down and SHALL finish part move query when replicas return.

#### Distributed Table Data

##### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DistributedTable
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL not cause data duplication when 
`MOVE PART TO SHARD` query is used multiple times when sharded table is accessed using
`Distributed` table engine.

##### Replica Stopped

###### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DistributedTable.ReplicaStopped
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL not cause data duplication when 
`MOVE PART TO SHARD` query is used multiple times and some replica on one shard 
starts and stops when sharded table is accessed using `Distributed` table engine.


### System Table

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable
version: 1.0

[ClickHouse] SHALL write information about `MOVE PART TO SHARD` queries to special
system table `system.part_moves_between_shards`. 

The table SHALL have the following column names and types:

    `database` String - database`s name
    `table` String - table`s name
    `task_name` String - task`s name
    `task_uuid` UUID - task`s UUID
    `create_time` DateTime - time of `PART MOVE` query creation
    `part_name` String - part`s name
    `part_uuid` UUID - part`s UUID
    `to_shard` String - destination shard path in ZooKeeper
    `dst_part_name` String - new part`s name on destination shard
    `update_time` DateTime - time of update
    `state` String - current state of task
    `rollback` UInt8 - rollback state
    `num_tries` UInt32 - number of tries
    `last_exception` String - description of the last exception


#### Sync Fail Source

##### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable.SyncFailSource
version: 1.0

[ClickHouse] SHALL change value in the `state` column to `SYNC_SOURCE` and show information
about exception in `last_exception` column of system table `system.part_moves_between_shards` 
when one of the source replicas is down and `MOVE PART TO SHARD` query is in progress.

#### Sync Fail Destination

##### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable.SyncFailDestination
version: 1.0

[ClickHouse] SHALL change value in `state` column to `SYNC_DESTINATION` and show information
about exception in `last_exception` column of system table `system.part_moves_between_shards` 
when one of the destination replicas is down and `MOVE PART TO SHARD` query is in progress.

## References

* **ClickHouse:** https://clickhouse.com

[SRS]: #srs
[ClickHouse]: https://clickhouse.com


