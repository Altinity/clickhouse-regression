# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_ClickHouse_ExportPartition_S3 = Requirement(
    name="RQ.ClickHouse.ExportPartition.S3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions (all parts within a partition) from ReplicatedMergeTree engine tables to S3 object storage. The export operation SHALL export all parts that belong to the specified partition ID, ensuring complete partition data is transferred to the destination.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.1",
)

RQ_ClickHouse_ExportPartition_EmptyPartition = Requirement(
    name="RQ.ClickHouse.ExportPartition.EmptyPartition",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting from empty partitions by:\n"
        "* Completing export operations successfully when the specified partition contains no parts\n"
        "* Resulting in an empty destination partition when exporting from an empty source partition\n"
        "* Not creating any files in destination storage when there are no parts to export in the partition\n"
        "* Handling empty partitions gracefully without errors\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.2",
)

RQ_ClickHouse_ExportPartition_SQLCommand = Requirement(
    name="RQ.ClickHouse.ExportPartition.SQLCommand",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the following SQL command syntax for exporting partitions from ReplicatedMergeTree tables to object storage tables:\n"
        "\n"
        "```sql\n"
        "ALTER TABLE [database.]source_table_name \n"
        "EXPORT PARTITION ID 'partition_id' \n"
        "TO TABLE [database.]destination_table_name\n"
        "SETTINGS allow_experimental_export_merge_tree_part = 1\n"
        "```\n"
        "\n"
        "**Parameters:**\n"
        "- `source_table_name`: Name of the source ReplicatedMergeTree table\n"
        "- `partition_id`: The partition ID to export (string literal), which identifies all parts belonging to that partition\n"
        "- `destination_table_name`: Name of the destination object storage table\n"
        "- `allow_experimental_export_merge_tree_part`: Setting that must be set to `1` to enable this experimental feature\n"
        "\n"
        "This command allows users to export entire partitions in a single operation, which is more efficient than exporting individual parts and ensures all data for a partition is exported together.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.1",
)

RQ_ClickHouse_ExportPartition_IntoOutfile = Requirement(
    name="RQ.ClickHouse.ExportPartition.IntoOutfile",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of the `INTO OUTFILE` clause with `EXPORT PARTITION` and SHALL not output any errors.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "ALTER TABLE source_table \n"
        "EXPORT PARTITION ID '2020' \n"
        "TO TABLE destination_table\n"
        "INTO OUTFILE '/path/to/file'\n"
        "SETTINGS allow_experimental_export_merge_tree_part = 1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.2",
)

RQ_ClickHouse_ExportPartition_Format = Requirement(
    name="RQ.ClickHouse.ExportPartition.Format",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of the `FORMAT` clause with `EXPORT PARTITION` and SHALL not output any errors.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "ALTER TABLE source_table \n"
        "EXPORT PARTITION ID '2020' \n"
        "TO TABLE destination_table\n"
        "FORMAT JSON\n"
        "SETTINGS allow_experimental_export_merge_tree_part = 1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.3",
)

RQ_ClickHouse_ExportPartition_SettingsClause = Requirement(
    name="RQ.ClickHouse.ExportPartition.SettingsClause",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of the `SETTINGS` clause with `EXPORT PARTITION` and SHALL not output any errors.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "ALTER TABLE source_table \n"
        "EXPORT PARTITION ID '2020' \n"
        "TO TABLE destination_table\n"
        "SETTINGS allow_experimental_export_merge_tree_part = 1, \n"
        "         export_merge_tree_partition_max_retries = 5\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.4",
)

RQ_ClickHouse_ExportPartition_SourceEngines = Requirement(
    name="RQ.ClickHouse.ExportPartition.SourceEngines",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions from the following source table engines:\n"
        "* `ReplicatedMergeTree` - Replicated MergeTree engine (primary use case)\n"
        "* `ReplicatedSummingMergeTree` - Replicated MergeTree with automatic summation\n"
        "* `ReplicatedAggregatingMergeTree` - Replicated MergeTree with pre-aggregated data\n"
        "* `ReplicatedCollapsingMergeTree` - Replicated MergeTree with row versioning\n"
        "* `ReplicatedVersionedCollapsingMergeTree` - Replicated CollapsingMergeTree with version tracking\n"
        "* `ReplicatedGraphiteMergeTree` - Replicated MergeTree optimized for Graphite data\n"
        "* All other ReplicatedMergeTree family engines\n"
        "\n"
        "Export partition functionality manages export operations across multiple replicas in a cluster, ensuring that parts are exported correctly and avoiding conflicts.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.1",
)

RQ_ClickHouse_ExportPartition_ClustersNodes = Requirement(
    name="RQ.ClickHouse.ExportPartition.ClustersNodes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions from multiple nodes in a ReplicatedMergeTree cluster to the same destination storage, ensuring that:\n"
        "* Each replica in the cluster can independently export parts from the partition that it owns locally\n"
        "* All parts within a partition are exported exactly once, even when distributed across multiple replicas\n"
        "* Exported data from different replicas is correctly aggregated in the destination storage\n"
        "* All nodes in the cluster can read the same exported partition data from the destination\n"
        "* Export operations continue to make progress even if some replicas are temporarily unavailable\n"
        "\n"
        "In a replicated cluster, different parts of the same partition may exist on different replicas. The system must coordinate exports across all replicas to ensure complete partition export without duplication.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.1",
)

RQ_ClickHouse_ExportPartition_Shards = Requirement(
    name="RQ.ClickHouse.ExportPartition.Shards",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions from source tables that are on different shards than the destination table.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.2",
)

RQ_ClickHouse_ExportPartition_Versions = Requirement(
    name="RQ.ClickHouse.ExportPartition.Versions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions from source tables that are stored on servers with different ClickHouse versions than the destination server.\n"
        "\n"
        "Users can export partitions from tables on servers with older ClickHouse versions to tables on servers with newer versions, enabling data migration and version upgrades.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.3",
)

RQ_ClickHouse_ExportPartition_LegacyTables = Requirement(
    name="RQ.ClickHouse.ExportPartition.LegacyTables",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions from ReplicatedMergeTree tables that were created in ClickHouse versions that did not have the export partition feature, where the ZooKeeper structure does not contain an exports directory.\n"
        "\n"
        "The system SHALL:\n"
        "* Automatically create the necessary ZooKeeper structure (including the exports directory) when attempting to export from legacy tables\n"
        "* Handle the absence of export-related metadata gracefully without errors\n"
        "* Support export operations on tables created before the export partition feature was introduced\n"
        "* Maintain backward compatibility with existing replicated tables regardless of when they were created\n"
        "\n"
        "This ensures that users can export partitions from existing production tables without requiring table recreation or migration, even if those tables were created before the export partition feature existed.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.4",
)

RQ_ClickHouse_ExportPartition_SourcePartStorage = Requirement(
    name="RQ.ClickHouse.ExportPartition.SourcePartStorage",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions regardless of the underlying storage type where the source parts are stored, including:\n"
        "* **Local Disks**: Parts stored on local filesystem\n"
        "* **S3/Object Storage**: Parts stored on S3 or S3-compatible object storage\n"
        "* **Encrypted Disks**: Parts stored on encrypted disks (disk-level encryption)\n"
        "* **Cached Disks**: Parts stored with filesystem cache enabled\n"
        "* **Remote Disks**: Parts stored on HDFS, Azure Blob Storage, or Google Cloud Storage\n"
        "* **Tiered Storage**: Parts stored across multiple storage tiers (hot/cold)\n"
        "* **Zero-Copy Replication Disks**: Parts stored with zero-copy replication enabled\n"
        "\n"
        "Users should be able to export partitions regardless of where the source data is physically stored, providing flexibility in storage configurations.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.1",
)

RQ_ClickHouse_ExportPartition_StoragePolicies = Requirement(
    name="RQ.ClickHouse.ExportPartition.StoragePolicies",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions from tables using different storage policies, where storage policies are composed of volumes which are composed of disks, including:\n"
        "* **JBOD Volumes**: Just a Bunch Of Disks volumes with multiple disks\n"
        "* **External Volumes**: Volumes using external storage systems\n"
        "* **Tiered Storage Policies**: Storage policies with multiple volumes for hot/cold data tiers\n"
        "* **Custom Storage Policies**: Any storage policy configuration composed of volumes and disks\n"
        "* Exporting all parts in a partition regardless of which volume or disk within the storage policy contains each part\n"
        "* Maintaining data integrity when exporting from parts stored on any volume or disk in the storage policy\n"
        "\n"
        "Users may have partitions with parts distributed across different storage tiers or volumes, and the export should handle all parts regardless of their storage location.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.1",
)

RQ_ClickHouse_ExportPartition_DestinationEngines = Requirement(
    name="RQ.ClickHouse.ExportPartition.DestinationEngines",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting to destination tables that:\n"
        "* Support object storage engines including:\n"
        "  * `S3` - Amazon S3 and S3-compatible storage\n"
        "  * `StorageObjectStorage` - Generic object storage interface\n"
        "  * `HDFS` - Hadoop Distributed File System (with Hive partitioning)\n"
        "  * `Azure` - Microsoft Azure Blob Storage (with Hive partitioning)\n"
        "  * `GCS` - Google Cloud Storage (with Hive partitioning)\n"
        "\n"
        "Export partition is designed to move data from local or replicated storage to object storage systems for long-term storage, analytics, or data sharing purposes.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.1",
)

RQ_ClickHouse_ExportPartition_TemporaryTable = Requirement(
    name="RQ.ClickHouse.ExportPartition.TemporaryTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions from temporary ReplicatedMergeTree tables to destination object storage tables.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "CREATE TEMPORARY TABLE temp_table (p UInt64, k String, d UInt64) \n"
        "ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/temp_table', '{replica}') \n"
        "PARTITION BY p ORDER BY k;\n"
        "\n"
        "INSERT INTO temp_table VALUES (2020, 'key1', 100), (2020, 'key2', 200);\n"
        "\n"
        "ALTER TABLE temp_table \n"
        "EXPORT PARTITION ID '2020' \n"
        "TO TABLE destination_table\n"
        "SETTINGS allow_experimental_export_merge_tree_part = 1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.1",
)

RQ_ClickHouse_ExportPartition_SchemaCompatibility = Requirement(
    name="RQ.ClickHouse.ExportPartition.SchemaCompatibility",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL require source and destination tables to have compatible schemas for successful export operations:\n"
        "* Identical physical column schemas between source and destination, with the following exceptions:\n"
        "  * Source DEFAULT columns SHALL match destination regular columns (destination must not have DEFAULT columns)\n"
        "  * Source ALIAS columns SHALL match destination regular columns (destination must not have ALIAS columns)\n"
        "  * Source MATERIALIZED columns SHALL match destination regular columns (destination must not have MATERIALIZED columns)\n"
        "  * Source EPHEMERAL columns SHALL NOT have matching columns in the destination (EPHEMERAL columns are ignored during export)\n"
        "* The same partition key expression in both tables\n"
        "* Compatible data types for all columns (matching base types, not column modifiers)\n"
        "* Matching column order and names for all exported columns\n"
        "\n"
        "Schema compatibility ensures that exported data can be correctly read from the destination table without data loss or corruption. Special column types (DEFAULT, ALIAS, MATERIALIZED) in the source are materialized during export and written as regular columns to the destination.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.1",
)

RQ_ClickHouse_ExportPartition_PartitionKeyTypes = Requirement(
    name="RQ.ClickHouse.ExportPartition.PartitionKeyTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support export operations for tables with partition key types that are compatible with Hive partitioning, as shown in the following table:\n"
        "\n"
        "| Partition Key Type      | Supported | Examples                                                                 | Notes                          |\n"
        "|-------------------------|-----------|--------------------------------------------------------------------------|--------------------------------|\n"
        "| **Integer Types**       | ✅ Yes     | `UInt8`, `UInt16`, `UInt32`, `UInt64`, `Int8`, `Int16`, `Int32`, `Int64` | All integer types supported    |\n"
        "| **Date/DateTime Types** | ✅ Yes     | `Date`, `Date32`, `DateTime`, `DateTime64`                               | All date/time types supported  |\n"
        "| **String Types**        | ✅ Yes     | `String`, `FixedString`                                                  | All string types supported     |\n"
        "| **No Partition Key**    | ✅ Yes     | Tables without `PARTITION BY` clause                                     | Unpartitioned tables supported |\n"
        "\n"
        "[ClickHouse] SHALL automatically extract partition values from source parts and use them to create proper Hive partitioning structure in destination storage, but only for partition key types that are compatible with Hive partitioning requirements.\n"
        "\n"
        "[ClickHouse] SHALL require destination tables to support Hive partitioning, which limits the supported partition key types to Integer, Date/DateTime, and String types. Complex expressions that result in unsupported types are not supported for export operations.\n"
        "\n"
        "Hive partitioning is a standard way to organize data in object storage systems, making exported data compatible with various analytics tools and systems.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="11.1",
)

RQ_ClickHouse_ExportPartition_PartitionContent = Requirement(
    name="RQ.ClickHouse.ExportPartition.PartitionContent",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support export operations for partitions containing all valid MergeTree part types and their contents, including:\n"
        "\n"
        "| Part Type         | Supported | Description                                                  | Special Features               |\n"
        "|-------------------|-----------|--------------------------------------------------------------|--------------------------------|\n"
        "| **Wide Parts**    | ✅ Yes     | Data of each column stored in separate files with marks      | Standard format for most parts |\n"
        "| **Compact Parts** | ✅ Yes     | All column data stored in single file with single marks file | Optimized for small parts      |\n"
        "\n"
        "[ClickHouse] SHALL export all parts within the specified partition, regardless of their type. The system SHALL automatically apply lightweight delete masks during export to ensure only non-deleted rows are exported, and SHALL maintain data integrity in the destination storage.\n"
        "\n"
        "Partitions may contain a mix of different part types, and the export must handle all of them correctly to ensure complete partition export.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="12.1",
)

RQ_ClickHouse_ExportPartition_ColumnTypes_Alias = Requirement(
    name="RQ.ClickHouse.ExportPartition.ColumnTypes.Alias",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions containing tables with ALIAS columns by:\n"
        "* Computing ALIAS column values on-the-fly from expressions during export (ALIAS columns are not stored in parts)\n"
        "* Exporting ALIAS column values as regular columns in the destination table\n"
        "* Requiring destination tables to have matching regular columns (not ALIAS) for exported ALIAS columns\n"
        "* Including ALIAS columns when explicitly selected during export (ALIAS columns are not included in `SELECT *` by default)\n"
        "\n"
        "ALIAS columns are computed from expressions (e.g., `arr_1 ALIAS arr[1]`). During export, the system SHALL compute the ALIAS column values and export them as regular column data to the destination table.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.1",
)

RQ_ClickHouse_ExportPartition_ColumnTypes_Materialized = Requirement(
    name="RQ.ClickHouse.ExportPartition.ColumnTypes.Materialized",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions containing tables with MATERIALIZED columns by:\n"
        "* Reading MATERIALIZED column values from storage during export (MATERIALIZED columns are stored in parts and computed from expressions)\n"
        "* Exporting MATERIALIZED column values as regular columns in the destination table\n"
        "* Requiring destination tables to have matching regular columns (not MATERIALIZED) for exported MATERIALIZED columns\n"
        "\n"
        "MATERIALIZED columns are stored in parts and computed from expressions (e.g., `value * 2`). During export, the system SHALL read the stored MATERIALIZED column values and export them as regular column data to the destination table.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.2",
)

RQ_ClickHouse_ExportPartition_ColumnTypes_Default = Requirement(
    name="RQ.ClickHouse.ExportPartition.ColumnTypes.Default",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions containing tables with DEFAULT columns by:\n"
        "* Requiring the destination table to have a matching column that is NOT tagged as DEFAULT (must be a regular column)\n"
        "* Materializing the source DEFAULT column values during export (using either the default value or explicit value provided during INSERT)\n"
        "* Exporting the materialized values as a regular column to the destination table\n"
        "* Correctly handling both cases:\n"
        "  * When default values are used (no explicit value provided during INSERT)\n"
        "  * When explicit non-default values are provided during INSERT\n"
        "\n"
        "**Prior Behavior:**\n"
        "Prior to this feature, export operations with DEFAULT columns were not possible because object storage tables do not support DEFAULT columns, and schema compatibility required 100% matching column types between source and destination.\n"
        "\n"
        "**Current Behavior:**\n"
        "With this feature, the destination table schema SHALL have a regular column (not DEFAULT) that matches the source DEFAULT column's name and data type. During export, the system SHALL compute the actual values for DEFAULT columns (default or explicit) and export them as regular column data. This allows users to export partitions from source tables with DEFAULT columns to destination object storage tables that do not support DEFAULT columns.\n"
        "\n"
        "DEFAULT columns have default values (e.g., `status String DEFAULT 'active'`). The system SHALL materialize these values during export and write them as regular columns to the destination.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.3",
)

RQ_ClickHouse_ExportPartition_ColumnTypes_Ephemeral = Requirement(
    name="RQ.ClickHouse.ExportPartition.ColumnTypes.Ephemeral",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions containing tables with EPHEMERAL columns by:\n"
        "* Completely ignoring EPHEMERAL columns during export (EPHEMERAL columns are not stored and cannot be read from parts)\n"
        "* NOT exporting EPHEMERAL columns to the destination table\n"
        "* Requiring destination tables to NOT have matching columns for EPHEMERAL columns from the source table\n"
        "* Allowing EPHEMERAL columns to be used in DEFAULT column expressions, where the DEFAULT column values (computed from EPHEMERAL values) SHALL be exported correctly\n"
        "\n"
        "EPHEMERAL columns are not stored and are only used for DEFAULT column computation. During export, EPHEMERAL columns SHALL be completely ignored and SHALL NOT appear in the destination table schema.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.4",
)

RQ_ClickHouse_ExportPartition_ColumnTypes_Mixed = Requirement(
    name="RQ.ClickHouse.ExportPartition.ColumnTypes.Mixed",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions containing tables with a mix of ALIAS, MATERIALIZED, EPHEMERAL, and DEFAULT columns by:\n"
        "* Handling all column types correctly during export\n"
        "* Exporting only stored and computed columns (ALIAS, MATERIALIZED, DEFAULT) while ignoring EPHEMERAL columns\n"
        "* Maintaining data integrity when multiple column types are present in the same table\n"
        "\n"
        "Tables may contain a mix of different column types, and the export operation SHALL handle all column types correctly, exporting only stored and computed columns while ignoring EPHEMERAL columns.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.5",
)

RQ_ClickHouse_ExportPartition_SchemaChangeIsolation = Requirement(
    name="RQ.ClickHouse.ExportPartition.SchemaChangeIsolation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL ensure exported partition data is isolated from subsequent schema changes by:\n"
        "* Preserving exported data exactly as it was at the time of export\n"
        "* Not being affected by schema changes (column drops, renames, type changes) that occur after export\n"
        "* Maintaining data integrity in destination storage regardless of mutations applied to the source table after export\n"
        "* Ensuring exported data reflects the source table state at the time of export, not the current state\n"
        "\n"
        "Once a partition is exported, the exported data should remain stable and not be affected by future changes to the source table schema.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.6",
)

RQ_ClickHouse_ExportPartition_LargePartitions = Requirement(
    name="RQ.ClickHouse.ExportPartition.LargePartitions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting large partitions by:\n"
        "* Handling partitions with large numbers of parts (e.g., hundreds or thousands of parts)\n"
        "* Processing partitions with large numbers of rows (e.g., billions of rows)\n"
        "* Processing large data volumes efficiently during export\n"
        "* Maintaining data integrity when exporting large partitions\n"
        "* Completing export operations successfully regardless of partition size\n"
        "* Allowing export operations to continue over extended periods of time for very large partitions\n"
        "\n"
        "Production systems often have partitions containing very large amounts of data, and the export must handle these efficiently without timeouts or memory issues.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.7",
)

RQ_ClickHouse_ExportPartition_Corrupted = Requirement(
    name="RQ.ClickHouse.ExportPartition.Corrupted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error and prevent export operations from proceeding when trying to export a partition that contains corrupted parts in the source table.\n"
        "\n"
        "The system SHALL detect corruption in partitions containing compact parts, wide parts, or mixed part types.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.8",
)

RQ_ClickHouse_ExportPartition_PendingMutations = Requirement(
    name="RQ.ClickHouse.ExportPartition.PendingMutations",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL handle export operations when partitions contain pending mutations (e.g., DELETE mutations) by:\n"
        "* By default, throwing an error (`PENDING_MUTATIONS_NOT_ALLOWED`) when pending mutations exist in the partition and `export_merge_tree_part_throw_on_pending_mutations` is set to `1` (default)\n"
        "* When `export_merge_tree_part_throw_on_pending_mutations` is set to `0`, allowing export operations to proceed even when pending mutations exist\n"
        "* Providing users with control over whether exports should wait for mutations to complete or proceed with pending mutations\n"
        "* Maintaining data integrity in exported data regardless of the setting chosen\n"
        "\n"
        "**Pending Mutations Behavior:**\n"
        "* Pending mutations are mutations (e.g., DELETE, UPDATE) that have been initiated but not yet completed\n"
        "* By default, export operations SHALL fail with `PENDING_MUTATIONS_NOT_ALLOWED` error when pending mutations exist\n"
        "* Users can disable this behavior by setting `export_merge_tree_part_throw_on_pending_mutations = 0` to allow exports to proceed\n"
        "* When exports proceed with pending mutations, the exported data SHALL reflect the state of the partition at the time of export, which may include unapplied mutations\n"
        "\n"
        "This ensures that users can control whether export operations wait for mutations to complete or proceed immediately, providing flexibility for different use cases.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.9",
)

RQ_ClickHouse_ExportPartition_LightweightUpdate = Requirement(
    name="RQ.ClickHouse.ExportPartition.LightweightUpdate",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions that contain patch parts created by lightweight UPDATE operations by:\n"
        "* Allowing export operations to succeed even when patch parts exist in the source partition\n"
        "* Exporting partition data successfully regardless of the presence of patch parts\n"
        "* Not requiring patch parts to be materialized before export operations can proceed\n"
        "* Handling partitions with multiple patch parts correctly during export\n"
        "* Maintaining export operation stability when lightweight updates occur before or during export\n"
        "\n"
        "Lightweight updates create patch parts that contain only updated columns and rows. The export operation SHALL succeed even in the presence of these patch parts, though the patches might not be applied to the exported data. This ensures that export operations are not blocked by lightweight update operations and can proceed independently.\n"
        "\n"
        "**Pending Patch Parts Behavior:**\n"
        "* By default, export operations SHALL throw an error (`PENDING_MUTATIONS_NOT_ALLOWED`) when pending patch parts exist in the partition and `export_merge_tree_part_throw_on_pending_patch_parts` is set to `1` (default)\n"
        "* When `export_merge_tree_part_throw_on_pending_patch_parts` is set to `0`, export operations SHALL succeed even when pending patch parts exist\n"
        "* This allows users to control whether exports should wait for patch parts to be materialized or proceed with pending patch parts\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.10",
)

RQ_ClickHouse_ExportPartition_LightweightUpdate_MultiplePatches = Requirement(
    name="RQ.ClickHouse.ExportPartition.LightweightUpdate.MultiplePatches",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions that have multiple patch parts from multiple lightweight UPDATE operations by:\n"
        "* Handling partitions with multiple patch parts created by different UPDATE operations\n"
        "* Exporting partition data correctly when patch parts exist for the same partition\n"
        "* Not failing export operations due to the presence of multiple patch parts\n"
        "* Maintaining data integrity during export when multiple lightweight updates have been applied\n"
        "\n"
        "Users may perform multiple lightweight UPDATE operations on the same partition, creating multiple patch parts. The export operation must handle these correctly without errors.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.11",
)

RQ_ClickHouse_ExportPartition_LightweightUpdate_Concurrent = Requirement(
    name="RQ.ClickHouse.ExportPartition.LightweightUpdate.Concurrent",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support export operations when lightweight UPDATE operations occur concurrently or sequentially on partitions being exported by:\n"
        "* Allowing export operations to proceed when lightweight updates are performed before export starts\n"
        "* Not blocking lightweight UPDATE operations when export operations are in progress\n"
        "* Handling the presence of patch parts created during or before export operations\n"
        "* Ensuring export operations complete successfully regardless of when lightweight updates occur relative to the export operation\n"
        "\n"
        "Export operations and lightweight updates may occur at different times, and the system must handle both operations correctly without interference.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.12",
)

RQ_ClickHouse_ExportPartition_LightweightDelete = Requirement(
    name="RQ.ClickHouse.ExportPartition.LightweightDelete",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions that contain rows marked as deleted by lightweight DELETE operations by:\n"
        "* Allowing export operations to succeed even when deleted rows exist in the source partition\n"
        "* Automatically applying the `_row_exists` mask during export to ensure only non-deleted rows are exported\n"
        "* Exporting partition data successfully regardless of the presence of deleted rows\n"
        "* Not requiring deleted rows to be physically removed before export operations can proceed\n"
        "* Maintaining export operation stability when lightweight deletes occur before or during export\n"
        "\n"
        "Lightweight deletes mark rows as deleted using a hidden `_row_exists` system column. The export operation SHALL automatically apply this mask to ensure only visible (non-deleted) rows are exported to the destination, maintaining data consistency between source and destination tables.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.13",
)

RQ_ClickHouse_ExportPartition_LightweightDelete_MultipleDeletes = Requirement(
    name="RQ.ClickHouse.ExportPartition.LightweightDelete.MultipleDeletes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting partitions that have multiple lightweight DELETE operations applied by:\n"
        "* Handling partitions with multiple delete mutations on the same partition\n"
        "* Exporting partition data correctly when multiple deletes have been applied\n"
        "* Not failing export operations due to the presence of multiple delete mutations\n"
        "* Maintaining data integrity during export when multiple lightweight deletes have been applied\n"
        "* Ensuring that only non-deleted rows are exported even when multiple delete operations affect overlapping rows\n"
        "\n"
        "Users may perform multiple lightweight DELETE operations on the same partition, creating multiple delete mutations. The export operation must handle these correctly and ensure that all deleted rows are excluded from the export.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.14",
)

RQ_ClickHouse_ExportPartition_LightweightDelete_Concurrent = Requirement(
    name="RQ.ClickHouse.ExportPartition.LightweightDelete.Concurrent",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support export operations when lightweight DELETE operations occur concurrently or sequentially on partitions being exported by:\n"
        "* Allowing export operations to proceed when lightweight deletes are performed before export starts\n"
        "* Not blocking lightweight DELETE operations when export operations are in progress\n"
        "* Handling the presence of delete masks (`_row_exists` column) created during or before export operations\n"
        "* Ensuring export operations complete successfully regardless of when lightweight deletes occur relative to the export operation\n"
        "* Applying delete masks correctly to ensure deleted rows are not exported\n"
        "\n"
        "Export operations and lightweight deletes may occur at different times, and the system must handle both operations correctly without interference, ensuring that deleted rows are always excluded from exports.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.15",
)

RQ_ClickHouse_ExportPartition_RetryMechanism = Requirement(
    name="RQ.ClickHouse.ExportPartition.RetryMechanism",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL automatically retry failed part exports within a partition up to a configurable maximum retry count. If all retry attempts are exhausted for a part, the entire partition export operation SHALL be marked as failed.\n"
        "\n"
        "Unlike single-part exports, partition exports involve multiple parts and may take significant time. Retry mechanisms ensure that temporary failures don't require restarting the entire export operation.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="14.1",
)

RQ_ClickHouse_ExportPartition_Settings_MaxRetries = Requirement(
    name="RQ.ClickHouse.ExportPartition.Settings.MaxRetries",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `export_merge_tree_partition_max_retries` setting that controls the maximum number of retries for exporting a merge tree part in an export partition task. The default value SHALL be `3`.\n"
        "\n"
        "This setting allows users to control how many times the system will retry exporting a part before marking it as failed.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "ALTER TABLE source_table \n"
        "EXPORT PARTITION ID '2020' \n"
        "TO TABLE destination_table\n"
        "SETTINGS allow_experimental_export_merge_tree_part = 1,\n"
        "         export_merge_tree_partition_max_retries = 5\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="14.2",
)

RQ_ClickHouse_ExportPartition_ResumeAfterFailure = Requirement(
    name="RQ.ClickHouse.ExportPartition.ResumeAfterFailure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL allow export operations to resume after node failures or restarts. The system SHALL track which parts have been successfully exported and SHALL not re-export parts that were already successfully exported.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="14.3",
)

RQ_ClickHouse_ExportPartition_PartialProgress = Requirement(
    name="RQ.ClickHouse.ExportPartition.PartialProgress",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL allow export operations to make partial progress, with successfully exported parts remaining in the destination even if other parts fail. Users SHALL be able to see which parts have been successfully exported and which parts have failed.\n"
        "\n"
        "For example, users can query the export status to see partial progress:\n"
        "\n"
        "```sql\n"
        "SELECT source_table, destination_table, partition_id, status,\n"
        "       parts_total, parts_processed, parts_failed\n"
        "FROM system.replicated_partition_exports\n"
        "WHERE partition_id = '2020'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="14.4",
)

RQ_ClickHouse_ExportPartition_Cleanup = Requirement(
    name="RQ.ClickHouse.ExportPartition.Cleanup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL automatically clean up failed or completed export operations after a configurable TTL period.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="14.5",
)

RQ_ClickHouse_ExportPartition_Settings_ManifestTTL = Requirement(
    name="RQ.ClickHouse.ExportPartition.Settings.ManifestTTL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `export_merge_tree_partition_manifest_ttl` setting that determines how long the export manifest will be retained. This setting prevents the same partition from being exported twice to the same destination within the TTL period. The default value SHALL be `180` seconds.\n"
        "\n"
        "This setting only affects completed export operations and does not delete in-progress tasks. It allows users to control how long export history is maintained to prevent duplicate exports.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "ALTER TABLE source_table \n"
        "EXPORT PARTITION ID '2020' \n"
        "TO TABLE destination_table\n"
        "SETTINGS allow_experimental_export_merge_tree_part = 1,\n"
        "         export_merge_tree_partition_manifest_ttl = 360\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="14.6",
)

RQ_ClickHouse_ExportPartition_Settings_ThrowOnPendingMutations = Requirement(
    name="RQ.ClickHouse.ExportPartition.Settings.ThrowOnPendingMutations",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `export_merge_tree_part_throw_on_pending_mutations` setting that controls whether export operations should fail when pending mutations exist in the partition. The default value SHALL be `1` (enabled), meaning exports will fail with `PENDING_MUTATIONS_NOT_ALLOWED` error when pending mutations exist.\n"
        "\n"
        "When set to `0`, export operations SHALL proceed even when pending mutations exist in the partition. This allows users to export partitions without waiting for mutations to complete.\n"
        "\n"
        "This setting allows users to control whether export operations wait for mutations to complete or proceed immediately, providing flexibility for different use cases.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "ALTER TABLE source_table \n"
        "EXPORT PARTITION ID '2020' \n"
        "TO TABLE destination_table\n"
        "SETTINGS allow_experimental_export_merge_tree_part = 1,\n"
        "         export_merge_tree_part_throw_on_pending_mutations = 0\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="14.7",
)

RQ_ClickHouse_ExportPartition_Settings_ThrowOnPendingPatchParts = Requirement(
    name="RQ.ClickHouse.ExportPartition.Settings.ThrowOnPendingPatchParts",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `export_merge_tree_part_throw_on_pending_patch_parts` setting that controls whether export operations should fail when pending patch parts exist in the partition. The default value SHALL be `1` (enabled), meaning exports will fail with `PENDING_MUTATIONS_NOT_ALLOWED` error when pending patch parts exist.\n"
        "\n"
        "When set to `0`, export operations SHALL proceed even when pending patch parts exist in the partition. This allows users to export partitions without waiting for patch parts to be materialized.\n"
        "\n"
        "This setting allows users to control whether export operations wait for patch parts to be materialized or proceed with pending patch parts, providing flexibility for different use cases.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "ALTER TABLE source_table \n"
        "EXPORT PARTITION ID '2020' \n"
        "TO TABLE destination_table\n"
        "SETTINGS allow_experimental_export_merge_tree_part = 1,\n"
        "         export_merge_tree_part_throw_on_pending_patch_parts = 0\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="14.8",
)

RQ_ClickHouse_ExportPartition_QueryCancellation = Requirement(
    name="RQ.ClickHouse.ExportPartition.QueryCancellation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support cancellation of `EXPORT PARTITION`.\n" "\n"
    ),
    link=None,
    level=2,
    num="14.9",
)

RQ_ClickHouse_ExportPartition_QueryCancellation_KillExportPartition = Requirement(
    name="RQ.ClickHouse.ExportPartition.QueryCancellation.KillExportPartition",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support cancellation of in-progress `EXPORT PARTITION` operations with `KILL EXPORT PARTITION` command.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "CREATE TABLE rmt_table (id UInt64, year UInt16) \n"
        "ENGINE = ReplicatedMergeTree('/clickhouse/tables/{database}/rmt_table', 'replica1') \n"
        "PARTITION BY year ORDER BY tuple();\n"
        "\n"
        "CREATE TABLE s3_table (id UInt64, year UInt16) \n"
        "ENGINE = S3(s3_conn, filename='data', format=Parquet, partition_strategy='hive') \n"
        "PARTITION BY year;\n"
        "\n"
        "INSERT INTO rmt_table VALUES (1, 2020), (2, 2020), (3, 2020), (4, 2021);\n"
        "\n"
        "ALTER TABLE rmt_table EXPORT PARTITION ID '2020' TO TABLE s3_table;\n"
        "\n"
        "KILL EXPORT PARTITION \n"
        "WHERE partition_id = '2020' \n"
        "  AND source_table = 'rmt_table' \n"
        "  AND destination_table = 's3_table'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="14.9.1.1",
)

RQ_ClickHouse_ExportPartition_QueryCancellation_KillQuery = Requirement(
    name="RQ.ClickHouse.ExportPartition.QueryCancellation.KillQuery",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL NOT be able to cancel an in-progress `EXPORT PARTITION` operation using the `KILL QUERY` command.\n"
        "\n"
        "``\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "-- Start export in one session\n"
        "ALTER TABLE source_table \n"
        "EXPORT PARTITION ID '2020' \n"
        "TO TABLE destination_table\n"
        "SETTINGS allow_experimental_export_merge_tree_part = 1;\n"
        "\n"
        "-- Try to cancel the export in another session\n"
        "KILL QUERY WHERE query_id = '<query_id>';\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="14.9.2.1",
)

RQ_ClickHouse_ExportPartition_NetworkResilience_PacketIssues = Requirement(
    name="RQ.ClickHouse.ExportPartition.NetworkResilience.PacketIssues",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL handle network packet issues during export operations by:\n"
        "* Tolerating packet delay without data corruption or loss\n"
        "* Handling packet loss and retransmitting data as needed\n"
        "* Detecting and handling packet corruption to ensure data integrity\n"
        "* Managing packet duplication without data duplication in destination\n"
        "* Handling packet reordering to maintain correct data sequence\n"
        "* Operating correctly under packet rate limiting constraints\n"
        "* Completing exports successfully despite network impairments\n"
        "\n"
        "Network issues are common in distributed systems, and export operations must be resilient to ensure data integrity.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="15.1",
)

RQ_ClickHouse_ExportPartition_NetworkResilience_DestinationInterruption = Requirement(
    name="RQ.ClickHouse.ExportPartition.NetworkResilience.DestinationInterruption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL handle destination storage interruptions during export operations by:\n"
        "* Detecting when destination storage becomes unavailable during export\n"
        "* Retrying failed part exports when destination storage becomes available again\n"
        "* Logging failed exports in the `system.events` table with appropriate counters\n"
        "* Not leaving partial or corrupted data in destination storage when exports fail due to destination unavailability\n"
        "* Allowing exports to complete successfully once destination storage becomes available again\n"
        "* Resuming export operations from the last successfully exported part\n"
        "\n"
        "Destination storage systems may experience temporary outages, and the export should automatically recover when service is restored.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="15.2",
)

RQ_ClickHouse_ExportPartition_NetworkResilience_NodeInterruption = Requirement(
    name="RQ.ClickHouse.ExportPartition.NetworkResilience.NodeInterruption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL handle ClickHouse node interruptions during export operations by:\n"
        "* Allowing export operations to resume after node restart without data loss or duplication\n"
        "* Allowing other replicas to continue or complete export operations if a node fails\n"
        "* Not leaving partial or corrupted data in destination storage when node restarts occur\n"
        "* With safe shutdown, ensuring exports complete successfully before node shutdown when possible\n"
        "* With unsafe shutdown, allowing export operations to resume from the last checkpoint after node restart\n"
        "* Maintaining data integrity in destination storage regardless of node interruption type\n"
        "* Ensuring that parts already exported are not re-exported after node restart\n"
        "\n"
        "Node failures are common in distributed systems, and export operations must be able to recover and continue without data loss or duplication.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="15.3",
)

RQ_ClickHouse_ExportPartition_NetworkResilience_KeeperInterruption = Requirement(
    name="RQ.ClickHouse.ExportPartition.NetworkResilience.KeeperInterruption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL handle ClickHouse Keeper interruptions during the initial execution of `EXPORT PARTITION` queries.\n"
        "\n"
        "The system must handle these interruptions gracefully to ensure export operations can complete successfully.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="15.4",
)

RQ_ClickHouse_ExportPartition_Restrictions_SameTable = Requirement(
    name="RQ.ClickHouse.ExportPartition.Restrictions.SameTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL prevent exporting partitions to the same table as the source by:\n"
        "* Validating that source and destination table identifiers are different\n"
        '* Throwing a `BAD_ARGUMENTS` exception with message "Exporting to the same table is not allowed" when source and destination are identical\n'
        "* Performing this validation before any export processing begins\n"
        "\n"
        "Exporting to the same table would be redundant and could cause data duplication or conflicts.\n"
        "\n"
        "For example, the following command SHALL output an error:\n"
        "\n"
        "```sql\n"
        "ALTER TABLE my_table \n"
        "EXPORT PARTITION ID '2020' \n"
        "TO TABLE my_table\n"
        "SETTINGS allow_experimental_export_merge_tree_part = 1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="16.1.1",
)

RQ_ClickHouse_ExportPartition_Restrictions_DestinationSupport = Requirement(
    name="RQ.ClickHouse.ExportPartition.Restrictions.DestinationSupport",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL validate destination table compatibility by:\n"
        "\n"
        "* Checking that the destination storage supports importing MergeTree parts\n"
        "* Verifying that the destination uses Hive partitioning strategy (`partition_strategy = 'hive'`)\n"
        '* Throwing a `NOT_IMPLEMENTED` exception with message "Destination storage {} does not support MergeTree parts or uses unsupported partitioning" when requirements are not met\n'
        "* Performing this validation during the initial export setup phase\n"
        "\n"
        "The destination must support the format and partitioning strategy required for exported data.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="16.2.1",
)

RQ_ClickHouse_ExportPartition_Restrictions_LocalTable = Requirement(
    name="RQ.ClickHouse.ExportPartition.Restrictions.LocalTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL prevent exporting partitions to local MergeTree tables by:\n"
        "* Rejecting export operations where the destination table uses a MergeTree engine\n"
        '* Throwing a `NOT_IMPLEMENTED` exception (error code 48) with message "Destination storage MergeTree does not support MergeTree parts or uses unsupported partitioning" when attempting to export to a local table\n'
        "* Performing this validation during the initial export setup phase\n"
        "\n"
        "Export partition is designed to move data to object storage, not to local MergeTree tables.\n"
        "\n"
        "For example, if `local_table` is a MergeTree table, the following command SHALL output an error:\n"
        "\n"
        "```sql\n"
        "ALTER TABLE source_table \n"
        "EXPORT PARTITION ID '2020' \n"
        "TO TABLE local_table\n"
        "SETTINGS allow_experimental_export_merge_tree_part = 1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="16.3.1",
)

RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey = Requirement(
    name="RQ.ClickHouse.ExportPartition.Restrictions.PartitionKey",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL validate that source and destination tables have the same partition key expression by:\n"
        "* Checking that the partition key expression matches between source and destination tables\n"
        '* Throwing a `BAD_ARGUMENTS` exception (error code 36) with message "Tables have different partition key" when partition keys differ\n'
        "* Performing this validation during the initial export setup phase\n"
        "\n"
        "Matching partition keys ensure that exported data is organized correctly in the destination storage.\n"
        "\n"
        "For example, if `source_table` is partitioned by `toYYYYMM(date)` and `destination_table` is partitioned by `toYYYYMMDD(date)`, the following command SHALL output an error:\n"
        "\n"
        "```sql\n"
        "ALTER TABLE source_table \n"
        "EXPORT PARTITION ID '2020' \n"
        "TO TABLE destination_table\n"
        "SETTINGS allow_experimental_export_merge_tree_part = 1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="16.4.1",
)

RQ_ClickHouse_ExportPartition_Restrictions_SourcePartition = Requirement(
    name="RQ.ClickHouse.ExportPartition.Restrictions.SourcePartition",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL validate source partition availability by:\n"
        "* Checking that the specified partition ID exists in the source table\n"
        "* Verifying that the partition contains at least one active part (not detached or missing)\n"
        "* Throwing an exception with an appropriate error message when the partition is not found or is empty\n"
        "* Performing this validation before any export processing begins\n"
        "\n"
        "The system must verify that the partition exists and contains data before attempting to export it.\n"
        "\n"
        "For example, if partition ID '2025' does not exist in `source_table`, the following command SHALL output an error:\n"
        "\n"
        "```sql\n"
        "ALTER TABLE source_table \n"
        "EXPORT PARTITION ID '2025' \n"
        "TO TABLE destination_table\n"
        "SETTINGS allow_experimental_export_merge_tree_part = 1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="16.5.1",
)

RQ_ClickHouse_ExportPartition_Concurrency = Requirement(
    name="RQ.ClickHouse.ExportPartition.Concurrency",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support concurrent export operations by:\n"
        "* Allowing multiple partition exports to run simultaneously without interference\n"
        "* Supporting concurrent exports of different partitions to different destinations\n"
        "* Preventing concurrent exports of the same partition to the same destination\n"
        "* Allowing different replicas to export different parts of the same partition concurrently\n"
        "* Maintaining separate progress tracking for each concurrent operation\n"
        "\n"
        "Multiple users may want to export different partitions simultaneously, and the system must coordinate these operations to prevent conflicts while maximizing parallelism.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="17.1",
)

RQ_ClickHouse_ExportPartition_Concurrency_ParallelInserts = Requirement(
    name="RQ.ClickHouse.ExportPartition.Concurrency.ParallelInserts",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support export operations while parallel INSERT operations are executing on the source table by:\n"
        "* Allowing INSERT operations to continue executing while export partition is in progress\n"
        "* Exporting a consistent snapshot of partition data that existed at the time export started, or capturing data that is inserted during export depending on the export implementation\n"
        "* Handling exports correctly when merges are stopped (`SYSTEM STOP MERGES`) and parts are not merged during export\n"
        "* Handling exports correctly when merges are enabled and parts may be merged during export\n"
        "* Maintaining data integrity in both source and destination tables during concurrent inserts and exports\n"
        "* Ensuring that exported data accurately represents the partition state, whether merges are enabled or disabled\n"
        "\n"
        "Production systems often have continuous data ingestion, and export operations must work correctly even when new data is being inserted into the source table during export.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="17.2",
)

RQ_ClickHouse_ExportPartition_Concurrency_OptimizeTable = Requirement(
    name="RQ.ClickHouse.ExportPartition.Concurrency.OptimizeTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support export operations while `OPTIMIZE TABLE` operations are executing in parallel on the source table by:\n"
        "* Allowing `OPTIMIZE TABLE` operations to run concurrently with export partition operations\n"
        "* Handling merge operations that occur during export without data corruption or loss\n"
        "* Ensuring that exported data accurately represents the partition state during concurrent optimize and export operations\n"
        "* Maintaining data integrity in both source and destination tables when parts are being merged during export\n"
        "* Coordinating merge and export operations to prevent conflicts or race conditions\n"
        "\n"
        "Users may need to optimize tables for performance while export operations are in progress, and the system must handle these concurrent operations correctly.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="17.3",
)

RQ_ClickHouse_ExportPartition_Concurrency_ParallelSelects = Requirement(
    name="RQ.ClickHouse.ExportPartition.Concurrency.ParallelSelects",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support parallel SELECT queries on the source table while export partition operations are executing by:\n"
        "* Allowing multiple SELECT queries to execute concurrently with export partition operations\n"
        "* Ensuring that SELECT queries can read data from the source table during export without blocking or errors\n"
        "* Maintaining read consistency during export operations\n"
        "* Not interfering with export operations when SELECT queries are executing\n"
        "* Allowing users to query exported data from the destination table while export is in progress (for already exported partitions)\n"
        "\n"
        "Users need to be able to query data during export operations for monitoring, validation, or other operational purposes, and the system must support concurrent reads and exports.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="17.4",
)

RQ_ClickHouse_ExportPartition_Idempotency = Requirement(
    name="RQ.ClickHouse.ExportPartition.Idempotency",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL handle duplicate export operations by:\n"
        "* Preventing duplicate data from being exported when the same partition is exported multiple times to the same destination\n"
        "* Detecting when a partition export is already in progress or completed\n"
        "* Detecting when an export operation attempts to export a partition that already exists in the destination\n"
        "* Logging duplicate export attempts in the `system.events` table with appropriate counters\n"
        "* Ensuring that destination data matches source data without duplication when the same partition is exported multiple times\n"
        "* Allowing users to force re-export of a partition if needed (e.g., after TTL expiration or manual cleanup)\n"
        "\n"
        "Users may accidentally trigger the same export multiple times, and the system should prevent duplicate data while allowing legitimate re-exports when needed.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="18.1",
)

RQ_ClickHouse_ExportPartition_Settings_ForceExport = Requirement(
    name="RQ.ClickHouse.ExportPartition.Settings.ForceExport",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `export_merge_tree_partition_force_export` setting that allows users to ignore existing partition export entries and force a new export operation. The default value SHALL be `false` (turned off).\n"
        "\n"
        "When set to `true`, this setting allows users to overwrite existing export entries and force re-export of a partition, even if a previous export operation exists for the same partition and destination.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "ALTER TABLE source_table \n"
        "EXPORT PARTITION ID '2020' \n"
        "TO TABLE destination_table\n"
        "SETTINGS allow_experimental_export_merge_tree_part = 1,\n"
        "         export_merge_tree_partition_force_export = 1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="18.2",
)

RQ_ClickHouse_ExportPartition_Logging = Requirement(
    name="RQ.ClickHouse.ExportPartition.Logging",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide detailed logging for export operations by:\n"
        "* Logging all export operations (both successful and failed) with timestamps and details\n"
        "* Recording the specific partition ID in the `system.part_log` table for all operations\n"
        "* Logging export events in the `system.events` table, including:\n"
        "  * `PartsExports` - Number of successful part exports (within partitions)\n"
        "  * `PartsExportFailures` - Number of failed part exports\n"
        "  * `PartsExportDuplicated` - Number of part exports that failed because target already exists\n"
        "* Writing operation information to the `system.part_log` table with `event_type` set to `EXPORT_PARTITION`\n"
        "* Providing sufficient detail for monitoring and troubleshooting export operations\n"
        "* Logging per-part export status within partition exports\n"
        "\n"
        "Detailed logging helps users monitor export progress, troubleshoot issues, and audit export operations.\n"
        "\n"
        "For example, users can query export logs:\n"
        "\n"
        "```sql\n"
        "SELECT event_time, event_type, table, partition, rows, bytes_read, bytes_written\n"
        "FROM system.part_log\n"
        "WHERE event_type = 'EXPORT_PARTITION'\n"
        "ORDER BY event_time DESC\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="19.1",
)

RQ_ClickHouse_ExportPartition_SystemTables_Exports = Requirement(
    name="RQ.ClickHouse.ExportPartition.SystemTables.Exports",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide a `system.replicated_partition_exports` table that allows users to monitor active partition export operations with at least the following columns:\n"
        "* `source_table` - source table identifier\n"
        "* `destination_table` - destination table identifier\n"
        "* `partition_id` - the partition ID being exported\n"
        "* `status` - current status of the export operation (e.g., PENDING, IN_PROGRESS, COMPLETED, FAILED)\n"
        "* `parts_total` - total number of parts in the partition\n"
        "* `parts_processed` - number of parts successfully exported\n"
        "* `parts_failed` - number of parts that failed to export\n"
        "* `create_time` - when the export operation was created\n"
        "* `update_time` - last update time of the export operation\n"
        "\n"
        "The table SHALL track export operations before they complete and SHALL show completed or failed exports until they are cleaned up (based on TTL).\n"
        "\n"
        "Users need visibility into export operations to monitor progress, identify issues, and understand export status across the cluster.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT source_table, destination_table, partition_id, status, \n"
        "       parts_total, parts_processed, parts_failed, create_time, update_time\n"
        "FROM system.replicated_partition_exports\n"
        "WHERE status = 'IN_PROGRESS'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="20.1",
)

RQ_ClickHouse_ExportPartition_Settings_AllowExperimental = Requirement(
    name="RQ.ClickHouse.ExportPartition.Settings.AllowExperimental",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `allow_experimental_export_merge_tree_part` setting that SHALL gate the experimental export partition functionality, which SHALL be set to `1` to enable `ALTER TABLE ... EXPORT PARTITION ID ...` commands. The default value SHALL be `0` (turned off).\n"
        "\n"
        "This setting allows administrators to control access to experimental functionality and ensures users are aware they are using a feature that may change.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="21.1",
)

RQ_ClickHouse_ExportPartition_Settings_AllowExperimental_Disabled = Requirement(
    name="RQ.ClickHouse.ExportPartition.Settings.AllowExperimental.Disabled",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL prevent export partition operations when `allow_experimental_export_merge_tree_part` is set to `0` (turned off). When the setting is `0`, attempting to execute `ALTER TABLE ... EXPORT PARTITION ID ...` commands SHALL result in an error indicating that the experimental feature is not enabled.\n"
        "\n"
        "For example, the following command SHALL output an error when the setting is `0`:\n"
        "\n"
        "```sql\n"
        "ALTER TABLE source_table \n"
        "EXPORT PARTITION ID '2020' \n"
        "TO TABLE destination_table\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="21.2",
)

RQ_ClickHouse_ExportPartition_Settings_OverwriteFile = Requirement(
    name="RQ.ClickHouse.ExportPartition.Settings.OverwriteFile",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `export_merge_tree_part_overwrite_file_if_exists` setting that controls whether to overwrite files if they already exist when exporting a partition. The default value SHALL be `0` (turned off), meaning exports will fail if files already exist in the destination.\n"
        "\n"
        "This setting allows users to control whether to overwrite existing data in the destination, providing safety by default while allowing overwrites when needed.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "ALTER TABLE source_table \n"
        "EXPORT PARTITION ID '2020' \n"
        "TO TABLE destination_table\n"
        "SETTINGS allow_experimental_export_merge_tree_part = 1,\n"
        "         export_merge_tree_part_overwrite_file_if_exists = 1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="22.1",
)

RQ_ClickHouse_ExportPartition_ParallelFormatting = Requirement(
    name="RQ.ClickHouse.ExportPartition.ParallelFormatting",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support parallel formatting for export operations by:\n"
        "* Automatically enabling parallel formatting for large export operations to improve performance\n"
        "* Using the `output_format_parallel_formatting` setting to control parallel formatting behavior\n"
        "* Optimizing data processing based on export size and system resources\n"
        "* Providing consistent formatting performance across different export scenarios\n"
        "* Allowing parallel processing of multiple parts within a partition when possible\n"
        "\n"
        "Parallel formatting improves export performance, especially for large partitions with many parts.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="23.1",
)

RQ_ClickHouse_ExportPartition_ServerSettings_MaxBandwidth = Requirement(
    name="RQ.ClickHouse.ExportPartition.ServerSettings.MaxBandwidth",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `max_exports_bandwidth_for_server` server setting to limit the maximum read speed of all exports on the server in bytes per second, with `0` meaning unlimited bandwidth. The default value SHALL be `0`. This is a server-level setting configured in the server configuration file.\n"
        "\n"
        "Administrators need to control export bandwidth to avoid impacting other operations on the server.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="24.1",
)

RQ_ClickHouse_ExportPartition_ServerSettings_BackgroundMovePoolSize = Requirement(
    name="RQ.ClickHouse.ExportPartition.ServerSettings.BackgroundMovePoolSize",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `background_move_pool_size` server setting to control the maximum number of threads that will be used for executing export operations in the background. The default value SHALL be `8`. This is a server-level setting configured in the server configuration file.\n"
        "\n"
        "This setting allows administrators to balance export performance with other system operations.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="24.2",
)

RQ_ClickHouse_ExportPartition_Metrics_Export = Requirement(
    name="RQ.ClickHouse.ExportPartition.Metrics.Export",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide the `Export` current metric in `system.metrics` table that tracks the number of currently executing partition exports.\n"
        "\n"
        "This metric helps monitor system load from export operations.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="24.3",
)

RQ_ClickHouse_ExportPartition_Security_RBAC = Requirement(
    name="RQ.ClickHouse.ExportPartition.Security.RBAC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL enforce role-based access control (RBAC) for export operations. Users must have the following privileges to perform export operations:\n"
        "* **Source Table**: `SELECT` privilege on the source table to read data parts\n"
        "* **Destination Table**: `INSERT` privilege on the destination table to write exported data\n"
        "* **Database Access**: `SHOW` privilege on both source and destination databases\n"
        "* **System Tables**: `SELECT` privilege on `system.tables` and `system.replicated_partition_exports` to validate table existence and monitor exports\n"
        "\n"
        "Export operations move potentially sensitive data, and proper access controls ensure only authorized users can export partitions.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="25.1",
)

RQ_ClickHouse_ExportPartition_Security_DataEncryption = Requirement(
    name="RQ.ClickHouse.ExportPartition.Security.DataEncryption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL encrypt all data in transit to destination storage using TLS/SSL during export operations.\n"
        "\n"
        "Data encryption protects sensitive information from being intercepted or accessed during transmission to destination storage.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="25.2",
)

RQ_ClickHouse_ExportPartition_Security_Network = Requirement(
    name="RQ.ClickHouse.ExportPartition.Security.Network",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL use secure connections to destination storage during export operations. For S3-compatible storage, connections must use HTTPS. For other storage types, secure protocols appropriate to the storage system must be used.\n"
        "\n"
        "Secure network connections prevent unauthorized access and ensure data integrity during export operations.\n"
        "\n"
        "\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "\n"
    ),
    link=None,
    level=2,
    num="25.3",
)

SRS_016_ClickHouse_Export_Partition_to_S3 = Specification(
    name="SRS-016 ClickHouse Export Partition to S3",
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
        Heading(name="Exporting Partitions to S3", level=1, num="2"),
        Heading(name="RQ.ClickHouse.ExportPartition.S3", level=2, num="2.1"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.EmptyPartition", level=2, num="2.2"
        ),
        Heading(name="SQL command support", level=1, num="3"),
        Heading(name="RQ.ClickHouse.ExportPartition.SQLCommand", level=2, num="3.1"),
        Heading(name="RQ.ClickHouse.ExportPartition.IntoOutfile", level=2, num="3.2"),
        Heading(name="RQ.ClickHouse.ExportPartition.Format", level=2, num="3.3"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.SettingsClause", level=2, num="3.4"
        ),
        Heading(name="Supported source table engines", level=1, num="4"),
        Heading(name="RQ.ClickHouse.ExportPartition.SourceEngines", level=2, num="4.1"),
        Heading(name="Cluster and node support", level=1, num="5"),
        Heading(name="RQ.ClickHouse.ExportPartition.ClustersNodes", level=2, num="5.1"),
        Heading(name="RQ.ClickHouse.ExportPartition.Shards", level=2, num="5.2"),
        Heading(name="RQ.ClickHouse.ExportPartition.Versions", level=2, num="5.3"),
        Heading(name="RQ.ClickHouse.ExportPartition.LegacyTables", level=2, num="5.4"),
        Heading(name="Supported source part storage types", level=1, num="6"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.SourcePartStorage", level=2, num="6.1"
        ),
        Heading(name="Storage policies and volumes", level=1, num="7"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.StoragePolicies", level=2, num="7.1"
        ),
        Heading(name="Supported destination table engines", level=1, num="8"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.DestinationEngines", level=2, num="8.1"
        ),
        Heading(name="Temporary tables", level=1, num="9"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.TemporaryTable", level=2, num="9.1"
        ),
        Heading(name="Schema compatibility", level=1, num="10"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.SchemaCompatibility",
            level=2,
            num="10.1",
        ),
        Heading(name="Partition key types support", level=1, num="11"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.PartitionKeyTypes", level=2, num="11.1"
        ),
        Heading(name="Partition content support", level=1, num="12"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.PartitionContent", level=2, num="12.1"
        ),
        Heading(name="Column types support", level=1, num="13"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.ColumnTypes.Alias", level=2, num="13.1"
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.ColumnTypes.Materialized",
            level=2,
            num="13.2",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.ColumnTypes.Default",
            level=2,
            num="13.3",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.ColumnTypes.Ephemeral",
            level=2,
            num="13.4",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.ColumnTypes.Mixed", level=2, num="13.5"
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.SchemaChangeIsolation",
            level=2,
            num="13.6",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.LargePartitions", level=2, num="13.7"
        ),
        Heading(name="RQ.ClickHouse.ExportPartition.Corrupted", level=2, num="13.8"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.PendingMutations", level=2, num="13.9"
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.LightweightUpdate", level=2, num="13.10"
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.LightweightUpdate.MultiplePatches",
            level=2,
            num="13.11",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.LightweightUpdate.Concurrent",
            level=2,
            num="13.12",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.LightweightDelete", level=2, num="13.13"
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.LightweightDelete.MultipleDeletes",
            level=2,
            num="13.14",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.LightweightDelete.Concurrent",
            level=2,
            num="13.15",
        ),
        Heading(name="Export operation failure handling", level=1, num="14"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.RetryMechanism", level=2, num="14.1"
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Settings.MaxRetries",
            level=2,
            num="14.2",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.ResumeAfterFailure", level=2, num="14.3"
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.PartialProgress", level=2, num="14.4"
        ),
        Heading(name="RQ.ClickHouse.ExportPartition.Cleanup", level=2, num="14.5"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Settings.ManifestTTL",
            level=2,
            num="14.6",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Settings.ThrowOnPendingMutations",
            level=2,
            num="14.7",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Settings.ThrowOnPendingPatchParts",
            level=2,
            num="14.8",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.QueryCancellation", level=2, num="14.9"
        ),
        Heading(name="Kill Export Partition", level=3, num="14.9.1"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.QueryCancellation.KillExportPartition",
            level=4,
            num="14.9.1.1",
        ),
        Heading(name="Kill Query Cancellation", level=3, num="14.9.2"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.QueryCancellation.KillQuery",
            level=4,
            num="14.9.2.1",
        ),
        Heading(name="Network resilience", level=1, num="15"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.NetworkResilience.PacketIssues",
            level=2,
            num="15.1",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.NetworkResilience.DestinationInterruption",
            level=2,
            num="15.2",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.NetworkResilience.NodeInterruption",
            level=2,
            num="15.3",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.NetworkResilience.KeeperInterruption",
            level=2,
            num="15.4",
        ),
        Heading(name="Export operation restrictions", level=1, num="16"),
        Heading(name="Preventing same table exports", level=2, num="16.1"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Restrictions.SameTable",
            level=3,
            num="16.1.1",
        ),
        Heading(name="Destination table compatibility", level=2, num="16.2"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Restrictions.DestinationSupport",
            level=3,
            num="16.2.1",
        ),
        Heading(name="Local table restriction", level=2, num="16.3"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Restrictions.LocalTable",
            level=3,
            num="16.3.1",
        ),
        Heading(name="Partition key compatibility", level=2, num="16.4"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Restrictions.PartitionKey",
            level=3,
            num="16.4.1",
        ),
        Heading(name="Source partition availability", level=2, num="16.5"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Restrictions.SourcePartition",
            level=3,
            num="16.5.1",
        ),
        Heading(name="Export operation concurrency", level=1, num="17"),
        Heading(name="RQ.ClickHouse.ExportPartition.Concurrency", level=2, num="17.1"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Concurrency.ParallelInserts",
            level=2,
            num="17.2",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Concurrency.OptimizeTable",
            level=2,
            num="17.3",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Concurrency.ParallelSelects",
            level=2,
            num="17.4",
        ),
        Heading(name="Export operation idempotency", level=1, num="18"),
        Heading(name="RQ.ClickHouse.ExportPartition.Idempotency", level=2, num="18.1"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Settings.ForceExport",
            level=2,
            num="18.2",
        ),
        Heading(name="Export operation logging", level=1, num="19"),
        Heading(name="RQ.ClickHouse.ExportPartition.Logging", level=2, num="19.1"),
        Heading(name="Monitoring export operations", level=1, num="20"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.SystemTables.Exports",
            level=2,
            num="20.1",
        ),
        Heading(name="Enabling export functionality", level=1, num="21"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Settings.AllowExperimental",
            level=2,
            num="21.1",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Settings.AllowExperimental.Disabled",
            level=2,
            num="21.2",
        ),
        Heading(name="Handling file conflicts during export", level=1, num="22"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Settings.OverwriteFile",
            level=2,
            num="22.1",
        ),
        Heading(name="Export operation configuration", level=1, num="23"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.ParallelFormatting", level=2, num="23.1"
        ),
        Heading(name="Controlling export performance", level=1, num="24"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.ServerSettings.MaxBandwidth",
            level=2,
            num="24.1",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.ServerSettings.BackgroundMovePoolSize",
            level=2,
            num="24.2",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Metrics.Export", level=2, num="24.3"
        ),
        Heading(name="Export operation security", level=1, num="25"),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Security.RBAC", level=2, num="25.1"
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Security.DataEncryption",
            level=2,
            num="25.2",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPartition.Security.Network", level=2, num="25.3"
        ),
    ),
    requirements=(
        RQ_ClickHouse_ExportPartition_S3,
        RQ_ClickHouse_ExportPartition_EmptyPartition,
        RQ_ClickHouse_ExportPartition_SQLCommand,
        RQ_ClickHouse_ExportPartition_IntoOutfile,
        RQ_ClickHouse_ExportPartition_Format,
        RQ_ClickHouse_ExportPartition_SettingsClause,
        RQ_ClickHouse_ExportPartition_SourceEngines,
        RQ_ClickHouse_ExportPartition_ClustersNodes,
        RQ_ClickHouse_ExportPartition_Shards,
        RQ_ClickHouse_ExportPartition_Versions,
        RQ_ClickHouse_ExportPartition_LegacyTables,
        RQ_ClickHouse_ExportPartition_SourcePartStorage,
        RQ_ClickHouse_ExportPartition_StoragePolicies,
        RQ_ClickHouse_ExportPartition_DestinationEngines,
        RQ_ClickHouse_ExportPartition_TemporaryTable,
        RQ_ClickHouse_ExportPartition_SchemaCompatibility,
        RQ_ClickHouse_ExportPartition_PartitionKeyTypes,
        RQ_ClickHouse_ExportPartition_PartitionContent,
        RQ_ClickHouse_ExportPartition_ColumnTypes_Alias,
        RQ_ClickHouse_ExportPartition_ColumnTypes_Materialized,
        RQ_ClickHouse_ExportPartition_ColumnTypes_Default,
        RQ_ClickHouse_ExportPartition_ColumnTypes_Ephemeral,
        RQ_ClickHouse_ExportPartition_ColumnTypes_Mixed,
        RQ_ClickHouse_ExportPartition_SchemaChangeIsolation,
        RQ_ClickHouse_ExportPartition_LargePartitions,
        RQ_ClickHouse_ExportPartition_Corrupted,
        RQ_ClickHouse_ExportPartition_PendingMutations,
        RQ_ClickHouse_ExportPartition_LightweightUpdate,
        RQ_ClickHouse_ExportPartition_LightweightUpdate_MultiplePatches,
        RQ_ClickHouse_ExportPartition_LightweightUpdate_Concurrent,
        RQ_ClickHouse_ExportPartition_LightweightDelete,
        RQ_ClickHouse_ExportPartition_LightweightDelete_MultipleDeletes,
        RQ_ClickHouse_ExportPartition_LightweightDelete_Concurrent,
        RQ_ClickHouse_ExportPartition_RetryMechanism,
        RQ_ClickHouse_ExportPartition_Settings_MaxRetries,
        RQ_ClickHouse_ExportPartition_ResumeAfterFailure,
        RQ_ClickHouse_ExportPartition_PartialProgress,
        RQ_ClickHouse_ExportPartition_Cleanup,
        RQ_ClickHouse_ExportPartition_Settings_ManifestTTL,
        RQ_ClickHouse_ExportPartition_Settings_ThrowOnPendingMutations,
        RQ_ClickHouse_ExportPartition_Settings_ThrowOnPendingPatchParts,
        RQ_ClickHouse_ExportPartition_QueryCancellation,
        RQ_ClickHouse_ExportPartition_QueryCancellation_KillExportPartition,
        RQ_ClickHouse_ExportPartition_QueryCancellation_KillQuery,
        RQ_ClickHouse_ExportPartition_NetworkResilience_PacketIssues,
        RQ_ClickHouse_ExportPartition_NetworkResilience_DestinationInterruption,
        RQ_ClickHouse_ExportPartition_NetworkResilience_NodeInterruption,
        RQ_ClickHouse_ExportPartition_NetworkResilience_KeeperInterruption,
        RQ_ClickHouse_ExportPartition_Restrictions_SameTable,
        RQ_ClickHouse_ExportPartition_Restrictions_DestinationSupport,
        RQ_ClickHouse_ExportPartition_Restrictions_LocalTable,
        RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey,
        RQ_ClickHouse_ExportPartition_Restrictions_SourcePartition,
        RQ_ClickHouse_ExportPartition_Concurrency,
        RQ_ClickHouse_ExportPartition_Concurrency_ParallelInserts,
        RQ_ClickHouse_ExportPartition_Concurrency_OptimizeTable,
        RQ_ClickHouse_ExportPartition_Concurrency_ParallelSelects,
        RQ_ClickHouse_ExportPartition_Idempotency,
        RQ_ClickHouse_ExportPartition_Settings_ForceExport,
        RQ_ClickHouse_ExportPartition_Logging,
        RQ_ClickHouse_ExportPartition_SystemTables_Exports,
        RQ_ClickHouse_ExportPartition_Settings_AllowExperimental,
        RQ_ClickHouse_ExportPartition_Settings_AllowExperimental_Disabled,
        RQ_ClickHouse_ExportPartition_Settings_OverwriteFile,
        RQ_ClickHouse_ExportPartition_ParallelFormatting,
        RQ_ClickHouse_ExportPartition_ServerSettings_MaxBandwidth,
        RQ_ClickHouse_ExportPartition_ServerSettings_BackgroundMovePoolSize,
        RQ_ClickHouse_ExportPartition_Metrics_Export,
        RQ_ClickHouse_ExportPartition_Security_RBAC,
        RQ_ClickHouse_ExportPartition_Security_DataEncryption,
        RQ_ClickHouse_ExportPartition_Security_Network,
    ),
    content=r"""
# SRS-016 ClickHouse Export Partition to S3
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Exporting Partitions to S3](#exporting-partitions-to-s3)
    * 2.1 [RQ.ClickHouse.ExportPartition.S3](#rqclickhouseexportpartitions3)
    * 2.2 [RQ.ClickHouse.ExportPartition.EmptyPartition](#rqclickhouseexportpartitionemptypartition)
* 3 [SQL command support](#sql-command-support)
    * 3.1 [RQ.ClickHouse.ExportPartition.SQLCommand](#rqclickhouseexportpartitionsqlcommand)
    * 3.2 [RQ.ClickHouse.ExportPartition.IntoOutfile](#rqclickhouseexportpartitionintooutfile)
    * 3.3 [RQ.ClickHouse.ExportPartition.Format](#rqclickhouseexportpartitionformat)
    * 3.4 [RQ.ClickHouse.ExportPartition.SettingsClause](#rqclickhouseexportpartitionsettingsclause)
* 4 [Supported source table engines](#supported-source-table-engines)
    * 4.1 [RQ.ClickHouse.ExportPartition.SourceEngines](#rqclickhouseexportpartitionsourceengines)
* 5 [Cluster and node support](#cluster-and-node-support)
    * 5.1 [RQ.ClickHouse.ExportPartition.ClustersNodes](#rqclickhouseexportpartitionclustersnodes)
    * 5.2 [RQ.ClickHouse.ExportPartition.Shards](#rqclickhouseexportpartitionshards)
    * 5.3 [RQ.ClickHouse.ExportPartition.Versions](#rqclickhouseexportpartitionversions)
    * 5.4 [RQ.ClickHouse.ExportPartition.LegacyTables](#rqclickhouseexportpartitionlegacytables)
* 6 [Supported source part storage types](#supported-source-part-storage-types)
    * 6.1 [RQ.ClickHouse.ExportPartition.SourcePartStorage](#rqclickhouseexportpartitionsourcepartstorage)
* 7 [Storage policies and volumes](#storage-policies-and-volumes)
    * 7.1 [RQ.ClickHouse.ExportPartition.StoragePolicies](#rqclickhouseexportpartitionstoragepolicies)
* 8 [Supported destination table engines](#supported-destination-table-engines)
    * 8.1 [RQ.ClickHouse.ExportPartition.DestinationEngines](#rqclickhouseexportpartitiondestinationengines)
* 9 [Temporary tables](#temporary-tables)
    * 9.1 [RQ.ClickHouse.ExportPartition.TemporaryTable](#rqclickhouseexportpartitiontemporarytable)
* 10 [Schema compatibility](#schema-compatibility)
    * 10.1 [RQ.ClickHouse.ExportPartition.SchemaCompatibility](#rqclickhouseexportpartitionschemacompatibility)
* 11 [Partition key types support](#partition-key-types-support)
    * 11.1 [RQ.ClickHouse.ExportPartition.PartitionKeyTypes](#rqclickhouseexportpartitionpartitionkeytypes)
* 12 [Partition content support](#partition-content-support)
    * 12.1 [RQ.ClickHouse.ExportPartition.PartitionContent](#rqclickhouseexportpartitionpartitioncontent)
* 13 [Column types support](#column-types-support)
    * 13.1 [RQ.ClickHouse.ExportPartition.ColumnTypes.Alias](#rqclickhouseexportpartitioncolumntypesalias)
    * 13.2 [RQ.ClickHouse.ExportPartition.ColumnTypes.Materialized](#rqclickhouseexportpartitioncolumntypesmaterialized)
    * 13.3 [RQ.ClickHouse.ExportPartition.ColumnTypes.Default](#rqclickhouseexportpartitioncolumntypesdefault)
    * 13.4 [RQ.ClickHouse.ExportPartition.ColumnTypes.Ephemeral](#rqclickhouseexportpartitioncolumntypesephemeral)
    * 13.5 [RQ.ClickHouse.ExportPartition.ColumnTypes.Mixed](#rqclickhouseexportpartitioncolumntypesmixed)
    * 13.6 [RQ.ClickHouse.ExportPartition.SchemaChangeIsolation](#rqclickhouseexportpartitionschemachangeisolation)
    * 13.7 [RQ.ClickHouse.ExportPartition.LargePartitions](#rqclickhouseexportpartitionlargepartitions)
    * 13.8 [RQ.ClickHouse.ExportPartition.Corrupted](#rqclickhouseexportpartitioncorrupted)
    * 13.9 [RQ.ClickHouse.ExportPartition.PendingMutations](#rqclickhouseexportpartitionpendingmutations)
    * 13.10 [RQ.ClickHouse.ExportPartition.LightweightUpdate](#rqclickhouseexportpartitionlightweightupdate)
    * 13.11 [RQ.ClickHouse.ExportPartition.LightweightUpdate.MultiplePatches](#rqclickhouseexportpartitionlightweightupdatemultiplepatches)
    * 13.12 [RQ.ClickHouse.ExportPartition.LightweightUpdate.Concurrent](#rqclickhouseexportpartitionlightweightupdateconcurrent)
    * 13.13 [RQ.ClickHouse.ExportPartition.LightweightDelete](#rqclickhouseexportpartitionlightweightdelete)
    * 13.14 [RQ.ClickHouse.ExportPartition.LightweightDelete.MultipleDeletes](#rqclickhouseexportpartitionlightweightdeletemultipledeletes)
    * 13.15 [RQ.ClickHouse.ExportPartition.LightweightDelete.Concurrent](#rqclickhouseexportpartitionlightweightdeleteconcurrent)
* 14 [Export operation failure handling](#export-operation-failure-handling)
    * 14.1 [RQ.ClickHouse.ExportPartition.RetryMechanism](#rqclickhouseexportpartitionretrymechanism)
    * 14.2 [RQ.ClickHouse.ExportPartition.Settings.MaxRetries](#rqclickhouseexportpartitionsettingsmaxretries)
    * 14.3 [RQ.ClickHouse.ExportPartition.ResumeAfterFailure](#rqclickhouseexportpartitionresumeafterfailure)
    * 14.4 [RQ.ClickHouse.ExportPartition.PartialProgress](#rqclickhouseexportpartitionpartialprogress)
    * 14.5 [RQ.ClickHouse.ExportPartition.Cleanup](#rqclickhouseexportpartitioncleanup)
    * 14.6 [RQ.ClickHouse.ExportPartition.Settings.ManifestTTL](#rqclickhouseexportpartitionsettingsmanifestttl)
    * 14.7 [RQ.ClickHouse.ExportPartition.Settings.ThrowOnPendingMutations](#rqclickhouseexportpartitionsettingsthrowonpendingmutations)
    * 14.8 [RQ.ClickHouse.ExportPartition.Settings.ThrowOnPendingPatchParts](#rqclickhouseexportpartitionsettingsthrowonpendingpatchparts)
    * 14.9 [RQ.ClickHouse.ExportPartition.QueryCancellation](#rqclickhouseexportpartitionquerycancellation)
        * 14.9.1 [Kill Export Partition](#kill-export-partition)
            * 14.9.1.1 [RQ.ClickHouse.ExportPartition.QueryCancellation.KillExportPartition](#rqclickhouseexportpartitionquerycancellationkillexportpartition)
        * 14.9.2 [Kill Query Cancellation](#kill-query-cancellation)
            * 14.9.2.1 [RQ.ClickHouse.ExportPartition.QueryCancellation.KillQuery](#rqclickhouseexportpartitionquerycancellationkillquery)
* 15 [Network resilience](#network-resilience)
    * 15.1 [RQ.ClickHouse.ExportPartition.NetworkResilience.PacketIssues](#rqclickhouseexportpartitionnetworkresiliencepacketissues)
    * 15.2 [RQ.ClickHouse.ExportPartition.NetworkResilience.DestinationInterruption](#rqclickhouseexportpartitionnetworkresiliencedestinationinterruption)
    * 15.3 [RQ.ClickHouse.ExportPartition.NetworkResilience.NodeInterruption](#rqclickhouseexportpartitionnetworkresiliencenodeinterruption)
    * 15.4 [RQ.ClickHouse.ExportPartition.NetworkResilience.KeeperInterruption](#rqclickhouseexportpartitionnetworkresiliencekeeperinterruption)
* 16 [Export operation restrictions](#export-operation-restrictions)
    * 16.1 [Preventing same table exports](#preventing-same-table-exports)
        * 16.1.1 [RQ.ClickHouse.ExportPartition.Restrictions.SameTable](#rqclickhouseexportpartitionrestrictionssametable)
    * 16.2 [Destination table compatibility](#destination-table-compatibility)
        * 16.2.1 [RQ.ClickHouse.ExportPartition.Restrictions.DestinationSupport](#rqclickhouseexportpartitionrestrictionsdestinationsupport)
    * 16.3 [Local table restriction](#local-table-restriction)
        * 16.3.1 [RQ.ClickHouse.ExportPartition.Restrictions.LocalTable](#rqclickhouseexportpartitionrestrictionslocaltable)
    * 16.4 [Partition key compatibility](#partition-key-compatibility)
        * 16.4.1 [RQ.ClickHouse.ExportPartition.Restrictions.PartitionKey](#rqclickhouseexportpartitionrestrictionspartitionkey)
    * 16.5 [Source partition availability](#source-partition-availability)
        * 16.5.1 [RQ.ClickHouse.ExportPartition.Restrictions.SourcePartition](#rqclickhouseexportpartitionrestrictionssourcepartition)
* 17 [Export operation concurrency](#export-operation-concurrency)
    * 17.1 [RQ.ClickHouse.ExportPartition.Concurrency](#rqclickhouseexportpartitionconcurrency)
    * 17.2 [RQ.ClickHouse.ExportPartition.Concurrency.ParallelInserts](#rqclickhouseexportpartitionconcurrencyparallelinserts)
    * 17.3 [RQ.ClickHouse.ExportPartition.Concurrency.OptimizeTable](#rqclickhouseexportpartitionconcurrencyoptimizetable)
    * 17.4 [RQ.ClickHouse.ExportPartition.Concurrency.ParallelSelects](#rqclickhouseexportpartitionconcurrencyparallelselects)
* 18 [Export operation idempotency](#export-operation-idempotency)
    * 18.1 [RQ.ClickHouse.ExportPartition.Idempotency](#rqclickhouseexportpartitionidempotency)
    * 18.2 [RQ.ClickHouse.ExportPartition.Settings.ForceExport](#rqclickhouseexportpartitionsettingsforceexport)
* 19 [Export operation logging](#export-operation-logging)
    * 19.1 [RQ.ClickHouse.ExportPartition.Logging](#rqclickhouseexportpartitionlogging)
* 20 [Monitoring export operations](#monitoring-export-operations)
    * 20.1 [RQ.ClickHouse.ExportPartition.SystemTables.Exports](#rqclickhouseexportpartitionsystemtablesexports)
* 21 [Enabling export functionality](#enabling-export-functionality)
    * 21.1 [RQ.ClickHouse.ExportPartition.Settings.AllowExperimental](#rqclickhouseexportpartitionsettingsallowexperimental)
    * 21.2 [RQ.ClickHouse.ExportPartition.Settings.AllowExperimental.Disabled](#rqclickhouseexportpartitionsettingsallowexperimentaldisabled)
* 22 [Handling file conflicts during export](#handling-file-conflicts-during-export)
    * 22.1 [RQ.ClickHouse.ExportPartition.Settings.OverwriteFile](#rqclickhouseexportpartitionsettingsoverwritefile)
* 23 [Export operation configuration](#export-operation-configuration)
    * 23.1 [RQ.ClickHouse.ExportPartition.ParallelFormatting](#rqclickhouseexportpartitionparallelformatting)
* 24 [Controlling export performance](#controlling-export-performance)
    * 24.1 [RQ.ClickHouse.ExportPartition.ServerSettings.MaxBandwidth](#rqclickhouseexportpartitionserversettingsmaxbandwidth)
    * 24.2 [RQ.ClickHouse.ExportPartition.ServerSettings.BackgroundMovePoolSize](#rqclickhouseexportpartitionserversettingsbackgroundmovepoolsize)
    * 24.3 [RQ.ClickHouse.ExportPartition.Metrics.Export](#rqclickhouseexportpartitionmetricsexport)
* 25 [Export operation security](#export-operation-security)
    * 25.1 [RQ.ClickHouse.ExportPartition.Security.RBAC](#rqclickhouseexportpartitionsecurityrbac)
    * 25.2 [RQ.ClickHouse.ExportPartition.Security.DataEncryption](#rqclickhouseexportpartitionsecuritydataencryption)
    * 25.3 [RQ.ClickHouse.ExportPartition.Security.Network](#rqclickhouseexportpartitionsecuritynetwork)

## Introduction

This specification defines requirements for exporting partitions (all parts within a partition) from ReplicatedMergeTree tables to S3-compatible object storage. This feature enables users to export entire partitions containing multiple data parts across cluster nodes.

## Exporting Partitions to S3

### RQ.ClickHouse.ExportPartition.S3
version: 1.0

[ClickHouse] SHALL support exporting partitions (all parts within a partition) from ReplicatedMergeTree engine tables to S3 object storage. The export operation SHALL export all parts that belong to the specified partition ID, ensuring complete partition data is transferred to the destination.

### RQ.ClickHouse.ExportPartition.EmptyPartition
version: 1.0

[ClickHouse] SHALL support exporting from empty partitions by:
* Completing export operations successfully when the specified partition contains no parts
* Resulting in an empty destination partition when exporting from an empty source partition
* Not creating any files in destination storage when there are no parts to export in the partition
* Handling empty partitions gracefully without errors

## SQL command support

### RQ.ClickHouse.ExportPartition.SQLCommand
version: 1.0

[ClickHouse] SHALL support the following SQL command syntax for exporting partitions from ReplicatedMergeTree tables to object storage tables:

```sql
ALTER TABLE [database.]source_table_name 
EXPORT PARTITION ID 'partition_id' 
TO TABLE [database.]destination_table_name
SETTINGS allow_experimental_export_merge_tree_part = 1
```

**Parameters:**
- `source_table_name`: Name of the source ReplicatedMergeTree table
- `partition_id`: The partition ID to export (string literal), which identifies all parts belonging to that partition
- `destination_table_name`: Name of the destination object storage table
- `allow_experimental_export_merge_tree_part`: Setting that must be set to `1` to enable this experimental feature

This command allows users to export entire partitions in a single operation, which is more efficient than exporting individual parts and ensures all data for a partition is exported together.

### RQ.ClickHouse.ExportPartition.IntoOutfile
version: 1.0

[ClickHouse] SHALL support the usage of the `INTO OUTFILE` clause with `EXPORT PARTITION` and SHALL not output any errors.

For example,

```sql
ALTER TABLE source_table 
EXPORT PARTITION ID '2020' 
TO TABLE destination_table
INTO OUTFILE '/path/to/file'
SETTINGS allow_experimental_export_merge_tree_part = 1
```

### RQ.ClickHouse.ExportPartition.Format
version: 1.0

[ClickHouse] SHALL support the usage of the `FORMAT` clause with `EXPORT PARTITION` and SHALL not output any errors.

For example,

```sql
ALTER TABLE source_table 
EXPORT PARTITION ID '2020' 
TO TABLE destination_table
FORMAT JSON
SETTINGS allow_experimental_export_merge_tree_part = 1
```

### RQ.ClickHouse.ExportPartition.SettingsClause
version: 1.0

[ClickHouse] SHALL support the usage of the `SETTINGS` clause with `EXPORT PARTITION` and SHALL not output any errors.

For example,

```sql
ALTER TABLE source_table 
EXPORT PARTITION ID '2020' 
TO TABLE destination_table
SETTINGS allow_experimental_export_merge_tree_part = 1, 
         export_merge_tree_partition_max_retries = 5
```

## Supported source table engines

### RQ.ClickHouse.ExportPartition.SourceEngines
version: 1.0

[ClickHouse] SHALL support exporting partitions from the following source table engines:
* `ReplicatedMergeTree` - Replicated MergeTree engine (primary use case)
* `ReplicatedSummingMergeTree` - Replicated MergeTree with automatic summation
* `ReplicatedAggregatingMergeTree` - Replicated MergeTree with pre-aggregated data
* `ReplicatedCollapsingMergeTree` - Replicated MergeTree with row versioning
* `ReplicatedVersionedCollapsingMergeTree` - Replicated CollapsingMergeTree with version tracking
* `ReplicatedGraphiteMergeTree` - Replicated MergeTree optimized for Graphite data
* All other ReplicatedMergeTree family engines

Export partition functionality manages export operations across multiple replicas in a cluster, ensuring that parts are exported correctly and avoiding conflicts.

## Cluster and node support

### RQ.ClickHouse.ExportPartition.ClustersNodes
version: 1.0

[ClickHouse] SHALL support exporting partitions from multiple nodes in a ReplicatedMergeTree cluster to the same destination storage, ensuring that:
* Each replica in the cluster can independently export parts from the partition that it owns locally
* All parts within a partition are exported exactly once, even when distributed across multiple replicas
* Exported data from different replicas is correctly aggregated in the destination storage
* All nodes in the cluster can read the same exported partition data from the destination
* Export operations continue to make progress even if some replicas are temporarily unavailable

In a replicated cluster, different parts of the same partition may exist on different replicas. The system must coordinate exports across all replicas to ensure complete partition export without duplication.

### RQ.ClickHouse.ExportPartition.Shards
version: 1.0

[ClickHouse] SHALL support exporting partitions from source tables that are on different shards than the destination table.

### RQ.ClickHouse.ExportPartition.Versions
version: 1.0

[ClickHouse] SHALL support exporting partitions from source tables that are stored on servers with different ClickHouse versions than the destination server.

Users can export partitions from tables on servers with older ClickHouse versions to tables on servers with newer versions, enabling data migration and version upgrades.

### RQ.ClickHouse.ExportPartition.LegacyTables
version: 1.0

[ClickHouse] SHALL support exporting partitions from ReplicatedMergeTree tables that were created in ClickHouse versions that did not have the export partition feature, where the ZooKeeper structure does not contain an exports directory.

The system SHALL:
* Automatically create the necessary ZooKeeper structure (including the exports directory) when attempting to export from legacy tables
* Handle the absence of export-related metadata gracefully without errors
* Support export operations on tables created before the export partition feature was introduced
* Maintain backward compatibility with existing replicated tables regardless of when they were created

This ensures that users can export partitions from existing production tables without requiring table recreation or migration, even if those tables were created before the export partition feature existed.

## Supported source part storage types

### RQ.ClickHouse.ExportPartition.SourcePartStorage
version: 1.0

[ClickHouse] SHALL support exporting partitions regardless of the underlying storage type where the source parts are stored, including:
* **Local Disks**: Parts stored on local filesystem
* **S3/Object Storage**: Parts stored on S3 or S3-compatible object storage
* **Encrypted Disks**: Parts stored on encrypted disks (disk-level encryption)
* **Cached Disks**: Parts stored with filesystem cache enabled
* **Remote Disks**: Parts stored on HDFS, Azure Blob Storage, or Google Cloud Storage
* **Tiered Storage**: Parts stored across multiple storage tiers (hot/cold)
* **Zero-Copy Replication Disks**: Parts stored with zero-copy replication enabled

Users should be able to export partitions regardless of where the source data is physically stored, providing flexibility in storage configurations.

## Storage policies and volumes

### RQ.ClickHouse.ExportPartition.StoragePolicies
version: 1.0

[ClickHouse] SHALL support exporting partitions from tables using different storage policies, where storage policies are composed of volumes which are composed of disks, including:
* **JBOD Volumes**: Just a Bunch Of Disks volumes with multiple disks
* **External Volumes**: Volumes using external storage systems
* **Tiered Storage Policies**: Storage policies with multiple volumes for hot/cold data tiers
* **Custom Storage Policies**: Any storage policy configuration composed of volumes and disks
* Exporting all parts in a partition regardless of which volume or disk within the storage policy contains each part
* Maintaining data integrity when exporting from parts stored on any volume or disk in the storage policy

Users may have partitions with parts distributed across different storage tiers or volumes, and the export should handle all parts regardless of their storage location.

## Supported destination table engines

### RQ.ClickHouse.ExportPartition.DestinationEngines
version: 1.0

[ClickHouse] SHALL support exporting to destination tables that:
* Support object storage engines including:
  * `S3` - Amazon S3 and S3-compatible storage
  * `StorageObjectStorage` - Generic object storage interface
  * `HDFS` - Hadoop Distributed File System (with Hive partitioning)
  * `Azure` - Microsoft Azure Blob Storage (with Hive partitioning)
  * `GCS` - Google Cloud Storage (with Hive partitioning)

Export partition is designed to move data from local or replicated storage to object storage systems for long-term storage, analytics, or data sharing purposes.

## Temporary tables

### RQ.ClickHouse.ExportPartition.TemporaryTable
version: 1.0

[ClickHouse] SHALL support exporting partitions from temporary ReplicatedMergeTree tables to destination object storage tables.

For example,

```sql
CREATE TEMPORARY TABLE temp_table (p UInt64, k String, d UInt64) 
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/temp_table', '{replica}') 
PARTITION BY p ORDER BY k;

INSERT INTO temp_table VALUES (2020, 'key1', 100), (2020, 'key2', 200);

ALTER TABLE temp_table 
EXPORT PARTITION ID '2020' 
TO TABLE destination_table
SETTINGS allow_experimental_export_merge_tree_part = 1
```

## Schema compatibility

### RQ.ClickHouse.ExportPartition.SchemaCompatibility
version: 1.0

[ClickHouse] SHALL require source and destination tables to have compatible schemas for successful export operations:
* Identical physical column schemas between source and destination, with the following exceptions:
  * Source DEFAULT columns SHALL match destination regular columns (destination must not have DEFAULT columns)
  * Source ALIAS columns SHALL match destination regular columns (destination must not have ALIAS columns)
  * Source MATERIALIZED columns SHALL match destination regular columns (destination must not have MATERIALIZED columns)
  * Source EPHEMERAL columns SHALL NOT have matching columns in the destination (EPHEMERAL columns are ignored during export)
* The same partition key expression in both tables
* Compatible data types for all columns (matching base types, not column modifiers)
* Matching column order and names for all exported columns

Schema compatibility ensures that exported data can be correctly read from the destination table without data loss or corruption. Special column types (DEFAULT, ALIAS, MATERIALIZED) in the source are materialized during export and written as regular columns to the destination.

## Partition key types support

### RQ.ClickHouse.ExportPartition.PartitionKeyTypes
version: 1.0

[ClickHouse] SHALL support export operations for tables with partition key types that are compatible with Hive partitioning, as shown in the following table:

| Partition Key Type      | Supported | Examples                                                                 | Notes                          |
|-------------------------|-----------|--------------------------------------------------------------------------|--------------------------------|
| **Integer Types**       | ✅ Yes     | `UInt8`, `UInt16`, `UInt32`, `UInt64`, `Int8`, `Int16`, `Int32`, `Int64` | All integer types supported    |
| **Date/DateTime Types** | ✅ Yes     | `Date`, `Date32`, `DateTime`, `DateTime64`                               | All date/time types supported  |
| **String Types**        | ✅ Yes     | `String`, `FixedString`                                                  | All string types supported     |
| **No Partition Key**    | ✅ Yes     | Tables without `PARTITION BY` clause                                     | Unpartitioned tables supported |

[ClickHouse] SHALL automatically extract partition values from source parts and use them to create proper Hive partitioning structure in destination storage, but only for partition key types that are compatible with Hive partitioning requirements.

[ClickHouse] SHALL require destination tables to support Hive partitioning, which limits the supported partition key types to Integer, Date/DateTime, and String types. Complex expressions that result in unsupported types are not supported for export operations.

Hive partitioning is a standard way to organize data in object storage systems, making exported data compatible with various analytics tools and systems.

## Partition content support

### RQ.ClickHouse.ExportPartition.PartitionContent
version: 1.0

[ClickHouse] SHALL support export operations for partitions containing all valid MergeTree part types and their contents, including:

| Part Type         | Supported | Description                                                  | Special Features               |
|-------------------|-----------|--------------------------------------------------------------|--------------------------------|
| **Wide Parts**    | ✅ Yes     | Data of each column stored in separate files with marks      | Standard format for most parts |
| **Compact Parts** | ✅ Yes     | All column data stored in single file with single marks file | Optimized for small parts      |

[ClickHouse] SHALL export all parts within the specified partition, regardless of their type. The system SHALL automatically apply lightweight delete masks during export to ensure only non-deleted rows are exported, and SHALL maintain data integrity in the destination storage.

Partitions may contain a mix of different part types, and the export must handle all of them correctly to ensure complete partition export.

## Column types support

### RQ.ClickHouse.ExportPartition.ColumnTypes.Alias
version: 1.0

[ClickHouse] SHALL support exporting partitions containing tables with ALIAS columns by:
* Computing ALIAS column values on-the-fly from expressions during export (ALIAS columns are not stored in parts)
* Exporting ALIAS column values as regular columns in the destination table
* Requiring destination tables to have matching regular columns (not ALIAS) for exported ALIAS columns
* Including ALIAS columns when explicitly selected during export (ALIAS columns are not included in `SELECT *` by default)

ALIAS columns are computed from expressions (e.g., `arr_1 ALIAS arr[1]`). During export, the system SHALL compute the ALIAS column values and export them as regular column data to the destination table.

### RQ.ClickHouse.ExportPartition.ColumnTypes.Materialized
version: 1.0

[ClickHouse] SHALL support exporting partitions containing tables with MATERIALIZED columns by:
* Reading MATERIALIZED column values from storage during export (MATERIALIZED columns are stored in parts and computed from expressions)
* Exporting MATERIALIZED column values as regular columns in the destination table
* Requiring destination tables to have matching regular columns (not MATERIALIZED) for exported MATERIALIZED columns

MATERIALIZED columns are stored in parts and computed from expressions (e.g., `value * 2`). During export, the system SHALL read the stored MATERIALIZED column values and export them as regular column data to the destination table.

### RQ.ClickHouse.ExportPartition.ColumnTypes.Default
version: 1.0

[ClickHouse] SHALL support exporting partitions containing tables with DEFAULT columns by:
* Requiring the destination table to have a matching column that is NOT tagged as DEFAULT (must be a regular column)
* Materializing the source DEFAULT column values during export (using either the default value or explicit value provided during INSERT)
* Exporting the materialized values as a regular column to the destination table
* Correctly handling both cases:
  * When default values are used (no explicit value provided during INSERT)
  * When explicit non-default values are provided during INSERT

**Prior Behavior:**
Prior to this feature, export operations with DEFAULT columns were not possible because object storage tables do not support DEFAULT columns, and schema compatibility required 100% matching column types between source and destination.

**Current Behavior:**
With this feature, the destination table schema SHALL have a regular column (not DEFAULT) that matches the source DEFAULT column's name and data type. During export, the system SHALL compute the actual values for DEFAULT columns (default or explicit) and export them as regular column data. This allows users to export partitions from source tables with DEFAULT columns to destination object storage tables that do not support DEFAULT columns.

DEFAULT columns have default values (e.g., `status String DEFAULT 'active'`). The system SHALL materialize these values during export and write them as regular columns to the destination.

### RQ.ClickHouse.ExportPartition.ColumnTypes.Ephemeral
version: 1.0

[ClickHouse] SHALL support exporting partitions containing tables with EPHEMERAL columns by:
* Completely ignoring EPHEMERAL columns during export (EPHEMERAL columns are not stored and cannot be read from parts)
* NOT exporting EPHEMERAL columns to the destination table
* Requiring destination tables to NOT have matching columns for EPHEMERAL columns from the source table
* Allowing EPHEMERAL columns to be used in DEFAULT column expressions, where the DEFAULT column values (computed from EPHEMERAL values) SHALL be exported correctly

EPHEMERAL columns are not stored and are only used for DEFAULT column computation. During export, EPHEMERAL columns SHALL be completely ignored and SHALL NOT appear in the destination table schema.

### RQ.ClickHouse.ExportPartition.ColumnTypes.Mixed
version: 1.0

[ClickHouse] SHALL support exporting partitions containing tables with a mix of ALIAS, MATERIALIZED, EPHEMERAL, and DEFAULT columns by:
* Handling all column types correctly during export
* Exporting only stored and computed columns (ALIAS, MATERIALIZED, DEFAULT) while ignoring EPHEMERAL columns
* Maintaining data integrity when multiple column types are present in the same table

Tables may contain a mix of different column types, and the export operation SHALL handle all column types correctly, exporting only stored and computed columns while ignoring EPHEMERAL columns.

### RQ.ClickHouse.ExportPartition.SchemaChangeIsolation
version: 1.0

[ClickHouse] SHALL ensure exported partition data is isolated from subsequent schema changes by:
* Preserving exported data exactly as it was at the time of export
* Not being affected by schema changes (column drops, renames, type changes) that occur after export
* Maintaining data integrity in destination storage regardless of mutations applied to the source table after export
* Ensuring exported data reflects the source table state at the time of export, not the current state

Once a partition is exported, the exported data should remain stable and not be affected by future changes to the source table schema.

### RQ.ClickHouse.ExportPartition.LargePartitions
version: 1.0

[ClickHouse] SHALL support exporting large partitions by:
* Handling partitions with large numbers of parts (e.g., hundreds or thousands of parts)
* Processing partitions with large numbers of rows (e.g., billions of rows)
* Processing large data volumes efficiently during export
* Maintaining data integrity when exporting large partitions
* Completing export operations successfully regardless of partition size
* Allowing export operations to continue over extended periods of time for very large partitions

Production systems often have partitions containing very large amounts of data, and the export must handle these efficiently without timeouts or memory issues.

### RQ.ClickHouse.ExportPartition.Corrupted
version: 1.0

[ClickHouse] SHALL output an error and prevent export operations from proceeding when trying to export a partition that contains corrupted parts in the source table.

The system SHALL detect corruption in partitions containing compact parts, wide parts, or mixed part types.

### RQ.ClickHouse.ExportPartition.PendingMutations
version: 1.0

[ClickHouse] SHALL handle export operations when partitions contain pending mutations (e.g., DELETE mutations) by:
* By default, throwing an error (`PENDING_MUTATIONS_NOT_ALLOWED`) when pending mutations exist in the partition and `export_merge_tree_part_throw_on_pending_mutations` is set to `1` (default)
* When `export_merge_tree_part_throw_on_pending_mutations` is set to `0`, allowing export operations to proceed even when pending mutations exist
* Providing users with control over whether exports should wait for mutations to complete or proceed with pending mutations
* Maintaining data integrity in exported data regardless of the setting chosen

**Pending Mutations Behavior:**
* Pending mutations are mutations (e.g., DELETE, UPDATE) that have been initiated but not yet completed
* By default, export operations SHALL fail with `PENDING_MUTATIONS_NOT_ALLOWED` error when pending mutations exist
* Users can disable this behavior by setting `export_merge_tree_part_throw_on_pending_mutations = 0` to allow exports to proceed
* When exports proceed with pending mutations, the exported data SHALL reflect the state of the partition at the time of export, which may include unapplied mutations

This ensures that users can control whether export operations wait for mutations to complete or proceed immediately, providing flexibility for different use cases.

### RQ.ClickHouse.ExportPartition.LightweightUpdate
version: 1.0

[ClickHouse] SHALL support exporting partitions that contain patch parts created by lightweight UPDATE operations by:
* Allowing export operations to succeed even when patch parts exist in the source partition
* Exporting partition data successfully regardless of the presence of patch parts
* Not requiring patch parts to be materialized before export operations can proceed
* Handling partitions with multiple patch parts correctly during export
* Maintaining export operation stability when lightweight updates occur before or during export

Lightweight updates create patch parts that contain only updated columns and rows. The export operation SHALL succeed even in the presence of these patch parts, though the patches might not be applied to the exported data. This ensures that export operations are not blocked by lightweight update operations and can proceed independently.

**Pending Patch Parts Behavior:**
* By default, export operations SHALL throw an error (`PENDING_MUTATIONS_NOT_ALLOWED`) when pending patch parts exist in the partition and `export_merge_tree_part_throw_on_pending_patch_parts` is set to `1` (default)
* When `export_merge_tree_part_throw_on_pending_patch_parts` is set to `0`, export operations SHALL succeed even when pending patch parts exist
* This allows users to control whether exports should wait for patch parts to be materialized or proceed with pending patch parts

### RQ.ClickHouse.ExportPartition.LightweightUpdate.MultiplePatches
version: 1.0

[ClickHouse] SHALL support exporting partitions that have multiple patch parts from multiple lightweight UPDATE operations by:
* Handling partitions with multiple patch parts created by different UPDATE operations
* Exporting partition data correctly when patch parts exist for the same partition
* Not failing export operations due to the presence of multiple patch parts
* Maintaining data integrity during export when multiple lightweight updates have been applied

Users may perform multiple lightweight UPDATE operations on the same partition, creating multiple patch parts. The export operation must handle these correctly without errors.

### RQ.ClickHouse.ExportPartition.LightweightUpdate.Concurrent
version: 1.0

[ClickHouse] SHALL support export operations when lightweight UPDATE operations occur concurrently or sequentially on partitions being exported by:
* Allowing export operations to proceed when lightweight updates are performed before export starts
* Not blocking lightweight UPDATE operations when export operations are in progress
* Handling the presence of patch parts created during or before export operations
* Ensuring export operations complete successfully regardless of when lightweight updates occur relative to the export operation

Export operations and lightweight updates may occur at different times, and the system must handle both operations correctly without interference.

### RQ.ClickHouse.ExportPartition.LightweightDelete
version: 1.0

[ClickHouse] SHALL support exporting partitions that contain rows marked as deleted by lightweight DELETE operations by:
* Allowing export operations to succeed even when deleted rows exist in the source partition
* Automatically applying the `_row_exists` mask during export to ensure only non-deleted rows are exported
* Exporting partition data successfully regardless of the presence of deleted rows
* Not requiring deleted rows to be physically removed before export operations can proceed
* Maintaining export operation stability when lightweight deletes occur before or during export

Lightweight deletes mark rows as deleted using a hidden `_row_exists` system column. The export operation SHALL automatically apply this mask to ensure only visible (non-deleted) rows are exported to the destination, maintaining data consistency between source and destination tables.

### RQ.ClickHouse.ExportPartition.LightweightDelete.MultipleDeletes
version: 1.0

[ClickHouse] SHALL support exporting partitions that have multiple lightweight DELETE operations applied by:
* Handling partitions with multiple delete mutations on the same partition
* Exporting partition data correctly when multiple deletes have been applied
* Not failing export operations due to the presence of multiple delete mutations
* Maintaining data integrity during export when multiple lightweight deletes have been applied
* Ensuring that only non-deleted rows are exported even when multiple delete operations affect overlapping rows

Users may perform multiple lightweight DELETE operations on the same partition, creating multiple delete mutations. The export operation must handle these correctly and ensure that all deleted rows are excluded from the export.

### RQ.ClickHouse.ExportPartition.LightweightDelete.Concurrent
version: 1.0

[ClickHouse] SHALL support export operations when lightweight DELETE operations occur concurrently or sequentially on partitions being exported by:
* Allowing export operations to proceed when lightweight deletes are performed before export starts
* Not blocking lightweight DELETE operations when export operations are in progress
* Handling the presence of delete masks (`_row_exists` column) created during or before export operations
* Ensuring export operations complete successfully regardless of when lightweight deletes occur relative to the export operation
* Applying delete masks correctly to ensure deleted rows are not exported

Export operations and lightweight deletes may occur at different times, and the system must handle both operations correctly without interference, ensuring that deleted rows are always excluded from exports.

## Export operation failure handling

### RQ.ClickHouse.ExportPartition.RetryMechanism
version: 1.0

[ClickHouse] SHALL automatically retry failed part exports within a partition up to a configurable maximum retry count. If all retry attempts are exhausted for a part, the entire partition export operation SHALL be marked as failed.

Unlike single-part exports, partition exports involve multiple parts and may take significant time. Retry mechanisms ensure that temporary failures don't require restarting the entire export operation.

### RQ.ClickHouse.ExportPartition.Settings.MaxRetries
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_partition_max_retries` setting that controls the maximum number of retries for exporting a merge tree part in an export partition task. The default value SHALL be `3`.

This setting allows users to control how many times the system will retry exporting a part before marking it as failed.

For example,

```sql
ALTER TABLE source_table 
EXPORT PARTITION ID '2020' 
TO TABLE destination_table
SETTINGS allow_experimental_export_merge_tree_part = 1,
         export_merge_tree_partition_max_retries = 5
```

### RQ.ClickHouse.ExportPartition.ResumeAfterFailure
version: 1.0

[ClickHouse] SHALL allow export operations to resume after node failures or restarts. The system SHALL track which parts have been successfully exported and SHALL not re-export parts that were already successfully exported.

### RQ.ClickHouse.ExportPartition.PartialProgress
version: 1.0

[ClickHouse] SHALL allow export operations to make partial progress, with successfully exported parts remaining in the destination even if other parts fail. Users SHALL be able to see which parts have been successfully exported and which parts have failed.

For example, users can query the export status to see partial progress:

```sql
SELECT source_table, destination_table, partition_id, status,
       parts_total, parts_processed, parts_failed
FROM system.replicated_partition_exports
WHERE partition_id = '2020'
```

### RQ.ClickHouse.ExportPartition.Cleanup
version: 1.0

[ClickHouse] SHALL automatically clean up failed or completed export operations after a configurable TTL period.

### RQ.ClickHouse.ExportPartition.Settings.ManifestTTL
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_partition_manifest_ttl` setting that determines how long the export manifest will be retained. This setting prevents the same partition from being exported twice to the same destination within the TTL period. The default value SHALL be `180` seconds.

This setting only affects completed export operations and does not delete in-progress tasks. It allows users to control how long export history is maintained to prevent duplicate exports.

For example,

```sql
ALTER TABLE source_table 
EXPORT PARTITION ID '2020' 
TO TABLE destination_table
SETTINGS allow_experimental_export_merge_tree_part = 1,
         export_merge_tree_partition_manifest_ttl = 360
```

### RQ.ClickHouse.ExportPartition.Settings.ThrowOnPendingMutations
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_part_throw_on_pending_mutations` setting that controls whether export operations should fail when pending mutations exist in the partition. The default value SHALL be `1` (enabled), meaning exports will fail with `PENDING_MUTATIONS_NOT_ALLOWED` error when pending mutations exist.

When set to `0`, export operations SHALL proceed even when pending mutations exist in the partition. This allows users to export partitions without waiting for mutations to complete.

This setting allows users to control whether export operations wait for mutations to complete or proceed immediately, providing flexibility for different use cases.

For example,

```sql
ALTER TABLE source_table 
EXPORT PARTITION ID '2020' 
TO TABLE destination_table
SETTINGS allow_experimental_export_merge_tree_part = 1,
         export_merge_tree_part_throw_on_pending_mutations = 0
```

### RQ.ClickHouse.ExportPartition.Settings.ThrowOnPendingPatchParts
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_part_throw_on_pending_patch_parts` setting that controls whether export operations should fail when pending patch parts exist in the partition. The default value SHALL be `1` (enabled), meaning exports will fail with `PENDING_MUTATIONS_NOT_ALLOWED` error when pending patch parts exist.

When set to `0`, export operations SHALL proceed even when pending patch parts exist in the partition. This allows users to export partitions without waiting for patch parts to be materialized.

This setting allows users to control whether export operations wait for patch parts to be materialized or proceed with pending patch parts, providing flexibility for different use cases.

For example,

```sql
ALTER TABLE source_table 
EXPORT PARTITION ID '2020' 
TO TABLE destination_table
SETTINGS allow_experimental_export_merge_tree_part = 1,
         export_merge_tree_part_throw_on_pending_patch_parts = 0
```

### RQ.ClickHouse.ExportPartition.QueryCancellation
version: 1.0

[ClickHouse] SHALL support cancellation of `EXPORT PARTITION`.

#### Kill Export Partition

##### RQ.ClickHouse.ExportPartition.QueryCancellation.KillExportPartition
version: 1.0

[ClickHouse] SHALL support cancellation of in-progress `EXPORT PARTITION` operations with `KILL EXPORT PARTITION` command.

For example,

```sql
CREATE TABLE rmt_table (id UInt64, year UInt16) 
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{database}/rmt_table', 'replica1') 
PARTITION BY year ORDER BY tuple();

CREATE TABLE s3_table (id UInt64, year UInt16) 
ENGINE = S3(s3_conn, filename='data', format=Parquet, partition_strategy='hive') 
PARTITION BY year;

INSERT INTO rmt_table VALUES (1, 2020), (2, 2020), (3, 2020), (4, 2021);

ALTER TABLE rmt_table EXPORT PARTITION ID '2020' TO TABLE s3_table;

KILL EXPORT PARTITION 
WHERE partition_id = '2020' 
  AND source_table = 'rmt_table' 
  AND destination_table = 's3_table'
```

#### Kill Query Cancellation

##### RQ.ClickHouse.ExportPartition.QueryCancellation.KillQuery
version: 1.0

[ClickHouse] SHALL NOT be able to cancel an in-progress `EXPORT PARTITION` operation using the `KILL QUERY` command.

``
For example,

```sql
-- Start export in one session
ALTER TABLE source_table 
EXPORT PARTITION ID '2020' 
TO TABLE destination_table
SETTINGS allow_experimental_export_merge_tree_part = 1;

-- Try to cancel the export in another session
KILL QUERY WHERE query_id = '<query_id>';
```

## Network resilience

### RQ.ClickHouse.ExportPartition.NetworkResilience.PacketIssues
version: 1.0

[ClickHouse] SHALL handle network packet issues during export operations by:
* Tolerating packet delay without data corruption or loss
* Handling packet loss and retransmitting data as needed
* Detecting and handling packet corruption to ensure data integrity
* Managing packet duplication without data duplication in destination
* Handling packet reordering to maintain correct data sequence
* Operating correctly under packet rate limiting constraints
* Completing exports successfully despite network impairments

Network issues are common in distributed systems, and export operations must be resilient to ensure data integrity.

### RQ.ClickHouse.ExportPartition.NetworkResilience.DestinationInterruption
version: 1.0

[ClickHouse] SHALL handle destination storage interruptions during export operations by:
* Detecting when destination storage becomes unavailable during export
* Retrying failed part exports when destination storage becomes available again
* Logging failed exports in the `system.events` table with appropriate counters
* Not leaving partial or corrupted data in destination storage when exports fail due to destination unavailability
* Allowing exports to complete successfully once destination storage becomes available again
* Resuming export operations from the last successfully exported part

Destination storage systems may experience temporary outages, and the export should automatically recover when service is restored.

### RQ.ClickHouse.ExportPartition.NetworkResilience.NodeInterruption
version: 1.0

[ClickHouse] SHALL handle ClickHouse node interruptions during export operations by:
* Allowing export operations to resume after node restart without data loss or duplication
* Allowing other replicas to continue or complete export operations if a node fails
* Not leaving partial or corrupted data in destination storage when node restarts occur
* With safe shutdown, ensuring exports complete successfully before node shutdown when possible
* With unsafe shutdown, allowing export operations to resume from the last checkpoint after node restart
* Maintaining data integrity in destination storage regardless of node interruption type
* Ensuring that parts already exported are not re-exported after node restart

Node failures are common in distributed systems, and export operations must be able to recover and continue without data loss or duplication.

### RQ.ClickHouse.ExportPartition.NetworkResilience.KeeperInterruption
version: 1.0

[ClickHouse] SHALL handle ClickHouse Keeper interruptions during the initial execution of `EXPORT PARTITION` queries.

The system must handle these interruptions gracefully to ensure export operations can complete successfully.

## Export operation restrictions

### Preventing same table exports

#### RQ.ClickHouse.ExportPartition.Restrictions.SameTable
version: 1.0

[ClickHouse] SHALL prevent exporting partitions to the same table as the source by:
* Validating that source and destination table identifiers are different
* Throwing a `BAD_ARGUMENTS` exception with message "Exporting to the same table is not allowed" when source and destination are identical
* Performing this validation before any export processing begins

Exporting to the same table would be redundant and could cause data duplication or conflicts.

For example, the following command SHALL output an error:

```sql
ALTER TABLE my_table 
EXPORT PARTITION ID '2020' 
TO TABLE my_table
SETTINGS allow_experimental_export_merge_tree_part = 1
```

### Destination table compatibility

#### RQ.ClickHouse.ExportPartition.Restrictions.DestinationSupport
version: 1.0

[ClickHouse] SHALL validate destination table compatibility by:

* Checking that the destination storage supports importing MergeTree parts
* Verifying that the destination uses Hive partitioning strategy (`partition_strategy = 'hive'`)
* Throwing a `NOT_IMPLEMENTED` exception with message "Destination storage {} does not support MergeTree parts or uses unsupported partitioning" when requirements are not met
* Performing this validation during the initial export setup phase

The destination must support the format and partitioning strategy required for exported data.

### Local table restriction

#### RQ.ClickHouse.ExportPartition.Restrictions.LocalTable
version: 1.0

[ClickHouse] SHALL prevent exporting partitions to local MergeTree tables by:
* Rejecting export operations where the destination table uses a MergeTree engine
* Throwing a `NOT_IMPLEMENTED` exception (error code 48) with message "Destination storage MergeTree does not support MergeTree parts or uses unsupported partitioning" when attempting to export to a local table
* Performing this validation during the initial export setup phase

Export partition is designed to move data to object storage, not to local MergeTree tables.

For example, if `local_table` is a MergeTree table, the following command SHALL output an error:

```sql
ALTER TABLE source_table 
EXPORT PARTITION ID '2020' 
TO TABLE local_table
SETTINGS allow_experimental_export_merge_tree_part = 1
```

### Partition key compatibility

#### RQ.ClickHouse.ExportPartition.Restrictions.PartitionKey
version: 1.0

[ClickHouse] SHALL validate that source and destination tables have the same partition key expression by:
* Checking that the partition key expression matches between source and destination tables
* Throwing a `BAD_ARGUMENTS` exception (error code 36) with message "Tables have different partition key" when partition keys differ
* Performing this validation during the initial export setup phase

Matching partition keys ensure that exported data is organized correctly in the destination storage.

For example, if `source_table` is partitioned by `toYYYYMM(date)` and `destination_table` is partitioned by `toYYYYMMDD(date)`, the following command SHALL output an error:

```sql
ALTER TABLE source_table 
EXPORT PARTITION ID '2020' 
TO TABLE destination_table
SETTINGS allow_experimental_export_merge_tree_part = 1
```

### Source partition availability

#### RQ.ClickHouse.ExportPartition.Restrictions.SourcePartition
version: 1.0

[ClickHouse] SHALL validate source partition availability by:
* Checking that the specified partition ID exists in the source table
* Verifying that the partition contains at least one active part (not detached or missing)
* Throwing an exception with an appropriate error message when the partition is not found or is empty
* Performing this validation before any export processing begins

The system must verify that the partition exists and contains data before attempting to export it.

For example, if partition ID '2025' does not exist in `source_table`, the following command SHALL output an error:

```sql
ALTER TABLE source_table 
EXPORT PARTITION ID '2025' 
TO TABLE destination_table
SETTINGS allow_experimental_export_merge_tree_part = 1
```

## Export operation concurrency

### RQ.ClickHouse.ExportPartition.Concurrency
version: 1.0

[ClickHouse] SHALL support concurrent export operations by:
* Allowing multiple partition exports to run simultaneously without interference
* Supporting concurrent exports of different partitions to different destinations
* Preventing concurrent exports of the same partition to the same destination
* Allowing different replicas to export different parts of the same partition concurrently
* Maintaining separate progress tracking for each concurrent operation

Multiple users may want to export different partitions simultaneously, and the system must coordinate these operations to prevent conflicts while maximizing parallelism.

### RQ.ClickHouse.ExportPartition.Concurrency.ParallelInserts
version: 1.0

[ClickHouse] SHALL support export operations while parallel INSERT operations are executing on the source table by:
* Allowing INSERT operations to continue executing while export partition is in progress
* Exporting a consistent snapshot of partition data that existed at the time export started, or capturing data that is inserted during export depending on the export implementation
* Handling exports correctly when merges are stopped (`SYSTEM STOP MERGES`) and parts are not merged during export
* Handling exports correctly when merges are enabled and parts may be merged during export
* Maintaining data integrity in both source and destination tables during concurrent inserts and exports
* Ensuring that exported data accurately represents the partition state, whether merges are enabled or disabled

Production systems often have continuous data ingestion, and export operations must work correctly even when new data is being inserted into the source table during export.

### RQ.ClickHouse.ExportPartition.Concurrency.OptimizeTable
version: 1.0

[ClickHouse] SHALL support export operations while `OPTIMIZE TABLE` operations are executing in parallel on the source table by:
* Allowing `OPTIMIZE TABLE` operations to run concurrently with export partition operations
* Handling merge operations that occur during export without data corruption or loss
* Ensuring that exported data accurately represents the partition state during concurrent optimize and export operations
* Maintaining data integrity in both source and destination tables when parts are being merged during export
* Coordinating merge and export operations to prevent conflicts or race conditions

Users may need to optimize tables for performance while export operations are in progress, and the system must handle these concurrent operations correctly.

### RQ.ClickHouse.ExportPartition.Concurrency.ParallelSelects
version: 1.0

[ClickHouse] SHALL support parallel SELECT queries on the source table while export partition operations are executing by:
* Allowing multiple SELECT queries to execute concurrently with export partition operations
* Ensuring that SELECT queries can read data from the source table during export without blocking or errors
* Maintaining read consistency during export operations
* Not interfering with export operations when SELECT queries are executing
* Allowing users to query exported data from the destination table while export is in progress (for already exported partitions)

Users need to be able to query data during export operations for monitoring, validation, or other operational purposes, and the system must support concurrent reads and exports.

## Export operation idempotency

### RQ.ClickHouse.ExportPartition.Idempotency
version: 1.0

[ClickHouse] SHALL handle duplicate export operations by:
* Preventing duplicate data from being exported when the same partition is exported multiple times to the same destination
* Detecting when a partition export is already in progress or completed
* Detecting when an export operation attempts to export a partition that already exists in the destination
* Logging duplicate export attempts in the `system.events` table with appropriate counters
* Ensuring that destination data matches source data without duplication when the same partition is exported multiple times
* Allowing users to force re-export of a partition if needed (e.g., after TTL expiration or manual cleanup)

Users may accidentally trigger the same export multiple times, and the system should prevent duplicate data while allowing legitimate re-exports when needed.

### RQ.ClickHouse.ExportPartition.Settings.ForceExport
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_partition_force_export` setting that allows users to ignore existing partition export entries and force a new export operation. The default value SHALL be `false` (turned off).

When set to `true`, this setting allows users to overwrite existing export entries and force re-export of a partition, even if a previous export operation exists for the same partition and destination.

For example,

```sql
ALTER TABLE source_table 
EXPORT PARTITION ID '2020' 
TO TABLE destination_table
SETTINGS allow_experimental_export_merge_tree_part = 1,
         export_merge_tree_partition_force_export = 1
```

## Export operation logging

### RQ.ClickHouse.ExportPartition.Logging
version: 1.0

[ClickHouse] SHALL provide detailed logging for export operations by:
* Logging all export operations (both successful and failed) with timestamps and details
* Recording the specific partition ID in the `system.part_log` table for all operations
* Logging export events in the `system.events` table, including:
  * `PartsExports` - Number of successful part exports (within partitions)
  * `PartsExportFailures` - Number of failed part exports
  * `PartsExportDuplicated` - Number of part exports that failed because target already exists
* Writing operation information to the `system.part_log` table with `event_type` set to `EXPORT_PARTITION`
* Providing sufficient detail for monitoring and troubleshooting export operations
* Logging per-part export status within partition exports

Detailed logging helps users monitor export progress, troubleshoot issues, and audit export operations.

For example, users can query export logs:

```sql
SELECT event_time, event_type, table, partition, rows, bytes_read, bytes_written
FROM system.part_log
WHERE event_type = 'EXPORT_PARTITION'
ORDER BY event_time DESC
```

## Monitoring export operations

### RQ.ClickHouse.ExportPartition.SystemTables.Exports
version: 1.0

[ClickHouse] SHALL provide a `system.replicated_partition_exports` table that allows users to monitor active partition export operations with at least the following columns:
* `source_table` - source table identifier
* `destination_table` - destination table identifier
* `partition_id` - the partition ID being exported
* `status` - current status of the export operation (e.g., PENDING, IN_PROGRESS, COMPLETED, FAILED)
* `parts_total` - total number of parts in the partition
* `parts_processed` - number of parts successfully exported
* `parts_failed` - number of parts that failed to export
* `create_time` - when the export operation was created
* `update_time` - last update time of the export operation

The table SHALL track export operations before they complete and SHALL show completed or failed exports until they are cleaned up (based on TTL).

Users need visibility into export operations to monitor progress, identify issues, and understand export status across the cluster.

For example,

```sql
SELECT source_table, destination_table, partition_id, status, 
       parts_total, parts_processed, parts_failed, create_time, update_time
FROM system.replicated_partition_exports
WHERE status = 'IN_PROGRESS'
```

## Enabling export functionality

### RQ.ClickHouse.ExportPartition.Settings.AllowExperimental
version: 1.0

[ClickHouse] SHALL support the `allow_experimental_export_merge_tree_part` setting that SHALL gate the experimental export partition functionality, which SHALL be set to `1` to enable `ALTER TABLE ... EXPORT PARTITION ID ...` commands. The default value SHALL be `0` (turned off).

This setting allows administrators to control access to experimental functionality and ensures users are aware they are using a feature that may change.

### RQ.ClickHouse.ExportPartition.Settings.AllowExperimental.Disabled
version: 1.0

[ClickHouse] SHALL prevent export partition operations when `allow_experimental_export_merge_tree_part` is set to `0` (turned off). When the setting is `0`, attempting to execute `ALTER TABLE ... EXPORT PARTITION ID ...` commands SHALL result in an error indicating that the experimental feature is not enabled.

For example, the following command SHALL output an error when the setting is `0`:

```sql
ALTER TABLE source_table 
EXPORT PARTITION ID '2020' 
TO TABLE destination_table
```

## Handling file conflicts during export

### RQ.ClickHouse.ExportPartition.Settings.OverwriteFile
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_part_overwrite_file_if_exists` setting that controls whether to overwrite files if they already exist when exporting a partition. The default value SHALL be `0` (turned off), meaning exports will fail if files already exist in the destination.

This setting allows users to control whether to overwrite existing data in the destination, providing safety by default while allowing overwrites when needed.

For example,

```sql
ALTER TABLE source_table 
EXPORT PARTITION ID '2020' 
TO TABLE destination_table
SETTINGS allow_experimental_export_merge_tree_part = 1,
         export_merge_tree_part_overwrite_file_if_exists = 1
```

## Export operation configuration

### RQ.ClickHouse.ExportPartition.ParallelFormatting
version: 1.0

[ClickHouse] SHALL support parallel formatting for export operations by:
* Automatically enabling parallel formatting for large export operations to improve performance
* Using the `output_format_parallel_formatting` setting to control parallel formatting behavior
* Optimizing data processing based on export size and system resources
* Providing consistent formatting performance across different export scenarios
* Allowing parallel processing of multiple parts within a partition when possible

Parallel formatting improves export performance, especially for large partitions with many parts.

## Controlling export performance

### RQ.ClickHouse.ExportPartition.ServerSettings.MaxBandwidth
version: 1.0

[ClickHouse] SHALL support the `max_exports_bandwidth_for_server` server setting to limit the maximum read speed of all exports on the server in bytes per second, with `0` meaning unlimited bandwidth. The default value SHALL be `0`. This is a server-level setting configured in the server configuration file.

Administrators need to control export bandwidth to avoid impacting other operations on the server.

### RQ.ClickHouse.ExportPartition.ServerSettings.BackgroundMovePoolSize
version: 1.0

[ClickHouse] SHALL support the `background_move_pool_size` server setting to control the maximum number of threads that will be used for executing export operations in the background. The default value SHALL be `8`. This is a server-level setting configured in the server configuration file.

This setting allows administrators to balance export performance with other system operations.

### RQ.ClickHouse.ExportPartition.Metrics.Export
version: 1.0

[ClickHouse] SHALL provide the `Export` current metric in `system.metrics` table that tracks the number of currently executing partition exports.

This metric helps monitor system load from export operations.

## Export operation security

### RQ.ClickHouse.ExportPartition.Security.RBAC
version: 1.0

[ClickHouse] SHALL enforce role-based access control (RBAC) for export operations. Users must have the following privileges to perform export operations:
* **Source Table**: `SELECT` privilege on the source table to read data parts
* **Destination Table**: `INSERT` privilege on the destination table to write exported data
* **Database Access**: `SHOW` privilege on both source and destination databases
* **System Tables**: `SELECT` privilege on `system.tables` and `system.replicated_partition_exports` to validate table existence and monitor exports

Export operations move potentially sensitive data, and proper access controls ensure only authorized users can export partitions.

### RQ.ClickHouse.ExportPartition.Security.DataEncryption
version: 1.0

[ClickHouse] SHALL encrypt all data in transit to destination storage using TLS/SSL during export operations.

Data encryption protects sensitive information from being intercepted or accessed during transmission to destination storage.

### RQ.ClickHouse.ExportPartition.Security.Network
version: 1.0

[ClickHouse] SHALL use secure connections to destination storage during export operations. For S3-compatible storage, connections must use HTTPS. For other storage types, secure protocols appropriate to the storage system must be used.

Secure network connections prevent unauthorized access and ensure data integrity during export operations.


[ClickHouse]: https://clickhouse.com
""",
)
