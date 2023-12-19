# SRS-038 ClickHouse Disk Object Storage VFS
# Software Requirements Specification

## Table of Contents

## Revision History

This document is stored in an electronic form using [Git] source control
management software hosted in a [GitLab Repository]. All the updates are tracked
using the [Revision History].

## Introduction

## Terminology

## Requirements

### Generic

#### RQ.SRS-038.DiskObjectStorageVFS
version: 1.0

[ClickHouse] SHALL use DiskObjectStorageVFS only when it is started with the `<allow_object_storage_vfs>` parameter is set to 1. This is only available in versions 23.12 and later.

#### RQ.SRS-038.DiskObjectStorageVFS.IncompatibleSettings
version: 1.0

[ClickHouse] SHALL raise an error if `<allow_s3_zero_copy_replication>` is enabled while `<allow_object_storage_vfs>` is enabled.

#### RQ.SRS-038.DiskObjectStorageVFS.PreservesData
version: 1.0

When the value of the `<allow_object_storage_vfs>` parameter is changed from 0 to 1 or 1 to 0 and [ClickHouse] is restarted, [ClickHouse] SHALL ensure that data is not deleted.

#### RQ.SRS-038.DiskObjectStorageVFS.Migration
version: 1.0

[ClickHouse] SHALL provide scripts to migrate between any pair of "replicated", "zero-copy" and "vfs" .

#### RQ.SRS-038.DiskObjectStorageVFS.DeleteInParallel
version: 0.0

[ClickHouse] SHALL be able to delete files in parallel when `<allow_object_storage_vfs>` is enabled

#### RQ.SRS-038.DiskObjectStorageVFS.SharedSettings
version: 0.0

[ClickHouse] SHALL respect the following zero copy replication settings when`<allow_object_storage_vfs>` is enabled

- remote_fs_execute_merges_on_single_replica_time_threshold
- zero_copy_concurrent_part_removal_max_split_times
- zero_copy_concurrent_part_removal_max_postpone_ratio
- zero_copy_merge_mutation_min_parts_size_sleep_before_lock
- ...

#### RQ.SRS-038.DiskObjectStorageVFS.Performance
version: 0.0

[Clickhouse] DiskObjectStorageVFS shares performance requirements with [RQ.SRS-015.S3.Performance](https://github.com/Altinity/clickhouse-regression/blob/main/s3/requirements/requirements.md#performance)

#### RQ.SRS-038.DiskObjectStorageVFS.AWS
version: 1.0

[ClickHouse] SHALL support VFS on external storage using [AWS S3].

#### RQ.SRS-038.DiskObjectStorageVFS.MinIO
version: 1.0

[ClickHouse] SHALL support VFS on external storage using MinIO.

#### RQ.SRS-038.DiskObjectStorageVFS.GCS
version: 1.0

[ClickHouse] SHALL support VFS on external storage using Google Cloud Storage.

## References

- **AWS:** https://en.wikipedia.org/wiki/Amazon_Web_Services
- **S3:** https://en.wikipedia.org/wiki/Amazon_S3
- **ClickHouse:** https://clickhouse.tech
- **GitHub Repository:** https://github.com/Altinity/clickhouse-regression/tree/vfs_object_storage_testing/object_storage_vfs
- **Revision History:** https://github.com/Altinity/clickhouse-regression/blob/vfs_object_storage_testing/object_storage_vfs/requirements/requirements.md

[AWS]: https://en.wikipedia.org/wiki/Amazon_Web_Services
[AWS S3]: https://en.wikipedia.org/wiki/Amazon_S3
[ClickHouse]: https://clickhouse.tech
[GitHub]: https://github.com
[Git]: https://git-scm.com/
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/tree/vfs_object_storage_testing/object_storage_vfs
[Revision History]: https://github.com/Altinity/clickhouse-regression/blob/vfs_object_storage_testing/object_storage_vfs/requirements/requirements.md
[S3]: https://en.wikipedia.org/wiki/Amazon_S3
