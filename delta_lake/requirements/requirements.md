# SRS-050 ClickHouse Delta Lake
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Terminology](#terminology)
    * 2.1 [Delta Lake](#delta-lake)
    * 2.2 [Delta log](#delta-log)
    * 2.3 [Snapshot](#snapshot)
    * 2.4 [Unity Catalog](#unity-catalog)
    * 2.5 [Delta Kernel](#delta-kernel)
* 3 [Log protocol](#log-protocol)
    * 3.1 [RQ.SRS-050.ClickHouse.DeltaLake.Protocol.Replay](#rqsrs-050clickhousedeltalakeprotocolreplay)
    * 3.2 [RQ.SRS-050.ClickHouse.DeltaLake.Protocol.Paths](#rqsrs-050clickhousedeltalakeprotocolpaths)
    * 3.3 [RQ.SRS-050.ClickHouse.DeltaLake.Protocol.Format](#rqsrs-050clickhousedeltalakeprotocolformat)
    * 3.4 [RQ.SRS-050.ClickHouse.DeltaLake.Protocol.DataChange](#rqsrs-050clickhousedeltalakeprotocoldatachange)
    * 3.5 [RQ.SRS-050.ClickHouse.DeltaLake.Protocol.UnknownFields](#rqsrs-050clickhousedeltalakeprotocolunknownfields)
    * 3.6 [RQ.SRS-050.ClickHouse.DeltaLake.Protocol.Version](#rqsrs-050clickhousedeltalakeprotocolversion)
    * 3.7 [RQ.SRS-050.ClickHouse.DeltaLake.Protocol.CatalogManaged](#rqsrs-050clickhousedeltalakeprotocolcatalogmanaged)
    * 3.8 [RQ.SRS-050.ClickHouse.DeltaLake.Protocol.Statistics](#rqsrs-050clickhousedeltalakeprotocolstatistics)
* 4 [Access](#access)
    * 4.1 [Table function](#table-function)
        * 4.1.1 [RQ.SRS-050.ClickHouse.DeltaLake.Access.TableFunction](#rqsrs-050clickhousedeltalakeaccesstablefunction)
        * 4.1.2 [RQ.SRS-050.ClickHouse.DeltaLake.Access.TableFunction.Backends](#rqsrs-050clickhousedeltalakeaccesstablefunctionbackends)
    * 4.2 [Cluster function](#cluster-function)
        * 4.2.1 [RQ.SRS-050.ClickHouse.DeltaLake.Access.Cluster](#rqsrs-050clickhousedeltalakeaccesscluster)
    * 4.3 [Table engine](#table-engine)
        * 4.3.1 [RQ.SRS-050.ClickHouse.DeltaLake.Access.Engine](#rqsrs-050clickhousedeltalakeaccessengine)
        * 4.3.2 [RQ.SRS-050.ClickHouse.DeltaLake.Access.NamedCollection](#rqsrs-050clickhousedeltalakeaccessnamedcollection)
        * 4.3.3 [RQ.SRS-050.ClickHouse.DeltaLake.Access.Credentials](#rqsrs-050clickhousedeltalakeaccesscredentials)
* 5 [Creating a table](#creating-a-table)
    * 5.1 [RQ.SRS-050.ClickHouse.DeltaLake.Create.AttachExisting](#rqsrs-050clickhousedeltalakecreateattachexisting)
    * 5.2 [RQ.SRS-050.ClickHouse.DeltaLake.Create.NewTable](#rqsrs-050clickhousedeltalakecreatenewtable)
    * 5.3 [RQ.SRS-050.ClickHouse.DeltaLake.Create.NoPartition](#rqsrs-050clickhousedeltalakecreatenopartition)
    * 5.4 [RQ.SRS-050.ClickHouse.DeltaLake.Create.RegisterInUnity](#rqsrs-050clickhousedeltalakecreateregisterinunity)
* 6 [Schema](#schema)
    * 6.1 [RQ.SRS-050.ClickHouse.DeltaLake.Schema.PrimitiveTypes](#rqsrs-050clickhousedeltalakeschemaprimitivetypes)
    * 6.2 [RQ.SRS-050.ClickHouse.DeltaLake.Schema.Decimal](#rqsrs-050clickhousedeltalakeschemadecimal)
    * 6.3 [RQ.SRS-050.ClickHouse.DeltaLake.Schema.Varchar](#rqsrs-050clickhousedeltalakeschemavarchar)
    * 6.4 [RQ.SRS-050.ClickHouse.DeltaLake.Schema.Nested](#rqsrs-050clickhousedeltalakeschemanested)
    * 6.5 [RQ.SRS-050.ClickHouse.DeltaLake.Schema.Nulls](#rqsrs-050clickhousedeltalakeschemanulls)
    * 6.6 [RQ.SRS-050.ClickHouse.DeltaLake.Schema.Void](#rqsrs-050clickhousedeltalakeschemavoid)
    * 6.7 [RQ.SRS-050.ClickHouse.DeltaLake.Schema.PartitionColumns](#rqsrs-050clickhousedeltalakeschemapartitioncolumns)
    * 6.8 [RQ.SRS-050.ClickHouse.DeltaLake.Schema.Unsupported](#rqsrs-050clickhousedeltalakeschemaunsupported)
* 7 [Reads](#reads)
    * 7.1 [RQ.SRS-050.ClickHouse.DeltaLake.Read.Snapshot](#rqsrs-050clickhousedeltalakereadsnapshot)
    * 7.2 [RQ.SRS-050.ClickHouse.DeltaLake.Read.Projection](#rqsrs-050clickhousedeltalakereadprojection)
    * 7.3 [RQ.SRS-050.ClickHouse.DeltaLake.Read.Kernel](#rqsrs-050clickhousedeltalakereadkernel)
    * 7.4 [RQ.SRS-050.ClickHouse.DeltaLake.Read.PartitionPruning](#rqsrs-050clickhousedeltalakereadpartitionpruning)
    * 7.5 [RQ.SRS-050.ClickHouse.DeltaLake.Read.SchemaEvolution](#rqsrs-050clickhousedeltalakereadschemaevolution)
    * 7.6 [RQ.SRS-050.ClickHouse.DeltaLake.Read.TypeWidening](#rqsrs-050clickhousedeltalakereadtypewidening)
    * 7.7 [RQ.SRS-050.ClickHouse.DeltaLake.Read.SchemaReload](#rqsrs-050clickhousedeltalakereadschemareload)
    * 7.8 [RQ.SRS-050.ClickHouse.DeltaLake.Read.ColumnMapping](#rqsrs-050clickhousedeltalakereadcolumnmapping)
    * 7.9 [RQ.SRS-050.ClickHouse.DeltaLake.Read.DeletionVectors](#rqsrs-050clickhousedeltalakereaddeletionvectors)
    * 7.10 [RQ.SRS-050.ClickHouse.DeltaLake.Read.TimeTravel](#rqsrs-050clickhousedeltalakereadtimetravel)
    * 7.11 [RQ.SRS-050.ClickHouse.DeltaLake.Read.ChangeDataFeed](#rqsrs-050clickhousedeltalakereadchangedatafeed)
    * 7.12 [RQ.SRS-050.ClickHouse.DeltaLake.Read.Checkpoint](#rqsrs-050clickhousedeltalakereadcheckpoint)
    * 7.13 [RQ.SRS-050.ClickHouse.DeltaLake.Read.WriterFeatures](#rqsrs-050clickhousedeltalakereadwriterfeatures)
    * 7.14 [RQ.SRS-050.ClickHouse.DeltaLake.Read.UnreadableFeature](#rqsrs-050clickhousedeltalakereadunreadablefeature)
    * 7.15 [RQ.SRS-050.ClickHouse.DeltaLake.Read.VacuumProtocolCheck](#rqsrs-050clickhousedeltalakereadvacuumprotocolcheck)
    * 7.16 [RQ.SRS-050.ClickHouse.DeltaLake.Read.VirtualColumns](#rqsrs-050clickhousedeltalakereadvirtualcolumns)
    * 7.17 [RQ.SRS-050.ClickHouse.DeltaLake.Read.Prewhere](#rqsrs-050clickhousedeltalakereadprewhere)
* 8 [Unity Catalog database](#unity-catalog-database)
    * 8.1 [RQ.SRS-050.ClickHouse.DeltaLake.Unity.Enable](#rqsrs-050clickhousedeltalakeunityenable)
    * 8.2 [RQ.SRS-050.ClickHouse.DeltaLake.Unity.CreateDatabase](#rqsrs-050clickhousedeltalakeunitycreatedatabase)
    * 8.3 [RQ.SRS-050.ClickHouse.DeltaLake.Unity.DeltaTable](#rqsrs-050clickhousedeltalakeunitydeltatable)
    * 8.4 [RQ.SRS-050.ClickHouse.DeltaLake.Unity.V2](#rqsrs-050clickhousedeltalakeunityv2)
    * 8.5 [RQ.SRS-050.ClickHouse.DeltaLake.Unity.Names](#rqsrs-050clickhousedeltalakeunitynames)
    * 8.6 [RQ.SRS-050.ClickHouse.DeltaLake.Unity.Show](#rqsrs-050clickhousedeltalakeunityshow)
    * 8.7 [RQ.SRS-050.ClickHouse.DeltaLake.Unity.Credentials](#rqsrs-050clickhousedeltalakeunitycredentials)
    * 8.8 [RQ.SRS-050.ClickHouse.DeltaLake.Unity.StorageKeys](#rqsrs-050clickhousedeltalakeunitystoragekeys)
    * 8.9 [RQ.SRS-050.ClickHouse.DeltaLake.Unity.VendedCredentials](#rqsrs-050clickhousedeltalakeunityvendedcredentials)
    * 8.10 [RQ.SRS-050.ClickHouse.DeltaLake.Unity.ManagedStorage](#rqsrs-050clickhousedeltalakeunitymanagedstorage)
    * 8.11 [RQ.SRS-050.ClickHouse.DeltaLake.Unity.Check](#rqsrs-050clickhousedeltalakeunitycheck)
    * 8.12 [RQ.SRS-050.ClickHouse.DeltaLake.Unity.SystemTables](#rqsrs-050clickhousedeltalakeunitysystemtables)
    * 8.13 [RQ.SRS-050.ClickHouse.DeltaLake.Unity.Insert](#rqsrs-050clickhousedeltalakeunityinsert)
* 9 [Writes](#writes)
    * 9.1 [RQ.SRS-050.ClickHouse.DeltaLake.Writes.Setting](#rqsrs-050clickhousedeltalakewritessetting)
    * 9.2 [RQ.SRS-050.ClickHouse.DeltaLake.Writes.Insert](#rqsrs-050clickhousedeltalakewritesinsert)
    * 9.3 [RQ.SRS-050.ClickHouse.DeltaLake.Writes.AppendVisible](#rqsrs-050clickhousedeltalakewritesappendvisible)
    * 9.4 [RQ.SRS-050.ClickHouse.DeltaLake.Writes.Commit](#rqsrs-050clickhousedeltalakewritescommit)
    * 9.5 [RQ.SRS-050.ClickHouse.DeltaLake.Writes.WriterProtocol](#rqsrs-050clickhousedeltalakewriteswriterprotocol)
    * 9.6 [RQ.SRS-050.ClickHouse.DeltaLake.Writes.DomainMetadata](#rqsrs-050clickhousedeltalakewritesdomainmetadata)
    * 9.7 [RQ.SRS-050.ClickHouse.DeltaLake.Writes.RowTracking](#rqsrs-050clickhousedeltalakewritesrowtracking)
    * 9.8 [RQ.SRS-050.ClickHouse.DeltaLake.Writes.ChangeFeed](#rqsrs-050clickhousedeltalakewriteschangefeed)
    * 9.9 [RQ.SRS-050.ClickHouse.DeltaLake.Writes.Backends](#rqsrs-050clickhousedeltalakewritesbackends)
    * 9.10 [RQ.SRS-050.ClickHouse.DeltaLake.Writes.AzureIdentity](#rqsrs-050clickhousedeltalakewritesazureidentity)
    * 9.11 [RQ.SRS-050.ClickHouse.DeltaLake.Writes.FileSize](#rqsrs-050clickhousedeltalakewritesfilesize)
    * 9.12 [RQ.SRS-050.ClickHouse.DeltaLake.Writes.Cast](#rqsrs-050clickhousedeltalakewritescast)
    * 9.13 [RQ.SRS-050.ClickHouse.DeltaLake.Writes.NoMutation](#rqsrs-050clickhousedeltalakewritesnomutation)
    * 9.14 [RQ.SRS-050.ClickHouse.DeltaLake.Writes.AppendOnly](#rqsrs-050clickhousedeltalakewritesappendonly)
* 10 [Cache and diagnostics](#cache-and-diagnostics)
    * 10.1 [RQ.SRS-050.ClickHouse.DeltaLake.Cache.Data](#rqsrs-050clickhousedeltalakecachedata)
    * 10.2 [RQ.SRS-050.ClickHouse.DeltaLake.MetadataLog](#rqsrs-050clickhousedeltalakemetadatalog)
* 11 [References](#references)

## Introduction

This document specifies how [ClickHouse] reads and writes [Delta Lake] tables. It covers the `deltaLake` table function, the `DeltaLake` table engine, cluster reads, and Delta tables reached through a [Unity Catalog] database. The `delta_lake` suite verifies these requirements.

ClickHouse 22.11 added Delta Lake reads: the `DeltaLake` table engine and the `deltaLake` table function, both read-only and limited to tables on S3. Later versions added the [Delta Kernel](#delta-kernel), writes, Azure and GCS, and Unity Catalog. `use_unity_catalog_v2` arrived in 26.10. The suite skips older servers because its scenarios open the catalog with that setting. A requirement that names an earlier version applies from that version on. Where a setting was renamed, the requirement uses the current name and records the previous one.

A few ClickHouse pages disagree. This specification follows the page that describes the operation:

* Creating a table follows the [DeltaLake engine reference](https://clickhouse.com/docs/reference/engines/table-engines/integrations/deltalake). `allow_delta_lake_create_table = 1` creates a table at an empty location. The [support matrix](https://clickhouse.com/docs/guides/use-cases/data-warehousing/support-matrix) still says an empty table cannot be created.
* Azure reads and writes follow the engine reference and the support matrix. Kernel reads on Azure Blob Storage start in 26.4. Writes start in 26.9. The [best-practices guide](https://clickhouse.com/docs/guides/use-cases/data-warehousing/getting-started/best-practices) still tells you to use the legacy Azure reader.
* The Unity database gate is `allow_database_unity_catalog`, as in the [DataLakeCatalog reference](https://clickhouse.com/docs/reference/engines/database-engines/datalake) and in this suite. The Unity guide still shows the older name `allow_experimental_database_unity_catalog`.
* A `gs://` table URL follows the engine argument list, which says that form is converted to `https://storage.googleapis.com/...`. A note on the same page still says a gsutil URI is not supported.

ClickHouse does not copy the table into a local MergeTree. A query reads the Parquet files named by the snapshot.

ClickHouse is a Delta client. A read or a write is correct when it matches the [Delta Transaction Log Protocol](https://github.com/delta-io/delta/blob/master/PROTOCOL.md#delta-table-specification). [Log protocol](#log-protocol) records every rule in that specification that changes the rows ClickHouse returns or the commit it is allowed to write. A reader feature ClickHouse does not implement fails the query. A writer feature ClickHouse cannot honor fails the insert. `DROP TABLE` of a Delta table in Unity Catalog is outside this specification.


## Terminology

### Delta Lake

[Delta Lake](https://delta.io/) is an open table format. A table is a directory of Parquet data files plus a transaction log. Readers reconstruct a snapshot from that log instead of listing every file under the directory.

### Delta log

The Delta log is the `_delta_log` directory in the table root. Each commit is a JSON file, `00000000000000000000.json` and so on. A checkpoint, when present, is a Parquet summary of the actions a reader needs to build a snapshot.

### Snapshot

A snapshot is one committed version of the table. Version 0 is the first commit. The latest version is the highest committed version. A query reads one snapshot. It does not mix files from two commits.

### Unity Catalog

[Unity Catalog](https://www.databricks.com/product/unity-catalog) is the Databricks catalog for tables, schemas, and storage locations. ClickHouse attaches it with the `DataLakeCatalog` database engine and `catalog_type = 'unity'`. The OSS server used by this suite speaks the Unity REST API at `/api/2.1/unity-catalog`. A Delta table is registered there with `data_source_format = DELTA` and a storage location that contains a [Delta log](#delta-log).

### Delta Kernel

The Delta Kernel is the Rust library `delta-kernel-rs`. From ClickHouse 25.6, reads of Delta tables on S3 and GCS go through this library. The setting is `allow_delta_kernel_rs` on 26.8 and newer, and `allow_experimental_delta_kernel_rs` on 25.5 through 26.7. It is on by default for S3 and GCS. Partition pruning, change data feed, snapshot reads, and writes all require it.


## Log protocol

These requirements are the parts of the [Delta table specification](https://github.com/delta-io/delta/blob/master/PROTOCOL.md#delta-table-specification) that a ClickHouse read or write has to follow. They apply to the table function, the table engine, and a Delta table opened through Unity Catalog.

### RQ.SRS-050.ClickHouse.DeltaLake.Protocol.Replay
version: 1.0

[ClickHouse] SHALL build a snapshot by replaying commits in ascending version order. A checkpoint MAY stand in for the commits up to and including its version. The checkpoint SHALL NOT be newer than the version being read.

The latest `protocol` action wins. The latest `metaData` action wins and replaces the metadata that came before it. Live data is the `add` actions that remain after [action reconciliation](https://github.com/delta-io/delta/blob/master/PROTOCOL.md#action-reconciliation). A `remove` tombstone SHALL contribute no rows. The same logical file, identified by `(path, deletion vector)`, SHALL NOT be both live and removed in one snapshot.

`commitInfo` and `txn` actions SHALL NOT change the rows of a `SELECT`. [ClickHouse] SHALL ignore a `domainMetadata` action it does not understand and still return the table rows.

### RQ.SRS-050.ClickHouse.DeltaLake.Protocol.Paths
version: 1.0

[ClickHouse] SHALL URI-decode `add.path` and `remove.path`. A relative path is relative to the table root. An absolute path SHALL be read as that URI.

Partition values SHALL come from `partitionValues` on the `add` action. Directory names such as `date=2017-12-10/` SHALL NOT override the log.

### RQ.SRS-050.ClickHouse.DeltaLake.Protocol.Format
version: 1.0

[ClickHouse] SHALL read a table whose `metaData.format.provider` is `parquet`. Any other provider SHALL fail the query. [ClickHouse] SHALL NOT scan those files as Parquet.

Data files MAY use Data page V1 or Data page V2. [ClickHouse] SHALL return the same rows for both. The table property `delta.parquet.format.version` is a writer hint and SHALL NOT change which pages a read accepts.

### RQ.SRS-050.ClickHouse.DeltaLake.Protocol.DataChange
version: 1.0

A commit whose `add` and `remove` actions set `dataChange` to `false` only rearranges rows that are already in the table, or replaces statistics. A `SELECT` of the latest snapshot after that commit SHALL return the same logical rows as the snapshot before it.

### RQ.SRS-050.ClickHouse.DeltaLake.Protocol.UnknownFields
version: 1.0

Inside a reader protocol version [ClickHouse] implements, an unrecognized JSON field on a known action SHALL be ignored. The rows SHALL still match the snapshot.

An unknown action name SHALL be ignored when the protocol version does not require it. A name listed in `readerFeatures` is not an unknown field. See [RQ.SRS-050.ClickHouse.DeltaLake.Protocol.Version](#rqsrs-050clickhousedeltalakeprotocolversion).

### RQ.SRS-050.ClickHouse.DeltaLake.Protocol.Version
version: 1.0

[ClickHouse] SHALL enforce `minReaderVersion` and `readerFeatures` before it returns rows.

| Reader version | What the read must honor |
|---|---|
| 1 | The baseline log, schema, and `add` / `remove` actions |
| 2 | Column mapping, as in [RQ.SRS-050.ClickHouse.DeltaLake.Read.ColumnMapping](#rqsrs-050clickhousedeltalakereadcolumnmapping) |
| 3 | Every name in `readerFeatures`. The table's writer version is 7 |

A `minReaderVersion` above 3 SHALL fail the query. A name in `readerFeatures` that this specification does not require [ClickHouse] to apply SHALL fail the query. The failure is [RQ.SRS-050.ClickHouse.DeltaLake.Read.UnreadableFeature](#rqsrs-050clickhousedeltalakereadunreadablefeature). `vacuumProtocolCheck` is not such a name. See [RQ.SRS-050.ClickHouse.DeltaLake.Read.VacuumProtocolCheck](#rqsrs-050clickhousedeltalakereadvacuumprotocolcheck).

Before an `INSERT`, [ClickHouse] SHALL also enforce `minWriterVersion` and every name in `writerFeatures`. A writer protocol it cannot honor SHALL fail the insert. See [RQ.SRS-050.ClickHouse.DeltaLake.Writes.WriterProtocol](#rqsrs-050clickhousedeltalakewriteswriterprotocol).

### RQ.SRS-050.ClickHouse.DeltaLake.Protocol.CatalogManaged
version: 1.0

When `catalogManaged` is in `readerFeatures`, the catalog is the source of truth for which commits are ratified. [ClickHouse] SHALL NOT build that snapshot by listing `_delta_log` alone. A file under `_delta_log/_staged_commits` SHALL NOT count as a commit unless the catalog has ratified it. A published log file newer than the latest ratified version SHALL be ignored.

[ClickHouse] does not implement this commit protocol. The read SHALL fail closed, as in [RQ.SRS-050.ClickHouse.DeltaLake.Read.UnreadableFeature](#rqsrs-050clickhousedeltalakereadunreadablefeature). An external Delta table registered in Unity with an ordinary `_delta_log`, and no `catalogManaged` feature, stays on [RQ.SRS-050.ClickHouse.DeltaLake.Protocol.Replay](#rqsrs-050clickhousedeltalakeprotocolreplay).

### RQ.SRS-050.ClickHouse.DeltaLake.Protocol.Statistics
version: 1.0

`stats` on an `add` action are optional. [ClickHouse] MAY skip a file whose min and max exclude a filter. It SHALL NOT skip a file that contains a matching row. A file with no `stats` SHALL remain a candidate for that filter.

Partition columns are not skipped from these stats. Their values come from `partitionValues`. See [RQ.SRS-050.ClickHouse.DeltaLake.Read.PartitionPruning](#rqsrs-050clickhousedeltalakereadpartitionpruning).


## Access

ClickHouse exposes a Delta table in three ways: a table function for one query, a table engine for a stored definition, and a [Unity Catalog](#unity-catalog) database when the table is registered in a catalog. Cluster functions distribute the file reads across a ClickHouse cluster.

### Table function

#### RQ.SRS-050.ClickHouse.DeltaLake.Access.TableFunction
version: 1.0

[ClickHouse] SHALL read a Delta table through the `deltaLake` table function. The function returns the columns of the snapshot. Callers MAY omit `format`, `structure`, and `compression`. [ClickHouse] SHALL take the schema from the [Delta log](#delta-log).

```sql
SELECT *
FROM deltaLake('https://clickhouse-public-datasets.s3.amazonaws.com/delta_lake/hits/')
LIMIT 2
```

A path that has no `_delta_log` SHALL fail the query. [ClickHouse] SHALL NOT treat that path as a plain Parquet directory.

#### RQ.SRS-050.ClickHouse.DeltaLake.Access.TableFunction.Backends
version: 1.0

[ClickHouse] SHALL read a Delta table from the backends below. `deltaLake` is an alias of `deltaLakeS3`. HDFS is not a backend.

| Backend | Function | Where it runs |
|---|---|---|
| Amazon S3, and S3-compatible storage such as RustFS | `deltaLake` / `deltaLakeS3` | Cloud and self-managed |
| Google Cloud Storage | `deltaLake` / `deltaLakeS3` with an `https://storage.googleapis.com/...` URL | Cloud and self-managed |
| Azure Blob Storage | `deltaLakeAzure` | Cloud and self-managed. Kernel reads from 26.4 |
| Local disk | `deltaLakeLocal` | Self-managed only |

```sql
deltaLake(url [, aws_access_key_id, aws_secret_access_key] [, format] [, structure] [, compression] [, extra_credentials])

deltaLakeS3(url [, aws_access_key_id, aws_secret_access_key] [, format] [, structure] [, compression] [, extra_credentials])

deltaLakeAzure(connection_string | storage_account_url, container_name, blobpath [, account_name] [, account_key] [, format] [, compression_method])

deltaLakeLocal(path [, format])
```

A GCS URL written as `gs://bucket/path` SHALL be accepted and read as the same object as `https://storage.googleapis.com/bucket/path`.

`deltaLakeLocal` SHALL read a table from a path on the server's local disk. ClickHouse Cloud does not provide this function.

Data files in a snapshot MAY use the Parquet codecs the Delta protocol requires readers to accept: uncompressed, `snappy`, `gzip`, `lz4`, `lz4_raw`, and `zstd`. [ClickHouse] SHALL return the same rows for each of those codecs. A mix of those codecs in one table SHALL still return every live row.

### Cluster function

#### RQ.SRS-050.ClickHouse.DeltaLake.Access.Cluster
version: 1.0

[ClickHouse] SHALL distribute reads of a Delta table across the nodes of a named cluster. The initiator assigns data files to workers. A worker asks the initiator for the next file until the snapshot is exhausted.

`deltaLakeS3Cluster` is an alias of `deltaLakeCluster`. Both read S3 and GCS. `deltaLakeAzureCluster` reads Azure Blob Storage.

```sql
deltaLakeCluster(cluster_name, url [, aws_access_key_id, aws_secret_access_key] [, format] [, structure] [, compression] [, extra_credentials])

deltaLakeS3Cluster(cluster_name, url [, aws_access_key_id, aws_secret_access_key] [, format] [, structure] [, compression] [, extra_credentials])

deltaLakeAzureCluster(cluster_name, connection_string | storage_account_url, container_name, blobpath [, account_name] [, account_key] [, format] [, compression_method])
```

For one snapshot, `deltaLakeCluster` and `deltaLakeAzureCluster` SHALL return the same rows as `deltaLake` and `deltaLakeAzure` on a single node. The cluster functions accept a named collection in place of the inline arguments.

### Table engine

#### RQ.SRS-050.ClickHouse.DeltaLake.Access.Engine
version: 1.0

[ClickHouse] SHALL attach a stored table to an existing Delta location with `ENGINE = DeltaLake`. The engine reads and, when writes are enabled, writes the same snapshots as the table function for that location. Column definitions are omitted when the table already exists. The schema comes from the log.

```sql
CREATE TABLE events
ENGINE = DeltaLake('https://bucket.s3.amazonaws.com/warehouse/events/', 'key', 'secret')
```

S3 and GCS use the URL form. GCS uses an `https://storage.googleapis.com/...` URL, and a `gs://` URL is accepted as in [RQ.SRS-050.ClickHouse.DeltaLake.Access.TableFunction.Backends](#rqsrs-050clickhousedeltalakeaccesstablefunctionbackends). Azure uses the account URL or a connection string, a container, and a blob path:

```sql
CREATE TABLE events
ENGINE = DeltaLake('https://account.blob.core.windows.net', 'container', 'path/to/table')
```

#### RQ.SRS-050.ClickHouse.DeltaLake.Access.NamedCollection
version: 1.0

On self-managed [ClickHouse], a named collection SHALL supply the engine or table-function arguments.

```sql
CREATE NAMED COLLECTION delta_conf AS
    url = 'https://bucket.s3.amazonaws.com/warehouse/events/',
    access_key_id = 'key',
    secret_access_key = 'secret';

CREATE TABLE events
ENGINE = DeltaLake(delta_conf);
```

The same collection SHALL work as the argument of `deltaLake` and `deltaLakeCluster`.

#### RQ.SRS-050.ClickHouse.DeltaLake.Access.Credentials
version: 1.0

[ClickHouse] SHALL authenticate to object storage with the keys passed to the engine or function. When those arguments are omitted, [ClickHouse] SHALL use the credentials from the server configuration.

An optional `extra_credentials` argument SHALL pass a `role_arn`. [ClickHouse] SHALL assume that role for the request. On Azure, `extra_credentials(client_id = ..., tenant_id = ...)` is workload-identity authentication. Writes through the Delta Kernel do not accept that form. See [RQ.SRS-050.ClickHouse.DeltaLake.Writes.AzureIdentity](#rqsrs-050clickhousedeltalakewritesazureidentity).


## Creating a table

By default, `CREATE TABLE ... ENGINE = DeltaLake` attaches to a table that already has a [Delta log](#delta-log). Creating a new log is a separate, disabled-by-default path.

### RQ.SRS-050.ClickHouse.DeltaLake.Create.AttachExisting
version: 1.0

`CREATE TABLE ... ENGINE = DeltaLake` without column definitions SHALL attach to a location that already contains `_delta_log`. `SHOW CREATE TABLE` SHALL list the columns of the latest snapshot and `ENGINE = DeltaLake` with that location.

A location with no `_delta_log` SHALL fail this statement when `allow_delta_lake_create_table` is off. The statement SHALL leave the location unchanged.

### RQ.SRS-050.ClickHouse.DeltaLake.Create.NewTable
version: 1.0

With `allow_delta_lake_create_table = 1`, `CREATE TABLE` with an explicit column list SHALL create a Delta table at a location that has no `_delta_log`. [ClickHouse] SHALL write the initial commit through the [Delta Kernel](#delta-kernel). A following `SELECT` SHALL return zero rows, and the column names and types SHALL match the `CREATE TABLE` list under the mapping in [Schema](#schema).

```sql
SET allow_delta_lake_create_table = 1;

CREATE TABLE people
(
    id Int64,
    name String
)
ENGINE = DeltaLake('https://bucket.s3.amazonaws.com/warehouse/people/', 'key', 'secret');
```

The new `_delta_log` SHALL be a valid Delta table that an external Delta reader can open.

### RQ.SRS-050.ClickHouse.DeltaLake.Create.NoPartition
version: 1.0

`CREATE TABLE ... ENGINE = DeltaLake` SHALL reject a partition clause. [ClickHouse] SHALL NOT write a partitioned `_delta_log` for that statement.

```sql
SET allow_delta_lake_create_table = 1;

CREATE TABLE events
(
    id Int64,
    day Date
)
ENGINE = DeltaLake('https://bucket.s3.amazonaws.com/warehouse/events/', 'key', 'secret')
PARTITION BY day;
```

Reading a partitioned table that an external writer created is a separate requirement. See [RQ.SRS-050.ClickHouse.DeltaLake.Read.PartitionPruning](#rqsrs-050clickhousedeltalakereadpartitionpruning).

### RQ.SRS-050.ClickHouse.DeltaLake.Create.RegisterInUnity
version: 1.0

When [RQ.SRS-050.ClickHouse.DeltaLake.Create.NewTable](#rqsrs-050clickhousedeltalakecreatenewtable) runs inside a Unity `DataLakeCatalog` database, [ClickHouse] SHALL also register the table in the catalog. `SHOW TABLES` on that database SHALL list it, and `SHOW CREATE TABLE` SHALL show `ENGINE = DeltaLake` at the new location.

```sql
SET allow_database_unity_catalog = 1;
SET allow_delta_lake_create_table = 1;

CREATE TABLE unity.`schema.people`
(
    id Int64,
    name String
)
ENGINE = DeltaLake('https://bucket.s3.amazonaws.com/warehouse/schema/people/', 'key', 'secret');
```


## Schema

[ClickHouse] builds the read schema from the snapshot metadata. The mapping below is what `SHOW CREATE TABLE` and `DESCRIBE` report. Nullable struct fields become `Nullable(...)`.

### RQ.SRS-050.ClickHouse.DeltaLake.Schema.PrimitiveTypes
version: 1.0

[ClickHouse] SHALL map Delta primitive types as follows.

| Delta type | ClickHouse type |
|---|---|
| `string` | `String` |
| `binary` | `String` |
| `long` | `Int64` |
| `integer` | `Int32` |
| `short` | `Int16` |
| `byte` | `Int8` |
| `float` | `Float32` |
| `double` | `Float64` |
| `boolean` | `Bool` |
| `date` | `Date32` |
| `timestamp` | `DateTime64(6)` |
| `timestamp_ntz` | `DateTime64(6)` |

`timestamp` values SHALL be the UTC instants stored in the table, at microsecond precision. `timestamp_ntz` SHALL return the same civil time that was written, at microsecond precision, on a table that enables the `timestampNtz` reader feature. `date` SHALL return the calendar date written in the file.

A `SELECT` of each column SHALL return the values an external Delta writer committed, including the minimum and maximum of each integer type.

### RQ.SRS-050.ClickHouse.DeltaLake.Schema.Decimal
version: 1.0

[ClickHouse] SHALL map `decimal(p, s)` to `Decimal(p, s)` for a precision `p` from 1 to 38 and a scale `s` from 0 to `p`. The values SHALL match the decimal values written to the table.

### RQ.SRS-050.ClickHouse.DeltaLake.Schema.Varchar
version: 1.0

[ClickHouse] SHALL map `varchar(n)` and `char(n)` to `String`. Unity Catalog returns those names in `type_json` for columns whose Delta log type is `string`. The length SHALL NOT change the values [ClickHouse] returns.

### RQ.SRS-050.ClickHouse.DeltaLake.Schema.Nested
version: 1.0

[ClickHouse] SHALL map Delta nested types as follows.

| Delta type | ClickHouse type |
|---|---|
| `struct` | `Tuple` with the struct field names |
| `array` | `Array` |
| `map` | `Map` |

An array element SHALL be `Nullable` when `containsNull` is true. A map value SHALL be `Nullable` when `valueContainsNull` is true. Map keys SHALL NOT be nullable. Nested structs, arrays, and maps SHALL keep their field names and nullability at every level.

### RQ.SRS-050.ClickHouse.DeltaLake.Schema.Nulls
version: 1.0

A column whose Delta field is `nullable` SHALL be `Nullable(...)`. `SELECT` SHALL return `NULL` for a null value in the data file. A column that the snapshot schema contains and a data file does not SHALL be read as `NULL` for every row of that file.

### RQ.SRS-050.ClickHouse.DeltaLake.Schema.Void
version: 1.0

A top-level `void` column SHALL be read as an all-`NULL` column. The data file does not store that column. [ClickHouse] SHALL still list it in the schema of the snapshot.

An `INSERT` SHALL fail when the table schema has a `void` type inside an array or a map, a struct whose fields are all `void`, or only `void` columns. The failed insert SHALL NOT write a data file.

### RQ.SRS-050.ClickHouse.DeltaLake.Schema.PartitionColumns
version: 1.0

[ClickHouse] SHALL return partition columns as ordinary columns of the snapshot schema. The values SHALL come from the partition values recorded in the log for each file, including when those columns are absent from the Parquet file.

[ClickHouse] SHALL parse the Delta partition serialization:

| Partition text | Value |
|---|---|
| empty string | `NULL` |
| `true` / `false` | `Bool` |
| decimal text of a number | that number |
| `YYYY-MM-DD` | a `date` |
| `YYYY-MM-DD hh:mm:ss` or `YYYY-MM-DD hh:mm:ss.SSSSSS` | a timestamp |
| ISO-8601 UTC, such as `1970-01-01T00:00:00.123456Z` | that UTC instant |

### RQ.SRS-050.ClickHouse.DeltaLake.Schema.Unsupported
version: 1.0

A Delta type that this specification does not map SHALL fail the query. The error SHALL name the type. [ClickHouse] SHALL NOT substitute another type and return rows.


## Reads

Reads apply to the table function, the table engine, and a Delta table opened through [Unity Catalog](#unity-catalog). A query uses every [ClickHouse] SQL function on the resulting columns.

### RQ.SRS-050.ClickHouse.DeltaLake.Read.Snapshot
version: 1.0

A query SHALL read one committed snapshot. With `delta_lake_snapshot_version` left at its default of `-1`, that snapshot is the latest commit.

Rows whose files the snapshot has removed SHALL be absent. An external `overwrite` commit SHALL make a later query return only the rows of the new snapshot. An external `append` SHALL make those rows visible in addition to the rows already committed. Every row in one result SHALL belong to that single snapshot.

A table with a schema and no data files SHALL return zero rows, and `DESCRIBE` SHALL still report the schema.

### RQ.SRS-050.ClickHouse.DeltaLake.Read.Projection
version: 1.0

A `SELECT` of a subset of columns SHALL return those columns and no others. The values SHALL match a `SELECT *` of the same snapshot.

### RQ.SRS-050.ClickHouse.DeltaLake.Read.Kernel
version: 1.0

On ClickHouse 26.8 and newer, `allow_delta_kernel_rs` enables the [Delta Kernel](#delta-kernel). On 25.5 through 26.7 the setting name is `allow_experimental_delta_kernel_rs`. The kernel is on by default for S3 and GCS. Azure Blob Storage uses it from 26.4.

Partition pruning, change data feed, and `delta_lake_snapshot_version` SHALL run only with the kernel enabled.

With the kernel disabled, a query that sets `delta_lake_snapshot_version` to a version other than `-1`, or that sets a change-data-feed range, SHALL fail. [ClickHouse] SHALL NOT answer that query with the latest snapshot. A filter on a partition column SHALL still return the correct rows. Pruning is not required while the kernel is off.

### RQ.SRS-050.ClickHouse.DeltaLake.Read.PartitionPruning
version: 1.0

With `delta_lake_enable_engine_predicate = 1` (the default since 25.8), a filter on a partition column SHALL skip data files from partitions the filter excludes. The rows [ClickHouse] returns SHALL be the rows that match the filter. `_path` for that query SHALL NOT list a file from an excluded partition.

```sql
SELECT * FROM events
WHERE day = '2026-01-01'
SETTINGS delta_lake_enable_engine_predicate = 1
```

With `delta_lake_enable_engine_predicate = 0`, the same filter SHALL return the same rows. Skipping files is not required.

`delta_lake_throw_on_engine_predicate_error` defaults to `0`. When it is `1`, a predicate the kernel cannot analyze SHALL fail the query.

### RQ.SRS-050.ClickHouse.DeltaLake.Read.SchemaEvolution
version: 1.0

[ClickHouse] SHALL read a table whose schema changed across commits, using the schema of the snapshot being scanned. Each `metaData` action replaces the metadata of the previous snapshot. This requires the [Delta Kernel](#delta-kernel).

* A column added in a later commit SHALL appear in a read of the latest snapshot. Rows from files written before that commit SHALL return `NULL` for the new column when the column is nullable.
* A column removed in a later commit SHALL be absent from a read of the latest snapshot.
* `SELECT *` and `DESCRIBE` SHALL list columns in the order of the snapshot schema after a reorder.
* A rename performed with column mapping SHALL return the original values under the new logical name. See [RQ.SRS-050.ClickHouse.DeltaLake.Read.ColumnMapping](#rqsrs-050clickhousedeltalakereadcolumnmapping).

A read of an older snapshot with `delta_lake_snapshot_version` SHALL use the schema of that snapshot.

### RQ.SRS-050.ClickHouse.DeltaLake.Read.TypeWidening
version: 1.0

When `typeWidening` is in `readerFeatures`, [ClickHouse] SHALL read a value written before a supported type change as the current, wider type. It SHALL check every type change recorded in `delta.typeChanges` for the snapshot it is reading.

A type change [ClickHouse] does not support SHALL fail the query. [ClickHouse] SHALL NOT return the pre-widening type for a row written after the change. When [ClickHouse] does not implement `typeWidening` at all, the query SHALL fail closed under [RQ.SRS-050.ClickHouse.DeltaLake.Read.UnreadableFeature](#rqsrs-050clickhousedeltalakereadunreadablefeature).

### RQ.SRS-050.ClickHouse.DeltaLake.Read.SchemaReload
version: 1.0

`delta_lake_reload_schema_for_consistency` defaults to `0`. When it is `1`, [ClickHouse] SHALL reload the schema from the [Delta log](#delta-log) before executing the query, so the schema used for analysis and the schema used for execution are the same snapshot. A commit that adds or drops a column after analysis and before execution SHALL be reflected in the result.

### RQ.SRS-050.ClickHouse.DeltaLake.Read.ColumnMapping
version: 1.0

[ClickHouse] SHALL read tables with `delta.columnMapping.mode` set to `none`, `name`, or `id`. The property applies when the reader version is 2, or when the reader version is 3 and `columnMapping` is in `readerFeatures`.

`SELECT` and `DESCRIBE` SHALL use the logical column names from the snapshot schema. Physical Parquet names SHALL NOT be the names [ClickHouse] exposes.

* In `none` mode, and when the property is absent, [ClickHouse] SHALL read Parquet columns by the logical name.
* In `name` mode, [ClickHouse] SHALL resolve data columns, partition values, and column statistics by `delta.columnMapping.physicalName`. A column missing from a file SHALL be `NULL`.
* In `id` mode, [ClickHouse] SHALL resolve data columns by the Parquet field id `delta.columnMapping.id`. Partition values and column statistics SHALL be resolved by the physical name. A file with no field ids SHALL fail that file or return `NULL` for each column. An id missing from a file SHALL be `NULL`.

After a rename in `name` or `id` mode, a query of the latest snapshot SHALL return the column under its new logical name and SHALL return the values written under the old name. Nested struct fields, and fields reached through `element`, `key`, or `value`, SHALL follow the same mapping.

### RQ.SRS-050.ClickHouse.DeltaLake.Read.DeletionVectors
version: 1.0

ClickHouse 26.1 added deletion-vector reads for the `DeltaLake` table engine and for `deltaLakeCluster`. The Cloud release notes for February 2026 list the same change. From 26.1, those entry points SHALL omit every row whose index is set in the deletion vector of a data file. `deltaLake` and a Delta table opened through Unity Catalog SHALL do the same. This holds when `delta.enableDeletionVectors` is absent. A following `count()` SHALL equal the number of live rows in the snapshot. `deltaLakeCluster` SHALL return the same live rows as `deltaLake` for that snapshot.

The `storageType` of the vector SHALL be one of `u` (UUID path under the table), `i` (inline in the log), or `p` (absolute path). Any other `storageType` SHALL fail the query. [ClickHouse] SHALL NOT return the invalidated rows.

A file removed by a `remove` action, with or without a deletion vector, SHALL contribute no rows.

### RQ.SRS-050.ClickHouse.DeltaLake.Read.TimeTravel
version: 1.0

`delta_lake_snapshot_version` SHALL select the snapshot to read. The default is `-1`, which means the latest snapshot. Version `0` is the first commit and SHALL be accepted.

```sql
SELECT * FROM events
SETTINGS delta_lake_snapshot_version = 0
```

The rows SHALL be the rows of that snapshot, under that snapshot's schema. A version that does not exist SHALL fail the query. [ClickHouse] SHALL NOT substitute the latest snapshot.

This requires the [Delta Kernel](#delta-kernel) and has been available since 25.8.

### RQ.SRS-050.ClickHouse.DeltaLake.Read.ChangeDataFeed
version: 1.0

On a table whose property `delta.enableChangeDataFeed` is `true`, [ClickHouse] SHALL return the changes between two snapshot versions. Set both bounds. This requires the [Delta Kernel](#delta-kernel) and has been available since 25.12.

```sql
SELECT *
FROM deltaLake('s3://bucket/warehouse/events/', 'key', 'secret')
SETTINGS
    delta_lake_snapshot_start_version = 1,
    delta_lake_snapshot_end_version = 3
```

The result SHALL include the table columns and the change columns `_change_type`, `_commit_version`, and `_commit_timestamp`. `_change_type` SHALL use the Delta values `insert`, `delete`, `update_preimage`, and `update_postimage` for the corresponding commits. `_commit_version` SHALL be the commit that produced the change and SHALL lie in the requested range.

For each version in the range, [ClickHouse] SHALL follow the protocol's change-data rule. When that version has `cdc` actions, the change rows SHALL come only from those files, and the `add` and `remove` actions of that version SHALL be skipped. When that version has no `cdc` action, rows in `add` actions SHALL be `insert` and rows in `remove` actions SHALL be `delete`. An `INSERT` that only adds files is this second case. See [RQ.SRS-050.ClickHouse.DeltaLake.Writes.ChangeFeed](#rqsrs-050clickhousedeltalakewriteschangefeed).

When `inCommitTimestamp` is enabled, `_commit_timestamp` SHALL be the `inCommitTimestamp` of that version's `commitInfo`. Otherwise it SHALL be the modification time of that version's log file.

A `SELECT` that is not a change-data read SHALL ignore a `_change_type` column stored in a data file and absent from the table schema.

Setting only `delta_lake_snapshot_end_version`, and leaving `delta_lake_snapshot_start_version` at `-1`, SHALL fail the query. A range on a table that does not have change data feed enabled SHALL fail the query. [ClickHouse] SHALL NOT return the latest snapshot in either case.

### RQ.SRS-050.ClickHouse.DeltaLake.Read.Checkpoint
version: 1.0

[ClickHouse] SHALL read a snapshot whose actions are summarized in a classic Parquet checkpoint, `{version}.checkpoint.parquet`, under `_delta_log`. The rows SHALL match the rows of the same snapshot read from the JSON commits alone.

A multi-part checkpoint, `{version}.checkpoint.{part}.{total}.parquet`, SHALL be used only when every part is present. A missing part SHALL be ignored, and the snapshot SHALL still come from the JSON log and any older complete checkpoint.

`_delta_log/_last_checkpoint` is a hint. A missing or stale hint SHALL still produce the latest snapshot. A log-compaction file `{start}.{end}.compacted.json` MAY replace the commits in that closed range and SHALL produce the same snapshot as those commits. A missing `{version}.crc` file SHALL NOT fail the read.

A time-travel read SHALL NOT apply a checkpoint newer than `delta_lake_snapshot_version`. UUID-named v2 checkpoints are [RQ.SRS-050.ClickHouse.DeltaLake.Read.UnreadableFeature](#rqsrs-050clickhousedeltalakereadunreadablefeature) when [ClickHouse] does not implement `v2Checkpoint`.

### RQ.SRS-050.ClickHouse.DeltaLake.Read.WriterFeatures
version: 1.0

A writer-only table feature SHALL NOT stop a read of the committed data, and SHALL NOT change the stored values [ClickHouse] returns. The feature names are `appendOnly`, `invariants`, `checkConstraints`, `generatedColumns`, `changeDataFeed`, `identityColumns`, `allowColumnDefaults`, `domainMetadata`, `inCommitTimestamp`, `clustering`, `icebergCompatV1`, `icebergCompatV2`, `materializePartitionColumns`, and `rowTracking`.

[ClickHouse] returns the values stored in the data files and the partition values in the log. It does not evaluate generated-column expressions, identity generators, or `CHECK` expressions on read. Hidden row-tracking columns SHALL NOT appear in the table schema. A `SELECT` of the schema columns SHALL still return the stored rows when row tracking is enabled.

### RQ.SRS-050.ClickHouse.DeltaLake.Read.UnreadableFeature
version: 1.0

When a snapshot needs a reader feature that [ClickHouse] cannot apply, the query SHALL fail. [ClickHouse] SHALL NOT return rows that ignore that feature. A deletion vector [ClickHouse] cannot decode, and a column-mapping mode other than `none`, `name`, or `id`, are two such cases.

[ClickHouse] is not required to implement `variant`, variant shredding, `typeWidening`, `v2Checkpoint`, or `catalogManaged`. A snapshot that needs one of those features for a correct result SHALL fail when [ClickHouse] does not implement it. A successful read is valid when the server does implement it. `typeWidening`, when implemented, follows [RQ.SRS-050.ClickHouse.DeltaLake.Read.TypeWidening](#rqsrs-050clickhousedeltalakereadtypewidening). `catalogManaged`, when not implemented, follows [RQ.SRS-050.ClickHouse.DeltaLake.Protocol.CatalogManaged](#rqsrs-050clickhousedeltalakeprotocolcatalogmanaged).

### RQ.SRS-050.ClickHouse.DeltaLake.Read.VacuumProtocolCheck
version: 1.0

`vacuumProtocolCheck` in `readerFeatures` SHALL NOT change a `SELECT`. The query SHALL return the same rows as a table with the same files and no such feature. [ClickHouse] does not implement `VACUUM`. This requirement is the protocol's reader rule: acknowledge the feature, and leave the scan unchanged.

### RQ.SRS-050.ClickHouse.DeltaLake.Read.VirtualColumns
version: 1.0

A Delta read SHALL expose these virtual columns. They describe the data file of each row.

| Column | Type | Value |
|---|---|---|
| `_path` | `LowCardinality(String)` | Path of the file |
| `_file` | `LowCardinality(String)` | Name of the file |
| `_size` | `Nullable(UInt64)` | Size in bytes, or `NULL` when the size is unknown |
| `_time` | `Nullable(DateTime)` | Last modified time, or `NULL` when the time is unknown |
| `_etag` | `LowCardinality(String)` | ETag of the file. `NULL` when the ETag is unknown |

The table function, the cluster function, and the table engine SHALL all expose these columns.

### RQ.SRS-050.ClickHouse.DeltaLake.Read.Prewhere
version: 1.0

From ClickHouse 26.2, `PREWHERE` on a Delta read SHALL filter rows before the remaining columns are read. The rows SHALL match the same predicate written in `WHERE`. Partition pruning still depends on a filter of the partition columns, as in [RQ.SRS-050.ClickHouse.DeltaLake.Read.PartitionPruning](#rqsrs-050clickhousedeltalakereadpartitionpruning).


## Unity Catalog database

A `DataLakeCatalog` database with `catalog_type = 'unity'` lists the tables of one Unity catalog. Delta tables in that catalog are `DeltaLake` tables. The `delta_lake` suite registers those tables in a local Unity REST server and reads them through this database.

### RQ.SRS-050.ClickHouse.DeltaLake.Unity.Enable
version: 1.0

[ClickHouse] SHALL require `allow_database_unity_catalog = 1` before `CREATE DATABASE ... ENGINE = DataLakeCatalog` with `catalog_type = 'unity'`. With the setting off, the statement SHALL fail.

```sql
SET allow_database_unity_catalog = 1;
```

### RQ.SRS-050.ClickHouse.DeltaLake.Unity.CreateDatabase
version: 1.0

[ClickHouse] SHALL create a database over the Unity REST API. `warehouse` is the catalog name. `use_unity_catalog_v2` defaults to `false` and MAY be changed later with `ALTER DATABASE ... MODIFY SETTING`.

```sql
CREATE DATABASE unity
ENGINE = DataLakeCatalog('https://<workspace>.cloud.databricks.com/api/2.1/unity-catalog')
SETTINGS
    catalog_type = 'unity',
    warehouse = 'main',
    catalog_credential = '<token>';
```

`CREATE DATABASE` SHALL succeed without contacting the catalog. A wrong token or an unreachable endpoint SHALL NOT fail this statement. [RQ.SRS-050.ClickHouse.DeltaLake.Unity.Check](#rqsrs-050clickhousedeltalakeunitycheck) is the check that contacts the catalog.

`SHOW DATABASES` SHALL list the new database.

### RQ.SRS-050.ClickHouse.DeltaLake.Unity.DeltaTable
version: 1.0

A catalog entry with `data_source_format = DELTA` SHALL be a `DeltaLake` table. `SHOW CREATE TABLE` SHALL contain `DeltaLake` and the storage location registered for that table. `SELECT` SHALL return the rows of the latest snapshot at that location, under the schema rules in [Schema](#schema).

```sql
SELECT name, value
FROM unity.`schema.table`
ORDER BY name
```

This holds for `use_unity_catalog_v2 = 0`, which is the Delta catalog.

### RQ.SRS-050.ClickHouse.DeltaLake.Unity.V2
version: 1.0

With `use_unity_catalog_v2 = 1`, [ClickHouse] SHALL serve both Delta and Iceberg tables from the same Unity database and SHALL detect the format of each table.

A table registered as Delta SHALL still use `ENGINE = DeltaLake`. `SHOW CREATE TABLE` SHALL contain `DeltaLake` and the same storage location as with `use_unity_catalog_v2 = 0`. `SELECT` SHALL return the same rows.

```sql
CREATE DATABASE unity_v2
ENGINE = DataLakeCatalog('http://unity-catalog:8080/api/2.1/unity-catalog')
SETTINGS
    catalog_type = 'unity',
    use_unity_catalog_v2 = 1,
    warehouse = 'unity',
    vended_credentials = false,
    storage_endpoint = 'http://rustfs:9000/warehouse',
    aws_access_key_id = 'key',
    aws_secret_access_key = 'secret';
```

`ALTER DATABASE unity_v2 MODIFY SETTING use_unity_catalog_v2 = 0` SHALL switch that database back to the Delta catalog. A Delta table SHALL remain readable as `DeltaLake` after the change.

### RQ.SRS-050.ClickHouse.DeltaLake.Unity.Names
version: 1.0

[ClickHouse] SHALL address a Unity table as `` `schema.table` ``, with the schema and the table name in one backtick-quoted identifier. `schema.table` without backticks SHALL NOT resolve the catalog table.

### RQ.SRS-050.ClickHouse.DeltaLake.Unity.Show
version: 1.0

For a Unity database that contains a Delta table `schema.table`:

* `SHOW TABLES FROM unity` SHALL list `schema.table`.
* `SHOW CREATE TABLE unity.\`schema.table\`` SHALL show the column list and `ENGINE = DeltaLake` with the table's storage location.
* `SHOW COLUMNS FROM unity.\`schema.table\`` SHALL show the mapped ClickHouse types from [Schema](#schema).
* `DESCRIBE TABLE unity.\`schema.table\`` SHALL show the same columns.

### RQ.SRS-050.ClickHouse.DeltaLake.Unity.Credentials
version: 1.0

`catalog_credential` SHALL accept all three of these:

* a Databricks personal access token
* an OAuth service principal written as `<client_id>:<client_secret>`
* a pre-obtained OAuth token

For a read with a personal access token, the token's principal needs `EXTERNAL USE SCHEMA` on the schema, `USE CATALOG` on the catalog, `USE SCHEMA` on the schema, and `SELECT` on the table. With those grants, `SHOW TABLES` and `SELECT` SHALL succeed.

### RQ.SRS-050.ClickHouse.DeltaLake.Unity.StorageKeys
version: 1.0

With `vended_credentials = false`, [ClickHouse] SHALL read table data with the storage settings on the database: `storage_endpoint`, `aws_access_key_id`, and `aws_secret_access_key`. This is the configuration of the `delta_lake` suite, which uses RustFS and the OSS Unity server.

```sql
CREATE DATABASE unity
ENGINE = DataLakeCatalog('http://unity-catalog:8080/api/2.1/unity-catalog')
SETTINGS
    catalog_type = 'unity',
    use_unity_catalog_v2 = 0,
    warehouse = 'unity',
    vended_credentials = false,
    storage_endpoint = 'http://rustfs:9000/warehouse',
    aws_access_key_id = 'key',
    aws_secret_access_key = 'secret';
```

The bytes [ClickHouse] reads SHALL be the Parquet files at the table's storage location. A wrong storage key SHALL fail the `SELECT`.

### RQ.SRS-050.ClickHouse.DeltaLake.Unity.VendedCredentials
version: 1.0

With `vended_credentials = true`, [ClickHouse] SHALL use the credentials the catalog vends for each table, for AWS S3 and for Azure ADLS Gen2. `SELECT` SHALL then succeed without `aws_access_key_id` and `aws_secret_access_key` on the database.

### RQ.SRS-050.ClickHouse.DeltaLake.Unity.ManagedStorage
version: 1.0

Unity Catalog does not vend credentials for Delta tables on Databricks managed storage. [ClickHouse] SHALL fail a read of such a table. The failure SHALL happen when the data is read. `CREATE DATABASE` itself stays successful, as in [RQ.SRS-050.ClickHouse.DeltaLake.Unity.CreateDatabase](#rqsrs-050clickhousedeltalakeunitycreatedatabase).

Tables on an external location, with either vended credentials or static storage keys, remain readable under [RQ.SRS-050.ClickHouse.DeltaLake.Unity.StorageKeys](#rqsrs-050clickhousedeltalakeunitystoragekeys) and [RQ.SRS-050.ClickHouse.DeltaLake.Unity.VendedCredentials](#rqsrs-050clickhousedeltalakeunityvendedcredentials).

### RQ.SRS-050.ClickHouse.DeltaLake.Unity.Check
version: 1.0

From ClickHouse 26.4, `CHECK DATABASE` SHALL contact the catalog. It SHALL succeed for a Unity endpoint that accepts the database credentials. It SHALL fail when the endpoint is unreachable or rejects those credentials.

```sql
CHECK DATABASE unity;
```

### RQ.SRS-050.ClickHouse.DeltaLake.Unity.SystemTables
version: 1.0

Catalog tables SHALL stay out of `system.tables` unless `show_remote_databases_in_system_tables = 1`. With that setting, `system.tables` SHALL list the Unity Delta tables. On servers older than 26.6 the setting name is `show_data_lake_catalogs_in_system_tables`.

### RQ.SRS-050.ClickHouse.DeltaLake.Unity.Insert
version: 1.0

`INSERT` into a Delta table reached through a Unity database SHALL follow [Writes](#writes). The table is a `DeltaLake` table, so the statement needs `allow_delta_lake_writes = 1`. A following `SELECT` on that catalog table SHALL return the inserted rows together with the rows that were already committed. An external Delta reader of the same storage location SHALL see the same new commit.


## Writes

Writes go through the [Delta Kernel](#delta-kernel). They are disabled until the session turns them on. ClickHouse can append rows. It cannot delete, update, or merge. An insert into a table whose active writer features ClickHouse cannot enforce fails under [RQ.SRS-050.ClickHouse.DeltaLake.Writes.WriterProtocol](#rqsrs-050clickhousedeltalakewriteswriterprotocol).

### RQ.SRS-050.ClickHouse.DeltaLake.Writes.Setting
version: 1.0

Delta writes SHALL stay disabled until the session sets `allow_delta_lake_writes = 1`. An `INSERT` with the setting off SHALL fail and SHALL NOT add a commit to `_delta_log`.

On 26.7 and newer the setting name is `allow_delta_lake_writes`. On earlier versions the name is `allow_experimental_delta_lake_writes`.

```sql
SET allow_delta_lake_writes = 1;
```

### RQ.SRS-050.ClickHouse.DeltaLake.Writes.Insert
version: 1.0

With writes enabled, `INSERT` SHALL append rows through the table engine and through the table function.

```sql
INSERT INTO events (id, name) VALUES (1, 'a');

INSERT INTO TABLE FUNCTION deltaLake(
    's3://bucket/warehouse/events/', 'key', 'secret'
) VALUES (2, 'b');
```

`INSERT SELECT` SHALL append the selected rows under the same rules.

### RQ.SRS-050.ClickHouse.DeltaLake.Writes.AppendVisible
version: 1.0

An `INSERT` SHALL add a new commit and SHALL leave previously committed rows in place. A later `SELECT` of the latest snapshot SHALL return the old rows and the inserted rows. An external Delta reader that opens the same location SHALL return those inserted rows as well.

The new log entry SHALL NOT overwrite an existing log file.

### RQ.SRS-050.ClickHouse.DeltaLake.Writes.Commit
version: 1.0

The new commit SHALL be the next zero-padded JSON file in `_delta_log`. Each data file it adds SHALL have a name that is not already in the table, and [ClickHouse] SHALL NOT overwrite that data file.

The commit SHALL contain at most one `metaData` action and at most one `protocol` action. It SHALL NOT list the same path twice among its `add` actions or twice among its `remove` actions. Every `add` SHALL set `dataChange` to `true` and SHALL include `partitionValues` for every partition column. The Parquet columns SHALL use the types of the current table schema, except where [type widening](https://github.com/delta-io/delta/blob/master/PROTOCOL.md#type-widening) allows an older file to stay as it was.

A `{version}.crc` file is optional. When [ClickHouse] writes one, its `numFiles` and `tableSizeBytes` SHALL match the snapshot after reconciliation, and [ClickHouse] SHALL NOT overwrite an existing checksum.

### RQ.SRS-050.ClickHouse.DeltaLake.Writes.WriterProtocol
version: 1.0

[ClickHouse] SHALL read the table before it writes. When `minWriterVersion`, or any name in `writerFeatures`, requires behavior [ClickHouse] does not implement, the `INSERT` SHALL fail and SHALL NOT add a commit.

That refusal covers an active feature [ClickHouse] cannot enforce on the way out:

* `delta.appendOnly = true` together with any statement that would remove rows. An append is allowed. See [RQ.SRS-050.ClickHouse.DeltaLake.Writes.AppendOnly](#rqsrs-050clickhousedeltalakewritesappendonly).
* An active invariant, `CHECK` constraint, generated column, or column default.
* Identity columns when the insert does not supply a value and [ClickHouse] does not allocate one.
* `columnMapping` when [ClickHouse] would write a Parquet column under the logical name instead of the physical name.
* `deletionVectors` when the insert would have to attach a vector [ClickHouse] does not write. An append of a new file with no vector is allowed.
* `rowTracking` when row tracking is not suspended. See [RQ.SRS-050.ClickHouse.DeltaLake.Writes.RowTracking](#rqsrs-050clickhousedeltalakewritesrowtracking).

A feature that is listed but not active SHALL NOT by itself reject an append. `appendOnly` in `writerFeatures` with `delta.appendOnly` unset or `false` is that case.

### RQ.SRS-050.ClickHouse.DeltaLake.Writes.DomainMetadata
version: 1.0

An `INSERT` SHALL leave existing `domainMetadata` actions in the snapshot, including domains [ClickHouse] does not understand. It SHALL NOT drop a system domain whose name starts with `delta.`. It SHALL NOT let a user SQL clause rewrite a system domain.

### RQ.SRS-050.ClickHouse.DeltaLake.Writes.RowTracking
version: 1.0

When `rowTracking` is in `writerFeatures` and `delta.rowTrackingSuspended` is not `true`, an `INSERT` SHALL either assign a unique `baseRowId` on every new `add` action and advance the `delta.rowTracking` high-water mark, or fail without a commit. [ClickHouse] SHALL NOT commit duplicate row ids.

### RQ.SRS-050.ClickHouse.DeltaLake.Writes.ChangeFeed
version: 1.0

When change data feed is enabled, an `INSERT` that only adds rows SHALL commit `add` actions for those rows. It MAY omit `cdc` files. A later change-data read SHALL report the inserted rows as `insert`. See [RQ.SRS-050.ClickHouse.DeltaLake.Read.ChangeDataFeed](#rqsrs-050clickhousedeltalakereadchangedatafeed).

### RQ.SRS-050.ClickHouse.DeltaLake.Writes.Backends
version: 1.0

`INSERT` SHALL write to S3 and GCS from ClickHouse 25.10, and to Azure Blob Storage from 26.9. Each of these writes uses the [Delta Kernel](#delta-kernel). A write with the kernel disabled SHALL fail and SHALL NOT leave a partial commit as the latest snapshot.

### RQ.SRS-050.ClickHouse.DeltaLake.Writes.AzureIdentity
version: 1.0

An `INSERT` that authenticates to Azure with workload identity, `extra_credentials(client_id = ..., tenant_id = ...)`, SHALL fail. [ClickHouse] SHALL NOT report that insert as successful.

### RQ.SRS-050.ClickHouse.DeltaLake.Writes.FileSize
version: 1.0

Each data file an `INSERT` writes SHALL stay within both limits:

| Setting | Default | Meaning |
|---|---|---|
| `delta_lake_insert_max_rows_in_data_file` | `1000000` | Maximum rows in one data file |
| `delta_lake_insert_max_bytes_in_data_file` | `1073741824` | Maximum bytes in one data file |

An insert larger than either limit SHALL be split into more than one data file, and every file SHALL respect both limits. Both settings have been available since 25.9.

### RQ.SRS-050.ClickHouse.DeltaLake.Writes.Cast
version: 1.0

`delta_lake_accurate_write_cast` defaults to `1`. [ClickHouse] SHALL cast each inserted value to the Delta column type and SHALL fail the insert when the value does not fit. A value of `300` inserted into a `byte` column SHALL fail. The failed insert SHALL NOT add a commit.

```sql
INSERT INTO readings (b) VALUES (300); -- b is byte
```

With `delta_lake_accurate_write_cast = 0`, or with `compatibility` set below 26.9, [ClickHouse] SHALL use a plain cast and SHALL commit the insert.

### RQ.SRS-050.ClickHouse.DeltaLake.Writes.NoMutation
version: 1.0

[ClickHouse] SHALL reject `DELETE`, `UPDATE`, and `MERGE` against a Delta table. `ALTER TABLE ... DELETE` SHALL be rejected as well. None of these statements SHALL add a commit.

### RQ.SRS-050.ClickHouse.DeltaLake.Writes.AppendOnly
version: 1.0

`INSERT` into a table with `delta.appendOnly = true` SHALL append rows and SHALL leave existing rows in the latest snapshot. The new commit SHALL NOT remove data.


## Cache and diagnostics

### RQ.SRS-050.ClickHouse.DeltaLake.Cache.Data
version: 1.0

The `DeltaLake` engine and the `deltaLake` table function SHALL cache data files through the same filesystem cache as the S3, Azure Blob Storage, and HDFS engines. `enable_filesystem_cache = 1` SHALL allow a later query to read an unchanged file from that cache. `enable_filesystem_cache = 0` SHALL read the file from object storage.

The cache SHALL NOT change the rows of the query. ClickHouse Cloud manages this cache. A self-managed server uses it when a filesystem cache disk is configured.

### RQ.SRS-050.ClickHouse.DeltaLake.MetadataLog
version: 1.0

With `delta_lake_log_metadata = 1`, [ClickHouse] SHALL record the Delta metadata files of that query in `system.delta_lake_metadata_log`. The setting defaults to `0`, and a query with the default SHALL NOT add rows for itself.

```sql
SELECT * FROM events SETTINGS delta_lake_log_metadata = 1;

SYSTEM FLUSH LOGS delta_lake_metadata_log;

SELECT file_path, content
FROM system.delta_lake_metadata_log
WHERE query_id = '<id>';
```

Each row SHALL carry `hostname`, `clickhouse_version`, `system_processor`, `event_date`, `event_time`, `query_id`, `table_path`, `file_path`, and `content`. `content` SHALL be JSON. `TRUNCATE` and `DROP` of this system table SHALL be allowed. This table has been available since 25.10.


## References

* **ClickHouse DeltaLake table engine:** https://clickhouse.com/docs/reference/engines/table-engines/integrations/deltalake
* **ClickHouse deltaLake table function:** https://clickhouse.com/docs/reference/functions/table-functions/deltalake
* **ClickHouse deltaLakeCluster table function:** https://clickhouse.com/docs/reference/functions/table-functions/deltalakeCluster
* **ClickHouse DataLakeCatalog:** https://clickhouse.com/docs/reference/engines/database-engines/datalake
* **ClickHouse Unity Catalog guide:** https://clickhouse.com/docs/guides/use-cases/data-warehousing/unity-catalog
* **ClickHouse support matrix:** https://clickhouse.com/docs/guides/use-cases/data-warehousing/support-matrix
* **ClickHouse data-lake best practices:** https://clickhouse.com/docs/guides/use-cases/data-warehousing/getting-started/best-practices
* **ClickHouse `delta_lake_*` settings:** https://clickhouse.com/docs/reference/settings/session-settings/delta-lake
* **ClickHouse `system.delta_lake_metadata_log`:** https://clickhouse.com/docs/reference/system-tables/delta_lake_metadata_log
* **Delta Lake protocol:** https://github.com/delta-io/delta/blob/master/PROTOCOL.md#delta-table-specification
* **Delta Lake feature versions:** https://docs.delta.io/versioning/
* **ClickHouse type mapping:** `DeltaLakeMetadata::getSimpleTypeByName` and `getComplexTypeFromObject` in `src/Storages/ObjectStorage/DataLakes/DeltaLakeMetadata.cpp`. `varchar(n)` and `char(n)` map to `String` so Unity `type_json` can be read.

[ClickHouse]: https://clickhouse.com
[Delta Lake]: https://delta.io/
[Unity Catalog]: https://www.databricks.com/product/unity-catalog
[Delta Kernel]: https://github.com/delta-io/delta-kernel-rs
