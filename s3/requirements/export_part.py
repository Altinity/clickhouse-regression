# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_ClickHouse_ExportPart_S3 = Requirement(
    name="RQ.ClickHouse.ExportPart.S3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting data parts from MergeTree engine tables to S3 object storage.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.1",
)

RQ_ClickHouse_ExportPart_SQLCommand = Requirement(
    name="RQ.ClickHouse.ExportPart.SQLCommand",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the following SQL command syntax for exporting MergeTree data parts to object storage tables:\n"
        "\n"
        "```sql\n"
        "ALTER TABLE [database.]source_table_name \n"
        "EXPORT PART 'part_name' \n"
        "TO TABLE [database.]destination_table_name\n"
        "```\n"
        "\n"
        "**Parameters:**\n"
        "- `source_table_name`: Name of the source MergeTree table\n"
        "- `part_name`: Name of the specific part to export (string literal)\n"
        "- `destination_table_name`: Name of the destination object storage table\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.1",
)

RQ_ClickHouse_ExportPart_SourceEngines = Requirement(
    name="RQ.ClickHouse.ExportPart.SourceEngines",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting from the following source table engines:\n"
        "* `MergeTree` - Base MergeTree engine\n"
        "* `ReplicatedMergeTree` - Replicated MergeTree engine with ZooKeeper coordination\n"
        "* `SummingMergeTree` - MergeTree with automatic summation of numeric columns\n"
        "* `AggregatingMergeTree` - MergeTree with pre-aggregated data\n"
        "* `CollapsingMergeTree` - MergeTree with row versioning for updates\n"
        "* `VersionedCollapsingMergeTree` - CollapsingMergeTree with version tracking\n"
        "* `GraphiteMergeTree` - MergeTree optimized for Graphite data\n"
        "* All other MergeTree family engines that inherit from `MergeTreeData`\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.1",
)

RQ_ClickHouse_ExportPart_SourcePartStorage = Requirement(
    name="RQ.ClickHouse.ExportPart.SourcePartStorage",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting data parts regardless of the underlying storage type where the source parts are stored, including:\n"
        "* **Local Disks**: Parts stored on local filesystem\n"
        "* **S3/Object Storage**: Parts stored on S3 or S3-compatible object storage\n"
        "* **Encrypted Disks**: Parts stored on encrypted disks (disk-level encryption)\n"
        "* **Cached Disks**: Parts stored with filesystem cache enabled\n"
        "* **Remote Disks**: Parts stored on HDFS, Azure Blob Storage, or Google Cloud Storage\n"
        "* **Tiered Storage**: Parts stored across multiple storage tiers (hot/cold)\n"
        "* **Zero-Copy Replication Disks**: Parts stored with zero-copy replication enabled\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.1",
)

RQ_ClickHouse_ExportPart_DestinationEngines = Requirement(
    name="RQ.ClickHouse.ExportPart.DestinationEngines",
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
    ),
    link=None,
    level=2,
    num="6.1",
)

RQ_ClickHouse_ExportPart_DestinationSetup = Requirement(
    name="RQ.ClickHouse.ExportPart.DestinationSetup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL handle destination setup and file management by:\n"
        "* Creating appropriate import sinks for destination storage systems\n"
        "* Generating unique file names in the format `{part_name}_{checksum_hex}` to avoid conflicts\n"
        "* Allowing destination storage to determine the final file path based on Hive partitioning\n"
        "* Creating files in the destination storage that users can observe and access\n"
        "* Providing the final destination file path in the `system.exports` table for monitoring\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.1",
)

RQ_ClickHouse_ExportPart_DataPreparation = Requirement(
    name="RQ.ClickHouse.ExportPart.DataPreparation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL prepare data for export by:\n"
        "* Automatically selecting all physical columns from source table metadata\n"
        "* Extracting partition key values for proper Hive partitioning in destination\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.1",
)

RQ_ClickHouse_ExportPart_SchemaCompatibility = Requirement(
    name="RQ.ClickHouse.ExportPart.SchemaCompatibility",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL require source and destination tables to have compatible schemas for successful export operations:\n"
        "* Identical physical column schemas between source and destination\n"
        "* The same partition key expression in both tables\n"
        "* Compatible data types for all columns\n"
        "* Matching column order and names\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.1",
)

RQ_ClickHouse_ExportPart_PartitionKeyTypes = Requirement(
    name="RQ.ClickHouse.ExportPart.PartitionKeyTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support export operations for tables with partition key types that are compatible with Hive partitioning, as shown in the following table:\n"
        "\n"
        "| Partition Key Type | Supported | Examples | Notes |\n"
        "|-------------------|------------|----------|-------|\n"
        "| **Integer Types** | ✅ Yes | `UInt8`, `UInt16`, `UInt32`, `UInt64`, `Int8`, `Int16`, `Int32`, `Int64` | All integer types supported |\n"
        "| **Date/DateTime Types** | ✅ Yes | `Date`, `Date32`, `DateTime`, `DateTime64` | All date/time types supported |\n"
        "| **String Types** | ✅ Yes | `String`, `FixedString` | All string types supported |\n"
        "| **No Partition Key** | ✅ Yes | Tables without `PARTITION BY` clause | Unpartitioned tables supported |\n"
        "\n"
        "[ClickHouse] SHALL automatically extract partition values from source parts and use them to create proper Hive partitioning structure in destination storage, but only for partition key types that are compatible with Hive partitioning requirements.\n"
        "\n"
        "[ClickHouse] SHALL require destination tables to support Hive partitioning, which limits the supported partition key types to Integer, Date/DateTime, and String types. Complex expressions that result in unsupported types are not supported for export operations.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.1",
)

RQ_ClickHouse_ExportPart_PartTypes = Requirement(
    name="RQ.ClickHouse.ExportPart.PartTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support export operations for all valid MergeTree part types and their contents, including:\n"
        "\n"
        "| Part Type | Supported | Description | Special Features |\n"
        "|-----------|------------|-------------|------------------|\n"
        "| **Wide Parts** | ✅ Yes | Data of each column stored in separate files with marks | Standard format for most parts |\n"
        "| **Compact Parts** | ✅ Yes | All column data stored in single file with single marks file | Optimized for small parts |\n"
        "| **Regular Parts** | ✅ Yes | Standard data parts created by inserts, merges, mutations | Full data content |\n"
        "| **Patch Parts** | ✅ Yes | Lightweight update parts containing only changed columns | Applied during export |\n"
        "| **Active Parts** | ✅ Yes | Currently active data parts | Primary export target |\n"
        "| **Outdated Parts** | ✅ Yes | Parts that have been replaced by newer versions | Can be exported for backup |\n"
        "\n"
        "[ClickHouse] SHALL handle all special columns and metadata present in parts during export:\n"
        "\n"
        "| Column Type | Supported | Description | Export Behavior |\n"
        "|-------------|------------|-------------|-----------------|\n"
        "| **Physical Columns** | ✅ Yes | User-defined table columns | All physical columns exported |\n"
        "| **RowExistsColumn (_row_exists)** | ✅ Yes | Lightweight delete mask showing row existence | Exported to maintain delete state |\n"
        "| **BlockNumberColumn (_block_number)** | ✅ Yes | Original block number from insert | Exported for row identification |\n"
        "| **BlockOffsetColumn (_block_offset)** | ✅ Yes | Original row offset within block | Exported for row identification |\n"
        "| **PartDataVersionColumn (_part_data_version)** | ✅ Yes | Data version for mutations | Exported for version tracking |\n"
        "| **Virtual Columns** | ✅ Yes | Runtime columns like _part, _partition_id | Generated during export |\n"
        "| **System Metadata** | ✅ Yes | Checksums, compression info, serialization | Preserved in export |\n"
        "\n"
        "[ClickHouse] SHALL handle all mutation and schema change information present in parts:\n"
        "\n"
        "| Mutation/Schema Type | Supported | Description | Export Behavior |\n"
        "|---------------------|------------|-------------|-----------------|\n"
        "| **Mutation Commands** | ✅ Yes | DELETE, UPDATE, MATERIALIZE_INDEX, DROP_COLUMN, RENAME_COLUMN | Applied during export |\n"
        "| **Alter Conversions** | ✅ Yes | Column renames, type changes, schema modifications | Applied during export |\n"
        "| **Patch Parts** | ✅ Yes | Lightweight updates with only changed columns | Applied during export |\n"
        "| **Mutation Versions** | ✅ Yes | Version tracking for applied mutations | Preserved in export |\n"
        "| **Schema Changes** | ✅ Yes | ALTER MODIFY, ALTER DROP, ALTER RENAME | Applied during export |\n"
        "| **TTL Information** | ✅ Yes | Time-to-live settings and expiration data | Preserved in export |\n"
        "| **Index Information** | ✅ Yes | Primary key, secondary indices, projections | Preserved in export |\n"
        "| **Statistics** | ✅ Yes | Column statistics and sampling information | Preserved in export |\n"
        "\n"
        "[ClickHouse] SHALL automatically apply lightweight delete masks during export to ensure only non-deleted rows are exported, and SHALL handle all part metadata including checksums, compression information, serialization details, mutation history, schema changes, and structural modifications to maintain data integrity in the destination storage.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="11.1",
)

RQ_ClickHouse_ExportPart_FailureHandling = Requirement(
    name="RQ.ClickHouse.ExportPart.FailureHandling",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL handle export operation failures in the following ways:\n"
        "* **Stateless Operation**: Export operations are stateless and ephemeral\n"
        "* **No Recovery**: If an export fails, it fails completely with no retry mechanism\n"
        "* **No State Persistence**: No export manifests or state are preserved across server restarts\n"
        "* **Simple Failure**: Export operations either succeed completely or fail with an error message\n"
        "* **No Partial Exports**: Failed exports leave no partial or corrupted data in destination storage\n"
        "\n"
    ),
    link=None,
    level=2,
    num="12.1",
)

RQ_ClickHouse_ExportPart_Restrictions_SameTable = Requirement(
    name="RQ.ClickHouse.ExportPart.Restrictions.SameTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL prevent exporting parts to the same table as the source by:\n"
        "* Validating that source and destination table identifiers are different\n"
        '* Throwing a `BAD_ARGUMENTS` exception with message "Exporting to the same table is not allowed" when source and destination are identical\n'
        "* Performing this validation before any export processing begins\n"
        "\n"
    ),
    link=None,
    level=3,
    num="13.1.1",
)

RQ_ClickHouse_ExportPart_Restrictions_DestinationSupport = Requirement(
    name="RQ.ClickHouse.ExportPart.Restrictions.DestinationSupport",
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
    ),
    link=None,
    level=3,
    num="13.2.1",
)

RQ_ClickHouse_ExportPart_Restrictions_SourcePart = Requirement(
    name="RQ.ClickHouse.ExportPart.Restrictions.SourcePart",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL validate source part availability by:\n"
        "\n"
        "* Checking that the specified part exists in the source table\n"
        "* Verifying the part is in an active state (not detached or missing)\n"
        "* Throwing a `NO_SUCH_DATA_PART` exception with message \"No such data part '{}' to export in table '{}'\" when the part is not found\n"
        "* Performing this validation before creating the export manifest\n"
        "\n"
    ),
    link=None,
    level=3,
    num="13.3.1",
)

RQ_ClickHouse_ExportPart_Concurrency = Requirement(
    name="RQ.ClickHouse.ExportPart.Concurrency",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support concurrent export operations by:\n"
        "\n"
        "* Allowing multiple exports to run simultaneously without interference\n"
        "* Processing export operations asynchronously in the background\n"
        "* Preventing race conditions and data corruption during concurrent operations\n"
        "* Supporting concurrent exports of different parts to different destinations\n"
        "* Preventing concurrent exports of the same part to the same destination\n"
        "* Maintaining separate progress tracking and state for each concurrent operation\n"
        "* Ensuring thread safety across all concurrent export operations\n"
        "\n"
    ),
    link=None,
    level=2,
    num="14.1",
)

RQ_ClickHouse_ExportPart_Idempotency = Requirement(
    name="RQ.ClickHouse.ExportPart.Idempotency",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL ensure export operations are idempotent by:\n"
        "\n"
        "* Allowing the same part to be exported multiple times safely without data corruption\n"
        "* Supporting file overwrite control through the `export_merge_tree_part_overwrite_file_if_exists` setting\n"
        "* Generating unique file names using part name and checksum to avoid conflicts\n"
        "* Maintaining export state consistency across retries\n"
        "\n"
    ),
    link=None,
    level=2,
    num="15.1",
)

RQ_ClickHouse_ExportPart_ErrorRecovery_GracefulFailure = Requirement(
    name="RQ.ClickHouse.ExportPart.ErrorRecovery.GracefulFailure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL handle export failures gracefully by:\n"
        "* Allowing users to retry failed export operations\n"
        "* Maintaining system stability even when exports fail\n"
        "* Not corrupting source data when export operations fail\n"
        "* Continuing to process other export operations when one fails\n"
        "\n"
    ),
    link=None,
    level=3,
    num="16.1.1",
)

RQ_ClickHouse_ExportPart_ErrorRecovery_AutomaticCleanup = Requirement(
    name="RQ.ClickHouse.ExportPart.ErrorRecovery.AutomaticCleanup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL automatically clean up failed export operations by:\n"
        "* Removing export manifests from the system when operations fail\n"
        "* Cleaning up any partial data written to destination storage\n"
        "* Releasing system resources (memory, file handles) used by failed exports\n"
        "* Updating export status to reflect the failure state\n"
        "* Allowing the system to recover and process other export operations\n"
        "\n"
    ),
    link=None,
    level=3,
    num="16.2.1",
)

RQ_ClickHouse_ExportPart_Logging = Requirement(
    name="RQ.ClickHouse.ExportPart.Logging",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide detailed logging for export operations by:\n"
        "* Logging all export operations (both successful and failed) with timestamps and details\n"
        "* Recording the specific part name and destination for all operations\n"
        "* Including execution time and progress information for all operations\n"
        "* Writing operation information to the `system.part_log` table with the following columns:\n"
        "  * `event_type` - Set to `EXPORT_PART` for export operations\n"
        "  * `event_time` - Timestamp when the export operation occurred\n"
        "  * `table` - Source table name\n"
        "  * `part_name` - Name of the part being exported\n"
        "  * `path_on_disk` - Path to the part in source storage\n"
        "  * `duration_ms` - Execution time in milliseconds\n"
        "  * `error` - Error message if the export failed (empty for successful exports)\n"
        "  * `thread_id` - Thread ID performing the export\n"
        "* Providing sufficient detail for monitoring and troubleshooting export operations\n"
        "\n"
    ),
    link=None,
    level=2,
    num="17.1",
)

RQ_ClickHouse_ExportPart_SystemTables_Exports = Requirement(
    name="RQ.ClickHouse.ExportPart.SystemTables.Exports",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide a `system.exports` table that allows users to monitor active and completed export operations, track progress metrics, performance statistics, and troubleshoot export issues with the following columns:\n"
        "\n"
        "* `source_database`, `source_table` - source table identifiers\n"
        "* `destination_database`, `destination_table` - destination table identifiers  \n"
        "* `create_time` - when export was submitted\n"
        "* `part_name` - name of the exported part\n"
        "* `destination_file_path` - path in destination storage\n"
        "* `elapsed` - execution time in seconds\n"
        "* `rows_read`, `total_rows_to_read` - progress metrics\n"
        "* `total_size_bytes_compressed`, `total_size_bytes_uncompressed` - size metrics\n"
        "* `bytes_read_uncompressed` - bytes processed\n"
        "* `memory_usage`, `peak_memory_usage` - memory consumption\n"
        "\n"
    ),
    link=None,
    level=2,
    num="18.1",
)

RQ_ClickHouse_ExportPart_Settings_AllowExperimental = Requirement(
    name="RQ.ClickHouse.ExportPart.Settings.AllowExperimental",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `allow_experimental_export_merge_tree_part` setting that SHALL gate the experimental export part functionality, which SHALL be set to `1` to enable `ALTER TABLE ... EXPORT PART ...` commands. The default value SHALL be `0` (turned off).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="19.1",
)

RQ_ClickHouse_ExportPart_Settings_OverwriteFile = Requirement(
    name="RQ.ClickHouse.ExportPart.Settings.OverwriteFile",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `export_merge_tree_part_overwrite_file_if_exists` setting that controls whether to overwrite files if they already exist when exporting a merge tree part. The default value SHALL be `0` (turned off).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="20.1",
)

RQ_ClickHouse_ExportPart_ParallelFormatting = Requirement(
    name="RQ.ClickHouse.ExportPart.ParallelFormatting",
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
        "\n"
    ),
    link=None,
    level=2,
    num="21.1",
)

RQ_ClickHouse_ExportPart_ServerSettings_MaxBandwidth = Requirement(
    name="RQ.ClickHouse.ExportPart.ServerSettings.MaxBandwidth",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `max_exports_bandwidth_for_server` server setting to limit the maximum read speed of all exports on the server in bytes per second, with `0` meaning unlimited bandwidth. The default value SHALL be `0`. This is a server-level setting configured in the server configuration file.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="22.1",
)

RQ_ClickHouse_ExportPart_Events = Requirement(
    name="RQ.ClickHouse.ExportPart.Events",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide the following export-related events in the `system.events` table:\n"
        "* `PartsExports` - Number of successful part exports\n"
        "* `PartsExportFailures` - Number of failed part exports  \n"
        "* `PartsExportDuplicated` - Number of part exports that failed because target already exists\n"
        "* `PartsExportTotalMilliseconds` - Total time spent on part export operations in milliseconds\n"
        "* `ExportsThrottlerBytes` - Bytes passed through the exports throttler\n"
        "* `ExportsThrottlerSleepMicroseconds` - Total time queries were sleeping to conform to export bandwidth throttling\n"
        "\n"
    ),
    link=None,
    level=2,
    num="23.1",
)

RQ_ClickHouse_ExportPart_Metrics_Export = Requirement(
    name="RQ.ClickHouse.ExportPart.Metrics.Export",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide the `Export` current metric in `system.metrics` table that tracks the number of currently executing exports.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="23.2",
)

RQ_ClickHouse_ExportPart_Security = Requirement(
    name="RQ.ClickHouse.ExportPart.Security",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL enforce security requirements for export operations:\n"
        "* **RBAC**: Users must have the following privileges:\n"
        "  * **Source Table**: `SELECT` privilege on the source table to read data parts\n"
        "  * **Destination Table**: `INSERT` privilege on the destination table to write exported data\n"
        "  * **Database Access**: `SHOW` privilege on both source and destination databases\n"
        "  * **System Tables**: `SELECT` privilege on `system.tables` to validate table existence\n"
        "* **Data Encryption**: All data in transit to destination storage must be encrypted using TLS/SSL\n"
        "* **Network Security**: Export operations must use secure connections to destination storage (HTTPS for S3, secure protocols for other storage)\n"
        "* **Credential Management**: Export operations must use secure credential storage and avoid exposing credentials in logs\n"
        "\n"
        "\n"
        "[ClickHouse]: https://clickhouse.com\n"
    ),
    link=None,
    level=2,
    num="24.1",
)

SRS_015_ClickHouse_Export_Part_to_S3 = Specification(
    name="SRS-015 ClickHouse Export Part to S3",
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
        Heading(name="Exporting Parts to S3", level=1, num="2"),
        Heading(name="RQ.ClickHouse.ExportPart.S3", level=2, num="2.1"),
        Heading(name="SQL command support", level=1, num="3"),
        Heading(name="RQ.ClickHouse.ExportPart.SQLCommand", level=2, num="3.1"),
        Heading(name="Supported source table engines", level=1, num="4"),
        Heading(name="RQ.ClickHouse.ExportPart.SourceEngines", level=2, num="4.1"),
        Heading(name="Supported source part storage types", level=1, num="5"),
        Heading(name="RQ.ClickHouse.ExportPart.SourcePartStorage", level=2, num="5.1"),
        Heading(name="Supported destination table engines", level=1, num="6"),
        Heading(name="RQ.ClickHouse.ExportPart.DestinationEngines", level=2, num="6.1"),
        Heading(name="Destination setup and file management", level=1, num="7"),
        Heading(name="RQ.ClickHouse.ExportPart.DestinationSetup", level=2, num="7.1"),
        Heading(name="Export data preparation", level=1, num="8"),
        Heading(name="RQ.ClickHouse.ExportPart.DataPreparation", level=2, num="8.1"),
        Heading(name="Schema compatibility", level=1, num="9"),
        Heading(
            name="RQ.ClickHouse.ExportPart.SchemaCompatibility", level=2, num="9.1"
        ),
        Heading(name="Partition key types support", level=1, num="10"),
        Heading(name="RQ.ClickHouse.ExportPart.PartitionKeyTypes", level=2, num="10.1"),
        Heading(name="Part types and content support", level=1, num="11"),
        Heading(name="RQ.ClickHouse.ExportPart.PartTypes", level=2, num="11.1"),
        Heading(name="Export operation failure handling", level=1, num="12"),
        Heading(name="RQ.ClickHouse.ExportPart.FailureHandling", level=2, num="12.1"),
        Heading(name="Export operation restrictions", level=1, num="13"),
        Heading(name="Preventing same table exports", level=2, num="13.1"),
        Heading(
            name="RQ.ClickHouse.ExportPart.Restrictions.SameTable",
            level=3,
            num="13.1.1",
        ),
        Heading(name="Destination table compatibility", level=2, num="13.2"),
        Heading(
            name="RQ.ClickHouse.ExportPart.Restrictions.DestinationSupport",
            level=3,
            num="13.2.1",
        ),
        Heading(name="Source part availability", level=2, num="13.3"),
        Heading(
            name="RQ.ClickHouse.ExportPart.Restrictions.SourcePart",
            level=3,
            num="13.3.1",
        ),
        Heading(name="Export operation concurrency", level=1, num="14"),
        Heading(name="RQ.ClickHouse.ExportPart.Concurrency", level=2, num="14.1"),
        Heading(name="Export operation idempotency", level=1, num="15"),
        Heading(name="RQ.ClickHouse.ExportPart.Idempotency", level=2, num="15.1"),
        Heading(name="Export operation error recovery", level=1, num="16"),
        Heading(name="Graceful failure handling", level=2, num="16.1"),
        Heading(
            name="RQ.ClickHouse.ExportPart.ErrorRecovery.GracefulFailure",
            level=3,
            num="16.1.1",
        ),
        Heading(name="Automatic cleanup on failure", level=2, num="16.2"),
        Heading(
            name="RQ.ClickHouse.ExportPart.ErrorRecovery.AutomaticCleanup",
            level=3,
            num="16.2.1",
        ),
        Heading(name="Export operation logging", level=1, num="17"),
        Heading(name="RQ.ClickHouse.ExportPart.Logging", level=2, num="17.1"),
        Heading(name="Monitoring export operations", level=1, num="18"),
        Heading(
            name="RQ.ClickHouse.ExportPart.SystemTables.Exports", level=2, num="18.1"
        ),
        Heading(name="Enabling export functionality", level=1, num="19"),
        Heading(
            name="RQ.ClickHouse.ExportPart.Settings.AllowExperimental",
            level=2,
            num="19.1",
        ),
        Heading(name="Handling file conflicts during export", level=1, num="20"),
        Heading(
            name="RQ.ClickHouse.ExportPart.Settings.OverwriteFile", level=2, num="20.1"
        ),
        Heading(name="Export operation configuration", level=1, num="21"),
        Heading(
            name="RQ.ClickHouse.ExportPart.ParallelFormatting", level=2, num="21.1"
        ),
        Heading(name="Controlling export performance", level=1, num="22"),
        Heading(
            name="RQ.ClickHouse.ExportPart.ServerSettings.MaxBandwidth",
            level=2,
            num="22.1",
        ),
        Heading(name="Monitoring export performance metrics", level=1, num="23"),
        Heading(name="RQ.ClickHouse.ExportPart.Events", level=2, num="23.1"),
        Heading(name="RQ.ClickHouse.ExportPart.Metrics.Export", level=2, num="23.2"),
        Heading(name="Export operation security", level=1, num="24"),
        Heading(name="RQ.ClickHouse.ExportPart.Security", level=2, num="24.1"),
    ),
    requirements=(
        RQ_ClickHouse_ExportPart_S3,
        RQ_ClickHouse_ExportPart_SQLCommand,
        RQ_ClickHouse_ExportPart_SourceEngines,
        RQ_ClickHouse_ExportPart_SourcePartStorage,
        RQ_ClickHouse_ExportPart_DestinationEngines,
        RQ_ClickHouse_ExportPart_DestinationSetup,
        RQ_ClickHouse_ExportPart_DataPreparation,
        RQ_ClickHouse_ExportPart_SchemaCompatibility,
        RQ_ClickHouse_ExportPart_PartitionKeyTypes,
        RQ_ClickHouse_ExportPart_PartTypes,
        RQ_ClickHouse_ExportPart_FailureHandling,
        RQ_ClickHouse_ExportPart_Restrictions_SameTable,
        RQ_ClickHouse_ExportPart_Restrictions_DestinationSupport,
        RQ_ClickHouse_ExportPart_Restrictions_SourcePart,
        RQ_ClickHouse_ExportPart_Concurrency,
        RQ_ClickHouse_ExportPart_Idempotency,
        RQ_ClickHouse_ExportPart_ErrorRecovery_GracefulFailure,
        RQ_ClickHouse_ExportPart_ErrorRecovery_AutomaticCleanup,
        RQ_ClickHouse_ExportPart_Logging,
        RQ_ClickHouse_ExportPart_SystemTables_Exports,
        RQ_ClickHouse_ExportPart_Settings_AllowExperimental,
        RQ_ClickHouse_ExportPart_Settings_OverwriteFile,
        RQ_ClickHouse_ExportPart_ParallelFormatting,
        RQ_ClickHouse_ExportPart_ServerSettings_MaxBandwidth,
        RQ_ClickHouse_ExportPart_Events,
        RQ_ClickHouse_ExportPart_Metrics_Export,
        RQ_ClickHouse_ExportPart_Security,
    ),
    content=r"""
# SRS-015 ClickHouse Export Part to S3
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Exporting Parts to S3](#exporting-parts-to-s3)
    * 2.1 [RQ.ClickHouse.ExportPart.S3](#rqclickhouseexportparts3)
* 3 [SQL command support](#sql-command-support)
    * 3.1 [RQ.ClickHouse.ExportPart.SQLCommand](#rqclickhouseexportpartsqlcommand)
* 4 [Supported source table engines](#supported-source-table-engines)
    * 4.1 [RQ.ClickHouse.ExportPart.SourceEngines](#rqclickhouseexportpartsourceengines)
* 5 [Supported source part storage types](#supported-source-part-storage-types)
    * 5.1 [RQ.ClickHouse.ExportPart.SourcePartStorage](#rqclickhouseexportpartsourcepartstorage)
* 6 [Supported destination table engines](#supported-destination-table-engines)
    * 6.1 [RQ.ClickHouse.ExportPart.DestinationEngines](#rqclickhouseexportpartdestinationengines)
* 7 [Destination setup and file management](#destination-setup-and-file-management)
    * 7.1 [RQ.ClickHouse.ExportPart.DestinationSetup](#rqclickhouseexportpartdestinationsetup)
* 8 [Export data preparation](#export-data-preparation)
    * 8.1 [RQ.ClickHouse.ExportPart.DataPreparation](#rqclickhouseexportpartdatapreparation)
* 9 [Schema compatibility](#schema-compatibility)
    * 9.1 [RQ.ClickHouse.ExportPart.SchemaCompatibility](#rqclickhouseexportpartschemacompatibility)
* 10 [Partition key types support](#partition-key-types-support)
    * 10.1 [RQ.ClickHouse.ExportPart.PartitionKeyTypes](#rqclickhouseexportpartpartitionkeytypes)
* 11 [Part types and content support](#part-types-and-content-support)
    * 11.1 [RQ.ClickHouse.ExportPart.PartTypes](#rqclickhouseexportpartparttypes)
* 12 [Export operation failure handling](#export-operation-failure-handling)
    * 12.1 [RQ.ClickHouse.ExportPart.FailureHandling](#rqclickhouseexportpartfailurehandling)
* 13 [Export operation restrictions](#export-operation-restrictions)
    * 13.1 [Preventing same table exports](#preventing-same-table-exports)
        * 13.1.1 [RQ.ClickHouse.ExportPart.Restrictions.SameTable](#rqclickhouseexportpartrestrictionssametable)
    * 13.2 [Destination table compatibility](#destination-table-compatibility)
        * 13.2.1 [RQ.ClickHouse.ExportPart.Restrictions.DestinationSupport](#rqclickhouseexportpartrestrictionsdestinationsupport)
    * 13.3 [Source part availability](#source-part-availability)
        * 13.3.1 [RQ.ClickHouse.ExportPart.Restrictions.SourcePart](#rqclickhouseexportpartrestrictionssourcepart)
* 14 [Export operation concurrency](#export-operation-concurrency)
    * 14.1 [RQ.ClickHouse.ExportPart.Concurrency](#rqclickhouseexportpartconcurrency)
* 15 [Export operation idempotency](#export-operation-idempotency)
    * 15.1 [RQ.ClickHouse.ExportPart.Idempotency](#rqclickhouseexportpartidempotency)
* 16 [Export operation error recovery](#export-operation-error-recovery)
    * 16.1 [Graceful failure handling](#graceful-failure-handling)
        * 16.1.1 [RQ.ClickHouse.ExportPart.ErrorRecovery.GracefulFailure](#rqclickhouseexportparterrorrecoverygracefulfailure)
    * 16.2 [Automatic cleanup on failure](#automatic-cleanup-on-failure)
        * 16.2.1 [RQ.ClickHouse.ExportPart.ErrorRecovery.AutomaticCleanup](#rqclickhouseexportparterrorrecoveryautomaticcleanup)
* 17 [Export operation logging](#export-operation-logging)
    * 17.1 [RQ.ClickHouse.ExportPart.Logging](#rqclickhouseexportpartlogging)
* 18 [Monitoring export operations](#monitoring-export-operations)
    * 18.1 [RQ.ClickHouse.ExportPart.SystemTables.Exports](#rqclickhouseexportpartsystemtablesexports)
* 19 [Enabling export functionality](#enabling-export-functionality)
    * 19.1 [RQ.ClickHouse.ExportPart.Settings.AllowExperimental](#rqclickhouseexportpartsettingsallowexperimental)
* 20 [Handling file conflicts during export](#handling-file-conflicts-during-export)
    * 20.1 [RQ.ClickHouse.ExportPart.Settings.OverwriteFile](#rqclickhouseexportpartsettingsoverwritefile)
* 21 [Export operation configuration](#export-operation-configuration)
    * 21.1 [RQ.ClickHouse.ExportPart.ParallelFormatting](#rqclickhouseexportpartparallelformatting)
* 22 [Controlling export performance](#controlling-export-performance)
    * 22.1 [RQ.ClickHouse.ExportPart.ServerSettings.MaxBandwidth](#rqclickhouseexportpartserversettingsmaxbandwidth)
* 23 [Monitoring export performance metrics](#monitoring-export-performance-metrics)
    * 23.1 [RQ.ClickHouse.ExportPart.Events](#rqclickhouseexportpartevents)
    * 23.2 [RQ.ClickHouse.ExportPart.Metrics.Export](#rqclickhouseexportpartmetricsexport)
* 24 [Export operation security](#export-operation-security)
    * 24.1 [RQ.ClickHouse.ExportPart.Security](#rqclickhouseexportpartsecurity)

## Introduction

This specification defines requirements for exporting individual MergeTree data parts to S3-compatible object storage.

## Exporting Parts to S3

### RQ.ClickHouse.ExportPart.S3
version: 1.0

[ClickHouse] SHALL support exporting data parts from MergeTree engine tables to S3 object storage.

## SQL command support

### RQ.ClickHouse.ExportPart.SQLCommand
version: 1.0

[ClickHouse] SHALL support the following SQL command syntax for exporting MergeTree data parts to object storage tables:

```sql
ALTER TABLE [database.]source_table_name 
EXPORT PART 'part_name' 
TO TABLE [database.]destination_table_name
```

**Parameters:**
- `source_table_name`: Name of the source MergeTree table
- `part_name`: Name of the specific part to export (string literal)
- `destination_table_name`: Name of the destination object storage table

## Supported source table engines

### RQ.ClickHouse.ExportPart.SourceEngines
version: 1.0

[ClickHouse] SHALL support exporting from the following source table engines:
* `MergeTree` - Base MergeTree engine
* `ReplicatedMergeTree` - Replicated MergeTree engine with ZooKeeper coordination
* `SummingMergeTree` - MergeTree with automatic summation of numeric columns
* `AggregatingMergeTree` - MergeTree with pre-aggregated data
* `CollapsingMergeTree` - MergeTree with row versioning for updates
* `VersionedCollapsingMergeTree` - CollapsingMergeTree with version tracking
* `GraphiteMergeTree` - MergeTree optimized for Graphite data
* All other MergeTree family engines that inherit from `MergeTreeData`

## Supported source part storage types

### RQ.ClickHouse.ExportPart.SourcePartStorage
version: 1.0

[ClickHouse] SHALL support exporting data parts regardless of the underlying storage type where the source parts are stored, including:
* **Local Disks**: Parts stored on local filesystem
* **S3/Object Storage**: Parts stored on S3 or S3-compatible object storage
* **Encrypted Disks**: Parts stored on encrypted disks (disk-level encryption)
* **Cached Disks**: Parts stored with filesystem cache enabled
* **Remote Disks**: Parts stored on HDFS, Azure Blob Storage, or Google Cloud Storage
* **Tiered Storage**: Parts stored across multiple storage tiers (hot/cold)
* **Zero-Copy Replication Disks**: Parts stored with zero-copy replication enabled

## Supported destination table engines

### RQ.ClickHouse.ExportPart.DestinationEngines
version: 1.0

[ClickHouse] SHALL support exporting to destination tables that:
* Support object storage engines including:
  * `S3` - Amazon S3 and S3-compatible storage
  * `StorageObjectStorage` - Generic object storage interface
  * `HDFS` - Hadoop Distributed File System (with Hive partitioning)
  * `Azure` - Microsoft Azure Blob Storage (with Hive partitioning)
  * `GCS` - Google Cloud Storage (with Hive partitioning)

## Destination setup and file management

### RQ.ClickHouse.ExportPart.DestinationSetup
version: 1.0

[ClickHouse] SHALL handle destination setup and file management by:
* Creating appropriate import sinks for destination storage systems
* Generating unique file names in the format `{part_name}_{checksum_hex}` to avoid conflicts
* Allowing destination storage to determine the final file path based on Hive partitioning
* Creating files in the destination storage that users can observe and access
* Providing the final destination file path in the `system.exports` table for monitoring

## Export data preparation

### RQ.ClickHouse.ExportPart.DataPreparation
version: 1.0

[ClickHouse] SHALL prepare data for export by:
* Automatically selecting all physical columns from source table metadata
* Extracting partition key values for proper Hive partitioning in destination

## Schema compatibility

### RQ.ClickHouse.ExportPart.SchemaCompatibility
version: 1.0

[ClickHouse] SHALL require source and destination tables to have compatible schemas for successful export operations:
* Identical physical column schemas between source and destination
* The same partition key expression in both tables
* Compatible data types for all columns
* Matching column order and names

## Partition key types support

### RQ.ClickHouse.ExportPart.PartitionKeyTypes
version: 1.0

[ClickHouse] SHALL support export operations for tables with partition key types that are compatible with Hive partitioning, as shown in the following table:

| Partition Key Type | Supported | Examples | Notes |
|-------------------|------------|----------|-------|
| **Integer Types** | ✅ Yes | `UInt8`, `UInt16`, `UInt32`, `UInt64`, `Int8`, `Int16`, `Int32`, `Int64` | All integer types supported |
| **Date/DateTime Types** | ✅ Yes | `Date`, `Date32`, `DateTime`, `DateTime64` | All date/time types supported |
| **String Types** | ✅ Yes | `String`, `FixedString` | All string types supported |
| **No Partition Key** | ✅ Yes | Tables without `PARTITION BY` clause | Unpartitioned tables supported |

[ClickHouse] SHALL automatically extract partition values from source parts and use them to create proper Hive partitioning structure in destination storage, but only for partition key types that are compatible with Hive partitioning requirements.

[ClickHouse] SHALL require destination tables to support Hive partitioning, which limits the supported partition key types to Integer, Date/DateTime, and String types. Complex expressions that result in unsupported types are not supported for export operations.

## Part types and content support

### RQ.ClickHouse.ExportPart.PartTypes
version: 1.0

[ClickHouse] SHALL support export operations for all valid MergeTree part types and their contents, including:

| Part Type | Supported | Description | Special Features |
|-----------|------------|-------------|------------------|
| **Wide Parts** | ✅ Yes | Data of each column stored in separate files with marks | Standard format for most parts |
| **Compact Parts** | ✅ Yes | All column data stored in single file with single marks file | Optimized for small parts |
| **Regular Parts** | ✅ Yes | Standard data parts created by inserts, merges, mutations | Full data content |
| **Patch Parts** | ✅ Yes | Lightweight update parts containing only changed columns | Applied during export |
| **Active Parts** | ✅ Yes | Currently active data parts | Primary export target |
| **Outdated Parts** | ✅ Yes | Parts that have been replaced by newer versions | Can be exported for backup |

[ClickHouse] SHALL handle all special columns and metadata present in parts during export:

| Column Type | Supported | Description | Export Behavior |
|-------------|------------|-------------|-----------------|
| **Physical Columns** | ✅ Yes | User-defined table columns | All physical columns exported |
| **RowExistsColumn (_row_exists)** | ✅ Yes | Lightweight delete mask showing row existence | Exported to maintain delete state |
| **BlockNumberColumn (_block_number)** | ✅ Yes | Original block number from insert | Exported for row identification |
| **BlockOffsetColumn (_block_offset)** | ✅ Yes | Original row offset within block | Exported for row identification |
| **PartDataVersionColumn (_part_data_version)** | ✅ Yes | Data version for mutations | Exported for version tracking |
| **Virtual Columns** | ✅ Yes | Runtime columns like _part, _partition_id | Generated during export |
| **System Metadata** | ✅ Yes | Checksums, compression info, serialization | Preserved in export |

[ClickHouse] SHALL handle all mutation and schema change information present in parts:

| Mutation/Schema Type | Supported | Description | Export Behavior |
|---------------------|------------|-------------|-----------------|
| **Mutation Commands** | ✅ Yes | DELETE, UPDATE, MATERIALIZE_INDEX, DROP_COLUMN, RENAME_COLUMN | Applied during export |
| **Alter Conversions** | ✅ Yes | Column renames, type changes, schema modifications | Applied during export |
| **Patch Parts** | ✅ Yes | Lightweight updates with only changed columns | Applied during export |
| **Mutation Versions** | ✅ Yes | Version tracking for applied mutations | Preserved in export |
| **Schema Changes** | ✅ Yes | ALTER MODIFY, ALTER DROP, ALTER RENAME | Applied during export |
| **TTL Information** | ✅ Yes | Time-to-live settings and expiration data | Preserved in export |
| **Index Information** | ✅ Yes | Primary key, secondary indices, projections | Preserved in export |
| **Statistics** | ✅ Yes | Column statistics and sampling information | Preserved in export |

[ClickHouse] SHALL automatically apply lightweight delete masks during export to ensure only non-deleted rows are exported, and SHALL handle all part metadata including checksums, compression information, serialization details, mutation history, schema changes, and structural modifications to maintain data integrity in the destination storage.

## Export operation failure handling

### RQ.ClickHouse.ExportPart.FailureHandling
version: 1.0

[ClickHouse] SHALL handle export operation failures in the following ways:
* **Stateless Operation**: Export operations are stateless and ephemeral
* **No Recovery**: If an export fails, it fails completely with no retry mechanism
* **No State Persistence**: No export manifests or state are preserved across server restarts
* **Simple Failure**: Export operations either succeed completely or fail with an error message
* **No Partial Exports**: Failed exports leave no partial or corrupted data in destination storage

## Export operation restrictions

### Preventing same table exports

#### RQ.ClickHouse.ExportPart.Restrictions.SameTable
version: 1.0

[ClickHouse] SHALL prevent exporting parts to the same table as the source by:
* Validating that source and destination table identifiers are different
* Throwing a `BAD_ARGUMENTS` exception with message "Exporting to the same table is not allowed" when source and destination are identical
* Performing this validation before any export processing begins

### Destination table compatibility

#### RQ.ClickHouse.ExportPart.Restrictions.DestinationSupport
version: 1.0

[ClickHouse] SHALL validate destination table compatibility by:

* Checking that the destination storage supports importing MergeTree parts
* Verifying that the destination uses Hive partitioning strategy (`partition_strategy = 'hive'`)
* Throwing a `NOT_IMPLEMENTED` exception with message "Destination storage {} does not support MergeTree parts or uses unsupported partitioning" when requirements are not met
* Performing this validation during the initial export setup phase

### Source part availability

#### RQ.ClickHouse.ExportPart.Restrictions.SourcePart
version: 1.0

[ClickHouse] SHALL validate source part availability by:

* Checking that the specified part exists in the source table
* Verifying the part is in an active state (not detached or missing)
* Throwing a `NO_SUCH_DATA_PART` exception with message "No such data part '{}' to export in table '{}'" when the part is not found
* Performing this validation before creating the export manifest

## Export operation concurrency

### RQ.ClickHouse.ExportPart.Concurrency
version: 1.0

[ClickHouse] SHALL support concurrent export operations by:

* Allowing multiple exports to run simultaneously without interference
* Processing export operations asynchronously in the background
* Preventing race conditions and data corruption during concurrent operations
* Supporting concurrent exports of different parts to different destinations
* Preventing concurrent exports of the same part to the same destination
* Maintaining separate progress tracking and state for each concurrent operation
* Ensuring thread safety across all concurrent export operations

## Export operation idempotency

### RQ.ClickHouse.ExportPart.Idempotency
version: 1.0

[ClickHouse] SHALL ensure export operations are idempotent by:

* Allowing the same part to be exported multiple times safely without data corruption
* Supporting file overwrite control through the `export_merge_tree_part_overwrite_file_if_exists` setting
* Generating unique file names using part name and checksum to avoid conflicts
* Maintaining export state consistency across retries

## Export operation error recovery

### Graceful failure handling

#### RQ.ClickHouse.ExportPart.ErrorRecovery.GracefulFailure
version: 1.0

[ClickHouse] SHALL handle export failures gracefully by:
* Allowing users to retry failed export operations
* Maintaining system stability even when exports fail
* Not corrupting source data when export operations fail
* Continuing to process other export operations when one fails

### Automatic cleanup on failure

#### RQ.ClickHouse.ExportPart.ErrorRecovery.AutomaticCleanup
version: 1.0

[ClickHouse] SHALL automatically clean up failed export operations by:
* Removing export manifests from the system when operations fail
* Cleaning up any partial data written to destination storage
* Releasing system resources (memory, file handles) used by failed exports
* Updating export status to reflect the failure state
* Allowing the system to recover and process other export operations

## Export operation logging

### RQ.ClickHouse.ExportPart.Logging
version: 1.0

[ClickHouse] SHALL provide detailed logging for export operations by:
* Logging all export operations (both successful and failed) with timestamps and details
* Recording the specific part name and destination for all operations
* Including execution time and progress information for all operations
* Writing operation information to the `system.part_log` table with the following columns:
  * `event_type` - Set to `EXPORT_PART` for export operations
  * `event_time` - Timestamp when the export operation occurred
  * `table` - Source table name
  * `part_name` - Name of the part being exported
  * `path_on_disk` - Path to the part in source storage
  * `duration_ms` - Execution time in milliseconds
  * `error` - Error message if the export failed (empty for successful exports)
  * `thread_id` - Thread ID performing the export
* Providing sufficient detail for monitoring and troubleshooting export operations

## Monitoring export operations

### RQ.ClickHouse.ExportPart.SystemTables.Exports
version: 1.0

[ClickHouse] SHALL provide a `system.exports` table that allows users to monitor active and completed export operations, track progress metrics, performance statistics, and troubleshoot export issues with the following columns:

* `source_database`, `source_table` - source table identifiers
* `destination_database`, `destination_table` - destination table identifiers  
* `create_time` - when export was submitted
* `part_name` - name of the exported part
* `destination_file_path` - path in destination storage
* `elapsed` - execution time in seconds
* `rows_read`, `total_rows_to_read` - progress metrics
* `total_size_bytes_compressed`, `total_size_bytes_uncompressed` - size metrics
* `bytes_read_uncompressed` - bytes processed
* `memory_usage`, `peak_memory_usage` - memory consumption

## Enabling export functionality

### RQ.ClickHouse.ExportPart.Settings.AllowExperimental
version: 1.0

[ClickHouse] SHALL support the `allow_experimental_export_merge_tree_part` setting that SHALL gate the experimental export part functionality, which SHALL be set to `1` to enable `ALTER TABLE ... EXPORT PART ...` commands. The default value SHALL be `0` (turned off).

## Handling file conflicts during export

### RQ.ClickHouse.ExportPart.Settings.OverwriteFile
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_part_overwrite_file_if_exists` setting that controls whether to overwrite files if they already exist when exporting a merge tree part. The default value SHALL be `0` (turned off).

## Export operation configuration

### RQ.ClickHouse.ExportPart.ParallelFormatting
version: 1.0

[ClickHouse] SHALL support parallel formatting for export operations by:
* Automatically enabling parallel formatting for large export operations to improve performance
* Using the `output_format_parallel_formatting` setting to control parallel formatting behavior
* Optimizing data processing based on export size and system resources
* Providing consistent formatting performance across different export scenarios

## Controlling export performance

### RQ.ClickHouse.ExportPart.ServerSettings.MaxBandwidth
version: 1.0

[ClickHouse] SHALL support the `max_exports_bandwidth_for_server` server setting to limit the maximum read speed of all exports on the server in bytes per second, with `0` meaning unlimited bandwidth. The default value SHALL be `0`. This is a server-level setting configured in the server configuration file.

## Monitoring export performance metrics

### RQ.ClickHouse.ExportPart.Events
version: 1.0

[ClickHouse] SHALL provide the following export-related events in the `system.events` table:
* `PartsExports` - Number of successful part exports
* `PartsExportFailures` - Number of failed part exports  
* `PartsExportDuplicated` - Number of part exports that failed because target already exists
* `PartsExportTotalMilliseconds` - Total time spent on part export operations in milliseconds
* `ExportsThrottlerBytes` - Bytes passed through the exports throttler
* `ExportsThrottlerSleepMicroseconds` - Total time queries were sleeping to conform to export bandwidth throttling

### RQ.ClickHouse.ExportPart.Metrics.Export
version: 1.0

[ClickHouse] SHALL provide the `Export` current metric in `system.metrics` table that tracks the number of currently executing exports.

## Export operation security

### RQ.ClickHouse.ExportPart.Security
version: 1.0

[ClickHouse] SHALL enforce security requirements for export operations:
* **RBAC**: Users must have the following privileges:
  * **Source Table**: `SELECT` privilege on the source table to read data parts
  * **Destination Table**: `INSERT` privilege on the destination table to write exported data
  * **Database Access**: `SHOW` privilege on both source and destination databases
  * **System Tables**: `SELECT` privilege on `system.tables` to validate table existence
* **Data Encryption**: All data in transit to destination storage must be encrypted using TLS/SSL
* **Network Security**: Export operations must use secure connections to destination storage (HTTPS for S3, secure protocols for other storage)
* **Credential Management**: Export operations must use secure credential storage and avoid exposing credentials in logs


[ClickHouse]: https://clickhouse.com
""",
)
