# SRS-045 ClickHouse Iceberg Support
# Software Requirements Specification

## Table of Contents


## Introduction

This Software Requirements Specification (SRS) defines the requirements for ClickHouse's read-only integration with existing Apache Iceberg tables through three different interfaces: Iceberg Database Engine, Iceberg Table Engine, and Iceberg Table Function, supporting tables stored in Amazon S3, Azure, HDFS, and local filesystem storage.


## Iceberg Database Engine

The Iceberg Database Engine is a new database engine that integrates ClickHouse with Iceberg REST Catalog, allowing direct access to Iceberg tables through the catalog interface. Related pull request: [PR #71542](https://github.com/ClickHouse/ClickHouse/pull/71542).

### Create statement

#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.CreateStatement
version: 1.0  

[ClickHouse] SHALL support to create a database with Iceberg (DataLakeCatalog) engine.

Example:
```sql
CREATE DATABASE datalake
ENGINE = Iceberg('http://rest:8181/v1', 'minio', 'minio123')
SETTINGS catalog_type = 'rest', storage_endpoint = 'http://minio:9000/warehouse', warehouse = 'iceberg' 
```
#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.CreateStatement.Arguments
version: 1.0  

[ClickHouse] SHALL support the following arguments for the `CREATE DATABASE` statement:

- rest_catalog_url
- s3_access_key_id
- s3_secret_access_key

### Show statement

#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.Show.ShowDatabases
version: 1.0  

[ClickHouse] SHALL reflect Iceberg databases in the `SHOW DATABASES` statement.

Example:
```sql
SHOW DATABASES;
```
Output:
```
INFORMATION_SCHEMA
datalake
default
information_schema
system
```

#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.Show.ShowCreateDatabase
version: 1.0  

[ClickHouse] SHALL support the `SHOW CREATE DATABASE` statement for iceberg databases.

Example:
```sql
SHOW CREATE DATABASE datalake;
```
Output:
```
CREATE DATABASE datalake\nENGINE = DataLakeCatalog(\'http://ice-rest-catalog:5000\', \'admin\', \'password\')\nSETTINGS catalog_type = \'rest\', storage_endpoint = \'http://minio:9000/warehouse\', warehouse = \'s3://bucket1/\'
```
#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.Show.ShowTables
version: 1.0  

[ClickHouse] SHALL support the `SHOW TABLES` statement for iceberg databases.

Example:
```sql
SHOW TABLES FROM datalake;
```
Output:
```
iceberg.name
```
`iceberg` - is the name of namespace
`name` - is the name of table

#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.Show.ShowCreateTable
version: 1.0  

[ClickHouse] SHALL support the `SHOW CREATE TABLE` statement for tables from `Iceberg` database.

Example:
```sql
SHOW CREATE TABLE datalake.`iceberg.name`;
```
Output:

```
CREATE TABLE datalake.`iceberg.name`\n(\n    `name` Nullable(String),\n    `double` Nullable(Float64),\n    `integer` Nullable(Int64)\n)\nENGINE = Iceberg(\'http://minio:9000/warehouse/data/\', \'admin\', \'[HIDDEN]\')
```

#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.Show.ShowColumns
version: 1.0  

[ClickHouse] SHALL support the `SHOW COLUMNS` statement for tables from `Iceberg` database.

Example:
```sql
SHOW COLUMNS FROM datalake.`iceberg.name`;
```
Output:
```
   ┌─field───┬─type──────────────┬─null─┬─key─┬─default─┬─extra─┐
1. │ double  │ Nullable(Float64) │ YES  │     │ ᴺᵁᴸᴸ    │       │
2. │ integer │ Nullable(Int64)   │ YES  │     │ ᴺᵁᴸᴸ    │       │
3. │ name    │ Nullable(String)  │ YES  │     │ ᴺᵁᴸᴸ    │       │
   └─────────┴───────────────────┴──────┴─────┴─────────┴───────┘
```


### Schema Evolution

#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.SchemaEvolution
version: 1.0  

[ClickHouse] SHALL support reading iceberg tables, the schema of which has changed over time. 

Possible schema evolution operations:
- Add column
- Remove column
- Rename column
- Move column
    - to first position
    - before some column
    - after some column
- Rename column
- Union by name
- Type casting for simple types 
    - int -> long
    - float -> double
    - decimal(P,S) -> decimal(P,S) where P' > P

- Change column nullability (required to nullable)
    
Currently, it is not possible to change nested structures or the types of elements within arrays and maps.


### Partition evolution

#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.PartitionEvolution
version: 1.0  

[ClickHouse] SHALL support reading iceberg tables, the partition spec of which has changed over time.

Possible partition evolution operations:
- Add partition field
- Remove partition field


### Pruning

#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.Pruning.IcebergPartitionPruning
version: 1.0  

[ClickHouse] SHALL support partition pruning for tables from `Iceberg` database.

Example:
```sql
SELECT * FROM datalake.`iceberg.name` 
SETTINGS use_iceberg_partition_pruning = 1
WHERE integer > 100 AND integer < 200;
```

#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.Pruning.IcebergPartitionPruning.ProfileEvents
version: 1.0  

[ClickHouse] SHALL reflect partition pruning in `system.query_log` table in ProfileEvents['IcebergPartitionPrunedFiles'] by displaying the number of files that were pruned during query execution.

Example:
```sql
SELECT ProfileEvents['IcebergPartitionPrunedFiles'] FROM system.query_log WHERE log_comment = '...' and AND type = 'QueryFinish'
```


#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.Pruning.MinMax
version: 1.0  

[ClickHouse] SHALL support partition pruning based on lower_bound and upper_bound values for columns [PR #71542](https://github.com/ClickHouse/ClickHouse/pull/78242). Pruning is enabled by `use_iceberg_partition_pruning` setting.

Example:
```sql
SELECT * 
FROM datalake.`iceberg.name` 
SETTINGS use_iceberg_partition_pruning = 1
WHERE integer > 100 AND integer < 200;
```

#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.Pruning.MinMax.ProfileEvents
version: 1.0  

[ClickHouse] SHALL reflect partition pruning in `system.query_log` table in ProfileEvents['IcebergMinMaxIndexPrunedFiles'] by displaying the number of files that were pruned during query execution.

Example:
```sql
SELECT ProfileEvents['IcebergMinMaxIndexPrunedFiles'] FROM system.query_log WHERE log_comment = '...' and AND type = 'QueryFinish'
```

#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.Pruning.ParquetFilterPushDown
version: 1.0  

[ClickHouse] SHALL support skipping whole row groups in Parquet files when reading tables from `Iceberg` database based on WHERE/PREWHERE expressions and min/max statistics in the Parquet metadata. This feature is controlled by the `input_format_parquet_filter_push_down` setting, which is enabled by default.

Example:
```sql
SELECT * FROM datalake.`iceberg.name`
WHERE integer > 100 AND integer < 200
SETTINGS input_format_parquet_filter_push_down = 1;
```

#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.Pruning.ParquetBloomFilter
version: 1.0  

[ClickHouse] SHALL support utilizing Bloom filters in Parquet files when reading tables from `Iceberg` database to read data more efficiently. This feature is controlled by the `input_format_parquet_bloom_filter_push_down` setting.

Example:
```sql
SELECT * FROM datalake.`iceberg.name`
WHERE string_column = 'value'
SETTINGS input_format_parquet_bloom_filter_push_down = 1;
```




### Caching

#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.MetadataCache
version: 1.0  

[ClickHouse] SHALL support metadata cache storing the information of manifest files, manifest list and metadata json for tables from `Iceberg` database. The cache is stored in memory. This feature is controlled by setting `use_iceberg_metadata_files_cache`, which is enabled by default.

#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.MetadataCache.ProfileEvents
version: 1.0  

[ClickHouse] SHALL track metadata cache performance metrics in `system.query_log` table in ProfileEvents:

- `IcebergMetadataFilesCacheHits` - Number of times iceberg metadata files have been found in the cache
- `IcebergMetadataFilesCacheMisses` - Number of times iceberg metadata files have not been found in the cache and had to be read from (remote) disk
- `IcebergMetadataFilesCacheWeightLost` - Approximate number of bytes evicted from the iceberg metadata cache

Example:
```sql
SELECT 
    ProfileEvents['IcebergMetadataFilesCacheHits'] as cache_hits,
    ProfileEvents['IcebergMetadataFilesCacheMisses'] as cache_misses,
    ProfileEvents['IcebergMetadataFilesCacheWeightLost'] as cache_evicted_bytes
FROM system.query_log 
WHERE type = 'QueryFinish' AND log_comment = '...';
```

#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.ParquetMetadataCache
version: 1.0  

[ClickHouse] SHALL support caching the whole metadata object when querying Parquet files stored in any type of remote object storage by using the `input_format_parquet_use_metadata_cache` query setting (disabled by default). The metadata caching SHALL allow faster query execution by avoiding the need to read the Parquet file's metadata each time a query is executed.


#### RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.ParquetMetadataCache.ProfileEvents
version: 1.0  

[ClickHouse] SHALL track parquet metadata cache performance metrics in `system.query_log` table in ProfileEvents:
- `ParquetMetaDataCacheHits` - Number of times parquet metadata has been found in the cache


Example:
```sql
SELECT * FROM datalake.`iceberg.name`
SETTINGS input_format_parquet_use_metadata_cache = 1;
```



