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
        "[ClickHouse] SHALL use DiskObjectStorageVFS when the `allow_object_storage_vfs` parameter is set to 1. This is only available in versions 23.12 and later.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.1",
)

RQ_SRS_038_DiskObjectStorageVFS_Core_Delete = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Core.Delete",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL ensure disused files in S3 are eventually deleted when `<allow_object_storage_vfs>` is enabled\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.2",
)

RQ_SRS_038_DiskObjectStorageVFS_Core_DeleteInParallel = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Core.DeleteInParallel",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be able to delete s3 objects in parallel when `<allow_object_storage_vfs>` is enabled\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.3",
)

RQ_SRS_038_DiskObjectStorageVFS_Settings_Global = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Settings.Global",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL use DiskObjectStorageVFS for all new tables when it is set to 1 as a global merge tree setting.\n"
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

RQ_SRS_038_DiskObjectStorageVFS_Settings_SharedSettings = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Settings.SharedSettings",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL respect the following zero copy replication settings when`<allow_object_storage_vfs>` is enabled\n"
        "\n"
        "| Setting                                                   | Support |\n"
        "| --------------------------------------------------------- | ------- |\n"
        "| remote_fs_execute_merges_on_single_replica_time_threshold | yes     |\n"
        "| zero_copy_concurrent_part_removal_max_split_times         | yes     |\n"
        "| zero_copy_concurrent_part_removal_max_postpone_ratio      | yes     |\n"
        "| zero_copy_merge_mutation_min_parts_size_sleep_before_lock | yes     |\n"
        "| remote_fs_zero_copy_zookeeper_path                        | yes     |\n"
        "| remote_fs_zero_copy_path_compatible_mode                  | yes     |\n"
        "| alter_move_to_space_execute_async                         | yes     |\n"
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

RQ_SRS_038_DiskObjectStorageVFS_Performance = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Performance",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[Clickhouse] DiskObjectStorageVFS shares performance requirements with [RQ.SRS-015.S3.Performance](https://github.com/Altinity/clickhouse-regression/blob/main/s3/requirements/requirements.md#performance)\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.4.1",
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
    num="4.5.1",
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
    num="4.5.2",
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
    num="4.5.3",
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
            name="RQ.SRS-038.DiskObjectStorageVFS.Core.Delete", level=3, num="4.1.2"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Core.DeleteInParallel",
            level=3,
            num="4.1.3",
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
            name="RQ.SRS-038.DiskObjectStorageVFS.Settings.SharedSettings",
            level=3,
            num="4.2.4",
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
        Heading(name="Performance", level=2, num="4.4"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Performance", level=3, num="4.4.1"
        ),
        Heading(name="Object Storage Providers", level=2, num="4.5"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Providers.AWS", level=3, num="4.5.1"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Providers.MinIO", level=3, num="4.5.2"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Providers.GCS", level=3, num="4.5.3"
        ),
        Heading(name="References", level=1, num="5"),
    ),
    requirements=(
        RQ_SRS_038_DiskObjectStorageVFS,
        RQ_SRS_038_DiskObjectStorageVFS_Core_Delete,
        RQ_SRS_038_DiskObjectStorageVFS_Core_DeleteInParallel,
        RQ_SRS_038_DiskObjectStorageVFS_Settings_Global,
        RQ_SRS_038_DiskObjectStorageVFS_Settings_Local,
        RQ_SRS_038_DiskObjectStorageVFS_Settings_ZeroCopyIncompatible,
        RQ_SRS_038_DiskObjectStorageVFS_Settings_SharedSettings,
        RQ_SRS_038_DiskObjectStorageVFS_Integrity_VFSToggled,
        RQ_SRS_038_DiskObjectStorageVFS_Integrity_Migration,
        RQ_SRS_038_DiskObjectStorageVFS_Performance,
        RQ_SRS_038_DiskObjectStorageVFS_Providers_AWS,
        RQ_SRS_038_DiskObjectStorageVFS_Providers_MinIO,
        RQ_SRS_038_DiskObjectStorageVFS_Providers_GCS,
    ),
    content="""
# SRS-038 ClickHouse Disk Object Storage VFS
# Software Requirements Specification

## Table of Contents

## Revision History

This document is stored in an electronic form using [Git] source control
management software hosted in a [GitHub Repository]. All the updates are tracked
using the [Revision History].

## Introduction

## Terminology

- **Replicated Table** - A table whose metadata and data exists in multiple locations
- **Zero Copy Replication** - A replication mode where each server keeps a copy of the metadata, but shares the data on external storage
- **0-copy** - Shorthand for Zero Copy Replication
- **VFS** - Virtual File System
- **S3** - Object Storage provided by [AWS]. Also used to refer to object storage in general.
- **VFDiskObjectStorageVFS** - The specific VFS implementation used by [ClickHouse] for object storage

## Requirements

### Core

#### RQ.SRS-038.DiskObjectStorageVFS
version: 1.0

[ClickHouse] SHALL use DiskObjectStorageVFS when the `allow_object_storage_vfs` parameter is set to 1. This is only available in versions 23.12 and later.

#### RQ.SRS-038.DiskObjectStorageVFS.Core.Delete
version: 0.0

[ClickHouse] SHALL ensure disused files in S3 are eventually deleted when `<allow_object_storage_vfs>` is enabled

#### RQ.SRS-038.DiskObjectStorageVFS.Core.DeleteInParallel
version: 0.0

[ClickHouse] SHALL be able to delete s3 objects in parallel when `<allow_object_storage_vfs>` is enabled

### Settings

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.Global
version: 1.0

[ClickHouse] SHALL use DiskObjectStorageVFS for all new tables when it is set to 1 as a global merge tree setting.

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

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.SharedSettings
version: 0.0

[ClickHouse] SHALL respect the following zero copy replication settings when`<allow_object_storage_vfs>` is enabled

| Setting                                                   | Support |
| --------------------------------------------------------- | ------- |
| remote_fs_execute_merges_on_single_replica_time_threshold | yes     |
| zero_copy_concurrent_part_removal_max_split_times         | yes     |
| zero_copy_concurrent_part_removal_max_postpone_ratio      | yes     |
| zero_copy_merge_mutation_min_parts_size_sleep_before_lock | yes     |
| remote_fs_zero_copy_zookeeper_path                        | yes     |
| remote_fs_zero_copy_path_compatible_mode                  | yes     |
| alter_move_to_space_execute_async                         | yes     |

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

### Performance

#### RQ.SRS-038.DiskObjectStorageVFS.Performance
version: 1.0

[Clickhouse] DiskObjectStorageVFS shares performance requirements with [RQ.SRS-015.S3.Performance](https://github.com/Altinity/clickhouse-regression/blob/main/s3/requirements/requirements.md#performance)

### Object Storage Providers

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
""",
)
