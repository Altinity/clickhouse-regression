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

RQ_ClickHouse_ExportPart_EmptyTable = Requirement(
    name="RQ.ClickHouse.ExportPart.EmptyTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting from empty tables by:\n"
        "* Completing export operations successfully when the source table contains no parts\n"
        "* Resulting in an empty destination table when exporting from an empty source table\n"
        "* Not creating any files in destination storage when there are no parts to export\n"
        "* Handling empty tables gracefully without errors\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.2",
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
        "* `source_table_name`: Name of the source MergeTree table\n"
        "* `part_name`: Name of the specific part to export (string literal)\n"
        "* `destination_table_name`: Name of the destination object storage table\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.3",
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
        "* `ReplacingMergeTree` - MergeTree with automatic deduplication\n"
        "* All other MergeTree family engines that inherit from `MergeTreeData`\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.1",
)

RQ_ClickHouse_ExportPart_StoragePolicies = Requirement(
    name="RQ.ClickHouse.ExportPart.StoragePolicies",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting parts from tables using different storage policies, where storage policies are composed of volumes which are composed of disks, including:\n"
        "* **JBOD Volumes**: Just a Bunch Of Disks volumes with multiple disks\n"
        "* **External Volumes**: Volumes using external storage systems\n"
        "* **Tiered Storage Policies**: Storage policies with multiple volumes for hot/cold data tiers\n"
        "* **Encrypted Disks**: Parts stored on encrypted disks (disk-level encryption)\n"
        "* **Cached Disks**: Parts stored with filesystem cache enabled\n"
        "* **Custom Storage Policies**: Any storage policy configuration composed of volumes and disks\n"
        "* Exporting parts regardless of which volume or disk within the storage policy contains the part\n"
        "* Maintaining data integrity when exporting from parts stored on any volume or disk in the storage policy\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.2",
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
    num="4.1",
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
    num="4.2",
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
        "\n"
        "[ClickHouse] SHALL automatically apply lightweight delete masks during export to ensure only non-deleted rows are exported, and SHALL handle all part metadata including checksums, compression information, serialization details, mutation history, schema changes, and structural modifications to maintain data integrity in the destination storage.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.1",
)

RQ_ClickHouse_ExportPart_SchemaChangeIsolation = Requirement(
    name="RQ.ClickHouse.ExportPart.SchemaChangeIsolation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL ensure exported data is isolated from subsequent schema changes by:\n"
        "* Preserving exported data exactly as it was at the time of export\n"
        "* Not being affected by schema changes (column drops, renames, type changes) that occur after export\n"
        "* Maintaining data integrity in destination storage regardless of mutations applied to the source table after export\n"
        "* Ensuring exported data reflects the source table state at the time of export, not the current state\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.2",
)

RQ_ClickHouse_ExportPart_LargeParts = Requirement(
    name="RQ.ClickHouse.ExportPart.LargeParts",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting large parts by:\n"
        "* Handling parts with large numbers of rows (e.g., 100 million or more)\n"
        "* Processing large data volumes efficiently during export\n"
        "* Maintaining data integrity when exporting large parts\n"
        "* Completing export operations successfully regardless of part size\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.3",
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
        '* Throwing a `BAD_ARGUMENTS` exception (error code 36) with message "Exporting to the same table is not allowed" when source and destination are identical\n'
        "* Performing this validation before any export processing begins\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.1",
)

RQ_ClickHouse_ExportPart_Restrictions_LocalTable = Requirement(
    name="RQ.ClickHouse.ExportPart.Restrictions.LocalTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL prevent exporting parts to local MergeTree tables by:\n"
        "* Rejecting export operations where the destination table uses a MergeTree engine\n"
        '* Throwing a `NOT_IMPLEMENTED` exception (error code 48) with message "Destination storage MergeTree does not support MergeTree parts or uses unsupported partitioning" when attempting to export to a local table\n'
        "* Performing this validation during the initial export setup phase\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.2",
)

RQ_ClickHouse_ExportPart_Restrictions_PartitionKey = Requirement(
    name="RQ.ClickHouse.ExportPart.Restrictions.PartitionKey",
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
    ),
    link=None,
    level=2,
    num="6.3",
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
        "* Checking that the specified part exists in the source table\n"
        "* Verifying the part name format is valid\n"
        '* Throwing a `BAD_DATA_PART_NAME` exception (error code 233) with message containing "Unexpected part name" when the part name is invalid\n'
        "* Performing this validation before creating the export manifest\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.4",
)

RQ_ClickHouse_ExportPart_Restrictions_RemovedPart = Requirement(
    name="RQ.ClickHouse.ExportPart.Restrictions.RemovedPart",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL handle attempts to export parts that have been removed from the source table by:\n"
        "* Detecting when a part has been detached or dropped before export completes\n"
        "* Throwing a `NO_SUCH_DATA_PART` exception (error code 232) when attempting to export a removed part\n"
        "* Handling both detached parts and dropped parts/partitions correctly\n"
        "* Performing this validation during export execution\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.5",
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
        "* **Error Logging**: Failed exports are logged in `system.part_log` with error status\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.1",
)

RQ_ClickHouse_ExportPart_FailureHandling_PartCorruption = Requirement(
    name="RQ.ClickHouse.ExportPart.FailureHandling.PartCorruption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL handle corrupted source parts during export by:\n"
        "* Detecting corruption when reading part data during export\n"
        "* Failing the export operation with an appropriate error code\n"
        "* Logging the failure in `system.part_log` with error status\n"
        "* Not exporting corrupted parts to destination storage\n"
        "* Allowing non-corrupted parts to export successfully even when other parts are corrupted\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.2",
)

RQ_ClickHouse_ExportPart_NetworkResilience_PacketIssues = Requirement(
    name="RQ.ClickHouse.ExportPart.NetworkResilience.PacketIssues",
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
    ),
    link=None,
    level=2,
    num="8.1",
)

RQ_ClickHouse_ExportPart_NetworkResilience_DestinationInterruption = Requirement(
    name="RQ.ClickHouse.ExportPart.NetworkResilience.DestinationInterruption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL handle destination storage interruptions during export operations by:\n"
        "* Detecting when destination storage becomes unavailable during export\n"
        "* Failing export operations gracefully when destination storage is unavailable\n"
        "* Logging failed exports in the `system.events` table with `PartsExportFailures` counter\n"
        "* Not leaving partial or corrupted data in destination storage when exports fail due to destination unavailability\n"
        "* Allowing exports to complete successfully once destination storage becomes available again\n"
        "* Handling interruptions at different stages: before export starts, during export, after export completes\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.2",
)

RQ_ClickHouse_ExportPart_NetworkResilience_NodeInterruption = Requirement(
    name="RQ.ClickHouse.ExportPart.NetworkResilience.NodeInterruption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL handle ClickHouse node interruptions during export operations by:\n"
        "* Handling node restarts gracefully during export operations\n"
        "* Not leaving partial or corrupted data in destination storage when node restarts occur\n"
        "* With safe shutdown, ensuring exports complete successfully before node shutdown\n"
        "* With unsafe shutdown, allowing partial exports to complete successfully after node restart\n"
        "* Maintaining data integrity in destination storage regardless of node interruption type\n"
        "* Handling interruptions at different stages: before export starts, during export, after export completes\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.3",
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
        "* Allowing multiple exports to run simultaneously without interference\n"
        "* Processing export operations asynchronously in the background\n"
        "* Preventing race conditions and data corruption during concurrent operations\n"
        "* Supporting concurrent exports of different parts to different destinations\n"
        "* Supporting concurrent exports from multiple source tables to the same destination\n"
        "* Preventing concurrent exports of the same part to the same destination\n"
        "* Maintaining separate progress tracking and state for each concurrent operation\n"
        "* Ensuring thread safety across all concurrent export operations\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.1",
)

RQ_ClickHouse_ExportPart_Concurrency_NonBlocking = Requirement(
    name="RQ.ClickHouse.ExportPart.Concurrency.NonBlocking",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL ensure that export operations do not block other operations on the source table by:\n"
        "* Allowing SELECT queries to execute concurrently with exports without blocking\n"
        "* Allowing INSERT operations to execute concurrently with exports without blocking\n"
        "* Allowing MERGE operations to execute concurrently with exports without blocking\n"
        "* Ensuring that reads and writes to the source table are not blocked by active export operations\n"
        "* Maintaining data consistency for concurrent operations\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.2",
)

RQ_ClickHouse_ExportPart_Concurrency_ConcurrentAlters = Requirement(
    name="RQ.ClickHouse.ExportPart.Concurrency.ConcurrentAlters",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support concurrent ALTER operations on the source table during export by:\n"
        "* Allowing ALTER operations to execute concurrently with exports\n"
        "* Ensuring exported data reflects the source table state at the time export was initiated\n"
        "* Supporting ALTER operations before export (export uses post-ALTER schema)\n"
        "* Supporting ALTER operations after export (exported data unaffected)\n"
        "* Supporting ALTER operations during export (export uses pre-ALTER schema snapshot)\n"
        "* Maintaining data integrity when ALTER operations occur concurrently with exports\n"
        "* Handling various ALTER operations: add/drop columns, modify columns, rename columns, add/drop constraints, TTL modifications, partition operations, mutations, etc.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.3",
)

RQ_ClickHouse_ExportPart_ClustersNodes = Requirement(
    name="RQ.ClickHouse.ExportPart.ClustersNodes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting parts from multiple nodes in a cluster to the same destination storage, ensuring that:\n"
        "* Each node can independently export parts from its local storage to the shared destination\n"
        "* Exported data from different nodes is correctly aggregated in the destination\n"
        "* All nodes in the cluster can read the same exported data from the destination\n"
        "* Supporting various cluster configurations: sharded, replicated, one-shard clusters\n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.1",
)

RQ_ClickHouse_ExportPart_Idempotency = Requirement(
    name="RQ.ClickHouse.ExportPart.Idempotency",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL handle duplicate export operations by:\n"
        "* Detecting when an export operation attempts to export a part that already exists in the destination\n"
        "* Supporting configurable policies for handling file conflicts: `skip`, `error`, `overwrite`\n"
        "* With `skip` policy: Logging duplicate attempts in `system.events` with `PartsExportDuplicated` counter, not incrementing `PartsExportFailures`, treating as success\n"
        "* With `error` policy: Logging duplicate attempts in `system.events` with both `PartsExportDuplicated` and `PartsExportFailures` counters, failing the export\n"
        "* With `overwrite` policy: Overwriting existing files, logging as successful export, not incrementing duplicate or failure counters\n"
        "* Ensuring that destination data matches source data without duplication when the same part is exported multiple times with `skip` policy\n"
        "* Logging duplicate export attempts in the `system.events` table with the `PartsExportDuplicated` counter\n"
        "\n"
    ),
    link=None,
    level=2,
    num="11.1",
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
        "* Recording the specific part name in the `system.part_log` table for all operations\n"
        "* Logging export events in the `system.events` table, including:\n"
        "  * `PartsExports` - Number of successful part exports\n"
        "  * `PartsExportFailures` - Number of failed part exports\n"
        "  * `PartsExportDuplicated` - Number of part exports that detected existing files\n"
        "  * `PartsExportTotalMilliseconds` - Total time spent exporting\n"
        "* Writing operation information to the `system.part_log` table with `event_type` set to `EXPORT_PART`\n"
        "* Logging failed exports with error status and error details in `system.part_log`\n"
        "* Providing sufficient detail for monitoring and troubleshooting export operations\n"
        "\n"
    ),
    link=None,
    level=2,
    num="12.1",
)

RQ_ClickHouse_ExportPart_SystemTables_Exports = Requirement(
    name="RQ.ClickHouse.ExportPart.SystemTables.Exports",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide a `system.exports` table that allows users to monitor active export operations with at least the following columns:\n"
        "* `source_table` - source table identifier\n"
        "* `destination_table` - destination table identifier\n"
        "* `part_name` - name of the part being exported\n"
        "* Additional metadata about the export operation\n"
        "\n"
        "The table SHALL track export operations before they complete and SHALL be empty after all exports complete.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.1",
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
    num="13.2",
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
        '[ClickHouse] SHALL reject export operations when this setting is disabled, throwing an exception (error code 88) with message "Exporting merge tree part is experimental".\n'
        "\n"
    ),
    link=None,
    level=2,
    num="14.1",
)

RQ_ClickHouse_ExportPart_Settings_FileAlreadyExistsPolicy = Requirement(
    name="RQ.ClickHouse.ExportPart.Settings.FileAlreadyExistsPolicy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `export_merge_tree_part_file_already_exists_policy` setting that controls behavior when exporting a part that already exists in the destination. The setting SHALL accept the following values:\n"
        "* `skip` (default) - Skip the export if file already exists, log as duplicate, treat as success\n"
        "* `error` - Fail the export if file already exists, log as duplicate and failure\n"
        "* `overwrite` - Overwrite existing file, proceed with export\n"
        "\n"
    ),
    link=None,
    level=2,
    num="14.2",
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
    num="14.3",
)

RQ_ClickHouse_ExportPart_ServerSettings_BackgroundMovePoolSize = Requirement(
    name="RQ.ClickHouse.ExportPart.ServerSettings.BackgroundMovePoolSize",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `background_move_pool_size` server setting to control the maximum number of threads that will be used for executing export operations in the background. The default value SHALL be `8`. This is a server-level setting configured in the server configuration file.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="14.4",
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
        "  * **Source Table**: `ALTER` privilege on the source table to initiate export operations\n"
        "  * **Destination Table**: `INSERT` privilege on the destination table to write exported data\n"
        "  * **Query Management**: `KILL QUERY` privilege to terminate export operations, allowing users to kill their own export queries and administrators to kill any export query\n"
        "* **Data Encryption**: All data in transit to destination storage must be encrypted using TLS/SSL\n"
        "* **Network Security**: Export operations must use secure connections to destination storage (HTTPS for S3, secure protocols for other storage)\n"
        "* **Credential Management**: Export operations must use secure credential storage and avoid exposing credentials in logs\n"
        "\n"
        "\n"
        "[ClickHouse]: https://clickhouse.com\n"
    ),
    link=None,
    level=2,
    num="15.1",
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
        Heading(name="Basic Export Functionality", level=1, num="2"),
        Heading(name="RQ.ClickHouse.ExportPart.S3", level=2, num="2.1"),
        Heading(name="RQ.ClickHouse.ExportPart.EmptyTable", level=2, num="2.2"),
        Heading(name="RQ.ClickHouse.ExportPart.SQLCommand", level=2, num="2.3"),
        Heading(name="Source Table Support", level=1, num="3"),
        Heading(name="RQ.ClickHouse.ExportPart.SourceEngines", level=2, num="3.1"),
        Heading(name="RQ.ClickHouse.ExportPart.StoragePolicies", level=2, num="3.2"),
        Heading(name="Schema and Partition Compatibility", level=1, num="4"),
        Heading(
            name="RQ.ClickHouse.ExportPart.SchemaCompatibility", level=2, num="4.1"
        ),
        Heading(name="RQ.ClickHouse.ExportPart.PartitionKeyTypes", level=2, num="4.2"),
        Heading(name="Part Types and Content", level=1, num="5"),
        Heading(name="RQ.ClickHouse.ExportPart.PartTypes", level=2, num="5.1"),
        Heading(
            name="RQ.ClickHouse.ExportPart.SchemaChangeIsolation", level=2, num="5.2"
        ),
        Heading(name="RQ.ClickHouse.ExportPart.LargeParts", level=2, num="5.3"),
        Heading(name="Export Operation Restrictions", level=1, num="6"),
        Heading(
            name="RQ.ClickHouse.ExportPart.Restrictions.SameTable", level=2, num="6.1"
        ),
        Heading(
            name="RQ.ClickHouse.ExportPart.Restrictions.LocalTable", level=2, num="6.2"
        ),
        Heading(
            name="RQ.ClickHouse.ExportPart.Restrictions.PartitionKey",
            level=2,
            num="6.3",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPart.Restrictions.SourcePart", level=2, num="6.4"
        ),
        Heading(
            name="RQ.ClickHouse.ExportPart.Restrictions.RemovedPart", level=2, num="6.5"
        ),
        Heading(name="Export Operation Failure Handling", level=1, num="7"),
        Heading(name="RQ.ClickHouse.ExportPart.FailureHandling", level=2, num="7.1"),
        Heading(
            name="RQ.ClickHouse.ExportPart.FailureHandling.PartCorruption",
            level=2,
            num="7.2",
        ),
        Heading(name="Network Resilience", level=1, num="8"),
        Heading(
            name="RQ.ClickHouse.ExportPart.NetworkResilience.PacketIssues",
            level=2,
            num="8.1",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPart.NetworkResilience.DestinationInterruption",
            level=2,
            num="8.2",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPart.NetworkResilience.NodeInterruption",
            level=2,
            num="8.3",
        ),
        Heading(name="Export Operation Concurrency", level=1, num="9"),
        Heading(name="RQ.ClickHouse.ExportPart.Concurrency", level=2, num="9.1"),
        Heading(
            name="RQ.ClickHouse.ExportPart.Concurrency.NonBlocking", level=2, num="9.2"
        ),
        Heading(
            name="RQ.ClickHouse.ExportPart.Concurrency.ConcurrentAlters",
            level=2,
            num="9.3",
        ),
        Heading(name="Cluster and Node Support", level=1, num="10"),
        Heading(name="RQ.ClickHouse.ExportPart.ClustersNodes", level=2, num="10.1"),
        Heading(name="Export Operation Idempotency", level=1, num="11"),
        Heading(name="RQ.ClickHouse.ExportPart.Idempotency", level=2, num="11.1"),
        Heading(name="Export Operation Logging", level=1, num="12"),
        Heading(name="RQ.ClickHouse.ExportPart.Logging", level=2, num="12.1"),
        Heading(name="Monitoring Export Operations", level=1, num="13"),
        Heading(
            name="RQ.ClickHouse.ExportPart.SystemTables.Exports", level=2, num="13.1"
        ),
        Heading(name="RQ.ClickHouse.ExportPart.Metrics.Export", level=2, num="13.2"),
        Heading(name="Settings and Configuration", level=1, num="14"),
        Heading(
            name="RQ.ClickHouse.ExportPart.Settings.AllowExperimental",
            level=2,
            num="14.1",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPart.Settings.FileAlreadyExistsPolicy",
            level=2,
            num="14.2",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPart.ServerSettings.MaxBandwidth",
            level=2,
            num="14.3",
        ),
        Heading(
            name="RQ.ClickHouse.ExportPart.ServerSettings.BackgroundMovePoolSize",
            level=2,
            num="14.4",
        ),
        Heading(name="Export Operation Security", level=1, num="15"),
        Heading(name="RQ.ClickHouse.ExportPart.Security", level=2, num="15.1"),
    ),
    requirements=(
        RQ_ClickHouse_ExportPart_S3,
        RQ_ClickHouse_ExportPart_EmptyTable,
        RQ_ClickHouse_ExportPart_SQLCommand,
        RQ_ClickHouse_ExportPart_SourceEngines,
        RQ_ClickHouse_ExportPart_StoragePolicies,
        RQ_ClickHouse_ExportPart_SchemaCompatibility,
        RQ_ClickHouse_ExportPart_PartitionKeyTypes,
        RQ_ClickHouse_ExportPart_PartTypes,
        RQ_ClickHouse_ExportPart_SchemaChangeIsolation,
        RQ_ClickHouse_ExportPart_LargeParts,
        RQ_ClickHouse_ExportPart_Restrictions_SameTable,
        RQ_ClickHouse_ExportPart_Restrictions_LocalTable,
        RQ_ClickHouse_ExportPart_Restrictions_PartitionKey,
        RQ_ClickHouse_ExportPart_Restrictions_SourcePart,
        RQ_ClickHouse_ExportPart_Restrictions_RemovedPart,
        RQ_ClickHouse_ExportPart_FailureHandling,
        RQ_ClickHouse_ExportPart_FailureHandling_PartCorruption,
        RQ_ClickHouse_ExportPart_NetworkResilience_PacketIssues,
        RQ_ClickHouse_ExportPart_NetworkResilience_DestinationInterruption,
        RQ_ClickHouse_ExportPart_NetworkResilience_NodeInterruption,
        RQ_ClickHouse_ExportPart_Concurrency,
        RQ_ClickHouse_ExportPart_Concurrency_NonBlocking,
        RQ_ClickHouse_ExportPart_Concurrency_ConcurrentAlters,
        RQ_ClickHouse_ExportPart_ClustersNodes,
        RQ_ClickHouse_ExportPart_Idempotency,
        RQ_ClickHouse_ExportPart_Logging,
        RQ_ClickHouse_ExportPart_SystemTables_Exports,
        RQ_ClickHouse_ExportPart_Metrics_Export,
        RQ_ClickHouse_ExportPart_Settings_AllowExperimental,
        RQ_ClickHouse_ExportPart_Settings_FileAlreadyExistsPolicy,
        RQ_ClickHouse_ExportPart_ServerSettings_MaxBandwidth,
        RQ_ClickHouse_ExportPart_ServerSettings_BackgroundMovePoolSize,
        RQ_ClickHouse_ExportPart_Security,
    ),
    content=r"""
# SRS-015 ClickHouse Export Part to S3
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Basic Export Functionality](#basic-export-functionality)
    * 2.1 [RQ.ClickHouse.ExportPart.S3](#rqclickhouseexportparts3)
    * 2.2 [RQ.ClickHouse.ExportPart.EmptyTable](#rqclickhouseexportpartemptytable)
    * 2.3 [RQ.ClickHouse.ExportPart.SQLCommand](#rqclickhouseexportpartsqlcommand)
* 3 [Source Table Support](#source-table-support)
    * 3.1 [RQ.ClickHouse.ExportPart.SourceEngines](#rqclickhouseexportpartsourceengines)
    * 3.2 [RQ.ClickHouse.ExportPart.StoragePolicies](#rqclickhouseexportpartstoragepolicies)
* 4 [Schema and Partition Compatibility](#schema-and-partition-compatibility)
    * 4.1 [RQ.ClickHouse.ExportPart.SchemaCompatibility](#rqclickhouseexportpartschemacompatibility)
    * 4.2 [RQ.ClickHouse.ExportPart.PartitionKeyTypes](#rqclickhouseexportpartpartitionkeytypes)
* 5 [Part Types and Content](#part-types-and-content)
    * 5.1 [RQ.ClickHouse.ExportPart.PartTypes](#rqclickhouseexportpartparttypes)
    * 5.2 [RQ.ClickHouse.ExportPart.SchemaChangeIsolation](#rqclickhouseexportpartschemachangeisolation)
    * 5.3 [RQ.ClickHouse.ExportPart.LargeParts](#rqclickhouseexportpartlargeparts)
* 6 [Export Operation Restrictions](#export-operation-restrictions)
    * 6.1 [RQ.ClickHouse.ExportPart.Restrictions.SameTable](#rqclickhouseexportpartrestrictionssametable)
    * 6.2 [RQ.ClickHouse.ExportPart.Restrictions.LocalTable](#rqclickhouseexportpartrestrictionslocaltable)
    * 6.3 [RQ.ClickHouse.ExportPart.Restrictions.PartitionKey](#rqclickhouseexportpartrestrictionspartitionkey)
    * 6.4 [RQ.ClickHouse.ExportPart.Restrictions.SourcePart](#rqclickhouseexportpartrestrictionssourcepart)
    * 6.5 [RQ.ClickHouse.ExportPart.Restrictions.RemovedPart](#rqclickhouseexportpartrestrictionsremovedpart)
* 7 [Export Operation Failure Handling](#export-operation-failure-handling)
    * 7.1 [RQ.ClickHouse.ExportPart.FailureHandling](#rqclickhouseexportpartfailurehandling)
    * 7.2 [RQ.ClickHouse.ExportPart.FailureHandling.PartCorruption](#rqclickhouseexportpartfailurehandlingpartcorruption)
* 8 [Network Resilience](#network-resilience)
    * 8.1 [RQ.ClickHouse.ExportPart.NetworkResilience.PacketIssues](#rqclickhouseexportpartnetworkresiliencepacketissues)
    * 8.2 [RQ.ClickHouse.ExportPart.NetworkResilience.DestinationInterruption](#rqclickhouseexportpartnetworkresiliencedestinationinterruption)
    * 8.3 [RQ.ClickHouse.ExportPart.NetworkResilience.NodeInterruption](#rqclickhouseexportpartnetworkresiliencenodeinterruption)
* 9 [Export Operation Concurrency](#export-operation-concurrency)
    * 9.1 [RQ.ClickHouse.ExportPart.Concurrency](#rqclickhouseexportpartconcurrency)
    * 9.2 [RQ.ClickHouse.ExportPart.Concurrency.NonBlocking](#rqclickhouseexportpartconcurrencynonblocking)
    * 9.3 [RQ.ClickHouse.ExportPart.Concurrency.ConcurrentAlters](#rqclickhouseexportpartconcurrencyconcurrentalters)
* 10 [Cluster and Node Support](#cluster-and-node-support)
    * 10.1 [RQ.ClickHouse.ExportPart.ClustersNodes](#rqclickhouseexportpartclustersnodes)
* 11 [Export Operation Idempotency](#export-operation-idempotency)
    * 11.1 [RQ.ClickHouse.ExportPart.Idempotency](#rqclickhouseexportpartidempotency)
* 12 [Export Operation Logging](#export-operation-logging)
    * 12.1 [RQ.ClickHouse.ExportPart.Logging](#rqclickhouseexportpartlogging)
* 13 [Monitoring Export Operations](#monitoring-export-operations)
    * 13.1 [RQ.ClickHouse.ExportPart.SystemTables.Exports](#rqclickhouseexportpartsystemtablesexports)
    * 13.2 [RQ.ClickHouse.ExportPart.Metrics.Export](#rqclickhouseexportpartmetricsexport)
* 14 [Settings and Configuration](#settings-and-configuration)
    * 14.1 [RQ.ClickHouse.ExportPart.Settings.AllowExperimental](#rqclickhouseexportpartsettingsallowexperimental)
    * 14.2 [RQ.ClickHouse.ExportPart.Settings.FileAlreadyExistsPolicy](#rqclickhouseexportpartsettingsfilealreadyexistspolicy)
    * 14.3 [RQ.ClickHouse.ExportPart.ServerSettings.MaxBandwidth](#rqclickhouseexportpartserversettingsmaxbandwidth)
    * 14.4 [RQ.ClickHouse.ExportPart.ServerSettings.BackgroundMovePoolSize](#rqclickhouseexportpartserversettingsbackgroundmovepoolsize)
* 15 [Export Operation Security](#export-operation-security)
    * 15.1 [RQ.ClickHouse.ExportPart.Security](#rqclickhouseexportpartsecurity)

## Introduction

This specification defines requirements for exporting individual MergeTree data parts to S3-compatible object storage.

## Basic Export Functionality

### RQ.ClickHouse.ExportPart.S3
version: 1.0

[ClickHouse] SHALL support exporting data parts from MergeTree engine tables to S3 object storage.

### RQ.ClickHouse.ExportPart.EmptyTable
version: 1.0

[ClickHouse] SHALL support exporting from empty tables by:
* Completing export operations successfully when the source table contains no parts
* Resulting in an empty destination table when exporting from an empty source table
* Not creating any files in destination storage when there are no parts to export
* Handling empty tables gracefully without errors

### RQ.ClickHouse.ExportPart.SQLCommand
version: 1.0

[ClickHouse] SHALL support the following SQL command syntax for exporting MergeTree data parts to object storage tables:

```sql
ALTER TABLE [database.]source_table_name 
EXPORT PART 'part_name' 
TO TABLE [database.]destination_table_name
```

**Parameters:**
* `source_table_name`: Name of the source MergeTree table
* `part_name`: Name of the specific part to export (string literal)
* `destination_table_name`: Name of the destination object storage table

## Source Table Support

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
* `ReplacingMergeTree` - MergeTree with automatic deduplication
* All other MergeTree family engines that inherit from `MergeTreeData`

### RQ.ClickHouse.ExportPart.StoragePolicies
version: 1.0

[ClickHouse] SHALL support exporting parts from tables using different storage policies, where storage policies are composed of volumes which are composed of disks, including:
* **JBOD Volumes**: Just a Bunch Of Disks volumes with multiple disks
* **External Volumes**: Volumes using external storage systems
* **Tiered Storage Policies**: Storage policies with multiple volumes for hot/cold data tiers
* **Encrypted Disks**: Parts stored on encrypted disks (disk-level encryption)
* **Cached Disks**: Parts stored with filesystem cache enabled
* **Custom Storage Policies**: Any storage policy configuration composed of volumes and disks
* Exporting parts regardless of which volume or disk within the storage policy contains the part
* Maintaining data integrity when exporting from parts stored on any volume or disk in the storage policy

## Schema and Partition Compatibility

### RQ.ClickHouse.ExportPart.SchemaCompatibility
version: 1.0

[ClickHouse] SHALL require source and destination tables to have compatible schemas for successful export operations:
* Identical physical column schemas between source and destination
* The same partition key expression in both tables
* Compatible data types for all columns
* Matching column order and names

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

## Part Types and Content

### RQ.ClickHouse.ExportPart.PartTypes
version: 1.0

[ClickHouse] SHALL support export operations for all valid MergeTree part types and their contents, including:

| Part Type | Supported | Description | Special Features |
|-----------|------------|-------------|------------------|
| **Wide Parts** | ✅ Yes | Data of each column stored in separate files with marks | Standard format for most parts |
| **Compact Parts** | ✅ Yes | All column data stored in single file with single marks file | Optimized for small parts |

[ClickHouse] SHALL automatically apply lightweight delete masks during export to ensure only non-deleted rows are exported, and SHALL handle all part metadata including checksums, compression information, serialization details, mutation history, schema changes, and structural modifications to maintain data integrity in the destination storage.

### RQ.ClickHouse.ExportPart.SchemaChangeIsolation
version: 1.0

[ClickHouse] SHALL ensure exported data is isolated from subsequent schema changes by:
* Preserving exported data exactly as it was at the time of export
* Not being affected by schema changes (column drops, renames, type changes) that occur after export
* Maintaining data integrity in destination storage regardless of mutations applied to the source table after export
* Ensuring exported data reflects the source table state at the time of export, not the current state

### RQ.ClickHouse.ExportPart.LargeParts
version: 1.0

[ClickHouse] SHALL support exporting large parts by:
* Handling parts with large numbers of rows (e.g., 100 million or more)
* Processing large data volumes efficiently during export
* Maintaining data integrity when exporting large parts
* Completing export operations successfully regardless of part size

## Export Operation Restrictions

### RQ.ClickHouse.ExportPart.Restrictions.SameTable
version: 1.0

[ClickHouse] SHALL prevent exporting parts to the same table as the source by:
* Validating that source and destination table identifiers are different
* Throwing a `BAD_ARGUMENTS` exception (error code 36) with message "Exporting to the same table is not allowed" when source and destination are identical
* Performing this validation before any export processing begins

### RQ.ClickHouse.ExportPart.Restrictions.LocalTable
version: 1.0

[ClickHouse] SHALL prevent exporting parts to local MergeTree tables by:
* Rejecting export operations where the destination table uses a MergeTree engine
* Throwing a `NOT_IMPLEMENTED` exception (error code 48) with message "Destination storage MergeTree does not support MergeTree parts or uses unsupported partitioning" when attempting to export to a local table
* Performing this validation during the initial export setup phase

### RQ.ClickHouse.ExportPart.Restrictions.PartitionKey
version: 1.0

[ClickHouse] SHALL validate that source and destination tables have the same partition key expression by:
* Checking that the partition key expression matches between source and destination tables
* Throwing a `BAD_ARGUMENTS` exception (error code 36) with message "Tables have different partition key" when partition keys differ
* Performing this validation during the initial export setup phase

### RQ.ClickHouse.ExportPart.Restrictions.SourcePart
version: 1.0

[ClickHouse] SHALL validate source part availability by:
* Checking that the specified part exists in the source table
* Verifying the part name format is valid
* Throwing a `BAD_DATA_PART_NAME` exception (error code 233) with message containing "Unexpected part name" when the part name is invalid
* Performing this validation before creating the export manifest

### RQ.ClickHouse.ExportPart.Restrictions.RemovedPart
version: 1.0

[ClickHouse] SHALL handle attempts to export parts that have been removed from the source table by:
* Detecting when a part has been detached or dropped before export completes
* Throwing a `NO_SUCH_DATA_PART` exception (error code 232) when attempting to export a removed part
* Handling both detached parts and dropped parts/partitions correctly
* Performing this validation during export execution

## Export Operation Failure Handling

### RQ.ClickHouse.ExportPart.FailureHandling
version: 1.0

[ClickHouse] SHALL handle export operation failures in the following ways:
* **Stateless Operation**: Export operations are stateless and ephemeral
* **No Recovery**: If an export fails, it fails completely with no retry mechanism
* **No State Persistence**: No export manifests or state are preserved across server restarts
* **Simple Failure**: Export operations either succeed completely or fail with an error message
* **No Partial Exports**: Failed exports leave no partial or corrupted data in destination storage
* **Error Logging**: Failed exports are logged in `system.part_log` with error status

### RQ.ClickHouse.ExportPart.FailureHandling.PartCorruption
version: 1.0

[ClickHouse] SHALL handle corrupted source parts during export by:
* Detecting corruption when reading part data during export
* Failing the export operation with an appropriate error code
* Logging the failure in `system.part_log` with error status
* Not exporting corrupted parts to destination storage
* Allowing non-corrupted parts to export successfully even when other parts are corrupted

## Network Resilience

### RQ.ClickHouse.ExportPart.NetworkResilience.PacketIssues
version: 1.0

[ClickHouse] SHALL handle network packet issues during export operations by:
* Tolerating packet delay without data corruption or loss
* Handling packet loss and retransmitting data as needed
* Detecting and handling packet corruption to ensure data integrity
* Managing packet duplication without data duplication in destination
* Handling packet reordering to maintain correct data sequence
* Operating correctly under packet rate limiting constraints
* Completing exports successfully despite network impairments

### RQ.ClickHouse.ExportPart.NetworkResilience.DestinationInterruption
version: 1.0

[ClickHouse] SHALL handle destination storage interruptions during export operations by:
* Detecting when destination storage becomes unavailable during export
* Failing export operations gracefully when destination storage is unavailable
* Logging failed exports in the `system.events` table with `PartsExportFailures` counter
* Not leaving partial or corrupted data in destination storage when exports fail due to destination unavailability
* Allowing exports to complete successfully once destination storage becomes available again
* Handling interruptions at different stages: before export starts, during export, after export completes

### RQ.ClickHouse.ExportPart.NetworkResilience.NodeInterruption
version: 1.0

[ClickHouse] SHALL handle ClickHouse node interruptions during export operations by:
* Handling node restarts gracefully during export operations
* Not leaving partial or corrupted data in destination storage when node restarts occur
* With safe shutdown, ensuring exports complete successfully before node shutdown
* With unsafe shutdown, allowing partial exports to complete successfully after node restart
* Maintaining data integrity in destination storage regardless of node interruption type
* Handling interruptions at different stages: before export starts, during export, after export completes

## Export Operation Concurrency

### RQ.ClickHouse.ExportPart.Concurrency
version: 1.0

[ClickHouse] SHALL support concurrent export operations by:
* Allowing multiple exports to run simultaneously without interference
* Processing export operations asynchronously in the background
* Preventing race conditions and data corruption during concurrent operations
* Supporting concurrent exports of different parts to different destinations
* Supporting concurrent exports from multiple source tables to the same destination
* Preventing concurrent exports of the same part to the same destination
* Maintaining separate progress tracking and state for each concurrent operation
* Ensuring thread safety across all concurrent export operations

### RQ.ClickHouse.ExportPart.Concurrency.NonBlocking
version: 1.0

[ClickHouse] SHALL ensure that export operations do not block other operations on the source table by:
* Allowing SELECT queries to execute concurrently with exports without blocking
* Allowing INSERT operations to execute concurrently with exports without blocking
* Allowing MERGE operations to execute concurrently with exports without blocking
* Ensuring that reads and writes to the source table are not blocked by active export operations
* Maintaining data consistency for concurrent operations

### RQ.ClickHouse.ExportPart.Concurrency.ConcurrentAlters
version: 1.0

[ClickHouse] SHALL support concurrent ALTER operations on the source table during export by:
* Allowing ALTER operations to execute concurrently with exports
* Ensuring exported data reflects the source table state at the time export was initiated
* Supporting ALTER operations before export (export uses post-ALTER schema)
* Supporting ALTER operations after export (exported data unaffected)
* Supporting ALTER operations during export (export uses pre-ALTER schema snapshot)
* Maintaining data integrity when ALTER operations occur concurrently with exports
* Handling various ALTER operations: add/drop columns, modify columns, rename columns, add/drop constraints, TTL modifications, partition operations, mutations, etc.

## Cluster and Node Support

### RQ.ClickHouse.ExportPart.ClustersNodes
version: 1.0

[ClickHouse] SHALL support exporting parts from multiple nodes in a cluster to the same destination storage, ensuring that:
* Each node can independently export parts from its local storage to the shared destination
* Exported data from different nodes is correctly aggregated in the destination
* All nodes in the cluster can read the same exported data from the destination
* Supporting various cluster configurations: sharded, replicated, one-shard clusters

## Export Operation Idempotency

### RQ.ClickHouse.ExportPart.Idempotency
version: 1.0

[ClickHouse] SHALL handle duplicate export operations by:
* Detecting when an export operation attempts to export a part that already exists in the destination
* Supporting configurable policies for handling file conflicts: `skip`, `error`, `overwrite`
* With `skip` policy: Logging duplicate attempts in `system.events` with `PartsExportDuplicated` counter, not incrementing `PartsExportFailures`, treating as success
* With `error` policy: Logging duplicate attempts in `system.events` with both `PartsExportDuplicated` and `PartsExportFailures` counters, failing the export
* With `overwrite` policy: Overwriting existing files, logging as successful export, not incrementing duplicate or failure counters
* Ensuring that destination data matches source data without duplication when the same part is exported multiple times with `skip` policy
* Logging duplicate export attempts in the `system.events` table with the `PartsExportDuplicated` counter

## Export Operation Logging

### RQ.ClickHouse.ExportPart.Logging
version: 1.0

[ClickHouse] SHALL provide detailed logging for export operations by:
* Logging all export operations (both successful and failed) with timestamps and details
* Recording the specific part name in the `system.part_log` table for all operations
* Logging export events in the `system.events` table, including:
  * `PartsExports` - Number of successful part exports
  * `PartsExportFailures` - Number of failed part exports
  * `PartsExportDuplicated` - Number of part exports that detected existing files
  * `PartsExportTotalMilliseconds` - Total time spent exporting
* Writing operation information to the `system.part_log` table with `event_type` set to `EXPORT_PART`
* Logging failed exports with error status and error details in `system.part_log`
* Providing sufficient detail for monitoring and troubleshooting export operations

## Monitoring Export Operations

### RQ.ClickHouse.ExportPart.SystemTables.Exports
version: 1.0

[ClickHouse] SHALL provide a `system.exports` table that allows users to monitor active export operations with at least the following columns:
* `source_table` - source table identifier
* `destination_table` - destination table identifier
* `part_name` - name of the part being exported
* Additional metadata about the export operation

The table SHALL track export operations before they complete and SHALL be empty after all exports complete.

### RQ.ClickHouse.ExportPart.Metrics.Export
version: 1.0

[ClickHouse] SHALL provide the `Export` current metric in `system.metrics` table that tracks the number of currently executing exports.

## Settings and Configuration

### RQ.ClickHouse.ExportPart.Settings.AllowExperimental
version: 1.0

[ClickHouse] SHALL support the `allow_experimental_export_merge_tree_part` setting that SHALL gate the experimental export part functionality, which SHALL be set to `1` to enable `ALTER TABLE ... EXPORT PART ...` commands. The default value SHALL be `0` (turned off).

[ClickHouse] SHALL reject export operations when this setting is disabled, throwing an exception (error code 88) with message "Exporting merge tree part is experimental".

### RQ.ClickHouse.ExportPart.Settings.FileAlreadyExistsPolicy
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_part_file_already_exists_policy` setting that controls behavior when exporting a part that already exists in the destination. The setting SHALL accept the following values:
* `skip` (default) - Skip the export if file already exists, log as duplicate, treat as success
* `error` - Fail the export if file already exists, log as duplicate and failure
* `overwrite` - Overwrite existing file, proceed with export

### RQ.ClickHouse.ExportPart.ServerSettings.MaxBandwidth
version: 1.0

[ClickHouse] SHALL support the `max_exports_bandwidth_for_server` server setting to limit the maximum read speed of all exports on the server in bytes per second, with `0` meaning unlimited bandwidth. The default value SHALL be `0`. This is a server-level setting configured in the server configuration file.

### RQ.ClickHouse.ExportPart.ServerSettings.BackgroundMovePoolSize
version: 1.0

[ClickHouse] SHALL support the `background_move_pool_size` server setting to control the maximum number of threads that will be used for executing export operations in the background. The default value SHALL be `8`. This is a server-level setting configured in the server configuration file.

## Export Operation Security

### RQ.ClickHouse.ExportPart.Security
version: 1.0

[ClickHouse] SHALL enforce security requirements for export operations:
* **RBAC**: Users must have the following privileges:
  * **Source Table**: `ALTER` privilege on the source table to initiate export operations
  * **Destination Table**: `INSERT` privilege on the destination table to write exported data
  * **Query Management**: `KILL QUERY` privilege to terminate export operations, allowing users to kill their own export queries and administrators to kill any export query
* **Data Encryption**: All data in transit to destination storage must be encrypted using TLS/SSL
* **Network Security**: Export operations must use secure connections to destination storage (HTTPS for S3, secure protocols for other storage)
* **Credential Management**: Export operations must use secure credential storage and avoid exposing credentials in logs


[ClickHouse]: https://clickhouse.com
""",
)
