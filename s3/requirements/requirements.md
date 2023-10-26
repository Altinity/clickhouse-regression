# SRS-015 ClickHouse S3 External Storage
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Terminology](#terminology)
* 4 [Requirements](#requirements)
  * 4.1 [Generic](#generic)
    * 4.1.1 [RQ.SRS-015.S3](#rqsrs-015s3)
    * 4.1.2 [RQ.SRS-015.S3.Import](#rqsrs-015s3import)
    * 4.1.3 [RQ.SRS-015.S3.Export](#rqsrs-015s3export)
    * 4.1.4 [RQ.SRS-015.S3.Disk](#rqsrs-015s3disk)
    * 4.1.5 [RQ.SRS-015.S3.Policy](#rqsrs-015s3policy)
    * 4.1.6 [RQ.SRS-015.S3.TableFunction](#rqsrs-015s3tablefunction)
    * 4.1.7 [RQ.SRS-015.S3.DataParts](#rqsrs-015s3dataparts)
    * 4.1.8 [RQ.SRS-015.S3.Security.Encryption](#rqsrs-015s3securityencryption)
    * 4.1.9 [RQ.SRS-015.S3.RemoteHostFilter](#rqsrs-015s3remotehostfilter)
    * 4.1.10 [Backup](#backup)
      * 4.1.10.1 [MinIO Backup](#minio-backup)
        * 4.1.10.1.1 [RQ.SRS-015.S3.Backup.MinIOBackup](#rqsrs-015s3backupminiobackup)
      * 4.1.10.2 [AWS S3 Backup](#aws-s3-backup)
        * 4.1.10.2.1 [RQ.SRS-015.S3.Backup.AWSS3Backup](#rqsrs-015s3backupawss3backup)
      * 4.1.10.3 [GCS Backup](#gcs-backup)
        * 4.1.10.3.1 [RQ.SRS-015.S3.Backup.GCSBackup](#rqsrs-015s3backupgcsbackup)
      * 4.1.10.4 [Storage Policies](#storage-policies)
        * 4.1.10.4.1 [RQ.SRS-015.S3.Backup.StoragePolicies](#rqsrs-015s3backupstoragepolicies)
      * 4.1.10.5 [Alter Freeze](#alter-freeze)
        * 4.1.10.5.1 [RQ.SRS-015.S3.Backup.AlterFreeze](#rqsrs-015s3backupalterfreeze)
      * 4.1.10.6 [Alter Detach](#alter-detach)
        * 4.1.10.6.1 [RQ.SRS-015.S3.Backup.AlterDetach](#rqsrs-015s3backupalterdetach)
      * 4.1.10.7 [Alter Attach](#alter-attach)
        * 4.1.10.7.1 [RQ.SRS-015.S3.Backup.AlterAttach](#rqsrs-015s3backupalterattach)
    * 4.1.11 [Metadata](#metadata)
      * 4.1.11.1 [RQ.SRS-015.S3.Metadata](#rqsrs-015s3metadata)
      * 4.1.11.2 [Revisions](#revisions)
        * 4.1.11.2.1 [RQ.SRS-015.S3.Metadata.Revisions](#rqsrs-015s3metadatarevisions)
      * 4.1.11.3 [Bad Backup Number](#bad-backup-number)
        * 4.1.11.3.1 [RQ.SRS-015.S3.Metadata.BadBackupNumber](#rqsrs-015s3metadatabadbackupnumber)
    * 4.1.12 [Metadata Restore](#metadata-restore)
      * 4.1.12.1 [Restore File](#restore-file)
        * 4.1.12.1.1 [RQ.SRS-0.5.S3.MetadataRestore.RestoreFile](#rqsrs-05s3metadatarestorerestorefile)
      * 4.1.12.2 [Bad Restore File](#bad-restore-file)
        * 4.1.12.2.1 [RQ.SRS-0.5.S3.MetadataRestore.BadRestoreFile](#rqsrs-05s3metadatarestorebadrestorefile)
      * 4.1.12.3 [Huge Restore File](#huge-restore-file)
        * 4.1.12.3.1 [RQ.SRS-0.5.S3.MetadataRestore.HugeRestoreFile](#rqsrs-05s3metadatarestorehugerestorefile)
      * 4.1.12.4 [No Local Metadata](#no-local-metadata)
        * 4.1.12.4.1 [RQ.SRS-015.S3.MetadataRestore.NoLocalMetadata](#rqsrs-015s3metadatarestorenolocalmetadata)
      * 4.1.12.5 [Bucket Path](#bucket-path)
        * 4.1.12.5.1 [RQ.SRS-015.S3.MetadataRestore.BucketPath](#rqsrs-015s3metadatarestorebucketpath)
      * 4.1.12.6 [Revision Restore](#revision-restore)
        * 4.1.12.6.1 [RQ.SRS-015.S3.MetadataRestore.RevisionRestore](#rqsrs-015s3metadatarestorerevisionrestore)
      * 4.1.12.7 [Mutations](#mutations)
        * 4.1.12.7.1 [RQ.SRS-015.S3.MetadataRestore.Mutations](#rqsrs-015s3metadatarestoremutations)
      * 4.1.12.8 [Parallel Mutations](#parallel-mutations)
        * 4.1.12.8.1 [RQ.SRS-015.S3.MetadataRestore.ParallelMutations](#rqsrs-015s3metadatarestoreparallelmutations)
      * 4.1.12.9 [Detached](#detached)
        * 4.1.12.9.1 [RQ.SRS-015.S3.MetadataRestore.Detached](#rqsrs-015s3metadatarestoredetached)
    * 4.1.13 [RQ.SRS-015.S3.AWS](#rqsrs-015s3aws)
    * 4.1.14 [RQ.SRS-015.S3.MinIO](#rqsrs-015s3minio)
    * 4.1.15 [RQ.SRS-015.S3.GCS](#rqsrs-015s3gcs)
    * 4.1.16 [Automatic Reconnects](#automatic-reconnects)
      * 4.1.16.1 [RQ.SRS-015.S3.AutomaticReconnects.GCS](#rqsrs-015s3automaticreconnectsgcs)
      * 4.1.16.2 [RQ.SRS-015.S3.AutomaticReconnects.AWS](#rqsrs-015s3automaticreconnectsaws)
      * 4.1.16.3 [RQ.SRS-015.S3.AutomaticReconnects.MinIO](#rqsrs-015s3automaticreconnectsminio)
  * 4.2 [Users](#users)
    * 4.2.1 [RQ.SRS-015.S3.User.Configuration.Cache.22.8.EnableFilesystemCache](#rqsrs-015s3userconfigurationcache228enablefilesystemcache)
    * 4.2.2 [RQ.SRS-015.S3.User.Configuration.Cache.22.8.EnableFilesystemCacheOnWriteOperations](#rqsrs-015s3userconfigurationcache228enablefilesystemcacheonwriteoperations)
  * 4.3 [RQ.SRS-015.S3.FilesystemCacheLog.22.8](#rqsrs-015s3filesystemcachelog228)
  * 4.4 [Disk](#disk)
    * 4.4.1 [RQ.SRS-015.S3.Disk.AddingMoreStorageDevices](#rqsrs-015s3diskaddingmorestoragedevices)
    * 4.4.2 [RQ.SRS-015.S3.Disk.Endpoints](#rqsrs-015s3diskendpoints)
    * 4.4.3 [RQ.SRS-015.S3.Disk.MultipleStorageDevices](#rqsrs-015s3diskmultiplestoragedevices)
    * 4.4.4 [RQ.SRS-015.S3.Disk.MultipleStorageDevices.NoChangesForQuerying](#rqsrs-015s3diskmultiplestoragedevicesnochangesforquerying)
    * 4.4.5 [RQ.SRS-015.S3.Disk.Metadata](#rqsrs-015s3diskmetadata)
    * 4.4.6 [Disk Configuration](#disk-configuration)
      * 4.4.6.1 [RQ.SRS-015.S3.Disk.Configuration](#rqsrs-015s3diskconfiguration)
      * 4.4.6.2 [RQ.SRS-015.S3.Disk.Configuration.Syntax](#rqsrs-015s3diskconfigurationsyntax)
      * 4.4.6.3 [RQ.SRS-015.S3.Disk.Configuration.Invalid](#rqsrs-015s3diskconfigurationinvalid)
      * 4.4.6.4 [RQ.SRS-015.S3.Disk.Configuration.Changes.NoRestart](#rqsrs-015s3diskconfigurationchangesnorestart)
      * 4.4.6.5 [RQ.SRS-015.S3.Disk.Configuration.Access](#rqsrs-015s3diskconfigurationaccess)
      * 4.4.6.6 [RQ.SRS-015.S3.Disk.Configuration.Access.Default](#rqsrs-015s3diskconfigurationaccessdefault)
      * 4.4.6.7 [RQ.SRS-015.S3.Disk.Configuration.CacheEnabled](#rqsrs-015s3diskconfigurationcacheenabled)
      * 4.4.6.8 [RQ.SRS-015.S3.Disk.Configuration.CacheEnabled.Default](#rqsrs-015s3diskconfigurationcacheenableddefault)
      * 4.4.6.9 [RQ.SRS-015.S3.Disk.Configuration.Cache.22.8](#rqsrs-015s3diskconfigurationcache228)
      * 4.4.6.10 [RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.CacheOnWriteOperations](#rqsrs-015s3diskconfigurationcache228cacheonwriteoperations)
      * 4.4.6.11 [RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.DataCacheMaxSize](#rqsrs-015s3diskconfigurationcache228datacachemaxsize)
      * 4.4.6.12 [RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.EnableCacheHitsThreshold](#rqsrs-015s3diskconfigurationcache228enablecachehitsthreshold)
      * 4.4.6.13 [RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.FileSystemQueryCacheLimit](#rqsrs-015s3diskconfigurationcache228filesystemquerycachelimit)
      * 4.4.6.14 [RQ.SRS-015.S3.Disk.Configuration.CachePath](#rqsrs-015s3diskconfigurationcachepath)
      * 4.4.6.15 [RQ.SRS-015.S3.Disk.Configuration.CachePath.Conflict](#rqsrs-015s3diskconfigurationcachepathconflict)
      * 4.4.6.16 [RQ.SRS-015.S3.Disk.Configuration.MinBytesForSeek](#rqsrs-015s3diskconfigurationminbytesforseek)
      * 4.4.6.17 [RQ.SRS-015.S3.Disk.Configuration.MinBytesForSeek.Syntax](#rqsrs-015s3diskconfigurationminbytesforseeksyntax)
      * 4.4.6.18 [RQ.SRS-015.S3.Disk.Configuration.S3MaxSinglePartUploadSize](#rqsrs-015s3diskconfigurations3maxsinglepartuploadsize)
      * 4.4.6.19 [RQ.SRS-015.S3.Disk.Configuration.S3MaxSinglePartUploadSize.Syntax](#rqsrs-015s3diskconfigurations3maxsinglepartuploadsizesyntax)
      * 4.4.6.20 [RQ.SRS-015.S3.Disk.Configuration.S3UseEnvironmentCredentials](#rqsrs-015s3diskconfigurations3useenvironmentcredentials)
    * 4.4.7 [MergeTree Engine Family](#mergetree-engine-family)
      * 4.4.7.1 [RQ.SRS-015.S3.Disk.MergeTree](#rqsrs-015s3diskmergetree)
      * 4.4.7.2 [RQ.SRS-015.S3.Disk.MergeTree.MergeTree](#rqsrs-015s3diskmergetreemergetree)
      * 4.4.7.3 [RQ.SRS-015.S3.Disk.MergeTree.ReplacingMergeTree](#rqsrs-015s3diskmergetreereplacingmergetree)
      * 4.4.7.4 [RQ.SRS-015.S3.Disk.MergeTree.SummingMergeTree](#rqsrs-015s3diskmergetreesummingmergetree)
      * 4.4.7.5 [RQ.SRS-015.S3.Disk.MergeTree.AggregatingMergeTree](#rqsrs-015s3diskmergetreeaggregatingmergetree)
      * 4.4.7.6 [RQ.SRS-015.S3.Disk.MergeTree.CollapsingMergeTree](#rqsrs-015s3diskmergetreecollapsingmergetree)
      * 4.4.7.7 [RQ.SRS-015.S3.Disk.MergeTree.VersionedCollapsingMergeTree](#rqsrs-015s3diskmergetreeversionedcollapsingmergetree)
      * 4.4.7.8 [S3 Zero Copy Replication](#s3-zero-copy-replication)
        * 4.4.7.8.1 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication](#rqsrs-015s3diskmergetreeallows3zerocopyreplication)
        * 4.4.7.8.2 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Default](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationdefault)
        * 4.4.7.8.3 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Global](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationglobal)
        * 4.4.7.8.4 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Metadata](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationmetadata)
        * 4.4.7.8.5 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Alter](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationalter)
        * 4.4.7.8.6 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Delete](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationdelete)
        * 4.4.7.8.7 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.DeleteAll](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationdeleteall)
        * 4.4.7.8.8 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.DropReplica](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationdropreplica)
        * 4.4.7.8.9 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.AddReplica](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationaddreplica)
        * 4.4.7.8.10 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.NoDataDuplication](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationnodataduplication)
        * 4.4.7.8.11 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.TTL.Move](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationttlmove)
        * 4.4.7.8.12 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.TTL.Delete](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationttldelete)
  * 4.5 [Policy](#policy)
    * 4.5.1 [RQ.SRS-015.S3.Policy.Syntax](#rqsrs-015s3policysyntax)
    * 4.5.2 [RQ.SRS-015.S3.Policy.PerformTTLMoveOnInsert](#rqsrs-015s3policyperformttlmoveoninsert)
    * 4.5.3 [RQ.SRS-015.S3.Policy.PerformTTLMoveOnInsert.Default](#rqsrs-015s3policyperformttlmoveoninsertdefault)
  * 4.6 [Table Function](#table-function)
    * 4.6.1 [RQ.SRS-015.S3.TableFunction.Syntax](#rqsrs-015s3tablefunctionsyntax)
    * 4.6.2 [RQ.SRS-015.S3.TableFunction.Path](#rqsrs-015s3tablefunctionpath)
    * 4.6.3 [RQ.SRS-015.S3.TableFunction.Credentials](#rqsrs-015s3tablefunctioncredentials)
    * 4.6.4 [RQ.SRS-015.S3.TableFunction.Credentials.Invalid](#rqsrs-015s3tablefunctioncredentialsinvalid)
    * 4.6.5 [RQ.SRS-015.S3.TableFunction.Path.Wildcard](#rqsrs-015s3tablefunctionpathwildcard)
    * 4.6.6 [RQ.SRS-015.S3.TableFunction.ReadFromFile](#rqsrs-015s3tablefunctionreadfromfile)
    * 4.6.7 [RQ.SRS-015.S3.TableFunction.Redirect](#rqsrs-015s3tablefunctionredirect)
    * 4.6.8 [RQ.SRS-015.S3.TableFunction.Format](#rqsrs-015s3tablefunctionformat)
    * 4.6.9 [RQ.SRS-015.S3.TableFunction.Structure](#rqsrs-015s3tablefunctionstructure)
    * 4.6.10 [RQ.SRS-015.S3.TableFunction.Compression](#rqsrs-015s3tablefunctioncompression)
    * 4.6.11 [RQ.SRS-015.S3.TableFunction.Compression.Auto](#rqsrs-015s3tablefunctioncompressionauto)
    * 4.6.12 [RQ.SRS-015.S3.TableFunction.S3Cluster](#rqsrs-015s3tablefunctions3cluster)
  * 4.7 [MinIO](#minio)
    * 4.7.1 [RQ.SRS-015.S3.MinIO.Disk.Configuration](#rqsrs-015s3miniodiskconfiguration)
    * 4.7.2 [RQ.SRS-015.S3.MinIO.TableFunction](#rqsrs-015s3miniotablefunction)
    * 4.7.3 [RQ.SRS-015.S3.MinIO.AllowS3ZeroCopyReplication](#rqsrs-015s3minioallows3zerocopyreplication)
  * 4.8 [AWS](#aws)
    * 4.8.1 [RQ.SRS-015.S3.AWS.Disk.Configuration](#rqsrs-015s3awsdiskconfiguration)
    * 4.8.2 [RQ.SRS-015.S3.AWS.TableFunction](#rqsrs-015s3awstablefunction)
    * 4.8.3 [RQ.SRS-015.S3.AWS.Disk.URL](#rqsrs-015s3awsdiskurl)
    * 4.8.4 [RQ.SRS-015.S3.AWS.Disk.URL.Generic](#rqsrs-015s3awsdiskurlgeneric)
    * 4.8.5 [RQ.SRS-015.S3.AWS.Disk.URL.Specific](#rqsrs-015s3awsdiskurlspecific)
    * 4.8.6 [RQ.SRS-015.S3.AWS.EC2.Disk](#rqsrs-015s3awsec2disk)
    * 4.8.7 [RQ.SRS-015.S3.AWS.EC2.TableFunction](#rqsrs-015s3awsec2tablefunction)
    * 4.8.8 [RQ.SRS-015.S3.AWS.EC2.Endpoints](#rqsrs-015s3awsec2endpoints)
    * 4.8.9 [RQ.SRS-015.S3.AWS.AllowS3ZeroCopyReplication](#rqsrs-015s3awsallows3zerocopyreplication)
    * 4.8.10 [RQ.SRS-015.S3.AWS.SSEC](#rqsrs-015s3awsssec)
  * 4.9 [GCS](#gcs)
    * 4.9.1 [RQ.SRS-015.S3.GCS.Disk.Configuration](#rqsrs-015s3gcsdiskconfiguration)
    * 4.9.2 [RQ.SRS-015.S3.GCS.TableFunction](#rqsrs-015s3gcstablefunction)
    * 4.9.3 [RQ.SRS-015.S3.GCS.AllowS3ZeroCopyReplication](#rqsrs-015s3gcsallows3zerocopyreplication)
  * 4.10 [Settings](#settings)
    * 4.10.1 [RQ.SRS-015.S3.Settings.MaxThreads](#rqsrs-015s3settingsmaxthreads)
    * 4.10.2 [RQ.SRS-015.S3.Settings.MaxDownloadThreads](#rqsrs-015s3settingsmaxdownloadthreads)
    * 4.10.3 [RQ.SRS-015.S3.Settings.MaxDownloadBufferSize](#rqsrs-015s3settingsmaxdownloadbuffersize)
    * 4.10.4 [RQ.SRS-015.S3.Settings.PartitionBy](#rqsrs-015s3settingspartitionby)
    * 4.10.5 [RQ.SRS-015.S3.Settings.S3UploadPartSizeMultiplyFactor](#rqsrs-015s3settingss3uploadpartsizemultiplyfactor)
    * 4.10.6 [RQ.SRS-015.S3.Settings.S3UploadPartSizeMultiplyPartsCountThreshold](#rqsrs-015s3settingss3uploadpartsizemultiplypartscountthreshold)
  * 4.11 [Performance](#performance)
    * 4.11.1 [RQ.SRS-015.S3.Performance.PerformTTLMoveOnInsert](#rqsrs-015s3performanceperformttlmoveoninsert)
    * 4.11.2 [RQ.SRS-015.S3.Performance.AllowS3ZeroCopyReplication.Select](#rqsrs-015s3performanceallows3zerocopyreplicationselect)
    * 4.11.3 [RQ.SRS-015.S3.Performance.AllowS3ZeroCopyReplication.Insert](#rqsrs-015s3performanceallows3zerocopyreplicationinsert)
    * 4.11.4 [RQ.SRS-015.S3.Performance.AllowS3ZeroCopyReplication.Alter](#rqsrs-015s3performanceallows3zerocopyreplicationalter)
* 5 [References](#references)

## Revision History

This document is stored in an electronic form using [Git] source control
management software hosted in a [GitLab Repository]. All the updates are tracked
using the [Revision History].

## Introduction

[ClickHouse] currently has support for [AWS S3] storage and S3-compatible storage
through storage disks configured for [S3] and through [S3] table functions. The user
may import from [S3] storage and export to [S3] storage using the above methods.

## Terminology

* **Default disk** -
  the one specified in current ClickHouse configuration, usually: `<path>/var/lib/clickhouse</path>`

* **Disk** - mounted storage device.

* **JBOD** - Just a Bunch of Disks.

* **Part** -
  atomic data part from [ClickHouse] prospective, produced either by insert or merge process.
  Stored as a separate directory at the file system.

* **Volume** - one or multiple disks, combined together as a JBOD array.

## Requirements

### Generic

#### RQ.SRS-015.S3
version: 1.0

[ClickHouse] SHALL support external object storage using [AWS S3] and
S3-compatible storage.

#### RQ.SRS-015.S3.Import
version: 1.0

[ClickHouse] SHALL support importing files from [S3] external storage using
the [S3] table function or storage disks configured for [S3] storage.

#### RQ.SRS-015.S3.Export
version: 1.0

[ClickHouse] SHALL support exporting files to [S3] external storage using
the [S3] table function or storage disks configured for [S3] storage.

#### RQ.SRS-015.S3.Disk
version: 1.0

[ClickHouse] SHALL support [S3] external storage via one or more storage disks.

#### RQ.SRS-015.S3.Policy
version: 1.0

[ClickHouse] SHALL support selection of [S3] disks using policies defined in the
`<policies>` section of the `<storage_configuration>` section of the config.xml
file or the storage.xml file in the config.d directory.

#### RQ.SRS-015.S3.TableFunction
version: 1.0

[ClickHouse] SHALL support [S3] external storage via a call to the [S3] table
function. Using the table function, [ClickHouse] SHALL provide read and write
functionality. Upon a write to a location with data already stored, [ClickHouse]
SHALL overwrite existing data.

#### RQ.SRS-015.S3.DataParts
version: 1.0

[ClickHouse] SHALL support [S3] external storage of data parts as Wide parts,
Compact parts, or a combination of both types. The user may view the full storage
of data parts in the system.parts table.

#### RQ.SRS-015.S3.Security.Encryption
version: 1.0

[ClickHouse] SHALL support sending the `x-amz-server-side-encryption-customer-key`
header and the `x-amz-server-side-encryption-customer-key-md5` header as part of
the query when the S3 resouce is server-side encrypted.

#### RQ.SRS-015.S3.RemoteHostFilter
version: 1.0

[ClickHouse] SHALL support a remote host filter to prevent access to untrusted URL
addresses. The remote host filter configuration SHALL be similar to the following:

``` xml
<yandex>
    <!-- The list of hosts allowed to use in URL-related storage engines and table functions.
        If this section is not present in configuration, all hosts are allowed.
    -->
    <remote_url_allow_hosts>
        <!-- Host should be specified exactly as in URL. The name is checked before DNS resolution.
            Example: "yandex.ru", "yandex.ru." and "www.yandex.ru" are different hosts.
                If port is explicitly specified in URL, the host:port is checked as a whole.
                If host specified here without port, any port with this host allowed.
                "yandex.ru" -> "yandex.ru:443", "yandex.ru:80" etc. is allowed, but "yandex.ru:80" -> only "yandex.ru:80" is allowed.
                If the host is specified as IP address, it is checked as specified in URL. Example: "[2a02:6b8:a::a]".
                If there are redirects and support for redirects is enabled, every redirect (the Location field) is checked.
        -->
        <host>www.myhost.com</host>

        <!-- Regular expression can be specified. RE2 engine is used for regexps.
            Regexps are not aligned: don't forget to add ^ and $. Also don't forget to escape dot (.) metacharacter
            (forgetting to do so is a common source of error).
        -->
        <host_regexp>^.*\.myhost\.com$</host_regexp>
    </remote_url_allow_hosts>
</yandex>
```
#### Backup

##### MinIO Backup

###### RQ.SRS-015.S3.Backup.MinIOBackup
version: 1.0

[ClickHouse] SHALL support manual backups of tables that use minio storage.

##### AWS S3 Backup

###### RQ.SRS-015.S3.Backup.AWSS3Backup
version: 1.0

[ClickHouse] SHALL support manual backups of tables that use aws s3 storage.

##### GCS Backup

###### RQ.SRS-015.S3.Backup.GCSBackup
version: 1.0

[ClickHouse] SHALL support manual backups of tables that use gcs storage.

##### Storage Policies

###### RQ.SRS-015.S3.Backup.StoragePolicies
version: 1.0

[ClickHouse] SHALL support using creating manual backups of tables that use storage policies containing:
* one volume with s3 disk
* one volume with s3 and local disk
* multiple volumes with s3 and local disks

##### Alter Freeze

###### RQ.SRS-015.S3.Backup.AlterFreeze
version: 1.0

[ClickHouse] SHALL support using `ALTER TABLE FREEZE` on tables that use S3 in the storage policy. If the policy includes a local disk,
the query will create a local backup in the `shadow/` directory of the working ClickHouse directory (`/var/lib/clickhouse` by default).

##### Alter Detach

###### RQ.SRS-015.S3.Backup.AlterDetach
version: 1.0

[ClickHouse] SHALL support using `ALTER TABLE DETACH PARTITION` on partitions of tables that use S3.

##### Alter Attach

###### RQ.SRS-015.S3.Backup.AlterAttach
version: 1.0

[ClickHouse] SHALL support restoring backups of tables using `ALTER TABLE ATTACH PARTITION` from data inside
`/var/lib/clickhouse/data/database/table/detached/`.

#### Metadata

##### RQ.SRS-015.S3.Metadata
version: 1.0

[ClickHouse] SHALL store disk metadata of tables with S3 disk
if and only if they have `<send_metadata>` set to `true` in the disk config.
The disk metadata is stored in `/var/lib/clickhouse/disks/{disk name}/`.
The metadata is stored in the s3 bucket.

##### Revisions

###### RQ.SRS-015.S3.Metadata.Revisions
version: 1.0

[ClickHouse] SHALL keep a revision counter for each table and change the counter for
every insert, merge, or remove operation. The revision counter in stored in
`/var/lib/clickhouse/disks/s3/shadow/{backup number}/revision.txt`, where
the backup number indicated how many times `ALTER FREEZE` has been used on the table.

##### Bad Backup Number

###### RQ.SRS-015.S3.Metadata.BadBackupNumber
version: 1.0

[ClickHouse] SHALL

#### Metadata Restore

##### Restore File

###### RQ.SRS-0.5.S3.MetadataRestore.RestoreFile
version: 1.0

[ClickHouse] SHALL support restoring tables using a restore file
located in `/var/lib/clickhouse/disks/{disk name}/restore` and executing
`SYSTEM RESTART DISK` and reattaching the table.

##### Bad Restore File

###### RQ.SRS-0.5.S3.MetadataRestore.BadRestoreFile
version: 1.0

[ClickHouse] SHALL not support restoring tables using a restore file
located in `/var/lib/clickhouse/disks/{disk name}/restore` that contains
a wrong bucket, path, or revision value.

##### Huge Restore File

###### RQ.SRS-0.5.S3.MetadataRestore.HugeRestoreFile
version: 1.0

[ClickHouse] SHALL not support restoring tables using a restore file
located in `/var/lib/clickhouse/disks/{disk name}/restore` that contains
a large amount of not usable information.

##### No Local Metadata

###### RQ.SRS-015.S3.MetadataRestore.NoLocalMetadata
version: 1.0

[ClickHouse] SHALL support restoring a table from the restore file
located in `/var/lib/clickhouse/disks/{disk name}/restore` even
if the local metadata has been purged.

##### Bucket Path

###### RQ.SRS-015.S3.MetadataRestore.BucketPath
version: 1.0

[ClickHouse] SHALL support restoring a table to a specific bucket and path by indicating them
in the restore file located in `/var/lib/clickhouse/disks/{disk name}/restore`
using the following syntax:
```
'source_path' = {path}
'source_bucket' = {bucket}
```

##### Revision Restore

###### RQ.SRS-015.S3.MetadataRestore.RevisionRestore
version: 1.0

[ClickHouse] SHALL support restoring a table to a specific revision version.
The table shall restore to the original bucket and path if and only if it is the latest revision.
The revision can be indicated in the restore file located in `/var/lib/clickhouse/disks/{disk name}/restore`:
```
'revision' = {revision number}
```

##### Mutations

###### RQ.SRS-015.S3.MetadataRestore.Mutations
version: 1.0

[ClickHouse] SHALL support restoring a table to a state before, during, or after a mutation.

##### Parallel Mutations

###### RQ.SRS-015.S3.MetadataRestore.ParallelMutations
version: 1.0

[ClickHouse] SHALL support restoring a table correctly even when mutations
are being added in parallel with the restore process.

##### Detached

###### RQ.SRS-015.S3.MetadataRestore.Detached
version: 1.0

[ClickHouse] SHALL support restoring tables with a detached partition and
the ability to reattach that partition even if it was detached before the `ALTER FREEZE` backup.
It can be indicated in the restore file located in `/var/lib/clickhouse/disks/{disk name}/restore`:
```
'detached' = true
```

#### RQ.SRS-015.S3.AWS
version: 1.0

[ClickHouse] SHALL support [S3] external storage using [AWS S3].

#### RQ.SRS-015.S3.MinIO
version: 1.0

[ClickHouse] SHALL support [S3] external storage using MinIO.

#### RQ.SRS-015.S3.GCS
version: 1.0

[ClickHouse] SHALL support [S3] external storage using Google Cloud Storage.

#### Automatic Reconnects

##### RQ.SRS-015.S3.AutomaticReconnects.GCS
version: 1.0

[ClickHouse] SHALL support automatically reconnecting to GCS if the network connection has been interrupted.

##### RQ.SRS-015.S3.AutomaticReconnects.AWS
version: 1.0

[ClickHouse] SHALL support automatically reconnecting to AWS S3 if the network connection has been interrupted.

##### RQ.SRS-015.S3.AutomaticReconnects.MinIO
version: 1.0

[ClickHouse] SHALL support automatically reconnecting to MinIO if the network connection has been interrupted.

### Users

#### RQ.SRS-015.S3.User.Configuration.Cache.22.8.EnableFilesystemCache
version: 1.0

[ClickHouse] SHALL support setting `<enable_filesystem_cache>` parameter
when defining a user in the `<profiles>` section.
This is only available in versions 22.8 and later.

#### RQ.SRS-015.S3.User.Configuration.Cache.22.8.EnableFilesystemCacheOnWriteOperations
version: 1.0

[ClickHouse] SHALL support setting `<enable_filesystem_cache_on_write_operations>` parameter
when defining a user in the `<profiles>` section.
This is only available in versions 22.8 and later.

### RQ.SRS-015.S3.FilesystemCacheLog.22.8
version: 1.0

[ClickHouse] SHALL support setting `<database>` and `<table`> parameters
in the `<filesystem_cache_log>` section of configs.xml or any other xml in the config.d directory.
This is only available in versions 22.8 and later.

### Disk

#### RQ.SRS-015.S3.Disk.AddingMoreStorageDevices
version: 1.0

[ClickHouse] SHALL support adding more storage devices to the existing [ClickHouse] server.

#### RQ.SRS-015.S3.Disk.Endpoints
version: 1.0

[ClickHouse] SHALL support configuration of [S3] endpoints in the config.xml file
using credentials accessible to the entire ClickHouse server, with syntax similar
to the following:

``` xml
<yandex>
    <s3>
       <my_endpoint>
           <endpoint>http://s3.us-east-1.amazonaws.com/my-bucket/</endpoint>
           <access_key_id>*****</access_key_id>
           <secret_access_key>*****</secret_access_key>
           <header>Authorization: Bearer TOKEN</header>
       </my_endpoint>
   </s3>
</yandex>
```

#### RQ.SRS-015.S3.Disk.MultipleStorageDevices
version: 1.0

[ClickHouse] SHALL support storing data to multiple [S3] storage devices.

#### RQ.SRS-015.S3.Disk.MultipleStorageDevices.NoChangesForQuerying
version: 1.0

[ClickHouse] SHALL require no changes to query statements when querying data
from a table that supports multiple [S3] storage devices.

#### RQ.SRS-015.S3.Disk.Metadata
version: 1.0

[ClickHouse] SHALL create a metadata file for each [S3] disk which tracks the total
number of objects stored in the disk, the aggregate size of the objects, and for each
object stored in the disk, tracks the path to the object and the object size.

#### Disk Configuration

##### RQ.SRS-015.S3.Disk.Configuration
version: 1.0

[ClickHouse] SHALL support configuration of one or more [S3] disks in the `<disks>`
section of the `<storage_configuration>` section of the config.xml file or the
storage.xml file in the config.d directory.

##### RQ.SRS-015.S3.Disk.Configuration.Syntax
version: 1.0

[ClickHouse] SHALL support [S3] disk configuration using syntax similar to the
following:

``` xml
<yandex>
  <storage_configuration>
    <disks>
      <s3>
        <type>s3</type>
        <endpoint>http://s3.us-east-1.amazonaws.com/my-bucket/</endpoint>
        <access_key_id>*****</access_key_id>
        <secret_access_key>*****</secret_access_key>
      </s3>
    </disks>
...
</yandex>
```

##### RQ.SRS-015.S3.Disk.Configuration.Invalid
version: 1.0

[ClickHouse] SHALL return an error if the [S3] disk configuration is not valid.

##### RQ.SRS-015.S3.Disk.Configuration.Changes.NoRestart
version: 1.0

[ClickHouse] server SHALL not need to be restarted when storage device
configuration changes except some special cases.

##### RQ.SRS-015.S3.Disk.Configuration.Access
version: 1.1

[ClickHouse] SHALL support the `<skip_access_check>` parameter in the `<disks>`
section of the `<storage_configuration>` section of the config.xml file or the
storage.xml file in the config.d directory to toggle a runtime check for access
to the corresponding [S3] disk. If this runtime check fails, [ClickHouse] SHALL
return an "Access Denied" error. The specifics of the error depend on version:
 - In [Clickhouse] < 22.9 the error message SHALL be `DB::Exception: Access Denied.`
else `DB::Exception: Message: Access Denied`
 - In [Clickhouse] >= 23.8 the error SHALL be returned from CREATE TABLE,
else CREATE TABLE SHALL succeed and the error SHALL be returned from INSERT INTO


##### RQ.SRS-015.S3.Disk.Configuration.Access.Default
version: 1.0

[ClickHouse] SHALL set the `<skip_access_check>` parameter to 0 by default to
perform an access check.

##### RQ.SRS-015.S3.Disk.Configuration.CacheEnabled
version: 1.0

[ClickHouse] SHALL support the `<cache_enabled>` parameter in the `<disks>`
section of the `<storage_configuration>` section of the config.xml file or the
storage.xml file in the config.d directory to toggle caching for the
corresponding [S3] disk.

In 22.8 and later, this parameter has been renamed to `<data_cache_enabled>`.

##### RQ.SRS-015.S3.Disk.Configuration.CacheEnabled.Default
version: 1.0

[ClickHouse] SHALL set the `<cache_enabled>` parameter to 1 by default to
enable caching.

##### RQ.SRS-015.S3.Disk.Configuration.Cache.22.8
version: 1.0

[ClickHouse] SHALL support defining cache storage in the in the `<disks>`
section of the `<storage_configuration>` section of the config.xml file or the
storage.xml file in the config.d directory to toggle caching for the
corresponding [S3] disk in version 22.8 and later.

The definition requires `<type>`, `<disk>`, `<path>`, `<max_size>`, and `<do_not_evict_index_and_mark_files>` parameters.

Example:
```
<s3_cache>
    <type>cache</type>
    <disk>s3_disk</disk>
    <path>s3_disk_cache/</path>
    <max_size>22548578304</max_size>
    <do_not_evict_index_and_mark_files>0</do_not_evict_index_and_mark_files>
</s3_cache>
```

##### RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.CacheOnWriteOperations
version: 1.0

[ClickHouse] SHALL support setting `<cache_on_write_operations>` parameter
when defining a cache. This is only available in versions 22.8 and later.

##### RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.DataCacheMaxSize
version: 1.0

[ClickHouse] SHALL support setting `<data_cache_max_size>` parameter
when defining a cache. This is only available in versions 22.8 and later.

##### RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.EnableCacheHitsThreshold
version: 1.0

[ClickHouse] SHALL support setting `<enable_cache_hits_threshold>` parameter
when defining a cache. This is only available in versions 22.8 and later.

##### RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.FileSystemQueryCacheLimit
version: 1.0

[ClickHouse] SHALL support setting `<enable_filesystem_query_cache_limit>` parameter
when defining a cache. This is only available in versions 22.8 and later.

##### RQ.SRS-015.S3.Disk.Configuration.CachePath
version: 1.0

[ClickHouse] SHALL support the `<cache_path>` parameter in the `<disks>`
section of the `<storage_configuration>` section of the config.xml file or the
storage.xml file in the config.d directory to set the path to the disk cache.
This will have no effect if the `<cache_enabled>` parameter is set to 0.

##### RQ.SRS-015.S3.Disk.Configuration.CachePath.Conflict
version: 1.0

[ClickHouse] SHALL throw an error if the `<cache_path>` parameter in the
`<disks>` section of the `<storage_configuration>` section of the config.xml
file or the storage.xml file in the config.d directory is set such that the
path to the disk metadata and the path to the disk cache are the same.
The error SHALL be similar to the following:

    "DB::Exception: Metadata and cache path should be different"

##### RQ.SRS-015.S3.Disk.Configuration.MinBytesForSeek
version: 1.0

[ClickHouse] SHALL support the `<min_bytes_for_seek>` parameter in the `<disks>`
section of the `<storage_configuration>` section of the config.xml file or the
storage.xml file in the config.d directory to set the minimum number of
bytes to seek forward through the file.

##### RQ.SRS-015.S3.Disk.Configuration.MinBytesForSeek.Syntax
version: 1.0

[ClickHouse] SHALL run with no errors when the `<min_bytes_for_seek>` parameter
in the `<disks>` section of the `<storage_configuration>` section of the
config.xml file or the storage.xml file in the config.d directory is configured
with correct syntax.

##### RQ.SRS-015.S3.Disk.Configuration.S3MaxSinglePartUploadSize
version: 1.0

[ClickHouse] SHALL support the `<s3_max_single_part_upload_size>` parameter in
the `<disks>` section of the `<storage_configuration>` section of the config.xml
file or the storage.xml file in the config.d directory to set the maximum
size, in bytes, of single part uploads to S3.

##### RQ.SRS-015.S3.Disk.Configuration.S3MaxSinglePartUploadSize.Syntax
version: 1.0

[ClickHouse] SHALL run with no errors when the
`<s3_max_single_part_upload_size>` parameter in the `<disks>` section of the
`<storage_configuration>` section of the config.xml file or the storage.xml
file in the config.d directory is configured with correct syntax.

##### RQ.SRS-015.S3.Disk.Configuration.S3UseEnvironmentCredentials
version: 1.0

[ClickHouse] SHALL support the `<s3_use_environment_credentials>` parameter in
the `<disks>` section of the `<storage_configuration>` section of the config.xml
file or the storage.xml file in the config.d directory to use the server
environment credentials set in the config.xml file.

#### MergeTree Engine Family

##### RQ.SRS-015.S3.Disk.MergeTree
version: 1.0

[ClickHouse] SHALL support selection of one or more [S3] external storage disks using
engines in the MergeTree engine family.

##### RQ.SRS-015.S3.Disk.MergeTree.MergeTree
version: 1.0

[ClickHouse] SHALL support selection of one or more [S3] external storage disks using
the MergeTree engine.

##### RQ.SRS-015.S3.Disk.MergeTree.ReplacingMergeTree
version: 1.0

[ClickHouse] SHALL support selection of one or more [S3] external storage disks using
the ReplacingMergeTree engine.

##### RQ.SRS-015.S3.Disk.MergeTree.SummingMergeTree
version: 1.0

[ClickHouse] SHALL support selection of one or more [S3] external storage disks using
the SummingMergeTree engine.

##### RQ.SRS-015.S3.Disk.MergeTree.AggregatingMergeTree
version: 1.0

[ClickHouse] SHALL support selection of one or more [S3] external storage disks using
the AggregatingMergeTree engine.

##### RQ.SRS-015.S3.Disk.MergeTree.CollapsingMergeTree
version: 1.0

[ClickHouse] SHALL support selection of one or more [S3] external storage disks using
the CollapsingMergeTree engine.

##### RQ.SRS-015.S3.Disk.MergeTree.VersionedCollapsingMergeTree
version: 1.0

[ClickHouse] SHALL support selection of one or more [S3] external storage disks using
the VersionedCollapsingMergeTree engine.

##### S3 Zero Copy Replication

###### RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication
version: 1.0

[ClickHouse] SHALL support `<allow_s3_zero_copy_replication>` as a MergeTree
table engine setting for the ReplicatedMergeTree engine to toggle data
replication via S3 for replicated tables.

###### RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Default
version: 1.0

[ClickHouse] SHALL set the `<allow_s3_zero_copy_replication>` parameter to 0 by
default to disable data replication via S3 and replicate data directly when using
the ReplicatedMergeTree table engine.

###### RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Global
version: 1.0

[ClickHouse] SHALL support the `<allow_s3_zero_copy_replication>` setting to the
`<merge_tree>` section of the config.xml file or the merge_tree.xml file in
the config.d directory to configure the ReplicatedMergeTree engine globally. This
setting SHALL be applied to all ReplicatedMergeTree tables.

###### RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Metadata
version: 1.0

[ClickHouse] SHALL replicate only S3 metadata when the
`<allow_s3_zero_copy_replication>` parameter is set to 1. The receiver of the
metadata SHALL create identical metadata files which refer to the same object
keys in S3.

###### RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Alter
version: 1.0

[ClickHouse] SHALL support modifying replicated tables. If a replicated table
is modified, the changes SHALL be reproduced on all existing replicas, and
in [S3] storage.

###### RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Delete
version: 1.0

[ClickHouse] SHALL support dropping a replicated table with no changes to any
other replicas of the table. If the table is dropped normally, [ClickHouse]
SHALL delete only local metadata associated with the replicated table. If the
table is dropped using the SYNC keyword, [ClickHouse] SHALL delete the local
metadata and all associated data stored in [S3]. Other replicas will no
longer be able to access this data.

    ```sql
    DROP TABLE table_name SYNC;
    ```

###### RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.DeleteAll
version: 1.0

[ClickHouse] SHALL support deleting replicated tables from [S3] by dropping
all replicas of the table from each [ClickHouse] instance. For data to be
removed from [S3], data must be dropped using the SYNC keyword.

    ```sql
    DROP TABLE table_name SYNC;
    ```

###### RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.DropReplica
version: 1.0

[ClickHouse] SHALL support stopping and starting an instance of [ClickHouse]
with no changes to data in replicated tables. If the table is altered while
the instance restarts, [ClickHouse] SHALL update the table from [S3] when
the instance restarts.

###### RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.AddReplica
version: 1.0

[ClickHouse] SHALL support adding a replica of an existing replicated table
with no changes to the data in the table. When the replica is added, the
existing data SHALL be downloaded from [S3] to match the other replicas.

###### RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.NoDataDuplication
version: 1.0

[ClickHouse] SHALL support zero copy replication such that data is not
duplicated in [S3] storage during any operations on replicated tables (ALTER,
SELECT, INSERT, etc...).  Data SHALL be fully removed from [S3] via DELETE
operations.

###### RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.TTL.Move
version: 1.0

[ClickHouse] SHALL support TTL moves to other hard disks or [S3] disks when the
`<allow_s3_zero_copy_replication>` setting is used with the MergeTree engine.
When TTL moves are used, data will not be duplicated in [S3]. All objects in
a table SHALL be accessible with no errors, even if they have been moved
to a different disk.

###### RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.TTL.Delete
version: 1.0

[ClickHouse] SHALL support TTL object deletion when the
`<allow_s3_zero_copy_replication>` setting is used with the MergeTree engine.
When objects are removed, all other objects SHALL be accessible with no errors.

### Policy

#### RQ.SRS-015.S3.Policy.Syntax
version: 1.0

[ClickHouse] SHALL support selection of an [S3] disk for a volume using policies
with syntax similar to the following examples.

`<tiered>` shows a policy with an [S3] volume alongside another volume.

`<s3only>` shows a policy with only an [S3] volume.

``` xml
<yandex>
  <storage_configuration>
...
    <policies>
      <tiered>
        <volumes>
          <default>
            <disk>default</disk>
          </default>
          <s3>
            <disk>s3</disk>
          </s3>
        </volumes>
      </tiered>
      <s3only>
        <volumes>
          <s3>
            <disk>s3</disk>
          </s3>
        </volumes>
      </s3only>
    </policies>
  </storage_configuration>
</yandex>
```

#### RQ.SRS-015.S3.Policy.PerformTTLMoveOnInsert
version: 1.0

[ClickHouse] SHALL support the `<perform_ttl_move_on_insert>` parameter to the
`<volume>` section of the desired [S3] disk in the `<policies>` section of the
`<storage_configuration>` section of the config.xml file or the storage.xml file
in the config.d directory to toggle TTL moves to the [S3] disk on insert
operations. If `<perform_ttl_move_on_insert>` is set to 0, insert will go to the
first disk in the storage policy, and TTL moves to the [S3] volume will occur in
the background.

#### RQ.SRS-015.S3.Policy.PerformTTLMoveOnInsert.Default
version: 1.0

[ClickHouse] SHALL set the `<perform_ttl_move_on_insert>` parameter to 1 by
default to perform TTL moves immediately upon an insert operation.

### Table Function

#### RQ.SRS-015.S3.TableFunction.Syntax
version: 1.0

[ClickHouse] SHALL support the following syntax for the [S3] table function.

``` sql
s3(path, [access_key_id, secret_access_key,] format, structure, [compression])
```

#### RQ.SRS-015.S3.TableFunction.Path
version: 1.0

[ClickHouse] SHALL support the `<path>` parameter to the [S3] table function to
specify the url of the [S3] bucket and the path to the file. This parameter SHALL
be mandatory.

#### RQ.SRS-015.S3.TableFunction.Credentials
version: 1.0

[ClickHouse] SHALL support the `<access_key_id>` and `<secret_access_key>`
parameters to the [S3] table function to authorize access to the [S3] bucket url
specified in the `<path>` parameter.

#### RQ.SRS-015.S3.TableFunction.Credentials.Invalid
version: 1.0

[ClickHouse] SHALL return an error if the `<aws_access_key_id>` and
`<aws_secret_access_key>` parameters do not provide correct authentication to
the [S3] bucket.

#### RQ.SRS-015.S3.TableFunction.Path.Wildcard
version: 1.0

[ClickHouse] SHALL support the following wildcards for the `<path>` parameter
to the [S3] table function, where 'abc', 'def' SHALL be strings and 'N', 'M' SHALL
be numbers. Note: the `?` wildcard must be encoded as `%3F`.

* `*`
* `?`
* `{abc,def}`
* `{N..M}`

#### RQ.SRS-015.S3.TableFunction.ReadFromFile
version: 1.0

[ClickHouse] SHALL support reading data into the [S3] table function from a file,
with syntax similar to the following:

``` bash
    cat test.csv | INSERT INTO TABLE FUNCTION s3(...)
```

#### RQ.SRS-015.S3.TableFunction.Redirect
version: 1.0

[ClickHouse] SHALL support [S3] table function urls which cause redirects with
no errors.

#### RQ.SRS-015.S3.TableFunction.Format
version: 1.0

[ClickHouse] SHALL support the `<format>` parameter to the [S3] table function to
specify the format of the data using one of the following [data formats].

#### RQ.SRS-015.S3.TableFunction.Structure
version: 1.0

[ClickHouse] SHALL support the `<structure>` parameter to the [S3] table function to
specify the structure of the data. The structure SHALL use the following format:

    'column1_name column1_type, column2_name column2_type, ...'

#### RQ.SRS-015.S3.TableFunction.Compression
version: 1.0

[ClickHouse] SHALL support the `<compression>` parameter as an optional parameter
to the [S3] table function to specify the compression method used with the data.
The following compression methods are supported:

* `gzip`
* `zlib`
* `brotli`
* `xz`
* `zstd`

#### RQ.SRS-015.S3.TableFunction.Compression.Auto
version: 1.0

[ClickHouse] SHALL support 'auto' as an input to the `<compression>` parameter of
the [S3] table function. If 'auto' is specified, [ClickHouse] SHALL deduce the
compression algorithm from the endpoint URL extension. The following URL extensions
are supported:

* `gzip`
* `gz`
* `deflate`
* `brotli`
* `br`
* `LZMA`
* `xz`
* `zstd`
* `zst`

#### RQ.SRS-015.S3.TableFunction.S3Cluster
version: 1.0

[ClickHouse] SHALL support reading from AWS [S3] clusters using the
`s3Cluster` table function. The table function can be used with the following syntax:

``` sql
s3Cluster(cluster_name, source, [access_key_id, secret_access_key,] format, structure)
```

### MinIO

#### RQ.SRS-015.S3.MinIO.Disk.Configuration
version: 1.0

[ClickHouse] SHALL support configuration of [S3] disks using the MinIO server
with syntax similar to the following:

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

#### RQ.SRS-015.S3.MinIO.TableFunction
version: 1.0

[ClickHouse] SHALL support importing and exporting data to/from MinIO
using the [S3] table function with the following syntax:

``` sql
s3(http://minio:9000/my-bucket/object-key, [access_key_id, secret_access_key,] format, structure, [compression])
```

#### RQ.SRS-015.S3.MinIO.AllowS3ZeroCopyReplication
version: 1.0

[ClickHouse] SHALL support importing and exporting data to/from the MinIO
server using replicated tables with the ReplicatedMergeTree engine and
the `<allow_s3_zero_copy_replication>` parameter set to 1.

### AWS

#### RQ.SRS-015.S3.AWS.Disk.Configuration
version: 1.0

[ClickHouse] SHALL support [S3] disk configuration using [AWS S3] with syntax
similar to the following:

``` xml
<yandex>
  <storage_configuration>
    <disks>
      <aws>
        <type>s3</type>
        <endpoint>http://s3.us-east-1.amazonaws.com/my-bucket/object-key/</endpoint>
        <access_key_id>*****</access_key_id>
        <secret_access_key>*****</secret_access_key>
      </aws>
    </disks>
...
</yandex>
```

#### RQ.SRS-015.S3.AWS.TableFunction
version: 1.0

[ClickHouse] SHALL support importing and exporting data to/from [AWS S3]
using the [S3] table function with the following syntax:

``` sql
s3(http://s3.us-east-1.amazonaws.com/my-bucket/object-key, [access_key_id, secret_access_key,] format, structure, [compression])
```

#### RQ.SRS-015.S3.AWS.Disk.URL
version: 1.0

[ClickHouse] SHALL support [AWS S3] disks with the endpoint configured using
both generic and region-specific bucket URLs.

#### RQ.SRS-015.S3.AWS.Disk.URL.Generic
version: 1.0

[ClickHouse] SHALL support [AWS S3] disks with the endpoint configured using
generic bucket URLs with syntax similar to the following:

    “https://altinity-clickhouse-data.s3.amazonaws.com/”

#### RQ.SRS-015.S3.AWS.Disk.URL.Specific
version: 1.0

[ClickHouse] SHALL support [AWS S3] disks with the endpoint configured using
region-specific bucket URLs with syntax similar to the following:

    “https://s3.us-east-1.amazonaws.com/altinity-clickhouse-data/”

#### RQ.SRS-015.S3.AWS.EC2.Disk
version: 1.0

[ClickHouse] SHALL support [S3] external storage via one or more disks when
running on an AWS EC2 instance.

#### RQ.SRS-015.S3.AWS.EC2.TableFunction
version: 1.0

[ClickHouse] SHALL support [S3] external storage via a call to the [S3] table
function when running on an EC2 instance. Using the table function, [ClickHouse]
SHALL provide read and write functionality. Upon a write, [ClickHouse] SHALL overwrite
existing data.

#### RQ.SRS-015.S3.AWS.EC2.Endpoints
version: 1.0

[ClickHouse] SHALL support configuration of [S3] endpoints in the config.xml file
using credentials accessible to the entire ClickHouse server, when running on an
EC2 instance, with syntax similar to the following:

``` xml
<yandex>
    <s3>
       <my_endpoint>
           <endpoint>http://s3.us-east-1.amazonaws.com/my-bucket/object-key/</endpoint>
           <access_key_id>*****</access_key_id>
           <secret_access_key>*****</secret_access_key>
           <header>Authorization: Bearer TOKEN</header>
       </my_endpoint>
   </s3>
</yandex>
```

#### RQ.SRS-015.S3.AWS.AllowS3ZeroCopyReplication
version: 1.0

[ClickHouse] SHALL support importing and exporting data to/from [AWS S3]
using replicated tables with the ReplicatedMergeTree engine and the
`<allow_s3_zero_copy_replication>` parameter set to 1.

#### RQ.SRS-015.S3.AWS.SSEC
version: 1.0

[ClickHouse] SHALL support using the provided SSEC keys in order to perform
server-side encryption and decryption when writing and reading from AWS S3 endpoints.

The SSEC key can be specified using the `<server_side_encryption_customer_key_base64>` parameter.
Example:
```
<s3>
  <s3-bucket>
    <endpoint>masked</endpoint>
    <access_key_id>masked</access_key_id>
    <secret_access_key>masked</secret_access_key>
    <server_side_encryption_customer_key_base64>Wp+aNxm8EkYtL6myH99DYg==</server_side_encryption_customer_key_base64>
  </s3-bucket>
</s3>
```

### GCS

#### RQ.SRS-015.S3.GCS.Disk.Configuration
version: 1.0

[ClickHouse] SHALL support configuration of [S3] disks using Google Cloud Storage
with syntax similar to the following:

``` xml
<yandex>
  <storage_configuration>
    <disks>
      <gcs>
        <type>s3</type>
        <endpoint>https://storage.googleapis.com/my-bucket/object-key/</endpoint>
        <access_key_id>*****</access_key_id>
        <secret_access_key>*****</secret_access_key>
      </gcs>
    </disks>
...
</yandex>
```

#### RQ.SRS-015.S3.GCS.TableFunction
version: 1.0

[ClickHouse] SHALL support importing and exporting data to/from Google Cloud
Storage using the [S3] table function with the following syntax:

``` sql
s3(https://storage.googleapis.com/my-bucket/object-key, [access_key_id, secret_access_key,] format, structure, [compression])
```

#### RQ.SRS-015.S3.GCS.AllowS3ZeroCopyReplication
version: 1.0

[ClickHouse] SHALL support importing and exporting data to/from GCS
using replicated tables with the ReplicatedMergeTree engine and the
`<allow_s3_zero_copy_replication>` parameter set to 1.

### Settings

#### RQ.SRS-015.S3.Settings.MaxThreads
version: 1.0

[ClickHouse] SHALL read files from S3 in parallel when the value of `max_threads`
is greater than 1.

#### RQ.SRS-015.S3.Settings.MaxDownloadThreads
version: 1.0

[ClickHouse] SHALL download files from S3 in parallel using multiple threads 
specified by `max_download_threads`. Default is 1.

#### RQ.SRS-015.S3.Settings.MaxDownloadBufferSize
version: 1.0

[ClickHouse] SHALL download files from S3 with a maximum buffer size 
specified by `max_download_buffer_size`.

#### RQ.SRS-015.S3.Settings.PartitionBy
version: 1.0

[ClickHouse] SHALL support PARTITION BY expression for the S3 table engine to
partition writes to the S3 table into multiple files. These file names SHALL
be prefixed by the partition key.

#### RQ.SRS-015.S3.Settings.S3UploadPartSizeMultiplyFactor
version: 1.0

[ClickHouse] SHALL support specifying `s3_upload_part_size_multiply_factor` setting to
specifying how much `s3_min_upload_part_size` should be increased.

#### RQ.SRS-015.S3.Settings.S3UploadPartSizeMultiplyPartsCountThreshold
version: 1.0

[ClickHouse] SHALL support specifying `s3_upload_part_size_multiply_parts_count_threshold` setting
to specifying after how many parts the minimum part size should be increased by `s3_upload_part_size_multiply_factor`.

### Performance

#### RQ.SRS-015.S3.Performance.PerformTTLMoveOnInsert
version: 1.0

[ClickHouse] SHALL provide better insert performance of tiered storage policies
with [S3] volumes when the `<perform_ttl_move_on_insert>` parameter of the
`<volume>` section of the desired [S3] disk in the `<policies>` section of the
`<storage_configuration>` section of the config.xml file or the storage.xml file
in the config.d directory is set to 0.

#### RQ.SRS-015.S3.Performance.AllowS3ZeroCopyReplication.Select
version: 1.0

[ClickHouse] SHALL provide similar performance of SELECT operations on tables on
[S3] disks when the `<allow_s3_zero_copy_replication>` parameter is set, and when
it is not set.

#### RQ.SRS-015.S3.Performance.AllowS3ZeroCopyReplication.Insert
version: 1.0

[ClickHouse] SHALL provide similar performance of INSERT operations on tables on
[S3] disks when the `<allow_s3_zero_copy_replication>` parameter is set, and when
it is not set.

#### RQ.SRS-015.S3.Performance.AllowS3ZeroCopyReplication.Alter
version: 1.0

[ClickHouse] SHALL provide similar performance of ALTER operations on tables on
[S3] disks when the `<allow_s3_zero_copy_replication>` parameter is set, and when
it is not set.

## References

* **AWS:** https://en.wikipedia.org/wiki/Amazon_Web_Services
* **S3:** https://en.wikipedia.org/wiki/Amazon_S3
* **ClickHouse:** https://clickhouse.tech
* **ClickHouse Data Formats:** https://clickhouse.tech/docs/en/interfaces/formats
* **GitLab Repository:** https://gitlab.com/altinity-qa/documents/qa-srs015-clickhouse-s3-support/-/blob/master/QA_SRS_015_ClickHouse_S3_Support.md
* **Revision History:** https://gitlab.com/altinity-qa/documents/qa-srs015-clickhouse-s3-support/-/commits/master/QA_SRS_015_ClickHouse_S3_Support.md

[AWS]: https://en.wikipedia.org/wiki/Amazon_Web_Services
[AWS S3]: https://en.wikipedia.org/wiki/Amazon_S3
[ClickHouse]: https://clickhouse.tech
[data formats]: https://clickhouse.tech/docs/en/interfaces/formats
[GitHub]: https://github.com
[Git]: https://git-scm.com/
[GitLab Repository]: https://gitlab.com/altinity-qa/documents/qa-srs015-clickhouse-s3-support/-/blob/master/QA_SRS_015_ClickHouse_S3_Support.md
[Revision History]: https://gitlab.com/altinity-qa/documents/qa-srs015-clickhouse-s3-support/-/commits/master/QA_SRS_015_ClickHouse_S3_Support.md
[S3]: https://en.wikipedia.org/wiki/Amazon_S3
