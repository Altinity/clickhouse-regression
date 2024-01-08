# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.231130.1212236.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_038_DiskObjectStorageVFS = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL use DiskObjectStorageVFS when the `allow_object_storage_vfs`\n"
        "parameter is set to 1. This is only available in versions 23.12 and later.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.1",
)

RQ_SRS_038_DiskObjectStorageVFS_Core_AddReplica = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Core.AddReplica",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support adding a replica of an existing replicated table\n"
        "with no changes to the data in the table.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.2",
)

RQ_SRS_038_DiskObjectStorageVFS_Core_DropReplica = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Core.DropReplica",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support stopping and starting an instance of [ClickHouse]\n"
        "with no changes to data in replicated tables. If the table is altered while\n"
        "the instance restarts, [ClickHouse] SHALL update the table from [S3] when\n"
        "the instance restarts.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.3",
)

RQ_SRS_038_DiskObjectStorageVFS_Core_NoDataDuplication = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Core.NoDataDuplication",
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
    num="4.1.4",
)

RQ_SRS_038_DiskObjectStorageVFS_Core_Delete = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Core.Delete",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL ensure disused files in S3 are eventually removed when `<allow_object_storage_vfs>` is enabled\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.5",
)

RQ_SRS_038_DiskObjectStorageVFS_Core_DeleteInParallel = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Core.DeleteInParallel",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be able to remove s3 objects in parallel when `<allow_object_storage_vfs>` is enabled\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.6",
)

RQ_SRS_038_DiskObjectStorageVFS_Settings_Global = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Settings.Global",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `<allow_object_storage_vfs>` setting to the\n"
        "`<merge_tree>` section of the config.xml file or the merge_tree.xml file in\n"
        "the config.d directory to configure the ReplicatedMergeTree engine globally. This\n"
        "setting SHALL be applied to all new ReplicatedMergeTree tables.\n"
        "\n"
        "Example:\n"
        "\n"
        "```xml\n"
        "<yandex>\n"
        "  <merge_tree>\n"
        "    <allow_object_storage_vfs>1</allow_object_storage_vfs>\n"
        "  </merge_tree>\n"
        "</yandex>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.2.1",
)

RQ_SRS_038_DiskObjectStorageVFS_Settings_Local = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Settings.Local",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL use DiskObjectStorageVFS for a table when the allow_object_storage_vfs parameter is set to 1.\n"
        "\n"
        "Example:\n"
        "\n"
        "```sql\n"
        "CREATE TABLE zero_copy_replication (\n"
        "    d UInt64\n"
        ") ENGINE = MergeTree()\n"
        "ORDER BY d\n"
        "SETTINGS allow_object_storage_vfs=1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.2.2",
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
        "and `<allow_object_storage_vfs>` are enabled at the same time.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.2.3",
)

RQ_SRS_038_DiskObjectStorageVFS_Settings_Shared = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Settings.Shared",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL respect the following settings when`<allow_object_storage_vfs>` is enabled\n"
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
    num="4.2.4",
)

RQ_SRS_038_DiskObjectStorageVFS_Integrity_VFSToggled = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Integrity.VFSToggled",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When the value of the `<allow_object_storage_vfs>` parameter is changed from 0 to 1 or 1 to 0 and [ClickHouse] is restarted, [ClickHouse] SHALL ensure that data is still accessible.\n"
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
        '[ClickHouse] SHALL provide commands to migrate table data between any pair of "replicated", "0-copy" and "vfs" table configurations.\n'
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
        " [supported table combinations](#supported-table-configurations).\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.4.5",
)

RQ_SRS_038_DiskObjectStorageVFS_Combinatoric_Insert = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Combinatoric.Insert",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[Clickhouse]  SHALL support insert operations on a table configured with \n"
        "any combination of  [supported table combinations](#supported-table-configurations).\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.4.6",
)

RQ_SRS_038_DiskObjectStorageVFS_Performance = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Performance",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[Clickhouse] DiskObjectStorageVFS shares performance requirements with \n"
        "[RQ.SRS-015.S3.Performance](https://github.com/Altinity/clickhouse-regression/blob/main/s3/requirements/requirements.md#performance)\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.5.1",
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
    num="4.6.1",
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
    num="4.6.2",
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
    num="4.6.3",
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
    num="4.6.4",
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
        Heading(name="Core", level=2, num="4.1"),
        Heading(name="RQ.SRS-038.DiskObjectStorageVFS", level=3, num="4.1.1"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Core.AddReplica", level=3, num="4.1.2"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Core.DropReplica",
            level=3,
            num="4.1.3",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Core.NoDataDuplication",
            level=3,
            num="4.1.4",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Core.Delete", level=3, num="4.1.5"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Core.DeleteInParallel",
            level=3,
            num="4.1.6",
        ),
        Heading(name="Settings", level=2, num="4.2"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Settings.Global", level=3, num="4.2.1"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Settings.Local", level=3, num="4.2.2"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Settings.ZeroCopyIncompatible",
            level=3,
            num="4.2.3",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Settings.Shared", level=3, num="4.2.4"
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
        Heading(name="Combinatoric", level=2, num="4.4"),
        Heading(name="Supported Table Configurations", level=4, num="4.4.4.1"),
        Heading(name="Supported Operations", level=4, num="4.4.4.2"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Combinatoric", level=3, num="4.4.5"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Combinatoric.Insert",
            level=3,
            num="4.4.6",
        ),
        Heading(name="Performance", level=2, num="4.5"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Performance", level=3, num="4.5.1"
        ),
        Heading(name="Object Storage Providers", level=2, num="4.6"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Providers.Configuration",
            level=3,
            num="4.6.1",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Providers.AWS", level=3, num="4.6.2"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Providers.MinIO", level=3, num="4.6.3"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Providers.GCS", level=3, num="4.6.4"
        ),
        Heading(name="References", level=1, num="5"),
    ),
    requirements=(
        RQ_SRS_038_DiskObjectStorageVFS,
        RQ_SRS_038_DiskObjectStorageVFS_Core_AddReplica,
        RQ_SRS_038_DiskObjectStorageVFS_Core_DropReplica,
        RQ_SRS_038_DiskObjectStorageVFS_Core_NoDataDuplication,
        RQ_SRS_038_DiskObjectStorageVFS_Core_Delete,
        RQ_SRS_038_DiskObjectStorageVFS_Core_DeleteInParallel,
        RQ_SRS_038_DiskObjectStorageVFS_Settings_Global,
        RQ_SRS_038_DiskObjectStorageVFS_Settings_Local,
        RQ_SRS_038_DiskObjectStorageVFS_Settings_ZeroCopyIncompatible,
        RQ_SRS_038_DiskObjectStorageVFS_Settings_Shared,
        RQ_SRS_038_DiskObjectStorageVFS_Integrity_VFSToggled,
        RQ_SRS_038_DiskObjectStorageVFS_Integrity_Migration,
        RQ_SRS_038_DiskObjectStorageVFS_Integrity_TTLMove,
        RQ_SRS_038_DiskObjectStorageVFS_Integrity_TTLDelete,
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

* [Table of Contents](#table-of-contents)
* [Revision History](#revision-history)
* [Introduction](#introduction)
* [Terminology](#terminology)
* [Requirements](#requirements)
  * [Core](#core)
    * [RQ.SRS-038.DiskObjectStorageVFS](#rqsrs-038diskobjectstoragevfs)
    * [RQ.SRS-038.DiskObjectStorageVFS.Core.AddReplica](#rqsrs-038diskobjectstoragevfscoreaddreplica)
    * [RQ.SRS-038.DiskObjectStorageVFS.Core.DropReplica](#rqsrs-038diskobjectstoragevfscoredropreplica)
    * [RQ.SRS-038.DiskObjectStorageVFS.Core.NoDataDuplication](#rqsrs-038diskobjectstoragevfscorenodataduplication)
    * [RQ.SRS-038.DiskObjectStorageVFS.Core.Delete](#rqsrs-038diskobjectstoragevfscoredelete)
    * [RQ.SRS-038.DiskObjectStorageVFS.Core.DeleteInParallel](#rqsrs-038diskobjectstoragevfscoredeleteinparallel)
  * [Settings](#settings)
    * [RQ.SRS-038.DiskObjectStorageVFS.Settings.Global](#rqsrs-038diskobjectstoragevfssettingsglobal)
    * [RQ.SRS-038.DiskObjectStorageVFS.Settings.Local](#rqsrs-038diskobjectstoragevfssettingslocal)
    * [RQ.SRS-038.DiskObjectStorageVFS.Settings.ZeroCopyIncompatible](#rqsrs-038diskobjectstoragevfssettingszerocopyincompatible)
    * [RQ.SRS-038.DiskObjectStorageVFS.Settings.Shared](#rqsrs-038diskobjectstoragevfssettingsshared)
  * [Data Integrity](#data-integrity)
    * [RQ.SRS-038.DiskObjectStorageVFS.Integrity.VFSToggled](#rqsrs-038diskobjectstoragevfsintegrityvfstoggled)
    * [RQ.SRS-038.DiskObjectStorageVFS.Integrity.Migration](#rqsrs-038diskobjectstoragevfsintegritymigration)
    * [RQ.SRS-038.DiskObjectStorageVFS.Integrity.TTLMove](#rqsrs-038diskobjectstoragevfsintegrityttlmove)
    * [RQ.SRS-038.DiskObjectStorageVFS.Integrity.TTLDelete](#rqsrs-038diskobjectstoragevfsintegrityttldelete)
  * [Combinatorial](#combinatorial)
    * [RQ.SRS-038.DiskObjectStorageVFS.Combinatorial](#rqsrs-038diskobjectstoragevfscombinatorial)
      * [Supported Table Configurations](#supported-table-configurations)
      * [Supported Operations](#supported-operations)
  * [Performance](#performance)
    * [RQ.SRS-038.DiskObjectStorageVFS.Performance](#rqsrs-038diskobjectstoragevfsperformance)
  * [Object Storage Providers](#object-storage-providers)
    * [RQ.SRS-038.DiskObjectStorageVFS.Providers.Configuration](#rqsrs-038diskobjectstoragevfsprovidersconfiguration)
    * [RQ.SRS-038.DiskObjectStorageVFS.Providers.AWS](#rqsrs-038diskobjectstoragevfsprovidersaws)
    * [RQ.SRS-038.DiskObjectStorageVFS.Providers.MinIO](#rqsrs-038diskobjectstoragevfsprovidersminio)
    * [RQ.SRS-038.DiskObjectStorageVFS.Providers.GCS](#rqsrs-038diskobjectstoragevfsprovidersgcs)
* [References](#references)


## Revision History

This document is stored in an electronic form using [Git] source control
management software hosted in a [GitHub Repository]. All the updates are tracked
using the [Revision History].

## Introduction

[ClickHouse] supports using a virtual file system on [AWS S3] and S3-compatible object storage.

The virtual file system allows replicas to store table data and metadata on a single shared filesystem.

This is only available in versions 23.12 and later.

## Terminology

- **Replicated Table** - A table whose metadata and data exists in multiple locations
- **Zero Copy Replication** - A replication mode where each server keeps a copy of the metadata, but shares the data on external storage
- **0-copy** - Shorthand for Zero Copy Replication
- **VFS** - Virtual File System
- **S3** - Object Storage provided by [AWS]. Also used to refer to any S3-compatible object storage.
- **DiskObjectStorageVFS** - The specific VFS implementation used by [ClickHouse] for object storage

## Requirements

### Core

#### RQ.SRS-038.DiskObjectStorageVFS
version: 1.0

[ClickHouse] SHALL use DiskObjectStorageVFS when the `allow_object_storage_vfs`
parameter is set to 1. This is only available in versions 23.12 and later.

#### RQ.SRS-038.DiskObjectStorageVFS.Core.AddReplica
version: 1.0

[ClickHouse] SHALL support adding a replica of an existing replicated table
with no changes to the data in the table.

#### RQ.SRS-038.DiskObjectStorageVFS.Core.DropReplica
version: 1.0

[ClickHouse] SHALL support stopping and starting an instance of [ClickHouse]
with no changes to data in replicated tables. If the table is altered while
the instance restarts, [ClickHouse] SHALL update the table from [S3] when
the instance restarts.

#### RQ.SRS-038.DiskObjectStorageVFS.Core.NoDataDuplication
version: 1.0

[ClickHouse] SHALL support VFS such that data is not
duplicated in [S3] storage during any operations on replicated tables (ALTER,
SELECT, INSERT, etc...).

#### RQ.SRS-038.DiskObjectStorageVFS.Core.Delete
version: 0.0

[ClickHouse] SHALL ensure disused files in S3 are eventually removed when `<allow_object_storage_vfs>` is enabled

#### RQ.SRS-038.DiskObjectStorageVFS.Core.DeleteInParallel
version: 0.0

[ClickHouse] SHALL be able to remove s3 objects in parallel when `<allow_object_storage_vfs>` is enabled

### Settings

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.Global
version: 1.0

[ClickHouse] SHALL support the `<allow_object_storage_vfs>` setting to the
`<merge_tree>` section of the config.xml file or the merge_tree.xml file in
the config.d directory to configure the ReplicatedMergeTree engine globally. This
setting SHALL be applied to all new ReplicatedMergeTree tables.

Example:

```xml
<yandex>
  <merge_tree>
    <allow_object_storage_vfs>1</allow_object_storage_vfs>
  </merge_tree>
</yandex>
```

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.Local
version: 1.0

[ClickHouse] SHALL use DiskObjectStorageVFS for a table when the allow_object_storage_vfs parameter is set to 1.

Example:

```sql
CREATE TABLE zero_copy_replication (
    d UInt64
) ENGINE = MergeTree()
ORDER BY d
SETTINGS allow_object_storage_vfs=1
```

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.ZeroCopyIncompatible
version: 1.0

[ClickHouse] SHALL return an error if both `<allow_s3_zero_copy_replication>`
and `<allow_object_storage_vfs>` are enabled at the same time.

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.Shared
version: 0.0

[ClickHouse] SHALL respect the following settings when`<allow_object_storage_vfs>` is enabled

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

When the value of the `<allow_object_storage_vfs>` parameter is changed from 0 to 1 or 1 to 0 and [ClickHouse] is restarted, [ClickHouse] SHALL ensure that data is still accessible.

#### RQ.SRS-038.DiskObjectStorageVFS.Integrity.Migration
version: 1.0

[ClickHouse] SHALL provide commands to migrate table data between any pair of "replicated", "0-copy" and "vfs" table configurations.

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

### Combinatoric

##### Supported Table Configurations

| Engine                       | Replicated | # Columns | Storage Policy |
| ---------------------------- | :--------- | --------- | -------------- |
| MergeTree                    | Yes        | 10        | S3             |
| ReplacingMergeTree           | No         | 100       | Tiered         |
| CollapsingMergeTree          |            | 1000      |                |
| VersionedCollapsingMergeTree |            | 2000      |                |
| AggregatingMergeTree         |            |           |                |
| SummingMergeTree             |            |           |                |

##### Supported Operations

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

- **AWS:** <https://en.wikipedia.org/wiki/Amazon_Web_Services>
- **S3:** <https://en.wikipedia.org/wiki/Amazon_S3>
- **ClickHouse:** <https://clickhouse.tech>
- **GitHub Repository:** <https://github.com/Altinity/clickhouse-regression/tree/vfs_object_storage_testing/object_storage_vfs>
- **Revision History:** <https://github.com/Altinity/clickhouse-regression/blob/vfs_object_storage_testing/object_storage_vfs/requirements/requirements.md>

[AWS S3]: https://en.wikipedia.org/wiki/Amazon_S3
[ClickHouse]: https://clickhouse.tech
[Git]: https://git-scm.com/
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/tree/vfs_object_storage_testing/object_storage_vfs
[Revision History]: https://github.com/Altinity/clickhouse-regression/blob/vfs_object_storage_testing/object_storage_vfs/requirements/requirements.md
[Google Cloud Storage]: https://en.wikipedia.org/wiki/Google_Cloud_Storage
[MinIO]: https://en.wikipedia.org/wiki/MinIO
""",
)
