# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_Iceberg_ExportPartition_Sanity = Requirement(
    name="RQ.Iceberg.ExportPartition.Sanity",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the happy path of `ALTER TABLE … EXPORT PARTITION … TO TABLE …` from a `ReplicatedMergeTree` source into a compatible Iceberg destination such that:\n"
        "\n"
        "* The command can target a single partition or all partitions in a defined, documented way.\n"
        "* After a successful export, row counts and representative column values read back from the Iceberg destination match the exported slice of the source for the catalog modes the product claims to support.\n"
        "* `system.replicated_partition_exports` (or equivalent monitoring surface) reflects completion for successful exports.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.sanity` (`sanity.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.1",
)

RQ_Iceberg_ExportPartition_PartitionCompatibility = Requirement(
    name="RQ.Iceberg.ExportPartition.PartitionCompatibility",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL enforce compatibility between the MergeTree `PARTITION BY` definition (including supported partition transforms) and the Iceberg destination’s partition spec:\n"
        "\n"
        "* Accepted pairings SHALL export successfully.\n"
        "* Mismatched or unsupported pairings SHALL be rejected with a clear error (for example `BAD_ARGUMENTS`) rather than committing partial or corrupt Iceberg metadata.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.partition_compatibility` (`partition_compatibility.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.1",
)

RQ_Iceberg_ExportPartition_DataTypes = Requirement(
    name="RQ.Iceberg.ExportPartition.DataTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL map ClickHouse column types used in the export to Iceberg types that preserve the intended values for every supported primitive and nested layout advertised by the implementation.\n"
        "\n"
        "* For types with no supported Iceberg mapping, creation of the destination or the export itself SHALL fail explicitly; the system SHALL NOT silently coerce or drop data.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.datatypes` (`datatypes.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.2",
)

RQ_Iceberg_ExportPartition_ManifestIntegrity = Requirement(
    name="RQ.Iceberg.ExportPartition.ManifestIntegrity",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL produce Iceberg metadata after each successful export such that independent validators (for example PyIceberg reading manifests and snapshots) can confirm:\n"
        "\n"
        "* Snapshot lineage advances in a well-defined way per export.\n"
        "* Snapshot summaries and manifest statistics are internally consistent with the rows and files written (within the limits of which statistics the writer populates).\n"
        "* Partition spec references in manifests align with the source partitioning intent.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.manifest_integrity` (`manifest_integrity.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.1",
)

RQ_Iceberg_ExportPartition_CatalogIntegration = Requirement(
    name="RQ.Iceberg.ExportPartition.CatalogIntegration",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL commit exports through the same catalog-aware metadata paths used in production when the destination is registered in a **REST** or **Glue** (Hive metastore compatible) catalog:\n"
        "\n"
        "* After commit, the table SHALL be readable through ClickHouse’s catalog-backed database objects and through an external catalog client where the suite validates interoperability (for example PyIceberg).\n"
        "* **No-catalog** (`IcebergS3`) destinations SHALL remain readable via table functions or recreated tables pointing at the same warehouse prefix where that mode is supported.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.catalogs` (`catalogs.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.2",
)

RQ_Iceberg_ExportPartition_Transactions = Requirement(
    name="RQ.Iceberg.ExportPartition.Transactions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL treat each successful Iceberg commit from `EXPORT PARTITION` as an **append** snapshot with monotonic snapshot / sequence semantics relative to the prior table state.\n"
        "\n"
        "* Idempotency keys (for example ZooKeeper–backed guards keyed by source, destination, and partition) SHALL prevent duplicate commits within the configured TTL unless `export_merge_tree_partition_force_export` (or equivalent documented setting) overrides the guard as specified.\n"
        "* Documented failure-injection points in the commit path SHALL not leave the destination in a state that violates atomicity guarantees asserted by the implementation (for example orphaned files without a published snapshot, or published snapshots without readable data).\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.transactions` (`transactions.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.1",
)

RQ_Iceberg_ExportPartition_ConcurrentWrites = Requirement(
    name="RQ.Iceberg.ExportPartition.ConcurrentWrites",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL serialize or coordinate concurrent export work so that multiple partition exports targeting the same Iceberg destination produce a **linear append-only** snapshot history without corrupting metadata, including when multiple export statements are submitted in one client batch or interleaved with source writes under the scenarios the product defines as supported.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.concurrent_writes` (`concurrent_writes.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.2",
)

RQ_Iceberg_ExportPartition_SchemaEvolution = Requirement(
    name="RQ.Iceberg.ExportPartition.SchemaEvolution",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL allow documented schema evolution (for example add / drop / widen columns) on the Iceberg destination and the `ReplicatedMergeTree` source such that subsequent `EXPORT PARTITION` operations succeed only when the schemas remain compatible per `IcebergMetadata` rules; unsupported alterations SHALL be rejected deterministically.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.schema_evolution` (`schema_evolution.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.1",
)

RQ_Iceberg_ExportPartition_PartitionSpecEvolution = Requirement(
    name="RQ.Iceberg.ExportPartition.PartitionSpecEvolution",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL maintain correct partition metadata across sequential exports when the MergeTree and Iceberg tables share a stable partition expression, including correct per-file partition values for Iceberg partition pruning.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.partition_spec_evolution` (`partition_spec_evolution.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.2",
)

RQ_Iceberg_ExportPartition_StoragePaths = Requirement(
    name="RQ.Iceberg.ExportPartition.StoragePaths",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL honour `write_full_path_in_iceberg_metadata` (and related path rules) when laying out Iceberg table locations and metadata on S3, including deep prefix hierarchies and multiple isolated destinations under one bucket, such that committed paths remain consistent with the configured policy.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.storage_paths` (`storage_paths.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.3",
)

RQ_Iceberg_ExportPartition_DisasterRecovery = Requirement(
    name="RQ.Iceberg.ExportPartition.DisasterRecovery",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL surface export lifecycle states through `system.replicated_partition_exports` and SHALL recover or fail cleanly under operator actions such as stopping background moves, killing exports, invalid destinations, or non-existent partition IDs—without committing a partial Iceberg snapshot in success cases where the implementation promises all-or-nothing behaviour.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.disaster_recovery` (`disaster_recovery.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.1",
)

RQ_Iceberg_ExportPartition_MultiReplicaRecovery = Requirement(
    name="RQ.Iceberg.ExportPartition.MultiReplicaRecovery",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL preserve export idempotency and Iceberg snapshot linearity when exports are initiated from **different replicas** of the same `ReplicatedMergeTree` table, including under ZooKeeper restarts or process-level interruption mid-flight, converging to at most one successful commit per guarded export key where that invariant is defined.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.multi_replica_recovery` (`multi_replica_recovery.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.2",
)

RQ_Iceberg_ExportPartition_SystemMonitoring = Requirement(
    name="RQ.Iceberg.ExportPartition.SystemMonitoring",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL populate `system.replicated_partition_exports`, `system.part_log` (where applicable), and relevant `ProfileEvents` counters so operators can audit export progress, provenance, and completion—including correct handling when an export is killed.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.system_monitoring` (`system_monitoring.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.1",
)

RQ_Iceberg_ExportPartition_Settings = Requirement(
    name="RQ.Iceberg.ExportPartition.Settings",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL honour documented **merge-tree export partition** settings (for example preferences for remote vs local export metadata, compression flowing to Parquet writers where the implementation forwards format settings) in a way observable from successful exports and system tables.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.settings` (`settings.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.2",
)

RQ_Iceberg_ExportPartition_DirectWrites = Requirement(
    name="RQ.Iceberg.ExportPartition.DirectWrites",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL allow subsequent **`INSERT`** into the same Iceberg destination (when enabled by `allow_experimental_insert_into_iceberg` or successor settings) after an `EXPORT PARTITION` commit, extending the snapshot chain without breaking reads through ClickHouse or catalog-backed external readers used in the suite.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.direct_writes` (`direct_writes.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.1",
)

RQ_Iceberg_ExportPartition_Truncate = Requirement(
    name="RQ.Iceberg.ExportPartition.Truncate",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support **`TRUNCATE TABLE`** on an Iceberg destination previously populated by `EXPORT PARTITION` (when enabled by experimental truncate settings), clearing readable data, and SHALL allow a later `EXPORT PARTITION` to repopulate the table with a fresh append snapshot **provided** path-format and catalog rules remain internally consistent for the catalog mode in use.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.truncate` (`truncate.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.2",
)

RQ_Iceberg_ExportPartition_MinMaxPruning = Requirement(
    name="RQ.Iceberg.ExportPartition.MinMaxPruning",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL write Iceberg manifest column statistics (`lower_bounds` / `upper_bounds`) during export such that reads of the destination with selective predicates exhibit **min/max pruning** behaviour visible in `ProfileEvents` (for example fewer files touched and reduced `read_rows` than a full scan) when data layout makes pruning possible.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.minmax_pruning` (`minmax_pruning.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.3",
)

RQ_Iceberg_ExportPartition_ZooKeeperCompat = Requirement(
    name="RQ.Iceberg.ExportPartition.ZooKeeperCompat",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL recreate or ensure presence of the **`/exports`** coordination subtree under the table’s ZooKeeper path during normal replica attach / restart flows so that `ReplicatedMergeTree` tables whose ZooKeeper state predates the export feature (or temporarily lack `/exports`) become eligible for `EXPORT PARTITION` after a documented recovery step (for example `SYSTEM RESTART REPLICA` or full server restart), without requiring manual ZK surgery for the supported upgrade path.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.zk_compat` (`zk_compat.py`).\n"
    ),
    link=None,
    level=2,
    num="10.1",
)

SRS_047_ClickHouse_EXPORT_PARTITION_to_Apache_Iceberg = Specification(
    name="SRS-047 ClickHouse EXPORT PARTITION to Apache Iceberg",
    description=None,
    author=None,
    date=None,
    status=None,
    approved_by=None,
    approved_date=None,
    approved_version=None,
    version=None,
    group=None,
    type=None,
    link=None,
    uid=None,
    parent=None,
    children=None,
    headings=(
        Heading(name="Introduction", level=1, num="1"),
        Heading(name="Core export path", level=1, num="2"),
        Heading(name="RQ.Iceberg.ExportPartition.Sanity", level=2, num="2.1"),
        Heading(name="Partition and schema compatibility", level=1, num="3"),
        Heading(
            name="RQ.Iceberg.ExportPartition.PartitionCompatibility", level=2, num="3.1"
        ),
        Heading(name="RQ.Iceberg.ExportPartition.DataTypes", level=2, num="3.2"),
        Heading(name="Committed Iceberg metadata", level=1, num="4"),
        Heading(
            name="RQ.Iceberg.ExportPartition.ManifestIntegrity", level=2, num="4.1"
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.CatalogIntegration", level=2, num="4.2"
        ),
        Heading(name="Transactions, idempotency, and concurrency", level=1, num="5"),
        Heading(name="RQ.Iceberg.ExportPartition.Transactions", level=2, num="5.1"),
        Heading(name="RQ.Iceberg.ExportPartition.ConcurrentWrites", level=2, num="5.2"),
        Heading(name="Evolution and physical layout", level=1, num="6"),
        Heading(name="RQ.Iceberg.ExportPartition.SchemaEvolution", level=2, num="6.1"),
        Heading(
            name="RQ.Iceberg.ExportPartition.PartitionSpecEvolution", level=2, num="6.2"
        ),
        Heading(name="RQ.Iceberg.ExportPartition.StoragePaths", level=2, num="6.3"),
        Heading(name="Failure handling and multi-replica behaviour", level=1, num="7"),
        Heading(name="RQ.Iceberg.ExportPartition.DisasterRecovery", level=2, num="7.1"),
        Heading(
            name="RQ.Iceberg.ExportPartition.MultiReplicaRecovery", level=2, num="7.2"
        ),
        Heading(name="Observability and export settings", level=1, num="8"),
        Heading(name="RQ.Iceberg.ExportPartition.SystemMonitoring", level=2, num="8.1"),
        Heading(name="RQ.Iceberg.ExportPartition.Settings", level=2, num="8.2"),
        Heading(name="Post-export destination operations", level=1, num="9"),
        Heading(name="RQ.Iceberg.ExportPartition.DirectWrites", level=2, num="9.1"),
        Heading(name="RQ.Iceberg.ExportPartition.Truncate", level=2, num="9.2"),
        Heading(name="RQ.Iceberg.ExportPartition.MinMaxPruning", level=2, num="9.3"),
        Heading(name="Source replica and ZooKeeper compatibility", level=1, num="10"),
        Heading(name="RQ.Iceberg.ExportPartition.ZooKeeperCompat", level=2, num="10.1"),
    ),
    requirements=(
        RQ_Iceberg_ExportPartition_Sanity,
        RQ_Iceberg_ExportPartition_PartitionCompatibility,
        RQ_Iceberg_ExportPartition_DataTypes,
        RQ_Iceberg_ExportPartition_ManifestIntegrity,
        RQ_Iceberg_ExportPartition_CatalogIntegration,
        RQ_Iceberg_ExportPartition_Transactions,
        RQ_Iceberg_ExportPartition_ConcurrentWrites,
        RQ_Iceberg_ExportPartition_SchemaEvolution,
        RQ_Iceberg_ExportPartition_PartitionSpecEvolution,
        RQ_Iceberg_ExportPartition_StoragePaths,
        RQ_Iceberg_ExportPartition_DisasterRecovery,
        RQ_Iceberg_ExportPartition_MultiReplicaRecovery,
        RQ_Iceberg_ExportPartition_SystemMonitoring,
        RQ_Iceberg_ExportPartition_Settings,
        RQ_Iceberg_ExportPartition_DirectWrites,
        RQ_Iceberg_ExportPartition_Truncate,
        RQ_Iceberg_ExportPartition_MinMaxPruning,
        RQ_Iceberg_ExportPartition_ZooKeeperCompat,
    ),
    content=r"""
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
""",
)
