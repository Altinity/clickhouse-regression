# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.7.210813.1013350.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_004_TieredStorage = Requirement(
    name="RQ.SRS-004.TieredStorage",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support tiered storage.\n" "\n"),
    link=None,
    level=3,
    num="5.1.1",
)

RQ_SRS_004_MultipleStorageDevices = Requirement(
    name="RQ.SRS-004.MultipleStorageDevices",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support storing data to multiple storage devices.\n" "\n"
    ),
    link=None,
    level=3,
    num="5.1.2",
)

RQ_SRS_004_TableDefinition_NoChangesForQuerying = Requirement(
    name="RQ.SRS-004.TableDefinition.NoChangesForQuerying",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL require no changes to query statements \n"
        "when querying data from a table that supports multiple storage devices. \n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.3",
)

RQ_SRS_004_TableDefinition_ChangesForStoragePolicyOrTTLExpressions = Requirement(
    name="RQ.SRS-004.TableDefinition.ChangesForStoragePolicyOrTTLExpressions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] table definition SHALL need modification only if storage policy or \n"
        "TTL rules are used, whereupon [ClickHouse] automatically places data on different disks/volumes.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.4",
)

RQ_SRS_004_MultipleStorageDevices_Querying = Requirement(
    name="RQ.SRS-004.MultipleStorageDevices.Querying",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support querying data stored in multiple storage devices.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.5",
)

RQ_SRS_004_MultipleStorageDevices_TableMetadata = Requirement(
    name="RQ.SRS-004.MultipleStorageDevices.TableMetadata",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL store table metadata at the default disk.\n" "\n"),
    link=None,
    level=3,
    num="5.1.6",
)

RQ_SRS_004_MultipleStorageDevices_Queries = Requirement(
    name="RQ.SRS-004.MultipleStorageDevices.Queries",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The only thing that affects queries is data location. \n"
        "[ClickHouse] SHALL understand multiple disks and \n"
        "read information about parts from the multiple disks at startup.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.7",
)

RQ_SRS_004_BackgroundMergeProcess_MergingParts = Requirement(
    name="RQ.SRS-004.BackgroundMergeProcess.MergingParts",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] background merge process SHALL merge parts from one disk \n"
        "to another, or initiate special type of merge that moves \n"
        "parts without any extra processing (MOVE_PARTS) if needed.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.8",
)

RQ_SRS_004_BackgroundMergeProcess_MergingParts_MovesAgainstStoragePolicy = Requirement(
    name="RQ.SRS-004.BackgroundMergeProcess.MergingParts.MovesAgainstStoragePolicy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the background merge process to move data\n"
        "against the volume order defined by the storage policy.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.9",
)

RQ_SRS_004_BackgroundMergeProcess_MergingParts_FromMultipleVolumes = Requirement(
    name="RQ.SRS-004.BackgroundMergeProcess.MergingParts.FromMultipleVolumes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[Clickhouse] SHALL use the volume with lowest priority (coldest data storage)\n"
        "when merging parts from multiple volumes. \n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.10",
)

RQ_SRS_004_BackgroundMergeProcess_FaultTolerance_DataCorruption = Requirement(
    name="RQ.SRS-004.BackgroundMergeProcess.FaultTolerance.DataCorruption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be able to recover if data corruption occurs\n"
        "during the background merge process when writing new part\n"
        "to the destination disk.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.11",
)

RQ_SRS_004_BackgroundMergeProcess_FaultTolerance_Restart = Requirement(
    name="RQ.SRS-004.BackgroundMergeProcess.FaultTolerance.Restart",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be able to recover if an abrupt restart\n"
        "of the server occurs in the middle of the background merge\n"
        "process when it writes new part to the destination disk.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.12",
)

RQ_SRS_004_BackgroundMergeProcess_FaultTolerance_NoSpace = Requirement(
    name="RQ.SRS-004.BackgroundMergeProcess.FaultTolerance.NoSpace",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not merge parts if the resulting part's destination disk\n"
        "has no space. The merge SHALL fail and a warning SHALL be printed to the log.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.13",
)

RQ_SRS_004_BackgroundMergeProcess_CheckStoragePolicy = Requirement(
    name="RQ.SRS-004.BackgroundMergeProcess.CheckStoragePolicy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When storage policy is used, [ClickHouse] SHALL check part size and available disk space \n"
        "during periodic merge operations, and schedule move operations if needed.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.14",
)

RQ_SRS_004_BackgroundMergeProcess_ManualTrigger = Requirement(
    name="RQ.SRS-004.BackgroundMergeProcess.ManualTrigger",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL allow merge process to be explicitly triggered using \n"
        "`OPTIMIZE TABLE` or `OPTIMIZE TABLE PARTITION` statements.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.15",
)

RQ_SRS_004_AddingMoreStorageDevices = Requirement(
    name="RQ.SRS-004.AddingMoreStorageDevices",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support adding more storage devices to the existing [ClickHouse] server.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.16",
)

RQ_SRS_004_Configuration_Changes_Restart = Requirement(
    name="RQ.SRS-004.Configuration.Changes.Restart",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] server SHALL need to be restarted when storage device configuration changes\n"
        "except some special cases.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.17",
)

RQ_SRS_004_Configuration_Changes_NoRestart_Warning = Requirement(
    name="RQ.SRS-004.Configuration.Changes.NoRestart.Warning",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] server SHALL ignore the config changes that cannot be applied \n"
        "without a restart and a warning SHALL be written to the log.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.18",
)

RQ_SRS_004_Configuration_Changes_NoRestart_AddingNewDisks = Requirement(
    name="RQ.SRS-004.Configuration.Changes.NoRestart.AddingNewDisks",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] server SHALL not require restart when new disks are added to the storage\n"
        "configuration.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.19",
)

RQ_SRS_004_Configuration_Changes_NoRestart_AddingNewVolumes = Requirement(
    name="RQ.SRS-004.Configuration.Changes.NoRestart.AddingNewVolumes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] server SHALL not require restart when new volumes are added to the storage\n"
        "configuration.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.20",
)

RQ_SRS_004_Configuration_Changes_NoRestart_NewPolicies = Requirement(
    name="RQ.SRS-004.Configuration.Changes.NoRestart.NewPolicies",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] server SHALL not require restart when new policies are added to the storage\n"
        "configuration.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.21",
)

RQ_SRS_004_Configuration_Changes_NoRestart_ChangeInNumericalValues = Requirement(
    name="RQ.SRS-004.Configuration.Changes.NoRestart.ChangeInNumericalValues",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] server SHALL not require restart when numerical value changes are added to the storage\n"
        "configuration.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.22",
)

RQ_SRS_004_DataMovement_Locking = Requirement(
    name="RQ.SRS-004.DataMovement.Locking",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not use locking of any kind for `INSERT` and query operations when \n"
        "parts are moved between disks in the background.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.23",
)

RQ_SRS_004_MovingDataBetweenStorageDevices_FaultTolerant = Requirement(
    name="RQ.SRS-004.MovingDataBetweenStorageDevices.FaultTolerant",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL ensure that all data moves are fault-tolerant.\n" "\n"
    ),
    link=None,
    level=3,
    num="5.1.24",
)

RQ_SRS_004_MovingDataBetweenStorageDevices_Manual = Requirement(
    name="RQ.SRS-004.MovingDataBetweenStorageDevices.Manual",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support mechanism to manually move data between different storage devices.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.25",
)

RQ_SRS_004_MovingDataBetweenStorageDevices_Automatic = Requirement(
    name="RQ.SRS-004.MovingDataBetweenStorageDevices.Automatic",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support mechanism to move data between different storage devices based on a rule.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.26",
)

RQ_SRS_004_Configuration_Startup = Requirement(
    name="RQ.SRS-004.Configuration.Startup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL respect multi-volume configuration automatically during startup.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.27",
)

RQ_SRS_004_Configuration_DefiningMultipleDisks = Requirement(
    name="RQ.SRS-004.Configuration.DefiningMultipleDisks",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support a configuration section for defining multiple disks for a single [ClickHouse] server.\n"
        " \n"
    ),
    link=None,
    level=3,
    num="5.1.28",
)

RQ_SRS_004_Configuration_DefiningMultipleDisks_DefaultDisk = Requirement(
    name="RQ.SRS-004.Configuration.DefiningMultipleDisks.DefaultDisk",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support defining a default disk in the configuration section that defines multiple disks.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.29",
)

RQ_SRS_004_StoragePolicy = Requirement(
    name="RQ.SRS-004.StoragePolicy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support defining storage policies that [ClickHouse] server would use\n"
        "in order to place data on different storage devices.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.30",
)

RQ_SRS_004_StoragePolicy_Multiple = Requirement(
    name="RQ.SRS-004.StoragePolicy.Multiple",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support multiple storage policies.\n" "\n"),
    link=None,
    level=3,
    num="5.1.31",
)

RQ_SRS_004_StoragePolicy_NoEffectOnQueries = Requirement(
    name="RQ.SRS-004.StoragePolicy.NoEffectOnQueries",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] storage policy SHALL not affect queries.\n" "\n"),
    link=None,
    level=3,
    num="5.1.32",
)

RQ_SRS_004_StoragePolicy_Assignment = Requirement(
    name="RQ.SRS-004.StoragePolicy.Assignment",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support storage policy assignment on table basis\n"
        "with `CREATE TABLE` or `ALTER TABLE` statement.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.33",
)

RQ_SRS_004_StoragePolicy_Rules_RoundRobinDistribution = Requirement(
    name="RQ.SRS-004.StoragePolicy.Rules.RoundRobinDistribution",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support storage policy that distributes data between \n"
        "set of disks in a volume (by parts) using round robin selection.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.34",
)

RQ_SRS_004_StoragePolicy_Rules_MoveData_FreeSpace = Requirement(
    name="RQ.SRS-004.StoragePolicy.Rules.MoveData.FreeSpace",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support storage policy rule that specifies how to move data \n"
        "between available volumes based on free space available on the volume.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.35",
)

RQ_SRS_004_StoragePolicy_Rules_MoveData_MaxPartSize = Requirement(
    name="RQ.SRS-004.StoragePolicy.Rules.MoveData.MaxPartSize",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support storage policy rule that specifies how to move data \n"
        "between available volumes based on the maximum partition or part size.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.36",
)

RQ_SRS_004_StoragePolicy_Enforcement_INSERT = Requirement(
    name="RQ.SRS-004.StoragePolicy.Enforcement.INSERT",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL enforce storage policy on `INSERT`.\n" "\n"),
    link=None,
    level=3,
    num="5.1.37",
)

RQ_SRS_004_StoragePolicy_Enforcement_Background = Requirement(
    name="RQ.SRS-004.StoragePolicy.Enforcement.Background",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL enforce storage policy during background operations.\n" "\n"
    ),
    link=None,
    level=3,
    num="5.1.38",
)

RQ_SRS_004_StoragePolicy_Introspection = Requirement(
    name="RQ.SRS-004.StoragePolicy.Introspection",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide introspection information about application\n"
        "of storage policy.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.39",
)

RQ_SRS_004_SQLStatement_MoveTablePartitions = Requirement(
    name="RQ.SRS-004.SQLStatement.MoveTablePartitions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL shall be extended to support new `ALTER TABLE MOVE`\n"
        "SQL statement\n"
        "\n"
        "```sql\n"
        "    ALTER TABLE MOVE PARTITION|PART TO DISK|VOLUME\n"
        "```\n"
        "\n"
        "where `VOLUME` is allowed if storage policy is used.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.40",
)

RQ_SRS_004_StoragePolicy_ReplicatedTable_DownloadedPartPlacement = Requirement(
    name="RQ.SRS-004.StoragePolicy.ReplicatedTable.DownloadedPartPlacement",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL place the parts downloaded from a replica\n"
        "according to the storage policy specified for the table.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.41",
)

RQ_SRS_004_TTLExpressions_ReplicatedTable_DownloadedPartPlacement = Requirement(
    name="RQ.SRS-004.TTLExpressions.ReplicatedTable.DownloadedPartPlacement",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL place the parts downloaded from a replica\n"
        "according to the TTL expressions specified for the table.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.42",
)

RQ_SRS_004_TTLExpressions_Compatibility = Requirement(
    name="RQ.SRS-004.TTLExpressions.Compatibility",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] TTL expressions for data relocation SHALL\n"
        "be compatible with the already available TTL expressions\n"
        "to force deletion of data after an interval.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.43",
)

RQ_SRS_004_TTLExpressions_Compatibility_DefaultDelete = Requirement(
    name="RQ.SRS-004.TTLExpressions.Compatibility.DefaultDelete",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "For backward compatibility with existing TTL expressions\n"
        "[ClickHouse] SHALL default to `DELETE` for all TTL expressions.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.44",
)

RQ_SRS_004_TTLExpressionsForDataRelocation = Requirement(
    name="RQ.SRS-004.TTLExpressionsForDataRelocation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[Clickhouse] SHALL support TTL (time to live) expressions for data relocation.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.45",
)

RQ_SRS_004_TTLExpressions_MaterializeTTL = Requirement(
    name="RQ.SRS-004.TTLExpressions.MaterializeTTL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support materialization of TTL expressions using\n"
        "```sql\n"
        "ALTER TABLE [db.]table MATERIALIZE TTL [IN PARTITION] partition_name\n"
        "```\n"
        "command that SHALL force re-evaluation of all TTL expressions for the whole table\n"
        "or only for a partition of the table if specified.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.46",
)

RQ_SRS_004_Configuration_MultipleDisksDefinition_Syntax = Requirement(
    name="RQ.SRS-004.Configuration.MultipleDisksDefinition.Syntax",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support configuring multiple disks using the following configuration file syntax\n"
        "\n"
        "```xml\n"
        "<path>/path/to/the/default/disk</path>\n"
        "<storage_configuration>\n"
        "    <move_factor>0.1</move_factor>\n"
        "    <disks>\n"
        "        <!--default path maps to <path>/var/lib/clickhouse/</path> in the main config file -->\n"
        "        <default>\n"
        "           <!-- optional, disk size -->\n"
        "           <disk_space_bytes>1000000000</disk_space_bytes>  \n"
        "           <!-- optional, desired free space -->\n"
        "           <keep_free_space_bytes>0</keep_free_space_bytes> \n"
        "           <!-- optional, desired free ratio: used space / total space -->\n"
        "           <keep_free_space_ratio>0</keep_free_space_ratio> \n"
        "        </default>    \n"
        "        <disk_a> <!-- any name of the disk except default -->\n"
        "            <keep_free_space_bytes>0</keep_free_space_bytes>\n"
        "            <keep_free_space_ratio>0</keep_free_space_ratio>\n"
        "            <path>/a/</path>\n"
        "        </disk_a>    \n"
        "        <disk_b>\n"
        "            <keep_free_space_bytes>0</keep_free_space_bytes>\n"
        "            <keep_free_space_ratio>0</keep_free_space_ratio>\n"
        "            <path>/b/</path>\n"
        "        </disk_b>  \n"
        "        <disk_c>\n"
        "            <keep_free_space_bytes>0</keep_free_space_bytes>\n"
        "            <keep_free_space_ratio>0</keep_free_space_ratio>\n"
        "            <path>/c/</path>\n"
        "        </disk_c>  \n"
        "  </disks>\n"
        "</storage_configuration>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.1",
)

RQ_SRS_004_AutomaticPartMovementInTheBackground = Requirement(
    name="RQ.SRS-004.AutomaticPartMovementInTheBackground",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL move parts between volumes in the background to free\n"
        "space in the volumes that are specified from top to bottom.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.2",
)

RQ_SRS_004_AutomaticPartMovementInTheBackground_NoEffectOnQuerying = Requirement(
    name="RQ.SRS-004.AutomaticPartMovementInTheBackground.NoEffectOnQuerying",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL implement background moves such that they have\n"
        "no effect on querying data with data being available for querying at all times.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.3",
)

RQ_SRS_004_Configuration_StorageConfiguration_MoveFactor = Requirement(
    name="RQ.SRS-004.Configuration.StorageConfiguration.MoveFactor",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The `move_factor` option SHALL specify the amount of free space which\n"
        "when exceeded causes data to be moved to the next volume, if exists.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.4",
)

RQ_SRS_004_Configuration_StorageConfiguration_MoveFactor_DefaultValue = Requirement(
    name="RQ.SRS-004.Configuration.StorageConfiguration.MoveFactor.DefaultValue",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL set the default value of `move_factor` to 0.1 if not specified.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.5",
)

RQ_SRS_004_Configuration_StorageConfiguration_MoveFactor_Range = Requirement(
    name="RQ.SRS-004.Configuration.StorageConfiguration.MoveFactor.Range",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("The `move_factor` SHALL have value range of 0 to 1.\n" "\n"),
    link=None,
    level=3,
    num="5.2.6",
)

RQ_SRS_004_Configuration_MultipleDisksDefinition_Syntax_Disk_Options = Requirement(
    name="RQ.SRS-004.Configuration.MultipleDisksDefinition.Syntax.Disk.Options",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the following values as part of the `DISK`\n"
        "description:\n"
        "\n"
        "* **disk_space_bytes** - disk size in bytes\n"
        "* **keep_free_space_bytes** - desired free space in bytes \n"
        "* **keep_free_space_ratio** - desired free ratio `used space / total space`\n"
        "* **path** - path to disk\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.7",
)

RQ_SRS_004_Configuration_MultipleDisksDefinition_Syntax_Disk_Options_EitherBytesOrRatio = Requirement(
    name="RQ.SRS-004.Configuration.MultipleDisksDefinition.Syntax.Disk.Options.EitherBytesOrRatio",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL raise an exception if both `keep_free_space_bytes` and \n"
        "`keep_free_space_ratio` is specified for the same disk.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.8",
)

RQ_SRS_004_Configuration_MultipleDisksDefinition_Syntax_Disk_Options_NoBytesOrRatio = Requirement(
    name="RQ.SRS-004.Configuration.MultipleDisksDefinition.Syntax.Disk.Options.NoBytesOrRatio",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL use only `disk_space_bytes` if neither `keep_free_space_bytes`\n"
        "or `keep_free_space_ratio` is specified.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.9",
)

RQ_SRS_004_Configuration_Disks_Reading = Requirement(
    name="RQ.SRS-004.Configuration.Disks.Reading",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading disk configuration using\n"
        "\n"
        "```sql\n"
        "SELECT * FROM system.disks\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.10",
)

RQ_SRS_004_Configuration_Disks_DetachedParts_Reading = Requirement(
    name="RQ.SRS-004.Configuration.Disks.DetachedParts.Reading",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading disk for the\n"
        "detached parts from the `system.detached_parts` table.\n"
        "\n"
        "```sql\n"
        "SELECT disk FROM system.detached_parts\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.11",
)

RQ_SRS_004_MovingDataBetweenStorageDevices_Manual_WithDowntime = Requirement(
    name="RQ.SRS-004.MovingDataBetweenStorageDevices.Manual.WithDowntime",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support manually moving data between storage devices **with\n"
        "downtime** using the following procedure:\n"
        "\n"
        "```sql\n"
        "ALTER TABLE DETACH PARTITION|PART <name>\n"
        "-- mv disk_a/.../detached/<name> disk_b/…/detached/<name>\n"
        "ALTER TABLE ATTACH PARTITION|PART <name>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.12",
)

RQ_SRS_004_MovingDataBetweenStorageDevices_Manual_NoDowntime = Requirement(
    name="RQ.SRS-004.MovingDataBetweenStorageDevices.Manual.NoDowntime",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support manually moving data between storage devices **with no\n"
        "downtime** using the following procedure:\n"
        "\n"
        "```sql\n"
        "ALTER TABLE MOVE PARTITION|PART <name> TO DISK|VOLUME <name>\n"
        "ALTER TABLE OPTIMIZE PARTITION <name> TO DISK|VOLUME <name> [FINAL]\n"
        "```\n"
        "with an additional merge performed during the relocation if necessary.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.13",
)

RQ_SRS_004_StoragePolicy_Syntax = Requirement(
    name="RQ.SRS-004.StoragePolicy.Syntax",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the following syntax to define storage policy\n"
        "\n"
        "```xml\n"
        "<storage_configuration>\n"
        "    <!-- policies are used in order to configure JBOD and server level rules -->\n"
        "    <!-- they are optional and not required unless JBOD and automatic rules are necessary -->\n"
        "    <!-- volumes support 2 parameters: max_data_part_size_bytes, max_data_part_size_ratio -->\n"
        "    \n"
        "    <policies>\n"
        "        <default> <!-- policy name, used to reference from the table definition -->\n"
        "            <volumes>\n"
        "              <vol1>\n"
        "                <disk>default</disk>\n"
        "                <max_data_part_size_bytes>10000000</max_data_part_size_bytes>\n"
        "              </vol1>\n"
        "              <vol2>\n"
        "                <disk>disk_a</disk>\n"
        "                <max_data_part_size_bytes>100000000</max_data_part_size_bytes>\n"
        "              </vol2>\n"
        "              <vol3>\n"
        "                <disk>disk_b</disk>\n"
        "                <disk>disk_c</disk> \n"
        "             </vol3>\n"
        "           </volumes>\n"
        "        <default>\n"
        "</storage_configuration>\n"
        "```\n"
        "\n"
        "when `default` policy is not explicitly stated the following default policy\n"
        "is used that is equal to the definition below\n"
        "\n"
        "```xml\n"
        "<default>\n"
        "    <volumes>\n"
        "       <disk>default</disk>\n"
        "    </volumes>\n"
        "</default>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.14",
)

RQ_SRS_004_StoragePolicy_Reading = Requirement(
    name="RQ.SRS-004.StoragePolicy.Reading",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading storage policy using\n"
        "\n"
        "```sql\n"
        "SELECT * FROM system.storage_policies\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.15",
)

RQ_SRS_004_StoragePolicy_Syntax_Volume_Options = Requirement(
    name="RQ.SRS-004.StoragePolicy.Syntax.Volume.Options",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the following values as part of `VOLUME`\n"
        "description:\n"
        "\n"
        "* **disk** - one or more disks to use\n"
        "* **max_data_part_size_bytes** - maximum part size in bytes\n"
        "* **max_data_part_size_ratio** - maximum part size ratio that is defined as\n"
        "  `max_data_part_size > (sum_size * max_data_part_size_ratio / number_of_disks)`\n"
        "  where `sum_size` is the total size of the space on all disks inside the volume\n"
        "  and the `number_of_disks` is the number of disks inside the volume.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.16",
)

RQ_SRS_004_StoragePolicy_Syntax_Volume_Options_EitherBytesOrRatio = Requirement(
    name="RQ.SRS-004.StoragePolicy.Syntax.Volume.Options.EitherBytesOrRatio",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL raise an exception if both `max_data_part_size_bytes` and \n"
        "`max_data_part_size_ratio` is specified for the same volume.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.17",
)

RQ_SRS_004_StoragePolicy_RuleMatchOrder = Requirement(
    name="RQ.SRS-004.StoragePolicy.RuleMatchOrder",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL apply storage policy rules from top to bottom\n"
        "and the first match SHALL be used.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.18",
)

RQ_SRS_004_StoragePolicy_AddingToTable_CreateTable = Requirement(
    name="RQ.SRS-004.StoragePolicy.AddingToTable.CreateTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support assigning storage policy\n"
        "when creating a table with the `CREATE TABLE` command using the\n"
        "`storage_policy_name` setting.\n"
        "\n"
        "```sql\n"
        "CREATE TABLE … SETTINGS storage_policy_name='policy2';\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.19",
)

RQ_SRS_004_Volume_StoragePolicy_AddingToTable_AlterTable = Requirement(
    name="RQ.SRS-004.Volume.StoragePolicy.AddingToTable.AlterTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support assigning storage policy\n"
        "to an already existing table using the `ALTER TABLE` command\n"
        "only when new policy have all the disks from the previous policy,\n"
        "otherwise an exception SHALL be raised.\n"
        "\n"
        "```sql\n"
        "ALTER TABLE … SETTINGS storage_policy_name='policy2';\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.20",
)

RQ_SRS_004_StoragePolicy_Application_BackgroundMerge = Requirement(
    name="RQ.SRS-004.StoragePolicy.Application.BackgroundMerge",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL estimate the size of the new generated part that would \n"
        "comply with the `volume` storage policy. \n"
        "The storage policy is checked top to bottom against constraints of each\n"
        "volume. \n"
        "\n"
        "If part size > `max_part_size_bytes` or part ratio > `max_part_size_ratio`\n"
        "then the next `volume` is checked.\n"
        "\n"
        "When a volume is considered, it then is checked against the constraints of the\n"
        "disks that are part of the volume.\n"
        "\n"
        "If no volume can be chosen then an exception SHALL be raised.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.21",
)

RQ_SRS_004_TTLExpressions_RuleNotSatisfied = Requirement(
    name="RQ.SRS-004.TTLExpressions.RuleNotSatisfied",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL ignore any TTL expressions to move data if the TTL expression\n"
        "or the TTL destination can't be satisfied. If the TTL destination can't be satisfied\n"
        "then a warning message SHALL be written to the log.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.22",
)

RQ_SRS_004_TTLExpressions_Evaluation = Requirement(
    name="RQ.SRS-004.TTLExpressions.Evaluation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support only TTL expressions that evaluate to\n"
        "`Date` or `DateTime` data type.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.23",
)

RQ_SRS_004_TTLExpressions_Selection = Requirement(
    name="RQ.SRS-004.TTLExpressions.Selection",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] TTL expressions SHALL be selected based on the length of the time interval\n"
        "with shorter intervals being selected first.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.24",
)

RQ_SRS_004_TTLExpressions_Syntax = Requirement(
    name="RQ.SRS-004.TTLExpressions.Syntax",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support TTL expressions using the following syntax\n"
        "\n"
        "```sql\n"
        "TTL <expr> [TO DISK <name> | TO VOLUME <name> | DELETE]\n"
        "```\n"
        "\n"
        "where multiple comma can be used to separated TTL expressions.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.25",
)

RQ_SRS_004_TTLExpressions_MultipleColumns = Requirement(
    name="RQ.SRS-004.TTLExpressions.MultipleColumns",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support TTL expressions that use multiple columns.\n"
        "\n"
        "```sql\n"
        "TTL d1 + d2 + INTERVAL 7 DAY TO DISK 'disk_2',\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.26",
)

RQ_SRS_004_TTLExpressions_Alter_DropColumn = Requirement(
    name="RQ.SRS-004.TTLExpressions.Alter.DropColumn",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL raise an exception if a column that is used\n"
        "inside a TTL expression is attempted to be dropped using the\n"
        "`ALTER` `DROP COLUMN` statement.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.27",
)

RQ_SRS_004_TTLExpressions_Alter_AddColumn = Requirement(
    name="RQ.SRS-004.TTLExpressions.Alter.AddColumn",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support adding a new column to a table\n"
        "that has a TTL expression using the `ALTER` `ADD COLUMN` statement.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.28",
)

RQ_SRS_004_TTLExpressions_Alter_CommentColumn = Requirement(
    name="RQ.SRS-004.TTLExpressions.Alter.CommentColumn",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support adding a text comment to a column\n"
        "that is used in a TTL expression using the `ALTER` `COMMENT COLUMN` \n"
        "statement.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.29",
)

RQ_SRS_004_TTLExpressions_Alter_ClearColumn = Requirement(
    name="RQ.SRS-004.TTLExpressions.Alter.ClearColumn",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support clearing a column that is used in a\n"
        "TTL expression using the `ALTER` `CLEAR COLUMN` statement.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.30",
)

RQ_SRS_004_TTLExpressions_Alter_ModifyColumn = Requirement(
    name="RQ.SRS-004.TTLExpressions.Alter.ModifyColumn",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support modifying type of a column that is used in\n"
        "a TTL expression using the `ALTER` `CLEAR COLUMN` statement as long as\n"
        "the TTL expression still evaluates to a `Date` or a `DateTime` type.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.31",
)

RQ_SRS_004_TTLExpressions_Mutations_Update = Requirement(
    name="RQ.SRS-004.TTLExpressions.Mutations.Update",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `ALTER` `UPDATE` mutation on a column that is \n"
        "used in a TTL expression and the TTL expression SHALL be recalculated.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.32",
)

RQ_SRS_004_TTLExpressions_Mutations_Delete = Requirement(
    name="RQ.SRS-004.TTLExpressions.Mutations.Delete",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `ALTER` `DELETE` mutation on a column that is used\n"
        "in a TTL expression.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.33",
)

RQ_SRS_004_TTLExpressions_Application_NoEffectOnQuerying = Requirement(
    name="RQ.SRS-004.TTLExpressions.Application.NoEffectOnQuerying",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL implement TTL moves such that TTL moves have\n"
        "no effect on querying data with data being available for querying at all times.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.34",
)

RQ_SRS_004_TTLExpressions_FaultTolerance_DataCorruption = Requirement(
    name="RQ.SRS-004.TTLExpressions.FaultTolerance.DataCorruption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be able to recover if data corruption occurs\n"
        "during the TTL move.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.35",
)

RQ_SRS_004_TTLExpressions_FaultTolerance_Restart = Requirement(
    name="RQ.SRS-004.TTLExpressions.FaultTolerance.Restart",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be able to recover if an abrupt restart\n"
        "of the server occurs in the middle of the TTL move.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.36",
)

RQ_SRS_004_TTLExpressions_FaultTolerance_NoSpace = Requirement(
    name="RQ.SRS-004.TTLExpressions.FaultTolerance.NoSpace",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not perform TTL move if the destination disk \n"
        "has no free space. The TTL move SHALL be aborted and\n"
        "a warning SHALL be written to the log file.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.37",
)

RQ_SRS_004_TTLExpressions_AddingToTable_CreateTable = Requirement(
    name="RQ.SRS-004.TTLExpressions.AddingToTable.CreateTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support adding TTL expressions for data relocation\n"
        "when creating a table with the `CREATE TABLE` command.\n"
        "\n"
        "```sql\n"
        "CREATE TABLE ... \n"
        "TTL date + INTERVAL 7 DAY TO DISK 'disk_2', \n"
        "    date + INTERVAL 30 DAY TO DISK 'disk_3',\n"
        "    date + INTERVAL 60 DAY TO VOLUME 'vol1',\n"
        "    date + INTERVAL 180 DAY DELETE\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.38",
)

RQ_SRS_004_TTLExpressions_AddingToTable_AlterTable = Requirement(
    name="RQ.SRS-004.TTLExpressions.AddingToTable.AlterTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support adding TTL expressions for data relocation\n"
        "to an already existing table using the `ALTER TABLE` command.\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "ALTER TABLE MODIFY \n"
        "TTL date + INTERVAL 7 DAY TO DISK 'disk_2', \n"
        "    date + INTERVAL 30 DAY TO DISK 'disk_3',\n"
        "    date + INTERVAL 180 DAY DELETE\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.39",
)

RQ_SRS_004_TTLExpressions_AddingToTable_AlterTable_ReplaceExisting = Requirement(
    name="RQ.SRS-004.TTLExpressions.AddingToTable.AlterTable.ReplaceExisting",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL drop all existing TTL expression rules\n"
        "when the `ALTER TABLE` command is used to add or update TTL expressions.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.40",
)

QA_SRS004_ClickHouse_Tiered_Storage = Specification(
    name="QA-SRS004 ClickHouse Tiered Storage",
    description=None,
    author="vzakaznikov@altinity.com",
    date="October 7, 2019",
    status="-",
    approved_by="-",
    approved_date="-",
    approved_version="-",
    version=None,
    group=None,
    type=None,
    link=None,
    uid=None,
    parent=None,
    children=None,
    headings=(
        Heading(name="Revision History", level=1, num="1"),
        Heading(name="Introduction", level=1, num="2"),
        Heading(name="Terminology", level=1, num="3"),
        Heading(name="TTL Expressions for Data Relocation", level=1, num="4"),
        Heading(name="Requirements", level=1, num="5"),
        Heading(name="General", level=2, num="5.1"),
        Heading(name="RQ.SRS-004.TieredStorage", level=3, num="5.1.1"),
        Heading(name="RQ.SRS-004.MultipleStorageDevices", level=3, num="5.1.2"),
        Heading(
            name="RQ.SRS-004.TableDefinition.NoChangesForQuerying", level=3, num="5.1.3"
        ),
        Heading(
            name="RQ.SRS-004.TableDefinition.ChangesForStoragePolicyOrTTLExpressions",
            level=3,
            num="5.1.4",
        ),
        Heading(
            name="RQ.SRS-004.MultipleStorageDevices.Querying", level=3, num="5.1.5"
        ),
        Heading(
            name="RQ.SRS-004.MultipleStorageDevices.TableMetadata", level=3, num="5.1.6"
        ),
        Heading(name="RQ.SRS-004.MultipleStorageDevices.Queries", level=3, num="5.1.7"),
        Heading(
            name="RQ.SRS-004.BackgroundMergeProcess.MergingParts", level=3, num="5.1.8"
        ),
        Heading(
            name="RQ.SRS-004.BackgroundMergeProcess.MergingParts.MovesAgainstStoragePolicy",
            level=3,
            num="5.1.9",
        ),
        Heading(
            name="RQ.SRS-004.BackgroundMergeProcess.MergingParts.FromMultipleVolumes",
            level=3,
            num="5.1.10",
        ),
        Heading(
            name="RQ.SRS-004.BackgroundMergeProcess.FaultTolerance.DataCorruption",
            level=3,
            num="5.1.11",
        ),
        Heading(
            name="RQ.SRS-004.BackgroundMergeProcess.FaultTolerance.Restart",
            level=3,
            num="5.1.12",
        ),
        Heading(
            name="RQ.SRS-004.BackgroundMergeProcess.FaultTolerance.NoSpace",
            level=3,
            num="5.1.13",
        ),
        Heading(
            name="RQ.SRS-004.BackgroundMergeProcess.CheckStoragePolicy",
            level=3,
            num="5.1.14",
        ),
        Heading(
            name="RQ.SRS-004.BackgroundMergeProcess.ManualTrigger",
            level=3,
            num="5.1.15",
        ),
        Heading(name="RQ.SRS-004.AddingMoreStorageDevices", level=3, num="5.1.16"),
        Heading(name="RQ.SRS-004.Configuration.Changes.Restart", level=3, num="5.1.17"),
        Heading(
            name="RQ.SRS-004.Configuration.Changes.NoRestart.Warning",
            level=3,
            num="5.1.18",
        ),
        Heading(
            name="RQ.SRS-004.Configuration.Changes.NoRestart.AddingNewDisks",
            level=3,
            num="5.1.19",
        ),
        Heading(
            name="RQ.SRS-004.Configuration.Changes.NoRestart.AddingNewVolumes",
            level=3,
            num="5.1.20",
        ),
        Heading(
            name="RQ.SRS-004.Configuration.Changes.NoRestart.NewPolicies",
            level=3,
            num="5.1.21",
        ),
        Heading(
            name="RQ.SRS-004.Configuration.Changes.NoRestart.ChangeInNumericalValues",
            level=3,
            num="5.1.22",
        ),
        Heading(name="RQ.SRS-004.DataMovement.Locking", level=3, num="5.1.23"),
        Heading(
            name="RQ.SRS-004.MovingDataBetweenStorageDevices.FaultTolerant",
            level=3,
            num="5.1.24",
        ),
        Heading(
            name="RQ.SRS-004.MovingDataBetweenStorageDevices.Manual",
            level=3,
            num="5.1.25",
        ),
        Heading(
            name="RQ.SRS-004.MovingDataBetweenStorageDevices.Automatic",
            level=3,
            num="5.1.26",
        ),
        Heading(name="RQ.SRS-004.Configuration.Startup", level=3, num="5.1.27"),
        Heading(
            name="RQ.SRS-004.Configuration.DefiningMultipleDisks", level=3, num="5.1.28"
        ),
        Heading(
            name="RQ.SRS-004.Configuration.DefiningMultipleDisks.DefaultDisk",
            level=3,
            num="5.1.29",
        ),
        Heading(name="RQ.SRS-004.StoragePolicy", level=3, num="5.1.30"),
        Heading(name="RQ.SRS-004.StoragePolicy.Multiple", level=3, num="5.1.31"),
        Heading(
            name="RQ.SRS-004.StoragePolicy.NoEffectOnQueries", level=3, num="5.1.32"
        ),
        Heading(name="RQ.SRS-004.StoragePolicy.Assignment", level=3, num="5.1.33"),
        Heading(
            name="RQ.SRS-004.StoragePolicy.Rules.RoundRobinDistribution",
            level=3,
            num="5.1.34",
        ),
        Heading(
            name="RQ.SRS-004.StoragePolicy.Rules.MoveData.FreeSpace",
            level=3,
            num="5.1.35",
        ),
        Heading(
            name="RQ.SRS-004.StoragePolicy.Rules.MoveData.MaxPartSize",
            level=3,
            num="5.1.36",
        ),
        Heading(
            name="RQ.SRS-004.StoragePolicy.Enforcement.INSERT", level=3, num="5.1.37"
        ),
        Heading(
            name="RQ.SRS-004.StoragePolicy.Enforcement.Background",
            level=3,
            num="5.1.38",
        ),
        Heading(name="RQ.SRS-004.StoragePolicy.Introspection", level=3, num="5.1.39"),
        Heading(
            name="RQ.SRS-004.SQLStatement.MoveTablePartitions", level=3, num="5.1.40"
        ),
        Heading(
            name="RQ.SRS-004.StoragePolicy.ReplicatedTable.DownloadedPartPlacement",
            level=3,
            num="5.1.41",
        ),
        Heading(
            name="RQ.SRS-004.TTLExpressions.ReplicatedTable.DownloadedPartPlacement",
            level=3,
            num="5.1.42",
        ),
        Heading(name="RQ.SRS-004.TTLExpressions.Compatibility", level=3, num="5.1.43"),
        Heading(
            name="RQ.SRS-004.TTLExpressions.Compatibility.DefaultDelete",
            level=3,
            num="5.1.44",
        ),
        Heading(
            name="RQ.SRS-004.TTLExpressionsForDataRelocation", level=3, num="5.1.45"
        ),
        Heading(name="RQ.SRS-004.TTLExpressions.MaterializeTTL", level=3, num="5.1.46"),
        Heading(name="Specific", level=2, num="5.2"),
        Heading(
            name="RQ.SRS-004.Configuration.MultipleDisksDefinition.Syntax",
            level=3,
            num="5.2.1",
        ),
        Heading(
            name="RQ.SRS-004.AutomaticPartMovementInTheBackground", level=3, num="5.2.2"
        ),
        Heading(
            name="RQ.SRS-004.AutomaticPartMovementInTheBackground.NoEffectOnQuerying",
            level=3,
            num="5.2.3",
        ),
        Heading(
            name="RQ.SRS-004.Configuration.StorageConfiguration.MoveFactor",
            level=3,
            num="5.2.4",
        ),
        Heading(
            name="RQ.SRS-004.Configuration.StorageConfiguration.MoveFactor.DefaultValue",
            level=3,
            num="5.2.5",
        ),
        Heading(
            name="RQ.SRS-004.Configuration.StorageConfiguration.MoveFactor.Range",
            level=3,
            num="5.2.6",
        ),
        Heading(
            name="RQ.SRS-004.Configuration.MultipleDisksDefinition.Syntax.Disk.Options",
            level=3,
            num="5.2.7",
        ),
        Heading(
            name="RQ.SRS-004.Configuration.MultipleDisksDefinition.Syntax.Disk.Options.EitherBytesOrRatio",
            level=3,
            num="5.2.8",
        ),
        Heading(
            name="RQ.SRS-004.Configuration.MultipleDisksDefinition.Syntax.Disk.Options.NoBytesOrRatio",
            level=3,
            num="5.2.9",
        ),
        Heading(name="RQ.SRS-004.Configuration.Disks.Reading", level=3, num="5.2.10"),
        Heading(
            name="RQ.SRS-004.Configuration.Disks.DetachedParts.Reading",
            level=3,
            num="5.2.11",
        ),
        Heading(
            name="RQ.SRS-004.MovingDataBetweenStorageDevices.Manual.WithDowntime",
            level=3,
            num="5.2.12",
        ),
        Heading(
            name="RQ.SRS-004.MovingDataBetweenStorageDevices.Manual.NoDowntime",
            level=3,
            num="5.2.13",
        ),
        Heading(name="RQ.SRS-004.StoragePolicy.Syntax", level=3, num="5.2.14"),
        Heading(name="RQ.SRS-004.StoragePolicy.Reading", level=3, num="5.2.15"),
        Heading(
            name="RQ.SRS-004.StoragePolicy.Syntax.Volume.Options", level=3, num="5.2.16"
        ),
        Heading(
            name="RQ.SRS-004.StoragePolicy.Syntax.Volume.Options.EitherBytesOrRatio",
            level=3,
            num="5.2.17",
        ),
        Heading(name="RQ.SRS-004.StoragePolicy.RuleMatchOrder", level=3, num="5.2.18"),
        Heading(
            name="RQ.SRS-004.StoragePolicy.AddingToTable.CreateTable",
            level=3,
            num="5.2.19",
        ),
        Heading(
            name="RQ.SRS-004.Volume.StoragePolicy.AddingToTable.AlterTable",
            level=3,
            num="5.2.20",
        ),
        Heading(
            name="RQ.SRS-004.StoragePolicy.Application.BackgroundMerge",
            level=3,
            num="5.2.21",
        ),
        Heading(
            name="RQ.SRS-004.TTLExpressions.RuleNotSatisfied", level=3, num="5.2.22"
        ),
        Heading(name="RQ.SRS-004.TTLExpressions.Evaluation", level=3, num="5.2.23"),
        Heading(name="RQ.SRS-004.TTLExpressions.Selection", level=3, num="5.2.24"),
        Heading(name="RQ.SRS-004.TTLExpressions.Syntax", level=3, num="5.2.25"),
        Heading(
            name="RQ.SRS-004.TTLExpressions.MultipleColumns", level=3, num="5.2.26"
        ),
        Heading(
            name="RQ.SRS-004.TTLExpressions.Alter.DropColumn", level=3, num="5.2.27"
        ),
        Heading(
            name="RQ.SRS-004.TTLExpressions.Alter.AddColumn", level=3, num="5.2.28"
        ),
        Heading(
            name="RQ.SRS-004.TTLExpressions.Alter.CommentColumn", level=3, num="5.2.29"
        ),
        Heading(
            name="RQ.SRS-004.TTLExpressions.Alter.ClearColumn", level=3, num="5.2.30"
        ),
        Heading(
            name="RQ.SRS-004.TTLExpressions.Alter.ModifyColumn", level=3, num="5.2.31"
        ),
        Heading(
            name="RQ.SRS-004.TTLExpressions.Mutations.Update", level=3, num="5.2.32"
        ),
        Heading(
            name="RQ.SRS-004.TTLExpressions.Mutations.Delete", level=3, num="5.2.33"
        ),
        Heading(
            name="RQ.SRS-004.TTLExpressions.Application.NoEffectOnQuerying",
            level=3,
            num="5.2.34",
        ),
        Heading(
            name="RQ.SRS-004.TTLExpressions.FaultTolerance.DataCorruption",
            level=3,
            num="5.2.35",
        ),
        Heading(
            name="RQ.SRS-004.TTLExpressions.FaultTolerance.Restart",
            level=3,
            num="5.2.36",
        ),
        Heading(
            name="RQ.SRS-004.TTLExpressions.FaultTolerance.NoSpace",
            level=3,
            num="5.2.37",
        ),
        Heading(
            name="RQ.SRS-004.TTLExpressions.AddingToTable.CreateTable",
            level=3,
            num="5.2.38",
        ),
        Heading(
            name="RQ.SRS-004.TTLExpressions.AddingToTable.AlterTable",
            level=3,
            num="5.2.39",
        ),
        Heading(
            name="RQ.SRS-004.TTLExpressions.AddingToTable.AlterTable.ReplaceExisting",
            level=3,
            num="5.2.40",
        ),
        Heading(name="References", level=1, num="6"),
    ),
    requirements=(
        RQ_SRS_004_TieredStorage,
        RQ_SRS_004_MultipleStorageDevices,
        RQ_SRS_004_TableDefinition_NoChangesForQuerying,
        RQ_SRS_004_TableDefinition_ChangesForStoragePolicyOrTTLExpressions,
        RQ_SRS_004_MultipleStorageDevices_Querying,
        RQ_SRS_004_MultipleStorageDevices_TableMetadata,
        RQ_SRS_004_MultipleStorageDevices_Queries,
        RQ_SRS_004_BackgroundMergeProcess_MergingParts,
        RQ_SRS_004_BackgroundMergeProcess_MergingParts_MovesAgainstStoragePolicy,
        RQ_SRS_004_BackgroundMergeProcess_MergingParts_FromMultipleVolumes,
        RQ_SRS_004_BackgroundMergeProcess_FaultTolerance_DataCorruption,
        RQ_SRS_004_BackgroundMergeProcess_FaultTolerance_Restart,
        RQ_SRS_004_BackgroundMergeProcess_FaultTolerance_NoSpace,
        RQ_SRS_004_BackgroundMergeProcess_CheckStoragePolicy,
        RQ_SRS_004_BackgroundMergeProcess_ManualTrigger,
        RQ_SRS_004_AddingMoreStorageDevices,
        RQ_SRS_004_Configuration_Changes_Restart,
        RQ_SRS_004_Configuration_Changes_NoRestart_Warning,
        RQ_SRS_004_Configuration_Changes_NoRestart_AddingNewDisks,
        RQ_SRS_004_Configuration_Changes_NoRestart_AddingNewVolumes,
        RQ_SRS_004_Configuration_Changes_NoRestart_NewPolicies,
        RQ_SRS_004_Configuration_Changes_NoRestart_ChangeInNumericalValues,
        RQ_SRS_004_DataMovement_Locking,
        RQ_SRS_004_MovingDataBetweenStorageDevices_FaultTolerant,
        RQ_SRS_004_MovingDataBetweenStorageDevices_Manual,
        RQ_SRS_004_MovingDataBetweenStorageDevices_Automatic,
        RQ_SRS_004_Configuration_Startup,
        RQ_SRS_004_Configuration_DefiningMultipleDisks,
        RQ_SRS_004_Configuration_DefiningMultipleDisks_DefaultDisk,
        RQ_SRS_004_StoragePolicy,
        RQ_SRS_004_StoragePolicy_Multiple,
        RQ_SRS_004_StoragePolicy_NoEffectOnQueries,
        RQ_SRS_004_StoragePolicy_Assignment,
        RQ_SRS_004_StoragePolicy_Rules_RoundRobinDistribution,
        RQ_SRS_004_StoragePolicy_Rules_MoveData_FreeSpace,
        RQ_SRS_004_StoragePolicy_Rules_MoveData_MaxPartSize,
        RQ_SRS_004_StoragePolicy_Enforcement_INSERT,
        RQ_SRS_004_StoragePolicy_Enforcement_Background,
        RQ_SRS_004_StoragePolicy_Introspection,
        RQ_SRS_004_SQLStatement_MoveTablePartitions,
        RQ_SRS_004_StoragePolicy_ReplicatedTable_DownloadedPartPlacement,
        RQ_SRS_004_TTLExpressions_ReplicatedTable_DownloadedPartPlacement,
        RQ_SRS_004_TTLExpressions_Compatibility,
        RQ_SRS_004_TTLExpressions_Compatibility_DefaultDelete,
        RQ_SRS_004_TTLExpressionsForDataRelocation,
        RQ_SRS_004_TTLExpressions_MaterializeTTL,
        RQ_SRS_004_Configuration_MultipleDisksDefinition_Syntax,
        RQ_SRS_004_AutomaticPartMovementInTheBackground,
        RQ_SRS_004_AutomaticPartMovementInTheBackground_NoEffectOnQuerying,
        RQ_SRS_004_Configuration_StorageConfiguration_MoveFactor,
        RQ_SRS_004_Configuration_StorageConfiguration_MoveFactor_DefaultValue,
        RQ_SRS_004_Configuration_StorageConfiguration_MoveFactor_Range,
        RQ_SRS_004_Configuration_MultipleDisksDefinition_Syntax_Disk_Options,
        RQ_SRS_004_Configuration_MultipleDisksDefinition_Syntax_Disk_Options_EitherBytesOrRatio,
        RQ_SRS_004_Configuration_MultipleDisksDefinition_Syntax_Disk_Options_NoBytesOrRatio,
        RQ_SRS_004_Configuration_Disks_Reading,
        RQ_SRS_004_Configuration_Disks_DetachedParts_Reading,
        RQ_SRS_004_MovingDataBetweenStorageDevices_Manual_WithDowntime,
        RQ_SRS_004_MovingDataBetweenStorageDevices_Manual_NoDowntime,
        RQ_SRS_004_StoragePolicy_Syntax,
        RQ_SRS_004_StoragePolicy_Reading,
        RQ_SRS_004_StoragePolicy_Syntax_Volume_Options,
        RQ_SRS_004_StoragePolicy_Syntax_Volume_Options_EitherBytesOrRatio,
        RQ_SRS_004_StoragePolicy_RuleMatchOrder,
        RQ_SRS_004_StoragePolicy_AddingToTable_CreateTable,
        RQ_SRS_004_Volume_StoragePolicy_AddingToTable_AlterTable,
        RQ_SRS_004_StoragePolicy_Application_BackgroundMerge,
        RQ_SRS_004_TTLExpressions_RuleNotSatisfied,
        RQ_SRS_004_TTLExpressions_Evaluation,
        RQ_SRS_004_TTLExpressions_Selection,
        RQ_SRS_004_TTLExpressions_Syntax,
        RQ_SRS_004_TTLExpressions_MultipleColumns,
        RQ_SRS_004_TTLExpressions_Alter_DropColumn,
        RQ_SRS_004_TTLExpressions_Alter_AddColumn,
        RQ_SRS_004_TTLExpressions_Alter_CommentColumn,
        RQ_SRS_004_TTLExpressions_Alter_ClearColumn,
        RQ_SRS_004_TTLExpressions_Alter_ModifyColumn,
        RQ_SRS_004_TTLExpressions_Mutations_Update,
        RQ_SRS_004_TTLExpressions_Mutations_Delete,
        RQ_SRS_004_TTLExpressions_Application_NoEffectOnQuerying,
        RQ_SRS_004_TTLExpressions_FaultTolerance_DataCorruption,
        RQ_SRS_004_TTLExpressions_FaultTolerance_Restart,
        RQ_SRS_004_TTLExpressions_FaultTolerance_NoSpace,
        RQ_SRS_004_TTLExpressions_AddingToTable_CreateTable,
        RQ_SRS_004_TTLExpressions_AddingToTable_AlterTable,
        RQ_SRS_004_TTLExpressions_AddingToTable_AlterTable_ReplaceExisting,
    ),
    content="""
# QA-SRS004 ClickHouse Tiered Storage
# Software Requirements Specification

Copyright 2019-2021 Altinity Inc. All Rights Reserved.

**Document status:** Confidential

**Author:** vzakaznikov@altinity.com

**Date:** October 7, 2019

## Approval

**Status:** -

**Version:** -

**Approved by:** -

**Date:** -

## Table of Contents
* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Terminology](#terminology)
* 4 [TTL Expressions for Data Relocation](#ttl-expressions-for-data-relocation)
* 5 [Requirements](#requirements)
  * 5.1 [General](#general)
    * 5.1.1 [RQ.SRS-004.TieredStorage](#rqsrs-004tieredstorage)
    * 5.1.2 [RQ.SRS-004.MultipleStorageDevices](#rqsrs-004multiplestoragedevices)
    * 5.1.3 [RQ.SRS-004.TableDefinition.NoChangesForQuerying](#rqsrs-004tabledefinitionnochangesforquerying)
    * 5.1.4 [RQ.SRS-004.TableDefinition.ChangesForStoragePolicyOrTTLExpressions](#rqsrs-004tabledefinitionchangesforstoragepolicyorttlexpressions)
    * 5.1.5 [RQ.SRS-004.MultipleStorageDevices.Querying](#rqsrs-004multiplestoragedevicesquerying)
    * 5.1.6 [RQ.SRS-004.MultipleStorageDevices.TableMetadata](#rqsrs-004multiplestoragedevicestablemetadata)
    * 5.1.7 [RQ.SRS-004.MultipleStorageDevices.Queries](#rqsrs-004multiplestoragedevicesqueries)
    * 5.1.8 [RQ.SRS-004.BackgroundMergeProcess.MergingParts](#rqsrs-004backgroundmergeprocessmergingparts)
    * 5.1.9 [RQ.SRS-004.BackgroundMergeProcess.MergingParts.MovesAgainstStoragePolicy](#rqsrs-004backgroundmergeprocessmergingpartsmovesagainststoragepolicy)
    * 5.1.10 [RQ.SRS-004.BackgroundMergeProcess.MergingParts.FromMultipleVolumes](#rqsrs-004backgroundmergeprocessmergingpartsfrommultiplevolumes)
    * 5.1.11 [RQ.SRS-004.BackgroundMergeProcess.FaultTolerance.DataCorruption](#rqsrs-004backgroundmergeprocessfaulttolerancedatacorruption)
    * 5.1.12 [RQ.SRS-004.BackgroundMergeProcess.FaultTolerance.Restart](#rqsrs-004backgroundmergeprocessfaulttolerancerestart)
    * 5.1.13 [RQ.SRS-004.BackgroundMergeProcess.FaultTolerance.NoSpace](#rqsrs-004backgroundmergeprocessfaulttolerancenospace)
    * 5.1.14 [RQ.SRS-004.BackgroundMergeProcess.CheckStoragePolicy](#rqsrs-004backgroundmergeprocesscheckstoragepolicy)
    * 5.1.15 [RQ.SRS-004.BackgroundMergeProcess.ManualTrigger](#rqsrs-004backgroundmergeprocessmanualtrigger)
    * 5.1.16 [RQ.SRS-004.AddingMoreStorageDevices](#rqsrs-004addingmorestoragedevices)
    * 5.1.17 [RQ.SRS-004.Configuration.Changes.Restart](#rqsrs-004configurationchangesrestart)
    * 5.1.18 [RQ.SRS-004.Configuration.Changes.NoRestart.Warning](#rqsrs-004configurationchangesnorestartwarning)
    * 5.1.19 [RQ.SRS-004.Configuration.Changes.NoRestart.AddingNewDisks](#rqsrs-004configurationchangesnorestartaddingnewdisks)
    * 5.1.20 [RQ.SRS-004.Configuration.Changes.NoRestart.AddingNewVolumes](#rqsrs-004configurationchangesnorestartaddingnewvolumes)
    * 5.1.21 [RQ.SRS-004.Configuration.Changes.NoRestart.NewPolicies](#rqsrs-004configurationchangesnorestartnewpolicies)
    * 5.1.22 [RQ.SRS-004.Configuration.Changes.NoRestart.ChangeInNumericalValues](#rqsrs-004configurationchangesnorestartchangeinnumericalvalues)
    * 5.1.23 [RQ.SRS-004.DataMovement.Locking](#rqsrs-004datamovementlocking)
    * 5.1.24 [RQ.SRS-004.MovingDataBetweenStorageDevices.FaultTolerant](#rqsrs-004movingdatabetweenstoragedevicesfaulttolerant)
    * 5.1.25 [RQ.SRS-004.MovingDataBetweenStorageDevices.Manual](#rqsrs-004movingdatabetweenstoragedevicesmanual)
    * 5.1.26 [RQ.SRS-004.MovingDataBetweenStorageDevices.Automatic](#rqsrs-004movingdatabetweenstoragedevicesautomatic)
    * 5.1.27 [RQ.SRS-004.Configuration.Startup](#rqsrs-004configurationstartup)
    * 5.1.28 [RQ.SRS-004.Configuration.DefiningMultipleDisks](#rqsrs-004configurationdefiningmultipledisks)
    * 5.1.29 [RQ.SRS-004.Configuration.DefiningMultipleDisks.DefaultDisk](#rqsrs-004configurationdefiningmultipledisksdefaultdisk)
    * 5.1.30 [RQ.SRS-004.StoragePolicy](#rqsrs-004storagepolicy)
    * 5.1.31 [RQ.SRS-004.StoragePolicy.Multiple](#rqsrs-004storagepolicymultiple)
    * 5.1.32 [RQ.SRS-004.StoragePolicy.NoEffectOnQueries](#rqsrs-004storagepolicynoeffectonqueries)
    * 5.1.33 [RQ.SRS-004.StoragePolicy.Assignment](#rqsrs-004storagepolicyassignment)
    * 5.1.34 [RQ.SRS-004.StoragePolicy.Rules.RoundRobinDistribution](#rqsrs-004storagepolicyrulesroundrobindistribution)
    * 5.1.35 [RQ.SRS-004.StoragePolicy.Rules.MoveData.FreeSpace](#rqsrs-004storagepolicyrulesmovedatafreespace)
    * 5.1.36 [RQ.SRS-004.StoragePolicy.Rules.MoveData.MaxPartSize](#rqsrs-004storagepolicyrulesmovedatamaxpartsize)
    * 5.1.37 [RQ.SRS-004.StoragePolicy.Enforcement.INSERT](#rqsrs-004storagepolicyenforcementinsert)
    * 5.1.38 [RQ.SRS-004.StoragePolicy.Enforcement.Background](#rqsrs-004storagepolicyenforcementbackground)
    * 5.1.39 [RQ.SRS-004.StoragePolicy.Introspection](#rqsrs-004storagepolicyintrospection)
    * 5.1.40 [RQ.SRS-004.SQLStatement.MoveTablePartitions](#rqsrs-004sqlstatementmovetablepartitions)
    * 5.1.41 [RQ.SRS-004.StoragePolicy.ReplicatedTable.DownloadedPartPlacement](#rqsrs-004storagepolicyreplicatedtabledownloadedpartplacement)
    * 5.1.42 [RQ.SRS-004.TTLExpressions.ReplicatedTable.DownloadedPartPlacement](#rqsrs-004ttlexpressionsreplicatedtabledownloadedpartplacement)
    * 5.1.43 [RQ.SRS-004.TTLExpressions.Compatibility](#rqsrs-004ttlexpressionscompatibility)
    * 5.1.44 [RQ.SRS-004.TTLExpressions.Compatibility.DefaultDelete](#rqsrs-004ttlexpressionscompatibilitydefaultdelete)
    * 5.1.45 [RQ.SRS-004.TTLExpressionsForDataRelocation](#rqsrs-004ttlexpressionsfordatarelocation)
    * 5.1.46 [RQ.SRS-004.TTLExpressions.MaterializeTTL](#rqsrs-004ttlexpressionsmaterializettl)
  * 5.2 [Specific](#specific)
    * 5.2.1 [RQ.SRS-004.Configuration.MultipleDisksDefinition.Syntax](#rqsrs-004configurationmultipledisksdefinitionsyntax)
    * 5.2.2 [RQ.SRS-004.AutomaticPartMovementInTheBackground](#rqsrs-004automaticpartmovementinthebackground)
    * 5.2.3 [RQ.SRS-004.AutomaticPartMovementInTheBackground.NoEffectOnQuerying](#rqsrs-004automaticpartmovementinthebackgroundnoeffectonquerying)
    * 5.2.4 [RQ.SRS-004.Configuration.StorageConfiguration.MoveFactor](#rqsrs-004configurationstorageconfigurationmovefactor)
    * 5.2.5 [RQ.SRS-004.Configuration.StorageConfiguration.MoveFactor.DefaultValue](#rqsrs-004configurationstorageconfigurationmovefactordefaultvalue)
    * 5.2.6 [RQ.SRS-004.Configuration.StorageConfiguration.MoveFactor.Range](#rqsrs-004configurationstorageconfigurationmovefactorrange)
    * 5.2.7 [RQ.SRS-004.Configuration.MultipleDisksDefinition.Syntax.Disk.Options](#rqsrs-004configurationmultipledisksdefinitionsyntaxdiskoptions)
    * 5.2.8 [RQ.SRS-004.Configuration.MultipleDisksDefinition.Syntax.Disk.Options.EitherBytesOrRatio](#rqsrs-004configurationmultipledisksdefinitionsyntaxdiskoptionseitherbytesorratio)
    * 5.2.9 [RQ.SRS-004.Configuration.MultipleDisksDefinition.Syntax.Disk.Options.NoBytesOrRatio](#rqsrs-004configurationmultipledisksdefinitionsyntaxdiskoptionsnobytesorratio)
    * 5.2.10 [RQ.SRS-004.Configuration.Disks.Reading](#rqsrs-004configurationdisksreading)
    * 5.2.11 [RQ.SRS-004.Configuration.Disks.DetachedParts.Reading](#rqsrs-004configurationdisksdetachedpartsreading)
    * 5.2.12 [RQ.SRS-004.MovingDataBetweenStorageDevices.Manual.WithDowntime](#rqsrs-004movingdatabetweenstoragedevicesmanualwithdowntime)
    * 5.2.13 [RQ.SRS-004.MovingDataBetweenStorageDevices.Manual.NoDowntime](#rqsrs-004movingdatabetweenstoragedevicesmanualnodowntime)
    * 5.2.14 [RQ.SRS-004.StoragePolicy.Syntax](#rqsrs-004storagepolicysyntax)
    * 5.2.15 [RQ.SRS-004.StoragePolicy.Reading](#rqsrs-004storagepolicyreading)
    * 5.2.16 [RQ.SRS-004.StoragePolicy.Syntax.Volume.Options](#rqsrs-004storagepolicysyntaxvolumeoptions)
    * 5.2.17 [RQ.SRS-004.StoragePolicy.Syntax.Volume.Options.EitherBytesOrRatio](#rqsrs-004storagepolicysyntaxvolumeoptionseitherbytesorratio)
    * 5.2.18 [RQ.SRS-004.StoragePolicy.RuleMatchOrder](#rqsrs-004storagepolicyrulematchorder)
    * 5.2.19 [RQ.SRS-004.StoragePolicy.AddingToTable.CreateTable](#rqsrs-004storagepolicyaddingtotablecreatetable)
    * 5.2.20 [RQ.SRS-004.Volume.StoragePolicy.AddingToTable.AlterTable](#rqsrs-004volumestoragepolicyaddingtotablealtertable)
    * 5.2.21 [RQ.SRS-004.StoragePolicy.Application.BackgroundMerge](#rqsrs-004storagepolicyapplicationbackgroundmerge)
    * 5.2.22 [RQ.SRS-004.TTLExpressions.RuleNotSatisfied](#rqsrs-004ttlexpressionsrulenotsatisfied)
    * 5.2.23 [RQ.SRS-004.TTLExpressions.Evaluation](#rqsrs-004ttlexpressionsevaluation)
    * 5.2.24 [RQ.SRS-004.TTLExpressions.Selection](#rqsrs-004ttlexpressionsselection)
    * 5.2.25 [RQ.SRS-004.TTLExpressions.Syntax](#rqsrs-004ttlexpressionssyntax)
    * 5.2.26 [RQ.SRS-004.TTLExpressions.MultipleColumns](#rqsrs-004ttlexpressionsmultiplecolumns)
    * 5.2.27 [RQ.SRS-004.TTLExpressions.Alter.DropColumn](#rqsrs-004ttlexpressionsalterdropcolumn)
    * 5.2.28 [RQ.SRS-004.TTLExpressions.Alter.AddColumn](#rqsrs-004ttlexpressionsalteraddcolumn)
    * 5.2.29 [RQ.SRS-004.TTLExpressions.Alter.CommentColumn](#rqsrs-004ttlexpressionsaltercommentcolumn)
    * 5.2.30 [RQ.SRS-004.TTLExpressions.Alter.ClearColumn](#rqsrs-004ttlexpressionsalterclearcolumn)
    * 5.2.31 [RQ.SRS-004.TTLExpressions.Alter.ModifyColumn](#rqsrs-004ttlexpressionsaltermodifycolumn)
    * 5.2.32 [RQ.SRS-004.TTLExpressions.Mutations.Update](#rqsrs-004ttlexpressionsmutationsupdate)
    * 5.2.33 [RQ.SRS-004.TTLExpressions.Mutations.Delete](#rqsrs-004ttlexpressionsmutationsdelete)
    * 5.2.34 [RQ.SRS-004.TTLExpressions.Application.NoEffectOnQuerying](#rqsrs-004ttlexpressionsapplicationnoeffectonquerying)
    * 5.2.35 [RQ.SRS-004.TTLExpressions.FaultTolerance.DataCorruption](#rqsrs-004ttlexpressionsfaulttolerancedatacorruption)
    * 5.2.36 [RQ.SRS-004.TTLExpressions.FaultTolerance.Restart](#rqsrs-004ttlexpressionsfaulttolerancerestart)
    * 5.2.37 [RQ.SRS-004.TTLExpressions.FaultTolerance.NoSpace](#rqsrs-004ttlexpressionsfaulttolerancenospace)
    * 5.2.38 [RQ.SRS-004.TTLExpressions.AddingToTable.CreateTable](#rqsrs-004ttlexpressionsaddingtotablecreatetable)
    * 5.2.39 [RQ.SRS-004.TTLExpressions.AddingToTable.AlterTable](#rqsrs-004ttlexpressionsaddingtotablealtertable)
    * 5.2.40 [RQ.SRS-004.TTLExpressions.AddingToTable.AlterTable.ReplaceExisting](#rqsrs-004ttlexpressionsaddingtotablealtertablereplaceexisting)
* 6 [References](#references)

## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a Gitlab repository.

All the updates are tracked using the [Git]'s revision history.

* Gitlab repository: https://gitlab.com/altinity-qa/documents/qa-srs004-clickhouse-tiered-storage/blob/master/QA_SRS004_ClickHouse_Tiered_Storage.md 
* Revision history: https://gitlab.com/altinity-qa/documents/qa-srs004-clickhouse-tiered-storage/commits/master/QA_SRS004_ClickHouse_Tiered_Storage.md

## Introduction

Fast and capable storage is traditionally the most important part in DBMS and
[ClickHouse] is not an exception here. Though optimized for cheap spinning disk arrays, 
it performs best when modern NVMe SSDs are used. 
High performance storage is expensive, so users are often looking for a compromise.
They require frequently accessed (“hot”) data to be stored on the fast storage, 
and rarely accessed (“cold”) data to be moved to the slow storage.

[ClickHouse] currently does not allow to store data at multiple storage devices 
within a single server. The purpose of this project is to add multiple storage capabilities,
and enable tiered storage and extensible storage scenarios.

## Terminology

* **Part** - 
  atomic data part from [ClickHouse] prospective, produced either by insert or merge process.
  Stored as a separate directory at the file system.

* **Default disk** -
  the one specified in current ClickHouse configuration, usually: `<path>/var/lib/clickhouse</path>`

* **Disk** - mounted storage device.

* **JBOD** - Just a Bunch of Disks.

* **Volume** - one or multiple disks, combined together as a JBOD array. 

* **Tier** - volume with specific latency of throughput properties (e.g. SDD or HDD).

## TTL Expressions for Data Relocation

The TTL expressions are already available to force the deletion of data after an interval.
When the TTL expires it triggers a background merge that drops data that meets the TTL expression.
We can extend this capability to move data.  Let’s assume the following storage configuration. 

```xml
<storage_configuration>
    <disks>
        <!--default path maps to <path>/var/lib/clickhouse</path> in the main config file -->
        <default> <!-- SSD --> 
            <keep_free_space_ratio>0.1</keep_free_space_ratio>
        </default>    
        <disk_1> <!-- HDD 10TB -->
            <keep_free_space_ratio>0.1</keep_free_space_ratio>
            <path>/mnt/ext1/</path>
        </disk_1>    
        <disk_2> <!-- HDD 10TB -->
            <keep_free_space_ratio>0.1</keep_free_space_ratio>
            <path>/mnt/ext2/</path>
        </disk_2>    
        <disk_3> <!-- HDD 10TB -->
            <keep_free_space_ratio>0.1</keep_free_space_ratio>
            <path>/mnt/ext3/</path>
        </disk_3>    
  </disks>
</storage_configuration>
```

Now we can move the table data across disks using extended TTL syntax like the following example. 

```sql
CREATE TABLE ... 
TTL date + interval 7 days TO DISK 'disk_2', 
    date + interval 30 days TO DISK 'disk_3',
    date + interval 180 days DELETE
```

The target can also be `VOLUME` once that is implemented in ClickHouse. 
We will initially target `DISK`. 
For backward compatibility with existing TTL syntax, if no disk is specified, 
it defaults to `DELETE`. 

TTL expressions are just that -- SQL expressions that can refer 
to columns in the table. 

A more complex example that uses a TTL value embedded in the 
table row to control movement is presented below.  

```sql
CREATE TABLE foo
(
    `date` Date,
    `ttl_days` UInt16,
    `value` String
)
ENGINE = MergeTree
PARTITION BY (date, ttl_days)
ORDER BY (date, value)
TTL date + INTERVAL ttl_days DAY TO DISK 'disk_2',
    date + INTERVAL (ttl_days * 4) DAY TO DISK 'disk_3',
    date + INTERVAL (ttl_days * 24) DAY DELETE
```

Assuming the `ttl_days` has a value of seven, 
the effect of these expressions is similar to the 
first example using static interval values. 

## Requirements

### General

#### RQ.SRS-004.TieredStorage
version: 1.0

[ClickHouse] SHALL support tiered storage.

#### RQ.SRS-004.MultipleStorageDevices
version: 1.0

[ClickHouse] SHALL support storing data to multiple storage devices.

#### RQ.SRS-004.TableDefinition.NoChangesForQuerying
version: 1.0

[ClickHouse] SHALL require no changes to query statements 
when querying data from a table that supports multiple storage devices. 

#### RQ.SRS-004.TableDefinition.ChangesForStoragePolicyOrTTLExpressions
version: 1.0

[ClickHouse] table definition SHALL need modification only if storage policy or 
TTL rules are used, whereupon [ClickHouse] automatically places data on different disks/volumes.

#### RQ.SRS-004.MultipleStorageDevices.Querying
version: 1.0

[ClickHouse] SHALL support querying data stored in multiple storage devices.

#### RQ.SRS-004.MultipleStorageDevices.TableMetadata
version: 1.0

[ClickHouse] SHALL store table metadata at the default disk.

#### RQ.SRS-004.MultipleStorageDevices.Queries
version: 1.0

The only thing that affects queries is data location. 
[ClickHouse] SHALL understand multiple disks and 
read information about parts from the multiple disks at startup.

#### RQ.SRS-004.BackgroundMergeProcess.MergingParts
version: 1.0

[ClickHouse] background merge process SHALL merge parts from one disk 
to another, or initiate special type of merge that moves 
parts without any extra processing (MOVE_PARTS) if needed.

#### RQ.SRS-004.BackgroundMergeProcess.MergingParts.MovesAgainstStoragePolicy
version: 1.0

[ClickHouse] SHALL not allow the background merge process to move data
against the volume order defined by the storage policy.

#### RQ.SRS-004.BackgroundMergeProcess.MergingParts.FromMultipleVolumes
version: 1.0

[Clickhouse] SHALL use the volume with lowest priority (coldest data storage)
when merging parts from multiple volumes. 

#### RQ.SRS-004.BackgroundMergeProcess.FaultTolerance.DataCorruption
version: 1.0

[ClickHouse] SHALL be able to recover if data corruption occurs
during the background merge process when writing new part
to the destination disk.

#### RQ.SRS-004.BackgroundMergeProcess.FaultTolerance.Restart
version: 1.0

[ClickHouse] SHALL be able to recover if an abrupt restart
of the server occurs in the middle of the background merge
process when it writes new part to the destination disk.

#### RQ.SRS-004.BackgroundMergeProcess.FaultTolerance.NoSpace
version: 1.0

[ClickHouse] SHALL not merge parts if the resulting part's destination disk
has no space. The merge SHALL fail and a warning SHALL be printed to the log.

#### RQ.SRS-004.BackgroundMergeProcess.CheckStoragePolicy
version: 1.0

When storage policy is used, [ClickHouse] SHALL check part size and available disk space 
during periodic merge operations, and schedule move operations if needed.

#### RQ.SRS-004.BackgroundMergeProcess.ManualTrigger
version: 1.0

[ClickHouse] SHALL allow merge process to be explicitly triggered using 
`OPTIMIZE TABLE` or `OPTIMIZE TABLE PARTITION` statements.

#### RQ.SRS-004.AddingMoreStorageDevices
version: 1.0

[ClickHouse] SHALL support adding more storage devices to the existing [ClickHouse] server.

#### RQ.SRS-004.Configuration.Changes.Restart
version: 1.0

[ClickHouse] server SHALL need to be restarted when storage device configuration changes
except some special cases.

#### RQ.SRS-004.Configuration.Changes.NoRestart.Warning
version: 1.0

[ClickHouse] server SHALL ignore the config changes that cannot be applied 
without a restart and a warning SHALL be written to the log.

#### RQ.SRS-004.Configuration.Changes.NoRestart.AddingNewDisks
version: 1.0

[ClickHouse] server SHALL not require restart when new disks are added to the storage
configuration.

#### RQ.SRS-004.Configuration.Changes.NoRestart.AddingNewVolumes
version: 1.0

[ClickHouse] server SHALL not require restart when new volumes are added to the storage
configuration.

#### RQ.SRS-004.Configuration.Changes.NoRestart.NewPolicies
version: 1.0

[ClickHouse] server SHALL not require restart when new policies are added to the storage
configuration.

#### RQ.SRS-004.Configuration.Changes.NoRestart.ChangeInNumericalValues
version: 1.0

[ClickHouse] server SHALL not require restart when numerical value changes are added to the storage
configuration.

#### RQ.SRS-004.DataMovement.Locking
version: 1.0

[ClickHouse] SHALL not use locking of any kind for `INSERT` and query operations when 
parts are moved between disks in the background.

#### RQ.SRS-004.MovingDataBetweenStorageDevices.FaultTolerant
version: 1.0

[ClickHouse] SHALL ensure that all data moves are fault-tolerant.

#### RQ.SRS-004.MovingDataBetweenStorageDevices.Manual
version: 1.0

[ClickHouse] SHALL support mechanism to manually move data between different storage devices.

#### RQ.SRS-004.MovingDataBetweenStorageDevices.Automatic
version: 1.0

[ClickHouse] SHALL support mechanism to move data between different storage devices based on a rule.

#### RQ.SRS-004.Configuration.Startup
version: 1.0

[ClickHouse] SHALL respect multi-volume configuration automatically during startup.

#### RQ.SRS-004.Configuration.DefiningMultipleDisks
version: 1.0

[ClickHouse] SHALL support a configuration section for defining multiple disks for a single [ClickHouse] server.
 
#### RQ.SRS-004.Configuration.DefiningMultipleDisks.DefaultDisk
version: 1.0

[ClickHouse] SHALL support defining a default disk in the configuration section that defines multiple disks.

#### RQ.SRS-004.StoragePolicy
version: 1.0

[ClickHouse] SHALL support defining storage policies that [ClickHouse] server would use
in order to place data on different storage devices.

#### RQ.SRS-004.StoragePolicy.Multiple
version: 1.0

[ClickHouse] SHALL support multiple storage policies.

#### RQ.SRS-004.StoragePolicy.NoEffectOnQueries
version: 1.0

[ClickHouse] storage policy SHALL not affect queries.

#### RQ.SRS-004.StoragePolicy.Assignment
version: 1.0

[ClickHouse] SHALL support storage policy assignment on table basis
with `CREATE TABLE` or `ALTER TABLE` statement.

#### RQ.SRS-004.StoragePolicy.Rules.RoundRobinDistribution
version: 1.0

[ClickHouse] SHALL support storage policy that distributes data between 
set of disks in a volume (by parts) using round robin selection.

#### RQ.SRS-004.StoragePolicy.Rules.MoveData.FreeSpace
version: 1.0

[ClickHouse] SHALL support storage policy rule that specifies how to move data 
between available volumes based on free space available on the volume.

#### RQ.SRS-004.StoragePolicy.Rules.MoveData.MaxPartSize
version: 1.0

[ClickHouse] SHALL support storage policy rule that specifies how to move data 
between available volumes based on the maximum partition or part size.

#### RQ.SRS-004.StoragePolicy.Enforcement.INSERT
version: 1.0

[ClickHouse] SHALL enforce storage policy on `INSERT`.

#### RQ.SRS-004.StoragePolicy.Enforcement.Background
version: 1.0

[ClickHouse] SHALL enforce storage policy during background operations.

#### RQ.SRS-004.StoragePolicy.Introspection
version: 1.0

[ClickHouse] SHALL provide introspection information about application
of storage policy.

#### RQ.SRS-004.SQLStatement.MoveTablePartitions
version: 1.0

[ClickHouse] SHALL shall be extended to support new `ALTER TABLE MOVE`
SQL statement

```sql
    ALTER TABLE MOVE PARTITION|PART TO DISK|VOLUME
```

where `VOLUME` is allowed if storage policy is used.

#### RQ.SRS-004.StoragePolicy.ReplicatedTable.DownloadedPartPlacement
version: 1.0

[ClickHouse] SHALL place the parts downloaded from a replica
according to the storage policy specified for the table.

#### RQ.SRS-004.TTLExpressions.ReplicatedTable.DownloadedPartPlacement
version: 1.0

[ClickHouse] SHALL place the parts downloaded from a replica
according to the TTL expressions specified for the table.

#### RQ.SRS-004.TTLExpressions.Compatibility
version: 1.0

[ClickHouse] TTL expressions for data relocation SHALL
be compatible with the already available TTL expressions
to force deletion of data after an interval.

#### RQ.SRS-004.TTLExpressions.Compatibility.DefaultDelete
version: 1.0

For backward compatibility with existing TTL expressions
[ClickHouse] SHALL default to `DELETE` for all TTL expressions.

#### RQ.SRS-004.TTLExpressionsForDataRelocation
version: 1.0

[Clickhouse] SHALL support TTL (time to live) expressions for data relocation.

#### RQ.SRS-004.TTLExpressions.MaterializeTTL
version: 1.0

[ClickHouse] SHALL support materialization of TTL expressions using
```sql
ALTER TABLE [db.]table MATERIALIZE TTL [IN PARTITION] partition_name
```
command that SHALL force re-evaluation of all TTL expressions for the whole table
or only for a partition of the table if specified.

### Specific

#### RQ.SRS-004.Configuration.MultipleDisksDefinition.Syntax
version: 1.0

[ClickHouse] SHALL support configuring multiple disks using the following configuration file syntax

```xml
<path>/path/to/the/default/disk</path>
<storage_configuration>
    <move_factor>0.1</move_factor>
    <disks>
        <!--default path maps to <path>/var/lib/clickhouse/</path> in the main config file -->
        <default>
           <!-- optional, disk size -->
           <disk_space_bytes>1000000000</disk_space_bytes>  
           <!-- optional, desired free space -->
           <keep_free_space_bytes>0</keep_free_space_bytes> 
           <!-- optional, desired free ratio: used space / total space -->
           <keep_free_space_ratio>0</keep_free_space_ratio> 
        </default>    
        <disk_a> <!-- any name of the disk except default -->
            <keep_free_space_bytes>0</keep_free_space_bytes>
            <keep_free_space_ratio>0</keep_free_space_ratio>
            <path>/a/</path>
        </disk_a>    
        <disk_b>
            <keep_free_space_bytes>0</keep_free_space_bytes>
            <keep_free_space_ratio>0</keep_free_space_ratio>
            <path>/b/</path>
        </disk_b>  
        <disk_c>
            <keep_free_space_bytes>0</keep_free_space_bytes>
            <keep_free_space_ratio>0</keep_free_space_ratio>
            <path>/c/</path>
        </disk_c>  
  </disks>
</storage_configuration>
```

#### RQ.SRS-004.AutomaticPartMovementInTheBackground
version: 1.0

[ClickHouse] SHALL move parts between volumes in the background to free
space in the volumes that are specified from top to bottom.

#### RQ.SRS-004.AutomaticPartMovementInTheBackground.NoEffectOnQuerying
version: 1.0

[ClickHouse] SHALL implement background moves such that they have
no effect on querying data with data being available for querying at all times.

#### RQ.SRS-004.Configuration.StorageConfiguration.MoveFactor
version: 1.0

The `move_factor` option SHALL specify the amount of free space which
when exceeded causes data to be moved to the next volume, if exists.

#### RQ.SRS-004.Configuration.StorageConfiguration.MoveFactor.DefaultValue
version: 1.0

[ClickHouse] SHALL set the default value of `move_factor` to 0.1 if not specified.

#### RQ.SRS-004.Configuration.StorageConfiguration.MoveFactor.Range
version: 1.0

The `move_factor` SHALL have value range of 0 to 1.

#### RQ.SRS-004.Configuration.MultipleDisksDefinition.Syntax.Disk.Options
version: 1.0

[ClickHouse] SHALL support the following values as part of the `DISK`
description:

* **disk_space_bytes** - disk size in bytes
* **keep_free_space_bytes** - desired free space in bytes 
* **keep_free_space_ratio** - desired free ratio `used space / total space`
* **path** - path to disk

#### RQ.SRS-004.Configuration.MultipleDisksDefinition.Syntax.Disk.Options.EitherBytesOrRatio
version: 1.0

[ClickHouse] SHALL raise an exception if both `keep_free_space_bytes` and 
`keep_free_space_ratio` is specified for the same disk.

#### RQ.SRS-004.Configuration.MultipleDisksDefinition.Syntax.Disk.Options.NoBytesOrRatio
version: 1.0

[ClickHouse] SHALL use only `disk_space_bytes` if neither `keep_free_space_bytes`
or `keep_free_space_ratio` is specified.

#### RQ.SRS-004.Configuration.Disks.Reading
version: 1.0

[ClickHouse] SHALL support reading disk configuration using

```sql
SELECT * FROM system.disks
```

#### RQ.SRS-004.Configuration.Disks.DetachedParts.Reading
version: 1.0

[ClickHouse] SHALL support reading disk for the
detached parts from the `system.detached_parts` table.

```sql
SELECT disk FROM system.detached_parts
```

#### RQ.SRS-004.MovingDataBetweenStorageDevices.Manual.WithDowntime
version: 1.0

[ClickHouse] SHALL support manually moving data between storage devices **with
downtime** using the following procedure:

```sql
ALTER TABLE DETACH PARTITION|PART <name>
-- mv disk_a/.../detached/<name> disk_b/…/detached/<name>
ALTER TABLE ATTACH PARTITION|PART <name>
```

#### RQ.SRS-004.MovingDataBetweenStorageDevices.Manual.NoDowntime
version: 1.0

[ClickHouse] SHALL support manually moving data between storage devices **with no
downtime** using the following procedure:

```sql
ALTER TABLE MOVE PARTITION|PART <name> TO DISK|VOLUME <name>
ALTER TABLE OPTIMIZE PARTITION <name> TO DISK|VOLUME <name> [FINAL]
```
with an additional merge performed during the relocation if necessary.

#### RQ.SRS-004.StoragePolicy.Syntax
version: 1.0

[ClickHouse] SHALL support the following syntax to define storage policy

```xml
<storage_configuration>
    <!-- policies are used in order to configure JBOD and server level rules -->
    <!-- they are optional and not required unless JBOD and automatic rules are necessary -->
    <!-- volumes support 2 parameters: max_data_part_size_bytes, max_data_part_size_ratio -->
    
    <policies>
        <default> <!-- policy name, used to reference from the table definition -->
            <volumes>
              <vol1>
                <disk>default</disk>
                <max_data_part_size_bytes>10000000</max_data_part_size_bytes>
              </vol1>
              <vol2>
                <disk>disk_a</disk>
                <max_data_part_size_bytes>100000000</max_data_part_size_bytes>
              </vol2>
              <vol3>
                <disk>disk_b</disk>
                <disk>disk_c</disk> 
             </vol3>
           </volumes>
        <default>
</storage_configuration>
```

when `default` policy is not explicitly stated the following default policy
is used that is equal to the definition below

```xml
<default>
    <volumes>
       <disk>default</disk>
    </volumes>
</default>
```

#### RQ.SRS-004.StoragePolicy.Reading
version: 1.0

[ClickHouse] SHALL support reading storage policy using

```sql
SELECT * FROM system.storage_policies
```

#### RQ.SRS-004.StoragePolicy.Syntax.Volume.Options
version: 1.0

[ClickHouse] SHALL support the following values as part of `VOLUME`
description:

* **disk** - one or more disks to use
* **max_data_part_size_bytes** - maximum part size in bytes
* **max_data_part_size_ratio** - maximum part size ratio that is defined as
  `max_data_part_size > (sum_size * max_data_part_size_ratio / number_of_disks)`
  where `sum_size` is the total size of the space on all disks inside the volume
  and the `number_of_disks` is the number of disks inside the volume.

#### RQ.SRS-004.StoragePolicy.Syntax.Volume.Options.EitherBytesOrRatio
version: 1.0

[ClickHouse] SHALL raise an exception if both `max_data_part_size_bytes` and 
`max_data_part_size_ratio` is specified for the same volume.

#### RQ.SRS-004.StoragePolicy.RuleMatchOrder
version: 1.0

[ClickHouse] SHALL apply storage policy rules from top to bottom
and the first match SHALL be used.

#### RQ.SRS-004.StoragePolicy.AddingToTable.CreateTable
version: 1.0

[ClickHouse] SHALL support assigning storage policy
when creating a table with the `CREATE TABLE` command using the
`storage_policy_name` setting.

```sql
CREATE TABLE … SETTINGS storage_policy_name='policy2';
```

#### RQ.SRS-004.Volume.StoragePolicy.AddingToTable.AlterTable
version: 1.0

[ClickHouse] SHALL support assigning storage policy
to an already existing table using the `ALTER TABLE` command
only when new policy have all the disks from the previous policy,
otherwise an exception SHALL be raised.

```sql
ALTER TABLE … SETTINGS storage_policy_name='policy2';
```

#### RQ.SRS-004.StoragePolicy.Application.BackgroundMerge
version: 1.0

[ClickHouse] SHALL estimate the size of the new generated part that would 
comply with the `volume` storage policy. 
The storage policy is checked top to bottom against constraints of each
volume. 

If part size > `max_part_size_bytes` or part ratio > `max_part_size_ratio`
then the next `volume` is checked.

When a volume is considered, it then is checked against the constraints of the
disks that are part of the volume.

If no volume can be chosen then an exception SHALL be raised.

#### RQ.SRS-004.TTLExpressions.RuleNotSatisfied
version: 1.0

[ClickHouse] SHALL ignore any TTL expressions to move data if the TTL expression
or the TTL destination can't be satisfied. If the TTL destination can't be satisfied
then a warning message SHALL be written to the log.

#### RQ.SRS-004.TTLExpressions.Evaluation
version: 1.0

[ClickHouse] SHALL support only TTL expressions that evaluate to
`Date` or `DateTime` data type.

#### RQ.SRS-004.TTLExpressions.Selection
version: 1.0

[ClickHouse] TTL expressions SHALL be selected based on the length of the time interval
with shorter intervals being selected first.

#### RQ.SRS-004.TTLExpressions.Syntax
version: 1.0

[ClickHouse] SHALL support TTL expressions using the following syntax

```sql
TTL <expr> [TO DISK <name> | TO VOLUME <name> | DELETE]
```

where multiple comma can be used to separated TTL expressions.

#### RQ.SRS-004.TTLExpressions.MultipleColumns
version: 1.0

[ClickHouse] SHALL support TTL expressions that use multiple columns.

```sql
TTL d1 + d2 + INTERVAL 7 DAY TO DISK 'disk_2',
```

#### RQ.SRS-004.TTLExpressions.Alter.DropColumn
version: 1.0

[ClickHouse] SHALL raise an exception if a column that is used
inside a TTL expression is attempted to be dropped using the
`ALTER` `DROP COLUMN` statement.

#### RQ.SRS-004.TTLExpressions.Alter.AddColumn
version: 1.0

[ClickHouse] SHALL support adding a new column to a table
that has a TTL expression using the `ALTER` `ADD COLUMN` statement.

#### RQ.SRS-004.TTLExpressions.Alter.CommentColumn
version: 1.0

[ClickHouse] SHALL support adding a text comment to a column
that is used in a TTL expression using the `ALTER` `COMMENT COLUMN` 
statement.

#### RQ.SRS-004.TTLExpressions.Alter.ClearColumn
version: 1.0

[ClickHouse] SHALL support clearing a column that is used in a
TTL expression using the `ALTER` `CLEAR COLUMN` statement.

#### RQ.SRS-004.TTLExpressions.Alter.ModifyColumn
version: 1.0

[ClickHouse] SHALL support modifying type of a column that is used in
a TTL expression using the `ALTER` `CLEAR COLUMN` statement as long as
the TTL expression still evaluates to a `Date` or a `DateTime` type.

#### RQ.SRS-004.TTLExpressions.Mutations.Update
version: 1.0

[ClickHouse] SHALL support `ALTER` `UPDATE` mutation on a column that is 
used in a TTL expression and the TTL expression SHALL be recalculated.

#### RQ.SRS-004.TTLExpressions.Mutations.Delete
version: 1.0

[ClickHouse] SHALL support `ALTER` `DELETE` mutation on a column that is used
in a TTL expression.

#### RQ.SRS-004.TTLExpressions.Application.NoEffectOnQuerying
version: 1.0

[ClickHouse] SHALL implement TTL moves such that TTL moves have
no effect on querying data with data being available for querying at all times.

#### RQ.SRS-004.TTLExpressions.FaultTolerance.DataCorruption
version: 1.0

[ClickHouse] SHALL be able to recover if data corruption occurs
during the TTL move.

#### RQ.SRS-004.TTLExpressions.FaultTolerance.Restart
version: 1.0

[ClickHouse] SHALL be able to recover if an abrupt restart
of the server occurs in the middle of the TTL move.

#### RQ.SRS-004.TTLExpressions.FaultTolerance.NoSpace
version: 1.0

[ClickHouse] SHALL not perform TTL move if the destination disk 
has no free space. The TTL move SHALL be aborted and
a warning SHALL be written to the log file.

#### RQ.SRS-004.TTLExpressions.AddingToTable.CreateTable
version: 1.0

[ClickHouse] SHALL support adding TTL expressions for data relocation
when creating a table with the `CREATE TABLE` command.

```sql
CREATE TABLE ... 
TTL date + INTERVAL 7 DAY TO DISK 'disk_2', 
    date + INTERVAL 30 DAY TO DISK 'disk_3',
    date + INTERVAL 60 DAY TO VOLUME 'vol1',
    date + INTERVAL 180 DAY DELETE
```

#### RQ.SRS-004.TTLExpressions.AddingToTable.AlterTable
version: 1.0

[ClickHouse] SHALL support adding TTL expressions for data relocation
to an already existing table using the `ALTER TABLE` command.
For example,

```sql
ALTER TABLE MODIFY 
TTL date + INTERVAL 7 DAY TO DISK 'disk_2', 
    date + INTERVAL 30 DAY TO DISK 'disk_3',
    date + INTERVAL 180 DAY DELETE
```

#### RQ.SRS-004.TTLExpressions.AddingToTable.AlterTable.ReplaceExisting
version: 1.0

[ClickHouse] SHALL drop all existing TTL expression rules
when the `ALTER TABLE` command is used to add or update TTL expressions.

## References

* **ClickHouse:** https://clickhouse.clickhouse
* **Gitlab repository:** https://gitlab.com/altinity-qa/documents/qa-srs004-clickhouse-tiered-storage/blob/master/QA_SRS004_ClickHouse_Tiered_Storage.md
* **Revision history:** https://gitlab.com/altinity-qa/documents/qa-srs004-clickhouse-tiered-storage/commits/master/QA_SRS004_ClickHouse_Tiered_Storage.md
* **Git:** https://git-scm.com/

[ClickHouse]: https://clickhouse.clickhouse
[Gitlab repository]: https://gitlab.com/altinity-qa/documents/qa-srs004-clickhouse-tiered-storage/blob/master/QA_SRS004_ClickHouse_Tiered_Storage.md
[Revision history]: https://gitlab.com/altinity-qa/documents/qa-srs004-clickhouse-tiered-storage/commits/master/QA_SRS004_ClickHouse_Tiered_Storage.md
[Git]: https://git-scm.com/
""",
)
