# SRS-038 ClickHouse Disk Object Storage VFS
# Software Requirements Specification

## Table of Contents

## Revision History

This document is stored in an electronic form using [Git] source control
management software hosted in a [GitHub Repository]. All the updates are tracked
using the [Revision History].

## Introduction

[ClickHouse] supports using a virtual file system on [AWS S3] and S3-compatible object storage.

The virtual file system allows replicas to store table data and metadata on a single shared filesystem.

## Terminology

- **Replicated Table** - A table whose metadata and data exists in multiple locations
- **Zero Copy Replication** - A replication mode where each server keeps a copy of the metadata, but shares the data on external storage
- **0-copy** - Shorthand for Zero Copy Replication
- **VFS** - Virtual File System
- **S3** - Object Storage provided by [AWS]. Also used to refer to any S3-compatible object storage.
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
