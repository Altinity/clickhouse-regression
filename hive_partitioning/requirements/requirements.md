# SRS-045 Hive Partitioning
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Requirements](#requirements)
    * 2.1 [Generic Behavior](#generic-behavior)
        * 2.1.1 [RQ.HivePartitioning.Generic.Support](#rqhivepartitioninggenericsupport)
        * 2.1.2 [RQ.HivePartitioning.Generic.EnableSetting](#rqhivepartitioninggenericenablesetting)
        * 2.1.3 [RQ.HivePartitioning.Generic.Pruning](#rqhivepartitioninggenericpruning)
        * 2.1.4 [RQ.HivePartitioning.Generic.Performance](#rqhivepartitioninggenericperformance)
    * 2.2 [Virtual Columns](#virtual-columns)
        * 2.2.1 [RQ.HivePartitioning.VirtualColumns.Generic](#rqhivepartitioningvirtualcolumnsgeneric)
        * 2.2.2 [RQ.HivePartitioning.VirtualColumns.ReadOnly](#rqhivepartitioningvirtualcolumnsreadonly)
        * 2.2.3 [RQ.HivePartitioning.VirtualColumns.Appearance](#rqhivepartitioningvirtualcolumnsappearance)
        * 2.2.4 [RQ.HivePartitioning.VirtualColumns.Accessability](#rqhivepartitioningvirtualcolumnsaccessability)
        * 2.2.5 [RQ.HivePartitioning.VirtualColumns.InvalidPath](#rqhivepartitioningvirtualcolumnsinvalidpath)
        * 2.2.6 [RQ.HivePartitioning.VirtualColumns.NameConflict](#rqhivepartitioningvirtualcolumnsnameconflict)
        * 2.2.7 [RQ.HivePartitioning.VirtualColumns.HiveDisabled](#rqhivepartitioningvirtualcolumnshivedisabled)
        * 2.2.8 [RQ.HivePartitioning.VirtualColumns.NonExistingKey](#rqhivepartitioningvirtualcolumnsnonexistingkey)
    * 2.3 [Hive Partition Types](#hive-partition-types)
        * 2.3.1 [RQ.HivePartitioning.HivePartitionTypes.Generic](#rqhivepartitioninghivepartitiontypesgeneric)
        * 2.3.2 [RQ.HivePartitioning.HivePartitionTypes.DefaultType](#rqhivepartitioninghivepartitiontypesdefaulttype)
        * 2.3.3 [RQ.HivePartitioning.HivePartitionTypes.EmptyValue](#rqhivepartitioninghivepartitiontypesemptyvalue)
    * 2.4 [Wildcards](#wildcards)
        * 2.4.1 [RQ.HivePartitioning.Wildcards.Generic](#rqhivepartitioningwildcardsgeneric)
        * 2.4.2 [RQ.HivePartitioning.Wildcards.SingleStar](#rqhivepartitioningwildcardssinglestar)
        * 2.4.3 [RQ.HivePartitioning.Wildcards.DoubleStart](#rqhivepartitioningwildcardsdoublestart)
        * 2.4.4 [RQ.HivePartitioning.Wildcards.QuestionMark](#rqhivepartitioningwildcardsquestionmark)
        * 2.4.5 [RQ.HivePartitioning.Wildcards.List](#rqhivepartitioningwildcardslist)
        * 2.4.6 [RQ.HivePartitioning.Wildcards.WrongList](#rqhivepartitioningwildcardswronglist)
        * 2.4.7 [RQ.HivePartitioning.Wildcards.Range](#rqhivepartitioningwildcardsrange)
        * 2.4.8 [RQ.HivePartitioning.Wildcards.WrongRange](#rqhivepartitioningwildcardswrongrange)
    * 2.5 [Supported Table Functions](#supported-table-functions)
        * 2.5.1 [RQ.HivePartitioning.TableFunction.S3](#rqhivepartitioningtablefunctions3)
        * 2.5.2 [RQ.HivePartitioning.TableFunction.S3Cluster](#rqhivepartitioningtablefunctions3cluster)
        * 2.5.3 [RQ.HivePartitioning.TableFunction.HDFS](#rqhivepartitioningtablefunctionhdfs)
    * 2.6 [Supported Table Engines](#supported-table-engines)
        * 2.6.1 [S3 Table Engine](#s3-table-engine)
            * 2.6.1.1 [RQ.HivePartitioning.TableEngines.S3](#rqhivepartitioningtableenginess3)
        * 2.6.2 [HDFS Table Engine](#hdfs-table-engine)
            * 2.6.2.1 [RQ.HivePartitioning.TableEngines.HDFS](#rqhivepartitioningtableengineshdfs)
        * 2.6.3 [Hive Table Engine](#hive-table-engine)
            * 2.6.3.1 [RQ.HivePartitioning.TableEngines.Hive](#rqhivepartitioningtableengineshive)
    * 2.7 [Hive Partition Writes](#hive-partition-writes)
        * 2.7.1 [Generic](#generic)
            * 2.7.1.1 [RQ.HivePartitioning.HivePartitionWrites.S3](#rqhivepartitioninghivepartitionwritess3)
            * 2.7.1.2 [RQ.HivePartitioning.HivePartitionWrites.UseHivePartitions](#rqhivepartitioninghivepartitionwritesusehivepartitions)
            * 2.7.1.3 [RQ.HivePartitioning.HivePartitionWrites.FileExist](#rqhivepartitioninghivepartitionwritesfileexist)
            * 2.7.1.4 [RQ.HivePartitioning.HivePartitionWrites.MissingColumn](#rqhivepartitioninghivepartitionwritesmissingcolumn)
            * 2.7.1.5 [RQ.HivePartitioning.HivePartitionWrites.NullInColumn](#rqhivepartitioninghivepartitionwritesnullincolumn)
            * 2.7.1.6 [RQ.HivePartitioning.HivePartitionWrites.UnsupportedTypes](#rqhivepartitioninghivepartitionwritesunsupportedtypes)
            * 2.7.1.7 [RQ.HivePartitioning.HivePartitionWrites.ReadOnlyBucket](#rqhivepartitioninghivepartitionwritesreadonlybucket)
            * 2.7.1.8 [RQ.HivePartitioning.HivePartitionWrites.NonAccessibleBucket](#rqhivepartitioninghivepartitionwritesnonaccessiblebucket)
            * 2.7.1.9 [RQ.HivePartitioning.HivePartitionWrites.ParallelInserts](#rqhivepartitioninghivepartitionwritesparallelinserts)
            * 2.7.1.10 [RQ.HivePartitioning.HivePartitionWrites.WriteFail](#rqhivepartitioninghivepartitionwriteswritefail)
        * 2.7.2 [Partition By Clause For S3 Engine With Hive Partition Writes](#partition-by-clause-for-s3-engine-with-hive-partition-writes)
            * 2.7.2.1 [RQ.HivePartitioning.HivePartitionWrites.PartitionBy](#rqhivepartitioninghivepartitionwritespartitionby)
            * 2.7.2.2 [RQ.HivePartitioning.HivePartitionWrites.MissingPartitionBy](#rqhivepartitioninghivepartitionwritesmissingpartitionby)
            * 2.7.2.3 [RQ.HivePartitioning.HivePartitionWrites.PartitionKey](#rqhivepartitioninghivepartitionwritespartitionkey)
        * 2.7.3 [Hive Partition Writes Syntax](#hive-partition-writes-syntax)
            * 2.7.3.1 [RQ.HivePartitioning.HivePartitionWritesSyntax.Generic](#rqhivepartitioninghivepartitionwritessyntaxgeneric)
        * 2.7.4 [Partition Stratagy Parameter](#partition-stratagy-parameter)
            * 2.7.4.1 [RQ.HivePartitioning.HivePartitionWrites.PartitionStratagy](#rqhivepartitioninghivepartitionwritespartitionstratagy)
            * 2.7.4.2 [RQ.HivePartitioning.HivePartitionWrites.PartitionStratagyWrongArgument](#rqhivepartitioninghivepartitionwritespartitionstratagywrongargument)
        * 2.7.5 [Hive Partition Strategy Write Partition Columns Into Files Parameter](#hive-partition-strategy-write-partition-columns-into-files-parameter)
            * 2.7.5.1 [RQ.HivePartitioning.HivePartitionWrites.HivePartitionStrategyWritePartitionColumnsIntoFiles](#rqhivepartitioninghivepartitionwriteshivepartitionstrategywritepartitioncolumnsintofiles)
            * 2.7.5.2 [RQ.HivePartitioning.HivePartitionWrites.HivePartitionStrategyWritePartitionColumnsIntoFilesWrongArgument](#rqhivepartitioninghivepartitionwriteshivepartitionstrategywritepartitioncolumnsintofileswrongargument)
        * 2.7.6 [Path Parameter](#path-parameter)
            * 2.7.6.1 [RQ.HivePartitioning.HivePartitionWrites.Path](#rqhivepartitioninghivepartitionwritespath)
            * 2.7.6.2 [RQ.HivePartitioning.HivePartitionWrites.InvalidPath](#rqhivepartitioninghivepartitionwritesinvalidpath)
        * 2.7.7 [Filename Parameter](#filename-parameter)
            * 2.7.7.1 [RQ.HivePartitioning.HivePartitionWrites.Filename](#rqhivepartitioninghivepartitionwritesfilename)
            * 2.7.7.2 [RQ.HivePartitioning.HivePartitionWrites.InvalidFilename](#rqhivepartitioninghivepartitionwritesinvalidfilename)
            * 2.7.7.3 [RQ.HivePartitioning.HivePartitionWrites.NotDefinedFilename](#rqhivepartitioninghivepartitionwritesnotdefinedfilename)
        * 2.7.8 [S3 Engine Parameters](#s3-engine-parameters)
            * 2.7.8.1 [RQ.HivePartitioning.HivePartitionWrites.S3EngineParameters](#rqhivepartitioninghivepartitionwritess3engineparameters)



## Introduction

This document describes the requirements for the [ClickHouse] hive-style partitioning functionality. Hive-style partitioning refers to organizing files in a directory hierarchy where folder names encode column values (e.g. .../country=US/year=2021/file.parquet). [ClickHouse] provides functionality to read and write such partitioned data across various interfaces, including S3 and HDFS table functions and the Hive table engine. This allows users to query partitioned datasets efficiently by treating partition names as data columns and pruning unnecessary files. The following requirements describe the expected functionality and behavior for Hive-style partitioning support in [ClickHouse].

## Requirements

### Generic Behavior

#### RQ.HivePartitioning.Generic.Support
version: 1.0

[ClickHouse] SHALL support interpreting Hive-style partitioned paths (subdirectories in the form name=value) as virtual columns when accessing external data sources. This enables querying partitioned data without manual parsing of file paths.

#### RQ.HivePartitioning.Generic.EnableSetting
version: 1.0

[ClickHouse] SHALL use support setting `use_hive_partitioning` to toggle Hive-style partition recognition for file-based table engines and table functions. By default, in versions where it is disabled, users SHALL enable this setting to activate partition discovery.

#### RQ.HivePartitioning.Generic.Pruning
version: 1.0

[ClickHouse] SHALL only read the files from the partitions that satisfy filters when Hive-style partitioning is enabled and queries include filters on partition columns. In other words, partition pruning SHALL occur to avoid listing or scanning files in irrelevant directories. This behavior improves query performance by reducing I/O on external storage.

#### RQ.HivePartitioning.Generic.Performance
version: 1.0

[ClickHouse] SHALL execute queries with `use_hive_partitioning=1` faster than queries with `use_hive_partitioning=0` if some files from storage are pruned with `WHERE` clause.

### Virtual Columns

#### RQ.HivePartitioning.VirtualColumns.Generic
version: 1.0

[Clickhouse] SHALL create virtual column for each partition key present in the file path with the same name as the partition key. 

For example, given a path segment /city=London/, a virtual column city will be provided with value "London" for all rows read from that directory.

#### RQ.HivePartitioning.VirtualColumns.ReadOnly
version: 1.0

Virtual columns created by hive partitioning SHALL be read-only.

#### RQ.HivePartitioning.VirtualColumns.Appearance
version: 1.0

Virtual columns created by hive partitioning SHALL not appear in query output, when query does not select this queries.

For example:
`SELECT *` 
This query SHALL not return virtual columns.

#### RQ.HivePartitioning.VirtualColumns.Accessability
version: 1.0

Virtual columns created by hive partitioning SHALL be accessible in queries.

For example:
`SELECT date FROM s3(...) WHERE date='01-01-2020'`

#### RQ.HivePartitioning.VirtualColumns.InvalidPath
version: 1.0

[ClickHouse] SHALL return an error if path defined in query is invalid or storage does not contain defined files.

#### RQ.HivePartitioning.VirtualColumns.NameConflict
version: 1.0

[ClickHouse] SHALL not use virtual column if name of the virtual column matches with the name of table column.

#### RQ.HivePartitioning.VirtualColumns.HiveDisabled
version: 1.0

[Clickhouse] SHALL not create virtual column if `use_hive_partitioning` setting is disabled.


#### RQ.HivePartitioning.VirtualColumns.NonExistingKey
version: 1.0

[Clickhouse] SHALL return `Unknown identifier` error if query refers to nonexisting partition key.

### Hive Partition Types

#### RQ.HivePartitioning.HivePartitionTypes.Generic
version: 1.0

Partition values extracted from paths SHALL be treated as strings with no implicit type inference.

#### RQ.HivePartitioning.HivePartitionTypes.DefaultType
version: 1.0

Partition values extracted from paths SHALL have `LowCardinality(String)` type.

#### RQ.HivePartitioning.HivePartitionTypes.EmptyValue
version: 1.0

The hive value SHALL be empty string if directory is missing a key.

### Wildcards

#### RQ.HivePartitioning.Wildcards.Generic
version: 1.0

[ClickHouse] SHALL support glob-style wildcards for hive partitioning.

#### RQ.HivePartitioning.Wildcards.SingleStar
version: 1.0

[ClickHouse] SHALL support `*` wildcard for hive partitioning. `*` wildcard SHALL match any sequence of characters except `/`.

#### RQ.HivePartitioning.Wildcards.DoubleStart
version: 1.0

[ClickHouse] SHALL support `**` wildcard for hive partitioning. `**` wildcard SHALL match any sequence of characters including `/`.

#### RQ.HivePartitioning.Wildcards.QuestionMark
version: 1.0

[ClickHouse] SHALL support `?` wildcard for hive partitioning. `?` wildcard SHALL match a single character except `/`.

#### RQ.HivePartitioning.Wildcards.List
version: 1.0

[ClickHouse] SHALL support `{a[, b][, c]...}` wildcard for hive partitioning. `{a[, b][, c]...}` wildcard SHALL match one of the listed options.

#### RQ.HivePartitioning.Wildcards.WrongList
version: 1.0

[ClickHouse] SHALL return an error if one or more options in `{a[, b][, c]...}` are invalid or path does not exists.

#### RQ.HivePartitioning.Wildcards.Range
version: 1.0

[ClickHouse] SHALL support `{N..M}` wildcard for hive partitioning. `{N..M}` wildcard SHALL match numbers in a range.

#### RQ.HivePartitioning.Wildcards.WrongRange
version: 1.0

[ClickHouse] SHALL return an error if one or more options in `{N..M}` are invalid or path does not exists.

### Supported Table Functions

#### RQ.HivePartitioning.TableFunction.S3
version: 1.0

The [s3] table function SHALL support Hive-style partitions for reading in the provided URL path. If the S3 path contains wildcard patterns corresponding to name=value directories and use_hive_partitioning is enabled, ClickHouse SHALL detect those patterns, expose corresponding virtual columns and prune not related to the query partitions. For example, a query:

```SQL
SET use_hive_partitioning = 1;
SELECT COUNT(*) 
FROM s3('s3://bucket/data/date=*/country=*/*.parquet', 'Parquet') 
WHERE country = 'Netherlands' AND date >= '2020-01-01';
```

#### RQ.HivePartitioning.TableFunction.S3Cluster
version: 1.0

The [s3Cluster] table function SHALL equally support Hive-style partitioning for reading across a cluster. On each cluster node, the function SHALL interpret partition directories and prune files in the same manner as a local [s3] call. This ensures distributed querying of an S3-partitioned dataset is consistent and efficient, reading only the necessary partitions on each node.

#### RQ.HivePartitioning.TableFunction.HDFS
version: 1.0

The [HDFS] table function SHALL support Hive-style partitions for reading in the provided URL path. If the path contains wildcard patterns corresponding to name=value directories and use_hive_partitioning is enabled, ClickHouse SHALL detect those patterns, expose corresponding virtual columns and prune not related to the query partitions.

### Supported Table Engines

#### S3 Table Engine

##### RQ.HivePartitioning.TableEngines.S3
version: 1.0

[ClickHouse] SHALL support reading from S3 table engine with hive partitioning. Hive partitioning columns SHALL be defined in PARTITION BY statement.

```SQL
CREATE TABLE s3_engine_table(x Int64)
ENGINE = S3(...)
PARTITION BY date
```

#### HDFS Table Engine

##### RQ.HivePartitioning.TableEngines.HDFS
version: 1.0

[ClickHouse] SHALL support reading from HDFS table engine with hive partitioning. Hive partitioning columns SHALL be defined in PARTITION BY statement.

```SQL
CREATE TABLE hdfs_sales(x Int64)
ENGINE = HDFS(
    'hdfs:///data/{date}/file.parquet', 
    'Parquet'
)
PARTITION BY date
```

#### Hive Table Engine

##### RQ.HivePartitioning.TableEngines.Hive
version: 1.0

[ClickHouse] SHALL support reading from Hive table engine with hive partitioning. Hive partitioning columns SHALL be defined in Hive Metastore.

```SQL
CREATE TABLE hive_table(x Int64)
ENGINE = Hive(...) 
```

### Hive Partition Writes

#### Generic

##### RQ.HivePartitioning.HivePartitionWrites.S3
version: 1.0

[ClickHouse] SHALL support hive-style partition writes by using S3 table engine.


For example:
```SQL
CREATE TABLE hive_writes(year UInt16, country String, x UInt8)
ENGINE = S3(s3_conn, filename = 'filename', format = Parquet, partition_strategy='hive')
PARTITION BY (year, country);

INSERT INTO hive_writes VALUES
    (2022, 'USA', 1),
    (2022, 'Canada', 2);
```


##### RQ.HivePartitioning.HivePartitionWrites.UseHivePartitions
version: 1.0

[ClickHouse] SHALL ignore `use_hive_partitioning=0` if `partition_stratagy=hive`.

##### RQ.HivePartitioning.HivePartitionWrites.FileExist
version: 1.0

[ClickHouse] SHALL properly add data to the file if file already exists. This operation SHALL not delete or overwrite existing data.


##### RQ.HivePartitioning.HivePartitionWrites.MissingColumn
version: 1.0

[ClickHouse] SHALL return an error if columns defined in the `PARTITION BY` clause is missing.

##### RQ.HivePartitioning.HivePartitionWrites.NullInColumn
version: 1.0

[ClickHouse] SHALL return an error when attempting to insert a `NULL` value into a column that is specified in the `PARTITION BY` clause.

##### RQ.HivePartitioning.HivePartitionWrites.UnsupportedTypes
version: 1.0

[ClickHouse] SHALL return an error if type of the column defined in the `PARTITION BY` clause can't be casted into string.

##### RQ.HivePartitioning.HivePartitionWrites.ReadOnlyBucket
version: 1.0

[ClickHouse] SHALL return an error if bucket difined in S3 engine clause is read-only.

##### RQ.HivePartitioning.HivePartitionWrites.NonAccessibleBucket
version: 1.0

[ClickHouse] SHALL return an error if bucket difined in S3 engine clause is not accessible.

##### RQ.HivePartitioning.HivePartitionWrites.ParallelInserts
version: 1.0

[ClickHouse] SHALL support parallel inserts into one file.

##### RQ.HivePartitioning.HivePartitionWrites.WriteFail
version: 1.0

[ClickHouse] SHALL fail the insert and SHALL not leave partial data if any object write fails.

#### Partition By Clause For S3 Engine With Hive Partition Writes

##### RQ.HivePartitioning.HivePartitionWrites.PartitionBy
version: 1.0

[ClickHouse] SHALL perform hive partition writes only if table engine definition contains `PARTITION BY` clause.

##### RQ.HivePartitioning.HivePartitionWrites.MissingPartitionBy
version: 1.0

[ClickHouse] SHALL return an error if user tries to insert into table with S3 table engine without `PARTITION BY` clause.

##### RQ.HivePartitioning.HivePartitionWrites.PartitionKey
version: 1.0

[ClickHouse] SHALL create path containing {/key=value/} for all columns defined in `PARTITION BY` clause and file on this path on insert, if file does not exists.
Inserted data SHALL be located in this file.

#### Hive Partition Writes Syntax

##### RQ.HivePartitioning.HivePartitionWritesSyntax.Generic
version: 1.0

S3 table Engine SHALL have the following syntax:

```SQL
ENGINE = S3(path [, NOSIGN | aws_access_key_id, aws_secret_access_key,] format[, compression][, filename][, partition_stratagy][, hive_partition_strategy_write_partition_columns_into_files])
```

#### Partition Stratagy Parameter

##### RQ.HivePartitioning.HivePartitionWrites.PartitionStratagy
version: 1.0

[ClickHouse] SHALL support `partition_stratagy` parameter for S3 engine that SHALL define if [ClickHouse] enables hive partition writes or no.
[ClickHouse] SHALL support 'hive' and 'auto' values for this parameter. [ClickHouse] SHALL enable hive partition writes if it is set to 'hive' and disable if it is set to 'auto'.
`partition_stratagy` SHALL be 'auto' by default.

##### RQ.HivePartitioning.HivePartitionWrites.PartitionStratagyWrongArgument
version: 1.0

[ClickHouse] SHALL return an error if `partition_stratagy` parameter neither set to 'auto' and 'hive'.

#### Hive Partition Strategy Write Partition Columns Into Files Parameter

##### RQ.HivePartitioning.HivePartitionWrites.HivePartitionStrategyWritePartitionColumnsIntoFiles
version: 1.0

[ClickHouse] SHALL support `partition_columns_in_data_file` parameter for S3 engine that SHALL define if [ClickHouse] writes partition columns into files or not.
`partition_columns_in_data_file` SHALL be False by default.

##### RQ.HivePartitioning.HivePartitionWrites.HivePartitionStrategyWritePartitionColumnsIntoFilesWrongArgument
version: 1.0

[ClickHouse] SHALL return an error if `partition_columns_in_data_file` parameter gets argument that cannot be casted to boolean.

#### Path Parameter

##### RQ.HivePartitioning.HivePartitionWrites.Path
version: 1.0

[ClickHouse] SHALL support `path` parameter that defines path to the bucket for hive partition writes.

##### RQ.HivePartitioning.HivePartitionWrites.InvalidPath
version: 1.0

[ClickHouse] SHALL return an error if defined `path` is invalid.

#### Filename Parameter

##### RQ.HivePartitioning.HivePartitionWrites.Filename
version: 1.0

[ClickHouse] SHALL support `filename` parameter that defines filename for hive partition writes.

##### RQ.HivePartitioning.HivePartitionWrites.InvalidFilename
version: 1.0

[ClickHouse] SHALL return an error if defined `filename` is invalid or points to a directory.

##### RQ.HivePartitioning.HivePartitionWrites.NotDefinedFilename
version: 1.0

[ClickHouse] SHALL write table in the root directory if `filename` parameter is not defined but `partition_stratagy` is set to 'hive'.

#### S3 Engine Parameters

##### RQ.HivePartitioning.HivePartitionWrites.S3EngineParameters
version: 1.0

[ClickHouse] SHALL not change behavior of the following parameters if `partition_stratagy` is set to 'hive':
`aws_access_key_id`, `aws_secret_access_key`, `format`, `compression`.


[ClickHouse]: https://clickhouse.com
[s3]: https://clickhouse.com/docs/sql-reference/table-functions/s3
[s3Cluster]: https://clickhouse.com/docs/sql-reference/table-functions/s3Cluster
[HDFS]: https://clickhouse.com/docs/sql-reference/table-functions/hdfs
