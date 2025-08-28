
## Feature
https://github.com/Altinity/ClickHouse/pull/939

## High-level objects

Table
   Source (MergeTree) 
      Schema
         Partition expression
   Destination (Engine=AzureBlobStorage, Engine=S3, Engine=S3 (gcp uses other arguments))
      Schema
         Partition expression
         Must use hive partitioning
   Disks
       one
       multiple
       different types (cached, non-cached, local, s3, s3 cached, etc)
PARTITIONS
   Parts
      compact
      wide
      patch parts
      mutated
      not-yet mutated
   Operation on parts:
      merges
      mutations
      etc.

1. Doing crazy things while we attempt to do EXPORT (something might be stopped not alowed or export not started)
2. Doing crazy things while EXPORT is in progress (somethings might not be allowed)
3. Doing crazy things when EXPORT is done (normal operation is resumed)

## High-level Requirements
1. When export is in progress we what operations on that partition or parts are allowed or not allowed?
   Can we freeze a partition while export is in progress? etc.
   For example, export in progress, mutation is scheduled but parts are locked by export, but we restart a server.
   We need to check that part lock is actually persistent across clickhouse restarts.
   General: doing crazy things while export is in process.

1. Export PARTITION only

What can happen to PARTITION?

* New parts could be added or be in flight to that partition
* Active merges on parts inside partition

* We will need a complete list of operations on a part level
  * merge, mutate, move part, frozen partitions or parts, light weight mutations, light weight deletes
  * We need to worry about proper handling of "patched parts" (Biggy!)
  * On-the-fly mutations (Biggy!)
  * Compact vs wide parts (Biggy!)

* Starvation where we have a server with large number of inserts, queries, mutations while it tries
  to do an export. 

* What happens when a part has old schema structure and ALTER ADD COLUMN etc has not been applied
  This will cause new parts in the table have a different structure than the older parts
  The schemas of source and destination must match. We must test for this.
  We must check all different mutations on the table that has not yet been materialized on all the parts
  that belong to a given partition that we try to export. (Biggy!)
  
* PARTITION can have many parts
  * First lock the PARTITION  
  * You take snapshot of the current parts inside the partition
    * Then for each part in the snapshot we lock each parts
  * Export manifest file is created (should be protected by checksum)
    *```/**
     * JSON manifest for exporting a set of parts to object storage.
     * Layout on disk (pretty-printed JSON):
     * {
     *   "transaction_id": "<id>", # we make transactional write to S3 (there is no multi-object transactions supported by S3), id is a snowflake id
     *   "partition_id": "<partition_id>", # this the partition id of the partition being exported
     *   "destination": "<database>.<table>", # an abstraction layer for physical S3 hive partition writes
     *   "completed": <true/false>, # when it is false there is more work, when it is true then partition is locked from re-export
     *   "parts": [ {"part_name": "name", "remote_path": "path-or-empty"}, ... ] # remote_path is the flag that indicates the successful export to S3 for this specific part
     * }
    */```
  * It is an ASYNC command
  * Observability:
    * Two tables: system.part_log (info about what is happening to specific part), system.export (similar to system.moves)
      the entries exist only while the operation is in progress.
      ```
      ColumnsDescription StorageSystemExports::getColumnsDescription()
      {
          return ColumnsDescription
          {
              {"source_database", std::make_shared<DataTypeString>(), "Name of the source database."},
              {"source_table", std::make_shared<DataTypeString>(), "Name of the source table."},
              {"destination_database", std::make_shared<DataTypeString>(), "Name of the destination database."},
              {"destination_table", std::make_shared<DataTypeString>(), "Name of the destination table."},
              {"elapsed", std::make_shared<DataTypeFloat64>(), "Time elapsed (in seconds) since data part movement started."},
              {"destination_path", std::make_shared<DataTypeString>(), "Path to the destination file in the destination storage."},
              {"part_name", std::make_shared<DataTypeString>(), "Name of the data part being moved."},
              {"thread_id", std::make_shared<DataTypeUInt64>(), "Identifier of a thread performing the movement."},
          };
      }
      ```
  
  * On S3 /partition/id/<{snowflake_id}.parquet>
  * Completed flag is set to true only when commit file on S3 is successfully created
  * With disaster recovery, on flight failures 
  * If commit file is not confirmed it should be OK, because completed flag is not set (We test by monifying export manifest and delete commit file on S3)
  * Once remote_path is set there is nothing that export partition will do for that file or care about it
  * There is no way to do a re-export for any reason unless physically deleting the export manifest file
  * The result of export is a Parquet file on S3 and a commit file.
  * Right now there could be duplicate data on S3 if sucessfull write gets lost then new Parquet file is created but the commit file
    should only reflect the new file.
  * S3 will contain a commit file   
[source table] -> [destination table] -> Physical S3
    
  * The export manifest is created per exported PARTITION
  * We are OK we multiple parallel partitions being exported at the same time as long as these are different partitions
  * Check PARTITION expression is compatible with Hive partitions
    * We need to check Hive partition writes and what is compatible
  * The export manifest is permanent and is used to check if PARTITION has been previously exported
  * The same PARTITION can't be exported twice
  * Check if we only take a snapshot of active parts
  * Lock the currently exported parts only
  * Run logical AI check on the code src/Storages/StorageMergeTree.cpp

  * Merges and Mutations and inserts can still go into the same partition



* Partitions are immutable while they are moved
* Partition expression is immutable
* Watermarks are partition aligned
* MergeTree partition expression must be hive partition compatible (simple)
  Is PARTITION BY (eventDate, retention) hive compatible?
* Ordering?
  https://arrow.apache.org/docs/python/generated/pyarrow.parquet.SortingColumn.html
* Data type mapping ClickHouse -> Parquet -> Ice (we need test for this)
  * ALTER EXPORT or manual write of data to Parquet
* Partition pruning should work on exported parts to Ice

* attached disks (tiered storage configurations)
  * MergeTree table can have its data be spread out between multiple disks including S3
  * We need to check where export manifest is being stored because the part can potentially live on a different disk
  * We need to check part being moved from one disk to another while export is attempted

* Note: the export manifest on disk is pretty much MergeTree only feature. Future ReplicatedMergeTree will definitly not have it.
  This is similar to mutuations that are implemented on as files for MergeTree

* Soft failures must be covered (temporary connection loss to S3), (packets dropped), (network delays)
  S3 restarts, etc. but ClickHouse server is up

* Hard fails, SIGSEGV, SIGTERM, SIGSTOP, disk full, out of RAM (the actual export is streaming but still we need to check what happens when RAM limit is hit)
* Check resource utilization
  Multiple exports at the same time (what load to they add on a system)

* We must test when settings select different Partquet writer/reader implementation (Biggy!) 
* We need to look at current mutation tests

* What is the error recovery process.
  For some reason, you fail to create Parquet file in the middle, etc.

 
