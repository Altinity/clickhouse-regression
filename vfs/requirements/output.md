-   [SRS-038 ClickHouse Disk Object Storage
    VFS](#srs-038-clickhouse-disk-object-storage-vfs)
-   [Software Requirements
    Specification](#software-requirements-specification)
    -   [Table of Contents](#table-of-contents)
    -   [Revision History](#revision-history)
    -   [Introduction](#introduction)
    -   [Terminology](#terminology)
    -   [Requirements](#requirements)
        -   [Core](#core)
        -   [Settings](#settings)
        -   [Data Integrity](#data-integrity)
        -   [Combinatorial](#combinatorial)
        -   [Performance](#performance)
        -   [Object Storage Providers](#object-storage-providers)
    -   [References](#references)

SRS-038 ClickHouse Disk Object Storage VFS
==========================================

Software Requirements Specification
===================================

Table of Contents
-----------------

-   [SRS-038 ClickHouse Disk Object Storage
    VFS](#srs-038-clickhouse-disk-object-storage-vfs)
-   [Software Requirements
    Specification](#software-requirements-specification)
    -   [Table of Contents](#table-of-contents)
    -   [Revision History](#revision-history)
    -   [Introduction](#introduction)
    -   [Terminology](#terminology)
    -   [Requirements](#requirements)
        -   [Core](#core)
            -   [RQ.SRS-038.DiskObjectStorageVFS](#rqsrs-038diskobjectstoragevfs)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Core.AddReplica](#rqsrs-038diskobjectstoragevfscoreaddreplica)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Core.DropReplica](#rqsrs-038diskobjectstoragevfscoredropreplica)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Core.NoDataDuplication](#rqsrs-038diskobjectstoragevfscorenodataduplication)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Core.Delete](#rqsrs-038diskobjectstoragevfscoredelete)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Core.DeleteInParallel](#rqsrs-038diskobjectstoragevfscoredeleteinparallel)
        -   [Settings](#settings)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Settings.Global](#rqsrs-038diskobjectstoragevfssettingsglobal)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Settings.Local](#rqsrs-038diskobjectstoragevfssettingslocal)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Settings.ZeroCopyIncompatible](#rqsrs-038diskobjectstoragevfssettingszerocopyincompatible)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Settings.Shared](#rqsrs-038diskobjectstoragevfssettingsshared)
        -   [Data Integrity](#data-integrity)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Integrity.VFSToggled](#rqsrs-038diskobjectstoragevfsintegrityvfstoggled)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Integrity.Migration](#rqsrs-038diskobjectstoragevfsintegritymigration)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Integrity.TTLMove](#rqsrs-038diskobjectstoragevfsintegrityttlmove)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Integrity.TTLDelete](#rqsrs-038diskobjectstoragevfsintegrityttldelete)
        -   [Combinatorial](#combinatorial)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Combinatorial](#rqsrs-038diskobjectstoragevfscombinatorial)
                -   [Supported Table
                    Configurations](#supported-table-configurations)
                -   [Supported Operations](#supported-operations)
        -   [Performance](#performance)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Performance](#rqsrs-038diskobjectstoragevfsperformance)
        -   [Object Storage Providers](#object-storage-providers)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Providers.Configuration](#rqsrs-038diskobjectstoragevfsprovidersconfiguration)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Providers.AWS](#rqsrs-038diskobjectstoragevfsprovidersaws)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Providers.MinIO](#rqsrs-038diskobjectstoragevfsprovidersminio)
            -   [RQ.SRS-038.DiskObjectStorageVFS.Providers.GCS](#rqsrs-038diskobjectstoragevfsprovidersgcs)
    -   [References](#references)

Revision History
----------------

This document is stored in an electronic form using
[Git](https://git-scm.com/) source control management software hosted in
a [GitHub
Repository](https://github.com/Altinity/clickhouse-regression/tree/vfs_object_storage_testing/object_storage_vfs).
All the updates are tracked using the [Revision
History](https://github.com/Altinity/clickhouse-regression/blob/vfs_object_storage_testing/object_storage_vfs/requirements/requirements.md).

Introduction
------------

[ClickHouse](https://clickhouse.tech) supports using a virtual file
system on [AWS S3](https://en.wikipedia.org/wiki/Amazon_S3) and
S3-compatible object storage.

The virtual file system allows replicas to store table data and metadata
on a single shared filesystem.

This is only available in versions 23.12 and later.

Terminology
-----------

-   **Replicated Table** - A table whose metadata and data exists in
    multiple locations
-   **Zero Copy Replication** - A replication mode where each server
    keeps a copy of the metadata, but shares the data on external
    storage
-   **0-copy** - Shorthand for Zero Copy Replication
-   **VFS** - Virtual File System
-   **S3** - Object Storage provided by \[AWS\]. Also used to refer to
    any S3-compatible object storage.
-   **DiskObjectStorageVFS** - The specific VFS implementation used by
    [ClickHouse](https://clickhouse.tech) for object storage

Requirements
------------

### Core

#### RQ.SRS-038.DiskObjectStorageVFS

version: 1.0

[ClickHouse](https://clickhouse.tech) SHALL use DiskObjectStorageVFS
when the `allow_object_storage_vfs` parameter is set to 1. This is only
available in versions 23.12 and later.

#### RQ.SRS-038.DiskObjectStorageVFS.Core.AddReplica

version: 1.0

[ClickHouse](https://clickhouse.tech) SHALL support adding a replica of
an existing replicated table with no changes to the data in the table.

#### RQ.SRS-038.DiskObjectStorageVFS.Core.DropReplica

version: 1.0

[ClickHouse](https://clickhouse.tech) SHALL support stopping and
starting an instance of [ClickHouse](https://clickhouse.tech) with no
changes to data in replicated tables. If the table is altered while the
instance restarts, [ClickHouse](https://clickhouse.tech) SHALL update
the table from \[S3\] when the instance restarts.

#### RQ.SRS-038.DiskObjectStorageVFS.Core.NoDataDuplication

version: 1.0

[ClickHouse](https://clickhouse.tech) SHALL support VFS such that data
is not duplicated in \[S3\] storage during any operations on replicated
tables (ALTER, SELECT, INSERT, etc...).

#### RQ.SRS-038.DiskObjectStorageVFS.Core.Delete

version: 0.0

[ClickHouse](https://clickhouse.tech) SHALL ensure disused files in S3
are eventually removed when `<allow_object_storage_vfs>` is enabled

#### RQ.SRS-038.DiskObjectStorageVFS.Core.DeleteInParallel

version: 0.0

[ClickHouse](https://clickhouse.tech) SHALL be able to remove s3 objects
in parallel when `<allow_object_storage_vfs>` is enabled

### Settings

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.Global

version: 1.0

[ClickHouse](https://clickhouse.tech) SHALL support the
`<allow_object_storage_vfs>` setting to the `<merge_tree>` section of
the config.xml file or the merge\_tree.xml file in the config.d
directory to configure the ReplicatedMergeTree engine globally. This
setting SHALL be applied to all new ReplicatedMergeTree tables.

Example:

``` {.xml}
<yandex>
  <merge_tree>
    <allow_object_storage_vfs>1</allow_object_storage_vfs>
  </merge_tree>
</yandex>
```

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.Local

version: 1.0

[ClickHouse](https://clickhouse.tech) SHALL use DiskObjectStorageVFS for
a table when the allow\_object\_storage\_vfs parameter is set to 1.

Example:

``` {.sql}
CREATE TABLE zero_copy_replication (
    d UInt64
) ENGINE = MergeTree()
ORDER BY d
SETTINGS allow_object_storage_vfs=1
```

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.ZeroCopyIncompatible

version: 1.0

[ClickHouse](https://clickhouse.tech) SHALL return an error if both
`<allow_s3_zero_copy_replication>` and `<allow_object_storage_vfs>` are
enabled at the same time.

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.Shared

version: 0.0

[ClickHouse](https://clickhouse.tech) SHALL respect the following
settings when`<allow_object_storage_vfs>` is enabled

  Setting                                                              Support
  -------------------------------------------------------------------- ---------
  remote\_fs\_execute\_merges\_on\_single\_replica\_time\_threshold    yes
  zero\_copy\_concurrent\_part\_removal\_max\_split\_times             yes
  zero\_copy\_concurrent\_part\_removal\_max\_postpone\_ratio          yes
  zero\_copy\_merge\_mutation\_min\_parts\_size\_sleep\_before\_lock   yes
  perform\_ttl\_move\_on\_insert                                       yes
  ...                                                                  planned

### Data Integrity

#### RQ.SRS-038.DiskObjectStorageVFS.Integrity.VFSToggled

version: 1.0

When the value of the `<allow_object_storage_vfs>` parameter is changed
from 0 to 1 or 1 to 0 and [ClickHouse](https://clickhouse.tech) is
restarted, [ClickHouse](https://clickhouse.tech) SHALL ensure that data
is still accessible.

#### RQ.SRS-038.DiskObjectStorageVFS.Integrity.Migration

version: 1.0

[ClickHouse](https://clickhouse.tech) SHALL provide commands to migrate
table data between any pair of "replicated", "0-copy" and "vfs" table
configurations.

  From         To           Command
  ------------ ------------ ---------
  vfs          replicated   
  vfs          0-copy       
  0-copy       replicated   
  0-copy       vfs          
  replicated   0-copy       
  replicated   vfs          

#### RQ.SRS-038.DiskObjectStorageVFS.Integrity.TTLMove

version: 1.0

[ClickHouse](https://clickhouse.tech) SHALL support TTL moves to other
hard disks or \[S3\] disks when VFS is used with the MergeTree engine.
When TTL moves are used, data will not be duplicated in \[S3\]. All
objects in a table SHALL be accessible with no errors, even if they have
been moved to a different disk.

#### RQ.SRS-038.DiskObjectStorageVFS.Integrity.TTLDelete

version: 1.0

[ClickHouse](https://clickhouse.tech) SHALL support TTL object deletion
when VFS is used with the MergeTree engine. When objects are removed,
all other objects SHALL be accessible with no errors.

### Combinatorial

#### RQ.SRS-038.DiskObjectStorageVFS.Combinatorial

version: 0.0

[Clickhouse](https://clickhouse.tech) SHALL support any sequence of
supported operations on a table configured with any combination of
supported table combinations.

##### Supported Table Configurations

  Engine                         Replicated   \# Columns   Storage Policy
  ------------------------------ ------------ ------------ ----------------
  MergeTree                      Yes          10           S3
  ReplacingMergeTree             No           100          Tiered
  CollapsingMergeTree                         1000         
  VersionedCollapsingMergeTree                10000        
  AggregatingMergeTree                                     
  SummingMergeTree                                         

##### Supported Operations

  Simple   TABLE            
  -------- ---------------- --
  INSERT   DROP TABLE       
  DELETE   UNDROP TABLE     
  UPDATE   TRUNCATE TABLE   
  SELECT                    

### Performance

#### RQ.SRS-038.DiskObjectStorageVFS.Performance

version: 1.0

[Clickhouse](https://clickhouse.tech) DiskObjectStorageVFS shares
performance requirements with
[RQ.SRS-015.S3.Performance](https://github.com/Altinity/clickhouse-regression/blob/main/s3/requirements/requirements.md#performance)

### Object Storage Providers

#### RQ.SRS-038.DiskObjectStorageVFS.Providers.Configuration

version: 1.0

[ClickHouse](https://clickhouse.tech) SHALL support configuration of
object storage disks from a supported provider with syntax similar to
the following:

``` {.xml}
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

[ClickHouse](https://clickhouse.tech) SHALL support VFS on object
storage using [AWS S3](https://en.wikipedia.org/wiki/Amazon_S3).

#### RQ.SRS-038.DiskObjectStorageVFS.Providers.MinIO

version: 1.0

[ClickHouse](https://clickhouse.tech) SHALL support VFS on object
storage using [MinIO](https://en.wikipedia.org/wiki/MinIO).

#### RQ.SRS-038.DiskObjectStorageVFS.Providers.GCS

version: 1.0

[ClickHouse](https://clickhouse.tech) SHALL support VFS on object
storage using [Google Cloud
Storage](https://en.wikipedia.org/wiki/Google_Cloud_Storage).

References
----------

-   **AWS:** <https://en.wikipedia.org/wiki/Amazon_Web_Services>
-   **S3:** <https://en.wikipedia.org/wiki/Amazon_S3>
-   **ClickHouse:** <https://clickhouse.tech>
-   **GitHub Repository:**
    <https://github.com/Altinity/clickhouse-regression/tree/vfs_object_storage_testing/object_storage_vfs>
-   **Revision History:**
    <https://github.com/Altinity/clickhouse-regression/blob/vfs_object_storage_testing/object_storage_vfs/requirements/requirements.md>