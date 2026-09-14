---
description: Detailed guide to content-addressed storage for MergeTree, including architecture, protocols, operations, validation, performance, and current limitations
sidebar_label: Content-addressed MergeTree storage
sidebar_position: 0
slug: /superpowers/CAS
title: Content-addressed storage for MergeTree
doc_type: guide
---

# Content-addressed storage for MergeTree {#content-addressed-storage-for-mergetree}

> **Regression SRS:** testable product requirements for this suite are in
> [`requirements.md`](requirements.md) (**SRS-048**). This file is the product/architecture guide
> (from Altinity/ClickHouse CAS docs), not the TestFlows requirements document.

> **Experimental status:** the core read/write/ref/GC paths are implemented, but the current live backlog
> still contains release-blocking correctness, lifecycle, scalability, and operational work. Read
> [Current readiness and live backlog](#current-readiness) before considering deployment.

## Guide map {#guide-map}

- [Why this storage exists](#why-this-storage-exists) — the problem, the Git analogy, and MergeTree
  immutability.
- [Configuration](#complete-s3-configuration) — a complete S3 disk and SQL example.
- [Objects and layout](#objects-in-cas-pool) — blobs, manifests, refs, namespaces, and physical keys.
- [Writer protocol](#writer-protocol) — mount authority, precommit, upload, and promotion.
- [Read protocol](#read-protocol) — ref resolution, manifest lookup, ranged reads, and caches.
- [Garbage collection](#garbage-collection) — source edges, condemnation, exact-token deletion, and rebuild.
- [Formats](#persisted-formats) — text codecs, envelopes, compatibility, and backend contract.
- [Performance](#caching-and-cost) — deduplication limits, caches, memory, and request cost.
- [Operations](#operations-and-observability) — system tables, manual GC, `fsck`, dry-run, and alerts.
- [Validation](#validation-method) — tests, formal models, scenarios, soaks, and concurrency checks.
- [Backup and DR](#backup-and-disaster-recovery) — current choices and the CAS-native design direction.
- [Readiness](#current-readiness) — implemented foundations, blockers, non-goals, and backlog.
- [Source coverage](#documentation-provenance) — how all 23 source documents are represented.

Status labels used throughout:

- **Implemented** — present in current code and covered by tests or runtime validation.
- **Partial** — the core exists, but a material gap remains.
- **Design only** — documented direction, not shipped behavior.
- **Open** — confirmed remaining work.
- **Rejected or superseded** — retained only to explain current decisions.

## Why this storage exists {#why-this-storage-exists}

A ClickHouse `MergeTree` table is stored as a collection of **parts**. A part is a directory containing
files such as compressed column data, marks, indexes, checksums, and metadata. On a conventional
object-storage disk, those files are stored under paths that belong to that table and that part. If two
replicas contain the same file, each replica normally owns another stored copy.

Content-addressed storage changes that physical representation. Instead of identifying a file by the path
where it was written, it identifies the file by a hash of its bytes:

```text
ordinary storage:       store/<table>/<part>/data.bin
content-addressed:      blobs/<hash-algorithm>/<hash-prefix>/<hash>
```

The hash becomes the file's stable identity. Writing the same bytes again produces the same identity, so the
existing object can be reused. A small metadata object describes the files in a part, and another small
record says which description currently belongs to a part name.

This is similar to Git:

- a **blob** contains file bytes;
- a **manifest** lists the blobs and inline files that make up one `MergeTree` part;
- a **reference**, usually shortened to **ref**, maps a part name to a manifest.

Only the references change as a table changes. Blobs and manifests are immutable.

### Why immutability follows from MergeTree {#why-immutable}

This is not an extra constraint that CAS imposes. It is a direct consequence of how `MergeTree` already
works. `MergeTree` never modifies a part in place. Every operation that changes data produces a **new
part** and then atomically swaps the name to point at the new one. The old part is dropped separately:

- **INSERT** — writes a new part from scratch.
- **MERGE** — reads N source parts, writes one new part, drops the N originals.
- **MUTATION** — reads the old part, writes a new part, drops the old one.
- **ALTER** (column change, codec change, etc.) — same: new part, drop old.

Because the bytes inside a part never change after they are written, CAS can safely hash those bytes once
and treat the hash as a permanent identity. If bytes could change in place, the hash would become stale and
the whole content-addressing model would break. `MergeTree`'s own invariant is the foundation that makes
it sound.

The three CAS objects map directly onto `MergeTree` concepts:

| MergeTree concept | CAS object | Properties |
|---|---|---|
| The bytes of one part file (e.g. `data.bin`) | **Blob** | Immutable; identified by hash; pool-global; never re-keyed |
| The complete set of files that make up one part | **Manifest** | Immutable; lists blobs and inline files; one manifest per part build |
| "Part name `all_1_1_0` currently means this set of files" | **Ref** | The only mutable object; updated atomically when a part is created, merged, mutated, or dropped |

A merge produces a new part, which gets a new manifest pointing at new (and possibly reused) blobs, and
then the ref for the merged part name is updated to point at the new manifest. The source part refs are
dropped. None of the existing blob or manifest objects are touched — they are either reused as-is or left
for garbage collection.

This is why the Git analogy holds precisely: Git commits and tree objects are immutable for exactly the
same reason. A commit is a snapshot, not a mutable state; a branch pointer is the only thing that moves.
`MergeTree` parts are snapshots of a row range, so the same three-layer structure applies naturally.

The feature is selected by setting `<metadata_type>content_addressed</metadata_type>` on an object-storage
disk. It does not introduce a new table engine. Ordinary `MergeTree` and `ReplicatedMergeTree` tables use
the disk through a storage policy.

### The pool and `server_root_id` {#pool-and-server-root-id}

Two identities must be distinguished before configuring a CAS disk:

- The object-storage `<endpoint>` identifies the shared **pool**. Servers that use the same bucket and
  prefix see the same pool-global blobs.
- `<server_root_id>` identifies one ClickHouse server's durable ownership tree inside that pool. It is
  required even for a single-server deployment.

For example, two replicas can mount the same pool while owning different roots:

```text
shared pool endpoint: s3://example-bucket/clickhouse/cas-pool/

server replica-01: server_root_id = production-01-replica-01
server replica-02: server_root_id = production-01-replica-02
```

The root ID is used as part of the namespace for refs, manifests, and ordinary files owned by that server.
For an Atomic table, a namespace is conceptually:

```text
<server_root_id>/store/<uuid-prefix>/<table-uuid>@cas@
```

Consequently, the two replicas keep independent refs even when both refs ultimately reach the same shared
blob:

```text
cas/refs/production-01-replica-01/store/...@cas@/...
cas/refs/production-01-replica-02/store/...@cas@/...
blobs/sha256/8f/8f...                              # shared by both
```

`server_root_id` is therefore neither a table name nor a blob identifier. It is the stable identity of a
server's ownership subtree. It must:

- be unique among servers that can mount the same pool concurrently;
- remain unchanged across restarts and upgrades;
- come from persistent deployment identity, normally a `{replica}` macro, rather than a random value;
- not be reassigned to another server unless the previous pool member has been explicitly decommissioned.

The pool records an owner binding and a monotonic writer epoch for each root ID. If two servers attempt to
write through the same root, or a root is bound to another server identity, mount safety fails closed instead
of allowing both writers to mutate the same ref namespace.

### Complete S3 configuration example {#complete-s3-configuration}

The following file can be placed in `config.d/cas_storage.xml`. Replace the endpoint, region, and macros
with values for the deployment. Credentials in this example come from the standard AWS environment
variables rather than being stored in the ClickHouse configuration:

```xml
<clickhouse>
    <!-- These values are different on every replica. -->
    <macros>
        <shard>01</shard>
        <replica>replica-01</replica>
    </macros>

    <storage_configuration>
        <disks>
            <cas_s3>
                <type>object_storage</type>
                <object_storage_type>s3</object_storage_type>
                <metadata_type>content_addressed</metadata_type>

                <!-- All replicas that share this CAS pool use exactly the same endpoint. -->
                <endpoint>https://example-bucket.s3.us-east-1.amazonaws.com/clickhouse/cas-pool/</endpoint>
                <region>us-east-1</region>
                <use_environment_credentials>1</use_environment_credentials>

                <!-- Required and unique for every server mounting the pool. Macros are expanded. -->
                <server_root_id>production-{shard}-{replica}</server_root_id>

                <!-- CAS requires one transaction for the complete part publication. -->
                <use_fake_transaction>0</use_fake_transaction>

                <!-- Optional settings shown with representative values. -->
                <blob_hash>sha256</blob_hash>
                <gc_enabled>1</gc_enabled>
                <gc_interval_sec>60</gc_interval_sec>
                <gc_shards>1</gc_shards>
            </cas_s3>
        </disks>

        <policies>
            <cas_s3_policy>
                <volumes>
                    <main>
                        <disk>cas_s3</disk>
                    </main>
                </volumes>
            </cas_s3_policy>
        </policies>
    </storage_configuration>
</clickhouse>
```

The object-store prefix in `<endpoint>` is the CAS **pool**. Replicas that should reuse blobs and relink
parts must use the same endpoint, while each replica must expand `<server_root_id>` to a distinct stable
value. Reusing one `server_root_id` on two servers is rejected because both servers would otherwise claim
the same ownership subtree. Changing a server's root ID after it has written data creates a different
namespace; therefore it must be treated as persistent deployment identity, not as an ephemeral hostname.

The disk must use real transactions. ClickHouse has to collect every file of a part before it can publish
the manifest and its ref atomically. The disk factory rejects `use_fake_transaction=true` because per-file
autocommit would remove that publication point.

The bucket must provide the conditional write and exact-version delete behavior required by CAS. Startup
probes validate these capabilities and fail closed when the backend does not provide them. The current
protocol also requires bucket versioning to be disabled; see the backend requirements below.

### Using the storage policy from SQL {#using-cas-storage-policy-from-sql}

A non-replicated table uses the configured policy like any other `MergeTree` table:

```sql
CREATE DATABASE IF NOT EXISTS cas_demo;

CREATE TABLE cas_demo.events
(
    event_time DateTime,
    user_id UInt64,
    payload String
)
ENGINE = MergeTree
ORDER BY (event_time, user_id)
SETTINGS storage_policy = 'cas_s3_policy';

INSERT INTO cas_demo.events VALUES
    ('2026-07-26 12:00:00', 101, 'first'),
    ('2026-07-26 12:00:01', 102, 'second');

SELECT *
FROM cas_demo.events
ORDER BY event_time;

-- Produces a new immutable part and retires the source-part refs.
OPTIMIZE TABLE cas_demo.events FINAL;
```

`ReplicatedMergeTree` uses the same storage policy. Deploy the XML on every replica with the same
`<endpoint>` and a different `<replica>` macro:

```sql
CREATE TABLE cas_demo.replicated_events
(
    event_time DateTime,
    user_id UInt64,
    payload String
)
ENGINE = ReplicatedMergeTree(
    '/clickhouse/tables/{shard}/cas_demo/replicated_events',
    '{replica}')
ORDER BY (event_time, user_id)
SETTINGS storage_policy = 'cas_s3_policy';
```

Keeper still coordinates `ReplicatedMergeTree` operations. CAS changes the disk representation and permits
a receiving replica that mounts the same pool to relink the sender's manifest instead of copying all part
bytes. If replicas use different pool endpoints, replication falls back to the ordinary byte-transfer path.

The configured objects can be checked after server startup:

```sql
SELECT name, path, type, object_storage_type, metadata_type
FROM system.disks
WHERE name = 'cas_s3';

SELECT policy_name, volume_name, disks
FROM system.storage_policies
WHERE policy_name = 'cas_s3_policy';

SELECT database, table, name, active, disk_name
FROM system.parts
WHERE database = 'cas_demo'
ORDER BY table, name;
```

## A small example {#small-example}

Suppose a part named `all_1_1_0` contains three files:

```text
columns.txt
data.bin
data.mrk2
```

Small files may be embedded directly in the manifest. Large files are hashed and stored as blobs. The
resulting representation is conceptually:

```text
ref "all_1_1_0"
    |
    v
manifest M
    columns.txt  -> inline bytes
    data.bin     -> sha256:8f...
    data.mrk2    -> sha256:31...
                       |
                       v
                 objects in blobs/
```

A read starts with the ref, loads the manifest, finds the requested file, and then either returns the inline
bytes or reads the corresponding range from the blob.

If a mutation rewrites only `data.bin`, the new manifest can keep the existing `data.mrk2` entry and point
to a new `data.bin` blob. If another replica uses the same object-storage pool, it can publish its own ref to
the same blobs instead of downloading and uploading the files again.

Content addressing does not guarantee that two independently built parts deduplicate. ClickHouse parts are
not always byte-for-byte reproducible: compression boundaries, codec settings, and time-dependent
expressions can differ. Cross-replica sharing works reliably when one replica produces the part and another
replica adopts that exact manifest. Carry-forward is most useful for `Wide` parts, where files can be reused
individually. A `Compact` part stores many columns together and is rewritten as one blob.

## The objects in a CAS pool {#objects-in-cas-pool}

A **pool** is the object-storage prefix used by one content-addressed disk. It contains data objects,
reference metadata, server identities, and garbage-collection state.

### Blobs {#blobs}

A blob contains the bytes of one large part file. Its complete identity is a `BlobRef`: the hash algorithm
plus the digest. The algorithm is part of the identity because the same digest bytes under two algorithms
name different objects.

The current code supports:

- `CityHash128`;
- `XXH3_128`;
- `SHA-256`.

A pool may contain blobs written with different algorithms. Blob keys therefore include the algorithm:

```text
blobs/<algorithm>/<first-two-hash-characters>/<full-hash>
```

For example:

```text
blobs/sha256/8f/8f...
```

The hash is calculated while bytes are written; it is not copied from `checksums.txt`. Each stored blob has
a CAS envelope around its payload and a neighboring freshness metadata object used by writers and garbage
collection. Blob objects are pool-global: they are not placed under a table, replica, or server directory.
That is what allows sharing across tables and replicas.

### Part manifests {#part-manifests}

A part manifest is an immutable description of one complete part. Each entry contains a relative file path
and one of two placements:

- `Inline`: the file bytes are stored inside the manifest;
- `Blob`: the entry stores a `BlobRef` and the file size, while the bytes live under `blobs/`.

Directories do not need separate objects. A nested path such as `p_sum.proj/data.bin` is simply another
manifest entry. A projection is therefore stored inside its parent part's manifest, not as a separate ref or
sub-manifest.

Entries are sorted by path. This allows binary search for one file and range lookup for a directory prefix.
The encoding is deterministic: identical logical input produces identical encoded bytes. Duplicate paths,
malformed entries, an unexpected namespace, or a manifest identity that disagrees with its ref are rejected.

The current persisted format is not protobuf. It is a zstd-compressed hybrid text format:

1. a JSON header identifying `cas_part_manifest` and its version;
2. a descriptor containing the manifest identity, namespace, and payload digest;
3. one sorted JSON record per file;
4. a record count;
5. a raw payload area for inline binary bytes.

The raw area exists because an inline file may contain arbitrary bytes that cannot safely be represented as
UTF-8 JSON text.

A manifest is identified by:

```text
namespace + writer_epoch + build_sequence + manifest_ordinal
```

Its object key is:

```text
cas/manifests/<namespace>/<writer-epoch>-<build-sequence>/<ordinal>.zst
```

The epoch and sequence components are fixed-width hexadecimal values in the current layout. The ordinal is
a six-digit per-build number. A manifest payload digest is integrity metadata; it is not the manifest's
object key, a blob identity, or a garbage-collection count.

### References {#references}

A ref gives a stable part name, such as `all_1_1_0`, its current meaning. Resolving a ref returns the identity
and size of the manifest plus the publication time. The manifest body is then loaded separately.

The original architecture document described one mutable JSON `RefShard` object containing a `refs` map and
a journal. That is no longer the persisted protocol. The current implementation uses immutable objects:

```text
cas/refs/<namespace>/_log/<transaction-id>.zst
cas/refs/<namespace>/_snap/<transaction-id>.zst
cas/refs/<namespace>/_cleanup/<transaction-id>
```

A log records a ref transaction such as publish, drop, precommit, promote, abandon, or namespace removal. A
snapshot contains the complete ref-table state through a particular log transaction. Recovery means loading
a valid snapshot and replaying the later logs. Writers, recovery, `fsck`, and snapshot construction all use
the same `RefTableState` transition code so they do not assign different meanings to the same log sequence.

The in-memory state for one namespace contains:

- committed part-name-to-manifest mappings;
- precommit bindings for builds that are not yet published;
- namespace lifecycle state;
- the greatest applied transaction identifier;
- an index of manifests that still have owners.

Snapshots keep recovery bounded. By default a new snapshot is considered after 256 logs or 1 MiB of log
data. Old logs are removed only after a covering snapshot is durable and garbage collection has safely
folded their ownership edges.

### Verbatim files {#verbatim-files}

Not every ClickHouse file is part content. Files that must retain ordinary path semantics are stored under
`roots/` rather than hashed into `blobs/`.

Files inside a CAS table namespace use:

```text
roots/<namespace>/_files/<relative-path>
```

Loose files at the disk mount point are mirrored directly below `roots/`. Path validation prevents an entry
from escaping its namespace with absolute paths, empty segments, or `..`.

### Pool and server identity {#pool-and-server-identity}

`_pool_meta` identifies the pool and records its format and capability floors. Its stable `pool_id` is also
the identity used to decide whether two replicas really share a pool. Comparing endpoint strings would be
unsafe: aliases can make one pool look different, while a shared proxy endpoint can make different buckets
look identical.

Each writable server also has a configured `server_root_id`. It is explicit rather than derived from the
local server UUID, because losing or regenerating that UUID must not silently move the server to another
namespace. Three objects protect a server root:

```text
gc/server-roots/<server_root_id>/owner
gc/server-roots/<server_root_id>/epoch
gc/server-roots/<server_root_id>/mount
```

`owner` permanently binds the root to a server UUID unless an operator decommissions it. `epoch` allocates a
new monotonic writer epoch for each writable incarnation. `mount` is the active lease and carries liveness
and build-watermark information. A writer that loses this lease or is superseded by another epoch stops
making mutable operations.

## Physical layout {#physical-layout}

The important pool prefixes are:

```text
<pool>/
  _pool_meta
  blobs/
    <algorithm>/<hash-prefix>/<hash>
    <algorithm>/<hash-prefix>/<hash>.meta
  cas/
    manifests/<namespace>/<writer-epoch>-<build-sequence>/<ordinal>.zst
    refs/<namespace>/_log/<transaction-id>.zst
    refs/<namespace>/_snap/<transaction-id>.zst
    refs/<namespace>/_cleanup/<transaction-id>
  roots/
    <namespace>/_files/<relative-path>
  staging/
    <mount-id>/...
  gc/
    state
    hb
    server-roots/<server_root_id>/{owner,epoch,mount}
    gen/<generation>/attempt/<attempt>/...
```

This layout separates frequently listed ref objects from the much larger set of manifests. Earlier versions
placed both below `roots/`; garbage collection then had to page through the entire manifest backlog merely
to discover active namespaces. The split makes normal discovery proportional to the ref metadata rather
than the number of historical manifests.

Blob bodies remain global, while refs and manifests belong to namespaces. A live table namespace normally
starts with the owning `server_root_id`; backup shadows use their own `shadow/<backup>/...` namespaces. This
gives each server independent ref ownership without giving up blob sharing.

The physical namespace mirrors ClickHouse's table path and marks the point where content-addressed files
begin with an `@cas@` suffix:

```text
Atomic table:      <server_root_id>/store/<uuid-prefix>/<uuid>@cas@
non-Atomic table:  <server_root_id>/data/<database>/<table>@cas@
```

`@cas@` is attached to the table-directory name; it is not a separate directory. It works like an archive
suffix: paths below it are represented by refs, manifests, and blobs. The logical disk view removes the
suffix, so ClickHouse and `clickhouse-disks` still see the ordinary table path. Loose paths outside this
boundary remain verbatim objects below `roots/`.

Staging objects have a separate top-level prefix. Normal blob scans list only `blobs/`, so they cannot
mistake a partially uploaded staging object for an orphan blob. A mount-specific staging sweeper owns that
cleanup.

### Virtual filesystem path contract {#vfs-path-contract}

CAS preserves ClickHouse's logical disk paths while storing part contents through refs and manifests:

- `@cas@` is a suffix on the table-directory component and marks the content-addressed boundary.
- `_files` and `_manifests` are reserved namespace segments and cannot be used as ordinary namespace
  components.
- `roots/<namespace>/_files/` holds verbatim namespace files; loose paths outside a CAS table remain opaque
  ordinary objects even if a component happens to resemble a part or shard number.
- There is no physical `_precommits` directory in the current design; precommits are operations in the ref
  protocol.
- Detached parts stay in the table namespace under refs named `detached/<part>`, rather than creating a
  sibling namespace that table drop would miss.
- Moving parts use a separate `moving/<part>` ref until the destination swap completes, preventing a crash
  from publishing the final live name too early.
- Projection files are nested paths inside their parent part manifest, not separate CAS objects or refs.

Raw object-store maintenance commands do not understand these rules. Deleting a `roots/`, `cas/refs/`, or
`cas/manifests/` subtree directly can bypass ref transitions and GC ownership accounting. Use ClickHouse
operations and CAS inspection/decommission tools rather than treating the bucket layout as an ordinary
filesystem.

## What happens during normal operation {#normal-operation}

A later chapter describes the write protocol precisely. At architecture level, publishing a part has four
important stages:

1. ClickHouse writes the part through a real disk transaction while CAS hashes files and records manifest
   entries.
2. CAS creates the immutable manifest and records a durable precommit binding. The precommit makes the
   build's dependencies visible to garbage collection before publication.
3. Missing blob bodies are uploaded or existing bodies are reused. If garbage collection has condemned an
   old incarnation, the writer must create a safe new incarnation rather than blindly reuse it.
4. CAS promotes the precommit into the committed ref for the part name.

The order is deliberate: a committed ref must never point to missing content. A failed build can leave
unreferenced blobs, manifests, or staging objects, but those objects are debris, not live table state.
Garbage collection can reclaim them later.

A read performs the reverse lookup:

1. resolve the part name in the namespace's ref-table state;
2. load and validate the manifest;
3. find the requested relative path;
4. return inline bytes or read the referenced blob.

Dropping a part removes its ref. It does not immediately delete shared blobs, because other refs may still
name the same content. Garbage collection derives ownership from the ref-log history and deletes an object
only after proving that no live owner remains.

For replication, two disks may relink only when their stable pool IDs match. The sender offers the manifest;
the receiver creates its own precommit, confirms that the sender still owns the exact source ref, and then
promotes. A non-CAS peer, a different pool, or an unavailable relink mechanism uses the ordinary byte path.

Two replicas may independently produce different compressed bytes for logically equivalent data. This is
not a correctness failure: each result has its own blobs and manifest, and ClickHouse's existing checksum
comparison verifies the logical content. It is a missed deduplication opportunity. For that reason, an older
proposal to put a CAS manifest hash into the Keeper part header was rejected. The manifest identity now
travels only in the interserver relink exchange, keeping generic replication metadata independent of the
disk implementation.

The current code routes `FREEZE` shadow paths into dedicated CAS namespaces and carries file entries through
the same transaction machinery. Creating the shadow does not duplicate pool blobs: it publishes shadow refs
that pin the selected manifests. The disk API still presents ordinary files below `shadow/`, so a native
backup or external consumer reading the frozen tree receives materialized file bytes through the CAS read
path. “No blob copy at freeze time” does not mean “backup tools receive only opaque refs.”

## What CAS provides, and what it does not {#cas-provides-and-does-not}

CAS provides:

- pool-wide deduplication of identical blob bytes;
- metadata-only transfer between replicas that share a pool;
- reuse of unchanged files when building a new `Wide` part;
- immutable data objects that are safe to cache;
- object-store-backed coordination without per-blob Keeper refcounts.

It does not promise:

- byte-identical output from independent part builds;
- per-file reuse inside a rewritten `Compact` part;
- immediate physical deletion when a part is dropped;
- safety on an object store that ignores conditional writes or exact-version deletes.

## Safety properties {#safety-properties}

The architecture is built around these properties:

- A committed ref resolves to a valid manifest whose files are present.
- A physical delete cannot remove an object that a committed ref still reaches.
- Once garbage collection condemns one physical incarnation, a stale exact-token delete for that
  incarnation cannot delete a later replacement.
- Uncertainty delays cleanup or blocks publication; it must not accelerate deletion.
- A writer epoch is never reused for the same `server_root_id`.
- Object storage contains the durable truth needed for recovery. CAS does not require a per-object Keeper
  catalog for correctness.

The formal-model chapter will state which models cover each property and where implementation behavior is
not yet fully represented.

## Backend requirements {#backend-requirements}

CAS relies on conditional object-store operations. In particular, deleting with the wrong object token must
fail. A stale garbage collector can then target the incarnation it observed without deleting a newer object
that has appeared at the same logical key.

Startup probes verify the required behavior instead of trusting a backend's name or documentation. A
backend that silently ignores the condition is rejected.

The architecture document records the following support expectations, which must be revalidated against the
current backend code and live probes before release:

- AWS S3 uses `ETag` tokens when bucket versioning is off.
- Azure Blob Storage uses write-sensitive `ETag` tokens and requires versioning and soft delete to be off.
- GCS uses generation-based tokens. Its binding and core live validation are implemented; production
  hardening and additional operational coverage remain.
- the tested MinIO OSS behavior ignored conditional delete and is therefore rejected;
- Ceph RGW has no accepted conditional-delete contract and is therefore rejected.

Bucket versioning is incompatible with the current one-live-object protocol. A delete marker would make
"delete this exact live incarnation" mean something different from physical removal. Versioned operation
would need a separate protocol based on version IDs.

## Designs that were replaced {#replaced-designs}

Several earlier designs explain why the current object model looks the way it does.

**Merkle tree objects.** An earlier design stored directory trees as a Merkle DAG and used the tree hash as
part identity. Putting generation information into tree identity caused a reclaimed child to force ancestor
rebuilds, and resolving generations added a `404`-then-`LIST` read path. Manifests replaced the tree layer;
there is no current `trees/` object family.

**Epoch-based reclamation.** An earlier garbage collector waited for all writers to move beyond a safe
epoch. One stuck writer could stop reclamation for the whole pool, and Keeper became part of correctness.
The current design uses object incarnation tokens, writer leases, durable ownership edges, and
exact-token deletion instead of a global quiescence point.

**Mutable integer refcounts.** Updating a counter for every blob reference would require distributed
read-modify-write operations and would turn missed or premature decrements into leaks or dangling data.
Current GC derives ownership from durable source edges in ref transactions. It does not store one mutable
integer beside each blob.

**A namespace registry.** A former `gc/registry` grew with every table ever created and made discovery cost
depend on historical namespaces. The current collector discovers namespaces by listing `cas/refs/`; the
registry no longer exists.

**Deriving storage identity from the server UUID.** Regenerating the UUID could silently strand the old
namespace. The explicit `server_root_id`, permanent owner anchor, and monotonic writer epoch replaced that
layout.

**Endpoint matching for relink.** Endpoint and prefix strings are not reliable pool identities. The minted
`pool_id` in `_pool_meta` replaced string matching.

**Separate projection objects.** Projections are always children of their parent part and are rebuilt with
it. Nested projection manifests would add recursive resolution and another format layer. A separate
`projections/` ref namespace would add an independently managed lifecycle that still had to follow the
parent. Both designs were rejected in favor of ordinary nested paths in the parent manifest.

**Pack slices.** An earlier format design reserved a placement for a byte range inside a larger pack object.
The current `EntryPlacement` enum contains only `Inline` and `Blob`; pack objects are not implemented.

CAS does not remove ClickHouse's existing zero-copy replication feature. It is a separate opt-in disk
metadata type. Existing zero-copy disks continue to use their own protocol.

## Source precedence and correctness intent {#source-precedence-and-intent}

This guide consolidates the durable information from the 23 documents in `docs/superpowers/cas/`.
Those source documents were written at different stages of development, so some describe current code,
some describe intended work, and some preserve rejected or superseded designs. The status labels are defined
in the guide map at the beginning of the document.

The intent document imposes a stricter hierarchy than an ordinary roadmap:

- demonstrated behavior outranks an argument that the code “should” be correct;
- a test must be capable of failing for the property it claims to prove;
- a failure must be visible at the transition where it occurs;
- ambiguity must retain data or block publication;
- protocol steps are not removed as speculative optimizations without measurements and a safety review;
- a plan is a hypothesis and must be amended when it conflicts with observed behavior or the no-data-loss
  invariant.

The implementation and the live `BACKLOG.md` take precedence when an older protocol chapter disagrees
with them. In particular, older descriptions of mutable root-shard objects, three-cursor GC, separate
retired runs, and writer acknowledgement floors describe previous generations of the design. The current
layout uses per-table immutable ref logs and snapshots, source-edge runs, and condemned-state summaries.

Readers can follow the document in three passes:

1. Read the object model, configuration example, and normal-operation overview to understand the feature.
2. Read the writer, reader, and GC sections to understand correctness.
3. Read the operations, validation, backup, and release-readiness sections before deploying it.

## Writer protocol in detail {#writer-protocol}

**Status: Implemented, with open transaction and throughput work described below.**

The writer's job is to ensure that a published part can always be read. It must not create a committed ref
until the manifest and every non-inline file it names are safe. Conversely, it may leave unreferenced debris
after a failed operation because debris is reclaimable and does not make acknowledged data unreadable.

### Mount startup and write authority {#writer-mount-startup}

Before ordinary writes are admitted, a writable mount establishes its identity and authority:

1. Validate the configured `server_root_id`.
2. Read or create `gc/server-roots/<server_root_id>/owner`, permanently binding the root to the server UUID.
3. atomically allocate a new monotonic writer epoch from `gc/server-roots/<server_root_id>/epoch`.
4. Claim `gc/server-roots/<server_root_id>/mount`.
5. Start lease renewal and the local write fence.

A restart of the same server receives a new writer epoch. A stale process from an older epoch must not
continue writing after a newer process takes ownership. The mount lease, owner binding, and local write
fence enforce that rule. If lease renewal becomes ambiguous or ownership is lost, writes stop; the system
does not guess that the old writer is still authoritative.

The mount heartbeat also carries the minimum active build sequence. GC uses that watermark when deciding
whether a manifest from a failed build is old enough to sweep. A build sequence is monotonic within a
writer epoch, so the minimum active sequence is a meaningful floor.

### One part write, step by step {#part-write-steps}

Consider a new part named `all_42_42_0` containing `a.bin`, `a.mrk2`, `columns.txt`, and
`checksums.txt`.

#### 1. Stage, classify, and hash files {#write-stage-files}

The disk transaction sees all part files before publication:

- large immutable files are written to staging while their bytes are hashed;
- small files can be retained as inline manifest entries;
- loose files outside the `@cas@` table boundary remain ordinary verbatim objects;
- all file paths are recorded for the manifest.

The current inline cap is 1 MiB per entry, with a 16 MiB aggregate inline cap per manifest. Exceeding the
per-entry threshold spills that file into a blob. A manifest that exceeds its hard limits fails before any
committed ref is published.

Blob hashing is streaming. The blob identity includes the hash algorithm, so a pool may distinguish
`cityhash128`, `xxh3-128`, and `sha256` objects. Hashing the same bytes under different algorithms creates
different `BlobRef` values.

#### 2. Create the immutable manifest {#write-create-manifest}

The writer creates an immutable manifest containing sorted path entries:

```text
columns.txt   -> Inline(...)
checksums.txt -> Inline(...)
a.bin         -> Blob(sha256:8f..., size=...)
a.mrk2        -> Blob(sha256:31..., size=...)
```

The manifest is self-validating: duplicate paths, malformed entries, wrong namespace, an identity mismatch,
and unsupported format versions are rejected. The manifest key contains the owning namespace, writer
epoch, build sequence, and ordinal. It is not named only by a content hash.

#### 3. Append a durable precommit {#write-precommit}

The writer appends a precommit operation to the table's immutable ref log. Conceptually:

```text
build B intends to publish part all_42_42_0 using manifest M
```

This is not yet a visible part. It is an ownership edge that tells recovery and GC that the build is in
progress. Recording intent before relying on existing pool objects closes the race where GC could otherwise
classify those objects as unowned while a writer is about to publish them.

If it is uncertain whether the append landed, the writer records that uncertainty and confirms the exact
ref state. It must not simply retry as though nothing happened because two successful appends with different
meanings would break ref ordering.

#### 4. Materialize or reuse blobs {#write-materialize-blobs}

For every blob entry, the writer either:

- conditionally creates the blob if it is absent;
- reuses the existing incarnation when the hash and freshness state permit it; or
- uploads a fresh, verified incarnation when the old one has been condemned.

The in-memory dedup cache is a performance hint only. A positive hint can avoid an expensive upload, but it
cannot authorize publication. Conditional object-store operations, freshness metadata, and the durable
precommit remain the correctness mechanisms.

Blob uploads for one part can run through the server-wide blob upload pool. Parallel upload removed the
single-threaded wide-part bottleneck, but commit of multiple parts still has serialization points in the ref
lane.

#### 5. Promote to a committed ref {#write-promote}

Promotion appends a ref transition that changes the precommit into the committed binding:

```text
part all_42_42_0 -> manifest M
```

The committed ref is the durable statement that the part exists. Readers ignore an unpromoted precommit.
Promotion verifies that the expected precommit still owns the part name. If ownership is missing,
superseded, or ambiguous, promotion fails closed.

The ordering invariant is:

```text
manifest + precommit ownership
    before
safe blob dependencies
    before
committed ref
```

#### 6. Clean local and remote debris {#write-cleanup}

Local staging files are removed after the transaction completes. A failed build can leave an immutable
manifest, a blob, a staging object, or an abandoned precommit. Background sweepers and GC reclaim these
after proving they are not live.

### Merge, mutation, rename, and removal {#writer-other-transitions}

- A merge creates a new part and publishes a new committed ref. Source-part refs are removed afterward.
- A mutation can carry unchanged files from an old `Wide` part into the new manifest. Changed files receive
  new blob references.
- A `Compact` part normally rewrites its combined data file, so file-level carry-forward is limited.
- A rename or part move is represented as ordered ref transitions; it must never create a moment where two
  conflicting owners can both publish.
- Removing a part appends a ref removal. It does not directly delete its manifest or blobs.
- `FREEZE` creates refs in a shadow namespace. It does not copy pool blobs at freeze time; reads of the
  shadow tree materialize ordinary file bytes through the disk API for backup consumers.

The architecture preserves ClickHouse's documented weak guarantee for `DROP PART` racing a merge. A
concurrent merge can publish a larger covering part, so dropping one mid-range source part does not promise
that its rows disappear if they were concurrently incorporated into the winning merged part. CAS must not
strengthen that operation by inventing an unconditional physical delete. The covering-tombstone design
represents removal as a zero-blob part ref and reconciles it with any real covering part that wins.

### Hash collision and corruption handling {#hash-collision-handling}

When a writer encounters an existing blob at the expected logical key, it validates that the stored
envelope and payload identity agree with the expected `BlobRef`. A mismatch is not treated as a dedup hit.
The key is quarantined or rejected with a hard corruption error. Silently reusing mismatched bytes would
serve corrupt or adversarial content through a valid committed ref.

### Transactions and MergeTree MVCC {#writer-transactions-mvcc}

CAS supports MergeTree transactions through a capability distinct from append support:
`supportsTransactionalMutableFiles`. CAS must not claim generic append support merely to enable
transactions because content-addressed files cannot be appended in place and MergeTree has separate
fallback behavior for append users.

MergeTree's MVCC engine remains storage-independent. Snapshot assignment, CSN/TID visibility, and
`DataPartsLock` serialization are unchanged. CAS satisfies the storage contract for files such as
`txn_version.txt`:

- transaction metadata is an ordinary manifest entry under the current all-part-files design;
- updating the creation CSN or removal TID on an already committed part stages the changed entry;
- the new manifest carries every unchanged entry forward and atomically repoints the part ref;
- a byte-identical rewrite becomes a no-op at the content layer;
- a rewrite against a missing ref fails with `LOGICAL_ERROR` rather than fabricating a one-file part.

An INSERT inside an open transaction can publish physical CAS ownership while remaining logically invisible
through `txn_version.txt`. `ROLLBACK` removes that ref, making the manifest and blobs GC-eligible. This is
the same “publish ownership, then remove ownership” lifecycle GC already understands.

A MergeTree transaction can span several parts, for example a merge output plus source parts whose removal
metadata is rewritten. `ContentAddressedTransaction` therefore keeps a staging map keyed by
`(namespace, ref)`, not one global current part. A temporary-to-final rename re-keys and merges staging state
for that part.

The disk layer does not promise one atomic object-store flip across every affected part. Local MergeTree
transactions also perform several filesystem operations; MVCC visibility comes from CSN/TID state.
If a crash leaves some physical refs published before the transaction becomes visible, recovery and GC
treat them as uncommitted ownership to remove safely.

The open `TXN-ONE-PIPELINE` work aims to make this ordering structurally clearer: CAS-specific staging
operations should not be split between eager and deferred queues in a way that allows program-order
inversion. The proposed generic `precommit` phase and final transaction shape are not yet the shipped
contract and must remain marked as open design.

### Publish-gate invariants {#publish-gate-invariants}

Regardless of the current physical representation, promotion must establish all of these:

- the expected precommit is still the live owner of the target ref;
- the manifest body matches its claimed identity and namespace;
- every blob dependency is present through a safe incarnation or is recreated from a trusted source;
- a token known to have been displaced or deleted cannot be admitted as current;
- replacing one physical incarnation records enough information that a stale exact-token delete cannot
  remove the replacement;
- directory or nested-file closure is complete before the part becomes committed.

The implementation realizes these rules through owner-liveness, source edges, freshness metadata,
incarnation tokens, and fail-closed promotion. Older models use names such as `deadTok`, current-state
revalidation, and `TreeDepsOK`; those are useful statements of the invariant but not necessarily literal
current C++ data structures.

### Replication by relink {#writer-replication-relink}

When sender and receiver report the same stable pool ID, the receiver can adopt the sender's manifest:

1. The receiver creates its own precommit.
2. The sender confirms that it still owns the exact source ref.
3. The receiver checks the response under the current protocol's enumerated failure rules.
4. The receiver promotes its own committed ref to the offered manifest.

This transfers metadata rather than part bytes. The sender's identity is not inferred from matching endpoint
text; the minted pool ID is authoritative. If the pools differ, confirmation is unavailable, or any proof is
ambiguous, replication uses the ordinary byte-transfer path.

The manifest ID is intentionally not stored in Keeper's generic part header. Keeper coordinates
`ReplicatedMergeTree`, while manifest adoption remains a disk-level protocol carried in the interserver
exchange.

### Writer failure behavior {#writer-failure-behavior}

The protocol treats failures according to their certainty:

- **Definitely did not land** — retrying is allowed.
- **Definitely landed** — continue from the observed durable state.
- **May have landed** — confirm the exact state; do not assume failure.
- **Dependency was condemned** — recreate from a trusted source or abort and retry.
- **Lease or ownership lost** — stop writes for that incarnation.
- **Manifest or ref bytes disagree with their claimed identity** — report `CORRUPTED_DATA`.

This is the practical meaning of “fail closed under ambiguity.”

### Open writer work {#writer-open-work}

The live backlog contains writer-side work that must not be confused with implemented behavior:

- completing the single transaction pipeline so staging and durable effects cannot be reordered;
- reducing remaining cross-part commit serialization;
- optimizing relink into `detached`;
- finishing out-of-band staging adoption for bulk load and backup tooling;
- making rare condemned-blob overwrite paths fully streaming;
- reducing ref-lane queue latency and wasted repoints during part removal;
- preserving explicit production checks for invariants currently obvious only from internal structure.

## Read protocol in detail {#read-protocol}

**Status: Implemented. Raw CAS reads are object-store bound; the implemented, opt-in cache-disk
composition adds local byte caching for workloads that need it.**

A read begins with a logical table path and filename. The disk routes the path to the table namespace and
then resolves one of four storage forms:

| File form | Read behavior |
|---|---|
| Inline manifest entry | Return bytes from decoded manifest memory |
| Blob entry | Open the content-addressed object and expose only its payload range |
| Verbatim namespace file | Read the ordinary object directly |
| In-flight transaction entry | Read from the transaction overlay |

### Resolve the part ref {#read-resolve-ref}

The requested part name is looked up in the table's reconstructed ref state. Recovery obtains that state
from a valid snapshot plus later immutable log entries. A missing ref means the part is not currently
published.

Ref-state caches are allowed to improve normal reads, but force-fresh callers bypass stale results.
Absence is not retained as a long-lived cache fact because a concurrent publish may create the ref.

### Load and validate the manifest {#read-load-manifest}

The committed ref yields a manifest identity. The reader:

1. Gets the manifest's object token.
2. Checks the manifest decode cache keyed by identity and token.
3. Fetches and decodes the body on a miss.
4. Verifies the body identity, namespace, entry ordering, checksums, and version.

A committed ref naming a missing manifest is not interpreted as an empty part; it is an
`INV-NO-DANGLE` violation and surfaces as an error.

### Locate and read the requested file {#read-file}

For an inline entry, the manifest already contains the bytes. For a blob entry, the manifest provides the
hash algorithm, digest, and logical size. The blob envelope has a fixed payload offset, so the reader opens
the required range and wraps it in a file view whose logical position starts at zero.

MergeTree still controls column pruning. CAS receives requests only for the files needed by the query, so
unrequested column files are not fetched merely because they share a manifest.

### Read-your-writes {#read-your-writes}

Part construction sometimes reads paths before the disk transaction commits, including projection and
mutation workflows. The transaction therefore maintains an overlay for files and directories staged by the
current operation. Reads first consult that overlay and only then fall through to committed ref state.

This overlay is not a second durable namespace. Aborting the transaction discards it; publishing the part
replaces it with the committed manifest/ref representation.

Committed projection directories are also virtual. A path such as
`all_42_42_0/proj.proj/data.bin` is one manifest entry under the parent part. Directory existence and
listing use prefix ranges over sorted manifest paths; no separate projection directory object is required.

Transaction metadata and other write-time reads that affect visibility use force-fresh ref resolution.
They must not accept the ordinary short TTL used by stale-tolerant query reads, because observing an old
`txn_version.txt` can make a transaction-visible part appear under the wrong CSN/TID state.

Normal readers are protected by the committed part/ref lifetime managed by MergeTree. A proposed ephemeral
reader-pin mechanism would be needed only if a future ref-less or cross-node read can outlive that ownership.
That mechanism is not currently part of the read protocol and should not be added without first identifying
a real unprotected reader path.

### Read caches {#read-caches}

There are three distinct cache layers:

1. **Ref-state and manifest decode caches** retain parsed metadata. They save decode and metadata GET work,
   but not column bytes.
2. **Part-folder view cache** retains an immutable logical directory view for a resolved manifest. Its
   memory is bounded by byte and entry limits; eviction affects performance only.
3. **Optional filesystem cache disk** caches object bytes locally. Cache-disk composition over CAS is
   implemented and integration-tested; enabling it is an operator choice. This is the layer that makes
   repeated scans approach local-disk latency.

The raw CAS disk deliberately does not claim that a warm data scan is free. Measurements found repeated raw
CAS reads remain object-store bound. A cache disk is useful for re-read-heavy workloads but can make a
one-shot cold scan slower because the first read also populates the cache.

Cache keys include immutable identity or object tokens. A stale cache entry may cause an extra request, but
must not authorize a delete or publish. Correctness never depends on retaining a cache entry.

### Read integrity and earlier failure lessons {#read-integrity}

The file-view wrapper must rebase its position after every operation on the underlying object-store buffer.
An earlier implementation incrementally tracked position and could return duplicated or missing granules
when the inner S3 buffer discarded and recreated its working range. The corrected implementation derives
the view position from the inner buffer after `next`, `seek`, and read-bound changes.

This incident is important because it demonstrates that a valid hash and manifest do not by themselves
prove reader correctness. Range translation, buffering, and position accounting are also part of the
trusted path.

### Read performance opportunities {#read-performance-opportunities}

Open improvements include:

- inlining small files by size while preserving useful column selectivity;
- reducing one ranged GET per requested blob file;
- making common small-part opens closer to one metadata GET;
- accurately accounting manifest memory in cache weights;
- avoiding repeated path parsing and debug-only mutexes on hot reads;
- verifying whether any ref-less reader requires an explicit ephemeral pin.

## Garbage collection in detail {#garbage-collection}

**Status: Implemented core with current correctness and scalability blockers listed in the live backlog.**

GC is responsible for reclaiming objects after refs stop reaching them. It is intentionally not part of the
foreground write transaction. The safety preference is asymmetric:

- retaining an unreferenced object wastes storage but preserves data;
- deleting an object that might still be referenced loses acknowledged data.

Therefore ambiguity always delays deletion.

### Ownership is a set of source edges {#gc-source-edges}

GC does not maintain a mutable integer refcount next to each blob. It derives ownership from durable ref
transitions. Conceptually, every manifest entry contributes an edge:

```text
(manifest identity, file path) -> blob identity
```

The source identity matters. Adding the same edge twice is still one edge; removing an absent edge is a
no-op. This set behavior makes replay idempotent and prevents repeated folding from driving an integer
counter negative.

The transient in-degree of a blob is the number of distinct live source edges that name it. A blob becomes a
candidate only after GC has observed an explicit transition from a non-empty edge set to zero. An arbitrary
unrecognized object is not immediately assumed safe to delete.

### How ref logs become GC state {#gc-fold}

For each table namespace, GC reconstructs ref transitions from immutable `_log` objects and covered
snapshots. It folds newly observed operations into sorted source-edge runs:

- publishing or activating a manifest adds its edges;
- removing a ref removes that manifest's edges;
- promoting a precommit to committed ownership preserves the same edges;
- repointing a ref removes the old manifest's edges and adds the new manifest's edges.

If an operation needs a manifest body that is missing or cannot be validated, the fold clamps before that
operation. It does not advance the cursor and pretend that the operation was processed. Destructive work is
suppressed while required coverage is incomplete.

The clamp must be visible to operators and `fsck`; silently treating a missing body as an empty closure
would under-count ownership. Similarly, GC must not fabricate a deletion token when a candidate HEAD returns
404. Absence can mean concurrent replacement, backend inconsistency, or an already-completed delete; the
round records the observed outcome and preserves the fail-closed state needed for another pass.

The current implementation represents condemned state inside the source-edge run with sentinel rows. A fold
seal summarizes the produced runs and records per-shard condemned totals, pending totals, and the oldest
non-pending condemnation round. Older documents that describe a separate `RetiredSet`, `CART` object,
`retired_refs`, or a three-cursor merge preserve a superseded representation.

### GC leader and attempts {#gc-leader}

Servers sharing a pool may all run GC schedulers, but a lease normally elects one leader. An advisory
heartbeat prevents a follower from stealing the lease merely because the leader is busy in a long round.

Safety does not rely solely on perfect leader uniqueness. Round artifacts are attempt-scoped:

```text
gc/gen/<generation>/attempt/<lease-sequence>/...
```

A deposed leader can leave immutable artifacts under its attempt, but they do not become authoritative
unless the single `gc/state` transition adopts that attempt. This converts split-brain work into reclaimable
debris instead of conflicting state.

### A normal GC round {#gc-round}

The exact implementation evolves, but the current conceptual round is:

1. **Acquire or confirm leadership.**
2. **Inspect server mounts.** Live mounts remain authoritative; expired mounts can be fenced so an old
   process cannot resume writes unnoticed.
3. **Discover ref namespaces and new logs.**
4. **Fold transitions.** Build a new source-edge view without advancing across incomplete input.
5. **Classify zero-edge objects.** Record condemned state and the exact physical token observed.
6. **Process objects condemned by earlier rounds.** Re-check required state and attempt exact-token
   deletion only after the protocol's delay.
7. **Publish deterministic artifacts.**
8. **Atomically adopt the new generation through `gc/state`.**
9. **Sweep safe debris.** This includes orphan manifests, stale staging, superseded attempts, and old
   generations within retention rules.

Idle rounds can reuse parent run references rather than reading and rewriting an unchanged full run.
Streaming run readers keep resident memory proportional to a block rather than the complete edge set.

### Condemnation is not deletion {#gc-condemnation}

A condemned blob body may still exist and may even be reusable after safe resurrection. Condemnation means
GC proved zero in-degree for the observed state and wrote freshness metadata. Physical deletion happens in
a later phase.

The physical operation is an exact-token delete:

```text
delete key K only if it is still physical incarnation token T
```

If another writer replaced `K` with a fresh incarnation, the token differs and the stale delete fails. GC
records the object as spared or replaced and re-evaluates it later.

Backends must report whether a delete created a marker rather than removing the exact live object. Under the
current unversioned protocol, a created delete marker is a contract violation and must fail loudly; it must
not be counted as successful reclamation.

### Publication order for destructive bookkeeping {#gc-publication-order}

Decision-bearing artifacts are written before the adopted `gc/state` pointer moves to them. A reader that
observes a new round or generation must be able to load the exact sealed runs and summaries that justify its
destructive decisions.

If a process writes artifacts and then loses the `gc/state` compare-and-swap, those artifacts belong to an
unadopted attempt and cannot influence writers or later deletion. Cleanup may remove them afterward. This
publish order is the GC analogue of manifest/precommit-before-committed-ref on the writer side.

### The race: GC versus a new reference {#gc-new-reference-race}

The dangerous interleaving is:

```text
GC observes no owner for manifest M
writer publishes a ref to M
GC deletes M or its blobs
```

Several layers close this race:

- a writer creates durable precommit ownership before promotion;
- fold does not advance past an unresolved precommit;
- promotion requires the expected precommit still to be live;
- destructive GC work is based on adopted, covered state rather than an unadopted attempt;
- blob deletion targets the exact observed physical token;
- uncertainty suppresses destruction.

The current fetch-handoff protocol adds source confirmation: a receiver adopting another replica's
manifest asks the sender to confirm the exact source ref before receiver promotion.

### Manifest and namespace cleanup {#gc-manifest-cleanup}

Dropping a ref eventually makes its manifest ownerless. The orphan-manifest sweeper can remove it only after
the writer watermark proves no older in-flight build can still publish it. Namespace cleanup similarly
requires lifecycle state and complete ref processing; emptiness alone cannot distinguish a dropped table
from a newly created empty table.

Removing a dead server from a pool is an explicit operator action, not an inference made by GC. Pool-member
decommissioning fences the member, drains its refs and debris, and removes its owner/epoch/mount control
objects only after a clean pass. A partial failure keeps enough state for a safe retry.

### GC recovery and rebuild {#gc-recovery}

`gc/state` and generation artifacts are derived bookkeeping. If the baseline is missing or inconsistent,
regular GC fails closed and deletes nothing. An operator can inspect the pool and run a rebuild:

```sql
SYSTEM CONTENT ADDRESSED GC REBUILD <disk>;
```

For offline tooling:

```bash
clickhouse-disks --disk <disk> ca-gc-rebuild
```

`FORCE` bypasses selected health refusals and must be treated as disaster recovery, not as routine GC. The
rebuild reconstructs a conservative baseline from surviving durable ownership information. Conservative
over-protection can leak objects temporarily; it must not invent a reference or delete uncertain content.

### Current GC blockers and known limitations {#gc-current-limitations}

The live backlog, not older “DONE” tables, is authoritative for current readiness. Important open items
include:

- **LIST-as-journal completeness:** advancing a fold cursor over records merely observed through paginated
  `LIST` lacks a complete-enumeration proof. This is a release-blocking correctness issue under active
  investigation.
- **Unmatched-minus-one retention leak:** a narrow fetch/ref lifecycle can leave residual source edges and
  prevent reclamation. The obvious “re-issue the removal” fix is unsafe because it can wedge the state
  machine; reconciliation must preserve set semantics.
- **Fold intake throughput:** measured intake can fall behind ref-log arrival, causing rounds to grow
  progressively longer.
- **Repeated manifest reads:** one manifest body can be fetched several times while folding related logs.
- **Orphan-sweep fixed cost:** it can dominate median idle-round time.
- **Large-pool `fsck` budget:** a flat timeout can expire precisely when the pool is large enough to need
  diagnosis.
- **Incremental snapshots:** changed hot shards can still rewrite large source-edge runs; delta runs and
  compaction remain a design direction.
- **Long clamp liveness:** suppression is safe, but a poison late log can starve progress and reporting.

These issues are primarily retention, performance, and observability problems unless explicitly marked as
data-loss class. `dangling` means referenced but absent and remains the stop-the-world signal.

## Persisted formats and compatibility {#persisted-formats}

**Status: Current codecs are implemented; older codec proposals are historical design input.**

CAS stores several kinds of object, each with a distinct mutability and integrity contract:

| Family | Examples | Mutability | Main validation |
|---|---|---|---|
| Blob payload | Large part files | Immutable | Content digest, envelope, physical token |
| Part manifest | File map for one part | Immutable | Self identity, namespace, sorted paths, payload digest |
| Ref log and snapshot | Ref transitions and recovered table state | Immutable new-key records | Transaction order, checksums, limits |
| Pool/server control | `_pool_meta`, owner, epoch, mount | Small controlled updates | Format/version checks and conditional writes |
| GC artifacts | Runs, seals, outcomes, state | Mostly immutable attempts plus small adopted pointer | CRCs, deterministic bytes, exact references |
| Verbatim files | Loose non-part objects | Path-addressed | Ordinary object-storage semantics |

### Blob envelope {#blob-envelope}

A blob object wraps raw part-file bytes in a fixed-size CAS header region followed by the payload. The
header is canonical text beginning with a JSON object such as `{"type":"cas_blob","v":...}`; it is not a
legacy binary magic header. It records:

- object type and format version;
- hash algorithm and digest;
- logical payload size;
- physical incarnation identity;
- integrity information needed to reject corrupt or unsupported input.

The content identity is computed from the logical payload, not from the physical incarnation fields. CAS can
therefore replace a condemned physical incarnation with a fresh token without changing the blob's logical
key.

Readers must not expose envelope bytes as part-file bytes. They locate the payload offset and provide a
bounded logical file view.

### Manifest format {#manifest-format}

The current manifest is a zstd-compressed hybrid format:

1. a JSON header naming the `cas_part_manifest` format and version;
2. a descriptor containing identity, namespace, and payload digest;
3. sorted records for inline and blob entries;
4. an entry count;
5. a raw payload zone for arbitrary inline bytes.

The raw zone avoids pretending binary data is UTF-8 JSON. Duplicate paths, malformed placement, count
mismatch, digest mismatch, oversized inline payload, and unsupported version all fail closed.

### Ref logs and snapshots {#ref-format}

Ref transitions are immutable transaction objects. Snapshots contain complete recovered state through a
specific transaction, and later log entries replay on top. The state machine is shared by writers, recovery,
snapshot construction, and `fsck` so that the same operation does not receive different meanings in
different components.

Decoders enforce object and operation size limits before allocation. Corrupt lengths must be rejected before
indexing memory; this requirement came from an earlier run-reader review that found an unchecked record
count could turn corruption into an out-of-bounds read.

### Run files and deterministic artifacts {#run-file-format}

Large GC data sets use block-framed record streams with:

- a typed header;
- bounded blocks;
- per-block checksums;
- a sparse footer index;
- a footer checksum;
- streaming and ranged-read support.

Sealed artifacts are deterministic. If two attempts write the same deterministic key, byte equality is
accepted as idempotent replay; different bytes at that key are `CORRUPTED_DATA`.

### Versioning rules {#format-versioning}

Every persisted family identifies its format and version. Readers:

- accept supported versions;
- validate reserved and critical fields;
- ignore only explicitly non-critical unknown extensions;
- reject newer incompatible versions rather than guessing.

The pool may admit multiple blob hash algorithms, but enabling a new algorithm in an existing pool requires
an explicit opt-in. Hash algorithm is part of blob identity; changing the default does not reinterpret old
objects.

The project is pre-release and deliberately avoids a permanent dual-protocol compatibility layer for
formats no production release has promised. Before the first persisted-data release, the format and upgrade
roster must be frozen and recorded in `_pool_meta`.

### Codec history {#codec-history}

The codec documents describe three generations:

- Early ad-hoc and mixed JSON/binary formats exposed inconsistent headers, weak size limits, and duplicated
  parsing rules.
- Proposal v2 introduced a universal preamble and three broad body families.
- Proposal v3 refined the design into role-based control objects, record streams, manifests, blob
  envelopes, integrity boundaries, deterministic encoding, and explicit dispositions.

`Formats/README.md` and the current codec code are authoritative for implemented type strings, fields, and
evolution rules. `codecs.md` is a historical codec audit whose protobuf-era inventory is partly stale. The
v2 and v3 proposal documents remain useful rationale, but no proposal overrides current decoders or wire
tests.

### Backend abstraction {#backend-abstraction}

The CAS backend wraps object storage behind operations with explicit semantics:

- get full or ranged bytes;
- list with pagination;
- create only if absent;
- compare-and-swap by token;
- overwrite under an expected token;
- delete the exact observed incarnation;
- stream immutable bodies.

The local in-memory and filesystem backends are useful for deterministic tests, but production acceptance
depends on the native backend honoring the same wire-level outcomes. A mock that reports conditional-delete
success while deleting the wrong object would make the entire GC proof irrelevant.

## Caching, memory, and object-store cost {#caching-and-cost}

**Status: Core caches and parallel blob upload are implemented; several request-count reductions remain
open.**

CAS exchanges storage duplication for metadata and object-store operations. A useful performance analysis
separates:

- bytes uploaded;
- billed requests;
- latency per request;
- local memory retained by metadata views;
- background GC work;
- duplicate work avoided through hashes and relinking.

### Write-path deduplication {#write-deduplication}

Let:

- `f` be the number of blob-backed files in a part;
- `D` be the number already present in the pool;
- `f - D` be novel blobs.

The ideal byte cost is proportional to `f - D`, not `f`. Request cost still includes metadata operations and
checks needed to prove whether reuse is safe.

The write path combines:

- a bounded known-present dedup cache;
- optional HEAD-before-PUT for sufficiently large blobs;
- conditional create for novel content;
- per-hash freshness reads when adopting existing content;
- parallel upload for independent files;
- one manifest and ordered ref-log transitions.

A cache hit saves work only when the backend confirms the reusable state. Concurrent writers can race on the
same blob key; one creates it and the other safely adopts the winner.

### Why large merged parts rarely deduplicate across tables {#cross-table-dedup}

CAS deduplicates physical file bytes, not SQL rows. Background merges normally produce large compressed
files. Two tables containing logically equal rows can still differ in:

- schema and serialization streams;
- codecs and compression boundaries;
- part granularity;
- marks and indexes;
- partition and sorting layout;
- time-dependent expressions;
- merge history.

Consequently, independently built large files rarely hash identically across unrelated tables. Cross-table
deduplication is opportunistic. Reliable savings come from:

- replicas adopting the exact same manifest;
- retries encountering identical already-uploaded bytes;
- `FREEZE` and backup refs retaining the same manifest;
- mutations carrying unchanged files from a `Wide` part;
- repeated small system-log or metadata content when bytes actually match.

Automatic background merges use the ordinary MergeTree selector. The default
`max_bytes_to_merge_at_max_space_in_pool` is 150 GiB of source parts and corresponds only roughly to a
maximum automatic output part. `OPTIMIZE FINAL` can exceed it. CAS does not change these merge rules.

### Blob count per part {#blob-count-per-part}

One active part has one committed ref and one manifest, but no fixed blob count:

```text
one part ref
  -> one manifest
       -> N blob entries
       -> M inline entries
```

For a `Wide` part, large data streams for individual columns generally become separate blobs. Complex types
can have several physical streams per logical column. Marks and indexes become blobs only when they exceed
the inline threshold.

For a `Compact` part, multiple columns share a combined data file, so one large blob often dominates. It
can still have additional mark, index, projection, or other large files. Blob count is therefore a property
of the physical part layout, not of row count or total part size.

### Part-folder view cache {#part-folder-cache}

The part-folder cache retains the immutable logical directory derived from a resolved manifest. A cache
entry is safe because its key includes immutable manifest identity and physical token. It is bounded by:

- total byte budget;
- maximum entry count;
- maximum single-entry weight.

Oversized views bypass retention. Disabled mode still uses the same access facade without retaining entries,
so code does not fork into separate correctness implementations.

Cache invalidation follows ref identity changes. Explicit “invalidate everything” calls are avoided where a
new immutable key naturally makes old entries unreachable. Eviction or a disabled cache can only add
requests.

The original cache RFC also records design constraints:

- do not hold a hot mutex across network I/O;
- avoid duplicate full-manifest allocations;
- prevent a debug decision journal from serializing every read;
- keep blob-byte caching separate from manifest-view caching;
- expose hit, miss, wait, eviction, bypass, and retained-byte metrics.

### Optional filesystem cache {#filesystem-cache}

A standard ClickHouse cache disk can wrap CAS object storage. This composition is implemented and tested.
The CAS metadata storage remains authoritative; only immutable object bytes use the read-through filesystem
cache.

This composition is valuable when the same data is scanned repeatedly. It is not automatically beneficial
for one-shot scans because the cold read pays both remote fetch and local population.

### GC cost shape {#gc-cost}

GC cost has several axes:

- ref-log discovery and intake;
- manifest bodies read while deriving source edges;
- source-edge run reads and writes;
- candidate token checks;
- exact deletes;
- orphan sweeps;
- generation retention cleanup.

Reference-parent runs and skip-unchanged rounds reduce idle work. Streaming readers bound memory. Hot pools
can still rewrite large runs and repeatedly read manifests. Current measurements indicate ref-log intake and
orphan sweep are more important targets than lease election.

### Practical tuning guidance {#performance-tuning}

- Keep `gc_interval_sec` moderate rather than forcing nearly continuous rounds; idle-skip makes quiet pools
  cheap, while hot ref logs need enough service capacity.
- Size `content_addressed_blob_upload_pool_size` and object-store connections together. More upload threads
  than backend permits create 503/retry storms rather than throughput.
- Use `dedup_head_first_min_bytes` to avoid streaming large known-present bodies, but do not add or remove
  protocol checks without measurement.
- Use a filesystem cache for repeated reads.
- Monitor ref-log backlog and per-phase GC duration before changing GC cadence.
- Keep scratch storage large enough for staged files and configure the condemned-upload memory budget for
  the chosen upload concurrency.
- Treat `sha256` as a stronger collision choice with extra CPU cost; choose the pool policy deliberately.

## Operations and observability {#operations-and-observability}

**Status: Core logs, mount view, manual GC, inspection, `fsck`, dry-run, rebuild, and member
decommissioning exist. Some control commands and views remain open.**

### System tables and logs {#system-tables}

The primary surfaces are:

- `system.content_addressed_mounts` — one row per mounted server-root slot, including lifecycle and GC
  health;
- `system.content_addressed_log` — per-event audit records for refs, blobs, mounts, and GC decisions;
- `system.content_addressed_garbage_collection_log` — round and per-phase GC records;
- `system.disks`, `system.storage_policies`, and `system.parts` — ordinary disk/policy/part placement.

Useful mount query:

```sql
SELECT *
FROM system.content_addressed_mounts
ORDER BY disk_name, server_root_id;
```

Recent GC outcomes:

```sql
SELECT
    event_time,
    disk_name,
    round,
    phase,
    outcome,
    duration_ms,
    error
FROM system.content_addressed_garbage_collection_log
ORDER BY event_time DESC
LIMIT 100;
```

Trace one blob:

```sql
SELECT
    event_time,
    event_type,
    namespace,
    ref_name,
    object_hash,
    token,
    outcome,
    reason,
    detail
FROM system.content_addressed_log
WHERE object_hash = '<hash>'
ORDER BY event_time;
```

Trace one part ref:

```sql
SELECT
    event_time,
    event_type,
    namespace,
    ref_name,
    outcome,
    reason,
    detail
FROM system.content_addressed_log
WHERE ref_name = '<part_name>'
ORDER BY event_time;
```

An error row, a missing finish for a started round, a wedged namespace, a lost mount, or a growing unmatched
removal count requires investigation. `NotALeader` on non-leader schedulers is expected.

### Manual GC {#manual-gc}

Run one synchronous round:

```sql
SYSTEM CONTENT ADDRESSED GC RUN cas_s3;
```

Manual and background rounds must share the scheduler's serialization and leadership state. Repeatedly
constructing unrelated leaders would prevent correct lease observation and could duplicate unsupported work;
tests and reviews explicitly guard this class.

### Filesystem check {#ca-fsck}

Run offline or through a dedicated read-only configuration:

```bash
clickhouse-disks --disk cas_s3 ca-fsck
clickhouse-disks --disk cas_s3 ca-fsck --detail --timeout 600
```

Important classes:

| Class | Meaning | Response |
|---|---|---|
| `reachable` | Named by live ownership and physically present | Healthy |
| `dangling` | Named by a live ref but physically absent | Data-loss invariant violation; stop and investigate |
| `pending-gc` | Condemned or queued for later physical deletion | Normally transient |
| `awaiting-gc` | Ref removal has not yet folded through the GC view | Normally transient |
| `unaccounted` | Present but outside known reachability and GC state | Re-run after quiescence; persistent values need investigation |
| `stale_edge` | GC ownership edge survives without matching current ref ownership | Retention or fold-consistency signal |
| `unreachable` | Aggregate present-but-unreferenced class, including debris | Inspect detailed subtype and persistence |

Use the terms precisely: a “stuck blob” normally means present-but-unreferenced
(`awaiting-gc`, `pending-gc`, `stale_edge`, or persistent `unreachable`). It does **not** mean
`dangling`. `dangling` is the opposite and more severe condition: a committed reference exists but the
required object is missing.

Do not decide health from a flat blob count. A byte-fetch fallback can deduplicate and leave the count flat,
so it does not prove metadata relinking occurred. Likewise, an empty observation is not evidence unless the
test proves it actually inspected the intended objects.

A read-only inspection disk over the same pool should not be placed in the live server's normal storage
policy configuration, because MergeTree disk discovery can see the same parts on an unexpected disk. Use a
standalone `clickhouse-disks` configuration.

### GC dry run {#ca-gc-dryrun}

Preview candidate deletes without writes:

```bash
clickhouse-disks --disk cas_s3 ca-gc-dryrun
```

The preview must be a subset of objects independently classified as unreferenced by the reachability walk.
Any candidate reachable from a committed ref is a correctness failure.

### Inspect persisted objects {#ca-inspect}

`ca-inspect` decodes control objects, manifests, ref records, and source-edge runs for forensic analysis.
Use it when summary counters cannot explain why one blob remains pinned. Inspection must be read-only and
must not claim a live mount slot.

### Rebuild derived GC state {#operator-gc-rebuild}

Use rebuild only when regular GC has failed closed because the adopted baseline is missing or corrupt:

```sql
SYSTEM CONTENT ADDRESSED GC REBUILD cas_s3;
```

or offline:

```bash
clickhouse-disks --disk cas_s3 ca-gc-rebuild
```

Run `ca-fsck` before and after. Do not broadcast `FORCE` casually across every disk.

### Decommission a pool member {#decommission-pool-member}

A server that will never return must be explicitly decommissioned so its stale precommits, mount slot, and
ownership state do not pin data forever. The operation refuses a live member and retains retryable control
state after partial failure.

Do not reuse its `server_root_id` on a replacement node before completing this lifecycle.

### Alerting principles {#alerting}

Alert on:

- any `dangling` object;
- mount ownership conflict or terminal lease loss;
- repeated GC errors;
- a started phase with no finish beyond its expected duration;
- increasing ref-log backlog or round duration;
- persistent `unaccounted` or `stale_edge` counts;
- unmatched removal deltas;
- `fsck` timeout or partial scans;
- ref-lane wedge indicators;
- conditional-operation capability probe failure.

Do not alert merely because some blobs await GC or because a non-leader scheduler reports `NotALeader`.

## Validation and engineering method {#validation-method}

CAS correctness is not based on one test suite. The project combines focused C++ tests, SQL and integration
tests, adversarial scenarios, long-running soaks, independent inspection, formal models, and deliberately
broken negative controls.

### Test-driven protocol development {#test-driven-development}

Behavior-changing work begins with a test that can fail for the intended reason. Important examples include:

- cancellation must remove staging and not publish a partial part;
- a shared blob must survive when one source part disappears;
- promotion must fail if its precommit ownership was reclaimed;
- concurrent leaders may duplicate work but must not over-delete;
- ref-log replay must be idempotent;
- a token mismatch must spare a new physical incarnation;
- a cache hit must not change correctness;
- corruption must produce a typed exception rather than partial parsing or undefined behavior.

A green check is evidence only if a sabotage or negative control demonstrates that removing the guarantee
makes it red. Tests that silently select no objects, discard a class through a whitelist, or observe an
empty signal are considered invalid evidence.

### Independent review workflow {#independent-review}

The development method separates:

1. ground-truth exploration of current code;
2. design and invariant review;
3. implementation;
4. spec-compliance review;
5. code-quality and concurrency review;
6. runtime validation.

This separation found defects that semantic tests alone missed, including unchecked format lengths,
shutdown races, lock-held network I/O, and tests whose assertions were vacuous.

### TLA+ role {#tla-role}

Formal models are used as pre-implementation gates for deletion semantics and distributed interleavings.
A model suite is considered healthy only when:

- all intended safety invariants hold;
- required liveness properties hold within the model's stated bounds;
- every sabotage configuration violates the invariant it was designed to remove;
- witness configurations reach the important success and failure states;
- the model's relationship to current code is documented.

The central modeled properties include:

- no committed ref reaches absent content;
- exact-token deletion cannot kill a replacement incarnation;
- precommit ownership and fail-closed promotion are jointly necessary;
- source-edge sets remain correct under replay;
- attempt-scoped GC artifacts from a deposed leader cannot become authoritative;
- shard or ref incarnation prevents path-reuse ABA;
- a mount handover cannot admit two active writers;
- deferred/skip-unchanged GC rounds cannot make destructive decisions on incomplete state;
- condemned state and deletion pacing preserve live re-reference.

Some older models prove the invariant shape but no longer mirror the concrete storage representation. For
example, a model may use a mutable shard journal while code uses immutable ref logs and snapshots. Such a
model remains evidence for the guard it isolates, but not proof that every current code transition is
represented. `docs/superpowers/models/README.md` is the currency index when older prose disagrees.

### Important model-driven decisions {#model-driven-decisions}

Formal counterexamples directly caused several design changes:

- unconditional deletion was replaced by exact-token deletion;
- build liveness hints were replaced by durable precommit ownership;
- integer in-degree was replaced by a source-edge set;
- registry-based discovery was removed after incarnation and lifecycle proofs;
- unadopted GC artifacts were isolated under attempt-scoped generations;
- skip-unchanged rounds were forbidden from making destructive decisions;
- one global quiescence epoch was replaced by per-object incarnation safety.

### Scenario suite {#scenario-suite}

The adversarial scenario suite exercises:

- inserts, merges, mutations, TTL, truncate, detach/attach, and drop;
- multiple replicas sharing one pool;
- dedup-cache pressure;
- GC with multiple shards;
- leader death and lease stealing;
- mount loss and restart;
- conditional-operation failures;
- list pagination and backend throttling where infrastructure supports injection;
- backup shadows and read-only inspection;
- fsck/dry-run agreement.

Some scenarios require CI-scale infrastructure and are not meaningful in a small developer run. A skipped
or scale-reduced scenario must be reported as such, not counted as a pass.

The S01–S35 catalog is intentionally not one undifferentiated green badge:

- many core correctness cards pass at developer scale;
- memory, manifest-cap, and large-universe cards require `ci/full` scale;
- S12 requires a 10-replica environment;
- S22 requires a fault-injecting throttling/retry proxy;
- S27 requires instrumented pagination behavior;
- multi-shard dry-run/fold coverage has dedicated scenarios and same-instant oracle requirements;
- a failure caused by a broken card or vacuous selector is classified as a test defect, then re-run after
  fixing the oracle.

The next broad validation gate remains a full-scale scenario sweep, even when short shakeouts and long soaks
are green.

### Soak validation {#soak-validation}

The soak harness runs deterministic workload and chaos workers against a shared pool. At quiesced
checkpoints it compares:

- SQL-visible row and checksum state;
- ref and manifest reachability;
- `ca-fsck` classes;
- `ca-gc-dryrun` candidates;
- audit-log anomaly classes;
- request and memory budgets;
- progress of GC over time.

The latest documented campaign includes multiple short shakeouts and a four-hour chaos run with no
acknowledged-data failures. This does not erase known open issues: a detector can fire without yet proving
its suspected cause, and a retention leak can remain while all reads are correct.

Recent harness hardening adds anti-vacuity checks, a skipped-transaction detector, per-phase GC timing,
source-edge inspection, and signals for unmatched removal deltas. A run that preserves reads while GC falls
behind is not a complete pass: retention and service-rate assertions must also make progress.

### Native backend validation {#native-backend-validation}

In-memory tests cannot prove that S3-compatible implementations honor `If-Match`, `If-None-Match`,
conditional copy, ranged reads, pagination, and token semantics. Native contract tests and live probes are
required.

Validated environments and limitations evolve:

- AWS S3 has live validation for core conditional operations, dedup, replication, and reclaim.
- GCS generation-token handling and core live validation are implemented. Remaining work is production
  hardening and broader operational coverage, not the basic binding.
- Azure requires dedicated validation of ETag and disabled soft-delete/versioning behavior.
- RustFS is useful for development but has had compaction and false-404 behavior that required defensive
  clamps.
- MinIO and Ceph behavior must not be assumed conformant merely because their APIs resemble S3.

### Concurrency checks {#concurrency-checks}

Concurrency review prioritizes:

- network I/O while holding a hot mutex;
- shutdown while a renewal or remount callback can create a new thread;
- exception paths that leave a queue leader flag set;
- stale cache reinsertion after invalidation;
- two writers using one `server_root_id`;
- manual and scheduled GC using unsynchronized leader state;
- fold cursor advancement across an incomplete list;
- ref removal racing manifest adoption;
- local backend operations that lack S3's atomic PUT behavior.

The motivating incident was a durable CAS publish running while MergeTree held `data_parts`: blob uploads,
manifest publication, and ref writes performed object-store round trips while every reader needing the parts
lock waited. Correctness-oriented soaks missed it because they had no continuous readers, no latency canary,
and reviewed on-CPU profiles rather than off-CPU lock wait.

That specific publish-under-lock defect was fixed by moving durable publication to the corrected
`renameParts` ordering. The checks below remain proposed defenses against reintroducing the same latency
class elsewhere.

Proposed validation improvements include latency histograms for expected-instant operations, lock-wait
metrics, debug guards against network calls under selected locks, real-thread fault-injection tests, and
regular instrumented runs with query-log anomaly review.

Specifically, the proposal calls for:

- sampling `PartsLockHoldMicroseconds`, `PartsLockWaitMicroseconds`, and context-lock wait deltas;
- a frequent cheap SELECT canary with a p99 latency gate outside chaos windows;
- continuous reader threads during writer/merge workloads;
- a debug thread-local guard that trips if synchronous CAS/S3 I/O starts while a hot parts lock is held;
- an inventory of every CAS mutex, its longest critical section, waiter type, timeout, and fence interaction;
- periodic off-CPU flamegraphs and lock-contention captures.

These are proposed validation improvements unless separately recorded as landed in the live backlog.

## Backup and disaster recovery {#backup-and-disaster-recovery}

**Status: Existing building blocks are usable; the complete CAS-native backup workflow is design only.**

CAS immutability helps incremental copying, but the current backend contract removes several cloud-native
options. Bucket versioning must be disabled, which also rules out S3 CRR/SRR, S3 Object Lock, AWS Backup
continuous mode, and analogous versioning-based rollback on the CAS prefix.

This is a semantic restriction, not merely a storage-cost concern. The current safety model assumes one live
physical incarnation per key and exact deletion of that incarnation. A future version-ID protocol would be
a separate design.

### Threats to cover {#backup-threats}

A backup plan should state which threats it covers:

- bucket or region loss;
- operator error such as `DROP TABLE`;
- a CAS or GC software defect;
- production credential compromise;
- loss of a compatible CAS binary or format knowledge.

No single current option covers all five.

### Existing options {#backup-options}

#### `FREEZE` shadows {#backup-freeze}

`ALTER TABLE ... FREEZE` creates shadow refs inside the same pool. It is immediate and deduplicated because
the shadow points to existing manifests and blobs. When a backup consumer walks `shadow/`, the CAS disk
resolves those refs and presents ordinary file bytes; the snapshot representation remains refs, while the
read interface remains compatible with file-oriented backup code.

It protects against accidental live-ref removal, but not bucket loss, credential compromise, or a storage
bug that destroys the shared blob.

#### Native `BACKUP` {#backup-native}

Native `BACKUP` reads logical MergeTree files through CAS and writes ordinary backup data. When sent to a
different bucket or plain object-storage prefix, it is format-independent and protects against CAS-format
bugs.

Do not write a supposedly independent backup as loose files onto the same CAS disk and prefix. That pays the
full byte cost while remaining inside the failure domain being backed up.

`clickhouse-backup` classic shadow-file mode does not apply because CAS shadows are refs rather than local
filesystem trees. Its embedded mode, which orchestrates native `BACKUP`, remains applicable.

#### Independent DR replica {#backup-dr-replica}

A replica in another region using a different CAS pool performs ordinary byte transfer because pool IDs
differ. It provides a continuously maintained independent byte copy with low RPO and RTO, but replicates
logical mistakes such as a table drop unless the DR pool also retains snapshots.

#### Periodic or event-driven object copy {#backup-object-copy}

Immutable objects make incremental copying practical. A periodic sync or event-driven mirror must still:

- pin a consistent source closure or run a fixpoint reconciliation;
- handle missed events;
- avoid copying stale epoch identity in a way that permits reuse;
- maintain independent retention on the destination;
- verify the result with CAS-aware inspection.

#### Logical export {#backup-logical-export}

Parquet or Iceberg export provides the greatest format independence, but can lose ClickHouse-specific
physical features and has the longest restore path. It is an archival tier, not a complete operational
backup.

### Chosen CAS-native direction {#cas-native-backup}

The design direction is Git-like:

| Operation | Meaning |
|---|---|
| Snapshot | Create immutable backup refs for a selected table state |
| Consolidate | Ensure one pool contains the complete snapshot closure |
| Mirror | Copy missing immutable objects to an independent backup pool |
| Fetch | Pull selected snapshot closure into a fresh pool |
| Restore | Publish local refs to the fetched manifests |

Only missing hashes need copying, preserving deduplication across backup generations. The destination can be
verified independently with `fsck`. This workflow is not yet a shipped end-to-end feature.

The detailed design adds these rules:

- an in-pool snapshot copies the table's ref snapshot into a shadow namespace and keeps manifest lifetime
  edge-driven, even when the original table namespace is later dropped;
- multi-disk tables snapshot each disk natively, then asynchronously consolidate selected snapshots into
  one pool-complete closure;
- a pull daemon runs with read-only source credentials and independent destination credentials, copies only
  missing closure objects, never mirrors source deletions, and applies independent retention;
- recovery fetches selected snapshots into a fresh writable pool and restores by local manifest relink;
- identity objects under `gc/server-roots/` are never copied between pools;
- source thinning happens only after consolidation and mirroring have durably completed;
- no normal restore path writes to the backup pool (`BAK-RO`);
- mounting the backup pool writable as production is an explicitly destructive last resort that consumes
  it as a backup.

### Recommended layered strategy today {#backup-recommendation}

Until CAS-native backup is implemented:

1. Use `FREEZE` for cheap short-term operator-error protection.
2. Maintain an independent bucket/prefix copy or a DR replica in a different pool.
3. Periodically create a native materialized backup in a separate failure domain.
4. Record the pool format version and compatible binary with long-retention backups.
5. Test restore, `fsck`, and GC rebuild; a backup without a validated restore path is not sufficient.

## Current readiness and live backlog {#current-readiness}

CAS is experimental and should not be described as production-ready merely because its core happy path is
implemented. The current live status must be read from `docs/superpowers/cas/BACKLOG.md`; historical
`DONE` rows in `ROADMAP.md` can predate later findings.

### Implemented foundations {#implemented-foundations}

- Content-addressed blobs and immutable manifests
- Per-server ownership roots and mount fencing
- Ref logs, snapshots, recovery, precommit, and promotion
- Ref-lane exception safety for uncertain appends and exact-ref confirmation
- Same-pool replication relink with publish-confirm protocol and enumerated failure outcomes
- Source-edge GC with exact-token delete
- Attempt-scoped GC generations and skip-unchanged behavior
- Streaming run readers
- Multiple hash algorithms including `sha256`
- Part-folder and decode caches
- Optional S3-native staging for the writer
- Parallel intra-part blob upload
- Capability gating at `CREATE`/`ATTACH` so unsupported operations are rejected explicitly instead of being
  advertised and failing later
- Event and per-phase GC logs, mount table, `fsck` (including `stale_edge`), unmatched-removal metrics,
  dry-run, source-edge inspection, and rebuild tools
- Skipped-transaction detection and anti-vacuity checks in the soak harness
- AWS and GCS validation for substantial portions of the backend contract

### Release-blocking or high-priority work {#release-blockers}

At the current documentation date, notable open work includes:

- resolve the LIST-as-journal completeness problem before relying on cursor advancement;
- complete the rev.6 lease-boundary exclusivity design, including the cross-epoch late-predecessor PUT
  hazard where an old writer's delayed log object can appear after successor recovery coverage;
- fix the root-caused retention leak without turning it into a ref-state wedge; blindly re-issuing an
  unmatched removal is explicitly unsafe because absent-binding validation can turn a leak into a permanent
  namespace wedge;
- complete the `TXN-ONE-PIPELINE` ordering work so staging and durable transaction effects cannot invert;
- complete GC performance characterization and backlog service-rate testing;
- address GC throughput collapse caused by large ref-log and dead-namespace backlogs;
- make `ca-gc-dryrun` use the same reachability basis as GC and `fsck` so it cannot under-report planned
  deletion work;
- expose all corruption counters and make large-pool inspection finish predictably;
- print `corrupted_runs` in `fsck` output and replace the flat inspection timeout with scalable progress;
- finish remaining mount force-claim and cleanup windows;
- complete clean shutdown and lifecycle tests;
- fix or explicitly gate unsupported product paths such as `MOVE PART ... TO DISK` into CAS and expensive
  `system.remote_data_paths` scans without predicate pushdown;
- complete the missing `SYSTEM` control surface for operational start/stop/check/read-only transitions;
- finish migration and mixed-version rollout rules;
- freeze persisted formats and pool version breadcrumbs;
- validate remaining backend-specific behavior, especially Azure;
- complete a supported backup/restore runbook;
- finish upstream repository hygiene and patch decomposition.

### Desirable but not required for core safety {#desirable-work}

- incremental GC delta runs and compaction;
- reduced read request count and one-GET small-part opens;
- faster rare overwrite/resurrection paths;
- compliance-oriented expedited deletion;
- encryption-domain-aware deduplication;
- stronger first-class local/NFS backend contracts;
- CAS-native cross-pool backup;
- additional per-part and per-ref system views.

### Explicit non-goals and rejected work {#non-goals}

- CAS does not deduplicate logical rows.
- It does not guarantee independently built parts are byte-identical.
- It does not replace Keeper for `ReplicatedMergeTree`.
- It does not make one shared bucket an independent disaster-recovery copy.
- It does not support bucket versioning under the current token model.
- It does not store mutable integer blob refcounts.
- It does not place a CAS manifest hash in Keeper's generic part header.
- It does not silently fall back when a correctness-critical operation fails.

## Maintainability and upstream integration {#maintainability-and-upstreaming}

The feature touches the object-storage disk layer, MergeTree part transactions, replication exchange,
system commands, system tables, logging, and backend HTTP behavior. Keeping generic ClickHouse code unaware
of CAS details is an explicit design goal.

### Preferred boundaries {#preferred-boundaries}

- Generic disk interfaces expose narrow capabilities; CAS-specific classes implement them.
- MergeTree works with ordinary part and transaction concepts rather than blob/ref/manifest internals.
- Keeper metadata remains disk-agnostic.
- CAS format codecs stay inside the CAS module.
- Backend conditional operations are generic only when they are independently useful and correctly specified.
- Administration uses a narrow inspection/control facade rather than casts to the concrete metadata class.

### Known architecture debt {#architecture-debt}

The branch review identified remaining structural work:

- split the large store class into mount lifecycle, ref lane, cache, and pool-access responsibilities;
- keep MergeTree part-path parsing out of generic object-storage transaction code;
- centralize CAS transaction dispatch rather than accumulating per-operation branches;
- remove debug-only locks and journals from hot paths;
- isolate per-disk metrics instead of allowing multiple CAS disks to overwrite one process-global gauge;
- move non-trivial parsers out of widely included headers;
- preserve direct tests for generic transaction ordering and native backend contracts.

Most correctness findings from the umbrella review were fixed in the stabilization iteration. The review's
claimed relink RBAC bypass was retracted: the interserver channel has the same trust boundary as ordinary
replicated part fetch. The remaining architectural and test-coverage findings are still useful upstreaming
guidance.

### Upstream patch decomposition {#upstream-patch-decomposition}

The upstream inventory classifies changes into:

- **CAS-local** — implementation under the content-addressed metadata-storage module;
- **generic prerequisite** — narrow reusable interfaces or conditional object-store operations;
- **integration** — MergeTree, replication, SQL, and operational wiring;
- **temporary workaround or cleanup candidate** — code that should be removed before upstreaming.

A reviewable sequence is:

1. Remove abandoned PoC and dead metrics.
2. Land backend-neutral conditional object-store primitives and their native wire tests.
3. Land narrow disk/metadata transaction interfaces with default-safe behavior.
4. Land CAS formats and core object model.
5. Land writer, reader, and GC protocols with focused tests.
6. Land MergeTree and replication integration.
7. Land system commands, tables, logs, and operational documentation.
8. Add backend-specific bindings and integration tests.

This order is not merely cosmetic. It prevents a single enormous change from making it impossible to
separate a generic regression from a CAS protocol defect.

### Review checklist {#review-checklist}

For any CAS change, verify:

- Does it preserve “no committed ref reaches missing content”?
- Can an ambiguous operation be mistaken for one that definitely failed?
- Can GC advance a cursor without proving input completeness?
- Can a stale token delete a replacement incarnation?
- Can a cache or metric become part of correctness?
- Does an exception leave a queue leader, lease, or lock permanently held?
- Is network I/O performed while holding a hot mutex?
- Can shutdown callbacks create work after the final join?
- Are limits checked before allocation and indexing?
- Does the test fail when the intended guard is removed?
- Is the implementation status clearly separated from a proposal?
- Does the change add CAS knowledge to generic MergeTree or Keeper code unnecessarily?

## Documentation provenance and source coverage {#documentation-provenance}

This guide synthesizes all 23 Markdown files currently under `docs/superpowers/cas/`. It keeps their durable
content while separating current implementation from historical plans and proposals. The source files
remain valuable for exhaustive wire tables, model-run results, issue IDs, and design discussion.

| Source document | Information represented in this guide |
|---|---|
| `README.md` | Reading order, status interpretation, feature-area map |
| `INTENT.md` | Demonstrated correctness, visible failures, fail-closed ambiguity, no silent data loss |
| `01-architecture.md` | Object model, pool layout, namespaces, replication, rejected architecture |
| `02-methodology.md` | TDD, independent review, formal gates, soak methodology |
| `03-writer-protocol.md` | Mount ownership, writer identity, precommit, blob materialization, promotion, transactions, and MVCC storage contract |
| `04-gc-protocol.md` | Ownership edges, leadership, fold, condemnation, exact deletion, cleanup |
| `05-formats-and-backend.md` | Object families, envelopes, backend conditional operations, format evolution |
| `06-tla-models.md` | Proven invariants, sabotages, model currency, model-driven decisions |
| `07-s3-budget.md` | Write/read/GC request shape, dedup hints, cost and tuning |
| `08-testing-and-soak.md` | `fsck`, dry-run, logs, scenarios, soak, health playbook |
| `09-read-protocol.md` | Ref resolution, manifests, ranged reads, pruning, caches, read-your-writes |
| `10-backups.md` | Threat model, unavailable versioning stack, current options, CAS-native direction |
| `ROADMAP.md` | Implemented foundations, historical statuses, release gates |
| `BACKLOG.md` | Current blockers, known leaks, performance work, remaining validation |
| `codecs.md` | Historical codec audit and strict-decoding lessons; parts of its protobuf-era inventory are stale, so `Formats/README.md` and current codec code are authoritative |
| `codecs_proposal_v2.md` | Universal framing and body-family rationale, marked historical |
| `codecs_proposal_v3.md` | Role-based codec design, integrity, determinism, limits, marked proposal history |
| `cache.md` | Part-folder cache architecture, bounds, invalidation, risks, observability |
| `review1.md` | Resolved review findings, remaining architecture and test debt |
| `refactoring-ideas.md` | Maintainability, naming, introspection, simplification opportunities |
| `concurrency_checks_improvements_proposal.md` | Lock/I/O audit, latency metrics, real-thread validation proposals |
| `upstream-patch-inventory.md` | Generic-vs-CAS patch boundaries and upstream sequencing |
| `CONSOLIDATION-COVERAGE.md` | Historical source-to-canonical mapping and the rule against deleting uncovered knowledge |

### Which source is authoritative {#source-authority}

When sources disagree, use this order:

1. Current code and executable tests
2. `BACKLOG.md` for open work and latest findings
3. Current model inventory in `docs/superpowers/models/README.md`
4. This guide and current canonical protocol chapters
5. `ROADMAP.md` for historical completion records
6. Review, refactoring, and proposal documents for rationale
7. Superseded codec and protocol descriptions for history only

### Final operational rule {#final-operational-rule}

The most important rule is:

> No path may lose acknowledged data, and no path may delete an object a committed ref still names.

When the implementation cannot prove that a transition, list, token, or ownership state is complete, it
must retain data or block publication and surface the uncertainty. A storage leak can be investigated and
reclaimed later; acknowledged data cannot be reconstructed from a confident but incorrect delete.
