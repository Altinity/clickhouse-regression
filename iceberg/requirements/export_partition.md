# SRS-047 ClickHouse EXPORT PARTITION to Apache Iceberg
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Core export path](#core-export-path)
    * 2.1 [RQ.Iceberg.ExportPartition.Sanity](#rqicebergexportpartitionsanity)
    * 2.2 [RQ.Iceberg.ExportPartition.Sanity.EmptyPartition](#rqicebergexportpartitionsanityemptypartition)
    * 2.3 [RQ.Iceberg.ExportPartition.Sanity.CrossReplicaInitiator](#rqicebergexportpartitionsanitycrossreplicainitiator)
* 3 [Partition and schema compatibility](#partition-and-schema-compatibility)
    * 3.1 [RQ.Iceberg.ExportPartition.PartitionCompatibility.AcceptedTransforms](#rqicebergexportpartitionpartitioncompatibilityacceptedtransforms)
    * 3.2 [RQ.Iceberg.ExportPartition.PartitionCompatibility.MismatchRejection](#rqicebergexportpartitionpartitioncompatibilitymismatchrejection)
    * 3.3 [RQ.Iceberg.ExportPartition.DataTypes.Primitives](#rqicebergexportpartitiondatatypesprimitives)
    * 3.4 [RQ.Iceberg.ExportPartition.DataTypes.Nullable](#rqicebergexportpartitiondatatypesnullable)
    * 3.5 [RQ.Iceberg.ExportPartition.DataTypes.Composite](#rqicebergexportpartitiondatatypescomposite)
    * 3.6 [RQ.Iceberg.ExportPartition.DataTypes.UnsupportedRejection](#rqicebergexportpartitiondatatypesunsupportedrejection)
* 4 [Committed Iceberg metadata](#committed-iceberg-metadata)
    * 4.1 [RQ.Iceberg.ExportPartition.ManifestIntegrity.SnapshotChain](#rqicebergexportpartitionmanifestintegritysnapshotchain)
    * 4.2 [RQ.Iceberg.ExportPartition.ManifestIntegrity.PartitionSpec](#rqicebergexportpartitionmanifestintegritypartitionspec)
    * 4.3 [RQ.Iceberg.ExportPartition.ManifestIntegrity.ColumnStats](#rqicebergexportpartitionmanifestintegritycolumnstats)
    * 4.4 [RQ.Iceberg.ExportPartition.ManifestIntegrity.PathLayout](#rqicebergexportpartitionmanifestintegritypathlayout)
    * 4.5 [RQ.Iceberg.ExportPartition.ManifestIntegrity.ExternalReader](#rqicebergexportpartitionmanifestintegrityexternalreader)
    * 4.6 [RQ.Iceberg.ExportPartition.CatalogIntegration.NoCatalog](#rqicebergexportpartitioncatalogintegrationnocatalog)
    * 4.7 [RQ.Iceberg.ExportPartition.CatalogIntegration.RestGlue](#rqicebergexportpartitioncatalogintegrationrestglue)
* 5 [Transactions, idempotency, and concurrency](#transactions-idempotency-and-concurrency)
    * 5.1 [RQ.Iceberg.ExportPartition.Transactions.SnapshotChain](#rqicebergexportpartitiontransactionssnapshotchain)
    * 5.2 [RQ.Iceberg.ExportPartition.Transactions.Idempotency](#rqicebergexportpartitiontransactionsidempotency)
    * 5.3 [RQ.Iceberg.ExportPartition.Transactions.CrashRecovery](#rqicebergexportpartitiontransactionscrashrecovery)
    * 5.4 [RQ.Iceberg.ExportPartition.ConcurrentWrites.MultiStatement](#rqicebergexportpartitionconcurrentwritesmultistatement)
    * 5.5 [RQ.Iceberg.ExportPartition.ConcurrentWrites.Interleaving](#rqicebergexportpartitionconcurrentwritesinterleaving)
* 6 [Evolution and physical layout](#evolution-and-physical-layout)
    * 6.1 [RQ.Iceberg.ExportPartition.SchemaEvolution.AcceptedAlterations](#rqicebergexportpartitionschemaevolutionacceptedalterations)
    * 6.2 [RQ.Iceberg.ExportPartition.SchemaEvolution.RejectedAlterations](#rqicebergexportpartitionschemaevolutionrejectedalterations)
    * 6.3 [RQ.Iceberg.ExportPartition.SchemaEvolution.SchemaHistory](#rqicebergexportpartitionschemaevolutionschemahistory)
    * 6.4 [RQ.Iceberg.ExportPartition.PartitionSpecEvolution](#rqicebergexportpartitionpartitionspecevolution)
    * 6.5 [RQ.Iceberg.ExportPartition.StoragePaths.PathFormat](#rqicebergexportpartitionstoragepathspathformat)
    * 6.6 [RQ.Iceberg.ExportPartition.StoragePaths.DeepPrefix](#rqicebergexportpartitionstoragepathsdeepprefix)
    * 6.7 [RQ.Iceberg.ExportPartition.StoragePaths.Isolation](#rqicebergexportpartitionstoragepathsisolation)
* 7 [Failure handling and multi-replica behaviour](#failure-handling-and-multi-replica-behaviour)
    * 7.1 [RQ.Iceberg.ExportPartition.DisasterRecovery.MovesControl](#rqicebergexportpartitiondisasterrecoverymovescontrol)
    * 7.2 [RQ.Iceberg.ExportPartition.DisasterRecovery.KillExport](#rqicebergexportpartitiondisasterrecoverykillexport)
    * 7.3 [RQ.Iceberg.ExportPartition.DisasterRecovery.InvalidInputs](#rqicebergexportpartitiondisasterrecoveryinvalidinputs)
    * 7.4 [RQ.Iceberg.ExportPartition.MultiReplicaRecovery.CrossReplicaConcurrency](#rqicebergexportpartitionmultireplicarecoverycrossreplicaconcurrency)
    * 7.5 [RQ.Iceberg.ExportPartition.MultiReplicaRecovery.InitiatorFailover](#rqicebergexportpartitionmultireplicarecoveryinitiatorfailover)
    * 7.6 [RQ.Iceberg.ExportPartition.MultiReplicaRecovery.ZooKeeperBounce](#rqicebergexportpartitionmultireplicarecoveryzookeeperbounce)
    * 7.7 [RQ.Iceberg.ExportPartition.MultiReplicaRecovery.RandomisedChaos](#rqicebergexportpartitionmultireplicarecoveryrandomisedchaos)
    * 7.8 [RQ.Iceberg.ExportPartition.MultiReplicaRecovery.SettingDisabledFailover](#rqicebergexportpartitionmultireplicarecoverysettingdisabledfailover)
* 8 [Observability and export settings](#observability-and-export-settings)
    * 8.1 [RQ.Iceberg.ExportPartition.SystemMonitoring.ReplicatedPartitionExports](#rqicebergexportpartitionsystemmonitoringreplicatedpartitionexports)
    * 8.2 [RQ.Iceberg.ExportPartition.SystemMonitoring.PartLog](#rqicebergexportpartitionsystemmonitoringpartlog)
    * 8.3 [RQ.Iceberg.ExportPartition.SystemMonitoring.ProfileEvents](#rqicebergexportpartitionsystemmonitoringprofileevents)
    * 8.4 [RQ.Iceberg.ExportPartition.SystemMonitoring.KilledProvenance](#rqicebergexportpartitionsystemmonitoringkilledprovenance)
    * 8.5 [RQ.Iceberg.ExportPartition.Settings.ParquetCompression](#rqicebergexportpartitionsettingsparquetcompression)
* 9 [Post-export destination operations](#post-export-destination-operations)
    * 9.1 [RQ.Iceberg.ExportPartition.DirectWrites](#rqicebergexportpartitiondirectwrites)
    * 9.2 [RQ.Iceberg.ExportPartition.Truncate](#rqicebergexportpartitiontruncate)
    * 9.3 [RQ.Iceberg.ExportPartition.Truncate.RepopulateAfterTruncate](#rqicebergexportpartitiontruncaterepopulateaftertruncate)
    * 9.4 [RQ.Iceberg.ExportPartition.Truncate.AfterDirectInsert](#rqicebergexportpartitiontruncateafterdirectinsert)
    * 9.5 [RQ.Iceberg.ExportPartition.MinMaxPruning](#rqicebergexportpartitionminmaxpruning)
* 10 [Source replica and ZooKeeper compatibility](#source-replica-and-zookeeper-compatibility)
    * 10.1 [RQ.Iceberg.ExportPartition.ZooKeeperCompat](#rqicebergexportpartitionzookeepercompat)

## Introduction

This specification defines requirements for **exporting partitions from `ReplicatedMergeTree` source tables into Apache Iceberg destinations** using ClickHouse's experimental `ALTER TABLE … EXPORT PARTITION … TO TABLE …` surface, when the destination is Iceberg on S3 (with or without an external REST / Glue catalog).

The experimental feature SHALL be gated by the server-level setting `allow_experimental_export_merge_tree_partition_feature` (default `0`). Subsequent direct writes against an Iceberg destination further require `allow_experimental_insert_into_iceberg`. When either gate is disabled, the corresponding statements SHALL fail with the standard "experimental feature disabled" error.

Regression tests live under the TestFlows package `iceberg.tests.export_partition`. The outer feature in `iceberg.tests.export_partition.feature` loads one sub-feature per Python module listed in its `MODULES` tuple and runs the same scenarios under multiple **catalog modes** (`no_catalog` / `rest` / `glue`) unless a module documents a narrower scope. Each requirement is attached directly to one or more scenarios that exercise it; the regression module that owns those scenarios is named in the requirement body for traceability.

[ClickHouse]: https://clickhouse.com

## Core export path

### RQ.Iceberg.ExportPartition.Sanity
version: 1.0

[ClickHouse] SHALL support the happy path of `ALTER TABLE … EXPORT PARTITION … TO TABLE …` from a `ReplicatedMergeTree` source into a compatible Iceberg destination such that:

* `EXPORT PARTITION ID '<id>'` exports exactly the rows that belong to that partition.
* `EXPORT PARTITION ALL` exports every active partition without skipping or duplicating rows.
* Multiple `EXPORT PARTITION` clauses chained in a single `ALTER` are accepted and produce one snapshot per partition.
* Row counts and representative column values read back from the Iceberg destination match the exported slice of the source under each catalog mode the product claims to support.
* `system.replicated_partition_exports` reflects `COMPLETED` for every successful export.

**Regression module:** `iceberg.tests.export_partition.sanity` (`sanity.py`).

### RQ.Iceberg.ExportPartition.Sanity.EmptyPartition
version: 1.0

[ClickHouse] SHALL accept `EXPORT PARTITION` against an empty partition without error:

* The export reaches `COMPLETED` even though no rows are written.
* The destination remains readable and reflects the empty contribution (no spurious data files appear).

### RQ.Iceberg.ExportPartition.Sanity.CrossReplicaInitiator
version: 1.0

[ClickHouse] SHALL allow any replica of a `ReplicatedMergeTree` source to issue `EXPORT PARTITION`:

* The chosen initiator may differ from the replica that originally inserted the data.
* The destination ends with the same row count regardless of which replica issued the `ALTER`.

## Partition and schema compatibility

### RQ.Iceberg.ExportPartition.PartitionCompatibility.AcceptedTransforms
version: 1.0

[ClickHouse] SHALL successfully export when the source `PARTITION BY` expression matches the Iceberg partition spec across the documented transforms:

* Identity partitioning, including compound identity over multiple columns.
* `year` / `month` / `day` / `hour` time-bucket transforms.
* `truncate[N]` on string columns.
* `bucket[N]` on integer columns.
* Compound specs that mix identity and a parametrised transform.

In every accepted case the destination's partition spec stays stable across exports and partition values written by ClickHouse match what an external Iceberg reader expects.

**Regression module:** `iceberg.tests.export_partition.partition_compatibility` (`partition_compatibility.py`).

### RQ.Iceberg.ExportPartition.PartitionCompatibility.MismatchRejection
version: 1.0

[ClickHouse] SHALL reject `EXPORT PARTITION` synchronously with `BAD_ARGUMENTS` when the source and destination partition specs disagree, including:

* Compound fields specified in different orders.
* A transform on one side and identity on the other for the same column.
* Different transform widths (for example `bucket[8]` vs `bucket[16]`, or `truncate[4]` vs `truncate[8]`).
* Different field counts (compound vs single-column).
* Source `PARTITION BY` expressions that have no Iceberg analogue (for example `intDiv`).
* Different partition columns entirely.
* Partitioned source paired with an unpartitioned Iceberg destination.

In every rejected case no Iceberg snapshot is created and the destination remains in its prior state.

### RQ.Iceberg.ExportPartition.DataTypes.Primitives
version: 1.0

[ClickHouse] SHALL export the following primitive types into their Iceberg equivalents and read them back unchanged through both ClickHouse and an external Iceberg reader:

* Integer types `Int16`, `Int32`, `Int64`, `UInt32`.
* Floating-point types `Float32` and `Float64`.
* Date / time types `Date`, `Date32`, `DateTime`, `DateTime64(3)`.
* `String` and `UUID`.

**Regression module:** `iceberg.tests.export_partition.datatypes` (`datatypes.py`).

### RQ.Iceberg.ExportPartition.DataTypes.Nullable
version: 1.0

[ClickHouse] SHALL preserve `Nullable(T)` semantics for any supported `T`:

* Explicit `NULL` values are exported as Iceberg nulls.
* Round-trip reads return `NULL` (not a default sentinel) for the same rows.
* Both numeric (`Nullable(Int64)`) and string-backed (`Nullable(String)`) cases are exercised.

### RQ.Iceberg.ExportPartition.DataTypes.Composite
version: 1.0

[ClickHouse] SHALL export the documented composite types into their Iceberg analogues:

* `Array(T)` for both numeric and string element types.
* `Map(K, V)` (verified for `Map(String, Int64)`).
* `Tuple(T1, T2, …)` mapped to an Iceberg struct, verified for a `(Int32, String)` tuple.

Element ordering and key/value pairings SHALL match the source after a round-trip.

### RQ.Iceberg.ExportPartition.DataTypes.UnsupportedRejection
version: 1.0

[ClickHouse] SHALL fail explicitly — and SHALL NOT silently coerce, downcast, or drop data — when an exported column has no supported Iceberg mapping in this release:

* Narrow integers `Int8` and `UInt8`.
* `Bool`.
* `FixedString(N)`.
* `Decimal(p, s)`.
* `Enum8` (and its variants).
* `LowCardinality(T)`.

The rejection SHALL fire either when the destination is created or when the export is issued, before any data files are written.

## Committed Iceberg metadata

### RQ.Iceberg.ExportPartition.ManifestIntegrity.SnapshotChain
version: 1.0

[ClickHouse] SHALL extend the destination's snapshot list by exactly one append snapshot per successful export, and the resulting Iceberg metadata SHALL be internally consistent with the rows and files written:

* The new snapshot's `parent_snapshot_id` SHALL point at the previously current snapshot.
* The snapshot summary's `total-records` SHALL match the row count contributed by the export.
* Repeated exports SHALL form a single linear chain, never a branch.

**Regression module:** `iceberg.tests.export_partition.manifest_integrity` (`manifest_integrity.py`).

### RQ.Iceberg.ExportPartition.ManifestIntegrity.PartitionSpec
version: 1.0

[ClickHouse] SHALL emit manifests whose partition-spec field references the same source columns the MergeTree `PARTITION BY` was defined on, so external pruning by partition value works without manual remapping.

### RQ.Iceberg.ExportPartition.ManifestIntegrity.ColumnStats
version: 1.0

[ClickHouse] SHALL populate per–data-file column statistics in committed manifests sufficient for selective reads:

* `value_counts`, `null_value_counts`, `lower_bounds`, and `upper_bounds` are present for every required column on every data file.
* `value_counts` summed across all data files SHALL equal the total row count contributed by the export.

### RQ.Iceberg.ExportPartition.ManifestIntegrity.PathLayout
version: 1.0

[ClickHouse] SHALL write every data file under the destination Iceberg table's configured S3 prefix; no file SHALL escape that prefix or land in another table's directory.

### RQ.Iceberg.ExportPartition.ManifestIntegrity.ExternalReader
version: 1.0

[ClickHouse]'s exported metadata SHALL be interoperable, not just self-consistent. An independent Iceberg reader (PyIceberg, in the regression suite) SHALL list the snapshots, read the data files, and return row counts and column values that match the source slice.

### RQ.Iceberg.ExportPartition.CatalogIntegration.NoCatalog
version: 1.0

[ClickHouse] SHALL produce a `no_catalog` (`IcebergS3`) destination — where the warehouse `metadata.json` pointer is managed directly, with no external catalog — whose committed data is independently readable:

* The committed slice can be read through the `icebergS3` table function pointed at the same warehouse prefix.
* Dropping the destination table from ClickHouse SHALL NOT delete the committed data; the same files remain readable through `icebergS3`.

**Regression module:** `iceberg.tests.export_partition.catalogs` (`catalogs.py`).

### RQ.Iceberg.ExportPartition.CatalogIntegration.RestGlue
version: 1.0

[ClickHouse] SHALL commit exports through the same catalog-aware metadata paths used in production for **REST** and **Glue** (Hive-metastore-compatible) catalogs, registering the export with the configured catalog:

* After commit the new snapshot SHALL be visible through the same catalog object operators use for production (REST or Glue).
* An external Iceberg reader connected to the same catalog SHALL list the snapshot and read the data files written by ClickHouse.

## Transactions, idempotency, and concurrency

### RQ.Iceberg.ExportPartition.Transactions.SnapshotChain
version: 1.0

[ClickHouse] SHALL treat each successful Iceberg commit from `EXPORT PARTITION` as an **append** snapshot with monotonic snapshot / sequence semantics relative to the prior table state, and SHALL append exactly one snapshot per successful `EXPORT PARTITION` with no gaps or branches:

* Sequential exports of distinct partitions produce one append snapshot each, in order.
* Each new snapshot points at the previous one as its parent.

**Regression module:** `iceberg.tests.export_partition.transactions` (`transactions.py`).

### RQ.Iceberg.ExportPartition.Transactions.Idempotency
version: 1.0

[ClickHouse] SHALL guard against accidental duplicate commits via a ZooKeeper-backed live manifest keyed on `(source_table, destination_table, partition_id)`:

* A second `EXPORT PARTITION` for the same key submitted within `export_merge_tree_partition_manifest_ttl` SHALL be rejected (`EXPORT_PARTITION_ALREADY_EXPORTED`, historically `BAD_ARGUMENTS`).
* Setting `export_merge_tree_partition_force_export = 1` SHALL bypass the gate, at the operator's documented risk.
* Once `export_merge_tree_partition_manifest_ttl` has elapsed (or the prior export has been removed), the same key SHALL be exportable again.

### RQ.Iceberg.ExportPartition.Transactions.CrashRecovery
version: 1.0

[ClickHouse] SHALL keep the destination consistent across each documented commit-path failpoint:

* `iceberg_writes_non_retry_cleanup` — pre-publish failure leaves no half-published snapshot; the retry succeeds and produces exactly one append.
* `iceberg_export_after_commit_before_zk_completed` — a crash window between a successful Iceberg commit and the `COMPLETED` status update SHALL be detected on retry via the `clickhouse.export-partition-transaction-id` marker, so the recovery does not double-commit.
* `export_partition_status_change_throw` — a manifest status transition failure SHALL be retried internally without producing a duplicate commit.
* `iceberg_writes_post_publish_throw` — an exception thrown after a successful publish SHALL not invalidate the committed snapshot; the next read still sees the data.

### RQ.Iceberg.ExportPartition.ConcurrentWrites.MultiStatement
version: 1.0

[ClickHouse] SHALL serialize concurrent export work — including multiple `EXPORT PARTITION` clauses chained in one client batch — so that the destination's snapshot history stays **linear append-only** without corrupting metadata:

* Each distinct partition produces its own append snapshot; the snapshot chain remains linear.
* A duplicate export of the same partition inside a single `ALTER` SHALL commit at most once — repeats are absorbed by the same idempotency key as the cross-statement guard in `Transactions.Idempotency`.

**Regression module:** `iceberg.tests.export_partition.concurrent_writes` (`concurrent_writes.py`).

### RQ.Iceberg.ExportPartition.ConcurrentWrites.Interleaving
version: 1.0

[ClickHouse] SHALL keep direct `INSERT INTO <iceberg_table>` writes that happen after a scheduled but not-yet-committed `EXPORT PARTITION` from leaking into the export's snapshot:

* The export's snapshot summary reflects only the rows the export was scheduled to write.
* The direct insert lands in its own subsequent snapshot.

## Evolution and physical layout

### RQ.Iceberg.ExportPartition.SchemaEvolution.AcceptedAlterations
version: 1.0

[ClickHouse] SHALL permit the following destination schema changes between exports and SHALL preserve compatibility on the next `EXPORT PARTITION`:

* Adding a column on both sides; the new column receives null / default values for previously exported rows.
* Dropping a column on both sides; subsequent exports omit the dropped column.
* Renaming a column on both sides; previously exported rows remain readable under the new name.
* Widening a numeric column (verified for `Int32 → Int64`); already-exported rows remain readable, new exports use the wider type.

**Regression module:** `iceberg.tests.export_partition.schema_evolution` (`schema_evolution.py`).

### RQ.Iceberg.ExportPartition.SchemaEvolution.RejectedAlterations
version: 1.0

[ClickHouse] SHALL reject schema changes that would corrupt destination metadata or break round-trip reads:

* Schema drift on the source alone (without the matching destination change) SHALL fail the export rather than commit a mismatched snapshot.

### RQ.Iceberg.ExportPartition.SchemaEvolution.SchemaHistory
version: 1.0

[ClickHouse] SHALL surface destination schema changes as new entries in the Iceberg schema history. After an `ADD COLUMN` and re-export, the destination table SHALL expose at least one additional schema id reflecting the new column.

### RQ.Iceberg.ExportPartition.PartitionSpecEvolution
version: 1.0

[ClickHouse] SHALL maintain stable, correct partition metadata across sequential exports when the MergeTree and Iceberg tables share a fixed partition expression:

* A single Iceberg partition spec is reused across multiple exports rather than evolved with each commit.
* Partition tuples written into manifests match the originating MergeTree partition id.
* Multi-column partition specs preserve both columns across every export.

**Regression module:** `iceberg.tests.export_partition.partition_spec_evolution` (`partition_spec_evolution.py`).

### RQ.Iceberg.ExportPartition.StoragePaths.PathFormat
version: 1.0

[ClickHouse] SHALL honour `write_full_path_in_iceberg_metadata` and respect both path-format modes for `metadata.json` location strings:

* With `write_full_path_in_iceberg_metadata = 1` the `metadata.json` location SHALL be a fully-qualified `s3://…` URI.
* With the default (`= 0`) the `metadata.json` location SHALL be bucket-relative (no scheme prefix).

In both modes the destination remains readable through ClickHouse and through an external reader.

**Regression module:** `iceberg.tests.export_partition.storage_paths` (`storage_paths.py`).

### RQ.Iceberg.ExportPartition.StoragePaths.DeepPrefix
version: 1.0

[ClickHouse] SHALL accept Iceberg destinations whose warehouse prefix is many segments deep, and SHALL round-trip reads cleanly without truncating or rewriting the prefix.

### RQ.Iceberg.ExportPartition.StoragePaths.Isolation
version: 1.0

[ClickHouse] SHALL keep multiple Iceberg destinations under the same bucket strictly isolated:

* No data file or metadata file written for one destination appears under another's prefix.
* An export to one destination SHALL NOT modify another destination's snapshot list.

## Failure handling and multi-replica behaviour

### RQ.Iceberg.ExportPartition.DisasterRecovery.MovesControl
version: 1.0

[ClickHouse] SHALL surface export lifecycle states through `system.replicated_partition_exports` and SHALL hold an in-flight export at `PENDING` while `SYSTEM STOP MOVES` is in effect, resuming it to `COMPLETED` after `SYSTEM START MOVES`, with no rows lost or duplicated and no partial Iceberg snapshot left behind.

**Regression module:** `iceberg.tests.export_partition.disaster_recovery` (`disaster_recovery.py`).

### RQ.Iceberg.ExportPartition.DisasterRecovery.KillExport
version: 1.0

[ClickHouse] SHALL respect `KILL EXPORT PARTITION` from any documented in-flight phase:

* While moves are stopped (task held at `PENDING`), `KILL` transitions the row to `KILLED`.
* While the commit is being attempted, `KILL` still terminates the task and the row reaches `KILLED`.

In both cases no second snapshot ever appears, regardless of whether the kill arrived before or during the publish step.

### RQ.Iceberg.ExportPartition.DisasterRecovery.InvalidInputs
version: 1.0

[ClickHouse] SHALL reject malformed export inputs without leaving residue:

* `EXPORT PARTITION` to a destination table that does not exist SHALL fail synchronously with a clear error.
* `EXPORT PARTITION ID '<missing>'` for a partition that has no parts SHALL be a safe no-op — no failed task row, no partial snapshot, no orphaned files.

### RQ.Iceberg.ExportPartition.MultiReplicaRecovery.CrossReplicaConcurrency
version: 1.0

[ClickHouse] SHALL coordinate concurrent exports issued by different replicas of the same `ReplicatedMergeTree` table, preserving idempotency and snapshot linearity and converging to at most one successful commit per guarded export key:

* Two replicas exporting **different** partitions to the same destination SHALL produce two append snapshots in a linear chain with no row loss.
* Two replicas issuing the **same** export key SHALL produce exactly one snapshot — the duplicate is rejected by the cross-replica idempotency guard.

**Regression module:** `iceberg.tests.export_partition.multi_replica_recovery` (`multi_replica_recovery.py`).

### RQ.Iceberg.ExportPartition.MultiReplicaRecovery.InitiatorFailover
version: 1.0

[ClickHouse] SHALL allow a peer replica to finish an in-flight export when the initiator dies mid-commit:

* The surviving replica picks the work up from the Keeper-stashed manifest.
* The `clickhouse.export-partition-transaction-id` marker prevents a double-commit if the dead initiator had already published.
* The destination ends with exactly one append snapshot for the partition.

### RQ.Iceberg.ExportPartition.MultiReplicaRecovery.ZooKeeperBounce
version: 1.0

[ClickHouse] SHALL recover an in-flight export from a mid-commit ZooKeeper disturbance:

* Both a graceful `zkServer.sh restart` and a SIGKILL + `docker start` (single-replica and cross-replica variants) SHALL leave the export converging to `COMPLETED`.
* No replica observes a duplicate snapshot during or after the bounce.
* When two replicas were exporting different partitions, both still produce their own append snapshots in a linear chain.

### RQ.Iceberg.ExportPartition.MultiReplicaRecovery.RandomisedChaos
version: 1.0

[ClickHouse] SHALL keep the snapshot chain linear and consistent under randomised replica disruption (stress-only, gated by `--stress`):

* Killing a replica at randomly-chosen export-lifecycle phases (before commit, during commit, after `COMPLETED`) with random kill modes and restart policies SHALL converge to a terminal status with at most one snapshot per partition; for kills after `COMPLETED` the destination state SHALL remain unchanged.
* Repeatedly bouncing the initiating replica during a single export SHALL still produce at most one append snapshot.
* Exporting many partitions concurrently while a chaos thread randomly bounces a replica SHALL produce a linear, txn-id-tagged snapshot chain with no double-commits.

### RQ.Iceberg.ExportPartition.MultiReplicaRecovery.SettingDisabledFailover
version: 1.0

[ClickHouse] SHALL allow a peer replica to finish an in-flight export when the initiating client authenticates as a ClickHouse user whose profile fixes `allow_experimental_insert_into_iceberg = 0`, while `default` keeps the gate enabled on every replica:

* The initiating session SHALL parse and schedule `ALTER TABLE … EXPORT PARTITION` because the per-query setting overrides the restrictive profile default.
* The export SHALL reach `COMPLETED` and the destination SHALL hold every source row once the peer applies the gate-enabled profile for its background work.
* The `source_replica` recorded in `system.replicated_partition_exports` SHALL name the **initiating** replica encoded in the Keeper manifest when `ALTER TABLE … EXPORT PARTITION` runs (ClickHouse documents this column as “Name of the source replica.”); it SHALL NOT be rewritten when a peer replica performs the Iceberg commit work.

Iceberg regression containers bind one host `users.d` directory into every replica service; overriding `profiles/default` on “just clickhouse1” is not replica-local, so the regression adds a dedicated restrictive profile and a matching **SQL** ``CREATE USER`` identity (``GRANT`` cannot extend ``users_xml``-only users).

**Regression module:** `iceberg.tests.export_partition.replicas` (`replicas.py`).

## Observability and export settings

### RQ.Iceberg.ExportPartition.SystemMonitoring.ReplicatedPartitionExports
version: 1.0

[ClickHouse] SHALL fill every documented column of `system.replicated_partition_exports` for a successful export, so the row is sufficient on its own to identify the source, the destination, the partition, the initiating replica, and the resulting status without consulting other system tables.

**Regression module:** `iceberg.tests.export_partition.system_monitoring` (`system_monitoring.py`).

### RQ.Iceberg.ExportPartition.SystemMonitoring.PartLog
version: 1.0

[ClickHouse] SHALL append one `system.part_log` row with `event_type = 'ExportPart'` for each part that is successfully exported as part of an `EXPORT PARTITION` task.

### RQ.Iceberg.ExportPartition.SystemMonitoring.ProfileEvents
version: 1.0

[ClickHouse] SHALL increment the documented `ProfileEvents` counters for a successful export, including `PartsExports` and the `ExportPartitionZooKeeper*` family that tracks Keeper round-trips made by the commit path.

### RQ.Iceberg.ExportPartition.SystemMonitoring.KilledProvenance
version: 1.0

[ClickHouse] SHALL preserve provenance and diagnostic fields on a killed export so the row remains attributable after the fact:

* `source_replica`, `create_time`, and identifying columns SHALL still match the original initiator and timing once the row has transitioned to `KILLED`.
* When the kill lands during the commit window, the same provenance fields and any diagnostic counters that were already populated SHALL remain readable for post-mortem analysis.

### RQ.Iceberg.ExportPartition.Settings.ParquetCompression
version: 1.0

[ClickHouse] SHALL forward `output_format_parquet_compression_method` to the Parquet writer used by `EXPORT PARTITION`, so the compression codec recorded inside committed data files reflects the requested setting.

## Post-export destination operations

### RQ.Iceberg.ExportPartition.DirectWrites
version: 1.0

[ClickHouse] SHALL allow `INSERT INTO <iceberg_table>` against an Iceberg destination previously populated by `EXPORT PARTITION` (when `allow_experimental_insert_into_iceberg` is on), and SHALL keep the snapshot chain consistent when exports and direct inserts alternate:

* An `INSERT` after an export adds its own append snapshot without rewriting the export's snapshot.
* Alternating `EXPORT` and `INSERT` operations produce one snapshot per operation, in order, all readable through ClickHouse and external readers.

**Regression module:** `iceberg.tests.export_partition.direct_writes` (`direct_writes.py`).

### RQ.Iceberg.ExportPartition.Truncate
version: 1.0

[ClickHouse] SHALL support `TRUNCATE TABLE` against an Iceberg destination previously populated by `EXPORT PARTITION` (when truncate is enabled), clearing readable rows while leaving the table itself usable for subsequent writes.

**Regression module:** `iceberg.tests.export_partition.truncate` (`truncate.py`).

### RQ.Iceberg.ExportPartition.Truncate.RepopulateAfterTruncate
version: 1.0

[ClickHouse] SHALL allow a fresh `EXPORT PARTITION` to repopulate a truncated destination:

* The first export after a `TRUNCATE` produces a new append snapshot.
* Subsequent reads return the freshly-exported rows; no rows from before the truncate leak through.

### RQ.Iceberg.ExportPartition.Truncate.AfterDirectInsert
version: 1.0

[ClickHouse] SHALL behave correctly when `TRUNCATE TABLE` runs after a direct `INSERT INTO <iceberg_table>` (with no preceding export), clearing the inserted rows and leaving the destination empty and reusable.

### RQ.Iceberg.ExportPartition.MinMaxPruning
version: 1.0

[ClickHouse] SHALL write Iceberg manifest column statistics (`lower_bounds` / `upper_bounds`) during export such that reads of the destination with selective predicates exhibit min/max pruning — fewer files touched and reduced `read_rows` than a full scan — when data layout makes pruning possible. This SHALL hold both for equality predicates and for range predicates.

**Regression module:** `iceberg.tests.export_partition.minmax_pruning` (`minmax_pruning.py`).

## Source replica and ZooKeeper compatibility

### RQ.Iceberg.ExportPartition.ZooKeeperCompat
version: 1.0

[ClickHouse] SHALL recreate the **`/exports`** coordination subtree under a `ReplicatedMergeTree` table's ZooKeeper path during normal replica attach / restart flows, so tables whose ZooKeeper state predates the export feature — or has had `/exports` deleted by an operator — become eligible for `EXPORT PARTITION` after a documented recovery step (`SYSTEM RESTART REPLICA` or full server restart) without manual ZooKeeper surgery.

**Regression module:** `iceberg.tests.export_partition.zk_compat` (`zk_compat.py`).
