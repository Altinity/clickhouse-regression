# upgrade-compat -- fresh audit 2026-08-12

## Scope

Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base `842f2b37b8f`, working tree as-is, read-only.
CAS root: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`.

Subject: mixed-version and rolling-upgrade safety of a shared CAS pool. Covered surfaces: the generation stamp
in `Formats/CasFormat.{h,cpp}` and every codec under `Formats/`; the unused `changePoints()` registry; additive/unknown
key handling and read-modify-write re-encode paths; pool meta version, hash-algo and geometry validation
(`Pool/CasPoolMeta.cpp`, `Formats/CasPoolMetaFormat.cpp`); on-disk-semantics settings in `ContentAddressedSettings.cpp`;
the relink/fetch wire contract in `src/Storages/MergeTree/DataPartsExchange.cpp` and
`ContentAddressedMetadataStorage::prepareAdoptFromManifest`; GC state / checkpoint / fold-seal formats; system-table surface.

Code-only rule observed: `docs/**` is deleted in the working tree and is not used as evidence anywhere below.
Shipped exception and log strings are treated as admissible.

Calibration verified before building on it:
- `Formats/CasFormat.cpp:19-75` holds the per-format `changePoints()` table. `rg` over `src` and `programs` finds
  **zero** callers outside its own declaration (`CasFormat.h:58`) and definition (`CasFormat.cpp:45`). Dead.
- `currentWriterVersion()` (`CasFormat.cpp:77-80`) also has zero callers.
- Every writer stamps `currentCompatibilityVersion()`, which returns `G_BUILD` unconditionally
  (`CasFormat.cpp:82-85`, `G_BUILD = 9` at `CasFormat.h:10`): `CasTextFormat.cpp:257`,
  `CasRecordStreamFormat.cpp:106`, `CasBlobEnvelopeFormat.cpp:102`.
- All CAS tests are deleted in the working tree; the only surviving copies are in `git show 842f2b37b8f:tests/...`.
  There is therefore no encode/decode golden corpus, and no cross-generation fixture, guarding any of this.

Throughout: **N** = a build with `G_BUILD = 10` (a hypothetical next generation), **N-1** = the build in the tree,
`G_BUILD = 9`. Nothing in the tree pins `G_BUILD` to a release, so "generation" and "build" are the same integer.

## Versioning scheme as implemented

There is exactly one version number on the wire: the `"v"` field of the header line, written by
`writeHeaderLine()` (`CasTextFormat.cpp:250-260`) and validated by `expectHeaderLine()` ->
`checkCompatibility()` (`CasTextFormat.cpp:310-319`, `CasFormat.cpp:87-93`). `checkCompatibility` treats the
stamped value as the **minimum reader generation**, so writer generation and required reader are the same number
by construction. `RunFile` writes/checks the same field through its own path
(`CasRecordStreamFormat.cpp:98-113`, `115-144`). The blob envelope writes it (`CasBlobEnvelopeFormat.cpp:102`)
and checks it only inside `decodeEnvelopeHeader` (`:171`), which has one caller in the whole tree.

Per-format table. "changePoints floor" is what `CasFormat.cpp:19-75` claims the format actually needs;
"stamped" is what the writer really emits.

| FormatId | changePoints floor (`CasFormat.cpp`) | stamped | checked on read | newer object at older reader | older object at newer reader |
|---|---|---|---|---|---|
| `Blob` (envelope) | BASELINE {1,1} (`:60,72`) | `G_BUILD` (`CasBlobEnvelopeFormat.cpp:102`) | **never on any production path** (only `Tools/CasInspect.cpp:571`) | accepted, header skipped by byte count (`CasManifestReader.cpp:141`) | accepted, skipped by byte count |
| `PartManifest` | BASELINE {1,1} (`:64,72`) | `G_BUILD` (`CasPartManifestFormat.cpp:84`) | `expectHeaderLine` (`:119`) **and** re-encode digest (`:263-267`) | `UNKNOWN_FORMAT_VERSION` | **`CORRUPTED_DATA` payload_digest mismatch** (finding 1) |
| `PoolMeta` | {1,1},{8,8},{9,9} (`:37-41`) | `G_BUILD` (`CasPoolMetaFormat.cpp:56`) | `expectHeaderLine` + `header.v < 9` floor (`:89-95`) + `mrg` floor (`:152-155`) | `UNKNOWN_FORMAT_VERSION`, whole pool unmountable | accepted if `v >= 9` |
| `RefLog` | REF_STREAM (`:49-51`) | `G_BUILD` (`CasRefLogFormat.cpp:271,390`) | `expectHeaderLine` (`:287`) | `UNKNOWN_FORMAT_VERSION` | accepted |
| `RefSnapshot` | REF_STREAM (`:50-51`) | `G_BUILD` (`CasRefSnapshotFormat.cpp:120,280`) | `expectHeaderLine` (`:141`) | `UNKNOWN_FORMAT_VERSION` | accepted |
| `RefCkpt` | REF_CKPT (`:52-53`) | `G_BUILD` (`CasRefCkptFormat.cpp:69`) | `expectHeaderLine` (`:96`), body **Strict** (`:99`) | `UNKNOWN_FORMAT_VERSION` | accepted; unknown key -> `CORRUPTED_DATA` |
| `RefCatalog` | REF_CATALOG (`:54-55`) | `G_BUILD` (`CasRefCatalogFormat.cpp:79`) | `expectHeaderLine` (`:148`), rows **Strict** (`:157`) | `UNKNOWN_FORMAT_VERSION` | accepted; unknown key -> `CORRUPTED_DATA` |
| `GcMaintenanceState` | {7,7} (`:36,56-57`) | `G_BUILD` (`CasGcMaintenanceStateFormat.cpp:23`) | `expectHeaderLine` (`:39`), body **Strict** (`:42`) | `UNKNOWN_FORMAT_VERSION` | accepted; unknown key -> `CORRUPTED_DATA` |
| `GcState` | BASELINE {1,1} (`:61,72`) | `G_BUILD` (`CasGcStateFormat.cpp:24`) | `expectHeaderLine` (`:42`), body Tolerant (`:45`) | `UNKNOWN_FORMAT_VERSION`, GC cannot take the lease | accepted; unknown keys silently dropped, then dropped on re-encode (`CasGc.cpp:3142-3144`) |
| `GcHeartbeat` | BASELINE {1,1} (`:71-72`) | `G_BUILD` (`CasGcStateFormat.cpp:74`) | `expectHeaderLine` (`:86`), Tolerant | `UNKNOWN_FORMAT_VERSION` | accepted, unknown dropped |
| `GcOutcomes` | BASELINE {1,1} (`:63,72`) | `G_BUILD` (`CasGcOutcomesFormat.cpp:47`) | `expectHeaderLine` (`:67`) | `UNKNOWN_FORMAT_VERSION` | accepted |
| `RunFile` | BASELINE {1,1} (`:65,72`) | `G_BUILD` (`CasRecordStreamFormat.cpp:106`) | `expectRunHeaderLine` (`:132`), rows **Strict** (`:229`) | `UNKNOWN_FORMAT_VERSION` | accepted; seal checksum is over stored bytes so it stays build-stable |
| `FoldSeal` | BASELINE {1,1} (`:66,72`) | `G_BUILD` (`CasFoldSealFormat.cpp:171`) | `expectHeaderLine` (`:289`), body **Strict** (`:297,312`) | `UNKNOWN_FORMAT_VERSION` | accepted; unknown key -> `CORRUPTED_DATA` |
| `Owner` | BASELINE {1,1} (`:67,72`) | `G_BUILD` (`CasServerRootFormats.cpp:30`) | `expectHeaderLine` (`:47`), Tolerant | `UNKNOWN_FORMAT_VERSION` | accepted, unknown dropped |
| `ServerEpoch` | BASELINE {1,1} (`:68,72`) | `G_BUILD` (`CasServerRootFormats.cpp:79`) | `expectHeaderLine` (`:91`), Tolerant | `UNKNOWN_FORMAT_VERSION` | accepted, unknown dropped |
| `MountLease` | BASELINE {1,1} (`:69,72`) | `G_BUILD` (`CasServerRootFormats.cpp:119`) | `expectHeaderLine` (`:138`), Tolerant | `UNKNOWN_FORMAT_VERSION`, node cannot join the pool | accepted; unknown dropped, then dropped on lease renewal re-encode |
| `BlobMeta` | BASELINE {1,1} (`:70,72`) | `G_BUILD` (`CasBlobMetaFormat.cpp:42`) | `expectHeaderLine` (`:58`), Tolerant | `UNKNOWN_FORMAT_VERSION` | accepted, unknown dropped |
| `Roster` | BASELINE {1,1} (`:62,72`) | -- no writer, **no TRAITS row** | `traitsFor` throws `LOGICAL_ERROR` (`CasFormat.cpp:127`) | n/a | n/a |

Two observations fall straight out of the table. First, ten of eighteen formats have a `changePoints` floor of
generation 1 yet are stamped 9, so the registry and the wire disagree for the majority of the pool. Second, the
`changePoints` entries are all of the form `{g, g}` -- even the registry that nobody calls encodes "no backward
window", so the scheme has no mechanism by which an older reader could ever be allowed to read a newer object.

## Findings

### upgrade-compat-1 -- PartManifest payload digest is recomputed with the local build's encoder, so manifests written by any other generation are reported as corrupt (High)

- **Anchor**: `Formats/CasPartManifestFormat.cpp:84` (header line is part of the encoded bytes), `:263-267`
  (recompute and compare), `:272-279` (`computePayloadDigest` re-encodes the decoded model and hashes the result);
  `Formats/CasTextFormat.cpp:250-259` (`writeHeaderLine` stamps `currentCompatibilityVersion()`);
  `Formats/CasFormat.cpp:82-85`.
- **Trigger (skew scenario)**: upgrade one node from generation 9 to generation 10. Every part manifest already in
  the pool carries `{"type":"cas_part_manifest","v":9}` as its first line, and the stored `pd` was computed over
  bytes containing `"v":9`. `decodePartManifest` passes `expectHeaderLine` (9 <= 10), discards the header, then calls
  `computePayloadDigest`, which re-encodes with `"v":10`. The CityHash over the re-encoded bytes differs, and the
  decode throws `CORRUPTED_DATA: PartManifest: payload_digest mismatch`.
- **Evidence**: `PartManifest` (`CasPartManifestFormat.h`) carries no version member, so the decoded model cannot
  reproduce the writer's stamp; `computePayloadDigest` has no way to re-emit the original header. The digest
  therefore covers the writer's generation number, making it a build fingerprint rather than a content digest.
  The failure is not confined to one call site: `Pool/CasManifestReader.cpp:86` (normal part reads),
  `Pool/CasPartWriteTxn.cpp:647`, `Gc/CasGc.cpp:973` (`foldManifestEdges`),
  `Gc/CasOrphanManifestSweep.cpp:698`, `Tools/CasFsck.cpp:535,729`, and
  `ContentAddressedMetadataStorage.cpp:1610` all decode manifests through this path.
- **Notes**: this is the one finding that breaks the *forward* direction, which is the direction an upgrade
  actually needs. `PartFolderAccess.cpp:453` does `decodePartManifest(encodePartManifest(probe))`, a same-process
  round trip, which is exactly the shape a unit test would have and exactly the shape that cannot catch this.
  The GC call sites throw out of the round rather than treating the part as unprotected, so no blob is deleted --
  see the by-design section -- but GC stops entirely.

### upgrade-compat-2 -- A single global build number is stamped as every object's minimum reader, so one generation bump invalidates every format including the ones that did not change (High)

- **Anchor**: `Formats/CasFormat.h:10` (`G_BUILD = 9`); `Formats/CasFormat.cpp:82-85`
  (`currentCompatibilityVersion()` returns `G_BUILD`); `:87-93` (`checkCompatibility` rejects
  `compatibility_version > G_BUILD`); writers at `CasTextFormat.cpp:257`, `CasRecordStreamFormat.cpp:106`,
  `CasBlobEnvelopeFormat.cpp:102`; the contradicting registry at `CasFormat.cpp:19-75`.
- **Trigger (skew scenario)**: node A is upgraded to generation 10 and writes anything at all -- a GC heartbeat, a
  mount lease renewal, a ref-log segment. Node B on generation 9 reads that object and throws
  `UNKNOWN_FORMAT_VERSION: object requires reader generation 10 but this build supports at most 9`.
- **Evidence**: `changePoints()` records that `GcState`, `GcHeartbeat`, `Owner`, `ServerEpoch`, `MountLease`,
  `BlobMeta`, `Blob`, `PartManifest`, `GcOutcomes`, `RunFile` and `FoldSeal` all sit at BASELINE `{1,1}`
  (`CasFormat.cpp:60-72`), i.e. generation 1 readers suffice. The writers ignore that entirely and stamp 9. The one
  place a per-format floor could be consulted -- `checkCompatibility` -- takes only the stamped integer and
  `G_BUILD`, and never receives a `FormatId` at all (`CasFormat.h:50`).
- **Notes**: the blast radius is the whole control plane, not one format. `MountLease` matters most: a
  generation-9 node that cannot decode the lease objects written by a generation-10 node cannot establish or
  observe mounts. Rolling upgrade in a shared pool is therefore not a partial-availability event, it is a split.

### upgrade-compat-3 -- The relink handshake negotiates a replication protocol number that says nothing about CAS generation, and a generation mismatch escapes the byte-fetch fallback (High)

- **Anchor**: `ContentAddressedMetadataStorage.cpp:1610-1619` -- the `catch` filters on
  `e.code() != ErrorCodes::CORRUPTED_DATA` and rethrows everything else;
  `Formats/CasFormat.cpp:90` throws `UNKNOWN_FORMAT_VERSION`, not `CORRUPTED_DATA`;
  `Formats/CasTextFormat.cpp:241` throws the same code for a critical key.
  Call chain: `DataPartsExchange.cpp:1182-1184` -> `:793-799` -> `fetchSelectedPart`.
  Negotiation: `DataPartsExchange.cpp:246` (`min(client, 11)`), `:578` (client always claims 11),
  `:310-330` (relink offered on protocol >= 11 plus pool-UUID equality).
- **Trigger (skew scenario)**: node A on generation 10 and node B on generation 9 share one pool. Both speak
  replication protocol 11, and `getPoolUUID()` matches because it is the pool identity, not a format version. A
  therefore offers a relink and sends its generation-10 manifest bytes. B calls `decodePartManifest`, which throws
  `UNKNOWN_FORMAT_VERSION` at `expectHeaderLine`. That code is not `CORRUPTED_DATA`, so line 1615 rethrows, the
  exception leaves `prepareAdoptFromManifest`, leaves `relinkPartToDisk`, leaves `fetchSelectedPart`, and the fetch
  fails. `fall_back_to_byte_fetch` at `DataPartsExchange.cpp:764-771` is never reached because it is only invoked
  on a `nullptr` return or a cookie mismatch, not on a thrown exception.
- **Evidence**: the fallback ladder in `fetchSelectedPart` handles exactly three degradations -- an unrecognised
  `cas_relink` cookie value (`:773-778`), a reservation that landed outside the advertised pool (`:781-787`), and a
  `nullptr` from `relinkPartToDisk` (`:798-799`). Format-generation skew is not among them. Every retry re-enters
  the same path and fails identically, so this is a permanent stall on that replication queue entry, not a
  transient error.
- **Notes**: `REPLICATION_PROTOCOL_VERSION_WITH_CA_RELINK = 10` is marked `[[maybe_unused]]`
  (`DataPartsExchange.cpp:91`) and is never compared against anything -- the relink capability is gated only on 11.
  The cookie value `CA_RELINK_COOKIE_VALUE = "part_manifest_v2"` (`:101`) is a second, independent version
  namespace that is hardcoded and not tied to `G_BUILD`, so bumping `G_BUILD` does not change the cookie and the
  clean cookie-mismatch fallback at `:773` cannot fire.

### upgrade-compat-4 -- One node admitting a hash algo rewrites the pool-wide reader floor to its own build number, locking every older node out of the entire pool (High)

- **Anchor**: `Pool/CasPoolMeta.cpp:72` (`next.min_reader_generation = G_BUILD;` inside `admitOrValidate`),
  `:115` (same on mint); `Formats/CasPoolMetaFormat.cpp:56` (the rewrite also restamps the header via
  `writeHeaderLine`), `:152-155` (`G_BUILD < pm.min_reader_generation` -> `UNKNOWN_FORMAT_VERSION`),
  `:89-95` (independent hard floor on `header.v`).
- **Trigger (skew scenario)**: an operator sets `<blob_hash>xxh3-128</blob_hash>` and
  `<blob_hash_allow_new>1</blob_hash_allow_new>` (`ContentAddressedSettings.cpp:33-34`) on the one node that has
  already been upgraded to generation 10. On mount, `admitOrValidate` CAS-writes a new `_pool_meta` with
  `mrg = 10` and header `v = 10`. Every generation-9 node in the pool now fails `decodePoolMeta` twice over: at
  `expectHeaderLine` (10 > 9) and at the `mrg` check. The disk fails to mount. No data changed and no format
  changed; the reader floor was raised purely because the writing node happened to be newer.
- **Evidence**: `min_reader_generation` is assigned `G_BUILD` at both of its only two assignment sites and is
  never derived from what actually changed -- adding an algo to `algos_used` is a semantics change that a
  generation-9 reader handles fine, since `validatePoolAlgosUsed` (`CasPoolMetaFormat.cpp:32-51`) accepts any algo
  name that build knows and `xxh3-128` is in `BlobHashAlgo` already. The bump is unconditional.
- **Notes**: the loop at `CasPoolMeta.cpp:61-84` retries on conflict, so this propagates on the first writable
  mount and there is no confirmation step or dry run. `_pool_meta` is the first object read on every mount
  (`CasPool.cpp:352,548`), so the failure is total for the affected nodes rather than per-table.

### upgrade-compat-5 -- Nothing binds a format change to a `G_BUILD` bump, and tolerant decoders drop unknown keys that the read-modify-write loops then discard (Medium)

- **Anchor**: `Formats/CasTextFormat.cpp:236-247` (`skipUnknown` silently discards unknown keys for
  `KeyStrictness::Tolerant`); `Formats/CasGcStateFormat.cpp:60` (drop) with `Gc/CasGc.cpp:3142-3144`
  (`GcState next = current; ... encodeGcState(next)`); `Formats/CasServerRootFormats.cpp:166` (drop) on the mount
  lease; `Formats/CasPoolMetaFormat.cpp:138`; `Formats/CasBlobEnvelopeFormat.cpp:201`. The would-be enforcement
  point, `changePoints()` (`CasFormat.cpp:45-75`), has zero consumers.
- **Trigger (skew scenario)**: a change adds a field to `GcState` or `MountLease` without bumping `G_BUILD` --
  which nothing prevents, because `G_BUILD` is a hand-maintained constant with no test, no registry consumer and
  no golden corpus (all CAS tests are deleted; only `git show 842f2b37b8f:tests/...` has them). Both builds now
  stamp and accept 9, so `checkCompatibility` passes. The older node decodes, drops the new key, and the very next
  lease renewal or GC lease acquisition re-encodes without it. The field is gone from the pool.
- **Evidence**: the RMW shape is explicit at `CasGc.cpp:3142-3144` -- the decoded `GcState` is copied, one counter
  is incremented, and the whole object is re-encoded from the model. Anything `decodeGcState` did not recognise is
  not in the model and therefore not in the bytes written back. The same holds for mount-lease renewal, `Owner`
  and `ServerEpoch`, all of which are Tolerant.
- **Notes**: the risk here is precisely the one the `changePoints()` table was built to manage. Because the table
  is dead, the only thing standing between an additive control-plane field and silent pool-wide erasure is a
  developer remembering to edit `CasFormat.h:10`.

### upgrade-compat-6 -- The blob envelope stamps a version that no production read path ever checks (Medium)

- **Anchor**: `Formats/CasBlobEnvelopeFormat.cpp:102` (stamp), `:146-232` (`decodeEnvelopeHeader`, including the
  `checkCompatibility` at `:171`). The only caller of `decodeEnvelopeHeader` in the entire tree is
  `Tools/CasInspect.cpp:571`. The production read path instead does
  `.offset = meta.blob_header_len` (`Pool/CasManifestReader.cpp:141`) and
  `staged->stream->ignore(meta.blob_header_len)` (`Pool/CasPartWriteTxn.cpp:462`).
- **Trigger (skew scenario)**: a future generation changes the envelope layout -- reorders fields, changes the pad
  convention, or moves the `ref` field. An older node reading those blobs does not parse the header at all; it
  seeks past a fixed byte count taken from `_pool_meta` and starts reading payload. There is no fail-closed check
  and no misparse either: the reader is structurally blind. Whether the resulting bytes are the intended payload
  depends entirely on whether the new layout kept the same total length, which is enforced only by
  `blob_header_len` remaining constant for the pool.
- **Evidence**: `checkCompatibility` on the envelope is reachable only from `clickhouse-disks ca-inspect`. Nothing
  in `CasPool`, `CasPartWriteTxn`, `CasManifestReader`, `CasGc` or `PartFolderAccess` calls it.
- **Notes**: this is the mirror image of finding 2. Every control-plane format is over-strict (fails closed on a
  version bump that did not affect it); the one data-plane format is not checked at all. The version discipline is
  applied in inverse proportion to the volume of bytes it governs.

### upgrade-compat-7 -- The `!`-prefixed critical-key escape hatch has no producer and its error code is on the non-recoverable path (Medium)

- **Anchor**: `Formats/CasTextFormat.cpp:240-242` (a key beginning with `!` throws `UNKNOWN_FORMAT_VERSION`);
  the only writer able to emit one is guarded by `EnvelopeHeader::emit_unknown_critical_key`
  (`Formats/CasBlobEnvelopeFormat.h:46`, used at `.cpp:112-115`), and `rg` over `src` and `programs` shows that
  field is never assigned `true` anywhere.
- **Trigger (skew scenario)**: a future generation wants to add a field that older readers must not ignore. The
  intended mechanism is to name it `!something`, so tolerant decoders fail closed instead of dropping it. As
  shipped there is no way to produce such a key outside the blob envelope, whose header no production reader
  parses at all (finding 6) -- so the mechanism cannot be exercised on the formats that need it.
- **Evidence**: the flag exists solely on `EnvelopeHeader`, not on `writeKey`/`writeHeaderLine`, so none of the
  seventeen other formats can emit a critical key even in principle.
- **Notes**: worse, if it did fire, it throws `UNKNOWN_FORMAT_VERSION`, which per finding 3 is the exact code that
  bypasses the relink byte-fetch fallback. The designed-for-safety escape hatch and the designed-for-safety
  degradation path use incompatible error codes.

### upgrade-compat-8 -- Strict formats report a same-generation additive field as data corruption rather than a version problem (Medium)

- **Anchor**: `Formats/CasTextFormat.cpp:243-244` -- `KeyStrictness::Strict` raises `CORRUPTED_DATA: unknown key
  '{}' in a strict format`. Strict formats per `CasFormat.cpp:107-112`: `RefCkpt`, `RefCatalog`,
  `GcMaintenanceState`, `RunFile`, `FoldSeal`. Decode sites: `CasRefCkptFormat.cpp:99`,
  `CasRefCatalogFormat.cpp:157`, `CasGcMaintenanceStateFormat.cpp:42`, `CasRecordStreamFormat.cpp:229`,
  `CasFoldSealFormat.cpp:297,312`.
- **Trigger (skew scenario)**: a field is added to the ref checkpoint or the fold seal without a `G_BUILD` bump
  (see finding 5). The header check passes, then the body decode reports the object as corrupt. Operators and
  automation see `CORRUPTED_DATA` on the recovery frontier and the GC seal -- the two objects whose corruption
  most strongly suggests running a repair.
- **Evidence**: the two codes are distinguished deliberately elsewhere -- `JsonObjectReader::guarded`
  (`CasTextFormat.cpp:119-120`) rethrows `CORRUPTED_DATA` and `UNKNOWN_FORMAT_VERSION` unchanged while
  normalising every parse error to `CORRUPTED_DATA`, and `prepareAdoptFromManifest` branches on exactly that
  distinction (`ContentAddressedMetadataStorage.cpp:1614`). An unknown-but-well-formed key is a version signal,
  and here it is classified as the opposite.
- **Notes**: the misclassification is load-bearing in one direction and merely misleading in the other. In the
  relink path a `CORRUPTED_DATA` verdict on a healthy newer manifest causes a silent, correct-looking fallback to
  a byte fetch, hiding the skew; on the local read path it causes a corruption alarm on an intact object.

### upgrade-compat-9 -- Pool meta hard-floors at generation 9 and no migration tooling exists anywhere in the tree (Low)

- **Anchor**: `Formats/CasPoolMetaFormat.cpp:89-95` -- `header.v < kCommittedRefFrontierGeneration` throws
  `UNKNOWN_FORMAT_VERSION` with the shipped string "recreate the pool ... CAS is pre-release: there is no in-place
  migration."
- **Trigger (skew scenario)**: any pool created by a generation-8 or older build. It cannot be read, and there is
  no path to convert it.
- **Evidence**: a case-insensitive search for `migrat` or `upgrade` across the whole CAS root and the
  `clickhouse-disks` CAS commands (`CommandCaDropMember.cpp`, `CommandCaGcDryRun.cpp`, `CommandCaGcRebuild.cpp`,
  `CommandCaInspect.cpp`, `CommandFsck.cpp`) matches exactly one line: the message quoted above. No rewrite, no
  dual-read, no in-place converter.
- **Notes**: recorded as Low only because the shipped string is explicit that this is the intended pre-release
  stance. It is the operational context for findings 1-4: since every skew above is resolved by recreating the
  pool, the effective upgrade procedure is a full pool rebuild, and none of the failures above degrade to
  anything less than that.

### upgrade-compat-10 -- `FormatId::Roster` is registered in `changePoints()` but has no traits row (Low)

- **Anchor**: `Formats/CasFormat.cpp:62` (`case FormatId::Roster:` returns BASELINE) versus the `TRAITS` array at
  `:100-119`, which has no `Roster` entry, and `traitsFor` at `:122-128`, which throws
  `LOGICAL_ERROR: CasFormat: no traits for FormatId {} (reserved?)`.
- **Trigger (skew scenario)**: a future generation that revives `Roster` gets a compatibility answer from the
  registry (`{1,1}`) while every actual encode or decode aborts with a logical error, since `writeHeaderLine`
  and `expectHeaderLine` both call `traitsFor` first.
- **Evidence**: `FormatId::Roster = 9` is declared at `CasFormat.h:29` and appears in no writer or reader.
- **Notes**: a second, smaller instance of the same pattern as finding 2 -- the registry describes a world the
  rest of the code does not implement.

## Rolling upgrade walkthrough (N and N-1 in one pool)

Setup: node A on generation 10, node B on generation 9, one shared pool, both configured writable, both with
`gc_enabled` true (`ContentAddressedSettings.cpp:31`).

1. **A restarts and mounts.** `PoolMeta::createOrValidate` reads `_pool_meta` (`CasPool.cpp:352`). The stored
   header is `v=9` and `mrg=9`; A's `G_BUILD` is 10, so both floors pass and A mounts. If A's config also carries
   a new `blob_hash` with `blob_hash_allow_new`, `admitOrValidate` rewrites `_pool_meta` at `v=10, mrg=10`
   (`CasPoolMeta.cpp:72`) and **B can no longer mount the disk at all** -- finding 4. Assume it does not, so the
   walkthrough can continue.
2. **A reads an existing part.** `CasManifestReader.cpp:86` decodes a manifest written at generation 9. The header
   check passes, then `computePayloadDigest` re-encodes with `"v":10` and the digest does not match, so the read
   throws `CORRUPTED_DATA: payload_digest mismatch` -- finding 1. **A cannot read any pre-upgrade part.** In
   practice the upgrade ends here.
3. **A's GC round.** `foldManifestEdges` (`CasGc.cpp:973`) hits the same decode on the first pre-existing manifest
   and throws out of the round. The orphan-manifest sweep (`CasOrphanManifestSweep.cpp:698`) does the same. GC on
   A halts. It halts *before* nominating anything for deletion, so nothing is reclaimed and nothing is
   incorrectly deleted -- the fail-closed ordering here is genuinely load-bearing.
4. **A writes a new part.** Blobs are content-addressed over the payload only, and the envelope header is a fixed
   `blob_header_len` prefix excluded from the digest (`CasPartWriteTxn.cpp:250-257,315-325`), so the blob bytes
   themselves are perfectly readable by B. The manifest, however, is stamped `v=10`.
5. **B reads that new part.** `expectHeaderLine` throws `UNKNOWN_FORMAT_VERSION` -- finding 2. B cannot read any
   post-upgrade part, even though the underlying blobs are byte-identical to what B writes.
6. **B fetches that part by replication.** Protocol negotiates to 11 on both sides (`DataPartsExchange.cpp:246,578`)
   and the pool UUIDs match, so A offers a relink and ships the generation-10 manifest. B's
   `prepareAdoptFromManifest` throws `UNKNOWN_FORMAT_VERSION`, which is not `CORRUPTED_DATA`, so it is rethrown
   past the fallback and **the fetch fails rather than degrading to a byte fetch** -- finding 3. Every retry
   repeats identically; the replication queue entry never drains.
7. **B's GC round.** B takes the GC lease by decoding `gc/state` (`CasGc.cpp:3134`). If A ever held the lease
   after upgrading, that object is stamped `v=10` and B's `decodeGcState` throws `UNKNOWN_FORMAT_VERSION`. **Both
   nodes' GC is now down**: A's by step 3, B's here. The pool accumulates condemned blobs and orphan manifests
   with no reclaimer, and the ref log grows without checkpointing.
8. **Both nodes' mount leases.** `MountLease` is stamped and checked the same way
   (`CasServerRootFormats.cpp:119,138`), so once A renews its lease, B cannot decode the mount roster entry for A.
   The two nodes stop being able to observe each other in the pool.

Net result: the pool does not lose data and GC does not delete anything it should not, but a two-generation pool
is not partially degraded -- it is bidirectionally partitioned at the format layer within one GC interval, and the
upgraded node cannot read the pre-existing data it was upgraded to serve. The only documented resolution is
recreating the pool (finding 9).

## By-design / info

- **Blob content addressing is generation-stable.** The envelope is a fixed-length prefix that is excluded from
  the logical size and from the content hash (`CasPartWriteTxn.cpp:252-257`), and it contains a random
  `incarnation_tag` (`:319`), so it could not be hashed. Identical payload bytes therefore produce the same
  `BlobRef` on any build, and dedup survives an upgrade. This is the one part of the design that gets
  cross-version identity right.
- **Run-file seal checksums are over stored bytes.** `sourceEdgeRunChecksum` (`CasRecordStreamFormat.cpp:208-214`)
  hashes the bytes as read, so unlike the manifest digest it does not embed the reader's generation. Correct
  pattern; finding 1 is what it looks like when the other pattern is used.
- **`gc_shards` skew is fail-closed.** `_pool_meta` is authoritative and overwrites the config value on mount
  (`CasPool.cpp:354,550`), and `acquireOrRenewLease` refuses to proceed if `gc/state` disagrees with it
  (`CasGc.cpp:3135-3138`). Two nodes configured with different `gc_shards` cannot corrupt the fold geometry.
- **`blob_header_len` skew is fail-closed.** Also taken from `_pool_meta` rather than config, re-verified on
  refresh (`CasPool.cpp:113`), and range-checked on both encode and decode (`CasPoolMetaFormat.cpp:21-30`).
- **Relink is gated on pool identity, not just protocol.** `DataPartsExchange.cpp:310-330` requires
  `receiver_pool_uuid == ca_meta->getPoolUUID()`, and the receiver re-checks after reservation (`:781-787`). A
  relink can never be offered across two different pools.
- **GC fails closed before it nominates.** Every manifest decode failure in the GC paths throws out of the round
  rather than treating the manifest as absent. An undecodable manifest stops reclamation; it does not cause its
  blobs to be swept.
- **The `mrg` field is the right idea.** `PoolMeta::min_reader_generation` is a genuine pool-wide reader floor,
  separate from the per-object stamp. Finding 4 is not that the field exists but that it is assigned `G_BUILD`
  rather than the generation of whatever change actually required a floor.

## Coverage

Read in full: `Formats/CasFormat.{h,cpp}`, `CasTextFormat.cpp`, `CasRecordStreamFormat.cpp`,
`CasBlobEnvelopeFormat.cpp`, `CasPoolMetaFormat.{h,cpp}`, `CasPartManifestFormat.cpp`, `CasGcStateFormat.cpp`,
`CasRefCkptFormat.cpp`, `CasServerRootFormats.cpp`, `Pool/CasPoolMeta.cpp`, `ContentAddressedSettings.cpp`.
Read in relevant part: `Gc/CasGc.cpp` (lease, fold, shard geometry), `Gc/CasOrphanManifestSweep.cpp`,
`Pool/CasManifestReader.cpp`, `Pool/CasPartWriteTxn.cpp`, `Pool/CasPool.cpp`,
`ContentAddressedMetadataStorage.cpp` (relink receiver), `src/Storages/MergeTree/DataPartsExchange.cpp`
(negotiation, offer, receive, relink).
Enumerated by search: every `writeHeaderLine`/`expectHeaderLine` site, every `changePoints`/`currentWriterVersion`/
`currentCompatibilityVersion`/`checkCompatibility` reference, every `decodePartManifest` call site, every
`min_reader_generation` reference, every `KeyStrictness::Strict` decoder.

Not covered, and not claimed on: the ref-log and ref-snapshot body grammars beyond their header handling
(`CasRefLogFormat.cpp`, `CasRefSnapshotFormat.cpp`, `CasRefLedger.cpp`) -- the generation-4 through -7 changes
they encode are outside a static skew analysis without fixtures; `Backend/*` object-store token semantics;
the `Cache/` metadata storage; `benchmarks/`; the `system.cas_log` / `cas_gc_log` / `cas_mounts` column sets
(`src/Interpreters/ContentAddressedGarbageCollectionLog.cpp`, `src/Storages/System/attachSystemTables.cpp`) --
these follow the standard `SystemLog` schema-evolution rules and showed no CAS-specific version coupling, but
were not audited column by column.

All findings are static; nothing here was executed, and no test exists in the working tree to execute
(CAS tests are deleted; `git show 842f2b37b8f:tests/...` holds the only copies).
