# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.7.211105.1001849.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_025_ClickHouse_DiskLevelEncryption = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support disk level encryption.\n" "\n"),
    link=None,
    level=3,
    num="3.1.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Restart = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Restart",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support restarting server without any errors\n"
        "when disk which is used by server is encrypted.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.2",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_WideAndCompactFormat = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.WideAndCompactFormat",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [wide table parts](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/#mergetree-data-storage) and [compact table parts](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/#mergetree-data-storage) when using encrypted disks.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.3",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_ComparablePerformance = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.ComparablePerformance",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support similar performance for insertion and selection to and from tables that use encrypted as compared to unencrypted disks.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.4",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_ComparablePartSizes = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.ComparablePartSizes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL have similar table part sizes for tables that use encrypted disks as compared to unencrypted disks.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.5",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_EncryptedType = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.EncryptedType",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support new `encrypted` disk type that SHALL\n"
        "define an encrypted disk inside the `<clickhouse><storage_configuration><disks>` section\n"
        "of the `config.xml` file.\n"
        "\n"
        "For example,\n"
        "\n"
        "```xml\n"
        "<storage_configuration>\n"
        "    <disks>\n"
        "        <encrypted_disk_name>\n"
        "            <type>encrypted</type>\n"
        "            ...\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.6",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_OnTheFlyEncryption = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.OnTheFlyEncryption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL encrypt all data that is written to an encrypted disk on the fly.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.7",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_OnTheFlyDecryption = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.OnTheFlyDecryption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL decrypt data from an encrypted disk automatically.\n" "\n"
    ),
    link=None,
    level=3,
    num="3.1.8",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_FileEncryption = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.FileEncryption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL encrypt all the files related to a table\n"
        "when the table stores its data on an encrypted disk.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.1.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_FileEncryption_FileHeader = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.FileEncryption.FileHeader",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL add three bytes header containing ASCII `ENC` text\n"
        "at the beginning of each encrypted file that SHALL server\n"
        "as an encrypted file marker.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.2.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_FileEncryption_Metadata = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.FileEncryption.Metadata",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL encrypt all the metadata files related to a table\n"
        "that stores its data on an encrypted cloud storage disk.\n"
        "\n"
        "When metadata for the disk is cached locally for performance\n"
        "local files SHALL use the same encryption algorithm and keys as for the\n"
        "original encrypted disk.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.3.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_DistributedTables = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.DistributedTables",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using encrypted disks for distributed tables.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_ReplicatedTables = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.ReplicatedTables",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using encrypted disks for replicated tables even if\n"
        "nodes have different encryption and decryption keys or nodes have different disk types.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.4.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Sharded = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Sharded",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using encrypted disks for sharded tables even if\n"
        "nodes have different encryption and decryption keys or nodes have different disk types.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.5.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_ShardedAndReplicatedTables = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.ShardedAndReplicatedTables",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using encrypted disks for sharded and replicated tables even if\n"
        "nodes have different encryption and decryption keys or nodes have different disk types.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.6.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_MultiDiskVolumes = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.MultiDiskVolumes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support having encrypted disk in multi-disk volumes.\n"
        "\n"
        "```xml\n"
        "  <volumes>\n"
        "    <my_volume>\n"
        "          <disk>encrypted_local</disk>\n"
        "          <disk>local</disk>\n"
        "    </my_volume>\n"
        "  </volumes>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.7.1.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_MultiVolumePolicies = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.MultiVolumePolicies",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support having encrypted disk when policy contains multiple\n"
        "volumes which have one or more encrypted disks.\n"
        "\n"
        "```xml\n"
        "  <my_policy>\n"
        "    <volumes>\n"
        "      <my_volume_0>\n"
        "            <disk>encrypted_local</disk>\n"
        "            <disk>local</disk>\n"
        "      </my_volume_0>\n"
        "      <my_volume_1>\n"
        "            <disk>other_encrypted_local</disk>\n"
        "            <disk>other_local</disk>\n"
        "      </my_volume_1>\n"
        "    </volumes>\n"
        "  </my_policy>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.7.2.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_MergingWithDifferentKeys = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.MergingWithDifferentKeys",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL merge different parts regardless of what keys they are encrypted with.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.7.3.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_Alter_PartitionsAndParts = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.Alter.PartitionsAndParts",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support all operations with partitions and parts\n"
        "when encrypted disk is used for table storage such as\n"
        "\n"
        "* [DETACH PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_detach-partition) \n"
        "* [DROP PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_drop-partition) \n"
        "* [ATTACH PART|PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_attach-partition)\n"
        "* [ATTACH PARTITION FROM](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_attach-partition-from)\n"
        "* [REPLACE PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_replace-partition)\n"
        "* [MOVE PARTITION TO TABLE](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_move_to_table-partition)\n"
        "* [CLEAR COLUMN IN PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_clear-column-partition)\n"
        "* [CLEAR INDEX IN PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_clear-index-partition)\n"
        "* [FREEZE PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_freeze-partition)\n"
        "* [UNFREEZE PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_unfreeze-partition)\n"
        "* [FETCH PARTITION|PART](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_fetch-partition) \n"
        "* [MOVE PARTITION|PART]\n"
        "* [UPDATE IN PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#update-in-partition)\n"
        "* [DELETE IN PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#delete-in-partition)\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.7.4.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_Alter_MoveBetweenEncryptedAndNonEncryptedDisks = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.Alter.MoveBetweenEncryptedAndNonEncryptedDisks",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [MOVE PARTITION|PART] from encrypted to non-encrypted disk and vice versa.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.7.4.2",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_InsertAndSelect = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.InsertAndSelect",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support all read and write operations when encrypted disk is used for table storage such as\n"
        "\n"
        "* [INSERT]\n"
        "* [SELECT]\n"
        "\n"
        "For [INSERT] the following cases SHALL work:\n"
        "\n"
        "* one block insert that has rows that go all into the same partition\n"
        "* one block insert that has rows that go into multiple partitions\n"
        "* multiple block insert that has rows that go all into the same partition\n"
        "* multiple block insert that has rows that go into multiple partitions\n"
        "* multiple statements executed back to back\n"
        "* cuncurrent inserts\n"
        "\n"
        "For [SELECT] the following cases SHALL work:\n"
        "\n"
        "* query that reads data where all rows come from only one partition and one part\n"
        "* query that reads data where all rows come from only one partition and multiple parts\n"
        "* query that reads data from multiple partitions and multiple parts\n"
        "* query that reads all the data\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.7.5.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_Table = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.Table",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support all table operations when encrypted disk is used for table storage such as\n"
        "\n"
        "* [CREATE](https://clickhouse.com/docs/en/sql-reference/statements/create/)\n"
        "* [DROP](https://clickhouse.com/docs/en/sql-reference/statements/drop/)\n"
        "* [DETACH](https://clickhouse.com/docs/en/sql-reference/statements/detach/)\n"
        "* [CHECK](https://clickhouse.com/docs/en/sql-reference/statements/check-table/)\n"
        "* [ATTACH](https://clickhouse.com/docs/en/sql-reference/statements/attach/)\n"
        "* [OPTIMIZE](https://clickhouse.com/docs/en/sql-reference/statements/optimize/)\n"
        "* [RENAME](https://clickhouse.com/docs/en/sql-reference/statements/rename/)\n"
        "* [EXCHANGE](https://clickhouse.com/docs/en/sql-reference/statements/exchange/)\n"
        "* [TRUNCATE](https://clickhouse.com/docs/en/sql-reference/statements/truncate/)\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.7.6.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_TableTTL = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.TableTTL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [Table TTL](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/#mergetree-table-ttl) from and to encrypted disk.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.7.7.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_ColumnTTL = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.ColumnTTL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [Column TTL](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/#mergetree-column-ttl) when table is stored on the encrypted disk.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.7.8.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_TieredStorage = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.TieredStorage",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using encrypted disks and other disks together as parts of [Tiered Storage]\n"
        "even when disks have different encryption keys.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.7.9.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Compatability_View = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Compatability.View",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using views over tables that are stored\n"
        "on the encrypted disk. \n"
        "\n"
        "* [NORMAL](https://clickhouse.com/docs/en/sql-reference/statements/create/view/#normal)\n"
        "* [MATERIALIZED](https://clickhouse.com/docs/en/sql-reference/statements/create/view/#materialized)\n"
        "* [LIVE](https://clickhouse.com/docs/en/sql-reference/statements/create/view/#live-view)\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.7.10.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Disk_Local = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.Local",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support disk level encryption for any `local` type (`<type>local</type>`)\n"
        "disks specified in the `<clickhouse><storage_configuration><disks>` section of the `config.xml`\n"
        "configuration file.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.8.1.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Disk_S3 = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.S3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support disk level encryption for any `s3` type (`<type>s3</type>`)\n"
        "disks specified in the `<clickhouse><storage_configuration><disks>` section of the `config.xml`\n"
        "configuration file.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.8.2.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Disk_Memory = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.Memory",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support disk level encryption for any `memory` type (`<type>memory</type>`)\n"
        "disks specified in the `<clickhouse><storage_configuration><disks>` section of the `config.xml`\n"
        "configuration file.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.8.3.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Disk_Encrypted = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.Encrypted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support disk level encryption for any `encrypted` type (`<type>encrypted</type>`)\n"
        "disks specified in the `<clickhouse><storage_configuration><disks>` section of the `config.xml`\n"
        "configuration file.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.8.4.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Disk_HDFS = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.HDFS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support disk level encryption for any `hdfs` type (`<type>hdfs</type>`)\n"
        "disks specified in the `<clickhouse><storage_configuration><disks>` section of the `config.xml`\n"
        "configuration file.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.8.5.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_Default = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.Default",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL use `AES_128_CTR` as the default algorithm for disk level encryption.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.9.1.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_AES_128_CTR = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.AES_128_CTR",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `AES_128_CTR` algorithm for disk level encryption.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.9.2.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_AES_192_CTR = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.AES_192_CTR",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `AES_192_CTR` algorithm for disk level encryption.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.9.3.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_AES_256_CTR = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.AES_256_CTR",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `AES_256_CTR` algorithm for disk level encryption.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.9.4.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_Conflict = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.Conflict",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if encryption algorithm is changed,\n"
        "but there are parts already encrypted with a previous algorithm.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.9.5.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Encryption = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Encryption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying key to be used for data encryption\n"
        "and uniquely identify the key used for encryption when multiple keys\n"
        "are defined for the disk.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.10.1.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_PartsWithDifferentKeys = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.PartsWithDifferentKeys",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support parts encrypted with different keys when using encrypted disk.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.10.1.2",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Decryption = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Decryption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying one or more keys to be used for data decryption.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.10.2.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Missing = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Missing",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if any key that was used to encrypt the disk is missing.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.10.2.2",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Format_ASCII = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Format.ASCII",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying encryption and decryption keys as an ASCII string \n"
        "that will be converted into an array of `UInt64`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.10.3.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Format_SpecialXMLSymbols = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Format.SpecialXMLSymbols",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying encryption and decryption keys that \n"
        "contain one or more special XML symbols that require escaping that will be \n"
        "converted into an array of `UInt64`.\n"
        "\n"
        "* `<` (less-than) `&#60;` or `&lt;`\n"
        "* `>` (greater-than) `&#62;` or  `&gt;`\n"
        "* `&` (ampersand) `&#38;`\n"
        "* `'` (apostrophe or single quote) `&#39;`\n"
        '* `"` (double-quote) `&#34;`\n'
        "\n"
    ),
    link=None,
    level=4,
    num="3.10.3.2",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Format_UTF8 = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Format.UTF8",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying encryption and decryption keys as a UTF-8 string\n"
        "that will be converted into an array of `UInt64`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.10.3.3",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Format_Hex = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Format.Hex",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying encryption and decryption keys as hexadecimal number.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.10.3.4",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Invalid_Size = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Invalid.Size",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if the the encryption key has the wrong size (either too long or too short)\n"
        "for the algorithm. The following sizes SHALL be enforced\n"
        "\n"
        "* for AES_128_CTR key size SHALL be equal to 16 bytes\n"
        "* for AES_192_CTR key size SHALL be equal to 24 bytes\n"
        "* for AES_256_CTR key size SHALL be equal to 32 bytes\n"
        "\n"
        "If the size of the key is invalid then the server SHALL not start and write and error message into\n"
        "its error log.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.10.4.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_AccessPermission_WideOrInvalid = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.AccessPermission.WideOrInvalid",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if the configuration file \n"
        "which contains encryption keys has invalid or wide access permissions.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.1.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_ApplicationOfChanges = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.ApplicationOfChanges",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL only apply changes to the encrypted disk definition in the `config.xml` without server restart. \n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.2.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Path = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `<path>` parameter\n"
        "inside the `<clickhouse><storage_configuration><disks><disk_name>` section\n"
        "of the `config.xml` file that SHALL specify the path\n"
        "where the encrypted data SHALL be stored on the disk\n"
        "referred by the `<disk>` parameter.\n"
        "\n"
        "For example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <storage_configuration>\n"
        "        <disks>\n"
        "            <encrypted_disk_name>\n"
        "                <path>path_name<path>\n"
        "                <disk>disk_name</disk>\n"
        "                ...\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.3.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Path_Default = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path.Default",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL save data to the root of the disk specified by the `<disk>` parameter\n"
        "if the `<path>` parameter is not specified or empty.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.3.2",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Path_Invalid = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path.Invalid",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if the path specified in the `<path>` parameter is invalid.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.3.3",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Path_NoAccessRights = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path.NoAccessRights",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if user has no rights to read or write to the path\n"
        "specified in the `<path>` parameter.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.3.4",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Path_NewDirectories = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path.NewDirectories",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL create new directories if the path specified by `path` parameter not exist.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.3.5",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Disk = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Disk",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `<disk>` parameter\n"
        "inside the `<clickhouse><storage_configuration><disks><disk_name>` section\n"
        "of the `config.xml` file that SHALL specify the disk\n"
        "where the encrypted data SHALL be stored. The specified disk\n"
        "SHALL refer to one of the previously defined disks inside the \n"
        "`<clickhouse><storage_configuration><disks>` section.\n"
        "\n"
        "For example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <storage_configuration>\n"
        "        <disks>\n"
        "            <disk_name>\n"
        "                ...\n"
        "            </disk_name>\n"
        "            <encrypted_disk_name>\n"
        "                <disk>disk_name</disk>\n"
        "                    ...\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.4.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Disk_Invalid = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Disk.Invalid",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if the disk specified in the `<disk>` parameter is either:\n"
        "\n"
        "* does not exist\n"
        "* the value is empty\n"
        "* the `<disk>` parameter itself is missing\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.4.2",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `<key>` parameter in the \n"
        "`<clickhouse><storage_configuration><disks><disk_name>` section of the `config.xml` file\n"
        "that SHALL specify a key that SHALL be used for encryption or decryption of\n"
        "data stored on the disk. \n"
        "\n"
        "For example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <storage_configuration>\n"
        "        <disks>\n"
        "            ...\n"
        "            <disk_local_encrypted>\n"
        "                <type>encrypted</type>\n"
        "                <disk>disk_local</disk>\n"
        "                <path>encrypted/</path>\n"
        "                <key>abcdefghijklmnop</key>\n"
        "            </disk_local_encrypted>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.5.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Hex = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Hex",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `<key_hex>` parameter in the \n"
        "`<clickhouse><storage_configuration><disks><disk_name>` section of the `config.xml` file\n"
        "that SHALL specify a key in the hexadecimal format that SHALL be used for encryption or decryption of\n"
        "data stored on the disk. \n"
        "\n"
        "For example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <storage_configuration>\n"
        "        <disks>\n"
        "            ...\n"
        "            <disk_local_encrypted>\n"
        "                <type>encrypted</type>\n"
        "                <disk>disk_local</disk>\n"
        "                <path>encrypted/</path>\n"
        "                <key_hex>efadfdfdfdfdfdfaefadfdfdfdfdfdfa</key_hex>\n"
        "            </disk_local_encrypted>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.5.2",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_HexKeyConflict = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.HexKeyConflict",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error when both `<key_hex>` and `<key>` parameters are defined\n"
        "without `id`.\n"
        "\n"
        "For example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <storage_configuration>\n"
        "        <disks>\n"
        "            ...\n"
        "            <disk_encrypted>\n"
        "                ...\n"
        "                <key_hex>efadfdfdfdfdfdfaefadfdfdfdfdfdfa</key_hex>\n"
        "                <key>firstfistfirstfirst<key>\n"
        "                ...  \n"
        "            </disk_encrypted>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.5.3",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `<key id="key_id">` parameter\n'
        "when more than one key is specified in the `<clickhouse><storage_configuration><disks><disk_name>`\n"
        "section of the `config.xml` file where `id` value SHALL uniquely\n"
        "identify each unique key.\n"
        "\n"
        "For example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <storage_configuration>\n"
        "        <disks>\n"
        "            ...\n"
        "            <disk_encrypted> \n"
        '                <key id="0">firstfirstfirstf</key>\n'
        '                <key id="1">secondsecondseco</key>\n'
        "                ...\n"
        "            </disk_encrypted>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.5.4",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_HexKeyIdConflict = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.HexKeyIdConflict",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error when both `<key_hex>` and `<key>` parameters are defined\n"
        "with the same `id`.\n"
        "\n"
        "For example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <storage_configuration>\n"
        "        <disks>\n"
        "            ...\n"
        "            <disk_encrypted>\n"
        "                ...\n"
        '                <key_hex id="0">efadfdfdfdfdfdfaefadfdfdfdfdfdfa</key_hex>\n'
        '                <key id="0">firstfistfirstfirst<key>\n'
        "                ...  \n"
        "            </disk_encrypted>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.5.5",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_MixedFormats = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.MixedFormats",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `id` parameter, when keys are defined in \n"
        "both hexadecimal and string formats for the same disk.\n"
        "\n"
        "For example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <storage_configuration>\n"
        "        <disks>\n"
        "            ...\n"
        "            <disk_encrypted>\n"
        "                ...\n"
        '                <key_hex id="0">efadfdfdfdfdfdfaefadfdfdfdfdfdfa</key_hex>\n'
        '                <key id="1">firstfistfirstfirst<key>\n'
        "                ...  \n"
        "            </disk_encrypted>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.5.6",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_Id_Invalid = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.Id.Invalid",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if `id` of the key is not a positive integer\n"
        "or a key with the same `id` is already defined.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.5.7",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_CurrentKeyId = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.CurrentKeyId",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `<current_key_id>` parameter in the `<clickhouse><storage_configuration><disks><disk_name>`\n"
        "section of the `config.xml` file that SHALL specify\n"
        "a key that SHALL be used for data encryption when multiple keys\n"
        "are present and are indentified by a unique `id`.\n"
        "\n"
        "For example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <storage_configuration>\n"
        "        <disks>\n"
        "            <disk_encrypted>\n"
        "                ...\n"
        '                <key id="0">firstfirstfirstf</key>\n'
        '                <key id="1">secondsecondseco</key>\n'
        "                <current_key_id>1</current_key_id>\n"
        "            <disk_encrypted>\n"
        "```\n"
        "\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.6.1",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_CurrentKeyId_Invalid = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.CurrentKeyId.Invalid",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if the value of the `<current_key_id>` is either:\n"
        "\n"
        "* does not refer to previously defined key\n"
        "* is empty\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.11.6.2",
)

RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_CurrentKeyId_Default = Requirement(
    name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.CurrentKeyId.Default",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL use `0` as the default `<current_key_id>` parameter \n"
        "when more than one key is defined for disk level encryption.\n"
        "\n"
        "\n"
        "[MOVE PARTITION|PART]: https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_move-partition\n"
        "[Tiered Storage]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/#table_engine-mergetree-multiple-volumes\n"
        "[INSERT]: https://clickhouse.com/docs/en/sql-reference/statements/insert-into/\n"
        "[SELECT]: https://clickhouse.com/docs/en/sql-reference/statements/select/\n"
        "[SRS]: #srs\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "[Gitlab repository]: https://gitlab.com/altinity-qa/documents/qa-srs025-clickhouse-disk-level-encryption/blob/main/QA_SRS025_ClickHouse_Disk_Level_Encryption.md\n"
        "[Revision history]: https://gitlab.com/altinity-qa/documents/qa-srs025-clickhouse-disk-level-encryption/commits/main/QA_SRS025_ClickHouse_Disk_Level_Encryption.md\n"
        "[Git]: https://git-scm.com/\n"
        "[GitLab]: https://gitlab.com\n"
    ),
    link=None,
    level=4,
    num="3.11.6.3",
)

QA_SRS025_ClickHouse_Disk_Level_Encryption = Specification(
    name="QA-SRS025 ClickHouse Disk Level Encryption",
    description=None,
    author="antipov",
    date="August 10, 2021",
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
        Heading(name="Requirements", level=1, num="3"),
        Heading(name="General", level=2, num="3.1"),
        Heading(name="RQ.SRS-025.ClickHouse.DiskLevelEncryption", level=3, num="3.1.1"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Restart",
            level=3,
            num="3.1.2",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.WideAndCompactFormat",
            level=3,
            num="3.1.3",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.ComparablePerformance",
            level=3,
            num="3.1.4",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.ComparablePartSizes",
            level=3,
            num="3.1.5",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.EncryptedType",
            level=3,
            num="3.1.6",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.OnTheFlyEncryption",
            level=3,
            num="3.1.7",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.OnTheFlyDecryption",
            level=3,
            num="3.1.8",
        ),
        Heading(name="File Encryption", level=2, num="3.2"),
        Heading(name="Table Files", level=3, num="3.2.1"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.FileEncryption",
            level=4,
            num="3.2.1.1",
        ),
        Heading(name="Encrypted Files Header", level=3, num="3.2.2"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.FileEncryption.FileHeader",
            level=4,
            num="3.2.2.1",
        ),
        Heading(name="Cached Table Metadata", level=3, num="3.2.3"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.FileEncryption.Metadata",
            level=4,
            num="3.2.3.1",
        ),
        Heading(name="Distributed Tables", level=2, num="3.3"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.DistributedTables",
            level=3,
            num="3.3.1",
        ),
        Heading(name="Replicated Tables", level=2, num="3.4"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.ReplicatedTables",
            level=3,
            num="3.4.1",
        ),
        Heading(name="Sharded Tables", level=2, num="3.5"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Sharded",
            level=3,
            num="3.5.1",
        ),
        Heading(name="Sharded And Replicated Tables", level=2, num="3.6"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.ShardedAndReplicatedTables",
            level=3,
            num="3.6.1",
        ),
        Heading(name="Operations", level=2, num="3.7"),
        Heading(name="Multi-Disk Volumes", level=3, num="3.7.1"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.MultiDiskVolumes",
            level=4,
            num="3.7.1.1",
        ),
        Heading(name="Multi-Volume Policies", level=3, num="3.7.2"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.MultiVolumePolicies",
            level=4,
            num="3.7.2.1",
        ),
        Heading(name="Merging Parts", level=3, num="3.7.3"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.MergingWithDifferentKeys",
            level=4,
            num="3.7.3.1",
        ),
        Heading(name="Partitions And Parts", level=3, num="3.7.4"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.Alter.PartitionsAndParts",
            level=4,
            num="3.7.4.1",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.Alter.MoveBetweenEncryptedAndNonEncryptedDisks",
            level=4,
            num="3.7.4.2",
        ),
        Heading(name="Insert And Select", level=3, num="3.7.5"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.InsertAndSelect",
            level=4,
            num="3.7.5.1",
        ),
        Heading(name="Table Operations", level=3, num="3.7.6"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.Table",
            level=4,
            num="3.7.6.1",
        ),
        Heading(name="Table TTL", level=3, num="3.7.7"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.TableTTL",
            level=4,
            num="3.7.7.1",
        ),
        Heading(name="Column TTL", level=3, num="3.7.8"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.ColumnTTL",
            level=4,
            num="3.7.8.1",
        ),
        Heading(name="Tiered Storage", level=3, num="3.7.9"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.TieredStorage",
            level=4,
            num="3.7.9.1",
        ),
        Heading(name="Table Views", level=3, num="3.7.10"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Compatability.View",
            level=4,
            num="3.7.10.1",
        ),
        Heading(name="Disk Types", level=2, num="3.8"),
        Heading(name="Local", level=3, num="3.8.1"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.Local",
            level=4,
            num="3.8.1.1",
        ),
        Heading(name="S3", level=3, num="3.8.2"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.S3",
            level=4,
            num="3.8.2.1",
        ),
        Heading(name="Memory", level=3, num="3.8.3"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.Memory",
            level=4,
            num="3.8.3.1",
        ),
        Heading(name="Encrypted", level=3, num="3.8.4"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.Encrypted",
            level=4,
            num="3.8.4.1",
        ),
        Heading(name="HDFS", level=3, num="3.8.5"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.HDFS",
            level=4,
            num="3.8.5.1",
        ),
        Heading(name="Encryption Algorithms", level=2, num="3.9"),
        Heading(name="Default Algorithm", level=3, num="3.9.1"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.Default",
            level=4,
            num="3.9.1.1",
        ),
        Heading(name="AES_128_CTR", level=3, num="3.9.2"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.AES_128_CTR",
            level=4,
            num="3.9.2.1",
        ),
        Heading(name="AES_192_CTR", level=3, num="3.9.3"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.AES_192_CTR",
            level=4,
            num="3.9.3.1",
        ),
        Heading(name="AES_256_CTR", level=3, num="3.9.4"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.AES_256_CTR",
            level=4,
            num="3.9.4.1",
        ),
        Heading(name="Mixed Algorithms", level=3, num="3.9.5"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.Conflict",
            level=4,
            num="3.9.5.1",
        ),
        Heading(name="Encryption Keys", level=2, num="3.10"),
        Heading(name="Encryption Key", level=3, num="3.10.1"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Encryption",
            level=4,
            num="3.10.1.1",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.PartsWithDifferentKeys",
            level=4,
            num="3.10.1.2",
        ),
        Heading(name="Decryption Key", level=3, num="3.10.2"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Decryption",
            level=4,
            num="3.10.2.1",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Missing",
            level=4,
            num="3.10.2.2",
        ),
        Heading(name="Key Formats", level=3, num="3.10.3"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Format.ASCII",
            level=4,
            num="3.10.3.1",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Format.SpecialXMLSymbols",
            level=4,
            num="3.10.3.2",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Format.UTF8",
            level=4,
            num="3.10.3.3",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Format.Hex",
            level=4,
            num="3.10.3.4",
        ),
        Heading(name="Invalid Size Key", level=3, num="3.10.4"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Invalid.Size",
            level=4,
            num="3.10.4.1",
        ),
        Heading(name="Config", level=2, num="3.11"),
        Heading(name="Access permission", level=3, num="3.11.1"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.AccessPermission.WideOrInvalid",
            level=4,
            num="3.11.1.1",
        ),
        Heading(name="Application of Changes", level=3, num="3.11.2"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.ApplicationOfChanges",
            level=4,
            num="3.11.2.1",
        ),
        Heading(name="Path", level=3, num="3.11.3"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path",
            level=4,
            num="3.11.3.1",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path.Default",
            level=4,
            num="3.11.3.2",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path.Invalid",
            level=4,
            num="3.11.3.3",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path.NoAccessRights",
            level=4,
            num="3.11.3.4",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path.NewDirectories",
            level=4,
            num="3.11.3.5",
        ),
        Heading(name="Disk", level=3, num="3.11.4"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Disk",
            level=4,
            num="3.11.4.1",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Disk.Invalid",
            level=4,
            num="3.11.4.2",
        ),
        Heading(name="Keys Configuration", level=3, num="3.11.5"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key",
            level=4,
            num="3.11.5.1",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Hex",
            level=4,
            num="3.11.5.2",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.HexKeyConflict",
            level=4,
            num="3.11.5.3",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple",
            level=4,
            num="3.11.5.4",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.HexKeyIdConflict",
            level=4,
            num="3.11.5.5",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.MixedFormats",
            level=4,
            num="3.11.5.6",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.Id.Invalid",
            level=4,
            num="3.11.5.7",
        ),
        Heading(name="Current Key Id", level=3, num="3.11.6"),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.CurrentKeyId",
            level=4,
            num="3.11.6.1",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.CurrentKeyId.Invalid",
            level=4,
            num="3.11.6.2",
        ),
        Heading(
            name="RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.CurrentKeyId.Default",
            level=4,
            num="3.11.6.3",
        ),
    ),
    requirements=(
        RQ_SRS_025_ClickHouse_DiskLevelEncryption,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Restart,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_WideAndCompactFormat,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_ComparablePerformance,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_ComparablePartSizes,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_EncryptedType,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_OnTheFlyEncryption,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_OnTheFlyDecryption,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_FileEncryption,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_FileEncryption_FileHeader,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_FileEncryption_Metadata,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_DistributedTables,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_ReplicatedTables,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Sharded,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_ShardedAndReplicatedTables,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_MultiDiskVolumes,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_MultiVolumePolicies,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_MergingWithDifferentKeys,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_Alter_PartitionsAndParts,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_Alter_MoveBetweenEncryptedAndNonEncryptedDisks,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_InsertAndSelect,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_Table,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_TableTTL,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_ColumnTTL,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_TieredStorage,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Compatability_View,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Disk_Local,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Disk_S3,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Disk_Memory,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Disk_Encrypted,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Disk_HDFS,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_Default,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_AES_128_CTR,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_AES_192_CTR,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_AES_256_CTR,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_Conflict,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Encryption,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_PartsWithDifferentKeys,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Decryption,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Missing,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Format_ASCII,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Format_SpecialXMLSymbols,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Format_UTF8,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Format_Hex,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Invalid_Size,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_AccessPermission_WideOrInvalid,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_ApplicationOfChanges,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Path,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Path_Default,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Path_Invalid,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Path_NoAccessRights,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Path_NewDirectories,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Disk,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Disk_Invalid,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Hex,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_HexKeyConflict,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_HexKeyIdConflict,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_MixedFormats,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_Id_Invalid,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_CurrentKeyId,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_CurrentKeyId_Invalid,
        RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_CurrentKeyId_Default,
    ),
    content="""
# QA-SRS025 ClickHouse Disk Level Encryption
# Software Requirements Specification

(c) 2021 Altinity LTD. All Rights Reserved.

**Document status:** Confidential

**Author:** antipov

**Date:** August 10, 2021

## Approval

**Status:** -

**Version:** -

**Approved by:** -

**Date:** -

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Requirements](#requirements)
  * 3.1 [General](#general)
    * 3.1.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption](#rqsrs-025clickhousedisklevelencryption)
    * 3.1.2 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Restart](#rqsrs-025clickhousedisklevelencryptionrestart)
    * 3.1.3 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.WideAndCompactFormat](#rqsrs-025clickhousedisklevelencryptionwideandcompactformat)
    * 3.1.4 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.ComparablePerformance](#rqsrs-025clickhousedisklevelencryptioncomparableperformance)
    * 3.1.5 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.ComparablePartSizes](#rqsrs-025clickhousedisklevelencryptioncomparablepartsizes)
    * 3.1.6 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.EncryptedType](#rqsrs-025clickhousedisklevelencryptionencryptedtype)
    * 3.1.7 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.OnTheFlyEncryption](#rqsrs-025clickhousedisklevelencryptionontheflyencryption)
    * 3.1.8 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.OnTheFlyDecryption](#rqsrs-025clickhousedisklevelencryptionontheflydecryption)
  * 3.2 [File Encryption](#file-encryption)
    * 3.2.1 [Table Files](#table-files)
      * 3.2.1.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.FileEncryption](#rqsrs-025clickhousedisklevelencryptionfileencryption)
    * 3.2.2 [Encrypted Files Header](#encrypted-files-header)
      * 3.2.2.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.FileEncryption.FileHeader](#rqsrs-025clickhousedisklevelencryptionfileencryptionfileheader)
    * 3.2.3 [Cached Table Metadata](#cached-table-metadata)
      * 3.2.3.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.FileEncryption.Metadata](#rqsrs-025clickhousedisklevelencryptionfileencryptionmetadata)
  * 3.3 [Distributed Tables](#distributed-tables)
    * 3.3.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.DistributedTables](#rqsrs-025clickhousedisklevelencryptiondistributedtables)
  * 3.4 [Replicated Tables](#replicated-tables)
    * 3.4.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.ReplicatedTables](#rqsrs-025clickhousedisklevelencryptionreplicatedtables)
  * 3.5 [Sharded Tables](#sharded-tables)
    * 3.5.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Sharded](#rqsrs-025clickhousedisklevelencryptionsharded)
  * 3.6 [Sharded And Replicated Tables](#sharded-and-replicated-tables)
    * 3.6.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.ShardedAndReplicatedTables](#rqsrs-025clickhousedisklevelencryptionshardedandreplicatedtables)
  * 3.7 [Operations](#operations)
    * 3.7.1 [Multi-Disk Volumes](#multi-disk-volumes)
      * 3.7.1.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.MultiDiskVolumes](#rqsrs-025clickhousedisklevelencryptionoperationsmultidiskvolumes)
    * 3.7.2 [Multi-Volume Policies](#multi-volume-policies)
      * 3.7.2.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.MultiVolumePolicies](#rqsrs-025clickhousedisklevelencryptionoperationsmultivolumepolicies)
    * 3.7.3 [Merging Parts](#merging-parts)
      * 3.7.3.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.MergingWithDifferentKeys](#rqsrs-025clickhousedisklevelencryptionoperationsmergingwithdifferentkeys)
    * 3.7.4 [Partitions And Parts](#partitions-and-parts)
      * 3.7.4.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.Alter.PartitionsAndParts](#rqsrs-025clickhousedisklevelencryptionoperationsalterpartitionsandparts)
      * 3.7.4.2 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.Alter.MoveBetweenEncryptedAndNonEncryptedDisks](#rqsrs-025clickhousedisklevelencryptionoperationsaltermovebetweenencryptedandnonencrypteddisks)
    * 3.7.5 [Insert And Select](#insert-and-select)
      * 3.7.5.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.InsertAndSelect](#rqsrs-025clickhousedisklevelencryptionoperationsinsertandselect)
    * 3.7.6 [Table Operations](#table-operations)
      * 3.7.6.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.Table](#rqsrs-025clickhousedisklevelencryptionoperationstable)
    * 3.7.7 [Table TTL](#table-ttl)
      * 3.7.7.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.TableTTL](#rqsrs-025clickhousedisklevelencryptionoperationstablettl)
    * 3.7.8 [Column TTL](#column-ttl)
      * 3.7.8.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.ColumnTTL](#rqsrs-025clickhousedisklevelencryptionoperationscolumnttl)
    * 3.7.9 [Tiered Storage](#tiered-storage)
      * 3.7.9.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.TieredStorage](#rqsrs-025clickhousedisklevelencryptionoperationstieredstorage)
    * 3.7.10 [Table Views](#table-views)
      * 3.7.10.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Compatability.View](#rqsrs-025clickhousedisklevelencryptioncompatabilityview)
  * 3.8 [Disk Types](#disk-types)
    * 3.8.1 [Local](#local)
      * 3.8.1.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.Local](#rqsrs-025clickhousedisklevelencryptiondisklocal)
    * 3.8.2 [S3](#s3)
      * 3.8.2.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.S3](#rqsrs-025clickhousedisklevelencryptiondisks3)
    * 3.8.3 [Memory](#memory)
      * 3.8.3.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.Memory](#rqsrs-025clickhousedisklevelencryptiondiskmemory)
    * 3.8.4 [Encrypted](#encrypted)
      * 3.8.4.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.Encrypted](#rqsrs-025clickhousedisklevelencryptiondiskencrypted)
    * 3.8.5 [HDFS](#hdfs)
      * 3.8.5.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.HDFS](#rqsrs-025clickhousedisklevelencryptiondiskhdfs)
  * 3.9 [Encryption Algorithms](#encryption-algorithms)
    * 3.9.1 [Default Algorithm](#default-algorithm)
      * 3.9.1.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.Default](#rqsrs-025clickhousedisklevelencryptionalgorithmdefault)
    * 3.9.2 [AES_128_CTR](#aes_128_ctr)
      * 3.9.2.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.AES_128_CTR](#rqsrs-025clickhousedisklevelencryptionalgorithmaes_128_ctr)
    * 3.9.3 [AES_192_CTR](#aes_192_ctr)
      * 3.9.3.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.AES_192_CTR](#rqsrs-025clickhousedisklevelencryptionalgorithmaes_192_ctr)
    * 3.9.4 [AES_256_CTR](#aes_256_ctr)
      * 3.9.4.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.AES_256_CTR](#rqsrs-025clickhousedisklevelencryptionalgorithmaes_256_ctr)
    * 3.9.5 [Mixed Algorithms](#mixed-algorithms)
      * 3.9.5.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.Conflict](#rqsrs-025clickhousedisklevelencryptionalgorithmconflict)
  * 3.10 [Encryption Keys](#encryption-keys)
    * 3.10.1 [Encryption Key](#encryption-key)
      * 3.10.1.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Encryption](#rqsrs-025clickhousedisklevelencryptionkeyencryption)
      * 3.10.1.2 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.PartsWithDifferentKeys](#rqsrs-025clickhousedisklevelencryptionkeypartswithdifferentkeys)
    * 3.10.2 [Decryption Key](#decryption-key)
      * 3.10.2.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Decryption](#rqsrs-025clickhousedisklevelencryptionkeydecryption)
      * 3.10.2.2 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Missing](#rqsrs-025clickhousedisklevelencryptionkeymissing)
    * 3.10.3 [Key Formats](#key-formats)
      * 3.10.3.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Format.ASCII](#rqsrs-025clickhousedisklevelencryptionkeyformatascii)
      * 3.10.3.2 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Format.SpecialXMLSymbols](#rqsrs-025clickhousedisklevelencryptionkeyformatspecialxmlsymbols)
      * 3.10.3.3 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Format.UTF8](#rqsrs-025clickhousedisklevelencryptionkeyformatutf8)
      * 3.10.3.4 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Format.Hex](#rqsrs-025clickhousedisklevelencryptionkeyformathex)
    * 3.10.4 [Invalid Size Key](#invalid-size-key)
      * 3.10.4.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Invalid.Size](#rqsrs-025clickhousedisklevelencryptionkeyinvalidsize)
  * 3.11 [Config](#config)
    * 3.11.1 [Access permission](#access-permission)
      * 3.11.1.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.AccessPermission.WideOrInvalid](#rqsrs-025clickhousedisklevelencryptionconfigaccesspermissionwideorinvalid)
    * 3.11.2 [Application of Changes](#application-of-changes)
      * 3.11.2.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.ApplicationOfChanges](#rqsrs-025clickhousedisklevelencryptionconfigapplicationofchanges)
    * 3.11.3 [Path](#path)
      * 3.11.3.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path](#rqsrs-025clickhousedisklevelencryptionconfigpath)
      * 3.11.3.2 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path.Default](#rqsrs-025clickhousedisklevelencryptionconfigpathdefault)
      * 3.11.3.3 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path.Invalid](#rqsrs-025clickhousedisklevelencryptionconfigpathinvalid)
      * 3.11.3.4 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path.NoAccessRights](#rqsrs-025clickhousedisklevelencryptionconfigpathnoaccessrights)
      * 3.11.3.5 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path.NewDirectories](#rqsrs-025clickhousedisklevelencryptionconfigpathnewdirectories)
    * 3.11.4 [Disk](#disk)
      * 3.11.4.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Disk](#rqsrs-025clickhousedisklevelencryptionconfigdisk)
      * 3.11.4.2 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Disk.Invalid](#rqsrs-025clickhousedisklevelencryptionconfigdiskinvalid)
    * 3.11.5 [Keys Configuration](#keys-configuration)
      * 3.11.5.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key](#rqsrs-025clickhousedisklevelencryptionconfigkey)
      * 3.11.5.2 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Hex](#rqsrs-025clickhousedisklevelencryptionconfigkeyhex)
      * 3.11.5.3 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.HexKeyConflict](#rqsrs-025clickhousedisklevelencryptionconfigkeyhexkeyconflict)
      * 3.11.5.4 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple](#rqsrs-025clickhousedisklevelencryptionconfigkeymultiple)
      * 3.11.5.5 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.HexKeyIdConflict](#rqsrs-025clickhousedisklevelencryptionconfigkeymultiplehexkeyidconflict)
      * 3.11.5.6 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.MixedFormats](#rqsrs-025clickhousedisklevelencryptionconfigkeymultiplemixedformats)
      * 3.11.5.7 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.Id.Invalid](#rqsrs-025clickhousedisklevelencryptionconfigkeymultipleidinvalid)
    * 3.11.6 [Current Key Id](#current-key-id)
      * 3.11.6.1 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.CurrentKeyId](#rqsrs-025clickhousedisklevelencryptionconfigkeymultiplecurrentkeyid)
      * 3.11.6.2 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.CurrentKeyId.Invalid](#rqsrs-025clickhousedisklevelencryptionconfigkeymultiplecurrentkeyidinvalid)
      * 3.11.6.3 [RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.CurrentKeyId.Default](#rqsrs-025clickhousedisklevelencryptionconfigkeymultiplecurrentkeyiddefault)


## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitLab Repository]. All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements related to [ClickHouse] 
disk level encryption feature.

## Requirements

### General

#### RQ.SRS-025.ClickHouse.DiskLevelEncryption
version: 1.0

[ClickHouse] SHALL support disk level encryption.

#### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Restart
version: 1.0

[ClickHouse] SHALL support restarting server without any errors
when disk which is used by server is encrypted.

#### RQ.SRS-025.ClickHouse.DiskLevelEncryption.WideAndCompactFormat
version: 1.0

[ClickHouse] SHALL support [wide table parts](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/#mergetree-data-storage) and [compact table parts](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/#mergetree-data-storage) when using encrypted disks.

#### RQ.SRS-025.ClickHouse.DiskLevelEncryption.ComparablePerformance
version: 1.0

[ClickHouse] SHALL support similar performance for insertion and selection to and from tables that use encrypted as compared to unencrypted disks.

#### RQ.SRS-025.ClickHouse.DiskLevelEncryption.ComparablePartSizes
version: 1.0

[ClickHouse] SHALL have similar table part sizes for tables that use encrypted disks as compared to unencrypted disks.

#### RQ.SRS-025.ClickHouse.DiskLevelEncryption.EncryptedType
version: 1.0

[ClickHouse] SHALL support new `encrypted` disk type that SHALL
define an encrypted disk inside the `<clickhouse><storage_configuration><disks>` section
of the `config.xml` file.

For example,

```xml
<storage_configuration>
    <disks>
        <encrypted_disk_name>
            <type>encrypted</type>
            ...
```

#### RQ.SRS-025.ClickHouse.DiskLevelEncryption.OnTheFlyEncryption
version: 1.0

[ClickHouse] SHALL encrypt all data that is written to an encrypted disk on the fly.

#### RQ.SRS-025.ClickHouse.DiskLevelEncryption.OnTheFlyDecryption
version: 1.0

[ClickHouse] SHALL decrypt data from an encrypted disk automatically.

### File Encryption

#### Table Files

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.FileEncryption
version: 1.0

[ClickHouse] SHALL encrypt all the files related to a table
when the table stores its data on an encrypted disk.

#### Encrypted Files Header

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.FileEncryption.FileHeader
version: 1.0

[ClickHouse] SHALL add three bytes header containing ASCII `ENC` text
at the beginning of each encrypted file that SHALL server
as an encrypted file marker.

#### Cached Table Metadata

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.FileEncryption.Metadata
version: 1.0

[ClickHouse] SHALL encrypt all the metadata files related to a table
that stores its data on an encrypted cloud storage disk.

When metadata for the disk is cached locally for performance
local files SHALL use the same encryption algorithm and keys as for the
original encrypted disk.

### Distributed Tables

#### RQ.SRS-025.ClickHouse.DiskLevelEncryption.DistributedTables
version: 1.0

[ClickHouse] SHALL support using encrypted disks for distributed tables.

### Replicated Tables

#### RQ.SRS-025.ClickHouse.DiskLevelEncryption.ReplicatedTables
version: 1.0

[ClickHouse] SHALL support using encrypted disks for replicated tables even if
nodes have different encryption and decryption keys or nodes have different disk types.

### Sharded Tables

#### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Sharded
version: 1.0

[ClickHouse] SHALL support using encrypted disks for sharded tables even if
nodes have different encryption and decryption keys or nodes have different disk types.

### Sharded And Replicated Tables

#### RQ.SRS-025.ClickHouse.DiskLevelEncryption.ShardedAndReplicatedTables
version: 1.0

[ClickHouse] SHALL support using encrypted disks for sharded and replicated tables even if
nodes have different encryption and decryption keys or nodes have different disk types.

### Operations

#### Multi-Disk Volumes

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.MultiDiskVolumes
version: 1.0

[ClickHouse] SHALL support having encrypted disk in multi-disk volumes.

```xml
  <volumes>
    <my_volume>
          <disk>encrypted_local</disk>
          <disk>local</disk>
    </my_volume>
  </volumes>
```

#### Multi-Volume Policies

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.MultiVolumePolicies
version: 1.0

[ClickHouse] SHALL support having encrypted disk when policy contains multiple
volumes which have one or more encrypted disks.

```xml
  <my_policy>
    <volumes>
      <my_volume_0>
            <disk>encrypted_local</disk>
            <disk>local</disk>
      </my_volume_0>
      <my_volume_1>
            <disk>other_encrypted_local</disk>
            <disk>other_local</disk>
      </my_volume_1>
    </volumes>
  </my_policy>
```

#### Merging Parts

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.MergingWithDifferentKeys
version: 1.0

[ClickHouse] SHALL merge different parts regardless of what keys they are encrypted with.

#### Partitions And Parts

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.Alter.PartitionsAndParts
version: 1.0

[ClickHouse] SHALL support all operations with partitions and parts
when encrypted disk is used for table storage such as

* [DETACH PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_detach-partition) 
* [DROP PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_drop-partition) 
* [ATTACH PART|PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_attach-partition)
* [ATTACH PARTITION FROM](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_attach-partition-from)
* [REPLACE PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_replace-partition)
* [MOVE PARTITION TO TABLE](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_move_to_table-partition)
* [CLEAR COLUMN IN PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_clear-column-partition)
* [CLEAR INDEX IN PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_clear-index-partition)
* [FREEZE PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_freeze-partition)
* [UNFREEZE PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_unfreeze-partition)
* [FETCH PARTITION|PART](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_fetch-partition) 
* [MOVE PARTITION|PART]
* [UPDATE IN PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#update-in-partition)
* [DELETE IN PARTITION](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#delete-in-partition)

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.Alter.MoveBetweenEncryptedAndNonEncryptedDisks
version: 1.0

[ClickHouse] SHALL support [MOVE PARTITION|PART] from encrypted to non-encrypted disk and vice versa.

#### Insert And Select

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.InsertAndSelect
version: 1.0

[ClickHouse] SHALL support all read and write operations when encrypted disk is used for table storage such as

* [INSERT]
* [SELECT]

For [INSERT] the following cases SHALL work:

* one block insert that has rows that go all into the same partition
* one block insert that has rows that go into multiple partitions
* multiple block insert that has rows that go all into the same partition
* multiple block insert that has rows that go into multiple partitions
* multiple statements executed back to back
* cuncurrent inserts

For [SELECT] the following cases SHALL work:

* query that reads data where all rows come from only one partition and one part
* query that reads data where all rows come from only one partition and multiple parts
* query that reads data from multiple partitions and multiple parts
* query that reads all the data

#### Table Operations

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.Table
version: 1.0

[ClickHouse] SHALL support all table operations when encrypted disk is used for table storage such as

* [CREATE](https://clickhouse.com/docs/en/sql-reference/statements/create/)
* [DROP](https://clickhouse.com/docs/en/sql-reference/statements/drop/)
* [DETACH](https://clickhouse.com/docs/en/sql-reference/statements/detach/)
* [CHECK](https://clickhouse.com/docs/en/sql-reference/statements/check-table/)
* [ATTACH](https://clickhouse.com/docs/en/sql-reference/statements/attach/)
* [OPTIMIZE](https://clickhouse.com/docs/en/sql-reference/statements/optimize/)
* [RENAME](https://clickhouse.com/docs/en/sql-reference/statements/rename/)
* [EXCHANGE](https://clickhouse.com/docs/en/sql-reference/statements/exchange/)
* [TRUNCATE](https://clickhouse.com/docs/en/sql-reference/statements/truncate/)

#### Table TTL

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.TableTTL
version: 1.0

[ClickHouse] SHALL support [Table TTL](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/#mergetree-table-ttl) from and to encrypted disk.

#### Column TTL

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.ColumnTTL
version: 1.0

[ClickHouse] SHALL support [Column TTL](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/#mergetree-column-ttl) when table is stored on the encrypted disk.

#### Tiered Storage

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Operations.TieredStorage
version: 1.0

[ClickHouse] SHALL support using encrypted disks and other disks together as parts of [Tiered Storage]
even when disks have different encryption keys.

#### Table Views

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Compatability.View
version: 1.0

[ClickHouse] SHALL support using views over tables that are stored
on the encrypted disk. 

* [NORMAL](https://clickhouse.com/docs/en/sql-reference/statements/create/view/#normal)
* [MATERIALIZED](https://clickhouse.com/docs/en/sql-reference/statements/create/view/#materialized)
* [LIVE](https://clickhouse.com/docs/en/sql-reference/statements/create/view/#live-view)

### Disk Types

#### Local

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.Local
version: 1.0

[ClickHouse] SHALL support disk level encryption for any `local` type (`<type>local</type>`)
disks specified in the `<clickhouse><storage_configuration><disks>` section of the `config.xml`
configuration file.

#### S3

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.S3
version: 1.0

[ClickHouse] SHALL support disk level encryption for any `s3` type (`<type>s3</type>`)
disks specified in the `<clickhouse><storage_configuration><disks>` section of the `config.xml`
configuration file.

#### Memory

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.Memory
version: 1.0

[ClickHouse] SHALL support disk level encryption for any `memory` type (`<type>memory</type>`)
disks specified in the `<clickhouse><storage_configuration><disks>` section of the `config.xml`
configuration file.

#### Encrypted

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.Encrypted
version: 1.0

[ClickHouse] SHALL support disk level encryption for any `encrypted` type (`<type>encrypted</type>`)
disks specified in the `<clickhouse><storage_configuration><disks>` section of the `config.xml`
configuration file.

#### HDFS

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Disk.HDFS
version: 1.0

[ClickHouse] SHALL support disk level encryption for any `hdfs` type (`<type>hdfs</type>`)
disks specified in the `<clickhouse><storage_configuration><disks>` section of the `config.xml`
configuration file.

### Encryption Algorithms

#### Default Algorithm

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.Default
version: 1.0

[ClickHouse] SHALL use `AES_128_CTR` as the default algorithm for disk level encryption.

#### AES_128_CTR

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.AES_128_CTR
version: 1.0

[ClickHouse] SHALL support `AES_128_CTR` algorithm for disk level encryption.

#### AES_192_CTR

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.AES_192_CTR
version: 1.0

[ClickHouse] SHALL support `AES_192_CTR` algorithm for disk level encryption.

#### AES_256_CTR

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.AES_256_CTR
version: 1.0

[ClickHouse] SHALL support `AES_256_CTR` algorithm for disk level encryption.

#### Mixed Algorithms

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Algorithm.Conflict
version: 1.0

[ClickHouse] SHALL return an error if encryption algorithm is changed,
but there are parts already encrypted with a previous algorithm.

### Encryption Keys

#### Encryption Key

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Encryption
version: 1.0

[ClickHouse] SHALL support specifying key to be used for data encryption
and uniquely identify the key used for encryption when multiple keys
are defined for the disk.

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.PartsWithDifferentKeys
version: 1.0

[ClickHouse] SHALL support parts encrypted with different keys when using encrypted disk.

#### Decryption Key

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Decryption
version: 1.0

[ClickHouse] SHALL support specifying one or more keys to be used for data decryption.


##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Missing
version: 1.0

[ClickHouse] SHALL return an error if any key that was used to encrypt the disk is missing.

#### Key Formats

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Format.ASCII
version: 1.0

[ClickHouse] SHALL support specifying encryption and decryption keys as an ASCII string 
that will be converted into an array of `UInt64`.

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Format.SpecialXMLSymbols
version: 1.0

[ClickHouse] SHALL support specifying encryption and decryption keys that 
contain one or more special XML symbols that require escaping that will be 
converted into an array of `UInt64`.

* `<` (less-than) `&#60;` or `&lt;`
* `>` (greater-than) `&#62;` or  `&gt;`
* `&` (ampersand) `&#38;`
* `'` (apostrophe or single quote) `&#39;`
* `"` (double-quote) `&#34;`

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Format.UTF8
version: 1.0

[ClickHouse] SHALL support specifying encryption and decryption keys as a UTF-8 string
that will be converted into an array of `UInt64`.

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Format.Hex
version: 1.0

[ClickHouse] SHALL support specifying encryption and decryption keys as hexadecimal number.

#### Invalid Size Key

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Key.Invalid.Size
version: 1.0

[ClickHouse] SHALL return an error if the the encryption key has the wrong size (either too long or too short)
for the algorithm. The following sizes SHALL be enforced

* for AES_128_CTR key size SHALL be equal to 16 bytes
* for AES_192_CTR key size SHALL be equal to 24 bytes
* for AES_256_CTR key size SHALL be equal to 32 bytes

If the size of the key is invalid then the server SHALL not start and write and error message into
its error log.

### Config

#### Access permission

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.AccessPermission.WideOrInvalid
version: 1.0

[ClickHouse] SHALL return an error if the configuration file 
which contains encryption keys has invalid or wide access permissions.

#### Application of Changes

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.ApplicationOfChanges
version: 1.0

[ClickHouse] SHALL only apply changes to the encrypted disk definition in the `config.xml` without server restart. 

#### Path

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path
version: 1.0

[ClickHouse] SHALL support `<path>` parameter
inside the `<clickhouse><storage_configuration><disks><disk_name>` section
of the `config.xml` file that SHALL specify the path
where the encrypted data SHALL be stored on the disk
referred by the `<disk>` parameter.

For example,

```xml
<clickhouse>
    <storage_configuration>
        <disks>
            <encrypted_disk_name>
                <path>path_name<path>
                <disk>disk_name</disk>
                ...
```

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path.Default
version: 1.0

[ClickHouse] SHALL save data to the root of the disk specified by the `<disk>` parameter
if the `<path>` parameter is not specified or empty.

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path.Invalid
version: 1.0

[ClickHouse] SHALL return an error if the path specified in the `<path>` parameter is invalid.

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path.NoAccessRights
version: 1.0

[ClickHouse] SHALL return an error if user has no rights to read or write to the path
specified in the `<path>` parameter.

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Path.NewDirectories
version: 1.0

[ClickHouse] SHALL create new directories if the path specified by `path` parameter not exist.

#### Disk

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Disk
version: 1.0

[ClickHouse] SHALL support `<disk>` parameter
inside the `<clickhouse><storage_configuration><disks><disk_name>` section
of the `config.xml` file that SHALL specify the disk
where the encrypted data SHALL be stored. The specified disk
SHALL refer to one of the previously defined disks inside the 
`<clickhouse><storage_configuration><disks>` section.

For example,

```xml
<clickhouse>
    <storage_configuration>
        <disks>
            <disk_name>
                ...
            </disk_name>
            <encrypted_disk_name>
                <disk>disk_name</disk>
                    ...
```

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Disk.Invalid
version: 1.0

[ClickHouse] SHALL return an error if the disk specified in the `<disk>` parameter is either:

* does not exist
* the value is empty
* the `<disk>` parameter itself is missing

#### Keys Configuration

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key
version: 1.0

[ClickHouse] SHALL support `<key>` parameter in the 
`<clickhouse><storage_configuration><disks><disk_name>` section of the `config.xml` file
that SHALL specify a key that SHALL be used for encryption or decryption of
data stored on the disk. 

For example,

```xml
<clickhouse>
    <storage_configuration>
        <disks>
            ...
            <disk_local_encrypted>
                <type>encrypted</type>
                <disk>disk_local</disk>
                <path>encrypted/</path>
                <key>abcdefghijklmnop</key>
            </disk_local_encrypted>
```

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Hex
version: 1.0

[ClickHouse] SHALL support `<key_hex>` parameter in the 
`<clickhouse><storage_configuration><disks><disk_name>` section of the `config.xml` file
that SHALL specify a key in the hexadecimal format that SHALL be used for encryption or decryption of
data stored on the disk. 

For example,

```xml
<clickhouse>
    <storage_configuration>
        <disks>
            ...
            <disk_local_encrypted>
                <type>encrypted</type>
                <disk>disk_local</disk>
                <path>encrypted/</path>
                <key_hex>efadfdfdfdfdfdfaefadfdfdfdfdfdfa</key_hex>
            </disk_local_encrypted>
```

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.HexKeyConflict
version: 1.0

[ClickHouse] SHALL return an error when both `<key_hex>` and `<key>` parameters are defined
without `id`.

For example,

```xml
<clickhouse>
    <storage_configuration>
        <disks>
            ...
            <disk_encrypted>
                ...
                <key_hex>efadfdfdfdfdfdfaefadfdfdfdfdfdfa</key_hex>
                <key>firstfistfirstfirst<key>
                ...  
            </disk_encrypted>
```

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple
version: 1.0

[ClickHouse] SHALL support `<key id="key_id">` parameter
when more than one key is specified in the `<clickhouse><storage_configuration><disks><disk_name>`
section of the `config.xml` file where `id` value SHALL uniquely
identify each unique key.

For example,

```xml
<clickhouse>
    <storage_configuration>
        <disks>
            ...
            <disk_encrypted> 
                <key id="0">firstfirstfirstf</key>
                <key id="1">secondsecondseco</key>
                ...
            </disk_encrypted>
```

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.HexKeyIdConflict
version: 1.0

[ClickHouse] SHALL return an error when both `<key_hex>` and `<key>` parameters are defined
with the same `id`.

For example,

```xml
<clickhouse>
    <storage_configuration>
        <disks>
            ...
            <disk_encrypted>
                ...
                <key_hex id="0">efadfdfdfdfdfdfaefadfdfdfdfdfdfa</key_hex>
                <key id="0">firstfistfirstfirst<key>
                ...  
            </disk_encrypted>
```

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.MixedFormats
version: 1.0

[ClickHouse] SHALL support specifying `id` parameter, when keys are defined in 
both hexadecimal and string formats for the same disk.

For example,

```xml
<clickhouse>
    <storage_configuration>
        <disks>
            ...
            <disk_encrypted>
                ...
                <key_hex id="0">efadfdfdfdfdfdfaefadfdfdfdfdfdfa</key_hex>
                <key id="1">firstfistfirstfirst<key>
                ...  
            </disk_encrypted>
```

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.Id.Invalid
version: 1.0

[ClickHouse] SHALL return an error if `id` of the key is not a positive integer
or a key with the same `id` is already defined.

#### Current Key Id

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.CurrentKeyId
version: 1.0

[ClickHouse] SHALL support `<current_key_id>` parameter in the `<clickhouse><storage_configuration><disks><disk_name>`
section of the `config.xml` file that SHALL specify
a key that SHALL be used for data encryption when multiple keys
are present and are indentified by a unique `id`.

For example,

```xml
<clickhouse>
    <storage_configuration>
        <disks>
            <disk_encrypted>
                ...
                <key id="0">firstfirstfirstf</key>
                <key id="1">secondsecondseco</key>
                <current_key_id>1</current_key_id>
            <disk_encrypted>
```


##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.CurrentKeyId.Invalid
version: 1.0

[ClickHouse] SHALL return an error if the value of the `<current_key_id>` is either:

* does not refer to previously defined key
* is empty

##### RQ.SRS-025.ClickHouse.DiskLevelEncryption.Config.Key.Multiple.CurrentKeyId.Default
version: 1.0

[ClickHouse] SHALL use `0` as the default `<current_key_id>` parameter 
when more than one key is defined for disk level encryption.


[MOVE PARTITION|PART]: https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#alter_move-partition
[Tiered Storage]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/#table_engine-mergetree-multiple-volumes
[INSERT]: https://clickhouse.com/docs/en/sql-reference/statements/insert-into/
[SELECT]: https://clickhouse.com/docs/en/sql-reference/statements/select/
[SRS]: #srs
[ClickHouse]: https://clickhouse.com
[Gitlab repository]: https://gitlab.com/altinity-qa/documents/qa-srs025-clickhouse-disk-level-encryption/blob/main/QA_SRS025_ClickHouse_Disk_Level_Encryption.md
[Revision history]: https://gitlab.com/altinity-qa/documents/qa-srs025-clickhouse-disk-level-encryption/commits/main/QA_SRS025_ClickHouse_Disk_Level_Encryption.md
[Git]: https://git-scm.com/
[GitLab]: https://gitlab.com
""",
)
