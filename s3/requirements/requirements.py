# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.241211.1164717.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_015_S3 = Requirement(
    name="RQ.SRS-015.S3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support external object storage using [AWS S3] and\n"
        "S3-compatible storage.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.1",
)

RQ_SRS_015_S3_Import = Requirement(
    name="RQ.SRS-015.S3.Import",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing files from [S3] external storage using\n"
        "the [S3] table function or storage disks configured for [S3] storage.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.2",
)

RQ_SRS_015_S3_Export = Requirement(
    name="RQ.SRS-015.S3.Export",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting files to [S3] external storage using\n"
        "the [S3] table function or storage disks configured for [S3] storage.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.3",
)

RQ_SRS_015_S3_Disk = Requirement(
    name="RQ.SRS-015.S3.Disk",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [S3] external storage via one or more storage disks.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.4",
)

RQ_SRS_015_S3_Policy = Requirement(
    name="RQ.SRS-015.S3.Policy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support selection of [S3] disks using policies defined in the\n"
        "`<policies>` section of the `<storage_configuration>` section of the config.xml\n"
        "file or the storage.xml file in the config.d directory.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.5",
)

RQ_SRS_015_S3_TableFunction = Requirement(
    name="RQ.SRS-015.S3.TableFunction",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [S3] external storage via a call to the [S3] table\n"
        "function. Using the table function, [ClickHouse] SHALL provide read and write\n"
        "functionality. Upon a write to a location with data already stored, [ClickHouse]\n"
        "SHALL overwrite existing data.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.6",
)

RQ_SRS_015_S3_DataParts = Requirement(
    name="RQ.SRS-015.S3.DataParts",
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
    num="4.1.7",
)

RQ_SRS_015_S3_Security_Encryption = Requirement(
    name="RQ.SRS-015.S3.Security.Encryption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support sending the `x-amz-server-side-encryption-customer-key`\n"
        "header and the `x-amz-server-side-encryption-customer-key-md5` header as part of\n"
        "the query when the S3 resource is server-side encrypted.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.8",
)

RQ_SRS_015_S3_RemoteHostFilter = Requirement(
    name="RQ.SRS-015.S3.RemoteHostFilter",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support a remote host filter to prevent access to untrusted URL\n"
        "addresses. The remote host filter configuration SHALL be similar to the following:\n"
        "\n"
        "``` xml\n"
        "<yandex>\n"
        "    <!-- The list of hosts allowed to use in URL-related storage engines and table functions.\n"
        "        If this section is not present in configuration, all hosts are allowed.\n"
        "    -->\n"
        "    <remote_url_allow_hosts>\n"
        "        <!-- Host should be specified exactly as in URL. The name is checked before DNS resolution.\n"
        '            Example: "yandex.ru", "yandex.ru." and "www.yandex.ru" are different hosts.\n'
        "                If port is explicitly specified in URL, the host:port is checked as a whole.\n"
        "                If host specified here without port, any port with this host allowed.\n"
        '                "yandex.ru" -> "yandex.ru:443", "yandex.ru:80" etc. is allowed, but "yandex.ru:80" -> only "yandex.ru:80" is allowed.\n'
        '                If the host is specified as IP address, it is checked as specified in URL. Example: "[2a02:6b8:a::a]".\n'
        "                If there are redirects and support for redirects is enabled, every redirect (the Location field) is checked.\n"
        "        -->\n"
        "        <host>www.myhost.com</host>\n"
        "\n"
        "        <!-- Regular expression can be specified. RE2 engine is used for regexps.\n"
        "            Regexps are not aligned: don't forget to add ^ and $. Also don't forget to escape dot (.) metacharacter\n"
        "            (forgetting to do so is a common source of error).\n"
        "        -->\n"
        "        <host_regexp>^.*\\.myhost\\.com$</host_regexp>\n"
        "    </remote_url_allow_hosts>\n"
        "</yandex>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.9",
)

RQ_SRS_015_S3_Alter = Requirement(
    name="RQ.SRS-015.S3.Alter",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support running `ALTER ...` queries on [S3] storage.\n"
        "[ClickHouse] SHALL reproduce these queries across replicas without data loss.\n"
        "[ClickHouse] SHALL support the above when configured with one or more of disk cache,\n"
        "disk encryption and zero copy replication.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.10",
)

RQ_SRS_015_S3_Backup_MinIOBackup = Requirement(
    name="RQ.SRS-015.S3.Backup.MinIOBackup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support manual backups of tables that use minio storage.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.11.1",
)

RQ_SRS_015_S3_Backup_AWSS3Backup = Requirement(
    name="RQ.SRS-015.S3.Backup.AWSS3Backup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support manual backups of tables that use aws s3 storage.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.11.2",
)

RQ_SRS_015_S3_Backup_GCSBackup = Requirement(
    name="RQ.SRS-015.S3.Backup.GCSBackup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support manual backups of tables that use gcs storage.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.11.3",
)

RQ_SRS_015_S3_Backup_AzureBackup = Requirement(
    name="RQ.SRS-015.S3.Backup.AzureBackup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support manual backups of tables that use azure storage.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.11.4",
)

RQ_SRS_015_S3_Backup_StoragePolicies = Requirement(
    name="RQ.SRS-015.S3.Backup.StoragePolicies",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using creating manual backups of tables that use storage policies containing:\n"
        "\n"
        "* one volume with s3 disk\n"
        "* one volume with s3 and local disk\n"
        "* multiple volumes with s3 and local disks\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.11.5",
)

RQ_SRS_015_S3_Backup_AlterFreeze = Requirement(
    name="RQ.SRS-015.S3.Backup.AlterFreeze",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `ALTER TABLE FREEZE` on tables that use S3 in the storage policy. If the policy includes a local disk,\n"
        "the query will create a local backup in the `shadow/` directory of the working ClickHouse directory (`/var/lib/clickhouse` by default).\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.11.6",
)

RQ_SRS_015_S3_Backup_AlterDetach = Requirement(
    name="RQ.SRS-015.S3.Backup.AlterDetach",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `ALTER TABLE DETACH PARTITION` on partitions of tables that use S3.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.11.7",
)

RQ_SRS_015_S3_Backup_AlterAttach = Requirement(
    name="RQ.SRS-015.S3.Backup.AlterAttach",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support restoring backups of tables using `ALTER TABLE ATTACH PARTITION` from data inside\n"
        "`/var/lib/clickhouse/data/database/table/detached/`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.11.8",
)

RQ_SRS_015_S3_Backup_Cleanup = Requirement(
    name="RQ.SRS-015.S3.Backup.Cleanup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL clean up local and remote files related to backed up partitions after a table is dropped.\n"
        "\n"
        "* Detached partitions SHALL be removed immediately\n"
        "* Frozen partitions SHALL be removed immediately after SYSTEM UNFREEZE\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.11.9",
)

RQ_SRS_015_S3_Metadata = Requirement(
    name="RQ.SRS-015.S3.Metadata",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL store disk metadata of tables with S3 disk\n"
        "if and only if they have `<send_metadata>` set to `true` in the disk config.\n"
        "The disk metadata is stored in `/var/lib/clickhouse/disks/{disk name}/`.\n"
        "The metadata is stored in the s3 bucket.\n"
        "\n"
        "`<send_metadata>` was deprecated in ClickHouse 21 and will be removed in the future.\n"
        "See <https://github.com/ClickHouse/ClickHouse/issues/30510>\n"
        "\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.12.1",
)

RQ_SRS_015_S3_Metadata_Revisions = Requirement(
    name="RQ.SRS-015.S3.Metadata.Revisions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL keep a revision counter for each table and change the counter for\n"
        "every insert, merge, or remove operation. The revision counter in stored in\n"
        "`/var/lib/clickhouse/disks/s3/shadow/{backup number}/revision.txt`, where\n"
        "the backup number indicated how many times `ALTER FREEZE` has been used on the table.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.12.2",
)

RQ_SRS_015_S3_Metadata_BadBackupNumber = Requirement(
    name="RQ.SRS-015.S3.Metadata.BadBackupNumber",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL\n" "\n"),
    link=None,
    level=4,
    num="4.1.12.3",
)

RQ_SRS_0_5_S3_MetadataRestore_RestoreFile = Requirement(
    name="RQ.SRS-0.5.S3.MetadataRestore.RestoreFile",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support restoring tables using a restore file\n"
        "located in `/var/lib/clickhouse/disks/{disk name}/restore` and executing\n"
        "`SYSTEM RESTART DISK` and reattaching the table.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.13.1",
)

RQ_SRS_0_5_S3_MetadataRestore_BadRestoreFile = Requirement(
    name="RQ.SRS-0.5.S3.MetadataRestore.BadRestoreFile",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not support restoring tables using a restore file\n"
        "located in `/var/lib/clickhouse/disks/{disk name}/restore` that contains\n"
        "a wrong bucket, path, or revision value.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.13.2",
)

RQ_SRS_0_5_S3_MetadataRestore_HugeRestoreFile = Requirement(
    name="RQ.SRS-0.5.S3.MetadataRestore.HugeRestoreFile",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not support restoring tables using a restore file\n"
        "located in `/var/lib/clickhouse/disks/{disk name}/restore` that contains\n"
        "a large amount of not usable information.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.13.3",
)

RQ_SRS_015_S3_MetadataRestore_NoLocalMetadata = Requirement(
    name="RQ.SRS-015.S3.MetadataRestore.NoLocalMetadata",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support restoring a table from the restore file\n"
        "located in `/var/lib/clickhouse/disks/{disk name}/restore` even\n"
        "if the local metadata has been purged.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.13.4",
)

RQ_SRS_015_S3_MetadataRestore_BucketPath = Requirement(
    name="RQ.SRS-015.S3.MetadataRestore.BucketPath",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support restoring a table to a specific bucket and path by indicating them\n"
        "in the restore file located in `/var/lib/clickhouse/disks/{disk name}/restore`\n"
        "using the following syntax:\n"
        "\n"
        "```\n"
        "'source_path' = {path}\n"
        "'source_bucket' = {bucket}\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.13.5",
)

RQ_SRS_015_S3_MetadataRestore_RevisionRestore = Requirement(
    name="RQ.SRS-015.S3.MetadataRestore.RevisionRestore",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support restoring a table to a specific revision version.\n"
        "The table shall restore to the original bucket and path if and only if it is the latest revision.\n"
        "The revision can be indicated in the restore file located in `/var/lib/clickhouse/disks/{disk name}/restore`:\n"
        "\n"
        "```\n"
        "'revision' = {revision number}\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.13.6",
)

RQ_SRS_015_S3_MetadataRestore_Mutations = Requirement(
    name="RQ.SRS-015.S3.MetadataRestore.Mutations",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support restoring a table to a state before, during, or after a mutation.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.13.7",
)

RQ_SRS_015_S3_MetadataRestore_ParallelMutations = Requirement(
    name="RQ.SRS-015.S3.MetadataRestore.ParallelMutations",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support restoring a table correctly even when mutations\n"
        "are being added in parallel with the restore process.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.13.8",
)

RQ_SRS_015_S3_MetadataRestore_Detached = Requirement(
    name="RQ.SRS-015.S3.MetadataRestore.Detached",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support restoring tables with a detached partition and\n"
        "the ability to reattach that partition even if it was detached before the `ALTER FREEZE` backup.\n"
        "It can be indicated in the restore file located in `/var/lib/clickhouse/disks/{disk name}/restore`:\n"
        "\n"
        "```\n"
        "'detached' = true\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.13.9",
)

RQ_SRS_015_S3_AWS = Requirement(
    name="RQ.SRS-015.S3.AWS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [S3] external storage using [AWS S3].\n" "\n"
    ),
    link=None,
    level=3,
    num="4.1.14",
)

RQ_SRS_015_S3_MinIO = Requirement(
    name="RQ.SRS-015.S3.MinIO",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [S3] external storage using MinIO.\n" "\n"
    ),
    link=None,
    level=3,
    num="4.1.15",
)

RQ_SRS_015_S3_GCS = Requirement(
    name="RQ.SRS-015.S3.GCS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [S3] external storage using Google Cloud Storage.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.16",
)

RQ_SRS_015_S3_Azure = Requirement(
    name="RQ.SRS-015.S3.Azure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support external disks using [Azure Blob Storage].\n" "\n"
    ),
    link=None,
    level=3,
    num="4.1.17",
)

RQ_SRS_015_S3_AutomaticReconnects_GCS = Requirement(
    name="RQ.SRS-015.S3.AutomaticReconnects.GCS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support automatically reconnecting to GCS if the network connection has been interrupted.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.18.1",
)

RQ_SRS_015_S3_AutomaticReconnects_AWS = Requirement(
    name="RQ.SRS-015.S3.AutomaticReconnects.AWS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support automatically reconnecting to AWS S3 if the network connection has been interrupted.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.18.2",
)

RQ_SRS_015_S3_AutomaticReconnects_MinIO = Requirement(
    name="RQ.SRS-015.S3.AutomaticReconnects.MinIO",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support automatically reconnecting to MinIO if the network connection has been interrupted.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.18.3",
)

RQ_SRS_015_S3_AutomaticReconnects_Azure = Requirement(
    name="RQ.SRS-015.S3.AutomaticReconnects.Azure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support automatically reconnecting to Azure if the network connection has been interrupted.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.1.18.4",
)

RQ_SRS_015_S3_User_Configuration_Cache_22_8_EnableFilesystemCache = Requirement(
    name="RQ.SRS-015.S3.User.Configuration.Cache.22.8.EnableFilesystemCache",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support setting `<enable_filesystem_cache>` parameter\n"
        "when defining a user in the `<profiles>` section.\n"
        "This is only available in versions 22.8 and later.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.2.1",
)

RQ_SRS_015_S3_User_Configuration_Cache_22_8_EnableFilesystemCacheOnWriteOperations = Requirement(
    name="RQ.SRS-015.S3.User.Configuration.Cache.22.8.EnableFilesystemCacheOnWriteOperations",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support setting `<enable_filesystem_cache_on_write_operations>` parameter\n"
        "when defining a user in the `<profiles>` section.\n"
        "This is only available in versions 22.8 and later.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.2.2",
)

RQ_SRS_015_S3_FilesystemCacheLog_22_8 = Requirement(
    name="RQ.SRS-015.S3.FilesystemCacheLog.22.8",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support setting `<database>` and `<table`> parameters\n"
        "in the `<filesystem_cache_log>` section of configs.xml or any other xml in the config.d directory.\n"
        "This is only available in versions 22.8 and later.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.3",
)

RQ_SRS_015_S3_Disk_AddingMoreStorageDevices = Requirement(
    name="RQ.SRS-015.S3.Disk.AddingMoreStorageDevices",
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
    num="4.4.1",
)

RQ_SRS_015_S3_Disk_Endpoints = Requirement(
    name="RQ.SRS-015.S3.Disk.Endpoints",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support configuration of [S3] endpoints in the config.xml file\n"
        "using credentials accessible to the entire ClickHouse server, with syntax similar\n"
        "to the following:\n"
        "\n"
        "``` xml\n"
        "<yandex>\n"
        "    <s3>\n"
        "       <my_endpoint>\n"
        "           <endpoint>http://s3.us-east-1.amazonaws.com/my-bucket/</endpoint>\n"
        "           <access_key_id>*****</access_key_id>\n"
        "           <secret_access_key>*****</secret_access_key>\n"
        "           <header>Authorization: Bearer TOKEN</header>\n"
        "       </my_endpoint>\n"
        "   </s3>\n"
        "</yandex>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.4.2",
)

RQ_SRS_015_S3_Disk_MultipleStorageDevices = Requirement(
    name="RQ.SRS-015.S3.Disk.MultipleStorageDevices",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support storing data to multiple [S3] storage devices.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.4.3",
)

RQ_SRS_015_S3_Disk_MultipleStorageDevices_NoChangesForQuerying = Requirement(
    name="RQ.SRS-015.S3.Disk.MultipleStorageDevices.NoChangesForQuerying",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL require no changes to query statements when querying data\n"
        "from a table that supports multiple [S3] storage devices.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.4.4",
)

RQ_SRS_015_S3_Disk_Metadata = Requirement(
    name="RQ.SRS-015.S3.Disk.Metadata",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL create a metadata file for each [S3] disk which tracks the total\n"
        "number of objects stored in the disk, the aggregate size of the objects, and for each\n"
        "object stored in the disk, tracks the path to the object and the object size.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.4.5",
)

RQ_SRS_015_S3_Disk_DropSync = Requirement(
    name="RQ.SRS-015.S3.Disk.DropSync",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL immediately remove related files from S3 when a table is dropped with the SYNC keyword.\n"
        "\n"
        "Usage:\n"
        "\n"
        "```sql\n"
        "DROP TABLE mytable SYNC\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.4.6",
)

RQ_SRS_015_S3_Disk_Configuration = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support configuration of one or more [S3] disks in the `<disks>`\n"
        "section of the `<storage_configuration>` section of the config.xml file or the\n"
        "storage.xml file in the config.d directory.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.1",
)

RQ_SRS_015_S3_Disk_Configuration_Syntax = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.Syntax",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [S3] disk configuration using syntax similar to the\n"
        "following:\n"
        "\n"
        "``` xml\n"
        "<yandex>\n"
        "  <storage_configuration>\n"
        "    <disks>\n"
        "      <s3>\n"
        "        <type>s3</type>\n"
        "        <endpoint>http://s3.us-east-1.amazonaws.com/my-bucket/</endpoint>\n"
        "        <access_key_id>*****</access_key_id>\n"
        "        <secret_access_key>*****</secret_access_key>\n"
        "      </s3>\n"
        "    </disks>\n"
        "...\n"
        "</yandex>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.2",
)

RQ_SRS_015_S3_Disk_Configuration_Invalid = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.Invalid",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if the [S3] disk configuration is not valid.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.3",
)

RQ_SRS_015_S3_Disk_Configuration_Changes_NoRestart = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.Changes.NoRestart",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] server SHALL not need to be restarted when storage device\n"
        "configuration changes except some special cases.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.4",
)

RQ_SRS_015_S3_Disk_Configuration_Access = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.Access",
    version="1.1",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `<skip_access_check>` parameter in the `<disks>`\n"
        "section of the `<storage_configuration>` section of the config.xml file or the\n"
        "storage.xml file in the config.d directory to toggle a runtime check for access\n"
        "to the corresponding [S3] disk. If this runtime check fails, [ClickHouse] SHALL\n"
        'return an "Access Denied" error. The specifics of the error depend on version:\n'
        "\n"
        " - In [Clickhouse] < 22.9 the error message SHALL be `DB::Exception: Access Denied.`\n"
        "else `DB::Exception: Message: Access Denied`\n"
        " - In [Clickhouse] >= 23.8 the error SHALL be returned from CREATE TABLE,\n"
        "else CREATE TABLE SHALL succeed and the error SHALL be returned from INSERT INTO\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.5",
)

RQ_SRS_015_S3_Disk_Configuration_Access_Default = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.Access.Default",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL set the `<skip_access_check>` parameter to 0 by default to\n"
        "perform an access check.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.6",
)

RQ_SRS_015_S3_Disk_Configuration_CacheEnabled = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.CacheEnabled",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `<cache_enabled>` parameter in the `<disks>`\n"
        "section of the `<storage_configuration>` section of the config.xml file or the\n"
        "storage.xml file in the config.d directory to toggle caching for the\n"
        "corresponding [S3] disk.\n"
        "\n"
        "In 22.8 and later, this parameter has been renamed to `<data_cache_enabled>`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.7",
)

RQ_SRS_015_S3_Disk_Configuration_CacheEnabled_Default = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.CacheEnabled.Default",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL set the `<cache_enabled>` parameter to 1 by default to\n"
        "enable caching.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.8",
)

RQ_SRS_015_S3_Disk_Configuration_Cache_22_8 = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.Cache.22.8",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support defining cache storage in the in the `<disks>`\n"
        "section of the `<storage_configuration>` section of the config.xml file or the\n"
        "storage.xml file in the config.d directory to toggle caching for the\n"
        "corresponding [S3] disk in version 22.8 and later.\n"
        "\n"
        "The definition requires `<type>`, `<disk>`, `<path>`, `<max_size>`, and `<do_not_evict_index_and_mark_files>` parameters.\n"
        "\n"
        "Example:\n"
        "\n"
        "```\n"
        "<s3_cache>\n"
        "    <type>cache</type>\n"
        "    <disk>s3_disk</disk>\n"
        "    <path>s3_disk_cache/</path>\n"
        "    <max_size>22548578304</max_size>\n"
        "    <do_not_evict_index_and_mark_files>0</do_not_evict_index_and_mark_files>\n"
        "</s3_cache>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.9",
)

RQ_SRS_015_S3_Disk_Configuration_Cache_22_8_CacheOnWriteOperations = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.CacheOnWriteOperations",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support setting `<cache_on_write_operations>` parameter\n"
        "when defining a cache. This is only available in versions 22.8 and later.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.10",
)

RQ_SRS_015_S3_Disk_Configuration_Cache_22_8_DataCacheMaxSize = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.DataCacheMaxSize",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support setting `<data_cache_max_size>` parameter\n"
        "when defining a cache. This is only available in versions 22.8 and later.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.11",
)

RQ_SRS_015_S3_Disk_Configuration_Cache_22_8_EnableCacheHitsThreshold = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.EnableCacheHitsThreshold",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support setting `<enable_cache_hits_threshold>` parameter\n"
        "when defining a cache. This is only available in versions 22.8 and later.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.12",
)

RQ_SRS_015_S3_Disk_Configuration_Cache_22_8_FileSystemQueryCacheLimit = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.FileSystemQueryCacheLimit",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support setting `<enable_filesystem_query_cache_limit>` parameter\n"
        "when defining a cache. This is only available in versions 22.8 and later.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.13",
)

RQ_SRS_015_S3_Disk_Configuration_CachePath = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.CachePath",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `<cache_path>` parameter in the `<disks>`\n"
        "section of the `<storage_configuration>` section of the config.xml file or the\n"
        "storage.xml file in the config.d directory to set the path to the disk cache.\n"
        "This will have no effect if the `<cache_enabled>` parameter is set to 0.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.14",
)

RQ_SRS_015_S3_Disk_Configuration_CachePath_Conflict = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.CachePath.Conflict",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL throw an error if the `<cache_path>` parameter in the\n"
        "`<disks>` section of the `<storage_configuration>` section of the config.xml\n"
        "file or the storage.xml file in the config.d directory is set such that the\n"
        "path to the disk metadata and the path to the disk cache are the same.\n"
        "The error SHALL be similar to the following:\n"
        "\n"
        "```sh\n"
        '"DB::Exception: Metadata and cache path should be different"\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.15",
)

RQ_SRS_015_S3_Disk_Configuration_MinBytesForSeek = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.MinBytesForSeek",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `<min_bytes_for_seek>` parameter in the `<disks>`\n"
        "section of the `<storage_configuration>` section of the config.xml file or the\n"
        "storage.xml file in the config.d directory to set the minimum number of\n"
        "bytes to seek forward through the file.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.16",
)

RQ_SRS_015_S3_Disk_Configuration_MinBytesForSeek_Syntax = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.MinBytesForSeek.Syntax",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL run with no errors when the `<min_bytes_for_seek>` parameter\n"
        "in the `<disks>` section of the `<storage_configuration>` section of the\n"
        "config.xml file or the storage.xml file in the config.d directory is configured\n"
        "with correct syntax.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.17",
)

RQ_SRS_015_S3_Disk_Configuration_S3MaxSinglePartUploadSize = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.S3MaxSinglePartUploadSize",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `<s3_max_single_part_upload_size>` parameter in\n"
        "the `<disks>` section of the `<storage_configuration>` section of the config.xml\n"
        "file or the storage.xml file in the config.d directory to set the maximum\n"
        "size, in bytes, of single part uploads to S3.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.18",
)

RQ_SRS_015_S3_Disk_Configuration_S3MaxSinglePartUploadSize_Syntax = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.S3MaxSinglePartUploadSize.Syntax",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL run with no errors when the\n"
        "`<s3_max_single_part_upload_size>` parameter in the `<disks>` section of the\n"
        "`<storage_configuration>` section of the config.xml file or the storage.xml\n"
        "file in the config.d directory is configured with correct syntax.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.19",
)

RQ_SRS_015_S3_Disk_Configuration_S3UseEnvironmentCredentials = Requirement(
    name="RQ.SRS-015.S3.Disk.Configuration.S3UseEnvironmentCredentials",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `<s3_use_environment_credentials>` parameter in\n"
        "the `<disks>` section of the `<storage_configuration>` section of the config.xml\n"
        "file or the storage.xml file in the config.d directory to use the server\n"
        "environment credentials set in the config.xml file.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.7.20",
)

RQ_SRS_015_S3_Disk_MergeTree = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support selection of one or more [S3] external storage disks using\n"
        "engines in the MergeTree engine family.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.8.1",
)

RQ_SRS_015_S3_Disk_MergeTree_MergeTree = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.MergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support selection of one or more [S3] external storage disks using\n"
        "the MergeTree engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.8.2",
)

RQ_SRS_015_S3_Disk_MergeTree_ReplacingMergeTree = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.ReplacingMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support selection of one or more [S3] external storage disks using\n"
        "the ReplacingMergeTree engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.8.3",
)

RQ_SRS_015_S3_Disk_MergeTree_SummingMergeTree = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.SummingMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support selection of one or more [S3] external storage disks using\n"
        "the SummingMergeTree engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.8.4",
)

RQ_SRS_015_S3_Disk_MergeTree_AggregatingMergeTree = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.AggregatingMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support selection of one or more [S3] external storage disks using\n"
        "the AggregatingMergeTree engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.8.5",
)

RQ_SRS_015_S3_Disk_MergeTree_CollapsingMergeTree = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.CollapsingMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support selection of one or more [S3] external storage disks using\n"
        "the CollapsingMergeTree engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.8.6",
)

RQ_SRS_015_S3_Disk_MergeTree_VersionedCollapsingMergeTree = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.VersionedCollapsingMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support selection of one or more [S3] external storage disks using\n"
        "the VersionedCollapsingMergeTree engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.8.7",
)

RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `<allow_s3_zero_copy_replication>` as a MergeTree\n"
        "table engine setting for the ReplicatedMergeTree engine to toggle data\n"
        "replication via S3 for replicated tables.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.4.8.8.1",
)

RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Default = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Default",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL set the `<allow_s3_zero_copy_replication>` parameter to 0 by\n"
        "default to disable data replication via S3 and replicate data directly when using\n"
        "the ReplicatedMergeTree table engine.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.4.8.8.2",
)

RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Global = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Global",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `<allow_s3_zero_copy_replication>` setting to the\n"
        "`<merge_tree>` section of the config.xml file or the merge_tree.xml file in\n"
        "the config.d directory to configure the ReplicatedMergeTree engine globally. This\n"
        "setting SHALL be applied to all ReplicatedMergeTree tables.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.4.8.8.3",
)

RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Metadata = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Metadata",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL replicate only S3 metadata when the\n"
        "`<allow_s3_zero_copy_replication>` parameter is set to 1. The receiver of the\n"
        "metadata SHALL create identical metadata files which refer to the same object\n"
        "keys in S3.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.4.8.8.4",
)

RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Alter = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Alter",
    version="1.1",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support operations on replicated tables (ALTER,\n"
        "SELECT, INSERT, etc...). If a replicated table is modified,\n"
        "the changes SHALL be synchronized without data loss on all existing\n"
        "replicas, and in [S3] storage.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.4.8.8.5",
)

RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Delete = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Delete",
    version="1.1",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support dropping a replicated table with no changes to any\n"
        "other replicas of the table.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.4.8.8.6",
)

RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_DeleteAll = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.DeleteAll",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support deleting replicated tables from [S3] by dropping\n"
        "all replicas of the table from each [ClickHouse] instance.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.4.8.8.7",
)

RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_DataPreservedAfterMutation = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.DataPreservedAfterMutation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[Clickhouse] SHALL distribute mutations to all replicas without data loss.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.4.8.8.8",
)

RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_DropReplica = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.DropReplica",
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
    level=5,
    num="4.4.8.8.9",
)

RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_AddReplica = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.AddReplica",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support adding a replica of an existing replicated table\n"
        "with no changes to the data in the table. When the replica is added, the\n"
        "existing data SHALL be downloaded from [S3] to match the other replicas.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.4.8.8.10",
)

RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_NoDataDuplication = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.NoDataDuplication",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support zero copy replication such that data is not\n"
        "duplicated in [S3] storage during any operations on replicated tables (ALTER,\n"
        "SELECT, INSERT, etc...).  Data SHALL be fully removed from [S3] via DELETE\n"
        "operations.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.4.8.8.11",
)

RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_TTL_Move = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.TTL.Move",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support TTL moves to other hard disks or [S3] disks when the\n"
        "`<allow_s3_zero_copy_replication>` setting is used with the MergeTree engine.\n"
        "When TTL moves are used, data will not be duplicated in [S3]. All objects in\n"
        "a table SHALL be accessible with no errors, even if they have been moved\n"
        "to a different disk.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.4.8.8.12",
)

RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_TTL_Delete = Requirement(
    name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.TTL.Delete",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support TTL object deletion when the\n"
        "`<allow_s3_zero_copy_replication>` setting is used with the MergeTree engine.\n"
        "When objects are removed, all other objects SHALL be accessible with no errors.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.4.8.8.13",
)

RQ_SRS_015_S3_Policy_Syntax = Requirement(
    name="RQ.SRS-015.S3.Policy.Syntax",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support selection of an [S3] disk for a volume using policies\n"
        "with syntax similar to the following examples.\n"
        "\n"
        "`<tiered>` shows a policy with an [S3] volume alongside another volume.\n"
        "\n"
        "`<s3only>` shows a policy with only an [S3] volume.\n"
        "\n"
        "``` xml\n"
        "<yandex>\n"
        "  <storage_configuration>\n"
        "...\n"
        "    <policies>\n"
        "      <tiered>\n"
        "        <volumes>\n"
        "          <default>\n"
        "            <disk>default</disk>\n"
        "          </default>\n"
        "          <s3>\n"
        "            <disk>s3</disk>\n"
        "          </s3>\n"
        "        </volumes>\n"
        "      </tiered>\n"
        "      <s3only>\n"
        "        <volumes>\n"
        "          <s3>\n"
        "            <disk>s3</disk>\n"
        "          </s3>\n"
        "        </volumes>\n"
        "      </s3only>\n"
        "    </policies>\n"
        "  </storage_configuration>\n"
        "</yandex>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.5.1",
)

RQ_SRS_015_S3_Policy_PerformTTLMoveOnInsert = Requirement(
    name="RQ.SRS-015.S3.Policy.PerformTTLMoveOnInsert",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `<perform_ttl_move_on_insert>` parameter to the\n"
        "`<volume>` section of the desired [S3] disk in the `<policies>` section of the\n"
        "`<storage_configuration>` section of the config.xml file or the storage.xml file\n"
        "in the config.d directory to toggle TTL moves to the [S3] disk on insert\n"
        "operations. If `<perform_ttl_move_on_insert>` is set to 0, insert will go to the\n"
        "first disk in the storage policy, and TTL moves to the [S3] volume will occur in\n"
        "the background.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.5.2",
)

RQ_SRS_015_S3_Policy_PerformTTLMoveOnInsert_Default = Requirement(
    name="RQ.SRS-015.S3.Policy.PerformTTLMoveOnInsert.Default",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL set the `<perform_ttl_move_on_insert>` parameter to 1 by\n"
        "default to perform TTL moves immediately upon an insert operation.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.5.3",
)

RQ_SRS_015_S3_TableFunction_Syntax = Requirement(
    name="RQ.SRS-015.S3.TableFunction.Syntax",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the following syntax for the [S3] table function.\n"
        "\n"
        "``` sql\n"
        "s3(path, [access_key_id, secret_access_key,] format, structure, [compression])\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.1",
)

RQ_SRS_015_S3_TableFunction_Path = Requirement(
    name="RQ.SRS-015.S3.TableFunction.Path",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `<path>` parameter to the [S3] table function to\n"
        "specify the url of the [S3] bucket and the path to the file. This parameter SHALL\n"
        "be mandatory.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.2",
)

RQ_SRS_015_S3_TableFunction_Credentials = Requirement(
    name="RQ.SRS-015.S3.TableFunction.Credentials",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `<access_key_id>` and `<secret_access_key>`\n"
        "parameters to the [S3] table function to authorize access to the [S3] bucket url\n"
        "specified in the `<path>` parameter.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.3",
)

RQ_SRS_015_S3_TableFunction_Credentials_Invalid = Requirement(
    name="RQ.SRS-015.S3.TableFunction.Credentials.Invalid",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if the `<aws_access_key_id>` and\n"
        "`<aws_secret_access_key>` parameters do not provide correct authentication to\n"
        "the [S3] bucket.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.4",
)

RQ_SRS_015_S3_TableFunction_Path_Glob = Requirement(
    name="RQ.SRS-015.S3.TableFunction.Path.Glob",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using glob patterns in file paths to import multiple files from [S3].\n"
        "\n"
        "> Multiple path components can have globs. For being processed file must exist and match to the whole path pattern (not only suffix or prefix).\n"
        ">\n"
        "> * `*` — Substitutes any number of any characters except / including empty string.\n"
        "> * `?` — Substitutes any single character.\n"
        "> * `{some_string,another_string,yet_another_one}` — Substitutes any of strings 'some_string', 'another_string', 'yet_another_one'.\n"
        "> * `{N..M}` — Substitutes any number in range from N to M including both borders.\n"
        "> * `**` - Fetches all files inside the folder recursively.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.5",
)

RQ_SRS_015_S3_TableFunction_ReadFromFile = Requirement(
    name="RQ.SRS-015.S3.TableFunction.ReadFromFile",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading data into the [S3] table function from a file,\n"
        "with syntax similar to the following:\n"
        "\n"
        "``` bash\n"
        "    cat test.csv | INSERT INTO TABLE FUNCTION s3(...)\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.6",
)

RQ_SRS_015_S3_TableFunction_Redirect = Requirement(
    name="RQ.SRS-015.S3.TableFunction.Redirect",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [S3] table function urls which cause redirects with\n"
        "no errors.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.7",
)

RQ_SRS_015_S3_TableFunction_Format = Requirement(
    name="RQ.SRS-015.S3.TableFunction.Format",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `<format>` parameter to the [S3] table function to\n"
        "specify the format of the data using one of the following [data formats].\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.8",
)

RQ_SRS_015_S3_TableFunction_Structure = Requirement(
    name="RQ.SRS-015.S3.TableFunction.Structure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `<structure>` parameter to the [S3] table function to\n"
        "specify the structure of the data. The structure SHALL use the following format:\n"
        "\n"
        "```xml\n"
        "'column1_name column1_type, column2_name column2_type, ...'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.9",
)

RQ_SRS_015_S3_TableFunction_MeasureFileSize = Requirement(
    name="RQ.SRS-015.S3.TableFunction.MeasureFileSize",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL report the accurate size of s3 objects through the `_size`\n"
        "virtual column of the s3 table function.\n"
        "\n"
        "Example:\n"
        "\n"
        "```sql\n"
        "SELECT count() AS files, sum(_size) as bytes\n"
        "FROM s3('https://s3.us-west-2.amazonaws.com/mybucket/clickhouse/demo2/s3_disk/**', 'One')\n"
        "\n"
        "┌─files─┬──────bytes─┐\n"
        "│   122 │ 1638600424 │\n"
        "└───────┴────────────┘\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.10",
)

RQ_SRS_015_S3_TableFunction_Compression = Requirement(
    name="RQ.SRS-015.S3.TableFunction.Compression",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `<compression>` parameter as an optional parameter\n"
        "to the [S3] table function to specify the compression method used with the data.\n"
        "The following compression methods are supported:\n"
        "\n"
        "* `gzip`\n"
        "* `zlib`\n"
        "* `brotli`\n"
        "* `xz`\n"
        "* `zstd`\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.11",
)

RQ_SRS_015_S3_TableFunction_Compression_Auto = Requirement(
    name="RQ.SRS-015.S3.TableFunction.Compression.Auto",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support 'auto' as an input to the `<compression>` parameter of\n"
        "the [S3] table function. If 'auto' is specified, [ClickHouse] SHALL deduce the\n"
        "compression algorithm from the endpoint URL extension. The following URL extensions\n"
        "are supported:\n"
        "\n"
        "* `gzip`\n"
        "* `gz`\n"
        "* `deflate`\n"
        "* `brotli`\n"
        "* `br`\n"
        "* `LZMA`\n"
        "* `xz`\n"
        "* `zstd`\n"
        "* `zst`\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.12",
)

RQ_SRS_015_S3_TableFunction_S3Cluster = Requirement(
    name="RQ.SRS-015.S3.TableFunction.S3Cluster",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading from AWS [S3] clusters using the\n"
        "`s3Cluster` table function. The table function can be used with the following syntax:\n"
        "\n"
        "``` sql\n"
        "s3Cluster(cluster_name, source, [access_key_id, secret_access_key,] format, structure)\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.13",
)

RQ_SRS_015_S3_MinIO_Disk_Configuration = Requirement(
    name="RQ.SRS-015.S3.MinIO.Disk.Configuration",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support configuration of [S3] disks using the MinIO server\n"
        "with syntax similar to the following:\n"
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
    num="4.7.1",
)

RQ_SRS_015_S3_MinIO_TableFunction = Requirement(
    name="RQ.SRS-015.S3.MinIO.TableFunction",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing and exporting data to/from MinIO\n"
        "using the [S3] table function with the following syntax:\n"
        "\n"
        "``` sql\n"
        "s3(http://minio:9000/my-bucket/object-key, [access_key_id, secret_access_key,] format, structure, [compression])\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.7.2",
)

RQ_SRS_015_S3_MinIO_AllowS3ZeroCopyReplication = Requirement(
    name="RQ.SRS-015.S3.MinIO.AllowS3ZeroCopyReplication",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing and exporting data to/from the MinIO\n"
        "server using replicated tables with the ReplicatedMergeTree engine and\n"
        "the `<allow_s3_zero_copy_replication>` parameter set to 1.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.7.3",
)

RQ_SRS_015_S3_AWS_Disk_Configuration = Requirement(
    name="RQ.SRS-015.S3.AWS.Disk.Configuration",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [S3] disk configuration using [AWS S3] with syntax\n"
        "similar to the following:\n"
        "\n"
        "``` xml\n"
        "<yandex>\n"
        "  <storage_configuration>\n"
        "    <disks>\n"
        "      <aws>\n"
        "        <type>s3</type>\n"
        "        <endpoint>http://s3.us-east-1.amazonaws.com/my-bucket/object-key/</endpoint>\n"
        "        <access_key_id>*****</access_key_id>\n"
        "        <secret_access_key>*****</secret_access_key>\n"
        "      </aws>\n"
        "    </disks>\n"
        "...\n"
        "</yandex>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.8.1",
)

RQ_SRS_015_S3_AWS_TableFunction = Requirement(
    name="RQ.SRS-015.S3.AWS.TableFunction",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing and exporting data to/from [AWS S3]\n"
        "using the [S3] table function with the following syntax:\n"
        "\n"
        "``` sql\n"
        "s3(http://s3.us-east-1.amazonaws.com/my-bucket/object-key, [access_key_id, secret_access_key,] format, structure, [compression])\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.8.2",
)

RQ_SRS_015_S3_AWS_Disk_URL = Requirement(
    name="RQ.SRS-015.S3.AWS.Disk.URL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [AWS S3] disks with the endpoint configured using\n"
        "both generic and region-specific bucket URLs.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.8.3",
)

RQ_SRS_015_S3_AWS_Disk_URL_Generic = Requirement(
    name="RQ.SRS-015.S3.AWS.Disk.URL.Generic",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [AWS S3] disks with the endpoint configured using\n"
        "generic bucket URLs with syntax similar to the following:\n"
        "\n"
        "    “https://altinity-clickhouse-data.s3.amazonaws.com/”\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.8.4",
)

RQ_SRS_015_S3_AWS_Disk_URL_Specific = Requirement(
    name="RQ.SRS-015.S3.AWS.Disk.URL.Specific",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [AWS S3] disks with the endpoint configured using\n"
        "region-specific bucket URLs with syntax similar to the following:\n"
        "\n"
        "    “https://s3.us-east-1.amazonaws.com/altinity-clickhouse-data/”\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.8.5",
)

RQ_SRS_015_S3_AWS_EC2_Disk = Requirement(
    name="RQ.SRS-015.S3.AWS.EC2.Disk",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [S3] external storage via one or more disks when\n"
        "running on an AWS EC2 instance.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.8.6",
)

RQ_SRS_015_S3_AWS_EC2_TableFunction = Requirement(
    name="RQ.SRS-015.S3.AWS.EC2.TableFunction",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [S3] external storage via a call to the [S3] table\n"
        "function when running on an EC2 instance. Using the table function, [ClickHouse]\n"
        "SHALL provide read and write functionality. Upon a write, [ClickHouse] SHALL overwrite\n"
        "existing data.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.8.7",
)

RQ_SRS_015_S3_AWS_EC2_Endpoints = Requirement(
    name="RQ.SRS-015.S3.AWS.EC2.Endpoints",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support configuration of [S3] endpoints in the config.xml file\n"
        "using credentials accessible to the entire ClickHouse server, when running on an\n"
        "EC2 instance, with syntax similar to the following:\n"
        "\n"
        "``` xml\n"
        "<yandex>\n"
        "    <s3>\n"
        "       <my_endpoint>\n"
        "           <endpoint>http://s3.us-east-1.amazonaws.com/my-bucket/object-key/</endpoint>\n"
        "           <access_key_id>*****</access_key_id>\n"
        "           <secret_access_key>*****</secret_access_key>\n"
        "           <header>Authorization: Bearer TOKEN</header>\n"
        "       </my_endpoint>\n"
        "   </s3>\n"
        "</yandex>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.8.8",
)

RQ_SRS_015_S3_AWS_AllowS3ZeroCopyReplication = Requirement(
    name="RQ.SRS-015.S3.AWS.AllowS3ZeroCopyReplication",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing and exporting data to/from [AWS S3]\n"
        "using replicated tables with the ReplicatedMergeTree engine and the\n"
        "`<allow_s3_zero_copy_replication>` parameter set to 1.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.8.9",
)

RQ_SRS_015_S3_AWS_SSEC = Requirement(
    name="RQ.SRS-015.S3.AWS.SSEC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using the provided SSEC keys in order to perform\n"
        "server-side encryption and decryption when writing and reading from AWS S3 endpoints.\n"
        "\n"
        "The SSEC key can be specified using the `<server_side_encryption_customer_key_base64>` parameter.\n"
        "Example:\n"
        "\n"
        "```\n"
        "<s3>\n"
        "  <s3-bucket>\n"
        "    <endpoint>masked</endpoint>\n"
        "    <access_key_id>masked</access_key_id>\n"
        "    <secret_access_key>masked</secret_access_key>\n"
        "    <server_side_encryption_customer_key_base64>Wp+aNxm8EkYtL6myH99DYg==</server_side_encryption_customer_key_base64>\n"
        "  </s3-bucket>\n"
        "</s3>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.8.10",
)

RQ_SRS_015_S3_GCS_Disk_Configuration = Requirement(
    name="RQ.SRS-015.S3.GCS.Disk.Configuration",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support configuration of [S3] disks using Google Cloud Storage\n"
        "with syntax similar to the following:\n"
        "\n"
        "``` xml\n"
        "<yandex>\n"
        "  <storage_configuration>\n"
        "    <disks>\n"
        "      <gcs>\n"
        "        <type>s3</type>\n"
        "        <endpoint>https://storage.googleapis.com/my-bucket/object-key/</endpoint>\n"
        "        <access_key_id>*****</access_key_id>\n"
        "        <secret_access_key>*****</secret_access_key>\n"
        "      </gcs>\n"
        "    </disks>\n"
        "...\n"
        "</yandex>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.9.1",
)

RQ_SRS_015_S3_GCS_TableFunction = Requirement(
    name="RQ.SRS-015.S3.GCS.TableFunction",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing and exporting data to/from Google Cloud\n"
        "Storage using the [S3] table function with the following syntax:\n"
        "\n"
        "``` sql\n"
        "s3(https://storage.googleapis.com/my-bucket/object-key, [access_key_id, secret_access_key,] format, structure, [compression])\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.9.2",
)

RQ_SRS_015_S3_GCS_AllowS3ZeroCopyReplication = Requirement(
    name="RQ.SRS-015.S3.GCS.AllowS3ZeroCopyReplication",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing and exporting data to/from GCS\n"
        "using replicated tables with the ReplicatedMergeTree engine and the\n"
        "`<allow_s3_zero_copy_replication>` parameter set to 1.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.9.3",
)

RQ_SRS_015_S3_Azure_Disk_Configuration = Requirement(
    name="RQ.SRS-015.S3.Azure.Disk.Configuration",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support configuration of [Azure Blob Storage] disks\n"
        "with syntax similar to the following:\n"
        "\n"
        "``` xml\n"
        "<yandex>\n"
        "  <storage_configuration>\n"
        "    <disks>\n"
        "      <azure_disk>\n"
        "          <type>azure_blob_storage</type>\n"
        "          <storage_account_url>http://myaccount.blob.core.windows.net</storage_account_url>\n"
        "          <container_name>my-container</container_name>\n"
        "          <account_name>*****</account_name>\n"
        "          <account_key>*****</account_key>\n"
        "      </azure_disk>\n"
        "    </disks>\n"
        "...\n"
        "</yandex>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.10.1",
)

RQ_SRS_015_S3_Azure_AllowS3ZeroCopyReplication = Requirement(
    name="RQ.SRS-015.S3.Azure.AllowS3ZeroCopyReplication",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing and exporting data to/from [Azure Blob Storage]\n"
        "using replicated tables with the ReplicatedMergeTree engine and the\n"
        "`<allow_s3_zero_copy_replication>` parameter set to 1.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.10.2",
)

RQ_SRS_015_S3_Settings_MaxThreads = Requirement(
    name="RQ.SRS-015.S3.Settings.MaxThreads",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL read files from S3 in parallel when the value of `max_threads`\n"
        "is greater than 1.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.11.1",
)

RQ_SRS_015_S3_Settings_MaxDownloadThreads = Requirement(
    name="RQ.SRS-015.S3.Settings.MaxDownloadThreads",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL download files from S3 in parallel using multiple threads\n"
        "specified by `max_download_threads`. Default is 1.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.11.2",
)

RQ_SRS_015_S3_Settings_MaxDownloadBufferSize = Requirement(
    name="RQ.SRS-015.S3.Settings.MaxDownloadBufferSize",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL download files from S3 with a maximum buffer size\n"
        "specified by `max_download_buffer_size`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.11.3",
)

RQ_SRS_015_S3_Settings_PartitionBy = Requirement(
    name="RQ.SRS-015.S3.Settings.PartitionBy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support PARTITION BY expression for the S3 table engine to\n"
        "partition writes to the S3 table into multiple files. These file names SHALL\n"
        "be prefixed by the partition key.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.11.4",
)

RQ_SRS_015_S3_Settings_S3UploadPartSizeMultiplyFactor = Requirement(
    name="RQ.SRS-015.S3.Settings.S3UploadPartSizeMultiplyFactor",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `s3_upload_part_size_multiply_factor` setting to\n"
        "specifying how much `s3_min_upload_part_size` should be increased.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.11.5",
)

RQ_SRS_015_S3_Settings_S3UploadPartSizeMultiplyPartsCountThreshold = Requirement(
    name="RQ.SRS-015.S3.Settings.S3UploadPartSizeMultiplyPartsCountThreshold",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `s3_upload_part_size_multiply_parts_count_threshold` setting\n"
        "to specifying after how many parts the minimum part size should be increased by `s3_upload_part_size_multiply_factor`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.11.6",
)

RQ_SRS_015_S3_Performance_PerformTTLMoveOnInsert = Requirement(
    name="RQ.SRS-015.S3.Performance.PerformTTLMoveOnInsert",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide better insert performance of tiered storage policies\n"
        "with [S3] volumes when the `<perform_ttl_move_on_insert>` parameter of the\n"
        "`<volume>` section of the desired [S3] disk in the `<policies>` section of the\n"
        "`<storage_configuration>` section of the config.xml file or the storage.xml file\n"
        "in the config.d directory is set to 0.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.12.1",
)

RQ_SRS_015_S3_Performance_Glob = Requirement(
    name="RQ.SRS-015.S3.Performance.Glob",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL handle glob patterns efficiently, in reasonable time and without memory errors.\n"
        "Fetch time SHALL be proportional to the amount of data that is fetched,\n"
        "regardless of the total number of items in the bucket.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.12.2",
)

RQ_SRS_015_S3_Performance_AllowS3ZeroCopyReplication_Select = Requirement(
    name="RQ.SRS-015.S3.Performance.AllowS3ZeroCopyReplication.Select",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide similar performance of SELECT operations on tables on\n"
        "[S3] disks when the `<allow_s3_zero_copy_replication>` parameter is set, and when\n"
        "it is not set.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.12.3",
)

RQ_SRS_015_S3_Performance_AllowS3ZeroCopyReplication_Insert = Requirement(
    name="RQ.SRS-015.S3.Performance.AllowS3ZeroCopyReplication.Insert",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide similar performance of INSERT operations on tables on\n"
        "[S3] disks when the `<allow_s3_zero_copy_replication>` parameter is set, and when\n"
        "it is not set.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.12.4",
)

RQ_SRS_015_S3_Performance_AllowS3ZeroCopyReplication_Alter = Requirement(
    name="RQ.SRS-015.S3.Performance.AllowS3ZeroCopyReplication.Alter",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide similar performance of ALTER operations on tables on\n"
        "[S3] disks when the `<allow_s3_zero_copy_replication>` parameter is set, and when\n"
        "it is not set.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.12.5",
)

SRS_015_ClickHouse_S3_External_Storage = Specification(
    name="SRS-015 ClickHouse S3 External Storage",
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
        Heading(name="RQ.SRS-015.S3", level=3, num="4.1.1"),
        Heading(name="RQ.SRS-015.S3.Import", level=3, num="4.1.2"),
        Heading(name="RQ.SRS-015.S3.Export", level=3, num="4.1.3"),
        Heading(name="RQ.SRS-015.S3.Disk", level=3, num="4.1.4"),
        Heading(name="RQ.SRS-015.S3.Policy", level=3, num="4.1.5"),
        Heading(name="RQ.SRS-015.S3.TableFunction", level=3, num="4.1.6"),
        Heading(name="RQ.SRS-015.S3.DataParts", level=3, num="4.1.7"),
        Heading(name="RQ.SRS-015.S3.Security.Encryption", level=3, num="4.1.8"),
        Heading(name="RQ.SRS-015.S3.RemoteHostFilter", level=3, num="4.1.9"),
        Heading(name="RQ.SRS-015.S3.Alter", level=3, num="4.1.10"),
        Heading(name="Backup", level=3, num="4.1.11"),
        Heading(name="RQ.SRS-015.S3.Backup.MinIOBackup", level=4, num="4.1.11.1"),
        Heading(name="RQ.SRS-015.S3.Backup.AWSS3Backup", level=4, num="4.1.11.2"),
        Heading(name="RQ.SRS-015.S3.Backup.GCSBackup", level=4, num="4.1.11.3"),
        Heading(name="RQ.SRS-015.S3.Backup.AzureBackup", level=4, num="4.1.11.4"),
        Heading(name="RQ.SRS-015.S3.Backup.StoragePolicies", level=4, num="4.1.11.5"),
        Heading(name="RQ.SRS-015.S3.Backup.AlterFreeze", level=4, num="4.1.11.6"),
        Heading(name="RQ.SRS-015.S3.Backup.AlterDetach", level=4, num="4.1.11.7"),
        Heading(name="RQ.SRS-015.S3.Backup.AlterAttach", level=4, num="4.1.11.8"),
        Heading(name="RQ.SRS-015.S3.Backup.Cleanup", level=4, num="4.1.11.9"),
        Heading(name="Metadata", level=3, num="4.1.12"),
        Heading(name="RQ.SRS-015.S3.Metadata", level=4, num="4.1.12.1"),
        Heading(name="RQ.SRS-015.S3.Metadata.Revisions", level=4, num="4.1.12.2"),
        Heading(name="RQ.SRS-015.S3.Metadata.BadBackupNumber", level=4, num="4.1.12.3"),
        Heading(name="Metadata Restore", level=3, num="4.1.13"),
        Heading(
            name="RQ.SRS-0.5.S3.MetadataRestore.RestoreFile", level=4, num="4.1.13.1"
        ),
        Heading(
            name="RQ.SRS-0.5.S3.MetadataRestore.BadRestoreFile", level=4, num="4.1.13.2"
        ),
        Heading(
            name="RQ.SRS-0.5.S3.MetadataRestore.HugeRestoreFile",
            level=4,
            num="4.1.13.3",
        ),
        Heading(
            name="RQ.SRS-015.S3.MetadataRestore.NoLocalMetadata",
            level=4,
            num="4.1.13.4",
        ),
        Heading(
            name="RQ.SRS-015.S3.MetadataRestore.BucketPath", level=4, num="4.1.13.5"
        ),
        Heading(
            name="RQ.SRS-015.S3.MetadataRestore.RevisionRestore",
            level=4,
            num="4.1.13.6",
        ),
        Heading(
            name="RQ.SRS-015.S3.MetadataRestore.Mutations", level=4, num="4.1.13.7"
        ),
        Heading(
            name="RQ.SRS-015.S3.MetadataRestore.ParallelMutations",
            level=4,
            num="4.1.13.8",
        ),
        Heading(name="RQ.SRS-015.S3.MetadataRestore.Detached", level=4, num="4.1.13.9"),
        Heading(name="RQ.SRS-015.S3.AWS", level=3, num="4.1.14"),
        Heading(name="RQ.SRS-015.S3.MinIO", level=3, num="4.1.15"),
        Heading(name="RQ.SRS-015.S3.GCS", level=3, num="4.1.16"),
        Heading(name="RQ.SRS-015.S3.Azure", level=3, num="4.1.17"),
        Heading(name="Automatic Reconnects", level=3, num="4.1.18"),
        Heading(name="RQ.SRS-015.S3.AutomaticReconnects.GCS", level=4, num="4.1.18.1"),
        Heading(name="RQ.SRS-015.S3.AutomaticReconnects.AWS", level=4, num="4.1.18.2"),
        Heading(
            name="RQ.SRS-015.S3.AutomaticReconnects.MinIO", level=4, num="4.1.18.3"
        ),
        Heading(
            name="RQ.SRS-015.S3.AutomaticReconnects.Azure", level=4, num="4.1.18.4"
        ),
        Heading(name="Users", level=2, num="4.2"),
        Heading(
            name="RQ.SRS-015.S3.User.Configuration.Cache.22.8.EnableFilesystemCache",
            level=3,
            num="4.2.1",
        ),
        Heading(
            name="RQ.SRS-015.S3.User.Configuration.Cache.22.8.EnableFilesystemCacheOnWriteOperations",
            level=3,
            num="4.2.2",
        ),
        Heading(name="RQ.SRS-015.S3.FilesystemCacheLog.22.8", level=2, num="4.3"),
        Heading(name="Disk", level=2, num="4.4"),
        Heading(
            name="RQ.SRS-015.S3.Disk.AddingMoreStorageDevices", level=3, num="4.4.1"
        ),
        Heading(name="RQ.SRS-015.S3.Disk.Endpoints", level=3, num="4.4.2"),
        Heading(name="RQ.SRS-015.S3.Disk.MultipleStorageDevices", level=3, num="4.4.3"),
        Heading(
            name="RQ.SRS-015.S3.Disk.MultipleStorageDevices.NoChangesForQuerying",
            level=3,
            num="4.4.4",
        ),
        Heading(name="RQ.SRS-015.S3.Disk.Metadata", level=3, num="4.4.5"),
        Heading(name="RQ.SRS-015.S3.Disk.DropSync", level=3, num="4.4.6"),
        Heading(name="Disk Configuration", level=3, num="4.4.7"),
        Heading(name="RQ.SRS-015.S3.Disk.Configuration", level=4, num="4.4.7.1"),
        Heading(name="RQ.SRS-015.S3.Disk.Configuration.Syntax", level=4, num="4.4.7.2"),
        Heading(
            name="RQ.SRS-015.S3.Disk.Configuration.Invalid", level=4, num="4.4.7.3"
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.Configuration.Changes.NoRestart",
            level=4,
            num="4.4.7.4",
        ),
        Heading(name="RQ.SRS-015.S3.Disk.Configuration.Access", level=4, num="4.4.7.5"),
        Heading(
            name="RQ.SRS-015.S3.Disk.Configuration.Access.Default",
            level=4,
            num="4.4.7.6",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.Configuration.CacheEnabled", level=4, num="4.4.7.7"
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.Configuration.CacheEnabled.Default",
            level=4,
            num="4.4.7.8",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.Configuration.Cache.22.8", level=4, num="4.4.7.9"
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.CacheOnWriteOperations",
            level=4,
            num="4.4.7.10",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.DataCacheMaxSize",
            level=4,
            num="4.4.7.11",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.EnableCacheHitsThreshold",
            level=4,
            num="4.4.7.12",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.FileSystemQueryCacheLimit",
            level=4,
            num="4.4.7.13",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.Configuration.CachePath", level=4, num="4.4.7.14"
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.Configuration.CachePath.Conflict",
            level=4,
            num="4.4.7.15",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.Configuration.MinBytesForSeek",
            level=4,
            num="4.4.7.16",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.Configuration.MinBytesForSeek.Syntax",
            level=4,
            num="4.4.7.17",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.Configuration.S3MaxSinglePartUploadSize",
            level=4,
            num="4.4.7.18",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.Configuration.S3MaxSinglePartUploadSize.Syntax",
            level=4,
            num="4.4.7.19",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.Configuration.S3UseEnvironmentCredentials",
            level=4,
            num="4.4.7.20",
        ),
        Heading(name="MergeTree Engine Family", level=3, num="4.4.8"),
        Heading(name="RQ.SRS-015.S3.Disk.MergeTree", level=4, num="4.4.8.1"),
        Heading(name="RQ.SRS-015.S3.Disk.MergeTree.MergeTree", level=4, num="4.4.8.2"),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.ReplacingMergeTree",
            level=4,
            num="4.4.8.3",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.SummingMergeTree", level=4, num="4.4.8.4"
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.AggregatingMergeTree",
            level=4,
            num="4.4.8.5",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.CollapsingMergeTree",
            level=4,
            num="4.4.8.6",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.VersionedCollapsingMergeTree",
            level=4,
            num="4.4.8.7",
        ),
        Heading(name="S3 Zero Copy Replication", level=4, num="4.4.8.8"),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication",
            level=5,
            num="4.4.8.8.1",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Default",
            level=5,
            num="4.4.8.8.2",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Global",
            level=5,
            num="4.4.8.8.3",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Metadata",
            level=5,
            num="4.4.8.8.4",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Alter",
            level=5,
            num="4.4.8.8.5",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Delete",
            level=5,
            num="4.4.8.8.6",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.DeleteAll",
            level=5,
            num="4.4.8.8.7",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.DataPreservedAfterMutation",
            level=5,
            num="4.4.8.8.8",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.DropReplica",
            level=5,
            num="4.4.8.8.9",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.AddReplica",
            level=5,
            num="4.4.8.8.10",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.NoDataDuplication",
            level=5,
            num="4.4.8.8.11",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.TTL.Move",
            level=5,
            num="4.4.8.8.12",
        ),
        Heading(
            name="RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.TTL.Delete",
            level=5,
            num="4.4.8.8.13",
        ),
        Heading(name="Policy", level=2, num="4.5"),
        Heading(name="RQ.SRS-015.S3.Policy.Syntax", level=3, num="4.5.1"),
        Heading(
            name="RQ.SRS-015.S3.Policy.PerformTTLMoveOnInsert", level=3, num="4.5.2"
        ),
        Heading(
            name="RQ.SRS-015.S3.Policy.PerformTTLMoveOnInsert.Default",
            level=3,
            num="4.5.3",
        ),
        Heading(name="Table Function", level=2, num="4.6"),
        Heading(name="RQ.SRS-015.S3.TableFunction.Syntax", level=3, num="4.6.1"),
        Heading(name="RQ.SRS-015.S3.TableFunction.Path", level=3, num="4.6.2"),
        Heading(name="RQ.SRS-015.S3.TableFunction.Credentials", level=3, num="4.6.3"),
        Heading(
            name="RQ.SRS-015.S3.TableFunction.Credentials.Invalid", level=3, num="4.6.4"
        ),
        Heading(name="RQ.SRS-015.S3.TableFunction.Path.Glob", level=3, num="4.6.5"),
        Heading(name="RQ.SRS-015.S3.TableFunction.ReadFromFile", level=3, num="4.6.6"),
        Heading(name="RQ.SRS-015.S3.TableFunction.Redirect", level=3, num="4.6.7"),
        Heading(name="RQ.SRS-015.S3.TableFunction.Format", level=3, num="4.6.8"),
        Heading(name="RQ.SRS-015.S3.TableFunction.Structure", level=3, num="4.6.9"),
        Heading(
            name="RQ.SRS-015.S3.TableFunction.MeasureFileSize", level=3, num="4.6.10"
        ),
        Heading(name="RQ.SRS-015.S3.TableFunction.Compression", level=3, num="4.6.11"),
        Heading(
            name="RQ.SRS-015.S3.TableFunction.Compression.Auto", level=3, num="4.6.12"
        ),
        Heading(name="RQ.SRS-015.S3.TableFunction.S3Cluster", level=3, num="4.6.13"),
        Heading(name="MinIO", level=2, num="4.7"),
        Heading(name="RQ.SRS-015.S3.MinIO.Disk.Configuration", level=3, num="4.7.1"),
        Heading(name="RQ.SRS-015.S3.MinIO.TableFunction", level=3, num="4.7.2"),
        Heading(
            name="RQ.SRS-015.S3.MinIO.AllowS3ZeroCopyReplication", level=3, num="4.7.3"
        ),
        Heading(name="AWS", level=2, num="4.8"),
        Heading(name="RQ.SRS-015.S3.AWS.Disk.Configuration", level=3, num="4.8.1"),
        Heading(name="RQ.SRS-015.S3.AWS.TableFunction", level=3, num="4.8.2"),
        Heading(name="RQ.SRS-015.S3.AWS.Disk.URL", level=3, num="4.8.3"),
        Heading(name="RQ.SRS-015.S3.AWS.Disk.URL.Generic", level=3, num="4.8.4"),
        Heading(name="RQ.SRS-015.S3.AWS.Disk.URL.Specific", level=3, num="4.8.5"),
        Heading(name="RQ.SRS-015.S3.AWS.EC2.Disk", level=3, num="4.8.6"),
        Heading(name="RQ.SRS-015.S3.AWS.EC2.TableFunction", level=3, num="4.8.7"),
        Heading(name="RQ.SRS-015.S3.AWS.EC2.Endpoints", level=3, num="4.8.8"),
        Heading(
            name="RQ.SRS-015.S3.AWS.AllowS3ZeroCopyReplication", level=3, num="4.8.9"
        ),
        Heading(name="RQ.SRS-015.S3.AWS.SSEC", level=3, num="4.8.10"),
        Heading(name="GCS", level=2, num="4.9"),
        Heading(name="RQ.SRS-015.S3.GCS.Disk.Configuration", level=3, num="4.9.1"),
        Heading(name="RQ.SRS-015.S3.GCS.TableFunction", level=3, num="4.9.2"),
        Heading(
            name="RQ.SRS-015.S3.GCS.AllowS3ZeroCopyReplication", level=3, num="4.9.3"
        ),
        Heading(name="Azure", level=2, num="4.10"),
        Heading(name="RQ.SRS-015.S3.Azure.Disk.Configuration", level=3, num="4.10.1"),
        Heading(
            name="RQ.SRS-015.S3.Azure.AllowS3ZeroCopyReplication", level=3, num="4.10.2"
        ),
        Heading(name="Settings", level=2, num="4.11"),
        Heading(name="RQ.SRS-015.S3.Settings.MaxThreads", level=3, num="4.11.1"),
        Heading(
            name="RQ.SRS-015.S3.Settings.MaxDownloadThreads", level=3, num="4.11.2"
        ),
        Heading(
            name="RQ.SRS-015.S3.Settings.MaxDownloadBufferSize", level=3, num="4.11.3"
        ),
        Heading(name="RQ.SRS-015.S3.Settings.PartitionBy", level=3, num="4.11.4"),
        Heading(
            name="RQ.SRS-015.S3.Settings.S3UploadPartSizeMultiplyFactor",
            level=3,
            num="4.11.5",
        ),
        Heading(
            name="RQ.SRS-015.S3.Settings.S3UploadPartSizeMultiplyPartsCountThreshold",
            level=3,
            num="4.11.6",
        ),
        Heading(name="Performance", level=2, num="4.12"),
        Heading(
            name="RQ.SRS-015.S3.Performance.PerformTTLMoveOnInsert",
            level=3,
            num="4.12.1",
        ),
        Heading(name="RQ.SRS-015.S3.Performance.Glob", level=3, num="4.12.2"),
        Heading(
            name="RQ.SRS-015.S3.Performance.AllowS3ZeroCopyReplication.Select",
            level=3,
            num="4.12.3",
        ),
        Heading(
            name="RQ.SRS-015.S3.Performance.AllowS3ZeroCopyReplication.Insert",
            level=3,
            num="4.12.4",
        ),
        Heading(
            name="RQ.SRS-015.S3.Performance.AllowS3ZeroCopyReplication.Alter",
            level=3,
            num="4.12.5",
        ),
        Heading(name="References", level=1, num="5"),
    ),
    requirements=(
        RQ_SRS_015_S3,
        RQ_SRS_015_S3_Import,
        RQ_SRS_015_S3_Export,
        RQ_SRS_015_S3_Disk,
        RQ_SRS_015_S3_Policy,
        RQ_SRS_015_S3_TableFunction,
        RQ_SRS_015_S3_DataParts,
        RQ_SRS_015_S3_Security_Encryption,
        RQ_SRS_015_S3_RemoteHostFilter,
        RQ_SRS_015_S3_Alter,
        RQ_SRS_015_S3_Backup_MinIOBackup,
        RQ_SRS_015_S3_Backup_AWSS3Backup,
        RQ_SRS_015_S3_Backup_GCSBackup,
        RQ_SRS_015_S3_Backup_AzureBackup,
        RQ_SRS_015_S3_Backup_StoragePolicies,
        RQ_SRS_015_S3_Backup_AlterFreeze,
        RQ_SRS_015_S3_Backup_AlterDetach,
        RQ_SRS_015_S3_Backup_AlterAttach,
        RQ_SRS_015_S3_Backup_Cleanup,
        RQ_SRS_015_S3_Metadata,
        RQ_SRS_015_S3_Metadata_Revisions,
        RQ_SRS_015_S3_Metadata_BadBackupNumber,
        RQ_SRS_0_5_S3_MetadataRestore_RestoreFile,
        RQ_SRS_0_5_S3_MetadataRestore_BadRestoreFile,
        RQ_SRS_0_5_S3_MetadataRestore_HugeRestoreFile,
        RQ_SRS_015_S3_MetadataRestore_NoLocalMetadata,
        RQ_SRS_015_S3_MetadataRestore_BucketPath,
        RQ_SRS_015_S3_MetadataRestore_RevisionRestore,
        RQ_SRS_015_S3_MetadataRestore_Mutations,
        RQ_SRS_015_S3_MetadataRestore_ParallelMutations,
        RQ_SRS_015_S3_MetadataRestore_Detached,
        RQ_SRS_015_S3_AWS,
        RQ_SRS_015_S3_MinIO,
        RQ_SRS_015_S3_GCS,
        RQ_SRS_015_S3_Azure,
        RQ_SRS_015_S3_AutomaticReconnects_GCS,
        RQ_SRS_015_S3_AutomaticReconnects_AWS,
        RQ_SRS_015_S3_AutomaticReconnects_MinIO,
        RQ_SRS_015_S3_AutomaticReconnects_Azure,
        RQ_SRS_015_S3_User_Configuration_Cache_22_8_EnableFilesystemCache,
        RQ_SRS_015_S3_User_Configuration_Cache_22_8_EnableFilesystemCacheOnWriteOperations,
        RQ_SRS_015_S3_FilesystemCacheLog_22_8,
        RQ_SRS_015_S3_Disk_AddingMoreStorageDevices,
        RQ_SRS_015_S3_Disk_Endpoints,
        RQ_SRS_015_S3_Disk_MultipleStorageDevices,
        RQ_SRS_015_S3_Disk_MultipleStorageDevices_NoChangesForQuerying,
        RQ_SRS_015_S3_Disk_Metadata,
        RQ_SRS_015_S3_Disk_DropSync,
        RQ_SRS_015_S3_Disk_Configuration,
        RQ_SRS_015_S3_Disk_Configuration_Syntax,
        RQ_SRS_015_S3_Disk_Configuration_Invalid,
        RQ_SRS_015_S3_Disk_Configuration_Changes_NoRestart,
        RQ_SRS_015_S3_Disk_Configuration_Access,
        RQ_SRS_015_S3_Disk_Configuration_Access_Default,
        RQ_SRS_015_S3_Disk_Configuration_CacheEnabled,
        RQ_SRS_015_S3_Disk_Configuration_CacheEnabled_Default,
        RQ_SRS_015_S3_Disk_Configuration_Cache_22_8,
        RQ_SRS_015_S3_Disk_Configuration_Cache_22_8_CacheOnWriteOperations,
        RQ_SRS_015_S3_Disk_Configuration_Cache_22_8_DataCacheMaxSize,
        RQ_SRS_015_S3_Disk_Configuration_Cache_22_8_EnableCacheHitsThreshold,
        RQ_SRS_015_S3_Disk_Configuration_Cache_22_8_FileSystemQueryCacheLimit,
        RQ_SRS_015_S3_Disk_Configuration_CachePath,
        RQ_SRS_015_S3_Disk_Configuration_CachePath_Conflict,
        RQ_SRS_015_S3_Disk_Configuration_MinBytesForSeek,
        RQ_SRS_015_S3_Disk_Configuration_MinBytesForSeek_Syntax,
        RQ_SRS_015_S3_Disk_Configuration_S3MaxSinglePartUploadSize,
        RQ_SRS_015_S3_Disk_Configuration_S3MaxSinglePartUploadSize_Syntax,
        RQ_SRS_015_S3_Disk_Configuration_S3UseEnvironmentCredentials,
        RQ_SRS_015_S3_Disk_MergeTree,
        RQ_SRS_015_S3_Disk_MergeTree_MergeTree,
        RQ_SRS_015_S3_Disk_MergeTree_ReplacingMergeTree,
        RQ_SRS_015_S3_Disk_MergeTree_SummingMergeTree,
        RQ_SRS_015_S3_Disk_MergeTree_AggregatingMergeTree,
        RQ_SRS_015_S3_Disk_MergeTree_CollapsingMergeTree,
        RQ_SRS_015_S3_Disk_MergeTree_VersionedCollapsingMergeTree,
        RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication,
        RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Default,
        RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Global,
        RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Metadata,
        RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Alter,
        RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Delete,
        RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_DeleteAll,
        RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_DataPreservedAfterMutation,
        RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_DropReplica,
        RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_AddReplica,
        RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_NoDataDuplication,
        RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_TTL_Move,
        RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_TTL_Delete,
        RQ_SRS_015_S3_Policy_Syntax,
        RQ_SRS_015_S3_Policy_PerformTTLMoveOnInsert,
        RQ_SRS_015_S3_Policy_PerformTTLMoveOnInsert_Default,
        RQ_SRS_015_S3_TableFunction_Syntax,
        RQ_SRS_015_S3_TableFunction_Path,
        RQ_SRS_015_S3_TableFunction_Credentials,
        RQ_SRS_015_S3_TableFunction_Credentials_Invalid,
        RQ_SRS_015_S3_TableFunction_Path_Glob,
        RQ_SRS_015_S3_TableFunction_ReadFromFile,
        RQ_SRS_015_S3_TableFunction_Redirect,
        RQ_SRS_015_S3_TableFunction_Format,
        RQ_SRS_015_S3_TableFunction_Structure,
        RQ_SRS_015_S3_TableFunction_MeasureFileSize,
        RQ_SRS_015_S3_TableFunction_Compression,
        RQ_SRS_015_S3_TableFunction_Compression_Auto,
        RQ_SRS_015_S3_TableFunction_S3Cluster,
        RQ_SRS_015_S3_MinIO_Disk_Configuration,
        RQ_SRS_015_S3_MinIO_TableFunction,
        RQ_SRS_015_S3_MinIO_AllowS3ZeroCopyReplication,
        RQ_SRS_015_S3_AWS_Disk_Configuration,
        RQ_SRS_015_S3_AWS_TableFunction,
        RQ_SRS_015_S3_AWS_Disk_URL,
        RQ_SRS_015_S3_AWS_Disk_URL_Generic,
        RQ_SRS_015_S3_AWS_Disk_URL_Specific,
        RQ_SRS_015_S3_AWS_EC2_Disk,
        RQ_SRS_015_S3_AWS_EC2_TableFunction,
        RQ_SRS_015_S3_AWS_EC2_Endpoints,
        RQ_SRS_015_S3_AWS_AllowS3ZeroCopyReplication,
        RQ_SRS_015_S3_AWS_SSEC,
        RQ_SRS_015_S3_GCS_Disk_Configuration,
        RQ_SRS_015_S3_GCS_TableFunction,
        RQ_SRS_015_S3_GCS_AllowS3ZeroCopyReplication,
        RQ_SRS_015_S3_Azure_Disk_Configuration,
        RQ_SRS_015_S3_Azure_AllowS3ZeroCopyReplication,
        RQ_SRS_015_S3_Settings_MaxThreads,
        RQ_SRS_015_S3_Settings_MaxDownloadThreads,
        RQ_SRS_015_S3_Settings_MaxDownloadBufferSize,
        RQ_SRS_015_S3_Settings_PartitionBy,
        RQ_SRS_015_S3_Settings_S3UploadPartSizeMultiplyFactor,
        RQ_SRS_015_S3_Settings_S3UploadPartSizeMultiplyPartsCountThreshold,
        RQ_SRS_015_S3_Performance_PerformTTLMoveOnInsert,
        RQ_SRS_015_S3_Performance_Glob,
        RQ_SRS_015_S3_Performance_AllowS3ZeroCopyReplication_Select,
        RQ_SRS_015_S3_Performance_AllowS3ZeroCopyReplication_Insert,
        RQ_SRS_015_S3_Performance_AllowS3ZeroCopyReplication_Alter,
    ),
    content=r"""
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
    * 4.1.10 [RQ.SRS-015.S3.Alter](#rqsrs-015s3alter)
    * 4.1.11 [Backup](#backup)
      * 4.1.11.1 [RQ.SRS-015.S3.Backup.MinIOBackup](#rqsrs-015s3backupminiobackup)
      * 4.1.11.2 [RQ.SRS-015.S3.Backup.AWSS3Backup](#rqsrs-015s3backupawss3backup)
      * 4.1.11.3 [RQ.SRS-015.S3.Backup.GCSBackup](#rqsrs-015s3backupgcsbackup)
      * 4.1.11.4 [RQ.SRS-015.S3.Backup.AzureBackup](#rqsrs-015s3backupazurebackup)
      * 4.1.11.5 [RQ.SRS-015.S3.Backup.StoragePolicies](#rqsrs-015s3backupstoragepolicies)
      * 4.1.11.6 [RQ.SRS-015.S3.Backup.AlterFreeze](#rqsrs-015s3backupalterfreeze)
      * 4.1.11.7 [RQ.SRS-015.S3.Backup.AlterDetach](#rqsrs-015s3backupalterdetach)
      * 4.1.11.8 [RQ.SRS-015.S3.Backup.AlterAttach](#rqsrs-015s3backupalterattach)
      * 4.1.11.9 [RQ.SRS-015.S3.Backup.Cleanup](#rqsrs-015s3backupcleanup)
    * 4.1.12 [Metadata](#metadata)
      * 4.1.12.1 [RQ.SRS-015.S3.Metadata](#rqsrs-015s3metadata)
      * 4.1.12.2 [RQ.SRS-015.S3.Metadata.Revisions](#rqsrs-015s3metadatarevisions)
      * 4.1.12.3 [RQ.SRS-015.S3.Metadata.BadBackupNumber](#rqsrs-015s3metadatabadbackupnumber)
    * 4.1.13 [Metadata Restore](#metadata-restore)
      * 4.1.13.1 [RQ.SRS-0.5.S3.MetadataRestore.RestoreFile](#rqsrs-05s3metadatarestorerestorefile)
      * 4.1.13.2 [RQ.SRS-0.5.S3.MetadataRestore.BadRestoreFile](#rqsrs-05s3metadatarestorebadrestorefile)
      * 4.1.13.3 [RQ.SRS-0.5.S3.MetadataRestore.HugeRestoreFile](#rqsrs-05s3metadatarestorehugerestorefile)
      * 4.1.13.4 [RQ.SRS-015.S3.MetadataRestore.NoLocalMetadata](#rqsrs-015s3metadatarestorenolocalmetadata)
      * 4.1.13.5 [RQ.SRS-015.S3.MetadataRestore.BucketPath](#rqsrs-015s3metadatarestorebucketpath)
      * 4.1.13.6 [RQ.SRS-015.S3.MetadataRestore.RevisionRestore](#rqsrs-015s3metadatarestorerevisionrestore)
      * 4.1.13.7 [RQ.SRS-015.S3.MetadataRestore.Mutations](#rqsrs-015s3metadatarestoremutations)
      * 4.1.13.8 [RQ.SRS-015.S3.MetadataRestore.ParallelMutations](#rqsrs-015s3metadatarestoreparallelmutations)
      * 4.1.13.9 [RQ.SRS-015.S3.MetadataRestore.Detached](#rqsrs-015s3metadatarestoredetached)
    * 4.1.14 [RQ.SRS-015.S3.AWS](#rqsrs-015s3aws)
    * 4.1.15 [RQ.SRS-015.S3.MinIO](#rqsrs-015s3minio)
    * 4.1.16 [RQ.SRS-015.S3.GCS](#rqsrs-015s3gcs)
    * 4.1.17 [RQ.SRS-015.S3.Azure](#rqsrs-015s3azure)
    * 4.1.18 [Automatic Reconnects](#automatic-reconnects)
      * 4.1.18.1 [RQ.SRS-015.S3.AutomaticReconnects.GCS](#rqsrs-015s3automaticreconnectsgcs)
      * 4.1.18.2 [RQ.SRS-015.S3.AutomaticReconnects.AWS](#rqsrs-015s3automaticreconnectsaws)
      * 4.1.18.3 [RQ.SRS-015.S3.AutomaticReconnects.MinIO](#rqsrs-015s3automaticreconnectsminio)
      * 4.1.18.4 [RQ.SRS-015.S3.AutomaticReconnects.Azure](#rqsrs-015s3automaticreconnectsazure)
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
    * 4.4.6 [RQ.SRS-015.S3.Disk.DropSync](#rqsrs-015s3diskdropsync)
    * 4.4.7 [Disk Configuration](#disk-configuration)
      * 4.4.7.1 [RQ.SRS-015.S3.Disk.Configuration](#rqsrs-015s3diskconfiguration)
      * 4.4.7.2 [RQ.SRS-015.S3.Disk.Configuration.Syntax](#rqsrs-015s3diskconfigurationsyntax)
      * 4.4.7.3 [RQ.SRS-015.S3.Disk.Configuration.Invalid](#rqsrs-015s3diskconfigurationinvalid)
      * 4.4.7.4 [RQ.SRS-015.S3.Disk.Configuration.Changes.NoRestart](#rqsrs-015s3diskconfigurationchangesnorestart)
      * 4.4.7.5 [RQ.SRS-015.S3.Disk.Configuration.Access](#rqsrs-015s3diskconfigurationaccess)
      * 4.4.7.6 [RQ.SRS-015.S3.Disk.Configuration.Access.Default](#rqsrs-015s3diskconfigurationaccessdefault)
      * 4.4.7.7 [RQ.SRS-015.S3.Disk.Configuration.CacheEnabled](#rqsrs-015s3diskconfigurationcacheenabled)
      * 4.4.7.8 [RQ.SRS-015.S3.Disk.Configuration.CacheEnabled.Default](#rqsrs-015s3diskconfigurationcacheenableddefault)
      * 4.4.7.9 [RQ.SRS-015.S3.Disk.Configuration.Cache.22.8](#rqsrs-015s3diskconfigurationcache228)
      * 4.4.7.10 [RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.CacheOnWriteOperations](#rqsrs-015s3diskconfigurationcache228cacheonwriteoperations)
      * 4.4.7.11 [RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.DataCacheMaxSize](#rqsrs-015s3diskconfigurationcache228datacachemaxsize)
      * 4.4.7.12 [RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.EnableCacheHitsThreshold](#rqsrs-015s3diskconfigurationcache228enablecachehitsthreshold)
      * 4.4.7.13 [RQ.SRS-015.S3.Disk.Configuration.Cache.22.8.FileSystemQueryCacheLimit](#rqsrs-015s3diskconfigurationcache228filesystemquerycachelimit)
      * 4.4.7.14 [RQ.SRS-015.S3.Disk.Configuration.CachePath](#rqsrs-015s3diskconfigurationcachepath)
      * 4.4.7.15 [RQ.SRS-015.S3.Disk.Configuration.CachePath.Conflict](#rqsrs-015s3diskconfigurationcachepathconflict)
      * 4.4.7.16 [RQ.SRS-015.S3.Disk.Configuration.MinBytesForSeek](#rqsrs-015s3diskconfigurationminbytesforseek)
      * 4.4.7.17 [RQ.SRS-015.S3.Disk.Configuration.MinBytesForSeek.Syntax](#rqsrs-015s3diskconfigurationminbytesforseeksyntax)
      * 4.4.7.18 [RQ.SRS-015.S3.Disk.Configuration.S3MaxSinglePartUploadSize](#rqsrs-015s3diskconfigurations3maxsinglepartuploadsize)
      * 4.4.7.19 [RQ.SRS-015.S3.Disk.Configuration.S3MaxSinglePartUploadSize.Syntax](#rqsrs-015s3diskconfigurations3maxsinglepartuploadsizesyntax)
      * 4.4.7.20 [RQ.SRS-015.S3.Disk.Configuration.S3UseEnvironmentCredentials](#rqsrs-015s3diskconfigurations3useenvironmentcredentials)
    * 4.4.8 [MergeTree Engine Family](#mergetree-engine-family)
      * 4.4.8.1 [RQ.SRS-015.S3.Disk.MergeTree](#rqsrs-015s3diskmergetree)
      * 4.4.8.2 [RQ.SRS-015.S3.Disk.MergeTree.MergeTree](#rqsrs-015s3diskmergetreemergetree)
      * 4.4.8.3 [RQ.SRS-015.S3.Disk.MergeTree.ReplacingMergeTree](#rqsrs-015s3diskmergetreereplacingmergetree)
      * 4.4.8.4 [RQ.SRS-015.S3.Disk.MergeTree.SummingMergeTree](#rqsrs-015s3diskmergetreesummingmergetree)
      * 4.4.8.5 [RQ.SRS-015.S3.Disk.MergeTree.AggregatingMergeTree](#rqsrs-015s3diskmergetreeaggregatingmergetree)
      * 4.4.8.6 [RQ.SRS-015.S3.Disk.MergeTree.CollapsingMergeTree](#rqsrs-015s3diskmergetreecollapsingmergetree)
      * 4.4.8.7 [RQ.SRS-015.S3.Disk.MergeTree.VersionedCollapsingMergeTree](#rqsrs-015s3diskmergetreeversionedcollapsingmergetree)
      * 4.4.8.8 [S3 Zero Copy Replication](#s3-zero-copy-replication)
        * 4.4.8.8.1 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication](#rqsrs-015s3diskmergetreeallows3zerocopyreplication)
        * 4.4.8.8.2 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Default](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationdefault)
        * 4.4.8.8.3 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Global](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationglobal)
        * 4.4.8.8.4 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Metadata](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationmetadata)
        * 4.4.8.8.5 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Alter](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationalter)
        * 4.4.8.8.6 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Delete](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationdelete)
        * 4.4.8.8.7 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.DeleteAll](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationdeleteall)
        * 4.4.8.8.8 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.DataPreservedAfterMutation](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationdatapreservedaftermutation)
        * 4.4.8.8.9 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.DropReplica](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationdropreplica)
        * 4.4.8.8.10 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.AddReplica](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationaddreplica)
        * 4.4.8.8.11 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.NoDataDuplication](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationnodataduplication)
        * 4.4.8.8.12 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.TTL.Move](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationttlmove)
        * 4.4.8.8.13 [RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.TTL.Delete](#rqsrs-015s3diskmergetreeallows3zerocopyreplicationttldelete)
  * 4.5 [Policy](#policy)
    * 4.5.1 [RQ.SRS-015.S3.Policy.Syntax](#rqsrs-015s3policysyntax)
    * 4.5.2 [RQ.SRS-015.S3.Policy.PerformTTLMoveOnInsert](#rqsrs-015s3policyperformttlmoveoninsert)
    * 4.5.3 [RQ.SRS-015.S3.Policy.PerformTTLMoveOnInsert.Default](#rqsrs-015s3policyperformttlmoveoninsertdefault)
  * 4.6 [Table Function](#table-function)
    * 4.6.1 [RQ.SRS-015.S3.TableFunction.Syntax](#rqsrs-015s3tablefunctionsyntax)
    * 4.6.2 [RQ.SRS-015.S3.TableFunction.Path](#rqsrs-015s3tablefunctionpath)
    * 4.6.3 [RQ.SRS-015.S3.TableFunction.Credentials](#rqsrs-015s3tablefunctioncredentials)
    * 4.6.4 [RQ.SRS-015.S3.TableFunction.Credentials.Invalid](#rqsrs-015s3tablefunctioncredentialsinvalid)
    * 4.6.5 [RQ.SRS-015.S3.TableFunction.Path.Glob](#rqsrs-015s3tablefunctionpathglob)
    * 4.6.6 [RQ.SRS-015.S3.TableFunction.ReadFromFile](#rqsrs-015s3tablefunctionreadfromfile)
    * 4.6.7 [RQ.SRS-015.S3.TableFunction.Redirect](#rqsrs-015s3tablefunctionredirect)
    * 4.6.8 [RQ.SRS-015.S3.TableFunction.Format](#rqsrs-015s3tablefunctionformat)
    * 4.6.9 [RQ.SRS-015.S3.TableFunction.Structure](#rqsrs-015s3tablefunctionstructure)
    * 4.6.10 [RQ.SRS-015.S3.TableFunction.MeasureFileSize](#rqsrs-015s3tablefunctionmeasurefilesize)
    * 4.6.11 [RQ.SRS-015.S3.TableFunction.Compression](#rqsrs-015s3tablefunctioncompression)
    * 4.6.12 [RQ.SRS-015.S3.TableFunction.Compression.Auto](#rqsrs-015s3tablefunctioncompressionauto)
    * 4.6.13 [RQ.SRS-015.S3.TableFunction.S3Cluster](#rqsrs-015s3tablefunctions3cluster)
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
  * 4.10 [Azure](#azure)
    * 4.10.1 [RQ.SRS-015.S3.Azure.Disk.Configuration](#rqsrs-015s3azurediskconfiguration)
    * 4.10.2 [RQ.SRS-015.S3.Azure.AllowS3ZeroCopyReplication](#rqsrs-015s3azureallows3zerocopyreplication)
  * 4.11 [Settings](#settings)
    * 4.11.1 [RQ.SRS-015.S3.Settings.MaxThreads](#rqsrs-015s3settingsmaxthreads)
    * 4.11.2 [RQ.SRS-015.S3.Settings.MaxDownloadThreads](#rqsrs-015s3settingsmaxdownloadthreads)
    * 4.11.3 [RQ.SRS-015.S3.Settings.MaxDownloadBufferSize](#rqsrs-015s3settingsmaxdownloadbuffersize)
    * 4.11.4 [RQ.SRS-015.S3.Settings.PartitionBy](#rqsrs-015s3settingspartitionby)
    * 4.11.5 [RQ.SRS-015.S3.Settings.S3UploadPartSizeMultiplyFactor](#rqsrs-015s3settingss3uploadpartsizemultiplyfactor)
    * 4.11.6 [RQ.SRS-015.S3.Settings.S3UploadPartSizeMultiplyPartsCountThreshold](#rqsrs-015s3settingss3uploadpartsizemultiplypartscountthreshold)
  * 4.12 [Performance](#performance)
    * 4.12.1 [RQ.SRS-015.S3.Performance.PerformTTLMoveOnInsert](#rqsrs-015s3performanceperformttlmoveoninsert)
    * 4.12.2 [RQ.SRS-015.S3.Performance.Glob](#rqsrs-015s3performanceglob)
    * 4.12.3 [RQ.SRS-015.S3.Performance.AllowS3ZeroCopyReplication.Select](#rqsrs-015s3performanceallows3zerocopyreplicationselect)
    * 4.12.4 [RQ.SRS-015.S3.Performance.AllowS3ZeroCopyReplication.Insert](#rqsrs-015s3performanceallows3zerocopyreplicationinsert)
    * 4.12.5 [RQ.SRS-015.S3.Performance.AllowS3ZeroCopyReplication.Alter](#rqsrs-015s3performanceallows3zerocopyreplicationalter)
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
the query when the S3 resource is server-side encrypted.

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

#### RQ.SRS-015.S3.Alter
version: 1.0

[ClickHouse] SHALL support running `ALTER ...` queries on [S3] storage.
[ClickHouse] SHALL reproduce these queries across replicas without data loss.
[ClickHouse] SHALL support the above when configured with one or more of disk cache,
disk encryption and zero copy replication.

#### Backup

##### RQ.SRS-015.S3.Backup.MinIOBackup
version: 1.0

[ClickHouse] SHALL support manual backups of tables that use minio storage.

##### RQ.SRS-015.S3.Backup.AWSS3Backup
version: 1.0

[ClickHouse] SHALL support manual backups of tables that use aws s3 storage.

##### RQ.SRS-015.S3.Backup.GCSBackup
version: 1.0

[ClickHouse] SHALL support manual backups of tables that use gcs storage.

##### RQ.SRS-015.S3.Backup.AzureBackup
version: 1.0

[ClickHouse] SHALL support manual backups of tables that use azure storage.

##### RQ.SRS-015.S3.Backup.StoragePolicies
version: 1.0

[ClickHouse] SHALL support using creating manual backups of tables that use storage policies containing:

* one volume with s3 disk
* one volume with s3 and local disk
* multiple volumes with s3 and local disks

##### RQ.SRS-015.S3.Backup.AlterFreeze
version: 1.0

[ClickHouse] SHALL support using `ALTER TABLE FREEZE` on tables that use S3 in the storage policy. If the policy includes a local disk,
the query will create a local backup in the `shadow/` directory of the working ClickHouse directory (`/var/lib/clickhouse` by default).

##### RQ.SRS-015.S3.Backup.AlterDetach
version: 1.0

[ClickHouse] SHALL support using `ALTER TABLE DETACH PARTITION` on partitions of tables that use S3.

##### RQ.SRS-015.S3.Backup.AlterAttach
version: 1.0

[ClickHouse] SHALL support restoring backups of tables using `ALTER TABLE ATTACH PARTITION` from data inside
`/var/lib/clickhouse/data/database/table/detached/`.

##### RQ.SRS-015.S3.Backup.Cleanup
version: 1.0

[ClickHouse] SHALL clean up local and remote files related to backed up partitions after a table is dropped.

* Detached partitions SHALL be removed immediately
* Frozen partitions SHALL be removed immediately after SYSTEM UNFREEZE

#### Metadata

##### RQ.SRS-015.S3.Metadata
version: 1.0

[ClickHouse] SHALL store disk metadata of tables with S3 disk
if and only if they have `<send_metadata>` set to `true` in the disk config.
The disk metadata is stored in `/var/lib/clickhouse/disks/{disk name}/`.
The metadata is stored in the s3 bucket.

`<send_metadata>` was deprecated in ClickHouse 21 and will be removed in the future.
See <https://github.com/ClickHouse/ClickHouse/issues/30510>


##### RQ.SRS-015.S3.Metadata.Revisions
version: 1.0

[ClickHouse] SHALL keep a revision counter for each table and change the counter for
every insert, merge, or remove operation. The revision counter in stored in
`/var/lib/clickhouse/disks/s3/shadow/{backup number}/revision.txt`, where
the backup number indicated how many times `ALTER FREEZE` has been used on the table.

##### RQ.SRS-015.S3.Metadata.BadBackupNumber
version: 1.0

[ClickHouse] SHALL

#### Metadata Restore

##### RQ.SRS-0.5.S3.MetadataRestore.RestoreFile
version: 1.0

[ClickHouse] SHALL support restoring tables using a restore file
located in `/var/lib/clickhouse/disks/{disk name}/restore` and executing
`SYSTEM RESTART DISK` and reattaching the table.

##### RQ.SRS-0.5.S3.MetadataRestore.BadRestoreFile
version: 1.0

[ClickHouse] SHALL not support restoring tables using a restore file
located in `/var/lib/clickhouse/disks/{disk name}/restore` that contains
a wrong bucket, path, or revision value.

##### RQ.SRS-0.5.S3.MetadataRestore.HugeRestoreFile
version: 1.0

[ClickHouse] SHALL not support restoring tables using a restore file
located in `/var/lib/clickhouse/disks/{disk name}/restore` that contains
a large amount of not usable information.

##### RQ.SRS-015.S3.MetadataRestore.NoLocalMetadata
version: 1.0

[ClickHouse] SHALL support restoring a table from the restore file
located in `/var/lib/clickhouse/disks/{disk name}/restore` even
if the local metadata has been purged.

##### RQ.SRS-015.S3.MetadataRestore.BucketPath
version: 1.0

[ClickHouse] SHALL support restoring a table to a specific bucket and path by indicating them
in the restore file located in `/var/lib/clickhouse/disks/{disk name}/restore`
using the following syntax:

```
'source_path' = {path}
'source_bucket' = {bucket}
```

##### RQ.SRS-015.S3.MetadataRestore.RevisionRestore
version: 1.0

[ClickHouse] SHALL support restoring a table to a specific revision version.
The table shall restore to the original bucket and path if and only if it is the latest revision.
The revision can be indicated in the restore file located in `/var/lib/clickhouse/disks/{disk name}/restore`:

```
'revision' = {revision number}
```

##### RQ.SRS-015.S3.MetadataRestore.Mutations
version: 1.0

[ClickHouse] SHALL support restoring a table to a state before, during, or after a mutation.

##### RQ.SRS-015.S3.MetadataRestore.ParallelMutations
version: 1.0

[ClickHouse] SHALL support restoring a table correctly even when mutations
are being added in parallel with the restore process.

##### RQ.SRS-015.S3.MetadataRestore.Detached
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

#### RQ.SRS-015.S3.Azure
version: 1.0

[ClickHouse] SHALL support external disks using [Azure Blob Storage].

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

##### RQ.SRS-015.S3.AutomaticReconnects.Azure
version: 1.0

[ClickHouse] SHALL support automatically reconnecting to Azure if the network connection has been interrupted.

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

#### RQ.SRS-015.S3.Disk.DropSync
version: 1.0

[ClickHouse] SHALL immediately remove related files from S3 when a table is dropped with the SYNC keyword.

Usage:

```sql
DROP TABLE mytable SYNC
```

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

```sh
"DB::Exception: Metadata and cache path should be different"
```

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
version: 1.1

[ClickHouse] SHALL support operations on replicated tables (ALTER,
SELECT, INSERT, etc...). If a replicated table is modified,
the changes SHALL be synchronized without data loss on all existing
replicas, and in [S3] storage.

###### RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.Delete
version: 1.1

[ClickHouse] SHALL support dropping a replicated table with no changes to any
other replicas of the table.

###### RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.DeleteAll
version: 1.0

[ClickHouse] SHALL support deleting replicated tables from [S3] by dropping
all replicas of the table from each [ClickHouse] instance.

###### RQ.SRS-015.S3.Disk.MergeTree.AllowS3ZeroCopyReplication.DataPreservedAfterMutation
version: 1.0

[Clickhouse] SHALL distribute mutations to all replicas without data loss.

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

#### RQ.SRS-015.S3.TableFunction.Path.Glob
version: 1.0

[ClickHouse] SHALL support using glob patterns in file paths to import multiple files from [S3].

> Multiple path components can have globs. For being processed file must exist and match to the whole path pattern (not only suffix or prefix).
>
> * `*` — Substitutes any number of any characters except / including empty string.
> * `?` — Substitutes any single character.
> * `{some_string,another_string,yet_another_one}` — Substitutes any of strings 'some_string', 'another_string', 'yet_another_one'.
> * `{N..M}` — Substitutes any number in range from N to M including both borders.
> * `**` - Fetches all files inside the folder recursively.

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

```xml
'column1_name column1_type, column2_name column2_type, ...'
```

#### RQ.SRS-015.S3.TableFunction.MeasureFileSize
version: 1.0

[ClickHouse] SHALL report the accurate size of s3 objects through the `_size`
virtual column of the s3 table function.

Example:

```sql
SELECT count() AS files, sum(_size) as bytes
FROM s3('https://s3.us-west-2.amazonaws.com/mybucket/clickhouse/demo2/s3_disk/**', 'One')

┌─files─┬──────bytes─┐
│   122 │ 1638600424 │
└───────┴────────────┘
```

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

### Azure

#### RQ.SRS-015.S3.Azure.Disk.Configuration
version: 1.0

[ClickHouse] SHALL support configuration of [Azure Blob Storage] disks
with syntax similar to the following:

``` xml
<yandex>
  <storage_configuration>
    <disks>
      <azure_disk>
          <type>azure_blob_storage</type>
          <storage_account_url>http://myaccount.blob.core.windows.net</storage_account_url>
          <container_name>my-container</container_name>
          <account_name>*****</account_name>
          <account_key>*****</account_key>
      </azure_disk>
    </disks>
...
</yandex>
```

#### RQ.SRS-015.S3.Azure.AllowS3ZeroCopyReplication
version: 1.0

[ClickHouse] SHALL support importing and exporting data to/from [Azure Blob Storage]
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

#### RQ.SRS-015.S3.Performance.Glob
version: 1.0

[ClickHouse] SHALL handle glob patterns efficiently, in reasonable time and without memory errors.
Fetch time SHALL be proportional to the amount of data that is fetched,
regardless of the total number of items in the bucket.

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
[Azure Blob Storage]: https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction
""",
)
