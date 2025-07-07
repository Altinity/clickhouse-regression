# SRS-045 Hive Partitioning
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Requirements](#requirements)
    * 2.1 [Generic Behavior](#generic-behavior)
        * 2.1.1 [RQ.HivePartitioning.Support  ](#rqhivepartitioningsupport-)
        * 2.1.2 [RQ.HivePartitioning.EnableSetting](#rqhivepartitioningenablesetting)
        * 2.1.3 [RQ.HivePartitioning.Generic.Pruning](#rqhivepartitioninggenericpruning)
        * 2.1.4 [RQ.HivePartitioning.Generic.Performance](#rqhivepartitioninggenericperformance)
    * 2.2 [Virtual Columns](#virtual-columns)
        * 2.2.1 [RQ.HivePartitioning.VirtualColumns  ](#rqhivepartitioningvirtualcolumns-)
        * 2.2.2 [RQ.HivePartitioning.VirtualColumns.ReadOnly  ](#rqhivepartitioningvirtualcolumnsreadonly-)
        * 2.2.3 [RQ.HivePartitioning.VirtualColumns.Appearance](#rqhivepartitioningvirtualcolumnsappearance)
        * 2.2.4 [RQ.HivePartitioning.VirtualColumns.Accessibility](#rqhivepartitioningvirtualcolumnsaccessibility)
            * 2.2.4.1 [RQ.HivePartitioning.VirtualColumns.InvalidPath  ](#rqhivepartitioningvirtualcolumnsinvalidpath-)
        * 2.2.5 [RQ.HivePartitioning.VirtualColumns.NameConflict  ](#rqhivepartitioningvirtualcolumnsnameconflict-)
        * 2.2.6 [RQ.HivePartitioning.VirtualColumns.HiveDisabled  ](#rqhivepartitioningvirtualcolumnshivedisabled-)
        * 2.2.7 [RQ.HivePartitioning.VirtualColumns.NonExistingKey](#rqhivepartitioningvirtualcolumnsnonexistingkey)
    * 2.3 [Hive Partition Types Value](#hive-partition-types-value)
        * 2.3.1 [RQ.HivePartitioning.HivePartitionValue  ](#rqhivepartitioninghivepartitionvalue-)
        * 2.3.2 [RQ.HivePartitioning.HivePartitionValue.EmptyValue  ](#rqhivepartitioninghivepartitionvalueemptyvalue-)
    * 2.4 [Wildcards](#wildcards)
        * 2.4.1 [RQ.HivePartitioning.Wildcards  ](#rqhivepartitioningwildcards-)
        * 2.4.2 [RQ.HivePartitioning.Wildcards.SingleStar  ](#rqhivepartitioningwildcardssinglestar-)
        * 2.4.3 [RQ.HivePartitioning.Wildcards.DoubleStar  ](#rqhivepartitioningwildcardsdoublestar-)
        * 2.4.4 [RQ.HivePartitioning.Wildcards.QuestionMark  ](#rqhivepartitioningwildcardsquestionmark-)
        * 2.4.5 [RQ.HivePartitioning.Wildcards.List  ](#rqhivepartitioningwildcardslist-)
        * 2.4.6 [RQ.HivePartitioning.Wildcards.WrongList  ](#rqhivepartitioningwildcardswronglist-)
        * 2.4.7 [RQ.HivePartitioning.Wildcards.Range  ](#rqhivepartitioningwildcardsrange-)
        * 2.4.8 [RQ.HivePartitioning.Wildcards.WrongRange  ](#rqhivepartitioningwildcardswrongrange-)
        * 2.4.9 [RQ.HivePartitioning.Wildcards.Escaping  ](#rqhivepartitioningwildcardsescaping-)
    * 2.5 [Supported Table Functions](#supported-table-functions)
        * 2.5.1 [RQ.HivePartitioning.TableFunction.S3  ](#rqhivepartitioningtablefunctions3-)
        * 2.5.2 [RQ.HivePartitioning.TableFunction.S3Cluster  ](#rqhivepartitioningtablefunctions3cluster-)
        * 2.5.3 [RQ.HivePartitioning.TableFunction.HDFS  ](#rqhivepartitioningtablefunctionhdfs-)
    * 2.6 [Supported Table Engines](#supported-table-engines)
        * 2.6.1 [S3 Table Engine](#s3-table-engine)
            * 2.6.1.1 [RQ.HivePartitioning.TableEngines.S3  ](#rqhivepartitioningtableenginess3-)
        * 2.6.2 [HDFS Table Engine](#hdfs-table-engine)
            * 2.6.2.1 [RQ.HivePartitioning.TableEngines.HDFS](#rqhivepartitioningtableengineshdfs)
        * 2.6.3 [Hive Table Engine](#hive-table-engine)
            * 2.6.3.1 [RQ.HivePartitioning.TableEngines.Hive](#rqhivepartitioningtableengineshive)
    * 2.7 [Hive Partition Writes](#hive-partition-writes)
        * 2.7.1 [S3 Table Engine Writes](#s3-table-engine-writes)
            * 2.7.1.1 [RQ.HivePartitioning.Writes.S3  ](#rqhivepartitioningwritess3-)
            * 2.7.1.2 [Partition Strategy Parameter](#partition-strategy-parameter)
                * 2.7.1.2.1 [RQ.HivePartitioning.Writes.PartitionStrategy](#rqhivepartitioningwritespartitionstrategy)
                * 2.7.1.2.2 [RQ.HivePartitioning.Writes.PartitionStrategyWrongArgument](#rqhivepartitioningwritespartitionstrategywrongargument)
            * 2.7.1.3 [Partition Columns In Data File Parameter](#partition-columns-in-data-file-parameter)
                * 2.7.1.3.1 [RQ.HivePartitioning.Writes.PartitionColumnsInDataFile](#rqhivepartitioningwritespartitioncolumnsindatafile)
                * 2.7.1.3.2 [RQ.HivePartitioning.Writes.PartitionColumnsInDataFileWithoutHivePartitionStrategy](#rqhivepartitioningwritespartitioncolumnsindatafilewithouthivepartitionstrategy)
                * 2.7.1.3.3 [RQ.HivePartitioning.Writes.PartitionColumnsInDataFileWrongArgiment](#rqhivepartitioningwritespartitioncolumnsindatafilewrongargiment)
            * 2.7.1.4 [Path Parameter](#path-parameter)
                * 2.7.1.4.1 [RQ.HivePartitioning.Writes.Path](#rqhivepartitioningwritespath)
            * 2.7.1.5 [RQ.HivePartitioning.Writes.InvalidPath](#rqhivepartitioningwritesinvalidpath)
            * 2.7.1.6 [Filename Parameter](#filename-parameter)
                * 2.7.1.6.1 [RQ.HivePartitioning.Writes.Filename  ](#rqhivepartitioningwritesfilename-)
                * 2.7.1.6.2 [RQ.HivePartitioning.Writes.FilenameWithoutHivePartitionStrategy ](#rqhivepartitioningwritesfilenamewithouthivepartitionstrategy-)
                * 2.7.1.6.3 [RQ.HivePartitioning.Writes.NotDefinedFilename ](#rqhivepartitioningwritesnotdefinedfilename-)
            * 2.7.1.7 [S3 Engine Parameters](#s3-engine-parameters)
                * 2.7.1.7.1 [RQ.HivePartitioning.Writes.S3EngineParameters  ](#rqhivepartitioningwritess3engineparameters-)
            * 2.7.1.8 [RQ.HivePartitioning.Writes.UseHivePartitions  ](#rqhivepartitioningwritesusehivepartitions-)
        * 2.7.2 [Writes By Partitions And Parts](#writes-by-partitions-and-parts)
            * 2.7.2.1 [RQ.HivePartitioning.Writes.PartitionsParts  ](#rqhivepartitioningwritespartitionsparts-)
        * 2.7.3 [Using Expressions In Partition By Clause](#using-expressions-in-partition-by-clause)
            * 2.7.3.1 [RQ.HivePartitioning.Writes.Expressions](#rqhivepartitioningwritesexpressions)
        * 2.7.4 [Inserting Into Existing File](#inserting-into-existing-file)
            * 2.7.4.1 [RQ.HivePartitioning.Writes.FileExist  ](#rqhivepartitioningwritesfileexist-)
        * 2.7.5 [Missing Partition By Column](#missing-partition-by-column)
            * 2.7.5.1 [RQ.HivePartitioning.Writes.MissingColumn](#rqhivepartitioningwritesmissingcolumn)
        * 2.7.6 [Using Default Value ](#using-default-value-)
            * 2.7.6.1 [RQ.HivePartitioning.Writes.DefaultValue  ](#rqhivepartitioningwritesdefaultvalue-)
        * 2.7.7 [Using Nullable Datatypes](#using-nullable-datatypes)
            * 2.7.7.1 [RQ.HivePartitioning.Writes.NullableDataType](#rqhivepartitioningwritesnullabledatatype)
        * 2.7.8 [Supported Data Types](#supported-data-types)
            * 2.7.8.1 [RQ.HivePartitioning.Writes.SupportedDataTypes  ](#rqhivepartitioningwritessupporteddatatypes-)
        * 2.7.9 [Unsupported Types](#unsupported-types)
            * 2.7.9.1 [RQ.HivePartitioning.Writes.DataTypesUnsupported](#rqhivepartitioningwritesdatatypesunsupported)
        * 2.7.10 [Using ReadOnly Bucket](#using-readonly-bucket)
            * 2.7.10.1 [RQ.HivePartitioning.Writes.ReadOnlyBucket](#rqhivepartitioningwritesreadonlybucket)
        * 2.7.11 [Non-Accessible Bucket](#non-accessible-bucket)
            * 2.7.11.1 [RQ.HivePartitioning.Writes.NonAccessibleBucket](#rqhivepartitioningwritesnonaccessiblebucket)
        * 2.7.12 [Parallel Inserts](#parallel-inserts)
            * 2.7.12.1 [RQ.HivePartitioning.Writes.ParallelInserts](#rqhivepartitioningwritesparallelinserts)
        * 2.7.13 [Failing Write](#failing-write)
            * 2.7.13.1 [RQ.HivePartitioning.Writes.WriteFail  ](#rqhivepartitioningwriteswritefail-)
        * 2.7.14 [Partition By Clause](#partition-by-clause)
            * 2.7.14.1 [RQ.HivePartitioning.Writes.PartitionBy](#rqhivepartitioningwritespartitionby)
            * 2.7.14.2 [RQ.HivePartitioning.Writes.PartitionKey](#rqhivepartitioningwritespartitionkey)



## Introduction

This document describes the requirements for the [ClickHouse] hive-style partitioning functionality. Hive-style partitioning refers to organizing files in a directory hierarchy where folder names encode column values (e.g. .../country=US/year=2021/file.parquet). [ClickHouse] provides functionality to read and write such partitioned data across various interfaces, including S3 and HDFS table functions and the Hive table engine. This allows users to query partitioned datasets efficiently by treating partition names as data columns and pruning unnecessary files. The following requirements describe the expected functionality and behavior for Hive-style partitioning support in [ClickHouse].

## Requirements

### Generic Behavior

#### RQ.HivePartitioning.Support  
version: 1.0

[ClickHouse] SHALL support interpreting Hive-style partitioned paths (subdirectories in the form `name=value`) as virtual columns when accessing external data sources. This enables querying partitioned data using partition columns directly, without requiring manual parsing of file paths.

For example:

```sql
SET use_hive_partitioning=1
```

```
Structure:
 - /data/sales/date=2025-01-01/file1.parquet  
 - /data/sales/date=2025-01-02/file2.parquet  
 - /data/sales/date=2025-01-03/file3.parquet
```

In this example, date is a virtual column automatically extracted from directory names.

#### RQ.HivePartitioning.EnableSetting
version: 1.0

[ClickHouse] SHALL support setting `use_hive_partitioning` to toggle Hive-style partition recognition for file-based table engines and table functions. By default, in versions where it is disabled, users SHALL enable this setting to activate partition discovery.

```sql
set use_hive_partitioning=1
```

#### RQ.HivePartitioning.Generic.Pruning
version: 1.0

[ClickHouse] SHALL only read files from partitions that satisfy query filters when Hive-style partitioning is enabled and the query includes filters on partition columns. In other words, partition pruning SHALL occur to avoid listing or scanning files in irrelevant directories. This behavior improves query performance by reducing I/O on external storage.

For example:

```
Structure:
 - /data/sales/date=2025-01-01/file1.parquet  
 - /data/sales/date=2025-01-02/file2.parquet  
 - /data/sales/date=2025-01-03/file3.parquet
```

```sql
SET use_hive_partitioning=1

CREATE TABLE sales(...)
Engine=S3('https://<bucket>/data/sales', 'access_key', 'secret_key', 'Parquet')

SELECT * FROM sales WHERE date='2025-01-02'
```

In the example select SHALL read only the second file.

#### RQ.HivePartitioning.Generic.Performance
version: 1.0

[ClickHouse] SHALL execute queries with `use_hive_partitioning = 1` faster than with `use_hive_partitioning = 0` when some files from storage are pruned using a `WHERE` clause on partition columns. This behavior is expected because Hive-style partitioning enables [ClickHouse] to skip irrelevant directories, reducing I/O and query execution time.


For example:

```
Structure:
 - /data/sales/date=2025-01-01/file1.parquet  
 - /data/sales/date=2025-01-02/file2.parquet  
 - /data/sales/date=2025-01-03/file3.parquet
```

```sql
-- Hive partition disabled
SET use_hive_partitioning = 0;

SELECT * FROM sales WHERE date = '2025-01-02';

-- Hive partition enabled
SET use_hive_partitioning = 1;

SELECT * FROM sales WHERE date = '2025-01-02';
```

In this example, the second query (with pruning enabled) SHALL complete faster than the first one.

### Virtual Columns

#### RQ.HivePartitioning.VirtualColumns  
version: 1.0

[ClickHouse] SHALL create a virtual column for each partition key present in the file path, using the same name as the partition key.  

For example, given a path segment `/city=London/`, a virtual column `city` SHALL be available with the value `'London'` for all rows read from that directory.

```
Structure:
 - /data/trips/city=London/file1.parquet
 - /data/trips/city=Berlin/file2.parquet
```

```sql
SET use_hive_partitioning = 1;

SELECT DISTINCT city FROM trips ORDER BY city;
```

Expected output:
```
Berlin  
London
```

#### RQ.HivePartitioning.VirtualColumns.ReadOnly  
version: 1.0

[ClickHouse] SHALL treat virtual columns created by Hive-style partitioning as read-only. Any attempt to modify, insert into, or otherwise write to these columns SHALL result in an error.
[ClickHouse] SHALL return the following error if a write operation targets a virtual column: `DB::Exception: Failed to check existence of a key`


#### RQ.HivePartitioning.VirtualColumns.Appearance
version: 1.0

[ClickHouse] SHALL NOT return virtual columns created by Hive-style partitioning in the query output unless they are explicitly selected.

For example:

```
Structure:
 - /data/sales/city=London/file1.parquet
 - /data/sales/city=Berlin/file2.parquet
```

```sql
SET use_hive_partitioning = 1;

SELECT * FROM sales;
```

The city column SHALL NOT appear in the result set, because it was not selected explicitly.

#### RQ.HivePartitioning.VirtualColumns.Accessibility
version: 1.0

Virtual columns created by Hive-style partitioning SHALL be accessible in queries.

For example:

```sql
SET use_hive_partitioning = 1;

SELECT date
FROM s3('https://<bucket>/data/sales', 'access_key', 'secret_key', 'Parquet')
WHERE date = '2020-01-01';
```

In this example, date is not a physical column in the file, but a virtual column automatically derived from the file path (e.g., /date=2020-01-01/).
[ClickHouse] SHALL allow filtering and selecting by this column as part of query execution.


##### RQ.HivePartitioning.VirtualColumns.InvalidPath  
version: 1.0

[ClickHouse] SHALL return an error  
`DB::Exception: Failed to check existence of a key`  
if the path defined in the query is invalid or the underlying storage does not contain the expected files.

This includes cases such as:
- The path does not exist.
- The path does not conform to the Hive-style partitioning pattern (e.g., mismatched `key` or `value`).

#### RQ.HivePartitioning.VirtualColumns.NameConflict  
version: 1.0

[ClickHouse] SHALL NOT use a virtual column if its name conflicts with the name of an existing table column.

This ensures that explicitly defined table columns always take precedence over virtual columns derived from partitioned paths.


For example:

```
Structure:
 - /data/events/date=2024-01-01/file1.parquet
```

```sql
SET use_hive_partitioning = 1;

CREATE TABLE events
(
    id UInt32,
    date Date
)
ENGINE = S3('https://<bucket>/data/events', 'access_key', 'secret_key', 'Parquet');

SELECT date FROM events WHERE id = 1;
```
In this example, the value of the date column SHALL come from the Parquet file, not from the path segment date=2024-01-01.
The virtual column date SHALL be ignored due to the name conflict with the real column date in the schema.

#### RQ.HivePartitioning.VirtualColumns.HiveDisabled  
version: 1.0

[ClickHouse] SHALL NOT create virtual columns if the `use_hive_partitioning` setting is disabled.


```
SET use_hive_partitioning=0
```


#### RQ.HivePartitioning.VirtualColumns.NonExistingKey
version: 1.0

[Clickhouse] SHALL return `Unknown identifier` error if query refers to nonexisting partition key.

For example:

```
Structure:
 - /data/events/date=2024-01-01/file1.parquet
```

```sql
SET use_hive_partitioning = 1;

CREATE TABLE events
(
    id UInt32,
)
ENGINE = S3('https://<bucket>/data/events', 'access_key', 'secret_key', 'Parquet');

SELECT region from events
```
In this example, the virtual column region does not exist in the partitioned path or in the Parquet file schema.


### Hive Partition Types Value

#### RQ.HivePartitioning.HivePartitionValue  
version: 1.0

Partition values extracted from Hive-style partitioned paths SHALL be treated as `LowCardinality(String)`, with no implicit type inference.

This ensures that values like `2024-01-01`, `123`, or `true` are interpreted as string literals, unless explicitly cast by the user.

#### RQ.HivePartitioning.HivePartitionValue.EmptyValue  
version: 1.0

The partition value SHALL be an empty string (`''`) if a directory in the path is missing a value.

For example:

```
Structure:
 - /data/events/city=/file1.parquet
```

```sql
SELECT city FROM events;
```

In this example, select SHALL return ''.


### Wildcards

#### RQ.HivePartitioning.Wildcards  
version: 1.0

[ClickHouse] SHALL support glob-style wildcards when resolving paths in Hive-style partitioning.


#### RQ.HivePartitioning.Wildcards.SingleStar  
version: 1.0

[ClickHouse] SHALL support the `*` wildcard in Hive-style partitioning.  
The `*` wildcard SHALL match any sequence of characters excluding `/`.

For example:
```sql
SELECT * FROM s3('https://<bucket>/data/year=*/month=*/', ...);
```

#### RQ.HivePartitioning.Wildcards.DoubleStar  
version: 1.0

[ClickHouse] SHALL support the `**` wildcard in Hive-style partitioning.  
The `**` wildcard SHALL match any sequence of characters including `/`.

for example:

```sql
SELECT * FROM s3('https://<bucket>/data/**/file.parquet', ...);
```

#### RQ.HivePartitioning.Wildcards.QuestionMark  
version: 1.0

[ClickHouse] SHALL support the `?` wildcard in Hive-style partitioning.  
The `?` wildcard SHALL match a single character, excluding `/`.

For example:

```sql
SELECT * FROM s3('https://<bucket>/data/year=202?', ...);
```

#### RQ.HivePartitioning.Wildcards.List  
version: 1.0

[ClickHouse] SHALL support the `{a[,b][,c]...}` wildcard syntax for Hive-style partitioning.  
This wildcard SHALL match one of the listed values.


For example
```sql
SELECT * FROM s3('https://<bucket>/data/month={01,02,03}/', ...);
```

#### RQ.HivePartitioning.Wildcards.WrongList  
version: 1.0

[ClickHouse] SHALL return an error if one or more paths specified in a `{a[,b]...}` list do not exist.

#### RQ.HivePartitioning.Wildcards.Range  
version: 1.0

[ClickHouse] SHALL support the `{N..M}` range wildcard in Hive-style partitioning.  
This wildcard SHALL expand to all integers from `N` to `M` inclusive.

```sql
SELECT * FROM s3('https://<bucket>/data/day={1..7}/', ...);
```

#### RQ.HivePartitioning.Wildcards.WrongRange  
version: 1.0

[ClickHouse] SHALL return an error if one or more values in the `{N..M}` range are invalid or the corresponding paths do not exist.

#### RQ.HivePartitioning.Wildcards.Escaping  
version: 1.0

[ClickHouse] SHALL allow escaping of wildcard characters (`*`, `?`, `{`, `}`) using a backslash (`\`) for literal matching.

Example:

```sql
SELECT * FROM s3('https://<bucket>/data/\{special\}/file.parquet', ...);
```

### Supported Table Functions

#### RQ.HivePartitioning.TableFunction.S3  
version: 1.0

[ClickHouse] SHALL support Hive-style partitioning with the `s3` table function when reading from the specified URL path.

If the S3 path contains wildcard patterns corresponding to `name=value` directories and `use_hive_partitioning` is enabled, [ClickHouse] SHALL:

- Detect and interpret partition keys from the path.
- Expose corresponding virtual columns.
- Prune irrelevant partitions based on query filters.

For example:

```sql
SET use_hive_partitioning = 1;

SELECT COUNT(*) 
FROM s3('s3://bucket/data/date=*/region=*/*.parquet', 'Parquet') 
WHERE region = 'EU' AND date >= '2022-01-01';
```
In this example, [ClickHouse] SHALL read only files matching the region='EU' and date >= '2022-01-01' filters,
and expose date and region as virtual columns.

#### RQ.HivePartitioning.TableFunction.S3Cluster  
version: 1.0

[ClickHouse] SHALL support Hive-style partitioning with the `s3Cluster` table function when reading across a cluster.

On each cluster node, the function SHALL:

- Detect and interpret partition keys from the S3 path using `name=value` directory structure.
- Expose corresponding virtual columns.
- Prune irrelevant partitions based on query filters, just like the `s3` table function.

This ensures that distributed querying of S3-partitioned datasets is consistent and efficient across all cluster nodes, reading only the necessary files per node.

For example:

```sql
SET use_hive_partitioning = 1;

SELECT COUNT(*)
FROM s3Cluster('my_cluster', 's3://bucket/data/date=*/region=*/*.parquet', 'Parquet')
WHERE region = 'EU' AND date >= '2022-01-01';
```

#### RQ.HivePartitioning.TableFunction.HDFS  
version: 1.0

[ClickHouse] SHALL support Hive-style partitioning with the `hdfs` table function when reading from the specified HDFS URL path.

If the path contains wildcard patterns corresponding to `name=value` directories and `use_hive_partitioning` is enabled, [ClickHouse] SHALL:

- Detect and interpret partition keys from the directory structure.
- Expose corresponding virtual columns.
- Prune irrelevant partitions based on query filters.

For example:

```sql
SET use_hive_partitioning = 1;

SELECT *
FROM hdfs('hdfs://namenode/data/year=*/region=*/*.parquet', 'Parquet')
WHERE region = 'US' AND year = '2023';
```

### Supported Table Engines

#### S3 Table Engine

##### RQ.HivePartitioning.TableEngines.S3  
version: 1.0

[ClickHouse] SHALL support reading from the `S3` table engine with Hive-style partitioning.  
Partitioning columns SHALL be explicitly defined in the `PARTITION BY` clause of the table definition.

For example:

```sql
SET use_hive_partitioning = 1;

CREATE TABLE s3_engine_table
(
    x Int64
)
ENGINE = S3('https://<bucket>/data/{date}/file.parquet', 'access_key', 'secret_key', 'Parquet')
PARTITION BY date;
```
In this example, [ClickHouse] SHALL extract the date value from the file path and expose it as a virtual column.

#### HDFS Table Engine

##### RQ.HivePartitioning.TableEngines.HDFS
version: 1.0

[ClickHouse] SHALL support reading from the HDFS table engine with Hive-style partitioning.
Partitioning columns SHALL be explicitly defined in the PARTITION BY clause.

For example:

```sql
SET use_hive_partitioning = 1;

CREATE TABLE hdfs_sales
(
    x Int64
)
ENGINE = HDFS('hdfs:///data/{date}/file.parquet', 'Parquet')
PARTITION BY date;
```
In this example, [ClickHouse] SHALL use the date segment from the path as a virtual partition column.

#### Hive Table Engine

##### RQ.HivePartitioning.TableEngines.Hive
version: 1.0

[ClickHouse] SHALL support reading from the Hive table engine with Hive-style partitioning.
Partitioning columns SHALL be defined in the Hive Metastore.

```sql
SET use_hive_partitioning = 1;

CREATE TABLE hive_table
(
    x Int64
)
ENGINE = Hive('thrift://metastore:9083', 'default', 'sales');
```
In this example, [ClickHouse] SHALL detect partition columns from the Hive Metastore schema
and expose them as virtual columns during query execution.

### Hive Partition Writes

#### S3 Table Engine Writes

##### RQ.HivePartitioning.Writes.S3  
version: 1.0

[ClickHouse] SHALL support Hive-style partitioned writes using the `S3` table engine.

For example:

```sql
CREATE TABLE hive_writes
(
    year UInt16,
    country String,
    x UInt8
)
ENGINE = S3(s3_conn, filename = 'filename', format = Parquet, partition_strategy = 'hive')
PARTITION BY (year, country);

INSERT INTO hive_writes VALUES
    (2022, 'USA', 1),
    (2022, 'Canada', 2);
```

In this example, [ClickHouse] SHALL write each row into a separate Hive-style partition path:
```
Structure:
 - /year=2023/country=Germany/...
 - /year=2023/country=France/...
```

##### Partition Strategy Parameter

###### RQ.HivePartitioning.Writes.PartitionStrategy
version: 1.0

[ClickHouse] SHALL support the `partition_strategy` parameter in the `S3` table engine definition. This parameter determines whether Hive-style partitioned writes are enabled.

[ClickHouse] SHALL support the following values for `partition_strategy`:

- `'hive'`: Enables Hive-style partitioned writes. Data will be written into partitioned paths based on the `PARTITION BY` clause (e.g., `/key=value/`).
- `'auto'`: Disables Hive-style partitioning. Data will be written without creating Hive-style partition directories.

If the `partition_strategy` parameter is not explicitly specified, it SHALL default to `'auto'`.


```sql
ENGINE = S3(s3_conn,..., partition_strategy='hive')
```

###### RQ.HivePartitioning.Writes.PartitionStrategyWrongArgument
version: 1.0

[ClickHouse] SHALL return an error `DB::Exception: Unknown partitioning style ` if the `partition_strategy` parameter is set to a value other than `'auto'` or `'hive'`.

##### Partition Columns In Data File Parameter

###### RQ.HivePartitioning.Writes.PartitionColumnsInDataFile
version: 1.0

[ClickHouse] SHALL support the `partition_columns_in_data_file` parameter in the `S3` table engine definition if `partition_strategy='hive'`.

This parameter controls whether columns used in the `PARTITION BY` clause are also written into the data files.

- If `partition_columns_in_data_file = true`, partition columns SHALL be included in the file.
- If `partition_columns_in_data_file = false`, partition columns SHALL NOT be included in the file and are expected to be inferred from the path (e.g., `/key=value/`).

By default, `partition_columns_in_data_file` SHALL be set to `false`.

```sql
ENGINE = S3(s3_conn,..., partition_columns_in_data_file=1)
```

###### RQ.HivePartitioning.Writes.PartitionColumnsInDataFileWithoutHivePartitionStrategy
version: 1.0

[ClickHouse] SHALL return an error if `partition_columns_in_data_file` is specified but `partition_strategy='auto'` or not defined.

###### RQ.HivePartitioning.Writes.PartitionColumnsInDataFileWrongArgiment
version: 1.0

[ClickHouse] SHALL return an error if the `partition_columns_in_data_file` parameter is assigned a value that cannot be interpreted as a Boolean.

##### Path Parameter

###### RQ.HivePartitioning.Writes.Path
version: 1.0

[ClickHouse] SHALL support the `path` parameter in the `S3` table engine definition to specify the full bucket path used as the root for Hive-style partitioned writes.
The `path` parameter SHALL define the S3 bucket and optional prefix under which partitioned files will be created. 
Partition subdirectories (e.g., `/key=value/`) and filenames defined by `filename` will be appended to this base path automatically.

##### RQ.HivePartitioning.Writes.InvalidPath
version: 1.0

[ClickHouse] SHALL return an error `DB::Exception: Invalid S3 key` if the defined `path` parameter is invalid in the context of Hive-style partitioning with the `S3` table engine.

This includes cases where the `path`:

- Is not a valid S3 URI.
- Contains illegal characters.

##### Filename Parameter

###### RQ.HivePartitioning.Writes.Filename  
version: 1.0

[ClickHouse] SHALL support the `filename` parameter in the `S3` table engine definition to specify a directory that SHALL be prepended before all Hive-style partition directories.
[ClickHouse] SHALL support this parameter only if `partition_strategy='hive'`.

The full write path SHALL be constructed as:
```
<path>/<filename>/<key1>=<value1>/<key2>=<value2>/...
```

###### RQ.HivePartitioning.Writes.FilenameWithoutHivePartitionStrategy 
version: 1.0

[ClickHouse] SHALL return an error if `filename` is specified but `partition_strategy='auto'` or not defined.

###### RQ.HivePartitioning.Writes.NotDefinedFilename 
version: 1.0

[ClickHouse] SHALL write partitioned data directly into the root `path` if the `filename` parameter is not defined and `partition_strategy` is set to `'hive'`.


In this case, the write path SHALL be constructed as:

```
<path>//<key1>=<value1>/<key2>=<value2>/...
```

##### S3 Engine Parameters

###### RQ.HivePartitioning.Writes.S3EngineParameters  
version: 1.0

[ClickHouse] SHALL NOT alter the behavior of the following S3 engine parameters when `partition_strategy` is set to `'hive'`:

- `aws_access_key_id`
- `aws_secret_access_key`
- `format`
- `compression`

##### RQ.HivePartitioning.Writes.UseHivePartitions  
version: 1.0

[ClickHouse] SHALL ignore the `use_hive_partitioning = 0` setting during write operations if `partition_strategy = 'hive'` is explicitly specified.

For example:

```sql
SET use_hive_partitioning = 0;

CREATE TABLE hive_writes
(
    year UInt16,
    country String,
    x UInt8
)
ENGINE = S3(s3_conn, filename = 'filename', format = Parquet, partition_strategy = 'hive')
PARTITION BY (year, country);

INSERT INTO hive_writes VALUES
    (2023, 'Germany', 10),
    (2023, 'France', 20);
```

In this example,[ClickHouse] SHALL write the data into Hive-style partitioned paths:
```
Structure:
 - /year=2023/country=Germany/...
 - /year=2023/country=France/...
```
#### Writes By Partitions And Parts

##### RQ.HivePartitioning.Writes.PartitionsParts  
version: 1.0

[ClickHouse] SHALL support writing data into multiple Hive-style partition paths when using the `S3` table engine with `partition_strategy = 'hive'`.

This includes:
- Writing rows to multiple partition paths within a single INSERT.
- Writing to the same or different partitions across multiple `INSERT`

#### Using Expressions In Partition By Clause

##### RQ.HivePartitioning.Writes.Expressions
version: 1.0

[ClickHouse] SHALL return an error if the `PARTITION BY` clause contains an expression, when using `partition_strategy = 'hive'`.

Only column names are allowed in the `PARTITION BY` clause for Hive-style partitioning.

For example:

```sql
CREATE TABLE hive_invalid
(
    year UInt16,
    month UInt8,
    value UInt32
)
ENGINE = S3(s3_conn, filename = 'file.parquet', format = Parquet, partition_strategy = 'hive')
PARTITION BY toString(year);
```

#### Inserting Into Existing File

##### RQ.HivePartitioning.Writes.FileExist  
version: 1.0

[ClickHouse] SHALL properly append data to an existing file when writing via the `S3` table engine with `partition_strategy = 'hive'`.

If the target file already exists, [ClickHouse] SHALL append the new data without deleting or overwriting existing content.

#### Missing Partition By Column

##### RQ.HivePartitioning.Writes.MissingColumn
version: 1.0

[ClickHouse] SHALL return an error if any column defined in the `PARTITION BY` clause is missing from the table schema.

For example:

```sql
CREATE TABLE hive_sales
(
    year UInt16,
    value UInt32
)
ENGINE = S3(s3_conn, filename = 'file.parquet', format = Parquet, partition_strategy = 'hive')
PARTITION BY (year, country);
```

#### Using Default Value 

##### RQ.HivePartitioning.Writes.DefaultValue  
version: 1.0

[ClickHouse] SHALL use the default value defined in the table schema for any partitioning column that is omitted during `INSERT`, when writing with `partition_strategy = 'hive'`.


For example:

```sql
CREATE TABLE hive_sales
(
    year UInt16 DEFAULT 2023,
    country String DEFAULT 'Unknown',
    value UInt32
)
ENGINE = S3(s3_conn, filename = 'file.parquet', format = Parquet, partition_strategy = 'hive')
PARTITION BY (year, country);

-- 'year' and 'country' are omitted; defaults will be used
INSERT INTO hive_sales (value) VALUES (100);
```

In this example, [ClickHouse] SHALL write to the following partition path:

```
Structure:
 - /year=2023/country=Unknown/file.parquet
```

#### Using Nullable Datatypes

##### RQ.HivePartitioning.Writes.NullableDataType
version: 1.0

[ClickHouse] SHALL return an error `DB::Exception: Hive partitioning supports only partition columns of types` 
if any column defined in the `PARTITION BY` clause is of a nullable data type when using `partition_strategy = 'hive'`.

#### Supported Data Types

##### RQ.HivePartitioning.Writes.SupportedDataTypes  
version: 1.0

[ClickHouse] SHALL support the following data types for Hive-style partitioning during write operations (`partition_strategy = 'hive'`)
if partition key satisfy all of the following conditions:

- The value length SHALL be less than 1024 characters.
- The value SHALL NOT contain special characters: `{}`, `\`, `/`, `"`, `'`, `*`, `?`.

The following data types are supported as partition keys:

| Data Type     | Supported |
|---------------|-----------|
| Int8          | ✅ Yes    |
| Int16         | ✅ Yes    |
| Int32         | ✅ Yes    |
| Int64         | ✅ Yes    |
| Int128        | ✅ Yes    |
| Int256        | ✅ Yes    |
| UInt8         | ✅ Yes    |
| UInt16        | ✅ Yes    |
| UInt32        | ✅ Yes    |
| UInt64        | ✅ Yes    |
| UInt128       | ✅ Yes    |
| UInt256       | ✅ Yes    |
| String        | ✅ Yes    |
| FixedString(N)| ✅ Yes    |
| Date          | ✅ Yes    |
| Date32        | ✅ Yes    |
| Time          | ✅ Yes    |
| Time64(N)     | ✅ Yes    |
| DateTime      | ✅ Yes    |
| DateTime64(N) | ✅ Yes    |
| Bool          | ✅ Yes    |

#### Unsupported Types

##### RQ.HivePartitioning.Writes.DataTypesUnsupported
version: 1.0

[ClickHouse] SHALL return an error `DB::Exception: Hive partitioning supports only partition columns of types` 
if the data type of any column defined in the `PARTITION BY` clause is not included in the list of supported types for Hive-style partitioning.

#### Using ReadOnly Bucket

##### RQ.HivePartitioning.Writes.ReadOnlyBucket
version: 1.0

[ClickHouse] SHALL return an error `DB::Exception: Failed to check existence of a key`
if bucket defined in S3 engine clause is read-only.

#### Non-Accessible Bucket

##### RQ.HivePartitioning.Writes.NonAccessibleBucket
version: 1.0

[ClickHouse] SHALL return an error `DB::Exception: Failed to check existence of a key`
 if bucket defined in S3 engine clause is not accessible.

#### Parallel Inserts

##### RQ.HivePartitioning.Writes.ParallelInserts
version: 1.0

[ClickHouse] SHALL support parallel inserts into the same Hive-style partition when writing with the `S3` table engine and `partition_strategy = 'hive'`.

Multiple concurrent `INSERT` operations targeting the same file or partition path SHALL succeed without data loss or corruption.

#### Failing Write

##### RQ.HivePartitioning.Writes.WriteFail  
version: 1.0

[ClickHouse] SHALL not leave any partial data if writing to one or more objects fails during Hive-style partitioned writes.

#### Partition By Clause

##### RQ.HivePartitioning.Writes.PartitionBy
version: 1.0

[ClickHouse] SHALL perform Hive-style partitioned writes only if the table definition includes a valid `PARTITION BY` clause.

If the `PARTITION BY` clause is missing, and `partition_strategy = 'hive'` is specified, 
[ClickHouse] SHALL return an error `DB::Exception: Partition strategy hive can not be used without a PARTITION BY expression.`.

This ensures that directory-based partitioning structure is explicitly defined and not left ambiguous.

For example:

```sql
CREATE TABLE hive_data
(
    year UInt16,
    value UInt32
)
ENGINE = S3(s3_conn, filename = 'table', format = Parquet, partition_strategy = 'hive');
```
In this example, [ClickHouse] SHALL return an error.

##### RQ.HivePartitioning.Writes.PartitionKey
version: 1.0

[ClickHouse] SHALL create a directory path of the form `/key=value/` for each column defined in the `PARTITION BY` clause when performing Hive-style partitioned writes.
If the target file at the resulting path does not exist, it SHALL be created automatically.  
Inserted data SHALL be written into that file.

Partition keys may contain special characters that are safe for directory names (e.g., spaces, `-`, `_`, `%`), and these SHALL be properly encoded if required by the underlying filesystem or object storage.

For example:

```sql
CREATE TABLE hive_orders
(
    region String,
    year UInt16,
    order_id UInt64
)
ENGINE = S3(s3_conn, filename = 'orders.parquet', format = Parquet, partition_strategy = 'hive')
PARTITION BY (region, year);

INSERT INTO hive_orders VALUES ('North-America', 2024, 1);
```

```
Structure:
 - /region=North-America/year=2024/orders.parquet
```

[ClickHouse]: https://clickhouse.com
[s3]: https://clickhouse.com/docs/sql-reference/table-functions/s3
[s3Cluster]: https://clickhouse.com/docs/sql-reference/table-functions/s3Cluster
[HDFS]: https://clickhouse.com/docs/sql-reference/table-functions/hdfs
