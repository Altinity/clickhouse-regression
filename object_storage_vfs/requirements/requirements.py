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
        "[ClickHouse] SHALL use DiskObjectStorageVFS only when it is started with the `<allow_object_storage_vfs>` parameter is set to 1. This is only available in versions 23.12 and later.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.1",
)

RQ_SRS_038_DiskObjectStorageVFS_IncompatibleSettings = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.IncompatibleSettings",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL raise an error if `<allow_s3_zero_copy_replication>` is enabled while `<allow_object_storage_vfs>` is enabled.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.2",
)

RQ_SRS_038_DiskObjectStorageVFS_PreservesData = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.PreservesData",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When the value of the `<allow_object_storage_vfs>` parameter is changed from 0 to 1 or 1 to 0 and [ClickHouse] is restarted, [ClickHouse] SHALL ensure that data is not deleted.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.3",
)

RQ_SRS_038_DiskObjectStorageVFS_Migration = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Migration",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL provide scripts to migrate between any pair of "replicated", "zero-copy" and "vfs" .\n'
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.4",
)

RQ_SRS_038_DiskObjectStorageVFS_DeleteInParallel = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.DeleteInParallel",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be able to delete files in parallel when `<allow_object_storage_vfs>` is enabled\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.5",
)

RQ_SRS_038_DiskObjectStorageVFS_SharedSettings = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.SharedSettings",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL respect the following zero copy replication settings when`<allow_object_storage_vfs>` is enabled\n"
        "\n"
        "- remote_fs_execute_merges_on_single_replica_time_threshold\n"
        "- zero_copy_concurrent_part_removal_max_split_times\n"
        "- zero_copy_concurrent_part_removal_max_postpone_ratio\n"
        "- zero_copy_merge_mutation_min_parts_size_sleep_before_lock\n"
        "- ...\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.6",
)

RQ_SRS_038_DiskObjectStorageVFS_Performance = Requirement(
    name="RQ.SRS-038.DiskObjectStorageVFS.Performance",
    version="0.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[Clickhouse] DiskObjectStorageVFS shares performance requirements with [RQ.SRS-015.S3.Performance](https://github.com/Altinity/clickhouse-regression/blob/main/s3/requirements/requirements.md#performance)\n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.7",
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
        Heading(name="Generic", level=2, num="4.1"),
        Heading(name="RQ.SRS-038.DiskObjectStorageVFS", level=3, num="4.1.1"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.IncompatibleSettings",
            level=3,
            num="4.1.2",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.PreservesData", level=3, num="4.1.3"
        ),
        Heading(name="RQ.SRS-038.DiskObjectStorageVFS.Migration", level=3, num="4.1.4"),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.DeleteInParallel",
            level=3,
            num="4.1.5",
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.SharedSettings", level=3, num="4.1.6"
        ),
        Heading(
            name="RQ.SRS-038.DiskObjectStorageVFS.Performance", level=3, num="4.1.7"
        ),
        Heading(name="References", level=1, num="5"),
    ),
    requirements=(
        RQ_SRS_038_DiskObjectStorageVFS,
        RQ_SRS_038_DiskObjectStorageVFS_IncompatibleSettings,
        RQ_SRS_038_DiskObjectStorageVFS_PreservesData,
        RQ_SRS_038_DiskObjectStorageVFS_Migration,
        RQ_SRS_038_DiskObjectStorageVFS_DeleteInParallel,
        RQ_SRS_038_DiskObjectStorageVFS_SharedSettings,
        RQ_SRS_038_DiskObjectStorageVFS_Performance,
    ),
    content="""
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
""",
)
