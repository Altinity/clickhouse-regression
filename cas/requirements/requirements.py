# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_048_CAS = Requirement(
    name='RQ.SRS-048.CAS',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support content-addressed storage as an object-storage disk\n'
        'backend for the [MergeTree] engine family.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.1.1'
)

RQ_SRS_048_CAS_NotATableEngine = Requirement(
    name='RQ.SRS-048.CAS.NotATableEngine',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL expose [CAS] as a disk / storage-policy choice, not as a\n'
        'separate table engine. Users SHALL create ordinary `MergeTree` /\n'
        '`ReplicatedMergeTree` (and MergeTree-family) tables on a [CAS] disk or policy.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.1.2'
)

RQ_SRS_048_CAS_Disk_Configuration = Requirement(
    name='RQ.SRS-048.CAS.Disk.Configuration',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support configuring a [CAS] disk in\n'
        '`<storage_configuration><disks>` with `type = object_storage`, an object-storage\n'
        'type such as `s3` or `local`, and [CAS]-specific settings including\n'
        '`metadata_type = cas` and `cas_server_root_id`. The recommended production\n'
        'shape layers a `type = cache` disk over the [CAS] disk and points the storage\n'
        'policy at the cached disk.\n'
        '\n'
        'Example:\n'
        '\n'
        '```xml\n'
        '<clickhouse>\n'
        '    <storage_configuration>\n'
        '        <disks>\n'
        '            <cas>\n'
        '                <type>object_storage</type>\n'
        '                <object_storage_type>s3</object_storage_type>\n'
        '                <metadata_type>cas</metadata_type>\n'
        '                <cas_server_root_id>{replica}</cas_server_root_id>\n'
        '                <endpoint>https://bucket.s3.amazonaws.com/cas/</endpoint>\n'
        '            </cas>\n'
        '            <cas_cache>\n'
        '                <type>cache</type>\n'
        '                <disk>cas</disk>\n'
        '                <path>/var/lib/clickhouse/cas_cache/</path>\n'
        '                <max_size>10Gi</max_size>\n'
        '            </cas_cache>\n'
        '        </disks>\n'
        '        <policies>\n'
        '            <cas>\n'
        '                <volumes>\n'
        '                    <main>\n'
        '                        <disk>cas_cache</disk>\n'
        '                    </main>\n'
        '                </volumes>\n'
        '            </cas>\n'
        '        </policies>\n'
        '    </storage_configuration>\n'
        '</clickhouse>\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.1'
)

RQ_SRS_048_CAS_Disk_MetadataType = Requirement(
    name='RQ.SRS-048.CAS.Disk.MetadataType',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL enable content-addressed storage when\n'
        '`metadata_type` is set to `cas` on an object-storage disk.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.2'
)

RQ_SRS_048_CAS_Disk_ServerRootId = Requirement(
    name='RQ.SRS-048.CAS.Disk.ServerRootId',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL require a configured `cas_server_root_id` that identifies the\n'
        "server's durable ownership tree inside the pool. Omitting the setting SHALL be a\n"
        'startup error. The value MAY expand macros (for example `{replica}`) and SHALL\n'
        "remain stable across restarts for that server's membership in the pool. The\n"
        'unprefixed spelling `server_root_id` SHALL be accepted for a bounded migration\n'
        'period and reported at startup; a key written in both spellings SHALL be\n'
        'rejected.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.3'
)

RQ_SRS_048_CAS_Disk_ServerRootId_Unique = Requirement(
    name='RQ.SRS-048.CAS.Disk.ServerRootId.Unique',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL fail closed when two servers attempt to mount the same pool\n'
        'with the same `cas_server_root_id` as concurrent writers, instead of allowing\n'
        'both to mutate the same ref namespace. A colliding identity SHALL be refused at\n'
        'the owner-claim / mount-lease gate.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.4'
)

RQ_SRS_048_CAS_Disk_Pool = Requirement(
    name='RQ.SRS-048.CAS.Disk.Pool',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL treat the object-storage endpoint (bucket and prefix) as the\n'
        'shared [CAS] pool for blob reuse among servers that mount that endpoint with\n'
        'distinct `cas_server_root_id` values. Relink eligibility SHALL use the minted\n'
        '`cas_pool_uuid`, not endpoint-plus-prefix string equality.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.5'
)

RQ_SRS_048_CAS_Disk_Inline = Requirement(
    name='RQ.SRS-048.CAS.Disk.Inline',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support selecting a [CAS] disk via the inline `disk = disk(...)`\n'
        'table setting as well as via a named disk in storage configuration.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.6'
)

RQ_SRS_048_CAS_Policy = Requirement(
    name='RQ.SRS-048.CAS.Policy',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support selecting [CAS] disks through storage policies in\n'
        '`<storage_configuration><policies>`, consistent with other object-storage disks.\n'
        'When a `type = cache` disk wraps [CAS], the policy volume SHALL name the cache\n'
        'disk, not the raw [CAS] disk.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.7'
)

RQ_SRS_048_CAS_Disk_Settings = Requirement(
    name='RQ.SRS-048.CAS.Disk.Settings',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL read [CAS]-owned disk settings from the `cas_` config-key\n'
        'namespace and leave every other key in the disk block to the object-storage or\n'
        'generic disk layer. A misspelled `cas_` key SHALL be rejected. Unprefixed\n'
        'spellings of [CAS] settings SHALL be accepted for a bounded period and reported\n'
        'at startup. `skip_access_check` and `gcs_max_conditional_put_bytes` SHALL remain\n'
        'unprefixed (they belong to the generic disk / S3 client layers).\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.8'
)

RQ_SRS_048_CAS_Disk_BlobHash = Requirement(
    name='RQ.SRS-048.CAS.Disk.BlobHash',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support selecting the pool blob content-hash function with\n'
        '`cas_blob_hash` (`cityhash128` default, `xxh3-128`, or `sha256`). The algorithm\n'
        'SHALL be recorded in the pool at creation; a mismatching config SHALL be refused\n'
        'at mount. `cas_blob_hash_allow_new` SHALL be the explicit opt-in that admits a\n'
        'second algorithm into an existing pool.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.9'
)

RQ_SRS_048_CAS_Disk_Backends = Requirement(
    name='RQ.SRS-048.CAS.Disk.Backends',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support [CAS] on AWS S3 (`ETag` conditional dialect) and on\n'
        'the `local` object-storage backend (single-node / demo). Google Cloud Storage\n'
        'SHALL use the generation-token dialect (`http_client = gcs_hmac` or\n'
        '`gcp_oauth`). Other S3-compatible stores SHALL be admitted only when the mount\n'
        'capability probe confirms they enforce conditional operations. Azure Blob is\n'
        'specified under\n'
        '[RQ.SRS-048.CAS.Restrictions.Azure](#rqsrs-048casrestrictionsazure).\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.10'
)

RQ_SRS_048_CAS_ObjectModel = Requirement(
    name='RQ.SRS-048.CAS.ObjectModel',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL store [MergeTree] parts on a [CAS] disk as content-addressed\n'
        'objects in the pool, consisting of blobs, part manifests, refs, and a blob\n'
        'condemnation-marker sidecar, rather than as ordinary per-table part path copies\n'
        'alone. There is no [CAS] state in Keeper; pool bookkeeping lives in the bucket.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.3.1'
)

RQ_SRS_048_CAS_ObjectModel_Blobs = Requirement(
    name='RQ.SRS-048.CAS.ObjectModel.Blobs',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL store content-addressed file payloads as immutable blob\n'
        'objects under a pool-global `blobs/` prefix, keyed by content hash, so identical\n'
        'bytes MAY be shared across tables and servers in the same pool.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.3.2'
)

RQ_SRS_048_CAS_ObjectModel_Manifests = Requirement(
    name='RQ.SRS-048.CAS.ObjectModel.Manifests',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL store an immutable part manifest that lists the files\n'
        'belonging to one [MergeTree] part and their blob (or inline) placements.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.3.3'
)

RQ_SRS_048_CAS_ObjectModel_Refs = Requirement(
    name='RQ.SRS-048.CAS.ObjectModel.Refs',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL maintain mutable refs under each server's ownership namespace\n"
        'that map part names to manifests. Refs SHALL be the mutable layer that changes\n'
        'when parts are created, merged, mutated, or dropped.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.3.4'
)

RQ_SRS_048_CAS_ObjectModel_Immutability = Requirement(
    name='RQ.SRS-048.CAS.ObjectModel.Immutability',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL treat blobs and manifests as immutable after publish. Logical\n'
        'part changes SHALL produce new parts (and therefore new manifests / ref updates)\n'
        'rather than rewriting existing blob or manifest identities in place.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.3.5'
)

RQ_SRS_048_CAS_MergeTree = Requirement(
    name='RQ.SRS-048.CAS.MergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support the [MergeTree] engine family on a [CAS] disk without\n'
        'requiring CAS-specific DDL beyond disk / policy selection.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.1'
)

RQ_SRS_048_CAS_MergeTree_Transparency = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Transparency',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL preserve ordinary [MergeTree] logical behavior for tables on\n'
        'a [CAS] disk. User-visible query results, part lifecycle semantics, and\n'
        'supported `ALTER` / partition operations SHALL match non-CAS [MergeTree] unless\n'
        'an explicit [CAS] restriction applies. [CAS] MUST NOT invent a separate SQL\n'
        'dialect for everyday table use.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.2'
)

RQ_SRS_048_CAS_MergeTree_Engines = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Engines',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support the mainstream [MergeTree] engine family on a [CAS]\n'
        'disk, including at least:\n'
        '\n'
        '* `MergeTree`\n'
        '* `ReplicatedMergeTree`\n'
        '* `ReplacingMergeTree` / `ReplicatedReplacingMergeTree`\n'
        '* `SummingMergeTree` / `ReplicatedSummingMergeTree`\n'
        '* `AggregatingMergeTree` / `ReplicatedAggregatingMergeTree`\n'
        '* `CollapsingMergeTree` / `ReplicatedCollapsingMergeTree`\n'
        '* `VersionedCollapsingMergeTree` / `ReplicatedVersionedCollapsingMergeTree`\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.3'
)

RQ_SRS_048_CAS_MergeTree_InsertSelect = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.InsertSelect',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `INSERT` and `SELECT` on [MergeTree] tables stored on\n'
        'a [CAS] disk with the same logical results as on a non-CAS disk for the same\n'
        'data.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.4'
)

RQ_SRS_048_CAS_MergeTree_Merge = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Merge',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support merges (`OPTIMIZE` / background merges) of parts on a\n'
        '[CAS] disk. After merge, logical table contents SHALL remain correct and unused\n'
        'source parts SHALL become eligible for [GC] reclaim when no longer referenced.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.5'
)

RQ_SRS_048_CAS_MergeTree_Replicated = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Replicated',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ReplicatedMergeTree` tables on a shared [CAS] pool\n'
        'so that replicas converge to the same logical data while each replica owns its\n'
        'own ref namespace under a distinct `cas_server_root_id`.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.6'
)

RQ_SRS_048_CAS_MergeTree_PartTypes = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.PartTypes',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Wide and Compact [MergeTree] parts on a [CAS] disk.\n'
        'Projections, patch parts, detached parts, temporary parts, and frozen/shadow\n'
        'parts SHALL be representable in the [CAS] object model.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.7'
)

RQ_SRS_048_CAS_MergeTree_Alter_Schema = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Alter.Schema',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support schema-changing `ALTER TABLE` operations on\n'
        '[CAS]-backed [MergeTree] tables (for example add / drop / modify / rename\n'
        'column, codec changes) with the same logical outcome as on non-CAS storage,\n'
        'implemented via the ordinary new-part / drop-old-part [MergeTree] path.\n'
        'The full [MergeTree] `ALTER TABLE` catalog is specified under\n'
        '[RQ.SRS-048.CAS.MergeTree.Alter](#rqsrs-048casmergetreealter).\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.8'
)

RQ_SRS_048_CAS_MergeTree_Mutations = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Mutations',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support mutations on [CAS]-backed [MergeTree] tables. Where\n'
        'Wide-part carry-forward applies, unchanged column blobs MAY be re-referenced\n'
        'without re-upload; logical mutation results SHALL match non-CAS behavior.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.9'
)

RQ_SRS_048_CAS_MergeTree_LightweightDelete = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.LightweightDelete',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support lightweight deletes on [CAS]-backed [MergeTree]\n'
        'tables with correct logical visibility of deleted rows.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.10'
)

RQ_SRS_048_CAS_MergeTree_PatchParts = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.PatchParts',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support patch parts on [CAS]-backed [MergeTree] tables and\n'
        'SHALL preserve patch-part durability across server restart.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.11'
)

RQ_SRS_048_CAS_MergeTree_Projections = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Projections',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support [MergeTree] projections on a [CAS] disk. Projection\n'
        'files SHALL be stored as nested entries of the parent part manifest (not as an\n'
        "independently GC'd projection ref namespace), and projection query results SHALL\n"
        'match non-CAS behavior.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.12'
)

RQ_SRS_048_CAS_MergeTree_TTL = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.TTL',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support TTL delete and TTL move rules on [CAS]-backed\n'
        '[MergeTree] tables with correct logical data removal or relocation semantics.\n'
        'Cross-disk TTL / `MOVE PARTITION ... TO DISK|VOLUME` onto or off [CAS] MAY be\n'
        'subject to additional verification constraints documented under restrictions.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.13'
)

RQ_SRS_048_CAS_MergeTree_Transactions = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Transactions',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support [MergeTree] transactions / MVCC metadata on a [CAS]\n'
        'disk through the content-addressed transactional mutable-file capability, so\n'
        'that transaction metadata files (for example `txn_version.txt`) are carried as\n'
        'ordinary manifest entries and atomically repointed with the part ref.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.14'
)

RQ_SRS_048_CAS_MergeTree_RestartDurability = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.RestartDurability',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL preserve committed [CAS]-backed table data and applicable\n'
        'mutation / patch-part / projection state across ClickHouse server restart.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.15'
)

RQ_SRS_048_CAS_MergeTree_Alter = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Alter',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support the documented `ALTER TABLE` modifiers for the\n'
        '[MergeTree] family on a [CAS] disk with the same logical outcome as on\n'
        'non-CAS [MergeTree] storage, except where this [SRS] lists a restriction.\n'
        'There SHALL be no [CAS]-specific SQL dialect for these commands.\n'
        '\n'
        'The catalog follows the upstream [ALTER](https://clickhouse.com/docs/reference/statements/alter)\n'
        'index. Commands that create mutations (`UPDATE`, `DELETE`, `MATERIALIZE *`,\n'
        '`CLEAR INDEX` / `CLEAR STATISTICS` / `CLEAR PROJECTION`, `APPLY DELETED MASK`,\n'
        '`APPLY PATCHES`, `REWRITE PARTS`, and similar) SHALL rewrite parts through the\n'
        'ordinary [MergeTree] mutation path (new parts / new refs). Metadata-only\n'
        'commands SHALL not invent a separate [CAS] rewrite of immutable blobs.\n'
        '\n'
        'Partition commands are additionally gated by\n'
        '[RQ.SRS-048.CAS.Partition.AlterAllowList](#rqsrs-048caspartitionalterallowlist).\n'
        'View, RBAC, named-collection, and `ALTER DATABASE` statements are out of\n'
        'scope for [CAS] table storage.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.16'
)

RQ_SRS_048_CAS_MergeTree_Alter_Column = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Alter.Column',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support column `ALTER TABLE` actions on [CAS]-backed\n'
        '[MergeTree] tables:\n'
        '\n'
        '* `ADD COLUMN [IF NOT EXISTS] ... [AFTER ... | FIRST]`\n'
        '* `DROP COLUMN [IF EXISTS] ...`\n'
        '* `RENAME COLUMN [IF EXISTS] ... TO ...`\n'
        '* `CLEAR COLUMN [IF EXISTS] ... IN PARTITION ...`\n'
        '* `COMMENT COLUMN [IF EXISTS] ...`\n'
        '* `MODIFY COLUMN` / `ALTER COLUMN ... TYPE` (type, default, codec, TTL,\n'
        '  statistics, column settings, `FIRST` / `AFTER`)\n'
        '* `MODIFY COLUMN ... REMOVE` (`DEFAULT`, `ALIAS`, `MATERIALIZED`, `CODEC`,\n'
        '  `COMMENT`, `TTL`, `SETTINGS`)\n'
        '* `MODIFY COLUMN ... MODIFY SETTING ...`\n'
        '* `MODIFY COLUMN ... RESET SETTING ...`\n'
        '* `MODIFY COLUMN ... ADD ENUM VALUES ...`\n'
        '* `MATERIALIZE COLUMN ... [IN PARTITION ... | IN PARTITION ID ...]`\n'
        '\n'
        'Logical results SHALL match non-CAS [MergeTree]. `MATERIALIZE COLUMN` SHALL\n'
        'be implemented as a mutation. Key-column rename / type-change limitations\n'
        'SHALL match upstream [MergeTree] (not [CAS]-specific).\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.17'
)

RQ_SRS_048_CAS_MergeTree_Alter_Update = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Alter.Update',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support heavyweight\n'
        '\n'
        '```sql\n'
        'ALTER TABLE [db.]table UPDATE column1 = expr1 [, ...] [IN PARTITION partition_expr] WHERE filter_expr\n'
        '```\n'
        '\n'
        'on [CAS]-backed [MergeTree] tables as a mutation. Logical updated values\n'
        'SHALL match non-CAS behavior. Updating columns used in the primary or\n'
        'partition key SHALL remain unsupported, as on non-CAS [MergeTree].\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.18'
)

RQ_SRS_048_CAS_MergeTree_Alter_Delete = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Alter.Delete',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support heavyweight\n'
        '\n'
        '```sql\n'
        'ALTER TABLE [db.]table DELETE [IN PARTITION partition_expr] WHERE filter_expr\n'
        '```\n'
        '\n'
        'on [CAS]-backed [MergeTree] tables as a mutation. Logical row removal SHALL\n'
        'match non-CAS behavior. This requirement covers `ALTER TABLE ... DELETE`,\n'
        'not `DELETE FROM` lightweight deletes\n'
        '([RQ.SRS-048.CAS.MergeTree.LightweightDelete](#rqsrs-048casmergetreelightweightdelete)).\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.19'
)

RQ_SRS_048_CAS_MergeTree_Alter_OrderBy = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Alter.OrderBy',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ALTER TABLE ... MODIFY ORDER BY ...` on\n'
        '[CAS]-backed [MergeTree] tables as a metadata-only change of the sorting\n'
        'key (primary key unchanged), with the same restrictions as non-CAS\n'
        '[MergeTree].\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.20'
)

RQ_SRS_048_CAS_MergeTree_Alter_SampleBy = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Alter.SampleBy',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ALTER TABLE ... MODIFY SAMPLE BY ...` and\n'
        '`ALTER TABLE ... REMOVE SAMPLE BY` on [CAS]-backed [MergeTree] tables as\n'
        'metadata-only sampling-key changes, with the same primary-key containment\n'
        'rules as non-CAS [MergeTree].\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.21'
)

RQ_SRS_048_CAS_MergeTree_Alter_Index = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Alter.Index',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support data-skipping-index `ALTER TABLE` actions on\n'
        '[CAS]-backed [MergeTree] tables:\n'
        '\n'
        '* `ADD INDEX [IF NOT EXISTS] ... TYPE ... [GRANULARITY ...] [FIRST | AFTER ...]`\n'
        '* `DROP INDEX [IF EXISTS] ...`\n'
        '* `MATERIALIZE INDEX [IF EXISTS] ... [IN PARTITION ...]`\n'
        '* `CLEAR INDEX [IF EXISTS] ... [IN PARTITION ...]`\n'
        '\n'
        '`ADD INDEX` SHALL update metadata. `MATERIALIZE INDEX`, `DROP INDEX`, and\n'
        '`CLEAR INDEX` SHALL follow upstream mutation / file-removal semantics.\n'
        'Logical skip-index behavior SHALL match non-CAS [MergeTree].\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.22'
)

RQ_SRS_048_CAS_MergeTree_Alter_Projection = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Alter.Projection',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support projection `ALTER TABLE` actions on [CAS]-backed\n'
        '[MergeTree] tables:\n'
        '\n'
        '* `ADD PROJECTION [IF NOT EXISTS] ...`\n'
        '* `DROP PROJECTION [IF EXISTS] ...`\n'
        '* `MATERIALIZE PROJECTION [IF EXISTS] ... [IN PARTITION ...]`\n'
        '* `CLEAR PROJECTION [IF EXISTS] ... [IN PARTITION ...]`\n'
        '* `MODIFY PROJECTION [IF EXISTS] ... ( SELECT ... ) WITH SETTINGS (...)`\n'
        '\n'
        'Projection files SHALL remain nested entries of the parent part manifest\n'
        '([RQ.SRS-048.CAS.MergeTree.Projections](#rqsrs-048casmergetreeprojections)).\n'
        'Query results that use the projection SHALL match non-CAS behavior.\n'
        '\n'
        '`MODIFY PROJECTION` only applies to [ClickHouse] >= 26.9, where the command\n'
        'was added to the parser. Older builds, including the 26.6-based Antalya\n'
        'build, reject it with `SYNTAX_ERROR` on non-CAS [MergeTree] as well, so\n'
        'scenarios covering it SHALL be skipped there.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.23'
)

RQ_SRS_048_CAS_MergeTree_Alter_Constraint = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Alter.Constraint',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support constraint `ALTER TABLE` actions on [CAS]-backed\n'
        '[MergeTree] tables:\n'
        '\n'
        '* `ADD CONSTRAINT [IF NOT EXISTS] ... {CHECK | ASSUME} ...`\n'
        '* `DROP CONSTRAINT [IF EXISTS] ...`\n'
        '* `MODIFY CONSTRAINT [IF EXISTS] ... {CHECK | ASSUME} ...`\n'
        '\n'
        'These commands SHALL change table metadata immediately and SHALL NOT\n'
        're-check existing rows, matching non-CAS [MergeTree].\n'
        '\n'
        '`MODIFY CONSTRAINT` only applies to [ClickHouse] >= 26.7, where the command\n'
        'was added to the parser. Older builds, including the 26.6-based Antalya\n'
        'build, reject it with `SYNTAX_ERROR` on non-CAS [MergeTree] as well, so\n'
        'scenarios covering it SHALL be skipped there.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.24'
)

RQ_SRS_048_CAS_MergeTree_Alter_TTL = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Alter.TTL',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support table-TTL `ALTER TABLE` actions on [CAS]-backed\n'
        '[MergeTree] tables:\n'
        '\n'
        '* `MODIFY TTL ...`\n'
        '* `REMOVE TTL`\n'
        '* `MATERIALIZE TTL`\n'
        '\n'
        '`MODIFY TTL` / `REMOVE TTL` SHALL update metadata. `MATERIALIZE TTL` SHALL\n'
        'force TTL application as a mutation. Column TTL SHALL be covered by\n'
        '`MODIFY COLUMN ... TTL` /\n'
        '[RQ.SRS-048.CAS.MergeTree.Alter.Column](#rqsrs-048casmergetreealtercolumn).\n'
        'Logical delete / move-to-volume TTL semantics SHALL match\n'
        '[RQ.SRS-048.CAS.MergeTree.TTL](#rqsrs-048casmergetreettl).\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.25'
)

RQ_SRS_048_CAS_MergeTree_Alter_Statistics = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Alter.Statistics',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support column-statistics `ALTER TABLE` actions on\n'
        '[CAS]-backed [MergeTree] tables:\n'
        '\n'
        '* `ADD STATISTICS [IF NOT EXISTS] ... TYPE ...`\n'
        '* `MODIFY STATISTICS ... TYPE ...`\n'
        '* `DROP STATISTICS [IF EXISTS] ...`\n'
        '* `CLEAR STATISTICS [IF EXISTS] ...`\n'
        '* `MATERIALIZE STATISTICS (ALL | [IF EXISTS] ...)`\n'
        '\n'
        'Metadata commands SHALL match non-CAS behavior. `MATERIALIZE STATISTICS`\n'
        'and `CLEAR STATISTICS` SHALL follow upstream mutation semantics.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.26'
)

RQ_SRS_048_CAS_MergeTree_Alter_Setting = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Alter.Setting',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support table-setting `ALTER TABLE` actions on\n'
        '[CAS]-backed [MergeTree] tables:\n'
        '\n'
        '* `MODIFY SETTING setting_name = value [, ...]`\n'
        '* `RESET SETTING setting_name [, ...]`\n'
        '\n'
        'These commands SHALL apply only to [MergeTree] table settings, matching\n'
        'non-CAS behavior.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.27'
)

RQ_SRS_048_CAS_MergeTree_Alter_Comment = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Alter.Comment',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `ALTER TABLE ... MODIFY COMMENT '...'` on\n"
        '[CAS]-backed [MergeTree] tables, including clearing the comment with an\n'
        'empty string. On `ReplicatedMergeTree`, comment changes MAY remain\n'
        'replica-local, matching upstream [MergeTree].\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.28'
)

RQ_SRS_048_CAS_MergeTree_Alter_ApplyDeletedMask = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Alter.ApplyDeletedMask',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support\n'
        '\n'
        '```sql\n'
        'ALTER TABLE [db.]table APPLY DELETED MASK [IN PARTITION partition_id]\n'
        '```\n'
        '\n'
        'on [CAS]-backed [MergeTree] tables as a mutation that physically removes\n'
        'rows marked by lightweight delete (`_row_exists = 0`), with the same\n'
        'logical outcome as on non-CAS storage.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.29'
)

RQ_SRS_048_CAS_MergeTree_Alter_ApplyPatches = Requirement(
    name='RQ.SRS-048.CAS.MergeTree.Alter.ApplyPatches',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support\n'
        '\n'
        '```sql\n'
        'ALTER TABLE [db.]table APPLY PATCHES [IN PARTITION partition_id]\n'
        '```\n'
        '\n'
        'on [CAS]-backed [MergeTree] tables as a mutation that materializes pending\n'
        'lightweight-update patch parts into data parts, with the same logical\n'
        'outcome as on non-CAS storage.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.30'
)

RQ_SRS_048_CAS_Partition_AlterAllowList = Requirement(
    name='RQ.SRS-048.CAS.Partition.AlterAllowList',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL allow the following partition commands on a [CAS] disk and\n'
        'SHALL reject unsupported partition commands fail-closed:\n'
        '\n'
        '* `DETACH PARTITION` / `DETACH PART`\n'
        '* `DROP PARTITION` / `DROP PART`\n'
        '* `DROP DETACHED PARTITION` / `DROP DETACHED PART`\n'
        '* `FORGET PARTITION`\n'
        '* `ATTACH PARTITION` / `ATTACH PART`\n'
        '* `REPLACE PARTITION` / `ATTACH PARTITION ... FROM`\n'
        '* `MOVE PARTITION` (including `MOVE PARTITION ... TO TABLE`)\n'
        '* `FETCH PARTITION` / `FETCH PART`\n'
        '* `FREEZE PARTITION` / `FREEZE`\n'
        '* `UNFREEZE PARTITION` / `UNFREEZE`\n'
        '\n'
        '`DROP` / `DETACH` / `ATTACH` / `ATTACH FROM` SHALL accept `PARTITION ALL`\n'
        'where upstream [MergeTree] does. Partition-scoped mutations\n'
        '(`CLEAR COLUMN` / `CLEAR INDEX`, `UPDATE` / `DELETE IN PARTITION`,\n'
        '`REWRITE PARTS`) are specified under the following requirements and are\n'
        'not limited to this allow-list when they use the ordinary mutation path.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.1'
)

RQ_SRS_048_CAS_Partition_Replace = Requirement(
    name='RQ.SRS-048.CAS.Partition.Replace',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ALTER TABLE ... REPLACE PARTITION ... FROM ...`\n'
        'between [MergeTree] tables on the same [CAS] pool with correct partition\n'
        'contents on the destination and without deleting the replaced partition from\n'
        'the source.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.2'
)

RQ_SRS_048_CAS_Partition_AttachFrom = Requirement(
    name='RQ.SRS-048.CAS.Partition.AttachFrom',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ALTER TABLE ... ATTACH PARTITION ... FROM ...`\n'
        'between [MergeTree] tables on the same [CAS] pool so that the destination gains\n'
        'the partition and the source retains it.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.3'
)

RQ_SRS_048_CAS_Partition_Attach = Requirement(
    name='RQ.SRS-048.CAS.Partition.Attach',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ALTER TABLE ... ATTACH PARTITION` /\n'
        '`ATTACH PART` of previously detached parts on a [CAS]-backed table so that\n'
        'attached data becomes readable and survives restart.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.4'
)

RQ_SRS_048_CAS_Partition_Detach = Requirement(
    name='RQ.SRS-048.CAS.Partition.Detach',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ALTER TABLE ... DETACH PARTITION` /\n'
        '`DETACH PART` on a [CAS]-backed table so that detached data is no longer\n'
        'queryable from the active table while remaining available under the detached\n'
        'namespace for later attach or drop.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.5'
)

RQ_SRS_048_CAS_Partition_DetachAttach = Requirement(
    name='RQ.SRS-048.CAS.Partition.DetachAttach',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `DETACH PARTITION` / `ATTACH PARTITION` round-trips\n'
        'on a [CAS]-backed [MergeTree] table without logical data loss.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.6'
)

RQ_SRS_048_CAS_Partition_MoveToTable = Requirement(
    name='RQ.SRS-048.CAS.Partition.MoveToTable',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ALTER TABLE ... MOVE PARTITION ... TO TABLE ...`\n'
        'between [MergeTree] tables on the same [CAS] pool so that the partition leaves\n'
        'the source and appears on the destination with unchanged contents.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.7'
)

RQ_SRS_048_CAS_Partition_Drop = Requirement(
    name='RQ.SRS-048.CAS.Partition.Drop',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ALTER TABLE ... DROP PARTITION` / `DROP PART` on a\n'
        '[CAS]-backed table. Dropped part refs SHALL be removed and their blobs /\n'
        'manifests SHALL become eligible for [GC] when no other ownership remains.\n'
        'Logical drop semantics SHALL match non-CAS [MergeTree] (including documented\n'
        'weak guarantees when `DROP PART` races a concurrent merge).\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.8'
)

RQ_SRS_048_CAS_Partition_DropDetached = Requirement(
    name='RQ.SRS-048.CAS.Partition.DropDetached',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ALTER TABLE ... DROP DETACHED PARTITION` /\n'
        '`DROP DETACHED PART` on a [CAS]-backed table when `allow_drop_detached` permits\n'
        'the command.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.9'
)

RQ_SRS_048_CAS_Partition_Forget = Requirement(
    name='RQ.SRS-048.CAS.Partition.Forget',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ALTER TABLE ... FORGET PARTITION` on\n'
        '`ReplicatedMergeTree` tables stored on [CAS]. The command manipulates Keeper\n'
        'partition metadata and SHALL NOT require rewriting or deleting [CAS] part blobs\n'
        'as part of the forget itself.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.10'
)

RQ_SRS_048_CAS_Partition_Fetch = Requirement(
    name='RQ.SRS-048.CAS.Partition.Fetch',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ALTER TABLE ... FETCH PARTITION` /\n'
        '`FETCH PART` (including fetch into detached) for `ReplicatedMergeTree` tables\n'
        'on a [CAS] disk. When the peer shares the same pool, fetch MAY use relink;\n'
        'otherwise it SHALL use ordinary byte fetch. Logical fetched data SHALL match\n'
        'the source.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.11'
)

RQ_SRS_048_CAS_Partition_Freeze = Requirement(
    name='RQ.SRS-048.CAS.Partition.Freeze',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ALTER TABLE ... FREEZE PARTITION` / `FREEZE` on a\n'
        '[CAS]-backed table by publishing shadow-namespace refs that share live blobs\n'
        '(no freeze-time byte copy of pool blobs), such that backup consumers can read\n'
        'frozen file bytes through the disk API. The shadow namespace SHALL be scoped\n'
        "under the creating server's `cas_server_root_id` so one server's `UNFREEZE`\n"
        "cannot reach another server's snapshots in the same pool.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.12'
)

RQ_SRS_048_CAS_Partition_Unfreeze = Requirement(
    name='RQ.SRS-048.CAS.Partition.Unfreeze',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ALTER TABLE ... UNFREEZE PARTITION` / `UNFREEZE` on\n'
        'a [CAS]-backed table by removing the corresponding shadow refs without deleting\n'
        'blobs still referenced by live table ownership.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.13'
)

RQ_SRS_048_CAS_Partition_Clone = Requirement(
    name='RQ.SRS-048.CAS.Partition.Clone',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support partition / part clone paths used by attach, replace,\n'
        'and freeze on [CAS] as ref publication (content-identical clones share blob\n'
        'identity) rather than requiring a full byte copy of already-present content.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.14'
)

RQ_SRS_048_CAS_Partition_ClearColumn = Requirement(
    name='RQ.SRS-048.CAS.Partition.ClearColumn',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support\n'
        '`ALTER TABLE ... CLEAR COLUMN ... IN PARTITION ...` on a [CAS]-backed\n'
        '[MergeTree] table, resetting the column in that partition to default\n'
        'values with the same logical outcome as on non-CAS storage.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.15'
)

RQ_SRS_048_CAS_Partition_ClearIndex = Requirement(
    name='RQ.SRS-048.CAS.Partition.ClearIndex',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support\n'
        '`ALTER TABLE ... CLEAR INDEX ... IN PARTITION ...` on a [CAS]-backed\n'
        '[MergeTree] table, removing skip-index files for that partition without\n'
        'dropping the index description, matching non-CAS behavior.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.16'
)

RQ_SRS_048_CAS_Partition_RewriteParts = Requirement(
    name='RQ.SRS-048.CAS.Partition.RewriteParts',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ALTER TABLE ... REWRITE PARTS` and\n'
        '`ALTER TABLE ... REWRITE PARTS IN PARTITION ...` on a [CAS]-backed\n'
        '[MergeTree] table, rewriting parts with current table settings and\n'
        'preserving logical table contents.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.17'
)

RQ_SRS_048_CAS_Partition_Update = Requirement(
    name='RQ.SRS-048.CAS.Partition.Update',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ALTER TABLE ... UPDATE ... IN PARTITION ...`\n'
        "(and `IN PARTITION ID '...'`) on a [CAS]-backed [MergeTree] table as a\n"
        'partition-scoped mutation, matching\n'
        '[RQ.SRS-048.CAS.MergeTree.Alter.Update](#rqsrs-048casmergetreealterupdate).\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.18'
)

RQ_SRS_048_CAS_Partition_Delete = Requirement(
    name='RQ.SRS-048.CAS.Partition.Delete',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ALTER TABLE ... DELETE IN PARTITION ...`\n'
        "(and `IN PARTITION ID '...'`) on a [CAS]-backed [MergeTree] table as a\n"
        'partition-scoped mutation, matching\n'
        '[RQ.SRS-048.CAS.MergeTree.Alter.Delete](#rqsrs-048casmergetreealterdelete).\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.19'
)

RQ_SRS_048_CAS_Partition_MoveToDisk = Requirement(
    name='RQ.SRS-048.CAS.Partition.MoveToDisk',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support\n'
        "`ALTER TABLE ... MOVE PARTITION|PART ... TO DISK|VOLUME '...'` on\n"
        '[CAS]-backed [MergeTree] tables when the destination is admitted by the\n'
        'table storage policy. This is the documented migration path onto and off\n'
        '[CAS] (including a cache-over-[CAS] disk named in the policy). Moving a\n'
        'partition off [CAS] SHALL make the abandoned blobs eligible for [GC]\n'
        'without deleting them synchronously. Commands that the partition\n'
        'allow-list does not admit SHALL fail closed.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.20'
)

RQ_SRS_048_CAS_Backup = Requirement(
    name='RQ.SRS-048.CAS.Backup',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `BACKUP` of [CAS]-backed [MergeTree] tables on Atomic\n'
        '(UUID) databases via the pointer-holding backup path, preserving logical table\n'
        'contents for a subsequent restore. This is ordinary [ClickHouse] `BACKUP`, not\n'
        'the unshipped native [CAS] snapshot / mirror design\n'
        '([RQ.SRS-048.CAS.Restrictions.Backup.NativeSnapshot](#rqsrs-048casrestrictionsbackupnativesnapshot)).\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.6.1'
)

RQ_SRS_048_CAS_Restore = Requirement(
    name='RQ.SRS-048.CAS.Restore',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `RESTORE` of [CAS]-backed [MergeTree] table backups\n'
        'produced through the supported backup path, restoring queryable logical contents\n'
        'equivalent to the backed-up table.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.6.2'
)

RQ_SRS_048_CAS_SharedPool = Requirement(
    name='RQ.SRS-048.CAS.SharedPool',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL allow multiple servers to mount one [CAS] pool concurrently\n'
        'when each server uses a distinct `cas_server_root_id`.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.7.1'
)

RQ_SRS_048_CAS_SharedPool_Deduplication = Requirement(
    name='RQ.SRS-048.CAS.SharedPool.Deduplication',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL deduplicate identical blob content across servers that share\n'
        'one pool so that writing the same bytes does not require storing a second pool\n'
        'copy of that blob.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.7.2'
)

RQ_SRS_048_CAS_SharedPool_IndependentRefs = Requirement(
    name='RQ.SRS-048.CAS.SharedPool.IndependentRefs',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL keep each server's refs independent under its\n"
        '`cas_server_root_id` even when those refs resolve to the same shared blobs.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.7.3'
)

RQ_SRS_048_CAS_SharedPool_NodeCrash = Requirement(
    name='RQ.SRS-048.CAS.SharedPool.NodeCrash',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL keep the shared pool and surviving servers consistent when\n'
        'one pool member process crashes or is killed, without corrupting surviving\n'
        "members' committed data.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='4.7.4'
)

RQ_SRS_048_CAS_Relink = Requirement(
    name='RQ.SRS-048.CAS.Relink',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support fetch-by-relink for `ReplicatedMergeTree` replicas\n'
        'that mount the same [CAS] pool: a receiving replica MAY publish a local ref to\n'
        "the sender's manifest instead of transferring all part bytes, when the relink\n"
        "protocol succeeds. The sender SHALL offer relink only when the receiver's\n"
        "advertised `cas_pool_uuid` equals the sender disk's pool uuid.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='4.8.1'
)

RQ_SRS_048_CAS_Relink_HappyPath = Requirement(
    name='RQ.SRS-048.CAS.Relink.HappyPath',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL complete the relink happy path by publishing the receiver\n'
        'precommit first, confirming the source still holds the offered manifest, then\n'
        "promoting the receiver's committed ref. Only a literal confirm-proven answer\n"
        'SHALL authorize promotion. Logical data SHALL be identical on both replicas\n'
        'without requiring a full byte copy of already-present blobs.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.8.2'
)

RQ_SRS_048_CAS_Relink_DetachedFetch = Requirement(
    name='RQ.SRS-048.CAS.Relink.DetachedFetch',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL use relink when fetching a part or partition into detached\n'
        'status on a same-pool replica (`FETCH PART` / `FETCH PARTITION` into detached),\n'
        'subject to the same pool-identity rules as ordinary fetch.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.8.3'
)

RQ_SRS_048_CAS_Relink_CrossPool_ByteFallback = Requirement(
    name='RQ.SRS-048.CAS.Relink.CrossPool.ByteFallback',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL fall back to ordinary byte fetch when sender and receiver do\n'
        'not share the same [CAS] `cas_pool_uuid` (or relink confirmation is unavailable),\n'
        'and SHALL not incorrectly claim a metadata-only relink in that case.\n'
        'Byte-fetched files SHALL still content-address and deduplicate on arrival.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.8.4'
)

RQ_SRS_048_CAS_Relink_AttachPartitionFrom = Requirement(
    name='RQ.SRS-048.CAS.Relink.AttachPartitionFrom',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `ATTACH PARTITION FROM` such that a subsequent\n'
        'replication queue fetch on a same-pool replica MAY relink rather than copy\n'
        'bytes, while preserving correct logical partition contents.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.8.5'
)

RQ_SRS_048_CAS_Relink_ReplacePartition = Requirement(
    name='RQ.SRS-048.CAS.Relink.ReplacePartition',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `REPLACE PARTITION` on a non-empty destination such\n'
        'that a subsequent same-pool replica queue fetch MAY relink, while preserving\n'
        'correct logical partition contents on all replicas.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.8.6'
)

RQ_SRS_048_CAS_Relink_VersionMix = Requirement(
    name='RQ.SRS-048.CAS.Relink.VersionMix',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL serve ordinary byte fetch to a peer that cannot participate\n'
        'in the relink confirm protocol (protocol version below the confirm promise,\n'
        'currently 11), instead of leaving that peer unable to obtain the part.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.8.7'
)

RQ_SRS_048_CAS_Relink_ConfirmRace = Requirement(
    name='RQ.SRS-048.CAS.Relink.ConfirmRace',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL refuse unsafe promotion when the source cannot prove it still\n'
        'holds the offered manifest (unproven, missing cookie, timeout, or transport\n'
        'error). The receiver SHALL throw and retry later and SHALL NOT promote or\n'
        'immediately re-request bytes from that same uncertain source.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.8.8'
)

RQ_SRS_048_CAS_Relink_StalledPublish = Requirement(
    name='RQ.SRS-048.CAS.Relink.StalledPublish',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL protect source blobs during a stalled publish and SHALL NOT\n'
        'commit a receiver ref when promotion cannot complete safely.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.8.9'
)

RQ_SRS_048_CAS_Relink_RecursionBrake = Requirement(
    name='RQ.SRS-048.CAS.Relink.RecursionBrake',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL bound relink recursion: a byte-fetch fallback SHALL re-invoke\n'
        'the fetch with relink disabled so the receiver stops advertising its pool uuid\n'
        'and the relink path cannot be entered twice for one fetch.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.8.10'
)

RQ_SRS_048_CAS_GC = Requirement(
    name='RQ.SRS-048.CAS.GC',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL provide background garbage collection for a [CAS] pool that\n'
        'reclaims objects no longer named by live ownership.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.9.1'
)

RQ_SRS_048_CAS_GC_NoLoss = Requirement(
    name='RQ.SRS-048.CAS.GC.NoLoss',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL NOT delete a blob or manifest while any committed reference\n'
        'or required ownership still names it. A dangling reference (live ref, missing\n'
        'object) SHALL be treated as a data-loss invariant violation.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.9.2'
)

RQ_SRS_048_CAS_GC_ReclaimAfterDrop = Requirement(
    name='RQ.SRS-048.CAS.GC.ReclaimAfterDrop',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL reclaim unreferenced blobs and part metadata after\n'
        '`DROP TABLE ... SYNC` (and equivalent removal of the last owners) once [GC]\n'
        'completes, returning the pool prefixes toward an empty / baseline state for\n'
        'that dropped ownership. Reclamation SHALL require at least two full [GC] rounds\n'
        'past condemnation (the grace period is measured in rounds, not acks); a single\n'
        'manual `SYSTEM CAS GC RUN` SHALL NOT finish physical delete by itself.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.9.3'
)

RQ_SRS_048_CAS_GC_Run = Requirement(
    name='RQ.SRS-048.CAS.GC.Run',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support a manual synchronous GC round via\n'
        '\n'
        '```sql\n'
        'SYSTEM CAS GC RUN [ON CLUSTER cluster_name] [disk_name];\n'
        '```\n'
        '\n'
        'When `disk_name` is omitted, one round SHALL run on every [CAS] disk on the\n'
        'node. A manual run SHALL execute even if `SYSTEM CAS GC STOP` has paused the\n'
        'background scheduler. The command SHALL return one row per disk it ran on\n'
        '(the `cas_gc_log` `Finish` shape).\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.9.4'
)

RQ_SRS_048_CAS_GC_Rebuild = Requirement(
    name='RQ.SRS-048.CAS.GC.Rebuild',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support reconstructing conservative GC baseline state via\n'
        '\n'
        '```sql\n'
        'SYSTEM CAS GC REBUILD [FORCE] [ON CLUSTER cluster_name] disk_name;\n'
        '```\n'
        '\n'
        'and/or offline `clickhouse-disks ... cas-gc-rebuild`. `disk_name` SHALL be\n'
        'required (no fan-out across every [CAS] disk). Rebuild SHALL refuse when\n'
        'existing `gc/state` looks healthy unless `FORCE` is given, and SHALL refuse\n'
        "(regardless of `FORCE`) when another GC leader holds the disk's lease.\n"
        'Rebuild SHALL write only the GC plane and SHALL fail closed rather than delete\n'
        'uncertain content; temporary over-protection (leaks) is preferred over data\n'
        'loss.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.9.5'
)

RQ_SRS_048_CAS_GC_Sharded = Requirement(
    name='RQ.SRS-048.CAS.GC.Sharded',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support sharded GC (`cas_gc_shards > 1`) such that GC work is\n'
        'partitioned across shard buckets, completion is sealed per generation, and\n'
        'reclaim remains free of dangle/loss under multi-replica pool use.\n'
        '`cas_gc_shards` SHALL be recorded in the pool at first lease acquire; a\n'
        'mismatching config SHALL be refused at mount.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.9.6'
)

RQ_SRS_048_CAS_GC_RefSnaplog = Requirement(
    name='RQ.SRS-048.CAS.GC.RefSnaplog',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL implement the snapshot+log ref protocol lifecycle so that\n'
        'after insert churn and table drop, unreclaimed objects become reclaimable and a\n'
        'read-only `cas-fsck` pass can report a clean pool for the inspected window.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.9.7'
)

RQ_SRS_048_CAS_GC_StopStart = Requirement(
    name='RQ.SRS-048.CAS.GC.StopStart',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support pausing and resuming the background GC scheduler on\n'
        'one disk without affecting reads or writes:\n'
        '\n'
        '```sql\n'
        'SYSTEM CAS GC STOP [ON CLUSTER cluster_name] disk_name;\n'
        'SYSTEM CAS GC START [ON CLUSTER cluster_name] disk_name;\n'
        '```\n'
        '\n'
        '`disk_name` SHALL be required. `STOP` SHALL be idempotent, SHALL stop in place\n'
        '(the same scheduler instance resumes on `START`), and SHALL NOT stop a manual\n'
        '`SYSTEM CAS GC RUN`. `START` SHALL NOT automatically restore GC leadership.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.9.8'
)

RQ_SRS_048_CAS_GC_DryRun = Requirement(
    name='RQ.SRS-048.CAS.GC.DryRun',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support a write-free preview of the next GC round's deletes\n"
        'via `clickhouse-disks ... cas-gc-dryrun` against a disk opened read-only. The\n'
        'preview SHALL NOT claim a live mount lease. Away from quiescence the preview\n'
        'MAY over-report; its output MUST NOT be used as a delete source.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.9.9'
)

RQ_SRS_048_CAS_Fsck = Requirement(
    name='RQ.SRS-048.CAS.Fsck',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL provide an offline filesystem check\n'
        '(`clickhouse-disks ... cas-fsck [--detail]`) that classifies reachable,\n'
        'dangling, pending-gc, awaiting-gc, and related object states for a [CAS] pool\n'
        'without mutating the pool. The tool SHALL open the disk read-only and MUST NOT\n'
        "claim a live server's mount. `dangling` SHALL be the class that means data\n"
        'loss; `unreachable` / `pending_gc` / `awaiting_gc` SHALL mean objects still\n'
        'moving through the condemn / graduate / delete pipeline. `--detail` SHALL be\n'
        'the per-object listing; the SQL form is summary-only.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.9.10'
)

RQ_SRS_048_CAS_Fsck_Online = Requirement(
    name='RQ.SRS-048.CAS.Fsck.Online',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support an online consistency check against a running,\n'
        'mounted [CAS] disk via\n'
        '\n'
        '```sql\n'
        'SYSTEM CAS FSCK [ON CLUSTER cluster_name] disk_name;\n'
        '```\n'
        '\n'
        '`disk_name` SHALL be required. The scan SHALL re-validate findings against a\n'
        'fresh authoritative read and SHALL need no quiesce. The command SHALL return\n'
        'one summary row including at least `reachable`, `dangling`, `unreachable`,\n'
        '`pending_gc`, and `awaiting_gc`.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.9.11'
)

RQ_SRS_048_CAS_DropPoolMember = Requirement(
    name='RQ.SRS-048.CAS.DropPoolMember',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support decommissioning a dead pool member via\n'
        '\n'
        '```sql\n'
        "SYSTEM CAS DROP POOL MEMBER 'server_root_id' FROM DISK 'disk_name' [ON CLUSTER cluster_name];\n"
        '```\n'
        '\n'
        'and the offline twin `clickhouse-disks ... cas-drop-member <server_root_id>`.\n'
        'The command SHALL refuse immediately if the member is still alive, SHALL fence\n'
        "that `cas_server_root_id` from writing again, SHALL drop the member's table\n"
        'namespaces, and SHALL retire the mount slot only after drains are confirmed.\n'
        'It SHALL emit ordinary ref-edge deltas rather than inventing GC transitions,\n'
        'and SHALL NOT synchronously reclaim shared blob content. The operation SHALL\n'
        "be resumable. After `slot_removed = true` with no warnings, the member's\n"
        '`cas_server_root_id` SHALL no longer appear in `system.cas_mounts` on any peer.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.10.1'
)

RQ_SRS_048_CAS_DropPoolMember_ReadonlyRejected = Requirement(
    name='RQ.SRS-048.CAS.DropPoolMember.ReadonlyRejected',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL reject the SQL `SYSTEM CAS DROP POOL MEMBER` command against\n'
        'a read-only [CAS] disk. The offline `cas-drop-member` tool SHALL open the disk\n'
        "read-only and MUST NOT claim a live server's mount (the pool-admin claim\n"
        'happens internally).\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.10.2'
)

RQ_SRS_048_CAS_Forget = Requirement(
    name='RQ.SRS-048.CAS.Forget',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support a node-local assertion that a [CAS] disk is\n'
        'permanently gone via\n'
        '\n'
        '```sql\n'
        'SYSTEM CAS FORGET [ON CLUSTER cluster_name] disk_name;\n'
        '```\n'
        '\n'
        '`FORGET` SHALL work on a disk that is not live. It is an assertion, not a proof\n'
        'of erasure: the disk SHALL stay registered, further store-class access SHALL\n'
        'return a typed error, and a server restart SHALL re-register the name. This is\n'
        "distinct from `SYSTEM CAS DROP POOL MEMBER`, which retires one pool member's\n"
        'identity across the whole shared pool.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.10.3'
)

RQ_SRS_048_CAS_Tools = Requirement(
    name='RQ.SRS-048.CAS.Tools',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL provide `clickhouse-disks` commands `cas-fsck`, `cas-inspect`,\n'
        '`cas-gc-dryrun`, `cas-gc-rebuild`, and `cas-drop-member`. All five SHALL require\n'
        "the disk to be opened read-only and MUST NOT claim a live server's mount.\n"
        '`cas-inspect` SHALL decode one raw object-storage key to JSON.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.10.4'
)

RQ_SRS_048_CAS_Fault_LostPartRecovery = Requirement(
    name='RQ.SRS-048.CAS.Fault.LostPartRecovery',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL heal via ordinary lost-part recovery when a replica is\n'
        'terminated after ZooKeeper multi / coordination commit but before durable [CAS]\n'
        'publish completes, without requiring a fixed sync timeout as the sole success\n'
        'oracle.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.11.1'
)

RQ_SRS_048_CAS_Fault_LazyLoad_S3Outage = Requirement(
    name='RQ.SRS-048.CAS.Fault.LazyLoad.S3Outage',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL NOT automatically requeue a lazily loaded [CAS] table's\n"
        'AsyncLoader job after a transient object-store error during first build. The\n'
        'job MAY remain `FAILED`; operators SHALL recover by restarting the server or\n'
        'issuing a fresh load for the table. This matches the documented one-shot\n'
        'AsyncLoader design (not a [CAS]-specific retry path).\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.11.2'
)

RQ_SRS_048_CAS_Fault_FailClosed = Requirement(
    name='RQ.SRS-048.CAS.Fault.FailClosed',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL fail closed under ambiguity on the write / promote / delete\n'
        'paths: an operation that may have landed MUST NOT be treated as one that did\n'
        'not, and uncertain deletes MUST be suppressed rather than assumed safe.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.11.3'
)

RQ_SRS_048_CAS_Cache = Requirement(
    name='RQ.SRS-048.CAS.Cache',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support composing a filesystem cache disk over a [CAS]\n'
        'object-storage disk. Cache-over-[CAS] is the supported wrapper shape (see\n'
        '[RQ.SRS-048.CAS.Disk.Configuration](#rqsrs-048casdiskconfiguration)).\n'
        '`system.cas_mounts` SHALL list a row per configured disk name, so a cache\n'
        'layered in front MAY appear twice under the same `cas_server_root_id`.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.12.1'
)

RQ_SRS_048_CAS_Cache_Hits = Requirement(
    name='RQ.SRS-048.CAS.Cache.Hits',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL serve repeated reads of the same [CAS] objects from the\n'
        'local cache when cache-over-CAS is configured, without changing logical query\n'
        'results.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.12.2'
)

RQ_SRS_048_CAS_Observability = Requirement(
    name='RQ.SRS-048.CAS.Observability',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL expose [CAS] operational state through documented system\n'
        'tables, `CAS*` / `CASGC*` `ProfileEvents`, and the `SYSTEM CAS` command\n'
        'surface so operators can observe pool membership, GC progress, and related\n'
        'health signals.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.13.1'
)

RQ_SRS_048_CAS_Observability_SystemTables = Requirement(
    name='RQ.SRS-048.CAS.Observability.SystemTables',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL provide:\n'
        '\n'
        '* `system.cas_mounts` — live per-mount view of every `cas_server_root_id` in\n'
        '  the pool (not only the local server), including lease state and process-local\n'
        '  GC-health columns (`is_leader` and related fields `NULL` on peer rows).\n'
        '* `system.cas_gc_log` — per-round `Start` / `Finish` / `Phase` rows correlated\n'
        '  by `round_id`, for both scheduled and manual (`SYSTEM CAS GC RUN`) rounds.\n'
        '* `system.cas_log` — per-decision event log (blob puts, dedup adoptions, ref\n'
        '  transitions, GC retire decisions, dangling-access findings).\n'
        '\n'
        '`system.cas_log` and `system.cas_gc_log` SHALL be created when the matching\n'
        'server settings are specified (enabled by default in the shipped `config.xml`).\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.13.2'
)

RQ_SRS_048_CAS_Observability_ProfileEvents = Requirement(
    name='RQ.SRS-048.CAS.Observability.ProfileEvents',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL expose [CAS]-related `ProfileEvents` under the uppercase\n'
        '`CAS` / `CASGC` prefix (blob, manifest, ref, mount-renewal/remount, and GC\n'
        'counters) so operators can attribute pool I/O and diagnose mount-lease\n'
        'recovery without reading server logs alone.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.13.3'
)

RQ_SRS_048_CAS_Access = Requirement(
    name='RQ.SRS-048.CAS.Access',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL enforce a distinct `GLOBAL SYSTEM` privilege for each\n'
        '`SYSTEM CAS` verb: `GC RUN`, `GC REBUILD`, `GC STOP`, `GC START`, `FSCK`,\n'
        '`FORGET`, and `DROP POOL MEMBER`. A read-only fsck grant SHALL be grantable\n'
        'without the destructive verbs.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.13.4'
)

RQ_SRS_048_CAS_Restrictions_BackendCapabilities = Requirement(
    name='RQ.SRS-048.CAS.Restrictions.BackendCapabilities',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL require an object store that provides the capabilities\n'
        'needed by the [CAS] mount and delete protocols, checked by a capability probe\n'
        'at every writable mount. Required capabilities include read-after-write,\n'
        'conditional create (`If-None-Match: *`) for manifests and control objects,\n'
        'conditional overwrite (`If-Match`) for mount leases and `gc/state`,\n'
        'unconditional blob publication, exact-token delete, ranged `GET`, and\n'
        'resumable `LIST`. Bucket versioning SHALL be disabled (a versioned or\n'
        'unanswerable versioning probe SHALL refuse a writable generation-token mount).\n'
        'Object soft-delete MUST be disabled by the operator (not verified at mount).\n'
        'When those capabilities are absent, mount SHALL fail closed rather than\n'
        'silently run an unsafe configuration. `skip_access_check = true` SHALL be\n'
        'refused on a writable generation-token (GCS) disk.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.14.1'
)

RQ_SRS_048_CAS_Restrictions_ZeroCopy = Requirement(
    name='RQ.SRS-048.CAS.Restrictions.ZeroCopy',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL NOT use classic zero-copy replication\n'
        '(`allow_remote_fs_zero_copy_replication`) as the [CAS] sharing mechanism.\n'
        'Same-pool sharing uses [CAS] refs and fetch-by-relink instead.\n'
        '`supportZeroCopyReplication` SHALL report false for content-addressed disks.\n'
        '[CAS] SHALL coexist with zero-copy: disks that do not set `metadata_type = cas`\n'
        'keep their existing zero-copy behavior.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.14.2'
)

RQ_SRS_048_CAS_Restrictions_UniqueKey = Requirement(
    name='RQ.SRS-048.CAS.Restrictions.UniqueKey',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL reject UNIQUE KEY / upsert [MergeTree] tables on non-local\n'
        'disks, which includes [CAS]. UNIQUE KEY on [CAS] is out of scope while that\n'
        'upstream fence remains.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.14.3'
)

RQ_SRS_048_CAS_Restrictions_NonMergeTree = Requirement(
    name='RQ.SRS-048.CAS.Restrictions.NonMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[CAS] is intended for the [MergeTree] engine family. Using a [CAS] disk as\n'
        'generic storage for non-MergeTree engines, temporary-files disks, dictionary\n'
        'SSD-cache backing, or Distributed spool is not a supported configuration and\n'
        'MAY fail with `NOT_IMPLEMENTED` or an equivalent error.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.14.4'
)

RQ_SRS_048_CAS_Restrictions_Backup_TempHardLinks = Requirement(
    name='RQ.SRS-048.CAS.Restrictions.Backup.TempHardLinks',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL reject the temporary-hard-link `BACKUP` path on a [CAS] disk\n'
        '(Ordinary / non-UUID databases that require that path). Operators SHALL use an\n'
        'Atomic database so backup uses the pointer-holding path.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.14.5'
)

RQ_SRS_048_CAS_Restrictions_Backup_NativeSnapshot = Requirement(
    name='RQ.SRS-048.CAS.Restrictions.Backup.NativeSnapshot',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'The git-shaped [CAS] `snapshot` / `mirror` / `fetch` / `restore` design is\n'
        'approved but not implemented and SHALL NOT be treated as wired into the\n'
        '`BACKUP` / `RESTORE` SQL surface. Ordinary pointer-holding `BACKUP` /\n'
        '`RESTORE` of [CAS] tables remains\n'
        '[RQ.SRS-048.CAS.Backup](#rqsrs-048casbackup) /\n'
        '[RQ.SRS-048.CAS.Restore](#rqsrs-048casrestore).\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.14.6'
)

RQ_SRS_048_CAS_Restrictions_Encryption = Requirement(
    name='RQ.SRS-048.CAS.Restrictions.Encryption',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'An `encrypted` disk wrapping a [CAS] disk is not supported. `CREATE TABLE` on\n'
        'such a disk MAY succeed; the first `INSERT` SHALL fail (documented as\n'
        '`Autocommit writes are not supported for content part files on a\n'
        'content-addressed disk`). Cache-over-[CAS] is the supported wrapper; encryption\n'
        'at rest currently has to come from the object store.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.14.7'
)

RQ_SRS_048_CAS_Restrictions_Azure = Requirement(
    name='RQ.SRS-048.CAS.Restrictions.Azure',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Azure Blob as a [CAS] backend is not supported. Azure's REST API documents\n"
        'equivalent conditional headers, but ClickHouse does not wire a [CAS]\n'
        'conditional dialect for Azure, and the capability probe does not validate it.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.14.8'
)

RQ_SRS_048_CAS_Restrictions_GCS = Requirement(
    name='RQ.SRS-048.CAS.Restrictions.GCS',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Google Cloud Storage's generation-token implementation is present, but the\n"
        'credentialed real-GCS release gate is pending. Suites against a fake GCS\n'
        "service SHALL NOT be treated as proof of Google's multipart, native-copy, or\n"
        'exact-delete wire behavior.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.14.9'
)

SRS_048_ClickHouse_Content_Addressed_Storage = Specification(
    name='SRS-048 ClickHouse Content-Addressed Storage',
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
        Heading(name='Revision History', level=1, num='1'),
        Heading(name='Introduction', level=1, num='2'),
        Heading(name='Terminology', level=1, num='3'),
        Heading(name='Requirements', level=1, num='4'),
        Heading(name='Generic', level=2, num='4.1'),
        Heading(name='RQ.SRS-048.CAS', level=3, num='4.1.1'),
        Heading(name='RQ.SRS-048.CAS.NotATableEngine', level=3, num='4.1.2'),
        Heading(name='Configuration', level=2, num='4.2'),
        Heading(name='RQ.SRS-048.CAS.Disk.Configuration', level=3, num='4.2.1'),
        Heading(name='RQ.SRS-048.CAS.Disk.MetadataType', level=3, num='4.2.2'),
        Heading(name='RQ.SRS-048.CAS.Disk.ServerRootId', level=3, num='4.2.3'),
        Heading(name='RQ.SRS-048.CAS.Disk.ServerRootId.Unique', level=3, num='4.2.4'),
        Heading(name='RQ.SRS-048.CAS.Disk.Pool', level=3, num='4.2.5'),
        Heading(name='RQ.SRS-048.CAS.Disk.Inline', level=3, num='4.2.6'),
        Heading(name='RQ.SRS-048.CAS.Policy', level=3, num='4.2.7'),
        Heading(name='RQ.SRS-048.CAS.Disk.Settings', level=3, num='4.2.8'),
        Heading(name='RQ.SRS-048.CAS.Disk.BlobHash', level=3, num='4.2.9'),
        Heading(name='RQ.SRS-048.CAS.Disk.Backends', level=3, num='4.2.10'),
        Heading(name='Object Model', level=2, num='4.3'),
        Heading(name='RQ.SRS-048.CAS.ObjectModel', level=3, num='4.3.1'),
        Heading(name='RQ.SRS-048.CAS.ObjectModel.Blobs', level=3, num='4.3.2'),
        Heading(name='RQ.SRS-048.CAS.ObjectModel.Manifests', level=3, num='4.3.3'),
        Heading(name='RQ.SRS-048.CAS.ObjectModel.Refs', level=3, num='4.3.4'),
        Heading(name='RQ.SRS-048.CAS.ObjectModel.Immutability', level=3, num='4.3.5'),
        Heading(name='MergeTree Compatibility', level=2, num='4.4'),
        Heading(name='RQ.SRS-048.CAS.MergeTree', level=3, num='4.4.1'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Transparency', level=3, num='4.4.2'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Engines', level=3, num='4.4.3'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.InsertSelect', level=3, num='4.4.4'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Merge', level=3, num='4.4.5'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Replicated', level=3, num='4.4.6'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.PartTypes', level=3, num='4.4.7'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Alter.Schema', level=3, num='4.4.8'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Mutations', level=3, num='4.4.9'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.LightweightDelete', level=3, num='4.4.10'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.PatchParts', level=3, num='4.4.11'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Projections', level=3, num='4.4.12'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.TTL', level=3, num='4.4.13'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Transactions', level=3, num='4.4.14'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.RestartDurability', level=3, num='4.4.15'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Alter', level=3, num='4.4.16'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Alter.Column', level=3, num='4.4.17'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Alter.Update', level=3, num='4.4.18'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Alter.Delete', level=3, num='4.4.19'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Alter.OrderBy', level=3, num='4.4.20'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Alter.SampleBy', level=3, num='4.4.21'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Alter.Index', level=3, num='4.4.22'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Alter.Projection', level=3, num='4.4.23'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Alter.Constraint', level=3, num='4.4.24'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Alter.TTL', level=3, num='4.4.25'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Alter.Statistics', level=3, num='4.4.26'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Alter.Setting', level=3, num='4.4.27'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Alter.Comment', level=3, num='4.4.28'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Alter.ApplyDeletedMask', level=3, num='4.4.29'),
        Heading(name='RQ.SRS-048.CAS.MergeTree.Alter.ApplyPatches', level=3, num='4.4.30'),
        Heading(name='Partition And Part Operations', level=2, num='4.5'),
        Heading(name='RQ.SRS-048.CAS.Partition.AlterAllowList', level=3, num='4.5.1'),
        Heading(name='RQ.SRS-048.CAS.Partition.Replace', level=3, num='4.5.2'),
        Heading(name='RQ.SRS-048.CAS.Partition.AttachFrom', level=3, num='4.5.3'),
        Heading(name='RQ.SRS-048.CAS.Partition.Attach', level=3, num='4.5.4'),
        Heading(name='RQ.SRS-048.CAS.Partition.Detach', level=3, num='4.5.5'),
        Heading(name='RQ.SRS-048.CAS.Partition.DetachAttach', level=3, num='4.5.6'),
        Heading(name='RQ.SRS-048.CAS.Partition.MoveToTable', level=3, num='4.5.7'),
        Heading(name='RQ.SRS-048.CAS.Partition.Drop', level=3, num='4.5.8'),
        Heading(name='RQ.SRS-048.CAS.Partition.DropDetached', level=3, num='4.5.9'),
        Heading(name='RQ.SRS-048.CAS.Partition.Forget', level=3, num='4.5.10'),
        Heading(name='RQ.SRS-048.CAS.Partition.Fetch', level=3, num='4.5.11'),
        Heading(name='RQ.SRS-048.CAS.Partition.Freeze', level=3, num='4.5.12'),
        Heading(name='RQ.SRS-048.CAS.Partition.Unfreeze', level=3, num='4.5.13'),
        Heading(name='RQ.SRS-048.CAS.Partition.Clone', level=3, num='4.5.14'),
        Heading(name='RQ.SRS-048.CAS.Partition.ClearColumn', level=3, num='4.5.15'),
        Heading(name='RQ.SRS-048.CAS.Partition.ClearIndex', level=3, num='4.5.16'),
        Heading(name='RQ.SRS-048.CAS.Partition.RewriteParts', level=3, num='4.5.17'),
        Heading(name='RQ.SRS-048.CAS.Partition.Update', level=3, num='4.5.18'),
        Heading(name='RQ.SRS-048.CAS.Partition.Delete', level=3, num='4.5.19'),
        Heading(name='RQ.SRS-048.CAS.Partition.MoveToDisk', level=3, num='4.5.20'),
        Heading(name='Backup And Restore', level=2, num='4.6'),
        Heading(name='RQ.SRS-048.CAS.Backup', level=3, num='4.6.1'),
        Heading(name='RQ.SRS-048.CAS.Restore', level=3, num='4.6.2'),
        Heading(name='Shared Pool', level=2, num='4.7'),
        Heading(name='RQ.SRS-048.CAS.SharedPool', level=3, num='4.7.1'),
        Heading(name='RQ.SRS-048.CAS.SharedPool.Deduplication', level=3, num='4.7.2'),
        Heading(name='RQ.SRS-048.CAS.SharedPool.IndependentRefs', level=3, num='4.7.3'),
        Heading(name='RQ.SRS-048.CAS.SharedPool.NodeCrash', level=3, num='4.7.4'),
        Heading(name='Replication Relink', level=2, num='4.8'),
        Heading(name='RQ.SRS-048.CAS.Relink', level=3, num='4.8.1'),
        Heading(name='RQ.SRS-048.CAS.Relink.HappyPath', level=3, num='4.8.2'),
        Heading(name='RQ.SRS-048.CAS.Relink.DetachedFetch', level=3, num='4.8.3'),
        Heading(name='RQ.SRS-048.CAS.Relink.CrossPool.ByteFallback', level=3, num='4.8.4'),
        Heading(name='RQ.SRS-048.CAS.Relink.AttachPartitionFrom', level=3, num='4.8.5'),
        Heading(name='RQ.SRS-048.CAS.Relink.ReplacePartition', level=3, num='4.8.6'),
        Heading(name='RQ.SRS-048.CAS.Relink.VersionMix', level=3, num='4.8.7'),
        Heading(name='RQ.SRS-048.CAS.Relink.ConfirmRace', level=3, num='4.8.8'),
        Heading(name='RQ.SRS-048.CAS.Relink.StalledPublish', level=3, num='4.8.9'),
        Heading(name='RQ.SRS-048.CAS.Relink.RecursionBrake', level=3, num='4.8.10'),
        Heading(name='Garbage Collection', level=2, num='4.9'),
        Heading(name='RQ.SRS-048.CAS.GC', level=3, num='4.9.1'),
        Heading(name='RQ.SRS-048.CAS.GC.NoLoss', level=3, num='4.9.2'),
        Heading(name='RQ.SRS-048.CAS.GC.ReclaimAfterDrop', level=3, num='4.9.3'),
        Heading(name='RQ.SRS-048.CAS.GC.Run', level=3, num='4.9.4'),
        Heading(name='RQ.SRS-048.CAS.GC.Rebuild', level=3, num='4.9.5'),
        Heading(name='RQ.SRS-048.CAS.GC.Sharded', level=3, num='4.9.6'),
        Heading(name='RQ.SRS-048.CAS.GC.RefSnaplog', level=3, num='4.9.7'),
        Heading(name='RQ.SRS-048.CAS.GC.StopStart', level=3, num='4.9.8'),
        Heading(name='RQ.SRS-048.CAS.GC.DryRun', level=3, num='4.9.9'),
        Heading(name='RQ.SRS-048.CAS.Fsck', level=3, num='4.9.10'),
        Heading(name='RQ.SRS-048.CAS.Fsck.Online', level=3, num='4.9.11'),
        Heading(name='Day-2 Operations', level=2, num='4.10'),
        Heading(name='RQ.SRS-048.CAS.DropPoolMember', level=3, num='4.10.1'),
        Heading(name='RQ.SRS-048.CAS.DropPoolMember.ReadonlyRejected', level=3, num='4.10.2'),
        Heading(name='RQ.SRS-048.CAS.Forget', level=3, num='4.10.3'),
        Heading(name='RQ.SRS-048.CAS.Tools', level=3, num='4.10.4'),
        Heading(name='Fault Recovery', level=2, num='4.11'),
        Heading(name='RQ.SRS-048.CAS.Fault.LostPartRecovery', level=3, num='4.11.1'),
        Heading(name='RQ.SRS-048.CAS.Fault.LazyLoad.S3Outage', level=3, num='4.11.2'),
        Heading(name='RQ.SRS-048.CAS.Fault.FailClosed', level=3, num='4.11.3'),
        Heading(name='Cache', level=2, num='4.12'),
        Heading(name='RQ.SRS-048.CAS.Cache', level=3, num='4.12.1'),
        Heading(name='RQ.SRS-048.CAS.Cache.Hits', level=3, num='4.12.2'),
        Heading(name='Observability And Access', level=2, num='4.13'),
        Heading(name='RQ.SRS-048.CAS.Observability', level=3, num='4.13.1'),
        Heading(name='RQ.SRS-048.CAS.Observability.SystemTables', level=3, num='4.13.2'),
        Heading(name='RQ.SRS-048.CAS.Observability.ProfileEvents', level=3, num='4.13.3'),
        Heading(name='RQ.SRS-048.CAS.Access', level=3, num='4.13.4'),
        Heading(name='Restrictions And Non-Goals', level=2, num='4.14'),
        Heading(name='RQ.SRS-048.CAS.Restrictions.BackendCapabilities', level=3, num='4.14.1'),
        Heading(name='RQ.SRS-048.CAS.Restrictions.ZeroCopy', level=3, num='4.14.2'),
        Heading(name='RQ.SRS-048.CAS.Restrictions.UniqueKey', level=3, num='4.14.3'),
        Heading(name='RQ.SRS-048.CAS.Restrictions.NonMergeTree', level=3, num='4.14.4'),
        Heading(name='RQ.SRS-048.CAS.Restrictions.Backup.TempHardLinks', level=3, num='4.14.5'),
        Heading(name='RQ.SRS-048.CAS.Restrictions.Backup.NativeSnapshot', level=3, num='4.14.6'),
        Heading(name='RQ.SRS-048.CAS.Restrictions.Encryption', level=3, num='4.14.7'),
        Heading(name='RQ.SRS-048.CAS.Restrictions.Azure', level=3, num='4.14.8'),
        Heading(name='RQ.SRS-048.CAS.Restrictions.GCS', level=3, num='4.14.9'),
        Heading(name='References', level=1, num='5'),
        ),
    requirements=(
        RQ_SRS_048_CAS,
        RQ_SRS_048_CAS_NotATableEngine,
        RQ_SRS_048_CAS_Disk_Configuration,
        RQ_SRS_048_CAS_Disk_MetadataType,
        RQ_SRS_048_CAS_Disk_ServerRootId,
        RQ_SRS_048_CAS_Disk_ServerRootId_Unique,
        RQ_SRS_048_CAS_Disk_Pool,
        RQ_SRS_048_CAS_Disk_Inline,
        RQ_SRS_048_CAS_Policy,
        RQ_SRS_048_CAS_Disk_Settings,
        RQ_SRS_048_CAS_Disk_BlobHash,
        RQ_SRS_048_CAS_Disk_Backends,
        RQ_SRS_048_CAS_ObjectModel,
        RQ_SRS_048_CAS_ObjectModel_Blobs,
        RQ_SRS_048_CAS_ObjectModel_Manifests,
        RQ_SRS_048_CAS_ObjectModel_Refs,
        RQ_SRS_048_CAS_ObjectModel_Immutability,
        RQ_SRS_048_CAS_MergeTree,
        RQ_SRS_048_CAS_MergeTree_Transparency,
        RQ_SRS_048_CAS_MergeTree_Engines,
        RQ_SRS_048_CAS_MergeTree_InsertSelect,
        RQ_SRS_048_CAS_MergeTree_Merge,
        RQ_SRS_048_CAS_MergeTree_Replicated,
        RQ_SRS_048_CAS_MergeTree_PartTypes,
        RQ_SRS_048_CAS_MergeTree_Alter_Schema,
        RQ_SRS_048_CAS_MergeTree_Mutations,
        RQ_SRS_048_CAS_MergeTree_LightweightDelete,
        RQ_SRS_048_CAS_MergeTree_PatchParts,
        RQ_SRS_048_CAS_MergeTree_Projections,
        RQ_SRS_048_CAS_MergeTree_TTL,
        RQ_SRS_048_CAS_MergeTree_Transactions,
        RQ_SRS_048_CAS_MergeTree_RestartDurability,
        RQ_SRS_048_CAS_MergeTree_Alter,
        RQ_SRS_048_CAS_MergeTree_Alter_Column,
        RQ_SRS_048_CAS_MergeTree_Alter_Update,
        RQ_SRS_048_CAS_MergeTree_Alter_Delete,
        RQ_SRS_048_CAS_MergeTree_Alter_OrderBy,
        RQ_SRS_048_CAS_MergeTree_Alter_SampleBy,
        RQ_SRS_048_CAS_MergeTree_Alter_Index,
        RQ_SRS_048_CAS_MergeTree_Alter_Projection,
        RQ_SRS_048_CAS_MergeTree_Alter_Constraint,
        RQ_SRS_048_CAS_MergeTree_Alter_TTL,
        RQ_SRS_048_CAS_MergeTree_Alter_Statistics,
        RQ_SRS_048_CAS_MergeTree_Alter_Setting,
        RQ_SRS_048_CAS_MergeTree_Alter_Comment,
        RQ_SRS_048_CAS_MergeTree_Alter_ApplyDeletedMask,
        RQ_SRS_048_CAS_MergeTree_Alter_ApplyPatches,
        RQ_SRS_048_CAS_Partition_AlterAllowList,
        RQ_SRS_048_CAS_Partition_Replace,
        RQ_SRS_048_CAS_Partition_AttachFrom,
        RQ_SRS_048_CAS_Partition_Attach,
        RQ_SRS_048_CAS_Partition_Detach,
        RQ_SRS_048_CAS_Partition_DetachAttach,
        RQ_SRS_048_CAS_Partition_MoveToTable,
        RQ_SRS_048_CAS_Partition_Drop,
        RQ_SRS_048_CAS_Partition_DropDetached,
        RQ_SRS_048_CAS_Partition_Forget,
        RQ_SRS_048_CAS_Partition_Fetch,
        RQ_SRS_048_CAS_Partition_Freeze,
        RQ_SRS_048_CAS_Partition_Unfreeze,
        RQ_SRS_048_CAS_Partition_Clone,
        RQ_SRS_048_CAS_Partition_ClearColumn,
        RQ_SRS_048_CAS_Partition_ClearIndex,
        RQ_SRS_048_CAS_Partition_RewriteParts,
        RQ_SRS_048_CAS_Partition_Update,
        RQ_SRS_048_CAS_Partition_Delete,
        RQ_SRS_048_CAS_Partition_MoveToDisk,
        RQ_SRS_048_CAS_Backup,
        RQ_SRS_048_CAS_Restore,
        RQ_SRS_048_CAS_SharedPool,
        RQ_SRS_048_CAS_SharedPool_Deduplication,
        RQ_SRS_048_CAS_SharedPool_IndependentRefs,
        RQ_SRS_048_CAS_SharedPool_NodeCrash,
        RQ_SRS_048_CAS_Relink,
        RQ_SRS_048_CAS_Relink_HappyPath,
        RQ_SRS_048_CAS_Relink_DetachedFetch,
        RQ_SRS_048_CAS_Relink_CrossPool_ByteFallback,
        RQ_SRS_048_CAS_Relink_AttachPartitionFrom,
        RQ_SRS_048_CAS_Relink_ReplacePartition,
        RQ_SRS_048_CAS_Relink_VersionMix,
        RQ_SRS_048_CAS_Relink_ConfirmRace,
        RQ_SRS_048_CAS_Relink_StalledPublish,
        RQ_SRS_048_CAS_Relink_RecursionBrake,
        RQ_SRS_048_CAS_GC,
        RQ_SRS_048_CAS_GC_NoLoss,
        RQ_SRS_048_CAS_GC_ReclaimAfterDrop,
        RQ_SRS_048_CAS_GC_Run,
        RQ_SRS_048_CAS_GC_Rebuild,
        RQ_SRS_048_CAS_GC_Sharded,
        RQ_SRS_048_CAS_GC_RefSnaplog,
        RQ_SRS_048_CAS_GC_StopStart,
        RQ_SRS_048_CAS_GC_DryRun,
        RQ_SRS_048_CAS_Fsck,
        RQ_SRS_048_CAS_Fsck_Online,
        RQ_SRS_048_CAS_DropPoolMember,
        RQ_SRS_048_CAS_DropPoolMember_ReadonlyRejected,
        RQ_SRS_048_CAS_Forget,
        RQ_SRS_048_CAS_Tools,
        RQ_SRS_048_CAS_Fault_LostPartRecovery,
        RQ_SRS_048_CAS_Fault_LazyLoad_S3Outage,
        RQ_SRS_048_CAS_Fault_FailClosed,
        RQ_SRS_048_CAS_Cache,
        RQ_SRS_048_CAS_Cache_Hits,
        RQ_SRS_048_CAS_Observability,
        RQ_SRS_048_CAS_Observability_SystemTables,
        RQ_SRS_048_CAS_Observability_ProfileEvents,
        RQ_SRS_048_CAS_Access,
        RQ_SRS_048_CAS_Restrictions_BackendCapabilities,
        RQ_SRS_048_CAS_Restrictions_ZeroCopy,
        RQ_SRS_048_CAS_Restrictions_UniqueKey,
        RQ_SRS_048_CAS_Restrictions_NonMergeTree,
        RQ_SRS_048_CAS_Restrictions_Backup_TempHardLinks,
        RQ_SRS_048_CAS_Restrictions_Backup_NativeSnapshot,
        RQ_SRS_048_CAS_Restrictions_Encryption,
        RQ_SRS_048_CAS_Restrictions_Azure,
        RQ_SRS_048_CAS_Restrictions_GCS,
        ),
    content=r'''
# SRS-048 ClickHouse Content-Addressed Storage
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Terminology](#terminology)
* 4 [Requirements](#requirements)
    * 4.1 [Generic](#generic)
        * 4.1.1 [RQ.SRS-048.CAS](#rqsrs-048cas)
        * 4.1.2 [RQ.SRS-048.CAS.NotATableEngine](#rqsrs-048casnotatableengine)
    * 4.2 [Configuration](#configuration)
        * 4.2.1 [RQ.SRS-048.CAS.Disk.Configuration](#rqsrs-048casdiskconfiguration)
        * 4.2.2 [RQ.SRS-048.CAS.Disk.MetadataType](#rqsrs-048casdiskmetadatatype)
        * 4.2.3 [RQ.SRS-048.CAS.Disk.ServerRootId](#rqsrs-048casdiskserverrootid)
        * 4.2.4 [RQ.SRS-048.CAS.Disk.ServerRootId.Unique](#rqsrs-048casdiskserverrootidunique)
        * 4.2.5 [RQ.SRS-048.CAS.Disk.Pool](#rqsrs-048casdiskpool)
        * 4.2.6 [RQ.SRS-048.CAS.Disk.Inline](#rqsrs-048casdiskinline)
        * 4.2.7 [RQ.SRS-048.CAS.Policy](#rqsrs-048caspolicy)
        * 4.2.8 [RQ.SRS-048.CAS.Disk.Settings](#rqsrs-048casdisksettings)
        * 4.2.9 [RQ.SRS-048.CAS.Disk.BlobHash](#rqsrs-048casdiskblobhash)
        * 4.2.10 [RQ.SRS-048.CAS.Disk.Backends](#rqsrs-048casdiskbackends)
    * 4.3 [Object Model](#object-model)
        * 4.3.1 [RQ.SRS-048.CAS.ObjectModel](#rqsrs-048casobjectmodel)
        * 4.3.2 [RQ.SRS-048.CAS.ObjectModel.Blobs](#rqsrs-048casobjectmodelblobs)
        * 4.3.3 [RQ.SRS-048.CAS.ObjectModel.Manifests](#rqsrs-048casobjectmodelmanifests)
        * 4.3.4 [RQ.SRS-048.CAS.ObjectModel.Refs](#rqsrs-048casobjectmodelrefs)
        * 4.3.5 [RQ.SRS-048.CAS.ObjectModel.Immutability](#rqsrs-048casobjectmodelimmutability)
    * 4.4 [MergeTree Compatibility](#mergetree-compatibility)
        * 4.4.1 [RQ.SRS-048.CAS.MergeTree](#rqsrs-048casmergetree)
        * 4.4.2 [RQ.SRS-048.CAS.MergeTree.Transparency](#rqsrs-048casmergetreetransparency)
        * 4.4.3 [RQ.SRS-048.CAS.MergeTree.Engines](#rqsrs-048casmergetreeengines)
        * 4.4.4 [RQ.SRS-048.CAS.MergeTree.InsertSelect](#rqsrs-048casmergetreeinsertselect)
        * 4.4.5 [RQ.SRS-048.CAS.MergeTree.Merge](#rqsrs-048casmergetreemerge)
        * 4.4.6 [RQ.SRS-048.CAS.MergeTree.Replicated](#rqsrs-048casmergetreereplicated)
        * 4.4.7 [RQ.SRS-048.CAS.MergeTree.PartTypes](#rqsrs-048casmergetreeparttypes)
        * 4.4.8 [RQ.SRS-048.CAS.MergeTree.Alter.Schema](#rqsrs-048casmergetreealterschema)
        * 4.4.9 [RQ.SRS-048.CAS.MergeTree.Mutations](#rqsrs-048casmergetreemutations)
        * 4.4.10 [RQ.SRS-048.CAS.MergeTree.LightweightDelete](#rqsrs-048casmergetreelightweightdelete)
        * 4.4.11 [RQ.SRS-048.CAS.MergeTree.PatchParts](#rqsrs-048casmergetreepatchparts)
        * 4.4.12 [RQ.SRS-048.CAS.MergeTree.Projections](#rqsrs-048casmergetreeprojections)
        * 4.4.13 [RQ.SRS-048.CAS.MergeTree.TTL](#rqsrs-048casmergetreettl)
        * 4.4.14 [RQ.SRS-048.CAS.MergeTree.Transactions](#rqsrs-048casmergetreetransactions)
        * 4.4.15 [RQ.SRS-048.CAS.MergeTree.RestartDurability](#rqsrs-048casmergetreerestartdurability)
        * 4.4.16 [RQ.SRS-048.CAS.MergeTree.Alter](#rqsrs-048casmergetreealter)
        * 4.4.17 [RQ.SRS-048.CAS.MergeTree.Alter.Column](#rqsrs-048casmergetreealtercolumn)
        * 4.4.18 [RQ.SRS-048.CAS.MergeTree.Alter.Update](#rqsrs-048casmergetreealterupdate)
        * 4.4.19 [RQ.SRS-048.CAS.MergeTree.Alter.Delete](#rqsrs-048casmergetreealterdelete)
        * 4.4.20 [RQ.SRS-048.CAS.MergeTree.Alter.OrderBy](#rqsrs-048casmergetreealterorderby)
        * 4.4.21 [RQ.SRS-048.CAS.MergeTree.Alter.SampleBy](#rqsrs-048casmergetreealtersampleby)
        * 4.4.22 [RQ.SRS-048.CAS.MergeTree.Alter.Index](#rqsrs-048casmergetreealterindex)
        * 4.4.23 [RQ.SRS-048.CAS.MergeTree.Alter.Projection](#rqsrs-048casmergetreealterprojection)
        * 4.4.24 [RQ.SRS-048.CAS.MergeTree.Alter.Constraint](#rqsrs-048casmergetreealterconstraint)
        * 4.4.25 [RQ.SRS-048.CAS.MergeTree.Alter.TTL](#rqsrs-048casmergetreealterttl)
        * 4.4.26 [RQ.SRS-048.CAS.MergeTree.Alter.Statistics](#rqsrs-048casmergetreealterstatistics)
        * 4.4.27 [RQ.SRS-048.CAS.MergeTree.Alter.Setting](#rqsrs-048casmergetreealtersetting)
        * 4.4.28 [RQ.SRS-048.CAS.MergeTree.Alter.Comment](#rqsrs-048casmergetreealtercomment)
        * 4.4.29 [RQ.SRS-048.CAS.MergeTree.Alter.ApplyDeletedMask](#rqsrs-048casmergetreealterapplydeletedmask)
        * 4.4.30 [RQ.SRS-048.CAS.MergeTree.Alter.ApplyPatches](#rqsrs-048casmergetreealterapplypatches)
    * 4.5 [Partition And Part Operations](#partition-and-part-operations)
        * 4.5.1 [RQ.SRS-048.CAS.Partition.AlterAllowList](#rqsrs-048caspartitionalterallowlist)
        * 4.5.2 [RQ.SRS-048.CAS.Partition.Replace](#rqsrs-048caspartitionreplace)
        * 4.5.3 [RQ.SRS-048.CAS.Partition.AttachFrom](#rqsrs-048caspartitionattachfrom)
        * 4.5.4 [RQ.SRS-048.CAS.Partition.Attach](#rqsrs-048caspartitionattach)
        * 4.5.5 [RQ.SRS-048.CAS.Partition.Detach](#rqsrs-048caspartitiondetach)
        * 4.5.6 [RQ.SRS-048.CAS.Partition.DetachAttach](#rqsrs-048caspartitiondetachattach)
        * 4.5.7 [RQ.SRS-048.CAS.Partition.MoveToTable](#rqsrs-048caspartitionmovetotable)
        * 4.5.8 [RQ.SRS-048.CAS.Partition.Drop](#rqsrs-048caspartitiondrop)
        * 4.5.9 [RQ.SRS-048.CAS.Partition.DropDetached](#rqsrs-048caspartitiondropdetached)
        * 4.5.10 [RQ.SRS-048.CAS.Partition.Forget](#rqsrs-048caspartitionforget)
        * 4.5.11 [RQ.SRS-048.CAS.Partition.Fetch](#rqsrs-048caspartitionfetch)
        * 4.5.12 [RQ.SRS-048.CAS.Partition.Freeze](#rqsrs-048caspartitionfreeze)
        * 4.5.13 [RQ.SRS-048.CAS.Partition.Unfreeze](#rqsrs-048caspartitionunfreeze)
        * 4.5.14 [RQ.SRS-048.CAS.Partition.Clone](#rqsrs-048caspartitionclone)
        * 4.5.15 [RQ.SRS-048.CAS.Partition.ClearColumn](#rqsrs-048caspartitionclearcolumn)
        * 4.5.16 [RQ.SRS-048.CAS.Partition.ClearIndex](#rqsrs-048caspartitionclearindex)
        * 4.5.17 [RQ.SRS-048.CAS.Partition.RewriteParts](#rqsrs-048caspartitionrewriteparts)
        * 4.5.18 [RQ.SRS-048.CAS.Partition.Update](#rqsrs-048caspartitionupdate)
        * 4.5.19 [RQ.SRS-048.CAS.Partition.Delete](#rqsrs-048caspartitiondelete)
        * 4.5.20 [RQ.SRS-048.CAS.Partition.MoveToDisk](#rqsrs-048caspartitionmovetodisk)
    * 4.6 [Backup And Restore](#backup-and-restore)
        * 4.6.1 [RQ.SRS-048.CAS.Backup](#rqsrs-048casbackup)
        * 4.6.2 [RQ.SRS-048.CAS.Restore](#rqsrs-048casrestore)
    * 4.7 [Shared Pool](#shared-pool)
        * 4.7.1 [RQ.SRS-048.CAS.SharedPool](#rqsrs-048cassharedpool)
        * 4.7.2 [RQ.SRS-048.CAS.SharedPool.Deduplication](#rqsrs-048cassharedpooldeduplication)
        * 4.7.3 [RQ.SRS-048.CAS.SharedPool.IndependentRefs](#rqsrs-048cassharedpoolindependentrefs)
        * 4.7.4 [RQ.SRS-048.CAS.SharedPool.NodeCrash](#rqsrs-048cassharedpoolnodecrash)
    * 4.8 [Replication Relink](#replication-relink)
        * 4.8.1 [RQ.SRS-048.CAS.Relink](#rqsrs-048casrelink)
        * 4.8.2 [RQ.SRS-048.CAS.Relink.HappyPath](#rqsrs-048casrelinkhappypath)
        * 4.8.3 [RQ.SRS-048.CAS.Relink.DetachedFetch](#rqsrs-048casrelinkdetachedfetch)
        * 4.8.4 [RQ.SRS-048.CAS.Relink.CrossPool.ByteFallback](#rqsrs-048casrelinkcrosspoolbytefallback)
        * 4.8.5 [RQ.SRS-048.CAS.Relink.AttachPartitionFrom](#rqsrs-048casrelinkattachpartitionfrom)
        * 4.8.6 [RQ.SRS-048.CAS.Relink.ReplacePartition](#rqsrs-048casrelinkreplacepartition)
        * 4.8.7 [RQ.SRS-048.CAS.Relink.VersionMix](#rqsrs-048casrelinkversionmix)
        * 4.8.8 [RQ.SRS-048.CAS.Relink.ConfirmRace](#rqsrs-048casrelinkconfirmrace)
        * 4.8.9 [RQ.SRS-048.CAS.Relink.StalledPublish](#rqsrs-048casrelinkstalledpublish)
        * 4.8.10 [RQ.SRS-048.CAS.Relink.RecursionBrake](#rqsrs-048casrelinkrecursionbrake)
    * 4.9 [Garbage Collection](#garbage-collection)
        * 4.9.1 [RQ.SRS-048.CAS.GC](#rqsrs-048casgc)
        * 4.9.2 [RQ.SRS-048.CAS.GC.NoLoss](#rqsrs-048casgcnoloss)
        * 4.9.3 [RQ.SRS-048.CAS.GC.ReclaimAfterDrop](#rqsrs-048casgcreclaimafterdrop)
        * 4.9.4 [RQ.SRS-048.CAS.GC.Run](#rqsrs-048casgcrun)
        * 4.9.5 [RQ.SRS-048.CAS.GC.Rebuild](#rqsrs-048casgcrebuild)
        * 4.9.6 [RQ.SRS-048.CAS.GC.Sharded](#rqsrs-048casgcsharded)
        * 4.9.7 [RQ.SRS-048.CAS.GC.RefSnaplog](#rqsrs-048casgcrefsnaplog)
        * 4.9.8 [RQ.SRS-048.CAS.GC.StopStart](#rqsrs-048casgcstopstart)
        * 4.9.9 [RQ.SRS-048.CAS.GC.DryRun](#rqsrs-048casgcdryrun)
        * 4.9.10 [RQ.SRS-048.CAS.Fsck](#rqsrs-048casfsck)
        * 4.9.11 [RQ.SRS-048.CAS.Fsck.Online](#rqsrs-048casfsckonline)
    * 4.10 [Day-2 Operations](#day-2-operations)
        * 4.10.1 [RQ.SRS-048.CAS.DropPoolMember](#rqsrs-048casdroppoolmember)
        * 4.10.2 [RQ.SRS-048.CAS.DropPoolMember.ReadonlyRejected](#rqsrs-048casdroppoolmemberreadonlyrejected)
        * 4.10.3 [RQ.SRS-048.CAS.Forget](#rqsrs-048casforget)
        * 4.10.4 [RQ.SRS-048.CAS.Tools](#rqsrs-048castools)
    * 4.11 [Fault Recovery](#fault-recovery)
        * 4.11.1 [RQ.SRS-048.CAS.Fault.LostPartRecovery](#rqsrs-048casfaultlostpartrecovery)
        * 4.11.2 [RQ.SRS-048.CAS.Fault.LazyLoad.S3Outage](#rqsrs-048casfaultlazyloads3outage)
        * 4.11.3 [RQ.SRS-048.CAS.Fault.FailClosed](#rqsrs-048casfaultfailclosed)
    * 4.12 [Cache](#cache)
        * 4.12.1 [RQ.SRS-048.CAS.Cache](#rqsrs-048cascache)
        * 4.12.2 [RQ.SRS-048.CAS.Cache.Hits](#rqsrs-048cascachehits)
    * 4.13 [Observability And Access](#observability-and-access)
        * 4.13.1 [RQ.SRS-048.CAS.Observability](#rqsrs-048casobservability)
        * 4.13.2 [RQ.SRS-048.CAS.Observability.SystemTables](#rqsrs-048casobservabilitysystemtables)
        * 4.13.3 [RQ.SRS-048.CAS.Observability.ProfileEvents](#rqsrs-048casobservabilityprofileevents)
        * 4.13.4 [RQ.SRS-048.CAS.Access](#rqsrs-048casaccess)
    * 4.14 [Restrictions And Non-Goals](#restrictions-and-non-goals)
        * 4.14.1 [RQ.SRS-048.CAS.Restrictions.BackendCapabilities](#rqsrs-048casrestrictionsbackendcapabilities)
        * 4.14.2 [RQ.SRS-048.CAS.Restrictions.ZeroCopy](#rqsrs-048casrestrictionszerocopy)
        * 4.14.3 [RQ.SRS-048.CAS.Restrictions.UniqueKey](#rqsrs-048casrestrictionsuniquekey)
        * 4.14.4 [RQ.SRS-048.CAS.Restrictions.NonMergeTree](#rqsrs-048casrestrictionsnonmergetree)
        * 4.14.5 [RQ.SRS-048.CAS.Restrictions.Backup.TempHardLinks](#rqsrs-048casrestrictionsbackuptemphardlinks)
        * 4.14.6 [RQ.SRS-048.CAS.Restrictions.Backup.NativeSnapshot](#rqsrs-048casrestrictionsbackupnativesnapshot)
        * 4.14.7 [RQ.SRS-048.CAS.Restrictions.Encryption](#rqsrs-048casrestrictionsencryption)
        * 4.14.8 [RQ.SRS-048.CAS.Restrictions.Azure](#rqsrs-048casrestrictionsazure)
        * 4.14.9 [RQ.SRS-048.CAS.Restrictions.GCS](#rqsrs-048casrestrictionsgcs)
* 5 [References](#references)

## Revision History

This document is stored in an electronic form using [Git] source control
management software hosted in a [GitHub Repository]. All the updates are tracked
using the [Revision History].

## Introduction

Content-addressed storage ([CAS]) is an **opt-in object-storage disk backend** for
the [MergeTree] engine family. It is selected with
`metadata_type = cas` on an `object_storage` disk. It does **not**
introduce a new table engine.

Ordinary `MergeTree` and `ReplicatedMergeTree` tables keep their SQL surface and
logical part lifecycle. **All mainstream MergeTree features that work on ordinary
object-storage disks are expected to work on [CAS]** (insert/select, merge,
mutations, projections, TTL, transactions, the documented [MergeTree]
`ALTER TABLE` surface (columns, mutations, keys, indexes, projections,
constraints, TTL, statistics, settings, comments, apply-deleted-mask /
apply-patches, and partition ALTER including ATTACH / REPLACE / MOVE /
DETACH / DROP / FETCH / FREEZE / FORGET / CLEAR / REWRITE), backup on
Atomic DBs, replication), except where this [SRS] explicitly lists a restriction.
[CAS] changes only the physical representation of parts in a shared object-store
**pool**:

* immutable **blobs** keyed by content hash;
* immutable **part manifests** listing the files of one part;
* mutable **refs** that map part names to manifests under a per-server ownership
  namespace (`cas_server_root_id`).

Replicas that mount the same pool can **relink** (adopt a peer's manifest by
reference) instead of copying part bytes. Background **garbage collection** is
the only path authorized to delete unreferenced CAS objects.

This [SRS] specifies the product requirements that the Altinity regression suite
exercises. Product architecture and operations live in
[Altinity/ClickHouse PR #2159](https://github.com/Altinity/ClickHouse/pull/2159)
(`docs/en/antalya/cas/`, plus the `SYSTEM CAS` page and the `system.cas_*`
tables). Upstream integration inventory is summarized in
[`cas/docs/CAS-INTEGRATION-TESTS.md`](../docs/CAS-INTEGRATION-TESTS.md).

**Status:** experimental. The on-disk format and the SQL surface can still change
between releases. Core read/write/ref/GC paths exist; release readiness is gated
by the live backlog in the product docs.

## Terminology

* **CAS** — content-addressed storage disk backend (`metadata_type = cas`).
* **Pool** — shared object-store bucket/prefix. Blob reuse is pool-global;
  relink eligibility is the minted `cas_pool_uuid`, not endpoint-plus-prefix
  string equality.
* **cas_server_root_id** — durable per-server ownership identity inside a pool.
  Distinct from the pool endpoint; must be unique among concurrent writers.
  The unprefixed spelling `server_root_id` is accepted for a bounded migration
  period and reported at startup.
* **Blob** — immutable content-addressed object under `blobs/...`.
* **Manifest** — immutable description of one MergeTree part's files.
* **Ref** — mutable mapping from a part name to a manifest in a server's
  namespace.
* **Relink** — replication path that publishes a local ref to an already-present
  peer manifest instead of transferring part bytes.
* **GC** — background garbage collection that reclaims objects with no live
  ownership, without deleting objects still named by a committed reference.

## Requirements

### Generic

#### RQ.SRS-048.CAS
version: 1.0

[ClickHouse] SHALL support content-addressed storage as an object-storage disk
backend for the [MergeTree] engine family.

#### RQ.SRS-048.CAS.NotATableEngine
version: 1.0

[ClickHouse] SHALL expose [CAS] as a disk / storage-policy choice, not as a
separate table engine. Users SHALL create ordinary `MergeTree` /
`ReplicatedMergeTree` (and MergeTree-family) tables on a [CAS] disk or policy.

### Configuration

#### RQ.SRS-048.CAS.Disk.Configuration
version: 1.0

[ClickHouse] SHALL support configuring a [CAS] disk in
`<storage_configuration><disks>` with `type = object_storage`, an object-storage
type such as `s3` or `local`, and [CAS]-specific settings including
`metadata_type = cas` and `cas_server_root_id`. The recommended production
shape layers a `type = cache` disk over the [CAS] disk and points the storage
policy at the cached disk.

Example:

```xml
<clickhouse>
    <storage_configuration>
        <disks>
            <cas>
                <type>object_storage</type>
                <object_storage_type>s3</object_storage_type>
                <metadata_type>cas</metadata_type>
                <cas_server_root_id>{replica}</cas_server_root_id>
                <endpoint>https://bucket.s3.amazonaws.com/cas/</endpoint>
            </cas>
            <cas_cache>
                <type>cache</type>
                <disk>cas</disk>
                <path>/var/lib/clickhouse/cas_cache/</path>
                <max_size>10Gi</max_size>
            </cas_cache>
        </disks>
        <policies>
            <cas>
                <volumes>
                    <main>
                        <disk>cas_cache</disk>
                    </main>
                </volumes>
            </cas>
        </policies>
    </storage_configuration>
</clickhouse>
```

#### RQ.SRS-048.CAS.Disk.MetadataType
version: 1.0

[ClickHouse] SHALL enable content-addressed storage when
`metadata_type` is set to `cas` on an object-storage disk.

#### RQ.SRS-048.CAS.Disk.ServerRootId
version: 1.0

[ClickHouse] SHALL require a configured `cas_server_root_id` that identifies the
server's durable ownership tree inside the pool. Omitting the setting SHALL be a
startup error. The value MAY expand macros (for example `{replica}`) and SHALL
remain stable across restarts for that server's membership in the pool. The
unprefixed spelling `server_root_id` SHALL be accepted for a bounded migration
period and reported at startup; a key written in both spellings SHALL be
rejected.

#### RQ.SRS-048.CAS.Disk.ServerRootId.Unique
version: 1.0

[ClickHouse] SHALL fail closed when two servers attempt to mount the same pool
with the same `cas_server_root_id` as concurrent writers, instead of allowing
both to mutate the same ref namespace. A colliding identity SHALL be refused at
the owner-claim / mount-lease gate.

#### RQ.SRS-048.CAS.Disk.Pool
version: 1.0

[ClickHouse] SHALL treat the object-storage endpoint (bucket and prefix) as the
shared [CAS] pool for blob reuse among servers that mount that endpoint with
distinct `cas_server_root_id` values. Relink eligibility SHALL use the minted
`cas_pool_uuid`, not endpoint-plus-prefix string equality.

#### RQ.SRS-048.CAS.Disk.Inline
version: 1.0

[ClickHouse] SHALL support selecting a [CAS] disk via the inline `disk = disk(...)`
table setting as well as via a named disk in storage configuration.

#### RQ.SRS-048.CAS.Policy
version: 1.0

[ClickHouse] SHALL support selecting [CAS] disks through storage policies in
`<storage_configuration><policies>`, consistent with other object-storage disks.
When a `type = cache` disk wraps [CAS], the policy volume SHALL name the cache
disk, not the raw [CAS] disk.

#### RQ.SRS-048.CAS.Disk.Settings
version: 1.0

[ClickHouse] SHALL read [CAS]-owned disk settings from the `cas_` config-key
namespace and leave every other key in the disk block to the object-storage or
generic disk layer. A misspelled `cas_` key SHALL be rejected. Unprefixed
spellings of [CAS] settings SHALL be accepted for a bounded period and reported
at startup. `skip_access_check` and `gcs_max_conditional_put_bytes` SHALL remain
unprefixed (they belong to the generic disk / S3 client layers).

#### RQ.SRS-048.CAS.Disk.BlobHash
version: 1.0

[ClickHouse] SHALL support selecting the pool blob content-hash function with
`cas_blob_hash` (`cityhash128` default, `xxh3-128`, or `sha256`). The algorithm
SHALL be recorded in the pool at creation; a mismatching config SHALL be refused
at mount. `cas_blob_hash_allow_new` SHALL be the explicit opt-in that admits a
second algorithm into an existing pool.

#### RQ.SRS-048.CAS.Disk.Backends
version: 1.0

[ClickHouse] SHALL support [CAS] on AWS S3 (`ETag` conditional dialect) and on
the `local` object-storage backend (single-node / demo). Google Cloud Storage
SHALL use the generation-token dialect (`http_client = gcs_hmac` or
`gcp_oauth`). Other S3-compatible stores SHALL be admitted only when the mount
capability probe confirms they enforce conditional operations. Azure Blob is
specified under
[RQ.SRS-048.CAS.Restrictions.Azure](#rqsrs-048casrestrictionsazure).

### Object Model

#### RQ.SRS-048.CAS.ObjectModel
version: 1.0

[ClickHouse] SHALL store [MergeTree] parts on a [CAS] disk as content-addressed
objects in the pool, consisting of blobs, part manifests, refs, and a blob
condemnation-marker sidecar, rather than as ordinary per-table part path copies
alone. There is no [CAS] state in Keeper; pool bookkeeping lives in the bucket.

#### RQ.SRS-048.CAS.ObjectModel.Blobs
version: 1.0

[ClickHouse] SHALL store content-addressed file payloads as immutable blob
objects under a pool-global `blobs/` prefix, keyed by content hash, so identical
bytes MAY be shared across tables and servers in the same pool.

#### RQ.SRS-048.CAS.ObjectModel.Manifests
version: 1.0

[ClickHouse] SHALL store an immutable part manifest that lists the files
belonging to one [MergeTree] part and their blob (or inline) placements.

#### RQ.SRS-048.CAS.ObjectModel.Refs
version: 1.0

[ClickHouse] SHALL maintain mutable refs under each server's ownership namespace
that map part names to manifests. Refs SHALL be the mutable layer that changes
when parts are created, merged, mutated, or dropped.

#### RQ.SRS-048.CAS.ObjectModel.Immutability
version: 1.0

[ClickHouse] SHALL treat blobs and manifests as immutable after publish. Logical
part changes SHALL produce new parts (and therefore new manifests / ref updates)
rather than rewriting existing blob or manifest identities in place.

### MergeTree Compatibility

[CAS] is a transparent storage backend for the [MergeTree] family: SQL surface
and logical part semantics remain those of [MergeTree]; only the physical layout
differs. Unless a requirement in
[Restrictions And Non-Goals](#restrictions-and-non-goals) says otherwise,
features that work for [MergeTree] on ordinary object-storage disks SHALL work
on [CAS].

#### RQ.SRS-048.CAS.MergeTree
version: 1.0

[ClickHouse] SHALL support the [MergeTree] engine family on a [CAS] disk without
requiring CAS-specific DDL beyond disk / policy selection.

#### RQ.SRS-048.CAS.MergeTree.Transparency
version: 1.0

[ClickHouse] SHALL preserve ordinary [MergeTree] logical behavior for tables on
a [CAS] disk. User-visible query results, part lifecycle semantics, and
supported `ALTER` / partition operations SHALL match non-CAS [MergeTree] unless
an explicit [CAS] restriction applies. [CAS] MUST NOT invent a separate SQL
dialect for everyday table use.

#### RQ.SRS-048.CAS.MergeTree.Engines
version: 1.0

[ClickHouse] SHALL support the mainstream [MergeTree] engine family on a [CAS]
disk, including at least:

* `MergeTree`
* `ReplicatedMergeTree`
* `ReplacingMergeTree` / `ReplicatedReplacingMergeTree`
* `SummingMergeTree` / `ReplicatedSummingMergeTree`
* `AggregatingMergeTree` / `ReplicatedAggregatingMergeTree`
* `CollapsingMergeTree` / `ReplicatedCollapsingMergeTree`
* `VersionedCollapsingMergeTree` / `ReplicatedVersionedCollapsingMergeTree`

#### RQ.SRS-048.CAS.MergeTree.InsertSelect
version: 1.0

[ClickHouse] SHALL support `INSERT` and `SELECT` on [MergeTree] tables stored on
a [CAS] disk with the same logical results as on a non-CAS disk for the same
data.

#### RQ.SRS-048.CAS.MergeTree.Merge
version: 1.0

[ClickHouse] SHALL support merges (`OPTIMIZE` / background merges) of parts on a
[CAS] disk. After merge, logical table contents SHALL remain correct and unused
source parts SHALL become eligible for [GC] reclaim when no longer referenced.

#### RQ.SRS-048.CAS.MergeTree.Replicated
version: 1.0

[ClickHouse] SHALL support `ReplicatedMergeTree` tables on a shared [CAS] pool
so that replicas converge to the same logical data while each replica owns its
own ref namespace under a distinct `cas_server_root_id`.

#### RQ.SRS-048.CAS.MergeTree.PartTypes
version: 1.0

[ClickHouse] SHALL support Wide and Compact [MergeTree] parts on a [CAS] disk.
Projections, patch parts, detached parts, temporary parts, and frozen/shadow
parts SHALL be representable in the [CAS] object model.

#### RQ.SRS-048.CAS.MergeTree.Alter.Schema
version: 1.0

[ClickHouse] SHALL support schema-changing `ALTER TABLE` operations on
[CAS]-backed [MergeTree] tables (for example add / drop / modify / rename
column, codec changes) with the same logical outcome as on non-CAS storage,
implemented via the ordinary new-part / drop-old-part [MergeTree] path.
The full [MergeTree] `ALTER TABLE` catalog is specified under
[RQ.SRS-048.CAS.MergeTree.Alter](#rqsrs-048casmergetreealter).

#### RQ.SRS-048.CAS.MergeTree.Mutations
version: 1.0

[ClickHouse] SHALL support mutations on [CAS]-backed [MergeTree] tables. Where
Wide-part carry-forward applies, unchanged column blobs MAY be re-referenced
without re-upload; logical mutation results SHALL match non-CAS behavior.

#### RQ.SRS-048.CAS.MergeTree.LightweightDelete
version: 1.0

[ClickHouse] SHALL support lightweight deletes on [CAS]-backed [MergeTree]
tables with correct logical visibility of deleted rows.

#### RQ.SRS-048.CAS.MergeTree.PatchParts
version: 1.0

[ClickHouse] SHALL support patch parts on [CAS]-backed [MergeTree] tables and
SHALL preserve patch-part durability across server restart.

#### RQ.SRS-048.CAS.MergeTree.Projections
version: 1.0

[ClickHouse] SHALL support [MergeTree] projections on a [CAS] disk. Projection
files SHALL be stored as nested entries of the parent part manifest (not as an
independently GC'd projection ref namespace), and projection query results SHALL
match non-CAS behavior.

#### RQ.SRS-048.CAS.MergeTree.TTL
version: 1.0

[ClickHouse] SHALL support TTL delete and TTL move rules on [CAS]-backed
[MergeTree] tables with correct logical data removal or relocation semantics.
Cross-disk TTL / `MOVE PARTITION ... TO DISK|VOLUME` onto or off [CAS] MAY be
subject to additional verification constraints documented under restrictions.

#### RQ.SRS-048.CAS.MergeTree.Transactions
version: 1.0

[ClickHouse] SHALL support [MergeTree] transactions / MVCC metadata on a [CAS]
disk through the content-addressed transactional mutable-file capability, so
that transaction metadata files (for example `txn_version.txt`) are carried as
ordinary manifest entries and atomically repointed with the part ref.

#### RQ.SRS-048.CAS.MergeTree.RestartDurability
version: 1.0

[ClickHouse] SHALL preserve committed [CAS]-backed table data and applicable
mutation / patch-part / projection state across ClickHouse server restart.

#### RQ.SRS-048.CAS.MergeTree.Alter
version: 1.0

[ClickHouse] SHALL support the documented `ALTER TABLE` modifiers for the
[MergeTree] family on a [CAS] disk with the same logical outcome as on
non-CAS [MergeTree] storage, except where this [SRS] lists a restriction.
There SHALL be no [CAS]-specific SQL dialect for these commands.

The catalog follows the upstream [ALTER](https://clickhouse.com/docs/reference/statements/alter)
index. Commands that create mutations (`UPDATE`, `DELETE`, `MATERIALIZE *`,
`CLEAR INDEX` / `CLEAR STATISTICS` / `CLEAR PROJECTION`, `APPLY DELETED MASK`,
`APPLY PATCHES`, `REWRITE PARTS`, and similar) SHALL rewrite parts through the
ordinary [MergeTree] mutation path (new parts / new refs). Metadata-only
commands SHALL not invent a separate [CAS] rewrite of immutable blobs.

Partition commands are additionally gated by
[RQ.SRS-048.CAS.Partition.AlterAllowList](#rqsrs-048caspartitionalterallowlist).
View, RBAC, named-collection, and `ALTER DATABASE` statements are out of
scope for [CAS] table storage.

#### RQ.SRS-048.CAS.MergeTree.Alter.Column
version: 1.0

[ClickHouse] SHALL support column `ALTER TABLE` actions on [CAS]-backed
[MergeTree] tables:

* `ADD COLUMN [IF NOT EXISTS] ... [AFTER ... | FIRST]`
* `DROP COLUMN [IF EXISTS] ...`
* `RENAME COLUMN [IF EXISTS] ... TO ...`
* `CLEAR COLUMN [IF EXISTS] ... IN PARTITION ...`
* `COMMENT COLUMN [IF EXISTS] ...`
* `MODIFY COLUMN` / `ALTER COLUMN ... TYPE` (type, default, codec, TTL,
  statistics, column settings, `FIRST` / `AFTER`)
* `MODIFY COLUMN ... REMOVE` (`DEFAULT`, `ALIAS`, `MATERIALIZED`, `CODEC`,
  `COMMENT`, `TTL`, `SETTINGS`)
* `MODIFY COLUMN ... MODIFY SETTING ...`
* `MODIFY COLUMN ... RESET SETTING ...`
* `MODIFY COLUMN ... ADD ENUM VALUES ...`
* `MATERIALIZE COLUMN ... [IN PARTITION ... | IN PARTITION ID ...]`

Logical results SHALL match non-CAS [MergeTree]. `MATERIALIZE COLUMN` SHALL
be implemented as a mutation. Key-column rename / type-change limitations
SHALL match upstream [MergeTree] (not [CAS]-specific).

#### RQ.SRS-048.CAS.MergeTree.Alter.Update
version: 1.0

[ClickHouse] SHALL support heavyweight

```sql
ALTER TABLE [db.]table UPDATE column1 = expr1 [, ...] [IN PARTITION partition_expr] WHERE filter_expr
```

on [CAS]-backed [MergeTree] tables as a mutation. Logical updated values
SHALL match non-CAS behavior. Updating columns used in the primary or
partition key SHALL remain unsupported, as on non-CAS [MergeTree].

#### RQ.SRS-048.CAS.MergeTree.Alter.Delete
version: 1.0

[ClickHouse] SHALL support heavyweight

```sql
ALTER TABLE [db.]table DELETE [IN PARTITION partition_expr] WHERE filter_expr
```

on [CAS]-backed [MergeTree] tables as a mutation. Logical row removal SHALL
match non-CAS behavior. This requirement covers `ALTER TABLE ... DELETE`,
not `DELETE FROM` lightweight deletes
([RQ.SRS-048.CAS.MergeTree.LightweightDelete](#rqsrs-048casmergetreelightweightdelete)).

#### RQ.SRS-048.CAS.MergeTree.Alter.OrderBy
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... MODIFY ORDER BY ...` on
[CAS]-backed [MergeTree] tables as a metadata-only change of the sorting
key (primary key unchanged), with the same restrictions as non-CAS
[MergeTree].

#### RQ.SRS-048.CAS.MergeTree.Alter.SampleBy
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... MODIFY SAMPLE BY ...` and
`ALTER TABLE ... REMOVE SAMPLE BY` on [CAS]-backed [MergeTree] tables as
metadata-only sampling-key changes, with the same primary-key containment
rules as non-CAS [MergeTree].

#### RQ.SRS-048.CAS.MergeTree.Alter.Index
version: 1.0

[ClickHouse] SHALL support data-skipping-index `ALTER TABLE` actions on
[CAS]-backed [MergeTree] tables:

* `ADD INDEX [IF NOT EXISTS] ... TYPE ... [GRANULARITY ...] [FIRST | AFTER ...]`
* `DROP INDEX [IF EXISTS] ...`
* `MATERIALIZE INDEX [IF EXISTS] ... [IN PARTITION ...]`
* `CLEAR INDEX [IF EXISTS] ... [IN PARTITION ...]`

`ADD INDEX` SHALL update metadata. `MATERIALIZE INDEX`, `DROP INDEX`, and
`CLEAR INDEX` SHALL follow upstream mutation / file-removal semantics.
Logical skip-index behavior SHALL match non-CAS [MergeTree].

#### RQ.SRS-048.CAS.MergeTree.Alter.Projection
version: 1.0

[ClickHouse] SHALL support projection `ALTER TABLE` actions on [CAS]-backed
[MergeTree] tables:

* `ADD PROJECTION [IF NOT EXISTS] ...`
* `DROP PROJECTION [IF EXISTS] ...`
* `MATERIALIZE PROJECTION [IF EXISTS] ... [IN PARTITION ...]`
* `CLEAR PROJECTION [IF EXISTS] ... [IN PARTITION ...]`
* `MODIFY PROJECTION [IF EXISTS] ... ( SELECT ... ) WITH SETTINGS (...)`

Projection files SHALL remain nested entries of the parent part manifest
([RQ.SRS-048.CAS.MergeTree.Projections](#rqsrs-048casmergetreeprojections)).
Query results that use the projection SHALL match non-CAS behavior.

`MODIFY PROJECTION` only applies to [ClickHouse] >= 26.9, where the command
was added to the parser. Older builds, including the 26.6-based Antalya
build, reject it with `SYNTAX_ERROR` on non-CAS [MergeTree] as well, so
scenarios covering it SHALL be skipped there.

#### RQ.SRS-048.CAS.MergeTree.Alter.Constraint
version: 1.0

[ClickHouse] SHALL support constraint `ALTER TABLE` actions on [CAS]-backed
[MergeTree] tables:

* `ADD CONSTRAINT [IF NOT EXISTS] ... {CHECK | ASSUME} ...`
* `DROP CONSTRAINT [IF EXISTS] ...`
* `MODIFY CONSTRAINT [IF EXISTS] ... {CHECK | ASSUME} ...`

These commands SHALL change table metadata immediately and SHALL NOT
re-check existing rows, matching non-CAS [MergeTree].

`MODIFY CONSTRAINT` only applies to [ClickHouse] >= 26.7, where the command
was added to the parser. Older builds, including the 26.6-based Antalya
build, reject it with `SYNTAX_ERROR` on non-CAS [MergeTree] as well, so
scenarios covering it SHALL be skipped there.

#### RQ.SRS-048.CAS.MergeTree.Alter.TTL
version: 1.0

[ClickHouse] SHALL support table-TTL `ALTER TABLE` actions on [CAS]-backed
[MergeTree] tables:

* `MODIFY TTL ...`
* `REMOVE TTL`
* `MATERIALIZE TTL`

`MODIFY TTL` / `REMOVE TTL` SHALL update metadata. `MATERIALIZE TTL` SHALL
force TTL application as a mutation. Column TTL SHALL be covered by
`MODIFY COLUMN ... TTL` /
[RQ.SRS-048.CAS.MergeTree.Alter.Column](#rqsrs-048casmergetreealtercolumn).
Logical delete / move-to-volume TTL semantics SHALL match
[RQ.SRS-048.CAS.MergeTree.TTL](#rqsrs-048casmergetreettl).

#### RQ.SRS-048.CAS.MergeTree.Alter.Statistics
version: 1.0

[ClickHouse] SHALL support column-statistics `ALTER TABLE` actions on
[CAS]-backed [MergeTree] tables:

* `ADD STATISTICS [IF NOT EXISTS] ... TYPE ...`
* `MODIFY STATISTICS ... TYPE ...`
* `DROP STATISTICS [IF EXISTS] ...`
* `CLEAR STATISTICS [IF EXISTS] ...`
* `MATERIALIZE STATISTICS (ALL | [IF EXISTS] ...)`

Metadata commands SHALL match non-CAS behavior. `MATERIALIZE STATISTICS`
and `CLEAR STATISTICS` SHALL follow upstream mutation semantics.

#### RQ.SRS-048.CAS.MergeTree.Alter.Setting
version: 1.0

[ClickHouse] SHALL support table-setting `ALTER TABLE` actions on
[CAS]-backed [MergeTree] tables:

* `MODIFY SETTING setting_name = value [, ...]`
* `RESET SETTING setting_name [, ...]`

These commands SHALL apply only to [MergeTree] table settings, matching
non-CAS behavior.

#### RQ.SRS-048.CAS.MergeTree.Alter.Comment
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... MODIFY COMMENT '...'` on
[CAS]-backed [MergeTree] tables, including clearing the comment with an
empty string. On `ReplicatedMergeTree`, comment changes MAY remain
replica-local, matching upstream [MergeTree].

#### RQ.SRS-048.CAS.MergeTree.Alter.ApplyDeletedMask
version: 1.0

[ClickHouse] SHALL support

```sql
ALTER TABLE [db.]table APPLY DELETED MASK [IN PARTITION partition_id]
```

on [CAS]-backed [MergeTree] tables as a mutation that physically removes
rows marked by lightweight delete (`_row_exists = 0`), with the same
logical outcome as on non-CAS storage.

#### RQ.SRS-048.CAS.MergeTree.Alter.ApplyPatches
version: 1.0

[ClickHouse] SHALL support

```sql
ALTER TABLE [db.]table APPLY PATCHES [IN PARTITION partition_id]
```

on [CAS]-backed [MergeTree] tables as a mutation that materializes pending
lightweight-update patch parts into data parts, with the same logical
outcome as on non-CAS storage.

### Partition And Part Operations

Same-disk / same-pool partition and part DDL MUST remain correct on [CAS]
tables. The product allow-list in `MergeTreeData::checkAlterPartitionIsPossible`
for `MetadataStorageType::ContentAddressed` is the authoritative gate for which
partition commands are admitted.

Replication-queue relink for the same operations is covered under
[Replication Relink](#replication-relink).

#### RQ.SRS-048.CAS.Partition.AlterAllowList
version: 1.0

[ClickHouse] SHALL allow the following partition commands on a [CAS] disk and
SHALL reject unsupported partition commands fail-closed:

* `DETACH PARTITION` / `DETACH PART`
* `DROP PARTITION` / `DROP PART`
* `DROP DETACHED PARTITION` / `DROP DETACHED PART`
* `FORGET PARTITION`
* `ATTACH PARTITION` / `ATTACH PART`
* `REPLACE PARTITION` / `ATTACH PARTITION ... FROM`
* `MOVE PARTITION` (including `MOVE PARTITION ... TO TABLE`)
* `FETCH PARTITION` / `FETCH PART`
* `FREEZE PARTITION` / `FREEZE`
* `UNFREEZE PARTITION` / `UNFREEZE`

`DROP` / `DETACH` / `ATTACH` / `ATTACH FROM` SHALL accept `PARTITION ALL`
where upstream [MergeTree] does. Partition-scoped mutations
(`CLEAR COLUMN` / `CLEAR INDEX`, `UPDATE` / `DELETE IN PARTITION`,
`REWRITE PARTS`) are specified under the following requirements and are
not limited to this allow-list when they use the ordinary mutation path.

#### RQ.SRS-048.CAS.Partition.Replace
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... REPLACE PARTITION ... FROM ...`
between [MergeTree] tables on the same [CAS] pool with correct partition
contents on the destination and without deleting the replaced partition from
the source.

#### RQ.SRS-048.CAS.Partition.AttachFrom
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... ATTACH PARTITION ... FROM ...`
between [MergeTree] tables on the same [CAS] pool so that the destination gains
the partition and the source retains it.

#### RQ.SRS-048.CAS.Partition.Attach
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... ATTACH PARTITION` /
`ATTACH PART` of previously detached parts on a [CAS]-backed table so that
attached data becomes readable and survives restart.

#### RQ.SRS-048.CAS.Partition.Detach
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... DETACH PARTITION` /
`DETACH PART` on a [CAS]-backed table so that detached data is no longer
queryable from the active table while remaining available under the detached
namespace for later attach or drop.

#### RQ.SRS-048.CAS.Partition.DetachAttach
version: 1.0

[ClickHouse] SHALL support `DETACH PARTITION` / `ATTACH PARTITION` round-trips
on a [CAS]-backed [MergeTree] table without logical data loss.

#### RQ.SRS-048.CAS.Partition.MoveToTable
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... MOVE PARTITION ... TO TABLE ...`
between [MergeTree] tables on the same [CAS] pool so that the partition leaves
the source and appears on the destination with unchanged contents.

#### RQ.SRS-048.CAS.Partition.Drop
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... DROP PARTITION` / `DROP PART` on a
[CAS]-backed table. Dropped part refs SHALL be removed and their blobs /
manifests SHALL become eligible for [GC] when no other ownership remains.
Logical drop semantics SHALL match non-CAS [MergeTree] (including documented
weak guarantees when `DROP PART` races a concurrent merge).

#### RQ.SRS-048.CAS.Partition.DropDetached
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... DROP DETACHED PARTITION` /
`DROP DETACHED PART` on a [CAS]-backed table when `allow_drop_detached` permits
the command.

#### RQ.SRS-048.CAS.Partition.Forget
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... FORGET PARTITION` on
`ReplicatedMergeTree` tables stored on [CAS]. The command manipulates Keeper
partition metadata and SHALL NOT require rewriting or deleting [CAS] part blobs
as part of the forget itself.

#### RQ.SRS-048.CAS.Partition.Fetch
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... FETCH PARTITION` /
`FETCH PART` (including fetch into detached) for `ReplicatedMergeTree` tables
on a [CAS] disk. When the peer shares the same pool, fetch MAY use relink;
otherwise it SHALL use ordinary byte fetch. Logical fetched data SHALL match
the source.

#### RQ.SRS-048.CAS.Partition.Freeze
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... FREEZE PARTITION` / `FREEZE` on a
[CAS]-backed table by publishing shadow-namespace refs that share live blobs
(no freeze-time byte copy of pool blobs), such that backup consumers can read
frozen file bytes through the disk API. The shadow namespace SHALL be scoped
under the creating server's `cas_server_root_id` so one server's `UNFREEZE`
cannot reach another server's snapshots in the same pool.

#### RQ.SRS-048.CAS.Partition.Unfreeze
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... UNFREEZE PARTITION` / `UNFREEZE` on
a [CAS]-backed table by removing the corresponding shadow refs without deleting
blobs still referenced by live table ownership.

#### RQ.SRS-048.CAS.Partition.Clone
version: 1.0

[ClickHouse] SHALL support partition / part clone paths used by attach, replace,
and freeze on [CAS] as ref publication (content-identical clones share blob
identity) rather than requiring a full byte copy of already-present content.

#### RQ.SRS-048.CAS.Partition.ClearColumn
version: 1.0

[ClickHouse] SHALL support
`ALTER TABLE ... CLEAR COLUMN ... IN PARTITION ...` on a [CAS]-backed
[MergeTree] table, resetting the column in that partition to default
values with the same logical outcome as on non-CAS storage.

#### RQ.SRS-048.CAS.Partition.ClearIndex
version: 1.0

[ClickHouse] SHALL support
`ALTER TABLE ... CLEAR INDEX ... IN PARTITION ...` on a [CAS]-backed
[MergeTree] table, removing skip-index files for that partition without
dropping the index description, matching non-CAS behavior.

#### RQ.SRS-048.CAS.Partition.RewriteParts
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... REWRITE PARTS` and
`ALTER TABLE ... REWRITE PARTS IN PARTITION ...` on a [CAS]-backed
[MergeTree] table, rewriting parts with current table settings and
preserving logical table contents.

#### RQ.SRS-048.CAS.Partition.Update
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... UPDATE ... IN PARTITION ...`
(and `IN PARTITION ID '...'`) on a [CAS]-backed [MergeTree] table as a
partition-scoped mutation, matching
[RQ.SRS-048.CAS.MergeTree.Alter.Update](#rqsrs-048casmergetreealterupdate).

#### RQ.SRS-048.CAS.Partition.Delete
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ... DELETE IN PARTITION ...`
(and `IN PARTITION ID '...'`) on a [CAS]-backed [MergeTree] table as a
partition-scoped mutation, matching
[RQ.SRS-048.CAS.MergeTree.Alter.Delete](#rqsrs-048casmergetreealterdelete).

#### RQ.SRS-048.CAS.Partition.MoveToDisk
version: 1.0

[ClickHouse] SHALL support
`ALTER TABLE ... MOVE PARTITION|PART ... TO DISK|VOLUME '...'` on
[CAS]-backed [MergeTree] tables when the destination is admitted by the
table storage policy. This is the documented migration path onto and off
[CAS] (including a cache-over-[CAS] disk named in the policy). Moving a
partition off [CAS] SHALL make the abandoned blobs eligible for [GC]
without deleting them synchronously. Commands that the partition
allow-list does not admit SHALL fail closed.

### Backup And Restore

#### RQ.SRS-048.CAS.Backup
version: 1.0

[ClickHouse] SHALL support `BACKUP` of [CAS]-backed [MergeTree] tables on Atomic
(UUID) databases via the pointer-holding backup path, preserving logical table
contents for a subsequent restore. This is ordinary [ClickHouse] `BACKUP`, not
the unshipped native [CAS] snapshot / mirror design
([RQ.SRS-048.CAS.Restrictions.Backup.NativeSnapshot](#rqsrs-048casrestrictionsbackupnativesnapshot)).

#### RQ.SRS-048.CAS.Restore
version: 1.0

[ClickHouse] SHALL support `RESTORE` of [CAS]-backed [MergeTree] table backups
produced through the supported backup path, restoring queryable logical contents
equivalent to the backed-up table.

### Shared Pool

#### RQ.SRS-048.CAS.SharedPool
version: 1.0

[ClickHouse] SHALL allow multiple servers to mount one [CAS] pool concurrently
when each server uses a distinct `cas_server_root_id`.

#### RQ.SRS-048.CAS.SharedPool.Deduplication
version: 1.0

[ClickHouse] SHALL deduplicate identical blob content across servers that share
one pool so that writing the same bytes does not require storing a second pool
copy of that blob.

#### RQ.SRS-048.CAS.SharedPool.IndependentRefs
version: 1.0

[ClickHouse] SHALL keep each server's refs independent under its
`cas_server_root_id` even when those refs resolve to the same shared blobs.

#### RQ.SRS-048.CAS.SharedPool.NodeCrash
version: 1.0

[ClickHouse] SHALL keep the shared pool and surviving servers consistent when
one pool member process crashes or is killed, without corrupting surviving
members' committed data.

### Replication Relink

#### RQ.SRS-048.CAS.Relink
version: 1.0

[ClickHouse] SHALL support fetch-by-relink for `ReplicatedMergeTree` replicas
that mount the same [CAS] pool: a receiving replica MAY publish a local ref to
the sender's manifest instead of transferring all part bytes, when the relink
protocol succeeds. The sender SHALL offer relink only when the receiver's
advertised `cas_pool_uuid` equals the sender disk's pool uuid.

#### RQ.SRS-048.CAS.Relink.HappyPath
version: 1.0

[ClickHouse] SHALL complete the relink happy path by publishing the receiver
precommit first, confirming the source still holds the offered manifest, then
promoting the receiver's committed ref. Only a literal confirm-proven answer
SHALL authorize promotion. Logical data SHALL be identical on both replicas
without requiring a full byte copy of already-present blobs.

#### RQ.SRS-048.CAS.Relink.DetachedFetch
version: 1.0

[ClickHouse] SHALL use relink when fetching a part or partition into detached
status on a same-pool replica (`FETCH PART` / `FETCH PARTITION` into detached),
subject to the same pool-identity rules as ordinary fetch.

#### RQ.SRS-048.CAS.Relink.CrossPool.ByteFallback
version: 1.0

[ClickHouse] SHALL fall back to ordinary byte fetch when sender and receiver do
not share the same [CAS] `cas_pool_uuid` (or relink confirmation is unavailable),
and SHALL not incorrectly claim a metadata-only relink in that case.
Byte-fetched files SHALL still content-address and deduplicate on arrival.

#### RQ.SRS-048.CAS.Relink.AttachPartitionFrom
version: 1.0

[ClickHouse] SHALL support `ATTACH PARTITION FROM` such that a subsequent
replication queue fetch on a same-pool replica MAY relink rather than copy
bytes, while preserving correct logical partition contents.

#### RQ.SRS-048.CAS.Relink.ReplacePartition
version: 1.0

[ClickHouse] SHALL support `REPLACE PARTITION` on a non-empty destination such
that a subsequent same-pool replica queue fetch MAY relink, while preserving
correct logical partition contents on all replicas.

#### RQ.SRS-048.CAS.Relink.VersionMix
version: 1.0

[ClickHouse] SHALL serve ordinary byte fetch to a peer that cannot participate
in the relink confirm protocol (protocol version below the confirm promise,
currently 11), instead of leaving that peer unable to obtain the part.

#### RQ.SRS-048.CAS.Relink.ConfirmRace
version: 1.0

[ClickHouse] SHALL refuse unsafe promotion when the source cannot prove it still
holds the offered manifest (unproven, missing cookie, timeout, or transport
error). The receiver SHALL throw and retry later and SHALL NOT promote or
immediately re-request bytes from that same uncertain source.

#### RQ.SRS-048.CAS.Relink.StalledPublish
version: 1.0

[ClickHouse] SHALL protect source blobs during a stalled publish and SHALL NOT
commit a receiver ref when promotion cannot complete safely.

#### RQ.SRS-048.CAS.Relink.RecursionBrake
version: 1.0

[ClickHouse] SHALL bound relink recursion: a byte-fetch fallback SHALL re-invoke
the fetch with relink disabled so the receiver stops advertising its pool uuid
and the relink path cannot be entered twice for one fetch.

### Garbage Collection

#### RQ.SRS-048.CAS.GC
version: 1.0

[ClickHouse] SHALL provide background garbage collection for a [CAS] pool that
reclaims objects no longer named by live ownership.

#### RQ.SRS-048.CAS.GC.NoLoss
version: 1.0

[ClickHouse] SHALL NOT delete a blob or manifest while any committed reference
or required ownership still names it. A dangling reference (live ref, missing
object) SHALL be treated as a data-loss invariant violation.

#### RQ.SRS-048.CAS.GC.ReclaimAfterDrop
version: 1.0

[ClickHouse] SHALL reclaim unreferenced blobs and part metadata after
`DROP TABLE ... SYNC` (and equivalent removal of the last owners) once [GC]
completes, returning the pool prefixes toward an empty / baseline state for
that dropped ownership. Reclamation SHALL require at least two full [GC] rounds
past condemnation (the grace period is measured in rounds, not acks); a single
manual `SYSTEM CAS GC RUN` SHALL NOT finish physical delete by itself.

#### RQ.SRS-048.CAS.GC.Run
version: 1.0

[ClickHouse] SHALL support a manual synchronous GC round via

```sql
SYSTEM CAS GC RUN [ON CLUSTER cluster_name] [disk_name];
```

When `disk_name` is omitted, one round SHALL run on every [CAS] disk on the
node. A manual run SHALL execute even if `SYSTEM CAS GC STOP` has paused the
background scheduler. The command SHALL return one row per disk it ran on
(the `cas_gc_log` `Finish` shape).

#### RQ.SRS-048.CAS.GC.Rebuild
version: 1.0

[ClickHouse] SHALL support reconstructing conservative GC baseline state via

```sql
SYSTEM CAS GC REBUILD [FORCE] [ON CLUSTER cluster_name] disk_name;
```

and/or offline `clickhouse-disks ... cas-gc-rebuild`. `disk_name` SHALL be
required (no fan-out across every [CAS] disk). Rebuild SHALL refuse when
existing `gc/state` looks healthy unless `FORCE` is given, and SHALL refuse
(regardless of `FORCE`) when another GC leader holds the disk's lease.
Rebuild SHALL write only the GC plane and SHALL fail closed rather than delete
uncertain content; temporary over-protection (leaks) is preferred over data
loss.

#### RQ.SRS-048.CAS.GC.Sharded
version: 1.0

[ClickHouse] SHALL support sharded GC (`cas_gc_shards > 1`) such that GC work is
partitioned across shard buckets, completion is sealed per generation, and
reclaim remains free of dangle/loss under multi-replica pool use.
`cas_gc_shards` SHALL be recorded in the pool at first lease acquire; a
mismatching config SHALL be refused at mount.

#### RQ.SRS-048.CAS.GC.RefSnaplog
version: 1.0

[ClickHouse] SHALL implement the snapshot+log ref protocol lifecycle so that
after insert churn and table drop, unreclaimed objects become reclaimable and a
read-only `cas-fsck` pass can report a clean pool for the inspected window.

#### RQ.SRS-048.CAS.GC.StopStart
version: 1.0

[ClickHouse] SHALL support pausing and resuming the background GC scheduler on
one disk without affecting reads or writes:

```sql
SYSTEM CAS GC STOP [ON CLUSTER cluster_name] disk_name;
SYSTEM CAS GC START [ON CLUSTER cluster_name] disk_name;
```

`disk_name` SHALL be required. `STOP` SHALL be idempotent, SHALL stop in place
(the same scheduler instance resumes on `START`), and SHALL NOT stop a manual
`SYSTEM CAS GC RUN`. `START` SHALL NOT automatically restore GC leadership.

#### RQ.SRS-048.CAS.GC.DryRun
version: 1.0

[ClickHouse] SHALL support a write-free preview of the next GC round's deletes
via `clickhouse-disks ... cas-gc-dryrun` against a disk opened read-only. The
preview SHALL NOT claim a live mount lease. Away from quiescence the preview
MAY over-report; its output MUST NOT be used as a delete source.

#### RQ.SRS-048.CAS.Fsck
version: 1.0

[ClickHouse] SHALL provide an offline filesystem check
(`clickhouse-disks ... cas-fsck [--detail]`) that classifies reachable,
dangling, pending-gc, awaiting-gc, and related object states for a [CAS] pool
without mutating the pool. The tool SHALL open the disk read-only and MUST NOT
claim a live server's mount. `dangling` SHALL be the class that means data
loss; `unreachable` / `pending_gc` / `awaiting_gc` SHALL mean objects still
moving through the condemn / graduate / delete pipeline. `--detail` SHALL be
the per-object listing; the SQL form is summary-only.

#### RQ.SRS-048.CAS.Fsck.Online
version: 1.0

[ClickHouse] SHALL support an online consistency check against a running,
mounted [CAS] disk via

```sql
SYSTEM CAS FSCK [ON CLUSTER cluster_name] disk_name;
```

`disk_name` SHALL be required. The scan SHALL re-validate findings against a
fresh authoritative read and SHALL need no quiesce. The command SHALL return
one summary row including at least `reachable`, `dangling`, `unreachable`,
`pending_gc`, and `awaiting_gc`.

### Day-2 Operations

#### RQ.SRS-048.CAS.DropPoolMember
version: 1.0

[ClickHouse] SHALL support decommissioning a dead pool member via

```sql
SYSTEM CAS DROP POOL MEMBER 'server_root_id' FROM DISK 'disk_name' [ON CLUSTER cluster_name];
```

and the offline twin `clickhouse-disks ... cas-drop-member <server_root_id>`.
The command SHALL refuse immediately if the member is still alive, SHALL fence
that `cas_server_root_id` from writing again, SHALL drop the member's table
namespaces, and SHALL retire the mount slot only after drains are confirmed.
It SHALL emit ordinary ref-edge deltas rather than inventing GC transitions,
and SHALL NOT synchronously reclaim shared blob content. The operation SHALL
be resumable. After `slot_removed = true` with no warnings, the member's
`cas_server_root_id` SHALL no longer appear in `system.cas_mounts` on any peer.

#### RQ.SRS-048.CAS.DropPoolMember.ReadonlyRejected
version: 1.0

[ClickHouse] SHALL reject the SQL `SYSTEM CAS DROP POOL MEMBER` command against
a read-only [CAS] disk. The offline `cas-drop-member` tool SHALL open the disk
read-only and MUST NOT claim a live server's mount (the pool-admin claim
happens internally).

#### RQ.SRS-048.CAS.Forget
version: 1.0

[ClickHouse] SHALL support a node-local assertion that a [CAS] disk is
permanently gone via

```sql
SYSTEM CAS FORGET [ON CLUSTER cluster_name] disk_name;
```

`FORGET` SHALL work on a disk that is not live. It is an assertion, not a proof
of erasure: the disk SHALL stay registered, further store-class access SHALL
return a typed error, and a server restart SHALL re-register the name. This is
distinct from `SYSTEM CAS DROP POOL MEMBER`, which retires one pool member's
identity across the whole shared pool.

#### RQ.SRS-048.CAS.Tools
version: 1.0

[ClickHouse] SHALL provide `clickhouse-disks` commands `cas-fsck`, `cas-inspect`,
`cas-gc-dryrun`, `cas-gc-rebuild`, and `cas-drop-member`. All five SHALL require
the disk to be opened read-only and MUST NOT claim a live server's mount.
`cas-inspect` SHALL decode one raw object-storage key to JSON.

### Fault Recovery

#### RQ.SRS-048.CAS.Fault.LostPartRecovery
version: 1.0

[ClickHouse] SHALL heal via ordinary lost-part recovery when a replica is
terminated after ZooKeeper multi / coordination commit but before durable [CAS]
publish completes, without requiring a fixed sync timeout as the sole success
oracle.

#### RQ.SRS-048.CAS.Fault.LazyLoad.S3Outage
version: 1.0

[ClickHouse] SHALL NOT automatically requeue a lazily loaded [CAS] table's
AsyncLoader job after a transient object-store error during first build. The
job MAY remain `FAILED`; operators SHALL recover by restarting the server or
issuing a fresh load for the table. This matches the documented one-shot
AsyncLoader design (not a [CAS]-specific retry path).

#### RQ.SRS-048.CAS.Fault.FailClosed
version: 1.0

[ClickHouse] SHALL fail closed under ambiguity on the write / promote / delete
paths: an operation that may have landed MUST NOT be treated as one that did
not, and uncertain deletes MUST be suppressed rather than assumed safe.

### Cache

#### RQ.SRS-048.CAS.Cache
version: 1.0

[ClickHouse] SHALL support composing a filesystem cache disk over a [CAS]
object-storage disk. Cache-over-[CAS] is the supported wrapper shape (see
[RQ.SRS-048.CAS.Disk.Configuration](#rqsrs-048casdiskconfiguration)).
`system.cas_mounts` SHALL list a row per configured disk name, so a cache
layered in front MAY appear twice under the same `cas_server_root_id`.

#### RQ.SRS-048.CAS.Cache.Hits
version: 1.0

[ClickHouse] SHALL serve repeated reads of the same [CAS] objects from the
local cache when cache-over-CAS is configured, without changing logical query
results.

### Observability And Access

#### RQ.SRS-048.CAS.Observability
version: 1.0

[ClickHouse] SHALL expose [CAS] operational state through documented system
tables, `CAS*` / `CASGC*` `ProfileEvents`, and the `SYSTEM CAS` command
surface so operators can observe pool membership, GC progress, and related
health signals.

#### RQ.SRS-048.CAS.Observability.SystemTables
version: 1.0

[ClickHouse] SHALL provide:

* `system.cas_mounts` — live per-mount view of every `cas_server_root_id` in
  the pool (not only the local server), including lease state and process-local
  GC-health columns (`is_leader` and related fields `NULL` on peer rows).
* `system.cas_gc_log` — per-round `Start` / `Finish` / `Phase` rows correlated
  by `round_id`, for both scheduled and manual (`SYSTEM CAS GC RUN`) rounds.
* `system.cas_log` — per-decision event log (blob puts, dedup adoptions, ref
  transitions, GC retire decisions, dangling-access findings).

`system.cas_log` and `system.cas_gc_log` SHALL be created when the matching
server settings are specified (enabled by default in the shipped `config.xml`).

#### RQ.SRS-048.CAS.Observability.ProfileEvents
version: 1.0

[ClickHouse] SHALL expose [CAS]-related `ProfileEvents` under the uppercase
`CAS` / `CASGC` prefix (blob, manifest, ref, mount-renewal/remount, and GC
counters) so operators can attribute pool I/O and diagnose mount-lease
recovery without reading server logs alone.

#### RQ.SRS-048.CAS.Access
version: 1.0

[ClickHouse] SHALL enforce a distinct `GLOBAL SYSTEM` privilege for each
`SYSTEM CAS` verb: `GC RUN`, `GC REBUILD`, `GC STOP`, `GC START`, `FSCK`,
`FORGET`, and `DROP POOL MEMBER`. A read-only fsck grant SHALL be grantable
without the destructive verbs.

### Restrictions And Non-Goals

#### RQ.SRS-048.CAS.Restrictions.BackendCapabilities
version: 1.0

[ClickHouse] SHALL require an object store that provides the capabilities
needed by the [CAS] mount and delete protocols, checked by a capability probe
at every writable mount. Required capabilities include read-after-write,
conditional create (`If-None-Match: *`) for manifests and control objects,
conditional overwrite (`If-Match`) for mount leases and `gc/state`,
unconditional blob publication, exact-token delete, ranged `GET`, and
resumable `LIST`. Bucket versioning SHALL be disabled (a versioned or
unanswerable versioning probe SHALL refuse a writable generation-token mount).
Object soft-delete MUST be disabled by the operator (not verified at mount).
When those capabilities are absent, mount SHALL fail closed rather than
silently run an unsafe configuration. `skip_access_check = true` SHALL be
refused on a writable generation-token (GCS) disk.

#### RQ.SRS-048.CAS.Restrictions.ZeroCopy
version: 1.0

[ClickHouse] SHALL NOT use classic zero-copy replication
(`allow_remote_fs_zero_copy_replication`) as the [CAS] sharing mechanism.
Same-pool sharing uses [CAS] refs and fetch-by-relink instead.
`supportZeroCopyReplication` SHALL report false for content-addressed disks.
[CAS] SHALL coexist with zero-copy: disks that do not set `metadata_type = cas`
keep their existing zero-copy behavior.

#### RQ.SRS-048.CAS.Restrictions.UniqueKey
version: 1.0

[ClickHouse] SHALL reject UNIQUE KEY / upsert [MergeTree] tables on non-local
disks, which includes [CAS]. UNIQUE KEY on [CAS] is out of scope while that
upstream fence remains.

#### RQ.SRS-048.CAS.Restrictions.NonMergeTree
version: 1.0

[CAS] is intended for the [MergeTree] engine family. Using a [CAS] disk as
generic storage for non-MergeTree engines, temporary-files disks, dictionary
SSD-cache backing, or Distributed spool is not a supported configuration and
MAY fail with `NOT_IMPLEMENTED` or an equivalent error.

#### RQ.SRS-048.CAS.Restrictions.Backup.TempHardLinks
version: 1.0

[ClickHouse] SHALL reject the temporary-hard-link `BACKUP` path on a [CAS] disk
(Ordinary / non-UUID databases that require that path). Operators SHALL use an
Atomic database so backup uses the pointer-holding path.

#### RQ.SRS-048.CAS.Restrictions.Backup.NativeSnapshot
version: 1.0

The git-shaped [CAS] `snapshot` / `mirror` / `fetch` / `restore` design is
approved but not implemented and SHALL NOT be treated as wired into the
`BACKUP` / `RESTORE` SQL surface. Ordinary pointer-holding `BACKUP` /
`RESTORE` of [CAS] tables remains
[RQ.SRS-048.CAS.Backup](#rqsrs-048casbackup) /
[RQ.SRS-048.CAS.Restore](#rqsrs-048casrestore).

#### RQ.SRS-048.CAS.Restrictions.Encryption
version: 1.0

An `encrypted` disk wrapping a [CAS] disk is not supported. `CREATE TABLE` on
such a disk MAY succeed; the first `INSERT` SHALL fail (documented as
`Autocommit writes are not supported for content part files on a
content-addressed disk`). Cache-over-[CAS] is the supported wrapper; encryption
at rest currently has to come from the object store.

#### RQ.SRS-048.CAS.Restrictions.Azure
version: 1.0

Azure Blob as a [CAS] backend is not supported. Azure's REST API documents
equivalent conditional headers, but ClickHouse does not wire a [CAS]
conditional dialect for Azure, and the capability probe does not validate it.

#### RQ.SRS-048.CAS.Restrictions.GCS
version: 1.0

Google Cloud Storage's generation-token implementation is present, but the
credentialed real-GCS release gate is pending. Suites against a fake GCS
service SHALL NOT be treated as proof of Google's multipart, native-copy, or
exact-delete wire behavior.

## References

* [Git]
* [GitHub Repository]
* [Revision History]
* [ClickHouse]
* [MergeTree]
* [CAS]
* [SRS]
* [Altinity/ClickHouse PR #2159](https://github.com/Altinity/ClickHouse/pull/2159)
* [CAS documentation](https://github.com/Altinity/ClickHouse/tree/antalya-26.6/docs/en/antalya/cas)
* [CAS integration test inventory](../docs/CAS-INTEGRATION-TESTS.md)
* [ClickHouse ALTER](https://clickhouse.com/docs/reference/statements/alter)
* [ClickHouse ALTER COLUMN](https://clickhouse.com/docs/reference/statements/alter/column)
* [ClickHouse ALTER PARTITION](https://clickhouse.com/docs/reference/statements/alter/partition)
* [SYSTEM CAS](https://github.com/Altinity/ClickHouse/blob/antalya-26.6/docs/en/sql-reference/statements/system.md)

[Git]: https://git-scm.com/
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/cas/requirements/requirements.md
[ClickHouse]: https://clickhouse.com
[MergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree
[CAS]: #terminology
[SRS]: #introduction
[GC]: #terminology
'''
)
