# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.240109.1181209.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_038_DiskObjectStorageVFS_Replica_NoDataDuplication = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Replica.NoDataDuplication",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support VFS such that data is not\n"
        "duplicated in [S3] storage during any operations on replicated tables (ALTER,\n"
        "SELECT, INSERT, etc...).\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.1",
)

RQ_SRS_038_DiskObjectStorageVFS_Replica_Add = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Replica.Add",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support adding a replica of an existing replicated table\n"
        "with no changes to data in any tables on the other replicating instances.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.2",
)

RQ_SRS_038_DiskObjectStorageVFS_Replica_Remove = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Replica.Remove",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support removing a replicated table on a [ClickHouse] instance\n"
        "with no changes to data in any tables on the other replicating instances.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.3",
)

RQ_SRS_038_DiskObjectStorageVFS_Replica_Offline = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Replica.Offline",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support stopping and starting an instance of [ClickHouse]\n"
        "with no changes to data in replicated tables. If the table is altered while\n"
        "an instance is offline, [ClickHouse] SHALL update the table from [S3] when\n"
        "that instance restarts.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.4",
)

RQ_SRS_038_DiskObjectStorageVFS_Replica_Stale = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Replica.Stale",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("stale replica\n" "\n"),
    link=None,
    level=3,
    num="4.1.5",
)

RQ_SRS_038_DiskObjectStorageVFS_Settings_Disk = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Settings.Disk",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `<allow_vfs>` setting in the\n"
        "`<disks>` section of the config.xml file or an xml file in\n"
        "the config.d directory to configure the ReplicatedMergeTree engine globally.\n"
        "\n"
        "Example:\n"
        "\n"
        "```xml\n"
        "<yandex>\n"
        "  <storage_configuration>\n"
        "    <disks>\n"
        "      <external>\n"
        "        <allow_vfs>1</allow_vfs>\n"
        "      </external>\n"
        "  </storage_configuration>\n"
        "</yandex>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.2.1",
)

RQ_SRS_038_DiskObjectStorageVFS_Settings_ZeroCopyIncompatible = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Settings.ZeroCopyIncompatible",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if both `<allow_s3_zero_copy_replication>`\n"
        "and `<allow_vfs>` are enabled at the same time.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.2.2",
)

RQ_SRS_038_DiskObjectStorageVFS_Settings_Shared = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Settings.Shared",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL respect the following settings when`<allow_vfs>` is enabled.\n"
        "\n"
        "| Setting                                                   | Support |\n"
        "| --------------------------------------------------------- | ------- |\n"
        "| remote_fs_execute_merges_on_single_replica_time_threshold | yes     |\n"
        "| zero_copy_concurrent_part_removal_max_split_times         | yes     |\n"
        "| zero_copy_concurrent_part_removal_max_postpone_ratio      | yes     |\n"
        "| zero_copy_merge_mutation_min_parts_size_sleep_before_lock | yes     |\n"
        "| perform_ttl_move_on_insert                                | yes     |\n"
        "| ...                                                       | planned |\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.2.3",
)

RQ_SRS_038_DiskObjectStorageVFS_Integrity_VFSToggled = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Integrity.VFSToggled",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When the value of the `<allow_vfs>` parameter is changed\n"
        "from 0 to 1 or 1 to 0 and [ClickHouse] is restarted,\n"
        "[ClickHouse] SHALL ensure that data is still accessible.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.3.1",
)

RQ_SRS_038_DiskObjectStorageVFS_Integrity_Migration = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Integrity.Migration",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL provide commands to migrate table data between any pair of "replicated",\n'
        '"0-copy" and "vfs" table configurations.\n'
        "\n"
        "| From       | To         | Command |\n"
        "| ---------- | ---------- | ------- |\n"
        "| vfs        | replicated |         |\n"
        "| vfs        | 0-copy     |         |\n"
        "| 0-copy     | replicated |         |\n"
        "| 0-copy     | vfs        |         |\n"
        "| replicated | 0-copy     |         |\n"
        "| replicated | vfs        |         |\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.3.2",
)

RQ_SRS_038_DiskObjectStorageVFS_Integrity_TTLMove = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Integrity.TTLMove",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support TTL moves to other hard disks or [S3] disks when VFS\n"
        "is used with the MergeTree engine. When TTL moves are used, data will not be\n"
        "duplicated in [S3]. All objects in a table SHALL be accessible with no errors,\n"
        "even if they have been moved to a different disk.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.3.3",
)

RQ_SRS_038_DiskObjectStorageVFS_Integrity_TTLDelete = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Integrity.TTLDelete",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support TTL object deletion when VFS is used with the MergeTree engine.\n"
        "When objects are removed, all other objects SHALL be accessible with no errors.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.3.4",
)

RQ_SRS_038_DiskObjectStorageVFS_Integrity_Detach = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Integrity.Detach",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support detaching and attaching tables on VFS disks.\n"
        "Should the detached table on a replica become corrupted,\n"
        "[ClickHouse] SHALL ensure that other replicas are not affected.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.3.5",
)

RQ_SRS_038_DiskObjectStorageVFS_Integrity_Delete = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Integrity.Delete",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL ensure disused files in S3 are eventually removed when `<allow_vfs>` is enabled\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.3.6",
)

RQ_SRS_038_DiskObjectStorageVFS_System_ConnectionInterruption = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.System.ConnectionInterruption",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be robust against the following types of connection interruptions.\n"
        "\n"
        "| Interruption                    |\n"
        "| ------------------------------- |\n"
        "| Unstable connection             |\n"
        "| Unfinished API requests (stuck) |\n"
        "| Interrupted API requests        |\n"
        "| Slow connection                 |\n"
        "| Lost connection to Keeper       |\n"
        "| Lost connection to Replica      |\n"
        "| insert_keeper_fault_injection   |\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.4.1",
)

RQ_SRS_038_DiskObjectStorageVFS_System_ConnectionInterruption_FaultInjection = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.System.ConnectionInterruption.FaultInjection",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be robust against faults created by insert_keeper_fault_injection.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.4.2",
)

RQ_SRS_038_DiskObjectStorageVFS_System_AddKeeper = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.System.AddKeeper",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] Replicated tables SHALL continue to operate without issue when a keeper node is added to the cluster.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.4.3",
)

RQ_SRS_038_DiskObjectStorageVFS_System_RemoveKeeper = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.System.RemoveKeeper",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] Replicated tables SHALL continue to operate without issue when a keeper node is removed from the cluster.\n"
        "This does not apply if there is only one keeper node.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.4.4",
)

RQ_SRS_038_DiskObjectStorageVFS_System_Compact_Wide = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.System.Compact_Wide",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [S3] external storage of data parts as Wide parts,\n"
        "Compact parts, or a combination of both types. The user may view the full storage\n"
        "of data parts in the system.parts table.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.4.5",
)

RQ_SRS_038_DiskObjectStorageVFS_Parts_Fetch = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Parts.Fetch",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support fetching a new part from another replica.\n" "\n"
    ),
    link=None,
    level=3,
    num="4.5.1",
)

RQ_SRS_038_DiskObjectStorageVFS_Parts_Optimize = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Parts.Optimize",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support manually triggering merges with `OPTIMIZE [FINAL]`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.5.2",
)

RQ_SRS_038_DiskObjectStorageVFS_Parts_BackgroundCollapse = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Parts.BackgroundCollapse",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support collapsing MergeTree engines and their replicated versions.\n"
        "\n"
        "| Collapsing Engines                   |\n"
        "| ------------------------------------ |\n"
        "| (Replicated)CollapsingMergeTree      |\n"
        "| (Replicated)ReplacingMergeTree       |\n"
        "| (Replicated)VersionedCollapsingMerge |\n"
        "| (Replicated)SummingMergeTree         |\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.5.3",
)

RQ_SRS_038_DiskObjectStorageVFS_Parts_Manipulation = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Parts.Manipulation",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "| Part Manipulations        |\n"
        "| ------------------------- |\n"
        "| DETACH PARTITION/PART     |\n"
        "| DROP PARTITION/PART       |\n"
        "| ATTACH PARTITION/PART     |\n"
        "| ATTACH PARTITION FROM     |\n"
        "| REPLACE PARTITION         |\n"
        "| MOVE PARTITION TO TABLE   |\n"
        "| CLEAR COLUMN IN PARTITION |\n"
        "| CLEAR INDEX IN PARTITION  |\n"
        "| FREEZE PARTITION          |\n"
        "| UNFREEZE PARTITION        |\n"
        "| FETCH PARTITION/PART      |\n"
        "| MOVE PARTITION/PART       |\n"
        "| UPDATE IN PARTITION       |\n"
        "| DELETE IN PARTITION       |\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.5.4",
)

RQ_SRS_038_DiskObjectStorageVFS_Alter_Index = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Alter.Index",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "| Index Operations  |\n"
        "| ----------------- |\n"
        "| ADD INDEX         |\n"
        "| DROP INDEX        |\n"
        "| MATERIALIZE INDEX |\n"
        "| CLEAR INDEX       |\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.1",
)

RQ_SRS_038_DiskObjectStorageVFS_Alter_OrderBy = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Alter.OrderBy",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support MODIFY ORDER BY.\n" "\n"),
    link=None,
    level=3,
    num="4.6.2",
)

RQ_SRS_038_DiskObjectStorageVFS_Alter_SampleBy = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Alter.SampleBy",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support MODIFY SAMPLE BY.\n" "\n"),
    link=None,
    level=3,
    num="4.6.3",
)

RQ_SRS_038_DiskObjectStorageVFS_Alter_Projections = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Alter.Projections",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "| Projection Operations  |\n"
        "| ---------------------- |\n"
        "| ADD PROJECTION         |\n"
        "| DROP PROJECTION        |\n"
        "| MATERIALIZE PROJECTION |\n"
        "| CLEAR PROJECTION       |\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.4",
)

RQ_SRS_038_DiskObjectStorageVFS_Alter_Column = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Alter.Column",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "| Column Operation     | Description                                                       |\n"
        "| -------------------- | ----------------------------------------------------------------- |\n"
        "| ADD COLUMN           | Adds a new column to the table.                                   |\n"
        "| DROP COLUMN          | Deletes the column.                                               |\n"
        "| RENAME COLUMN        | Renames an existing column.                                       |\n"
        "| CLEAR COLUMN         | Resets column values.                                             |\n"
        "| COMMENT COLUMN       | Adds a text comment to the column.                                |\n"
        "| MODIFY COLUMN        | Changes column's type, default expression and TTL.                |\n"
        "| MODIFY COLUMN REMOVE | Removes one of the column properties.                             |\n"
        "| MATERIALIZE COLUMN   | Materializes the column in the parts where the column is missing. |\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.5",
)

RQ_SRS_038_DiskObjectStorageVFS_Alter_Update = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Alter.Update",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "| Operation    |\n"
        "| ------------ |\n"
        "| DELETE       |\n"
        "| UPDATE       |\n"
        "| ALTER DELETE |\n"
        "| ALTER UPDATE |\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.6",
)

RQ_SRS_038_DiskObjectStorageVFS_StoragePolicy = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.StoragePolicy",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the following storage policy arrangements with VFS\n"
        "\n"
        "| Policy                             |\n"
        "| ---------------------------------- |\n"
        "| Tiered storage                     |\n"
        "| Single or multiple S3 buckets      |\n"
        "| Single or multiple object storages |\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.8.1",
)

RQ_SRS_038_DiskObjectStorageVFS_Combinatoric = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Combinatoric",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[Clickhouse]  SHALL support any sequence of [supported operations](#supported-operations)\n"
        "on a table configured with any combination of\n"
        "[supported table combinations](#supported-table-configurations).\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.9.3",
)

RQ_SRS_038_DiskObjectStorageVFS_Combinatoric_Insert = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Combinatoric.Insert",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[Clickhouse]  SHALL support insert operations on a table configured with\n"
        "any combination of  [supported table combinations](#supported-table-configurations).\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.9.4",
)

RQ_SRS_038_DiskObjectStorageVFS_Performance = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Performance",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[Clickhouse] DiskObjectStorageVFS shares performance requirements with\n"
        "[RQ.SRS-015.S3.Performance](https://github.com/Altinity/clickhouse-regression/blob/main/s3/requirements/requirements.md#performance)\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.10.1",
)

RQ_SRS_038_DiskObjectStorageVFS_Providers_Configuration = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Providers.Configuration",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support configuration of object storage disks from a\n"
        "supported provider with syntax similar to the following:\n"
        "\n"
        "``` xml\n"
        "<yandex>\n"
        "  <storage_configuration>\n"
        "    <disks>\n"
        "      <minio>\n"
        "        <type>s3</type>\n"
        "        <endpoint>http://minio:9000/my-bucket/object-key/</endpoint>\n"
        "        <access_key_id>*****</access_key_id>\n"
        "        <secret_access_key>*****</secret_access_key>\n"
        "      </minio>\n"
        "    </disks>\n"
        "...\n"
        "</yandex>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.11.1",
)

RQ_SRS_038_DiskObjectStorageVFS_Providers_AWS = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Providers.AWS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support VFS on object storage using [AWS S3].\n" "\n"
    ),
    link=None,
    level=3,
    num="4.11.2",
)

RQ_SRS_038_DiskObjectStorageVFS_Providers_MinIO = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Providers.MinIO",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support VFS on object storage using [MinIO].\n" "\n"
    ),
    link=None,
    level=3,
    num="4.11.3",
)

RQ_SRS_038_DiskObjectStorageVFS_Providers_GCS = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Providers.GCS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support VFS on object storage using [Google Cloud Storage].\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.11.4",
)

SRS_038_ClickHouse_Disk_Object_Storage_VFS = Specification(
    name="SRS-038 ClickHouse Disk Object Storage VFS",
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
        Heading(name="Revision History", level=1, num="1"),
        Heading(name="Introduction", level=1, num="2"),
        Heading(name="Terminology", level=1, num="3"),
        Heading(name="Requirements", level=1, num="4"),
        Heading(name="Replicas", level=2, num="4.1"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Replica.NoDataDuplication",
            level=3,
            num="4.1.1",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Replica.Add", level=3, num="4.1.2"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Replica.Remove", level=3, num="4.1.3"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Replica.Offline", level=3, num="4.1.4"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Replica.Stale", level=3, num="4.1.5"
        ),
        Heading(name="Settings", level=2, num="4.2"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Settings.Disk", level=3, num="4.2.1"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Settings.ZeroCopyIncompatible",
            level=3,
            num="4.2.2",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Settings.Shared", level=3, num="4.2.3"
        ),
        Heading(name="Data Integrity", level=2, num="4.3"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Integrity.VFSToggled",
            level=3,
            num="4.3.1",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Integrity.Migration",
            level=3,
            num="4.3.2",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Integrity.TTLMove",
            level=3,
            num="4.3.3",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Integrity.TTLDelete",
            level=3,
            num="4.3.4",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Integrity.Detach",
            level=3,
            num="4.3.5",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Integrity.Delete",
            level=3,
            num="4.3.6",
        ),
        Heading(name="System", level=2, num="4.4"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.System.ConnectionInterruption",
            level=3,
            num="4.4.1",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.System.ConnectionInterruption.FaultInjection",
            level=3,
            num="4.4.2",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.System.AddKeeper",
            level=3,
            num="4.4.3",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.System.RemoveKeeper",
            level=3,
            num="4.4.4",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.System.Compact_Wide",
            level=3,
            num="4.4.5",
        ),
        Heading(name="Parts", level=2, num="4.5"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Parts.Fetch", level=3, num="4.5.1"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Parts.Optimize", level=3, num="4.5.2"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Parts.BackgroundCollapse",
            level=3,
            num="4.5.3",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Parts.Manipulation",
            level=3,
            num="4.5.4",
        ),
        Heading(name="Alter", level=2, num="4.6"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Alter.Index", level=3, num="4.6.1"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Alter.OrderBy", level=3, num="4.6.2"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Alter.SampleBy", level=3, num="4.6.3"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Alter.Projections",
            level=3,
            num="4.6.4",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Alter.Column", level=3, num="4.6.5"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Alter.Update", level=3, num="4.6.6"
        ),
        Heading(name="Table", level=2, num="4.7"),
        Heading(name="StoragePolicy", level=2, num="4.8"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.StoragePolicy", level=3, num="4.8.1"
        ),
        Heading(name="Combinatoric", level=2, num="4.9"),
        Heading(name="Supported Table Configurations", level=3, num="4.9.1"),
        Heading(name="Supported Operations", level=3, num="4.9.2"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Combinatoric", level=3, num="4.9.3"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Combinatoric.Insert",
            level=3,
            num="4.9.4",
        ),
        Heading(name="Performance", level=2, num="4.10"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Performance", level=3, num="4.10.1"
        ),
        Heading(name="Object Storage Providers", level=2, num="4.11"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Providers.Configuration",
            level=3,
            num="4.11.1",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Providers.AWS", level=3, num="4.11.2"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Providers.MinIO",
            level=3,
            num="4.11.3",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Providers.GCS", level=3, num="4.11.4"
        ),
        Heading(name="References", level=1, num="5"),
    ),
    requirements=(
        RQ_SRS_038_DiskObjectStorageVFS_Replica_NoDataDuplication,
        RQ_SRS_038_DiskObjectStorageVFS_Replica_Add,
        RQ_SRS_038_DiskObjectStorageVFS_Replica_Remove,
        RQ_SRS_038_DiskObjectStorageVFS_Replica_Offline,
        RQ_SRS_038_DiskObjectStorageVFS_Replica_Stale,
        RQ_SRS_038_DiskObjectStorageVFS_Settings_Disk,
        RQ_SRS_038_DiskObjectStorageVFS_Settings_ZeroCopyIncompatible,
        RQ_SRS_038_DiskObjectStorageVFS_Settings_Shared,
        RQ_SRS_038_DiskObjectStorageVFS_Integrity_VFSToggled,
        RQ_SRS_038_DiskObjectStorageVFS_Integrity_Migration,
        RQ_SRS_038_DiskObjectStorageVFS_Integrity_TTLMove,
        RQ_SRS_038_DiskObjectStorageVFS_Integrity_TTLDelete,
        RQ_SRS_038_DiskObjectStorageVFS_Integrity_Detach,
        RQ_SRS_038_DiskObjectStorageVFS_Integrity_Delete,
        RQ_SRS_038_DiskObjectStorageVFS_System_ConnectionInterruption,
        RQ_SRS_038_DiskObjectStorageVFS_System_ConnectionInterruption_FaultInjection,
        RQ_SRS_038_DiskObjectStorageVFS_System_AddKeeper,
        RQ_SRS_038_DiskObjectStorageVFS_System_RemoveKeeper,
        RQ_SRS_038_DiskObjectStorageVFS_System_Compact_Wide,
        RQ_SRS_038_DiskObjectStorageVFS_Parts_Fetch,
        RQ_SRS_038_DiskObjectStorageVFS_Parts_Optimize,
        RQ_SRS_038_DiskObjectStorageVFS_Parts_BackgroundCollapse,
        RQ_SRS_038_DiskObjectStorageVFS_Parts_Manipulation,
        RQ_SRS_038_DiskObjectStorageVFS_Alter_Index,
        RQ_SRS_038_DiskObjectStorageVFS_Alter_OrderBy,
        RQ_SRS_038_DiskObjectStorageVFS_Alter_SampleBy,
        RQ_SRS_038_DiskObjectStorageVFS_Alter_Projections,
        RQ_SRS_038_DiskObjectStorageVFS_Alter_Column,
        RQ_SRS_038_DiskObjectStorageVFS_Alter_Update,
        RQ_SRS_038_DiskObjectStorageVFS_StoragePolicy,
        RQ_SRS_038_DiskObjectStorageVFS_Combinatoric,
        RQ_SRS_038_DiskObjectStorageVFS_Combinatoric_Insert,
        RQ_SRS_038_DiskObjectStorageVFS_Performance,
        RQ_SRS_038_DiskObjectStorageVFS_Providers_Configuration,
        RQ_SRS_038_DiskObjectStorageVFS_Providers_AWS,
        RQ_SRS_038_DiskObjectStorageVFS_Providers_MinIO,
        RQ_SRS_038_DiskObjectStorageVFS_Providers_GCS,
    ),
    content="""
# SRS-038 ClickHouse Disk Object Storage VFS
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Terminology](#terminology)
* 4 [Requirements](#requirements)
  * 4.1 [Replicas](#replicas)
    * 4.1.1 [RQ.SRS-038.DiskObjectStorageVFS.Replica.NoDataDuplication](#rqsrs-038diskobjectstoragevfsreplicanodataduplication)
    * 4.1.2 [RQ.SRS-038.DiskObjectStorageVFS.Replica.Add](#rqsrs-038diskobjectstoragevfsreplicaadd)
    * 4.1.3 [RQ.SRS-038.DiskObjectStorageVFS.Replica.Remove](#rqsrs-038diskobjectstoragevfsreplicaremove)
    * 4.1.4 [RQ.SRS-038.DiskObjectStorageVFS.Replica.Offline](#rqsrs-038diskobjectstoragevfsreplicaoffline)
    * 4.1.5 [RQ.SRS-038.DiskObjectStorageVFS.Replica.Stale](#rqsrs-038diskobjectstoragevfsreplicastale)
  * 4.2 [Settings](#settings)
    * 4.2.1 [RQ.SRS-038.DiskObjectStorageVFS.Settings.Disk](#rqsrs-038diskobjectstoragevfssettingsdisk)
    * 4.2.2 [RQ.SRS-038.DiskObjectStorageVFS.Settings.ZeroCopyIncompatible](#rqsrs-038diskobjectstoragevfssettingszerocopyincompatible)
    * 4.2.3 [RQ.SRS-038.DiskObjectStorageVFS.Settings.Shared](#rqsrs-038diskobjectstoragevfssettingsshared)
  * 4.3 [Data Integrity](#data-integrity)
    * 4.3.1 [RQ.SRS-038.DiskObjectStorageVFS.Integrity.VFSToggled](#rqsrs-038diskobjectstoragevfsintegrityvfstoggled)
    * 4.3.2 [RQ.SRS-038.DiskObjectStorageVFS.Integrity.Migration](#rqsrs-038diskobjectstoragevfsintegritymigration)
    * 4.3.3 [RQ.SRS-038.DiskObjectStorageVFS.Integrity.TTLMove](#rqsrs-038diskobjectstoragevfsintegrityttlmove)
    * 4.3.4 [RQ.SRS-038.DiskObjectStorageVFS.Integrity.TTLDelete](#rqsrs-038diskobjectstoragevfsintegrityttldelete)
    * 4.3.5 [RQ.SRS-038.DiskObjectStorageVFS.Integrity.Detach](#rqsrs-038diskobjectstoragevfsintegritydetach)
    * 4.3.6 [RQ.SRS-038.DiskObjectStorageVFS.Integrity.Delete](#rqsrs-038diskobjectstoragevfsintegritydelete)
  * 4.4 [System](#system)
    * 4.4.1 [RQ.SRS-038.DiskObjectStorageVFS.System.ConnectionInterruption](#rqsrs-038diskobjectstoragevfssystemconnectioninterruption)
    * 4.4.2 [RQ.SRS-038.DiskObjectStorageVFS.System.ConnectionInterruption.FaultInjection](#rqsrs-038diskobjectstoragevfssystemconnectioninterruptionfaultinjection)
    * 4.4.3 [RQ.SRS-038.DiskObjectStorageVFS.System.AddKeeper](#rqsrs-038diskobjectstoragevfssystemaddkeeper)
    * 4.4.4 [RQ.SRS-038.DiskObjectStorageVFS.System.RemoveKeeper](#rqsrs-038diskobjectstoragevfssystemremovekeeper)
    * 4.4.5 [RQ.SRS-038.DiskObjectStorageVFS.System.Compact_Wide](#rqsrs-038diskobjectstoragevfssystemcompact_wide)
  * 4.5 [Parts](#parts)
    * 4.5.1 [RQ.SRS-038.DiskObjectStorageVFS.Parts.Fetch](#rqsrs-038diskobjectstoragevfspartsfetch)
    * 4.5.2 [RQ.SRS-038.DiskObjectStorageVFS.Parts.Optimize](#rqsrs-038diskobjectstoragevfspartsoptimize)
    * 4.5.3 [RQ.SRS-038.DiskObjectStorageVFS.Parts.BackgroundCollapse](#rqsrs-038diskobjectstoragevfspartsbackgroundcollapse)
    * 4.5.4 [RQ.SRS-038.DiskObjectStorageVFS.Parts.Manipulation](#rqsrs-038diskobjectstoragevfspartsmanipulation)
  * 4.6 [Alter](#alter)
    * 4.6.1 [RQ.SRS-038.DiskObjectStorageVFS.Alter.Index](#rqsrs-038diskobjectstoragevfsalterindex)
    * 4.6.2 [RQ.SRS-038.DiskObjectStorageVFS.Alter.OrderBy](#rqsrs-038diskobjectstoragevfsalterorderby)
    * 4.6.3 [RQ.SRS-038.DiskObjectStorageVFS.Alter.SampleBy](#rqsrs-038diskobjectstoragevfsaltersampleby)
    * 4.6.4 [RQ.SRS-038.DiskObjectStorageVFS.Alter.Projections](#rqsrs-038diskobjectstoragevfsalterprojections)
    * 4.6.5 [RQ.SRS-038.DiskObjectStorageVFS.Alter.Column](#rqsrs-038diskobjectstoragevfsaltercolumn)
    * 4.6.6 [RQ.SRS-038.DiskObjectStorageVFS.Alter.Update](#rqsrs-038diskobjectstoragevfsalterupdate)
  * 4.7 [Table](#table)
  * 4.8 [StoragePolicy](#storagepolicy)
    * 4.8.1 [RQ.SRS-038.DiskObjectStorageVFS.StoragePolicy](#rqsrs-038diskobjectstoragevfsstoragepolicy)
  * 4.9 [Combinatoric](#combinatoric)
    * 4.9.1 [Supported Table Configurations](#supported-table-configurations)
    * 4.9.2 [Supported Operations](#supported-operations)
    * 4.9.3 [RQ.SRS-038.DiskObjectStorageVFS.Combinatoric](#rqsrs-038diskobjectstoragevfscombinatoric)
    * 4.9.4 [RQ.SRS-038.DiskObjectStorageVFS.Combinatoric.Insert](#rqsrs-038diskobjectstoragevfscombinatoricinsert)
  * 4.10 [Performance](#performance)
    * 4.10.1 [RQ.SRS-038.DiskObjectStorageVFS.Performance](#rqsrs-038diskobjectstoragevfsperformance)
  * 4.11 [Object Storage Providers](#object-storage-providers)
    * 4.11.1 [RQ.SRS-038.DiskObjectStorageVFS.Providers.Configuration](#rqsrs-038diskobjectstoragevfsprovidersconfiguration)
    * 4.11.2 [RQ.SRS-038.DiskObjectStorageVFS.Providers.AWS](#rqsrs-038diskobjectstoragevfsprovidersaws)
    * 4.11.3 [RQ.SRS-038.DiskObjectStorageVFS.Providers.MinIO](#rqsrs-038diskobjectstoragevfsprovidersminio)
    * 4.11.4 [RQ.SRS-038.DiskObjectStorageVFS.Providers.GCS](#rqsrs-038diskobjectstoragevfsprovidersgcs)
* 5 [References](#references)

## Revision History

This document is stored in an electronic form using [Git] source control
management software hosted in a [GitHub Repository]. All the updates are tracked
using the [Revision History].

## Introduction

[ClickHouse] supports using a virtual file system on [AWS S3] and S3-compatible object storage.

The virtual file system allows replicas to store table data and metadata on a single shared filesystem.

This is only available in versions 23.12 and later.

## Terminology

* **Replicated Table** - A table whose metadata and data exists in multiple locations
* **Zero Copy Replication** - A replication mode where each server keeps a copy of the metadata, but shares the data on external storage
* **0-copy** - Shorthand for Zero Copy Replication
* **VFS** - Virtual File System
* **S3** - Object Storage provided by [AWS]. Also used to refer to any S3-compatible object storage.
* **DiskObjectStorageVFS** - The specific VFS implementation used by [ClickHouse] for object storage

## Requirements

[ClickHouse] SHALL use DiskObjectStorageVFS when the `allow_vfs`
parameter is set to 1. This is only available in versions 23.12 and later.

### Replicas

#### RQ.SRS-038.DiskObjectStorageVFS.Replica.NoDataDuplication
version: 1.0

[ClickHouse] SHALL support VFS such that data is not
duplicated in [S3] storage during any operations on replicated tables (ALTER,
SELECT, INSERT, etc...).

#### RQ.SRS-038.DiskObjectStorageVFS.Replica.Add
version: 1.0

[ClickHouse] SHALL support adding a replica of an existing replicated table
with no changes to data in any tables on the other replicating instances.

#### RQ.SRS-038.DiskObjectStorageVFS.Replica.Remove
version: 1.0

[ClickHouse] SHALL support removing a replicated table on a [ClickHouse] instance
with no changes to data in any tables on the other replicating instances.

#### RQ.SRS-038.DiskObjectStorageVFS.Replica.Offline
version: 1.0

[ClickHouse] SHALL support stopping and starting an instance of [ClickHouse]
with no changes to data in replicated tables. If the table is altered while
an instance is offline, [ClickHouse] SHALL update the table from [S3] when
that instance restarts.

#### RQ.SRS-038.DiskObjectStorageVFS.Replica.Stale
version: 0.0

stale replica

### Settings

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.Disk
version: 1.0

[ClickHouse] SHALL support the `<allow_vfs>` setting in the
`<disks>` section of the config.xml file or an xml file in
the config.d directory to configure the ReplicatedMergeTree engine globally.

Example:

```xml
<yandex>
  <storage_configuration>
    <disks>
      <external>
        <allow_vfs>1</allow_vfs>
      </external>
  </storage_configuration>
</yandex>
```

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.ZeroCopyIncompatible
version: 1.0

[ClickHouse] SHALL return an error if both `<allow_s3_zero_copy_replication>`
and `<allow_vfs>` are enabled at the same time.

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.Shared
version: 0.0

[ClickHouse] SHALL respect the following settings when`<allow_vfs>` is enabled.

| Setting                                                   | Support |
| --------------------------------------------------------- | ------- |
| remote_fs_execute_merges_on_single_replica_time_threshold | yes     |
| zero_copy_concurrent_part_removal_max_split_times         | yes     |
| zero_copy_concurrent_part_removal_max_postpone_ratio      | yes     |
| zero_copy_merge_mutation_min_parts_size_sleep_before_lock | yes     |
| perform_ttl_move_on_insert                                | yes     |
| ...                                                       | planned |

### Data Integrity

#### RQ.SRS-038.DiskObjectStorageVFS.Integrity.VFSToggled
version: 1.0

When the value of the `<allow_vfs>` parameter is changed
from 0 to 1 or 1 to 0 and [ClickHouse] is restarted,
[ClickHouse] SHALL ensure that data is still accessible.

#### RQ.SRS-038.DiskObjectStorageVFS.Integrity.Migration
version: 1.0

[ClickHouse] SHALL provide commands to migrate table data between any pair of "replicated",
"0-copy" and "vfs" table configurations.

| From       | To         | Command |
| ---------- | ---------- | ------- |
| vfs        | replicated |         |
| vfs        | 0-copy     |         |
| 0-copy     | replicated |         |
| 0-copy     | vfs        |         |
| replicated | 0-copy     |         |
| replicated | vfs        |         |

#### RQ.SRS-038.DiskObjectStorageVFS.Integrity.TTLMove
version: 1.0

[ClickHouse] SHALL support TTL moves to other hard disks or [S3] disks when VFS
is used with the MergeTree engine. When TTL moves are used, data will not be
duplicated in [S3]. All objects in a table SHALL be accessible with no errors,
even if they have been moved to a different disk.

#### RQ.SRS-038.DiskObjectStorageVFS.Integrity.TTLDelete
version: 1.0

[ClickHouse] SHALL support TTL object deletion when VFS is used with the MergeTree engine.
When objects are removed, all other objects SHALL be accessible with no errors.

#### RQ.SRS-038.DiskObjectStorageVFS.Integrity.Detach
version: 1.0

[ClickHouse] SHALL support detaching and attaching tables on VFS disks.
Should the detached table on a replica become corrupted,
[ClickHouse] SHALL ensure that other replicas are not affected.

#### RQ.SRS-038.DiskObjectStorageVFS.Integrity.Delete
version: 1.0

[ClickHouse] SHALL ensure disused files in S3 are eventually removed when `<allow_vfs>` is enabled

### System

#### RQ.SRS-038.DiskObjectStorageVFS.System.ConnectionInterruption
version: 0.0

[ClickHouse] SHALL be robust against the following types of connection interruptions.

| Interruption                    |
| ------------------------------- |
| Unstable connection             |
| Unfinished API requests (stuck) |
| Interrupted API requests        |
| Slow connection                 |
| Lost connection to Keeper       |
| Lost connection to Replica      |
| insert_keeper_fault_injection   |

#### RQ.SRS-038.DiskObjectStorageVFS.System.ConnectionInterruption.FaultInjection
version: 0.0

[ClickHouse] SHALL be robust against faults created by insert_keeper_fault_injection.

#### RQ.SRS-038.DiskObjectStorageVFS.System.AddKeeper
version: 0.0

[ClickHouse] Replicated tables SHALL continue to operate without issue when a keeper node is added to the cluster.

#### RQ.SRS-038.DiskObjectStorageVFS.System.RemoveKeeper
version: 0.0

[ClickHouse] Replicated tables SHALL continue to operate without issue when a keeper node is removed from the cluster.
This does not apply if there is only one keeper node.

#### RQ.SRS-038.DiskObjectStorageVFS.System.Compact_Wide
version: 1.0

[ClickHouse] SHALL support [S3] external storage of data parts as Wide parts,
Compact parts, or a combination of both types. The user may view the full storage
of data parts in the system.parts table.

### Parts

[ClickHouse] SHALL support the following operations on parts without data loss.

#### RQ.SRS-038.DiskObjectStorageVFS.Parts.Fetch
version: 0.0

[ClickHouse] SHALL support fetching a new part from another replica.

#### RQ.SRS-038.DiskObjectStorageVFS.Parts.Optimize
version: 0.0

[ClickHouse] SHALL support manually triggering merges with `OPTIMIZE [FINAL]`.

#### RQ.SRS-038.DiskObjectStorageVFS.Parts.BackgroundCollapse
version: 0.0

[ClickHouse] SHALL support collapsing MergeTree engines and their replicated versions.

| Collapsing Engines                   |
| ------------------------------------ |
| (Replicated)CollapsingMergeTree      |
| (Replicated)ReplacingMergeTree       |
| (Replicated)VersionedCollapsingMerge |
| (Replicated)SummingMergeTree         |

#### RQ.SRS-038.DiskObjectStorageVFS.Parts.Manipulation
version: 0.0

| Part Manipulations        |
| ------------------------- |
| DETACH PARTITION/PART     |
| DROP PARTITION/PART       |
| ATTACH PARTITION/PART     |
| ATTACH PARTITION FROM     |
| REPLACE PARTITION         |
| MOVE PARTITION TO TABLE   |
| CLEAR COLUMN IN PARTITION |
| CLEAR INDEX IN PARTITION  |
| FREEZE PARTITION          |
| UNFREEZE PARTITION        |
| FETCH PARTITION/PART      |
| MOVE PARTITION/PART       |
| UPDATE IN PARTITION       |
| DELETE IN PARTITION       |

### Alter

[ClickHouse] SHALL support the following operations on parts without data loss.

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.Index
version: 0.0

| Index Operations  |
| ----------------- |
| ADD INDEX         |
| DROP INDEX        |
| MATERIALIZE INDEX |
| CLEAR INDEX       |

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.OrderBy
version: 0.0

[ClickHouse] SHALL support MODIFY ORDER BY.

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.SampleBy
version: 0.0

[ClickHouse] SHALL support MODIFY SAMPLE BY.

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.Projections
version: 0.0

| Projection Operations  |
| ---------------------- |
| ADD PROJECTION         |
| DROP PROJECTION        |
| MATERIALIZE PROJECTION |
| CLEAR PROJECTION       |

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.Column
version: 0.0

| Column Operation     | Description                                                       |
| -------------------- | ----------------------------------------------------------------- |
| ADD COLUMN           | Adds a new column to the table.                                   |
| DROP COLUMN          | Deletes the column.                                               |
| RENAME COLUMN        | Renames an existing column.                                       |
| CLEAR COLUMN         | Resets column values.                                             |
| COMMENT COLUMN       | Adds a text comment to the column.                                |
| MODIFY COLUMN        | Changes column's type, default expression and TTL.                |
| MODIFY COLUMN REMOVE | Removes one of the column properties.                             |
| MATERIALIZE COLUMN   | Materializes the column in the parts where the column is missing. |

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.Update
version: 0.0

| Operation    |
| ------------ |
| DELETE       |
| UPDATE       |
| ALTER DELETE |
| ALTER UPDATE |

### Table

| Table Operations |
| ---------------- |
| DROP             |
| UNDROP           |
| TRUNCATE         |

### StoragePolicy

#### RQ.SRS-038.DiskObjectStorageVFS.StoragePolicy
version: 0.0

[ClickHouse] SHALL support the following storage policy arrangements with VFS

| Policy                             |
| ---------------------------------- |
| Tiered storage                     |
| Single or multiple S3 buckets      |
| Single or multiple object storages |

### Combinatoric

#### Supported Table Configurations

| Engine                       | Replicated | # Columns | Storage Policy |
| ---------------------------- | :--------- | --------- | -------------- |
| MergeTree                    | Yes        | 10        | S3             |
| ReplacingMergeTree           | No         | 100       | Tiered         |
| CollapsingMergeTree          |            | 1000      |                |
| VersionedCollapsingMergeTree |            | 2000      |                |
| AggregatingMergeTree         |            |           |                |
| SummingMergeTree             |            |           |                |

#### Supported Operations

| Simple | TABLE          |     |
| ------ | -------------- | --- |
| INSERT | DROP TABLE     |     |
| DELETE | UNDROP TABLE   |     |
| UPDATE | TRUNCATE TABLE |     |
| SELECT |                |     |

#### RQ.SRS-038.DiskObjectStorageVFS.Combinatoric
version: 0.0

[Clickhouse]  SHALL support any sequence of [supported operations](#supported-operations)
on a table configured with any combination of
[supported table combinations](#supported-table-configurations).

#### RQ.SRS-038.DiskObjectStorageVFS.Combinatoric.Insert
version: 1.0

[Clickhouse]  SHALL support insert operations on a table configured with
any combination of  [supported table combinations](#supported-table-configurations).

### Performance

#### RQ.SRS-038.DiskObjectStorageVFS.Performance
version: 1.0

[Clickhouse] DiskObjectStorageVFS shares performance requirements with
[RQ.SRS-015.S3.Performance](https://github.com/Altinity/clickhouse-regression/blob/main/s3/requirements/requirements.md#performance)

### Object Storage Providers

#### RQ.SRS-038.DiskObjectStorageVFS.Providers.Configuration
version: 1.0

[ClickHouse] SHALL support configuration of object storage disks from a
supported provider with syntax similar to the following:

``` xml
<yandex>
  <storage_configuration>
    <disks>
      <minio>
        <type>s3</type>
        <endpoint>http://minio:9000/my-bucket/object-key/</endpoint>
        <access_key_id>*****</access_key_id>
        <secret_access_key>*****</secret_access_key>
      </minio>
    </disks>
...
</yandex>
```

#### RQ.SRS-038.DiskObjectStorageVFS.Providers.AWS
version: 1.0

[ClickHouse] SHALL support VFS on object storage using [AWS S3].

#### RQ.SRS-038.DiskObjectStorageVFS.Providers.MinIO
version: 1.0

[ClickHouse] SHALL support VFS on object storage using [MinIO].

#### RQ.SRS-038.DiskObjectStorageVFS.Providers.GCS
version: 1.0

[ClickHouse] SHALL support VFS on object storage using [Google Cloud Storage].

## References

* **AWS:** <https://en.wikipedia.org/wiki/Amazon_Web_Services>
* **S3:** <https://en.wikipedia.org/wiki/Amazon_S3>
* **ClickHouse:** <https://clickhouse.tech>
* **GitHub Repository:** <https://github.com/Altinity/clickhouse-regression/tree/vfs_object_storage_testing/object_storage_vfs>
* **Revision History:** <https://github.com/Altinity/clickhouse-regression/blob/vfs_object_storage_testing/object_storage_vfs/requirements/requirements.md>

[AWS S3]: https://en.wikipedia.org/wiki/Amazon_S3
[ClickHouse]: https://clickhouse.tech
[Git]: https://git-scm.com/
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/tree/vfs_object_storage_testing/object_storage_vfs
[Revision History]: https://github.com/Altinity/clickhouse-regression/blob/vfs_object_storage_testing/object_storage_vfs/requirements/requirements.md
[Google Cloud Storage]: https://en.wikipedia.org/wiki/Google_Cloud_Storage
[MinIO]: https://en.wikipedia.org/wiki/MinIO
""",
)
