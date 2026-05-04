# SRS-047 ClickHouse EXPORT PARTITION to Apache Iceberg
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Core export path](#core-export-path)
    * 2.1 [RQ.Iceberg.ExportPartition.Sanity](#rqicebergexportpartitionsanity)
* 3 [Partition and schema compatibility](#partition-and-schema-compatibility)
    * 3.1 [RQ.Iceberg.ExportPartition.PartitionCompatibility](#rqicebergexportpartitionpartitioncompatibility)
    * 3.2 [RQ.Iceberg.ExportPartition.DataTypes](#rqicebergexportpartitiondatatypes)
* 4 [Committed Iceberg metadata](#committed-iceberg-metadata)
    * 4.1 [RQ.Iceberg.ExportPartition.ManifestIntegrity](#rqicebergexportpartitionmanifestintegrity)
    * 4.2 [RQ.Iceberg.ExportPartition.CatalogIntegration](#rqicebergexportpartitioncatalogintegration)
* 5 [Transactions, idempotency, and concurrency](#transactions-idempotency-and-concurrency)
    * 5.1 [RQ.Iceberg.ExportPartition.Transactions](#rqicebergexportpartitiontransactions)
    * 5.2 [RQ.Iceberg.ExportPartition.ConcurrentWrites](#rqicebergexportpartitionconcurrentwrites)
* 6 [Evolution and physical layout](#evolution-and-physical-layout)
    * 6.1 [RQ.Iceberg.ExportPartition.SchemaEvolution](#rqicebergexportpartitionschemaevolution)
    * 6.2 [RQ.Iceberg.ExportPartition.PartitionSpecEvolution](#rqicebergexportpartitionpartitionspecevolution)
    * 6.3 [RQ.Iceberg.ExportPartition.StoragePaths](#rqicebergexportpartitionstoragepaths)
* 7 [Failure handling and multi-replica behaviour](#failure-handling-and-multi-replica-behaviour)
    * 7.1 [RQ.Iceberg.ExportPartition.DisasterRecovery](#rqicebergexportpartitiondisasterrecovery)
    * 7.2 [RQ.Iceberg.ExportPartition.MultiReplicaRecovery](#rqicebergexportpartitionmultireplicarecovery)
* 8 [Observability and export settings](#observability-and-export-settings)
    * 8.1 [RQ.Iceberg.ExportPartition.SystemMonitoring](#rqicebergexportpartitionsystemmonitoring)
    * 8.2 [RQ.Iceberg.ExportPartition.Settings](#rqicebergexportpartitionsettings)
* 9 [Post-export destination operations](#post-export-destination-operations)
    * 9.1 [RQ.Iceberg.ExportPartition.DirectWrites](#rqicebergexportpartitiondirectwrites)
    * 9.2 [RQ.Iceberg.ExportPartition.Truncate](#rqicebergexportpartitiontruncate)
    * 9.3 [RQ.Iceberg.ExportPartition.MinMaxPruning](#rqicebergexportpartitionminmaxpruning)
* 10 [Source replica and ZooKeeper compatibility](#source-replica-and-zookeeper-compatibility)
    * 10.1 [RQ.Iceberg.ExportPartition.ZooKeeperCompat](#rqicebergexportpartitionzookeepercompat)

## Introduction

This specification defines requirements for **exporting partitions from `ReplicatedMergeTree` source tables into Apache Iceberg destinations** using ClickHouse’s experimental `ALTER TABLE … EXPORT PARTITION … TO TABLE …` surface, when the destination is Iceberg on S3 (with or without an external REST / Glue catalog).

The experimental feature SHALL be gated by the server setting `allow_experimental_export_merge_tree_partition` (default `0`). When the setting is disabled, export behaviour SHALL match ClickHouse’s upstream contract (support disabled until explicitly enabled in server configuration).

Regression tests that exercise these requirements live under the TestFlows package `iceberg.tests.export_partition`. The outer feature in `iceberg.tests.export_partition.feature` loads one sub-feature per Python module listed in its `MODULES` tuple and runs the same scenarios under multiple **catalog modes** (`no_catalog` / `rest` / `glue`) unless a module documents a narrower scope. Each requirement below names exactly one such module so traceability stays roughly one-to-one: one requirement ↔ one coherent test module (not every individual scenario).

[ClickHouse]: https://clickhouse.com

## Core export path

### RQ.Iceberg.ExportPartition.Sanity
version: 1.0

[ClickHouse] SHALL support the happy path of `ALTER TABLE … EXPORT PARTITION … TO TABLE …` from a `ReplicatedMergeTree` source into a compatible Iceberg destination such that:

* The command can target a single partition or all partitions in a defined, documented way.
* After a successful export, row counts and representative column values read back from the Iceberg destination match the exported slice of the source for the catalog modes the product claims to support.
* `system.replicated_partition_exports` (or equivalent monitoring surface) reflects completion for successful exports.

**Regression module:** `iceberg.tests.export_partition.sanity` (`sanity.py`).

## Partition and schema compatibility

### RQ.Iceberg.ExportPartition.PartitionCompatibility
version: 1.0

[ClickHouse] SHALL enforce compatibility between the MergeTree `PARTITION BY` definition (including supported partition transforms) and the Iceberg destination’s partition spec:

* Accepted pairings SHALL export successfully.
* Mismatched or unsupported pairings SHALL be rejected with a clear error (for example `BAD_ARGUMENTS`) rather than committing partial or corrupt Iceberg metadata.

**Regression module:** `iceberg.tests.export_partition.partition_compatibility` (`partition_compatibility.py`).

### RQ.Iceberg.ExportPartition.DataTypes
version: 1.0

[ClickHouse] SHALL map ClickHouse column types used in the export to Iceberg types that preserve the intended values for every supported primitive and nested layout advertised by the implementation.

* For types with no supported Iceberg mapping, creation of the destination or the export itself SHALL fail explicitly; the system SHALL NOT silently coerce or drop data.

**Regression module:** `iceberg.tests.export_partition.datatypes` (`datatypes.py`).

## Committed Iceberg metadata

### RQ.Iceberg.ExportPartition.ManifestIntegrity
version: 1.0

[ClickHouse] SHALL produce Iceberg metadata after each successful export such that independent validators (for example PyIceberg reading manifests and snapshots) can confirm:

* Snapshot lineage advances in a well-defined way per export.
* Snapshot summaries and manifest statistics are internally consistent with the rows and files written (within the limits of which statistics the writer populates).
* Partition spec references in manifests align with the source partitioning intent.

**Regression module:** `iceberg.tests.export_partition.manifest_integrity` (`manifest_integrity.py`).

### RQ.Iceberg.ExportPartition.CatalogIntegration
version: 1.0

[ClickHouse] SHALL commit exports through the same catalog-aware metadata paths used in production when the destination is registered in a **REST** or **Glue** (Hive metastore compatible) catalog:

* After commit, the table SHALL be readable through ClickHouse’s catalog-backed database objects and through an external catalog client where the suite validates interoperability (for example PyIceberg).
* **No-catalog** (`IcebergS3`) destinations SHALL remain readable via table functions or recreated tables pointing at the same warehouse prefix where that mode is supported.

**Regression module:** `iceberg.tests.export_partition.catalogs` (`catalogs.py`).

## Transactions, idempotency, and concurrency

### RQ.Iceberg.ExportPartition.Transactions
version: 1.0

[ClickHouse] SHALL treat each successful Iceberg commit from `EXPORT PARTITION` as an **append** snapshot with monotonic snapshot / sequence semantics relative to the prior table state.

* Idempotency keys (for example ZooKeeper–backed guards keyed by source, destination, and partition) SHALL prevent duplicate commits within the configured TTL unless `export_merge_tree_partition_force_export` (or equivalent documented setting) overrides the guard as specified.
* Documented failure-injection points in the commit path SHALL not leave the destination in a state that violates atomicity guarantees asserted by the implementation (for example orphaned files without a published snapshot, or published snapshots without readable data).

**Regression module:** `iceberg.tests.export_partition.transactions` (`transactions.py`).

### RQ.Iceberg.ExportPartition.ConcurrentWrites
version: 1.0

[ClickHouse] SHALL serialize or coordinate concurrent export work so that multiple partition exports targeting the same Iceberg destination produce a **linear append-only** snapshot history without corrupting metadata, including when multiple export statements are submitted in one client batch or interleaved with source writes under the scenarios the product defines as supported.

**Regression module:** `iceberg.tests.export_partition.concurrent_writes` (`concurrent_writes.py`).

## Evolution and physical layout

### RQ.Iceberg.ExportPartition.SchemaEvolution
version: 1.0

[ClickHouse] SHALL allow documented schema evolution (for example add / drop / widen columns) on the Iceberg destination and the `ReplicatedMergeTree` source such that subsequent `EXPORT PARTITION` operations succeed only when the schemas remain compatible per `IcebergMetadata` rules; unsupported alterations SHALL be rejected deterministically.

**Regression module:** `iceberg.tests.export_partition.schema_evolution` (`schema_evolution.py`).

### RQ.Iceberg.ExportPartition.PartitionSpecEvolution
version: 1.0

[ClickHouse] SHALL maintain correct partition metadata across sequential exports when the MergeTree and Iceberg tables share a stable partition expression, including correct per-file partition values for Iceberg partition pruning.

**Regression module:** `iceberg.tests.export_partition.partition_spec_evolution` (`partition_spec_evolution.py`).

### RQ.Iceberg.ExportPartition.StoragePaths
version: 1.0

[ClickHouse] SHALL honour `write_full_path_in_iceberg_metadata` (and related path rules) when laying out Iceberg table locations and metadata on S3, including deep prefix hierarchies and multiple isolated destinations under one bucket, such that committed paths remain consistent with the configured policy.

**Regression module:** `iceberg.tests.export_partition.storage_paths` (`storage_paths.py`).

## Failure handling and multi-replica behaviour

### RQ.Iceberg.ExportPartition.DisasterRecovery
version: 1.0

[ClickHouse] SHALL surface export lifecycle states through `system.replicated_partition_exports` and SHALL recover or fail cleanly under operator actions such as stopping background moves, killing exports, invalid destinations, or non-existent partition IDs—without committing a partial Iceberg snapshot in success cases where the implementation promises all-or-nothing behaviour.

**Regression module:** `iceberg.tests.export_partition.disaster_recovery` (`disaster_recovery.py`).

### RQ.Iceberg.ExportPartition.MultiReplicaRecovery
version: 1.0

[ClickHouse] SHALL preserve export idempotency and Iceberg snapshot linearity when exports are initiated from **different replicas** of the same `ReplicatedMergeTree` table, including under ZooKeeper restarts or process-level interruption mid-flight, converging to at most one successful commit per guarded export key where that invariant is defined.

**Regression module:** `iceberg.tests.export_partition.multi_replica_recovery` (`multi_replica_recovery.py`).

## Observability and export settings

### RQ.Iceberg.ExportPartition.SystemMonitoring
version: 1.0

[ClickHouse] SHALL populate `system.replicated_partition_exports`, `system.part_log` (where applicable), and relevant `ProfileEvents` counters so operators can audit export progress, provenance, and completion—including correct handling when an export is killed.

**Regression module:** `iceberg.tests.export_partition.system_monitoring` (`system_monitoring.py`).

### RQ.Iceberg.ExportPartition.Settings
version: 1.0

[ClickHouse] SHALL honour documented **merge-tree export partition** settings (for example preferences for remote vs local export metadata, compression flowing to Parquet writers where the implementation forwards format settings) in a way observable from successful exports and system tables.

**Regression module:** `iceberg.tests.export_partition.settings` (`settings.py`).

## Post-export destination operations

### RQ.Iceberg.ExportPartition.DirectWrites
version: 1.0

[ClickHouse] SHALL allow subsequent **`INSERT`** into the same Iceberg destination (when enabled by `allow_experimental_insert_into_iceberg` or successor settings) after an `EXPORT PARTITION` commit, extending the snapshot chain without breaking reads through ClickHouse or catalog-backed external readers used in the suite.

**Regression module:** `iceberg.tests.export_partition.direct_writes` (`direct_writes.py`).

### RQ.Iceberg.ExportPartition.Truncate
version: 1.0

[ClickHouse] SHALL support **`TRUNCATE TABLE`** on an Iceberg destination previously populated by `EXPORT PARTITION` (when enabled by experimental truncate settings), clearing readable data, and SHALL allow a later `EXPORT PARTITION` to repopulate the table with a fresh append snapshot **provided** path-format and catalog rules remain internally consistent for the catalog mode in use.

**Regression module:** `iceberg.tests.export_partition.truncate` (`truncate.py`).

### RQ.Iceberg.ExportPartition.MinMaxPruning
version: 1.0

[ClickHouse] SHALL write Iceberg manifest column statistics (`lower_bounds` / `upper_bounds`) during export such that reads of the destination with selective predicates exhibit **min/max pruning** behaviour visible in `ProfileEvents` (for example fewer files touched and reduced `read_rows` than a full scan) when data layout makes pruning possible.

**Regression module:** `iceberg.tests.export_partition.minmax_pruning` (`minmax_pruning.py`).

## Source replica and ZooKeeper compatibility

### RQ.Iceberg.ExportPartition.ZooKeeperCompat
version: 1.0

[ClickHouse] SHALL recreate or ensure presence of the **`/exports`** coordination subtree under the table’s ZooKeeper path during normal replica attach / restart flows so that `ReplicatedMergeTree` tables whose ZooKeeper state predates the export feature (or temporarily lack `/exports`) become eligible for `EXPORT PARTITION` after a documented recovery step (for example `SYSTEM RESTART REPLICA` or full server restart), without requiring manual ZK surgery for the supported upgrade path.

**Regression module:** `iceberg.tests.export_partition.zk_compat` (`zk_compat.py`).
