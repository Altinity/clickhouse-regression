
## Feature
https://github.com/Altinity/ClickHouse/pull/939

## High-level Requirements

1. Export PARTITION only

What can happen to PARTITION?

* New parts could be added or be in flight to that partition
* Active merges on parts inside partition

* PARTITION can have many parts
  * First lock the PARTITION  
  * You take snapshot of the current parts inside the partition
    * Then for each part in the snapshot we lock each parts
  * Export manifest file is created (should be protected by checksum)
    * /**
     * JSON manifest for exporting a set of parts to object storage.
     * Layout on disk (pretty-printed JSON):
     * {
     *   "transaction_id": "<id>", # we make transactional write to S3 (there is no multi-object transactions supported by S3), id is a snowflake id
     *   "partition_id": "<partition_id>", # this the partition id of the partition being exported
     *   "destination": "<database>.<table>", # an abstraction layer for physical S3 hive partition writes
     *   "completed": <true/false>, # when it is false there is more work, when it is true then partition is locked from re-export
     *   "parts": [ {"part_name": "name", "remote_path": "path-or-empty"}, ... ] # remote_path is the flag that indicates the successful export to S3 for this specific part
     * }
    */
  * It is an ASYNC command
  * Observability:
    * Two tables: system. 
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
