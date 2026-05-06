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
        "* `EXPORT PARTITION ID '<id>'` exports exactly the rows that belong to that partition.\n"
        "* `EXPORT PARTITION ALL` exports every active partition without skipping or duplicating rows.\n"
        "* Multiple `EXPORT PARTITION` clauses chained in a single `ALTER` are accepted and produce one snapshot per partition.\n"
        "* Row counts and representative column values read back from the Iceberg destination match the exported slice of the source under each catalog mode the product claims to support.\n"
        "* `system.replicated_partition_exports` reflects `COMPLETED` for every successful export.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.sanity` (`sanity.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.1",
)

RQ_Iceberg_ExportPartition_Sanity_EmptyPartition = Requirement(
    name="RQ.Iceberg.ExportPartition.Sanity.EmptyPartition",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL accept `EXPORT PARTITION` against an empty partition without error:\n"
        "\n"
        "* The export reaches `COMPLETED` even though no rows are written.\n"
        "* The destination remains readable and reflects the empty contribution (no spurious data files appear).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.2",
)

RQ_Iceberg_ExportPartition_Sanity_CrossReplicaInitiator = Requirement(
    name="RQ.Iceberg.ExportPartition.Sanity.CrossReplicaInitiator",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL allow any replica of a `ReplicatedMergeTree` source to issue `EXPORT PARTITION`:\n"
        "\n"
        "* The chosen initiator may differ from the replica that originally inserted the data.\n"
        "* The destination ends with the same row count regardless of which replica issued the `ALTER`.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.3",
)

RQ_Iceberg_ExportPartition_PartitionCompatibility = Requirement(
    name="RQ.Iceberg.ExportPartition.PartitionCompatibility",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL enforce compatibility between the MergeTree `PARTITION BY` definition (including supported partition transforms) and the Iceberg destination's partition spec. Accepted pairings SHALL export successfully; mismatched or unsupported pairings SHALL be rejected with a clear error (typically `BAD_ARGUMENTS`) before any Iceberg metadata is committed.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.partition_compatibility` (`partition_compatibility.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.1",
)

RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms = Requirement(
    name="RQ.Iceberg.ExportPartition.PartitionCompatibility.AcceptedTransforms",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL successfully export when the source `PARTITION BY` expression matches the Iceberg partition spec across the documented transforms:\n"
        "\n"
        "* Identity partitioning, including compound identity over multiple columns.\n"
        "* `year` / `month` / `day` / `hour` time-bucket transforms.\n"
        "* `truncate[N]` on string columns.\n"
        "* `bucket[N]` on integer columns.\n"
        "* Compound specs that mix identity and a parametrised transform.\n"
        "\n"
        "In every accepted case the destination's partition spec stays stable across exports and partition values written by ClickHouse match what an external Iceberg reader expects.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.2",
)

RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection = Requirement(
    name="RQ.Iceberg.ExportPartition.PartitionCompatibility.MismatchRejection",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject `EXPORT PARTITION` synchronously with `BAD_ARGUMENTS` when the source and destination partition specs disagree, including:\n"
        "\n"
        "* Compound fields specified in different orders.\n"
        "* A transform on one side and identity on the other for the same column.\n"
        "* Different transform widths (for example `bucket[8]` vs `bucket[16]`, or `truncate[4]` vs `truncate[8]`).\n"
        "* Different field counts (compound vs single-column).\n"
        "* Source `PARTITION BY` expressions that have no Iceberg analogue (for example `intDiv`).\n"
        "* Different partition columns entirely.\n"
        "* Partitioned source paired with an unpartitioned Iceberg destination.\n"
        "\n"
        "In every rejected case no Iceberg snapshot is created and the destination remains in its prior state.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.3",
)

RQ_Iceberg_ExportPartition_DataTypes = Requirement(
    name="RQ.Iceberg.ExportPartition.DataTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL map ClickHouse column types used in the export to Iceberg types that preserve the intended values for every supported primitive and nested layout. Types with no supported Iceberg mapping SHALL fail explicitly at destination-creation or export time; the system SHALL NOT silently coerce, downcast, or drop data.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.datatypes` (`datatypes.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.4",
)

RQ_Iceberg_ExportPartition_DataTypes_Primitives = Requirement(
    name="RQ.Iceberg.ExportPartition.DataTypes.Primitives",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL export the following primitive types into their Iceberg equivalents and read them back unchanged through both ClickHouse and an external Iceberg reader:\n"
        "\n"
        "* Integer types `Int16`, `Int32`, `Int64`, `UInt32`.\n"
        "* Floating-point types `Float32` and `Float64`.\n"
        "* Date / time types `Date`, `Date32`, `DateTime`, `DateTime64(3)`.\n"
        "* `String` and `UUID`.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.5",
)

RQ_Iceberg_ExportPartition_DataTypes_Nullable = Requirement(
    name="RQ.Iceberg.ExportPartition.DataTypes.Nullable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL preserve `Nullable(T)` semantics for any supported `T`:\n"
        "\n"
        "* Explicit `NULL` values are exported as Iceberg nulls.\n"
        "* Round-trip reads return `NULL` (not a default sentinel) for the same rows.\n"
        "* Both numeric (`Nullable(Int64)`) and string-backed (`Nullable(String)`) cases are exercised.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.6",
)

RQ_Iceberg_ExportPartition_DataTypes_Composite = Requirement(
    name="RQ.Iceberg.ExportPartition.DataTypes.Composite",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL export the documented composite types into their Iceberg analogues:\n"
        "\n"
        "* `Array(T)` for both numeric and string element types.\n"
        "* `Map(K, V)` (verified for `Map(String, Int64)`).\n"
        "* `Tuple(T1, T2, …)` mapped to an Iceberg struct, verified for a `(Int32, String)` tuple.\n"
        "\n"
        "Element ordering and key/value pairings SHALL match the source after a round-trip.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.7",
)

RQ_Iceberg_ExportPartition_DataTypes_UnsupportedRejection = Requirement(
    name="RQ.Iceberg.ExportPartition.DataTypes.UnsupportedRejection",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject `EXPORT PARTITION` for column types that have no supported Iceberg mapping in this release:\n"
        "\n"
        "* Narrow integers `Int8` and `UInt8`.\n"
        "* `Bool`.\n"
        "* `FixedString(N)`.\n"
        "* `Decimal(p, s)`.\n"
        "* `Enum8` (and its variants).\n"
        "* `LowCardinality(T)`.\n"
        "\n"
        "The rejection SHALL fire either when the destination is created or when the export is issued, before any data files are written.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.8",
)

RQ_Iceberg_ExportPartition_ManifestIntegrity = Requirement(
    name="RQ.Iceberg.ExportPartition.ManifestIntegrity",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL produce Iceberg metadata after each successful export such that an external Iceberg reader can confirm snapshot lineage, summary statistics, manifest stats, partition spec references, and physical file layout are all internally consistent with the rows and files written.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.manifest_integrity` (`manifest_integrity.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.1",
)

RQ_Iceberg_ExportPartition_ManifestIntegrity_SnapshotChain = Requirement(
    name="RQ.Iceberg.ExportPartition.ManifestIntegrity.SnapshotChain",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL extend the destination's snapshot list by exactly one append snapshot per successful export:\n"
        "\n"
        "* The new snapshot's `parent_snapshot_id` SHALL point at the previously current snapshot.\n"
        "* The snapshot summary's `total-records` SHALL match the row count contributed by the export.\n"
        "* Repeated exports SHALL form a single linear chain, never a branch.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.2",
)

RQ_Iceberg_ExportPartition_ManifestIntegrity_PartitionSpec = Requirement(
    name="RQ.Iceberg.ExportPartition.ManifestIntegrity.PartitionSpec",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL emit manifests whose partition-spec field references the same source columns the MergeTree `PARTITION BY` was defined on, so external pruning by partition value works without manual remapping.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.3",
)

RQ_Iceberg_ExportPartition_ManifestIntegrity_ColumnStats = Requirement(
    name="RQ.Iceberg.ExportPartition.ManifestIntegrity.ColumnStats",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL populate per–data-file column statistics in committed manifests sufficient for selective reads:\n"
        "\n"
        "* `value_counts`, `null_value_counts`, `lower_bounds`, and `upper_bounds` are present for every required column on every data file.\n"
        "* `value_counts` summed across all data files SHALL equal the total row count contributed by the export.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.4",
)

RQ_Iceberg_ExportPartition_ManifestIntegrity_PathLayout = Requirement(
    name="RQ.Iceberg.ExportPartition.ManifestIntegrity.PathLayout",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL write every data file under the destination Iceberg table's configured S3 prefix; no file SHALL escape that prefix or land in another table's directory.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.5",
)

RQ_Iceberg_ExportPartition_ManifestIntegrity_ExternalReader = Requirement(
    name="RQ.Iceberg.ExportPartition.ManifestIntegrity.ExternalReader",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s exported metadata SHALL be interoperable, not just self-consistent. An independent Iceberg reader (PyIceberg, in the regression suite) SHALL list the snapshots, read the data files, and return row counts and column values that match the source slice.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.6",
)

RQ_Iceberg_ExportPartition_CatalogIntegration = Requirement(
    name="RQ.Iceberg.ExportPartition.CatalogIntegration",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL commit exports through the same catalog-aware metadata paths used in production for **REST** and **Glue** (Hive metastore compatible) catalogs, and SHALL preserve a usable on-disk layout in **no-catalog** mode where the warehouse `metadata.json` pointer is managed directly.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.catalogs` (`catalogs.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.7",
)

RQ_Iceberg_ExportPartition_CatalogIntegration_NoCatalog = Requirement(
    name="RQ.Iceberg.ExportPartition.CatalogIntegration.NoCatalog",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL produce a `no_catalog` (`IcebergS3`) destination whose committed data is independently readable:\n"
        "\n"
        "* The committed slice can be read through the `icebergS3` table function pointed at the same warehouse prefix.\n"
        "* Dropping the destination table from ClickHouse SHALL NOT delete the committed data; the same files remain readable through `icebergS3`.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.8",
)

RQ_Iceberg_ExportPartition_CatalogIntegration_RestGlue = Requirement(
    name="RQ.Iceberg.ExportPartition.CatalogIntegration.RestGlue",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL register the export with the configured external catalog:\n"
        "\n"
        "* After commit the new snapshot SHALL be visible through the same catalog object operators use for production (REST or Glue).\n"
        "* An external Iceberg reader connected to the same catalog SHALL list the snapshot and read the data files written by ClickHouse.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.9",
)

RQ_Iceberg_ExportPartition_Transactions = Requirement(
    name="RQ.Iceberg.ExportPartition.Transactions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL treat each successful Iceberg commit from `EXPORT PARTITION` as an **append** snapshot with monotonic snapshot / sequence semantics relative to the prior table state, and SHALL preserve atomicity of the commit even when the commit path is interrupted at documented failure-injection points.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.transactions` (`transactions.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.1",
)

RQ_Iceberg_ExportPartition_Transactions_SnapshotChain = Requirement(
    name="RQ.Iceberg.ExportPartition.Transactions.SnapshotChain",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL append exactly one snapshot per successful `EXPORT PARTITION`, with no gaps or branches:\n"
        "\n"
        "* Sequential exports of distinct partitions produce one append snapshot each, in order.\n"
        "* Each new snapshot points at the previous one as its parent.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.2",
)

RQ_Iceberg_ExportPartition_Transactions_Idempotency = Requirement(
    name="RQ.Iceberg.ExportPartition.Transactions.Idempotency",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL guard against accidental duplicate commits via a ZooKeeper-backed live manifest keyed on `(source_table, destination_table, partition_id)`:\n"
        "\n"
        "* A second `EXPORT PARTITION` for the same key submitted within `export_merge_tree_partition_manifest_ttl` SHALL be rejected (typically `BAD_ARGUMENTS`).\n"
        "* Setting `export_merge_tree_partition_force_export = 1` SHALL bypass the gate, at the operator's documented risk.\n"
        "* Once `export_merge_tree_partition_manifest_ttl` has elapsed (or the prior export has been removed), the same key SHALL be exportable again.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.3",
)

RQ_Iceberg_ExportPartition_Transactions_CrashRecovery = Requirement(
    name="RQ.Iceberg.ExportPartition.Transactions.CrashRecovery",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL keep the destination consistent across each documented commit-path failpoint:\n"
        "\n"
        "* `iceberg_writes_non_retry_cleanup` — pre-publish failure leaves no half-published snapshot; the retry succeeds and produces exactly one append.\n"
        "* `iceberg_export_after_commit_before_zk_completed` — a crash window between a successful Iceberg commit and the `COMPLETED` status update SHALL be detected on retry via the `clickhouse.export-partition-transaction-id` marker, so the recovery does not double-commit.\n"
        "* `export_partition_status_change_throw` — a manifest status transition failure SHALL be retried internally without producing a duplicate commit.\n"
        "* `iceberg_writes_post_publish_throw` — an exception thrown after a successful publish SHALL not invalidate the committed snapshot; the next read still sees the data.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.4",
)

RQ_Iceberg_ExportPartition_ConcurrentWrites = Requirement(
    name="RQ.Iceberg.ExportPartition.ConcurrentWrites",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL serialize concurrent export work so that multiple partition exports targeting the same Iceberg destination produce a **linear append-only** snapshot history without corrupting metadata, and SHALL keep direct writes (`INSERT`) interleaved with scheduled exports correctly attributed to their own snapshots.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.concurrent_writes` (`concurrent_writes.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.5",
)

RQ_Iceberg_ExportPartition_ConcurrentWrites_MultiStatement = Requirement(
    name="RQ.Iceberg.ExportPartition.ConcurrentWrites.MultiStatement",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL handle multiple `EXPORT PARTITION` clauses chained in one client batch correctly:\n"
        "\n"
        "* Each distinct partition produces its own append snapshot; the snapshot chain remains linear.\n"
        "* A duplicate export of the same partition inside a single `ALTER` SHALL commit at most once — repeats are absorbed by the same idempotency key as the cross-statement guard in `Transactions.Idempotency`.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.6",
)

RQ_Iceberg_ExportPartition_ConcurrentWrites_Interleaving = Requirement(
    name="RQ.Iceberg.ExportPartition.ConcurrentWrites.Interleaving",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL keep direct `INSERT INTO <iceberg_table>` writes that happen after a scheduled but not-yet-committed `EXPORT PARTITION` from leaking into the export's snapshot:\n"
        "\n"
        "* The export's snapshot summary reflects only the rows the export was scheduled to write.\n"
        "* The direct insert lands in its own subsequent snapshot.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.7",
)

RQ_Iceberg_ExportPartition_SchemaEvolution = Requirement(
    name="RQ.Iceberg.ExportPartition.SchemaEvolution",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL allow documented schema evolution on the Iceberg destination and the `ReplicatedMergeTree` source such that subsequent `EXPORT PARTITION` operations succeed only when the schemas remain compatible per Iceberg metadata rules; unsupported alterations SHALL be rejected deterministically.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.schema_evolution` (`schema_evolution.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.1",
)

RQ_Iceberg_ExportPartition_SchemaEvolution_AcceptedAlterations = Requirement(
    name="RQ.Iceberg.ExportPartition.SchemaEvolution.AcceptedAlterations",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL permit the following destination schema changes between exports and SHALL preserve compatibility on the next `EXPORT PARTITION`:\n"
        "\n"
        "* Adding a column on both sides; the new column receives null / default values for previously exported rows.\n"
        "* Dropping a column on both sides; subsequent exports omit the dropped column.\n"
        "* Widening a numeric column (verified for `Int32 → Int64`); already-exported rows remain readable, new exports use the wider type.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.2",
)

RQ_Iceberg_ExportPartition_SchemaEvolution_RejectedAlterations = Requirement(
    name="RQ.Iceberg.ExportPartition.SchemaEvolution.RejectedAlterations",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject schema changes that would corrupt destination metadata or break round-trip reads:\n"
        "\n"
        "* `RENAME COLUMN` on an Iceberg destination SHALL be rejected.\n"
        "* Schema drift on the source alone (without the matching destination change) SHALL fail the export rather than commit a mismatched snapshot.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.3",
)

RQ_Iceberg_ExportPartition_SchemaEvolution_SchemaHistory = Requirement(
    name="RQ.Iceberg.ExportPartition.SchemaEvolution.SchemaHistory",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL surface destination schema changes as new entries in the Iceberg schema history. After an `ADD COLUMN` and re-export, the destination table SHALL expose at least one additional schema id reflecting the new column.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.4",
)

RQ_Iceberg_ExportPartition_PartitionSpecEvolution = Requirement(
    name="RQ.Iceberg.ExportPartition.PartitionSpecEvolution",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL maintain stable, correct partition metadata across sequential exports when the MergeTree and Iceberg tables share a fixed partition expression:\n"
        "\n"
        "* A single Iceberg partition spec is reused across multiple exports rather than evolved with each commit.\n"
        "* Partition tuples written into manifests match the originating MergeTree partition id.\n"
        "* Multi-column partition specs preserve both columns across every export.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.partition_spec_evolution` (`partition_spec_evolution.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.5",
)

RQ_Iceberg_ExportPartition_StoragePaths = Requirement(
    name="RQ.Iceberg.ExportPartition.StoragePaths",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL honour `write_full_path_in_iceberg_metadata` and related path rules when laying out Iceberg table locations and metadata on S3, including deep prefix hierarchies and multiple isolated destinations under one bucket, so committed paths remain consistent with the configured policy.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.storage_paths` (`storage_paths.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.6",
)

RQ_Iceberg_ExportPartition_StoragePaths_PathFormat = Requirement(
    name="RQ.Iceberg.ExportPartition.StoragePaths.PathFormat",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL respect both path-format modes for `metadata.json` location strings:\n"
        "\n"
        "* With `write_full_path_in_iceberg_metadata = 1` the `metadata.json` location SHALL be a fully-qualified `s3://…` URI.\n"
        "* With the default (`= 0`) the `metadata.json` location SHALL be bucket-relative (no scheme prefix).\n"
        "\n"
        "In both modes the destination remains readable through ClickHouse and through an external reader.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.7",
)

RQ_Iceberg_ExportPartition_StoragePaths_DeepPrefix = Requirement(
    name="RQ.Iceberg.ExportPartition.StoragePaths.DeepPrefix",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL accept Iceberg destinations whose warehouse prefix is many segments deep, and SHALL round-trip reads cleanly without truncating or rewriting the prefix.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.8",
)

RQ_Iceberg_ExportPartition_StoragePaths_Isolation = Requirement(
    name="RQ.Iceberg.ExportPartition.StoragePaths.Isolation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL keep multiple Iceberg destinations under the same bucket strictly isolated:\n"
        "\n"
        "* No data file or metadata file written for one destination appears under another's prefix.\n"
        "* An export to one destination SHALL NOT modify another destination's snapshot list.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.9",
)

RQ_Iceberg_ExportPartition_DisasterRecovery = Requirement(
    name="RQ.Iceberg.ExportPartition.DisasterRecovery",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL surface export lifecycle states through `system.replicated_partition_exports` and SHALL recover or fail cleanly under operator actions and invalid inputs without committing a partial Iceberg snapshot in success cases where the implementation promises all-or-nothing behaviour.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.disaster_recovery` (`disaster_recovery.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.1",
)

RQ_Iceberg_ExportPartition_DisasterRecovery_MovesControl = Requirement(
    name="RQ.Iceberg.ExportPartition.DisasterRecovery.MovesControl",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL hold an in-flight export at `PENDING` while `SYSTEM STOP MOVES` is in effect and SHALL resume it to `COMPLETED` after `SYSTEM START MOVES`, with no rows lost or duplicated.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.2",
)

RQ_Iceberg_ExportPartition_DisasterRecovery_KillExport = Requirement(
    name="RQ.Iceberg.ExportPartition.DisasterRecovery.KillExport",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL respect `KILL EXPORT PARTITION` from any documented in-flight phase:\n"
        "\n"
        "* While moves are stopped (task held at `PENDING`), `KILL` transitions the row to `KILLED`.\n"
        "* While the commit is being attempted, `KILL` still terminates the task and the row reaches `KILLED`.\n"
        "\n"
        "In both cases no second snapshot ever appears, regardless of whether the kill arrived before or during the publish step.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.3",
)

RQ_Iceberg_ExportPartition_DisasterRecovery_InvalidInputs = Requirement(
    name="RQ.Iceberg.ExportPartition.DisasterRecovery.InvalidInputs",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject malformed export inputs without leaving residue:\n"
        "\n"
        "* `EXPORT PARTITION` to a destination table that does not exist SHALL fail synchronously with a clear error.\n"
        "* `EXPORT PARTITION ID '<missing>'` for a partition that has no parts SHALL be a safe no-op — no failed task row, no partial snapshot, no orphaned files.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.4",
)

RQ_Iceberg_ExportPartition_MultiReplicaRecovery = Requirement(
    name="RQ.Iceberg.ExportPartition.MultiReplicaRecovery",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL preserve export idempotency and Iceberg snapshot linearity when exports are initiated from **different replicas** of the same `ReplicatedMergeTree` table, including under ZooKeeper restarts, replica process failure, and randomised replica chaos, converging to at most one successful commit per guarded export key.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.multi_replica_recovery` (`multi_replica_recovery.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.5",
)

RQ_Iceberg_ExportPartition_MultiReplicaRecovery_CrossReplicaConcurrency = Requirement(
    name="RQ.Iceberg.ExportPartition.MultiReplicaRecovery.CrossReplicaConcurrency",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL coordinate concurrent exports issued by different replicas:\n"
        "\n"
        "* Two replicas exporting **different** partitions to the same destination SHALL produce two append snapshots in a linear chain with no row loss.\n"
        "* Two replicas issuing the **same** export key SHALL produce exactly one snapshot — the duplicate is rejected by the cross-replica idempotency guard.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.6",
)

RQ_Iceberg_ExportPartition_MultiReplicaRecovery_InitiatorFailover = Requirement(
    name="RQ.Iceberg.ExportPartition.MultiReplicaRecovery.InitiatorFailover",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL allow a peer replica to finish an in-flight export when the initiator dies mid-commit:\n"
        "\n"
        "* The surviving replica picks the work up from the Keeper-stashed manifest.\n"
        "* The `clickhouse.export-partition-transaction-id` marker prevents a double-commit if the dead initiator had already published.\n"
        "* The destination ends with exactly one append snapshot for the partition.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.7",
)

RQ_Iceberg_ExportPartition_MultiReplicaRecovery_ZooKeeperBounce = Requirement(
    name="RQ.Iceberg.ExportPartition.MultiReplicaRecovery.ZooKeeperBounce",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL recover an in-flight export from a mid-commit ZooKeeper disturbance:\n"
        "\n"
        "* Both a graceful `zkServer.sh restart` and a SIGKILL + `docker start` (single-replica and cross-replica variants) SHALL leave the export converging to `COMPLETED`.\n"
        "* No replica observes a duplicate snapshot during or after the bounce.\n"
        "* When two replicas were exporting different partitions, both still produce their own append snapshots in a linear chain.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.8",
)

RQ_Iceberg_ExportPartition_MultiReplicaRecovery_RandomisedChaos = Requirement(
    name="RQ.Iceberg.ExportPartition.MultiReplicaRecovery.RandomisedChaos",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL keep the snapshot chain linear and consistent under randomised replica disruption (stress-only, gated by `--stress`):\n"
        "\n"
        "* Killing a replica at randomly-chosen export-lifecycle phases (before commit, during commit, after `COMPLETED`) with random kill modes and restart policies SHALL converge to a terminal status with at most one snapshot per partition; for kills after `COMPLETED` the destination state SHALL remain unchanged.\n"
        "* Repeatedly bouncing the initiating replica during a single export SHALL still produce at most one append snapshot.\n"
        "* Exporting many partitions concurrently while a chaos thread randomly bounces a replica SHALL produce a linear, txn-id-tagged snapshot chain with no double-commits.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.9",
)

RQ_Iceberg_ExportPartition_SystemMonitoring = Requirement(
    name="RQ.Iceberg.ExportPartition.SystemMonitoring",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL populate `system.replicated_partition_exports`, `system.part_log` (where applicable), and relevant `ProfileEvents` counters so operators can audit export progress, provenance, and completion — including correct handling when an export is killed.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.system_monitoring` (`system_monitoring.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.1",
)

RQ_Iceberg_ExportPartition_SystemMonitoring_ReplicatedPartitionExports = Requirement(
    name="RQ.Iceberg.ExportPartition.SystemMonitoring.ReplicatedPartitionExports",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL fill every documented column of `system.replicated_partition_exports` for a successful export, so the row is sufficient on its own to identify the source, the destination, the partition, the initiating replica, and the resulting status without consulting other system tables.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.2",
)

RQ_Iceberg_ExportPartition_SystemMonitoring_PartLog = Requirement(
    name="RQ.Iceberg.ExportPartition.SystemMonitoring.PartLog",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL append one `system.part_log` row with `event_type = 'ExportPart'` for each part that is successfully exported as part of an `EXPORT PARTITION` task.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.3",
)

RQ_Iceberg_ExportPartition_SystemMonitoring_ProfileEvents = Requirement(
    name="RQ.Iceberg.ExportPartition.SystemMonitoring.ProfileEvents",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL increment the documented `ProfileEvents` counters for a successful export, including `PartsExports` and the `ExportPartitionZooKeeper*` family that tracks Keeper round-trips made by the commit path.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.4",
)

RQ_Iceberg_ExportPartition_SystemMonitoring_KilledProvenance = Requirement(
    name="RQ.Iceberg.ExportPartition.SystemMonitoring.KilledProvenance",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL preserve provenance and diagnostic fields on a killed export so the row remains attributable after the fact:\n"
        "\n"
        "* `source_replica`, `create_time`, and identifying columns SHALL still match the original initiator and timing once the row has transitioned to `KILLED`.\n"
        "* When the kill lands during the commit window, the same provenance fields and any diagnostic counters that were already populated SHALL remain readable for post-mortem analysis.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.5",
)

RQ_Iceberg_ExportPartition_Settings = Requirement(
    name="RQ.Iceberg.ExportPartition.Settings",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL honour documented `export_merge_tree_partition_*` settings and the format settings the writer forwards to Parquet, in a way observable from successful exports and system tables.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.settings` (`settings.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.6",
)

RQ_Iceberg_ExportPartition_Settings_SystemTablePreferRemote = Requirement(
    name="RQ.Iceberg.ExportPartition.Settings.SystemTablePreferRemote",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL serve consistent status information from `system.replicated_partition_exports` whether the row is read from the local cache (`export_merge_tree_partition_system_table_prefer_remote_information = 0`, the new default) or refreshed directly from Keeper (`= 1`). The two modes SHALL return the same status for an already-completed export.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.7",
)

RQ_Iceberg_ExportPartition_Settings_ParquetCompression = Requirement(
    name="RQ.Iceberg.ExportPartition.Settings.ParquetCompression",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL forward `output_format_parquet_compression_method` to the Parquet writer used by `EXPORT PARTITION`, so the compression codec recorded inside committed data files reflects the requested setting.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.8",
)

RQ_Iceberg_ExportPartition_DirectWrites = Requirement(
    name="RQ.Iceberg.ExportPartition.DirectWrites",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL allow `INSERT INTO <iceberg_table>` against an Iceberg destination previously populated by `EXPORT PARTITION` (when `allow_experimental_insert_into_iceberg` is on), and SHALL keep the snapshot chain consistent when exports and direct inserts alternate:\n"
        "\n"
        "* An `INSERT` after an export adds its own append snapshot without rewriting the export's snapshot.\n"
        "* Alternating `EXPORT` and `INSERT` operations produce one snapshot per operation, in order, all readable through ClickHouse and external readers.\n"
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
        "[ClickHouse] SHALL support `TRUNCATE TABLE` against an Iceberg destination previously populated by `EXPORT PARTITION` (when truncate is enabled), clearing readable rows while leaving the table itself usable for subsequent writes.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.truncate` (`truncate.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.2",
)

RQ_Iceberg_ExportPartition_Truncate_RepopulateAfterTruncate = Requirement(
    name="RQ.Iceberg.ExportPartition.Truncate.RepopulateAfterTruncate",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL allow a fresh `EXPORT PARTITION` to repopulate a truncated destination:\n"
        "\n"
        "* The first export after a `TRUNCATE` produces a new append snapshot.\n"
        "* Subsequent reads return the freshly-exported rows; no rows from before the truncate leak through.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.3",
)

RQ_Iceberg_ExportPartition_Truncate_AfterDirectInsert = Requirement(
    name="RQ.Iceberg.ExportPartition.Truncate.AfterDirectInsert",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL behave correctly when `TRUNCATE TABLE` runs after a direct `INSERT INTO <iceberg_table>` (with no preceding export), clearing the inserted rows and leaving the destination empty and reusable.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.4",
)

RQ_Iceberg_ExportPartition_MinMaxPruning = Requirement(
    name="RQ.Iceberg.ExportPartition.MinMaxPruning",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL write Iceberg manifest column statistics (`lower_bounds` / `upper_bounds`) during export such that reads of the destination with selective predicates exhibit min/max pruning — fewer files touched and reduced `read_rows` than a full scan — when data layout makes pruning possible. This SHALL hold both for equality predicates and for range predicates.\n"
        "\n"
        "**Regression module:** `iceberg.tests.export_partition.minmax_pruning` (`minmax_pruning.py`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.5",
)

RQ_Iceberg_ExportPartition_ZooKeeperCompat = Requirement(
    name="RQ.Iceberg.ExportPartition.ZooKeeperCompat",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL recreate the **`/exports`** coordination subtree under a `ReplicatedMergeTree` table's ZooKeeper path during normal replica attach / restart flows, so tables whose ZooKeeper state predates the export feature — or has had `/exports` deleted by an operator — become eligible for `EXPORT PARTITION` after a documented recovery step (`SYSTEM RESTART REPLICA` or full server restart) without manual ZooKeeper surgery.\n"
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
        Heading(
            name="RQ.Iceberg.ExportPartition.Sanity.EmptyPartition", level=2, num="2.2"
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.Sanity.CrossReplicaInitiator",
            level=2,
            num="2.3",
        ),
        Heading(name="Partition and schema compatibility", level=1, num="3"),
        Heading(
            name="RQ.Iceberg.ExportPartition.PartitionCompatibility", level=2, num="3.1"
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.PartitionCompatibility.AcceptedTransforms",
            level=2,
            num="3.2",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.PartitionCompatibility.MismatchRejection",
            level=2,
            num="3.3",
        ),
        Heading(name="RQ.Iceberg.ExportPartition.DataTypes", level=2, num="3.4"),
        Heading(
            name="RQ.Iceberg.ExportPartition.DataTypes.Primitives", level=2, num="3.5"
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.DataTypes.Nullable", level=2, num="3.6"
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.DataTypes.Composite", level=2, num="3.7"
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.DataTypes.UnsupportedRejection",
            level=2,
            num="3.8",
        ),
        Heading(name="Committed Iceberg metadata", level=1, num="4"),
        Heading(
            name="RQ.Iceberg.ExportPartition.ManifestIntegrity", level=2, num="4.1"
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.ManifestIntegrity.SnapshotChain",
            level=2,
            num="4.2",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.ManifestIntegrity.PartitionSpec",
            level=2,
            num="4.3",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.ManifestIntegrity.ColumnStats",
            level=2,
            num="4.4",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.ManifestIntegrity.PathLayout",
            level=2,
            num="4.5",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.ManifestIntegrity.ExternalReader",
            level=2,
            num="4.6",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.CatalogIntegration", level=2, num="4.7"
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.CatalogIntegration.NoCatalog",
            level=2,
            num="4.8",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.CatalogIntegration.RestGlue",
            level=2,
            num="4.9",
        ),
        Heading(name="Transactions, idempotency, and concurrency", level=1, num="5"),
        Heading(name="RQ.Iceberg.ExportPartition.Transactions", level=2, num="5.1"),
        Heading(
            name="RQ.Iceberg.ExportPartition.Transactions.SnapshotChain",
            level=2,
            num="5.2",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.Transactions.Idempotency",
            level=2,
            num="5.3",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.Transactions.CrashRecovery",
            level=2,
            num="5.4",
        ),
        Heading(name="RQ.Iceberg.ExportPartition.ConcurrentWrites", level=2, num="5.5"),
        Heading(
            name="RQ.Iceberg.ExportPartition.ConcurrentWrites.MultiStatement",
            level=2,
            num="5.6",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.ConcurrentWrites.Interleaving",
            level=2,
            num="5.7",
        ),
        Heading(name="Evolution and physical layout", level=1, num="6"),
        Heading(name="RQ.Iceberg.ExportPartition.SchemaEvolution", level=2, num="6.1"),
        Heading(
            name="RQ.Iceberg.ExportPartition.SchemaEvolution.AcceptedAlterations",
            level=2,
            num="6.2",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.SchemaEvolution.RejectedAlterations",
            level=2,
            num="6.3",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.SchemaEvolution.SchemaHistory",
            level=2,
            num="6.4",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.PartitionSpecEvolution", level=2, num="6.5"
        ),
        Heading(name="RQ.Iceberg.ExportPartition.StoragePaths", level=2, num="6.6"),
        Heading(
            name="RQ.Iceberg.ExportPartition.StoragePaths.PathFormat",
            level=2,
            num="6.7",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.StoragePaths.DeepPrefix",
            level=2,
            num="6.8",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.StoragePaths.Isolation", level=2, num="6.9"
        ),
        Heading(name="Failure handling and multi-replica behaviour", level=1, num="7"),
        Heading(name="RQ.Iceberg.ExportPartition.DisasterRecovery", level=2, num="7.1"),
        Heading(
            name="RQ.Iceberg.ExportPartition.DisasterRecovery.MovesControl",
            level=2,
            num="7.2",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.DisasterRecovery.KillExport",
            level=2,
            num="7.3",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.DisasterRecovery.InvalidInputs",
            level=2,
            num="7.4",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.MultiReplicaRecovery", level=2, num="7.5"
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.MultiReplicaRecovery.CrossReplicaConcurrency",
            level=2,
            num="7.6",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.MultiReplicaRecovery.InitiatorFailover",
            level=2,
            num="7.7",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.MultiReplicaRecovery.ZooKeeperBounce",
            level=2,
            num="7.8",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.MultiReplicaRecovery.RandomisedChaos",
            level=2,
            num="7.9",
        ),
        Heading(name="Observability and export settings", level=1, num="8"),
        Heading(name="RQ.Iceberg.ExportPartition.SystemMonitoring", level=2, num="8.1"),
        Heading(
            name="RQ.Iceberg.ExportPartition.SystemMonitoring.ReplicatedPartitionExports",
            level=2,
            num="8.2",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.SystemMonitoring.PartLog",
            level=2,
            num="8.3",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.SystemMonitoring.ProfileEvents",
            level=2,
            num="8.4",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.SystemMonitoring.KilledProvenance",
            level=2,
            num="8.5",
        ),
        Heading(name="RQ.Iceberg.ExportPartition.Settings", level=2, num="8.6"),
        Heading(
            name="RQ.Iceberg.ExportPartition.Settings.SystemTablePreferRemote",
            level=2,
            num="8.7",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.Settings.ParquetCompression",
            level=2,
            num="8.8",
        ),
        Heading(name="Post-export destination operations", level=1, num="9"),
        Heading(name="RQ.Iceberg.ExportPartition.DirectWrites", level=2, num="9.1"),
        Heading(name="RQ.Iceberg.ExportPartition.Truncate", level=2, num="9.2"),
        Heading(
            name="RQ.Iceberg.ExportPartition.Truncate.RepopulateAfterTruncate",
            level=2,
            num="9.3",
        ),
        Heading(
            name="RQ.Iceberg.ExportPartition.Truncate.AfterDirectInsert",
            level=2,
            num="9.4",
        ),
        Heading(name="RQ.Iceberg.ExportPartition.MinMaxPruning", level=2, num="9.5"),
        Heading(name="Source replica and ZooKeeper compatibility", level=1, num="10"),
        Heading(name="RQ.Iceberg.ExportPartition.ZooKeeperCompat", level=2, num="10.1"),
    ),
    requirements=(
        RQ_Iceberg_ExportPartition_Sanity,
        RQ_Iceberg_ExportPartition_Sanity_EmptyPartition,
        RQ_Iceberg_ExportPartition_Sanity_CrossReplicaInitiator,
        RQ_Iceberg_ExportPartition_PartitionCompatibility,
        RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms,
        RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection,
        RQ_Iceberg_ExportPartition_DataTypes,
        RQ_Iceberg_ExportPartition_DataTypes_Primitives,
        RQ_Iceberg_ExportPartition_DataTypes_Nullable,
        RQ_Iceberg_ExportPartition_DataTypes_Composite,
        RQ_Iceberg_ExportPartition_DataTypes_UnsupportedRejection,
        RQ_Iceberg_ExportPartition_ManifestIntegrity,
        RQ_Iceberg_ExportPartition_ManifestIntegrity_SnapshotChain,
        RQ_Iceberg_ExportPartition_ManifestIntegrity_PartitionSpec,
        RQ_Iceberg_ExportPartition_ManifestIntegrity_ColumnStats,
        RQ_Iceberg_ExportPartition_ManifestIntegrity_PathLayout,
        RQ_Iceberg_ExportPartition_ManifestIntegrity_ExternalReader,
        RQ_Iceberg_ExportPartition_CatalogIntegration,
        RQ_Iceberg_ExportPartition_CatalogIntegration_NoCatalog,
        RQ_Iceberg_ExportPartition_CatalogIntegration_RestGlue,
        RQ_Iceberg_ExportPartition_Transactions,
        RQ_Iceberg_ExportPartition_Transactions_SnapshotChain,
        RQ_Iceberg_ExportPartition_Transactions_Idempotency,
        RQ_Iceberg_ExportPartition_Transactions_CrashRecovery,
        RQ_Iceberg_ExportPartition_ConcurrentWrites,
        RQ_Iceberg_ExportPartition_ConcurrentWrites_MultiStatement,
        RQ_Iceberg_ExportPartition_ConcurrentWrites_Interleaving,
        RQ_Iceberg_ExportPartition_SchemaEvolution,
        RQ_Iceberg_ExportPartition_SchemaEvolution_AcceptedAlterations,
        RQ_Iceberg_ExportPartition_SchemaEvolution_RejectedAlterations,
        RQ_Iceberg_ExportPartition_SchemaEvolution_SchemaHistory,
        RQ_Iceberg_ExportPartition_PartitionSpecEvolution,
        RQ_Iceberg_ExportPartition_StoragePaths,
        RQ_Iceberg_ExportPartition_StoragePaths_PathFormat,
        RQ_Iceberg_ExportPartition_StoragePaths_DeepPrefix,
        RQ_Iceberg_ExportPartition_StoragePaths_Isolation,
        RQ_Iceberg_ExportPartition_DisasterRecovery,
        RQ_Iceberg_ExportPartition_DisasterRecovery_MovesControl,
        RQ_Iceberg_ExportPartition_DisasterRecovery_KillExport,
        RQ_Iceberg_ExportPartition_DisasterRecovery_InvalidInputs,
        RQ_Iceberg_ExportPartition_MultiReplicaRecovery,
        RQ_Iceberg_ExportPartition_MultiReplicaRecovery_CrossReplicaConcurrency,
        RQ_Iceberg_ExportPartition_MultiReplicaRecovery_InitiatorFailover,
        RQ_Iceberg_ExportPartition_MultiReplicaRecovery_ZooKeeperBounce,
        RQ_Iceberg_ExportPartition_MultiReplicaRecovery_RandomisedChaos,
        RQ_Iceberg_ExportPartition_SystemMonitoring,
        RQ_Iceberg_ExportPartition_SystemMonitoring_ReplicatedPartitionExports,
        RQ_Iceberg_ExportPartition_SystemMonitoring_PartLog,
        RQ_Iceberg_ExportPartition_SystemMonitoring_ProfileEvents,
        RQ_Iceberg_ExportPartition_SystemMonitoring_KilledProvenance,
        RQ_Iceberg_ExportPartition_Settings,
        RQ_Iceberg_ExportPartition_Settings_SystemTablePreferRemote,
        RQ_Iceberg_ExportPartition_Settings_ParquetCompression,
        RQ_Iceberg_ExportPartition_DirectWrites,
        RQ_Iceberg_ExportPartition_Truncate,
        RQ_Iceberg_ExportPartition_Truncate_RepopulateAfterTruncate,
        RQ_Iceberg_ExportPartition_Truncate_AfterDirectInsert,
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
    * 2.2 [RQ.Iceberg.ExportPartition.Sanity.EmptyPartition](#rqicebergexportpartitionsanityemptypartition)
    * 2.3 [RQ.Iceberg.ExportPartition.Sanity.CrossReplicaInitiator](#rqicebergexportpartitionsanitycrossreplicainitiator)
* 3 [Partition and schema compatibility](#partition-and-schema-compatibility)
    * 3.1 [RQ.Iceberg.ExportPartition.PartitionCompatibility](#rqicebergexportpartitionpartitioncompatibility)
    * 3.2 [RQ.Iceberg.ExportPartition.PartitionCompatibility.AcceptedTransforms](#rqicebergexportpartitionpartitioncompatibilityacceptedtransforms)
    * 3.3 [RQ.Iceberg.ExportPartition.PartitionCompatibility.MismatchRejection](#rqicebergexportpartitionpartitioncompatibilitymismatchrejection)
    * 3.4 [RQ.Iceberg.ExportPartition.DataTypes](#rqicebergexportpartitiondatatypes)
    * 3.5 [RQ.Iceberg.ExportPartition.DataTypes.Primitives](#rqicebergexportpartitiondatatypesprimitives)
    * 3.6 [RQ.Iceberg.ExportPartition.DataTypes.Nullable](#rqicebergexportpartitiondatatypesnullable)
    * 3.7 [RQ.Iceberg.ExportPartition.DataTypes.Composite](#rqicebergexportpartitiondatatypescomposite)
    * 3.8 [RQ.Iceberg.ExportPartition.DataTypes.UnsupportedRejection](#rqicebergexportpartitiondatatypesunsupportedrejection)
* 4 [Committed Iceberg metadata](#committed-iceberg-metadata)
    * 4.1 [RQ.Iceberg.ExportPartition.ManifestIntegrity](#rqicebergexportpartitionmanifestintegrity)
    * 4.2 [RQ.Iceberg.ExportPartition.ManifestIntegrity.SnapshotChain](#rqicebergexportpartitionmanifestintegritysnapshotchain)
    * 4.3 [RQ.Iceberg.ExportPartition.ManifestIntegrity.PartitionSpec](#rqicebergexportpartitionmanifestintegritypartitionspec)
    * 4.4 [RQ.Iceberg.ExportPartition.ManifestIntegrity.ColumnStats](#rqicebergexportpartitionmanifestintegritycolumnstats)
    * 4.5 [RQ.Iceberg.ExportPartition.ManifestIntegrity.PathLayout](#rqicebergexportpartitionmanifestintegritypathlayout)
    * 4.6 [RQ.Iceberg.ExportPartition.ManifestIntegrity.ExternalReader](#rqicebergexportpartitionmanifestintegrityexternalreader)
    * 4.7 [RQ.Iceberg.ExportPartition.CatalogIntegration](#rqicebergexportpartitioncatalogintegration)
    * 4.8 [RQ.Iceberg.ExportPartition.CatalogIntegration.NoCatalog](#rqicebergexportpartitioncatalogintegrationnocatalog)
    * 4.9 [RQ.Iceberg.ExportPartition.CatalogIntegration.RestGlue](#rqicebergexportpartitioncatalogintegrationrestglue)
* 5 [Transactions, idempotency, and concurrency](#transactions-idempotency-and-concurrency)
    * 5.1 [RQ.Iceberg.ExportPartition.Transactions](#rqicebergexportpartitiontransactions)
    * 5.2 [RQ.Iceberg.ExportPartition.Transactions.SnapshotChain](#rqicebergexportpartitiontransactionssnapshotchain)
    * 5.3 [RQ.Iceberg.ExportPartition.Transactions.Idempotency](#rqicebergexportpartitiontransactionsidempotency)
    * 5.4 [RQ.Iceberg.ExportPartition.Transactions.CrashRecovery](#rqicebergexportpartitiontransactionscrashrecovery)
    * 5.5 [RQ.Iceberg.ExportPartition.ConcurrentWrites](#rqicebergexportpartitionconcurrentwrites)
    * 5.6 [RQ.Iceberg.ExportPartition.ConcurrentWrites.MultiStatement](#rqicebergexportpartitionconcurrentwritesmultistatement)
    * 5.7 [RQ.Iceberg.ExportPartition.ConcurrentWrites.Interleaving](#rqicebergexportpartitionconcurrentwritesinterleaving)
* 6 [Evolution and physical layout](#evolution-and-physical-layout)
    * 6.1 [RQ.Iceberg.ExportPartition.SchemaEvolution](#rqicebergexportpartitionschemaevolution)
    * 6.2 [RQ.Iceberg.ExportPartition.SchemaEvolution.AcceptedAlterations](#rqicebergexportpartitionschemaevolutionacceptedalterations)
    * 6.3 [RQ.Iceberg.ExportPartition.SchemaEvolution.RejectedAlterations](#rqicebergexportpartitionschemaevolutionrejectedalterations)
    * 6.4 [RQ.Iceberg.ExportPartition.SchemaEvolution.SchemaHistory](#rqicebergexportpartitionschemaevolutionschemahistory)
    * 6.5 [RQ.Iceberg.ExportPartition.PartitionSpecEvolution](#rqicebergexportpartitionpartitionspecevolution)
    * 6.6 [RQ.Iceberg.ExportPartition.StoragePaths](#rqicebergexportpartitionstoragepaths)
    * 6.7 [RQ.Iceberg.ExportPartition.StoragePaths.PathFormat](#rqicebergexportpartitionstoragepathspathformat)
    * 6.8 [RQ.Iceberg.ExportPartition.StoragePaths.DeepPrefix](#rqicebergexportpartitionstoragepathsdeepprefix)
    * 6.9 [RQ.Iceberg.ExportPartition.StoragePaths.Isolation](#rqicebergexportpartitionstoragepathsisolation)
* 7 [Failure handling and multi-replica behaviour](#failure-handling-and-multi-replica-behaviour)
    * 7.1 [RQ.Iceberg.ExportPartition.DisasterRecovery](#rqicebergexportpartitiondisasterrecovery)
    * 7.2 [RQ.Iceberg.ExportPartition.DisasterRecovery.MovesControl](#rqicebergexportpartitiondisasterrecoverymovescontrol)
    * 7.3 [RQ.Iceberg.ExportPartition.DisasterRecovery.KillExport](#rqicebergexportpartitiondisasterrecoverykillexport)
    * 7.4 [RQ.Iceberg.ExportPartition.DisasterRecovery.InvalidInputs](#rqicebergexportpartitiondisasterrecoveryinvalidinputs)
    * 7.5 [RQ.Iceberg.ExportPartition.MultiReplicaRecovery](#rqicebergexportpartitionmultireplicarecovery)
    * 7.6 [RQ.Iceberg.ExportPartition.MultiReplicaRecovery.CrossReplicaConcurrency](#rqicebergexportpartitionmultireplicarecoverycrossreplicaconcurrency)
    * 7.7 [RQ.Iceberg.ExportPartition.MultiReplicaRecovery.InitiatorFailover](#rqicebergexportpartitionmultireplicarecoveryinitiatorfailover)
    * 7.8 [RQ.Iceberg.ExportPartition.MultiReplicaRecovery.ZooKeeperBounce](#rqicebergexportpartitionmultireplicarecoveryzookeeperbounce)
    * 7.9 [RQ.Iceberg.ExportPartition.MultiReplicaRecovery.RandomisedChaos](#rqicebergexportpartitionmultireplicarecoveryrandomisedchaos)
* 8 [Observability and export settings](#observability-and-export-settings)
    * 8.1 [RQ.Iceberg.ExportPartition.SystemMonitoring](#rqicebergexportpartitionsystemmonitoring)
    * 8.2 [RQ.Iceberg.ExportPartition.SystemMonitoring.ReplicatedPartitionExports](#rqicebergexportpartitionsystemmonitoringreplicatedpartitionexports)
    * 8.3 [RQ.Iceberg.ExportPartition.SystemMonitoring.PartLog](#rqicebergexportpartitionsystemmonitoringpartlog)
    * 8.4 [RQ.Iceberg.ExportPartition.SystemMonitoring.ProfileEvents](#rqicebergexportpartitionsystemmonitoringprofileevents)
    * 8.5 [RQ.Iceberg.ExportPartition.SystemMonitoring.KilledProvenance](#rqicebergexportpartitionsystemmonitoringkilledprovenance)
    * 8.6 [RQ.Iceberg.ExportPartition.Settings](#rqicebergexportpartitionsettings)
    * 8.7 [RQ.Iceberg.ExportPartition.Settings.SystemTablePreferRemote](#rqicebergexportpartitionsettingssystemtablepreferremote)
    * 8.8 [RQ.Iceberg.ExportPartition.Settings.ParquetCompression](#rqicebergexportpartitionsettingsparquetcompression)
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

Regression tests live under the TestFlows package `iceberg.tests.export_partition`. The outer feature in `iceberg.tests.export_partition.feature` loads one sub-feature per Python module listed in its `MODULES` tuple and runs the same scenarios under multiple **catalog modes** (`no_catalog` / `rest` / `glue`) unless a module documents a narrower scope. Each top-level requirement names one such module; sub-requirements break that module down into the specific behaviours its scenarios verify, so traceability runs **module ↔ umbrella requirement ↔ scenario clusters** rather than module-only.

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

### RQ.Iceberg.ExportPartition.PartitionCompatibility
version: 1.0

[ClickHouse] SHALL enforce compatibility between the MergeTree `PARTITION BY` definition (including supported partition transforms) and the Iceberg destination's partition spec. Accepted pairings SHALL export successfully; mismatched or unsupported pairings SHALL be rejected with a clear error (typically `BAD_ARGUMENTS`) before any Iceberg metadata is committed.

**Regression module:** `iceberg.tests.export_partition.partition_compatibility` (`partition_compatibility.py`).

### RQ.Iceberg.ExportPartition.PartitionCompatibility.AcceptedTransforms
version: 1.0

[ClickHouse] SHALL successfully export when the source `PARTITION BY` expression matches the Iceberg partition spec across the documented transforms:

* Identity partitioning, including compound identity over multiple columns.
* `year` / `month` / `day` / `hour` time-bucket transforms.
* `truncate[N]` on string columns.
* `bucket[N]` on integer columns.
* Compound specs that mix identity and a parametrised transform.

In every accepted case the destination's partition spec stays stable across exports and partition values written by ClickHouse match what an external Iceberg reader expects.

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

### RQ.Iceberg.ExportPartition.DataTypes
version: 1.0

[ClickHouse] SHALL map ClickHouse column types used in the export to Iceberg types that preserve the intended values for every supported primitive and nested layout. Types with no supported Iceberg mapping SHALL fail explicitly at destination-creation or export time; the system SHALL NOT silently coerce, downcast, or drop data.

**Regression module:** `iceberg.tests.export_partition.datatypes` (`datatypes.py`).

### RQ.Iceberg.ExportPartition.DataTypes.Primitives
version: 1.0

[ClickHouse] SHALL export the following primitive types into their Iceberg equivalents and read them back unchanged through both ClickHouse and an external Iceberg reader:

* Integer types `Int16`, `Int32`, `Int64`, `UInt32`.
* Floating-point types `Float32` and `Float64`.
* Date / time types `Date`, `Date32`, `DateTime`, `DateTime64(3)`.
* `String` and `UUID`.

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

[ClickHouse] SHALL reject `EXPORT PARTITION` for column types that have no supported Iceberg mapping in this release:

* Narrow integers `Int8` and `UInt8`.
* `Bool`.
* `FixedString(N)`.
* `Decimal(p, s)`.
* `Enum8` (and its variants).
* `LowCardinality(T)`.

The rejection SHALL fire either when the destination is created or when the export is issued, before any data files are written.

## Committed Iceberg metadata

### RQ.Iceberg.ExportPartition.ManifestIntegrity
version: 1.0

[ClickHouse] SHALL produce Iceberg metadata after each successful export such that an external Iceberg reader can confirm snapshot lineage, summary statistics, manifest stats, partition spec references, and physical file layout are all internally consistent with the rows and files written.

**Regression module:** `iceberg.tests.export_partition.manifest_integrity` (`manifest_integrity.py`).

### RQ.Iceberg.ExportPartition.ManifestIntegrity.SnapshotChain
version: 1.0

[ClickHouse] SHALL extend the destination's snapshot list by exactly one append snapshot per successful export:

* The new snapshot's `parent_snapshot_id` SHALL point at the previously current snapshot.
* The snapshot summary's `total-records` SHALL match the row count contributed by the export.
* Repeated exports SHALL form a single linear chain, never a branch.

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

### RQ.Iceberg.ExportPartition.CatalogIntegration
version: 1.0

[ClickHouse] SHALL commit exports through the same catalog-aware metadata paths used in production for **REST** and **Glue** (Hive metastore compatible) catalogs, and SHALL preserve a usable on-disk layout in **no-catalog** mode where the warehouse `metadata.json` pointer is managed directly.

**Regression module:** `iceberg.tests.export_partition.catalogs` (`catalogs.py`).

### RQ.Iceberg.ExportPartition.CatalogIntegration.NoCatalog
version: 1.0

[ClickHouse] SHALL produce a `no_catalog` (`IcebergS3`) destination whose committed data is independently readable:

* The committed slice can be read through the `icebergS3` table function pointed at the same warehouse prefix.
* Dropping the destination table from ClickHouse SHALL NOT delete the committed data; the same files remain readable through `icebergS3`.

### RQ.Iceberg.ExportPartition.CatalogIntegration.RestGlue
version: 1.0

[ClickHouse] SHALL register the export with the configured external catalog:

* After commit the new snapshot SHALL be visible through the same catalog object operators use for production (REST or Glue).
* An external Iceberg reader connected to the same catalog SHALL list the snapshot and read the data files written by ClickHouse.

## Transactions, idempotency, and concurrency

### RQ.Iceberg.ExportPartition.Transactions
version: 1.0

[ClickHouse] SHALL treat each successful Iceberg commit from `EXPORT PARTITION` as an **append** snapshot with monotonic snapshot / sequence semantics relative to the prior table state, and SHALL preserve atomicity of the commit even when the commit path is interrupted at documented failure-injection points.

**Regression module:** `iceberg.tests.export_partition.transactions` (`transactions.py`).

### RQ.Iceberg.ExportPartition.Transactions.SnapshotChain
version: 1.0

[ClickHouse] SHALL append exactly one snapshot per successful `EXPORT PARTITION`, with no gaps or branches:

* Sequential exports of distinct partitions produce one append snapshot each, in order.
* Each new snapshot points at the previous one as its parent.

### RQ.Iceberg.ExportPartition.Transactions.Idempotency
version: 1.0

[ClickHouse] SHALL guard against accidental duplicate commits via a ZooKeeper-backed live manifest keyed on `(source_table, destination_table, partition_id)`:

* A second `EXPORT PARTITION` for the same key submitted within `export_merge_tree_partition_manifest_ttl` SHALL be rejected (typically `BAD_ARGUMENTS`).
* Setting `export_merge_tree_partition_force_export = 1` SHALL bypass the gate, at the operator's documented risk.
* Once `export_merge_tree_partition_manifest_ttl` has elapsed (or the prior export has been removed), the same key SHALL be exportable again.

### RQ.Iceberg.ExportPartition.Transactions.CrashRecovery
version: 1.0

[ClickHouse] SHALL keep the destination consistent across each documented commit-path failpoint:

* `iceberg_writes_non_retry_cleanup` — pre-publish failure leaves no half-published snapshot; the retry succeeds and produces exactly one append.
* `iceberg_export_after_commit_before_zk_completed` — a crash window between a successful Iceberg commit and the `COMPLETED` status update SHALL be detected on retry via the `clickhouse.export-partition-transaction-id` marker, so the recovery does not double-commit.
* `export_partition_status_change_throw` — a manifest status transition failure SHALL be retried internally without producing a duplicate commit.
* `iceberg_writes_post_publish_throw` — an exception thrown after a successful publish SHALL not invalidate the committed snapshot; the next read still sees the data.

### RQ.Iceberg.ExportPartition.ConcurrentWrites
version: 1.0

[ClickHouse] SHALL serialize concurrent export work so that multiple partition exports targeting the same Iceberg destination produce a **linear append-only** snapshot history without corrupting metadata, and SHALL keep direct writes (`INSERT`) interleaved with scheduled exports correctly attributed to their own snapshots.

**Regression module:** `iceberg.tests.export_partition.concurrent_writes` (`concurrent_writes.py`).

### RQ.Iceberg.ExportPartition.ConcurrentWrites.MultiStatement
version: 1.0

[ClickHouse] SHALL handle multiple `EXPORT PARTITION` clauses chained in one client batch correctly:

* Each distinct partition produces its own append snapshot; the snapshot chain remains linear.
* A duplicate export of the same partition inside a single `ALTER` SHALL commit at most once — repeats are absorbed by the same idempotency key as the cross-statement guard in `Transactions.Idempotency`.

### RQ.Iceberg.ExportPartition.ConcurrentWrites.Interleaving
version: 1.0

[ClickHouse] SHALL keep direct `INSERT INTO <iceberg_table>` writes that happen after a scheduled but not-yet-committed `EXPORT PARTITION` from leaking into the export's snapshot:

* The export's snapshot summary reflects only the rows the export was scheduled to write.
* The direct insert lands in its own subsequent snapshot.

## Evolution and physical layout

### RQ.Iceberg.ExportPartition.SchemaEvolution
version: 1.0

[ClickHouse] SHALL allow documented schema evolution on the Iceberg destination and the `ReplicatedMergeTree` source such that subsequent `EXPORT PARTITION` operations succeed only when the schemas remain compatible per Iceberg metadata rules; unsupported alterations SHALL be rejected deterministically.

**Regression module:** `iceberg.tests.export_partition.schema_evolution` (`schema_evolution.py`).

### RQ.Iceberg.ExportPartition.SchemaEvolution.AcceptedAlterations
version: 1.0

[ClickHouse] SHALL permit the following destination schema changes between exports and SHALL preserve compatibility on the next `EXPORT PARTITION`:

* Adding a column on both sides; the new column receives null / default values for previously exported rows.
* Dropping a column on both sides; subsequent exports omit the dropped column.
* Widening a numeric column (verified for `Int32 → Int64`); already-exported rows remain readable, new exports use the wider type.

### RQ.Iceberg.ExportPartition.SchemaEvolution.RejectedAlterations
version: 1.0

[ClickHouse] SHALL reject schema changes that would corrupt destination metadata or break round-trip reads:

* `RENAME COLUMN` on an Iceberg destination SHALL be rejected.
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

### RQ.Iceberg.ExportPartition.StoragePaths
version: 1.0

[ClickHouse] SHALL honour `write_full_path_in_iceberg_metadata` and related path rules when laying out Iceberg table locations and metadata on S3, including deep prefix hierarchies and multiple isolated destinations under one bucket, so committed paths remain consistent with the configured policy.

**Regression module:** `iceberg.tests.export_partition.storage_paths` (`storage_paths.py`).

### RQ.Iceberg.ExportPartition.StoragePaths.PathFormat
version: 1.0

[ClickHouse] SHALL respect both path-format modes for `metadata.json` location strings:

* With `write_full_path_in_iceberg_metadata = 1` the `metadata.json` location SHALL be a fully-qualified `s3://…` URI.
* With the default (`= 0`) the `metadata.json` location SHALL be bucket-relative (no scheme prefix).

In both modes the destination remains readable through ClickHouse and through an external reader.

### RQ.Iceberg.ExportPartition.StoragePaths.DeepPrefix
version: 1.0

[ClickHouse] SHALL accept Iceberg destinations whose warehouse prefix is many segments deep, and SHALL round-trip reads cleanly without truncating or rewriting the prefix.

### RQ.Iceberg.ExportPartition.StoragePaths.Isolation
version: 1.0

[ClickHouse] SHALL keep multiple Iceberg destinations under the same bucket strictly isolated:

* No data file or metadata file written for one destination appears under another's prefix.
* An export to one destination SHALL NOT modify another destination's snapshot list.

## Failure handling and multi-replica behaviour

### RQ.Iceberg.ExportPartition.DisasterRecovery
version: 1.0

[ClickHouse] SHALL surface export lifecycle states through `system.replicated_partition_exports` and SHALL recover or fail cleanly under operator actions and invalid inputs without committing a partial Iceberg snapshot in success cases where the implementation promises all-or-nothing behaviour.

**Regression module:** `iceberg.tests.export_partition.disaster_recovery` (`disaster_recovery.py`).

### RQ.Iceberg.ExportPartition.DisasterRecovery.MovesControl
version: 1.0

[ClickHouse] SHALL hold an in-flight export at `PENDING` while `SYSTEM STOP MOVES` is in effect and SHALL resume it to `COMPLETED` after `SYSTEM START MOVES`, with no rows lost or duplicated.

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

### RQ.Iceberg.ExportPartition.MultiReplicaRecovery
version: 1.0

[ClickHouse] SHALL preserve export idempotency and Iceberg snapshot linearity when exports are initiated from **different replicas** of the same `ReplicatedMergeTree` table, including under ZooKeeper restarts, replica process failure, and randomised replica chaos, converging to at most one successful commit per guarded export key.

**Regression module:** `iceberg.tests.export_partition.multi_replica_recovery` (`multi_replica_recovery.py`).

### RQ.Iceberg.ExportPartition.MultiReplicaRecovery.CrossReplicaConcurrency
version: 1.0

[ClickHouse] SHALL coordinate concurrent exports issued by different replicas:

* Two replicas exporting **different** partitions to the same destination SHALL produce two append snapshots in a linear chain with no row loss.
* Two replicas issuing the **same** export key SHALL produce exactly one snapshot — the duplicate is rejected by the cross-replica idempotency guard.

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

## Observability and export settings

### RQ.Iceberg.ExportPartition.SystemMonitoring
version: 1.0

[ClickHouse] SHALL populate `system.replicated_partition_exports`, `system.part_log` (where applicable), and relevant `ProfileEvents` counters so operators can audit export progress, provenance, and completion — including correct handling when an export is killed.

**Regression module:** `iceberg.tests.export_partition.system_monitoring` (`system_monitoring.py`).

### RQ.Iceberg.ExportPartition.SystemMonitoring.ReplicatedPartitionExports
version: 1.0

[ClickHouse] SHALL fill every documented column of `system.replicated_partition_exports` for a successful export, so the row is sufficient on its own to identify the source, the destination, the partition, the initiating replica, and the resulting status without consulting other system tables.

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

### RQ.Iceberg.ExportPartition.Settings
version: 1.0

[ClickHouse] SHALL honour documented `export_merge_tree_partition_*` settings and the format settings the writer forwards to Parquet, in a way observable from successful exports and system tables.

**Regression module:** `iceberg.tests.export_partition.settings` (`settings.py`).

### RQ.Iceberg.ExportPartition.Settings.SystemTablePreferRemote
version: 1.0

[ClickHouse] SHALL serve consistent status information from `system.replicated_partition_exports` whether the row is read from the local cache (`export_merge_tree_partition_system_table_prefer_remote_information = 0`, the new default) or refreshed directly from Keeper (`= 1`). The two modes SHALL return the same status for an already-completed export.

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
""",
)
