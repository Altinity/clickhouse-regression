# security -- fresh audit 2026-08-12

## Scope

Static, code-only audit of the CAS security posture in
`/Volumes/workspace/altinity-clickhouse/ClickHouse` (branch `cas-code-only-strip`, base
`842f2b37b8f`), working tree as-is. CAS root
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`, plus the ClickHouse-level
surfaces that reach it: `src/Access/Common/AccessType.h`,
`src/Interpreters/InterpreterSystemQuery.cpp`, `src/Storages/MergeTree/DataPartsExchange.cpp`,
`programs/disks/CommandCa*.cpp`.

Per the code-only rule, `docs/**` and comments were not read as statements of intent. Shipped
strings (exception text, `ContentAddressedSettings.cpp` `DECLARE()` descriptions,
`describeUnresolvedReason` at `Backend/CasRequestControl.h:47-69`) were treated as admissible
evidence. All CAS tests are deleted in the working tree; no test-derived claims are made.

Attacker models used throughout, named explicitly per finding:

- **P** — *bucket-credential peer*: any principal holding read/write/delete credentials on the
  shared bucket and prefix (another pool member, a compromised member, a co-tenant IAM role).
- **U** — *ClickHouse user with limited grants*: can run SQL, holds no `SYSTEM CAS *` grant.
- **N** — *network attacker*: MITM or an unauthenticated client that can reach the interserver
  HTTP port.
- **O** — *malicious operator of one node*: local config and `clickhouse-disks` access on one host.

Static reasoning only. No build, no execution.

## Trust model as implemented

The pool is a **flat, unauthenticated shared medium**. Every cross-member protocol object —
pool identity, ownership, mount leases, GC state, ref logs, manifests, blobs — is a plain
object in the shared bucket. There is no signature, MAC, per-member key, capability, or any
other intra-pool authentication or authorization anywhere in the CAS tree. Identity is
*asserted by content*, and any writer to the prefix can assert any identity:

- Member identity is a field the writer chooses. `claimOwnerOrThrow`
  (`Pool/CasServerRoot.cpp:105-159`) decides ownership solely by comparing
  `owner->server_uuid` read from `gc/server-roots/<srid>/owner` to the local UUID.
- Mount exclusivity is likewise field comparison: `claimMount`
  (`Pool/CasServerRoot.cpp:298-366`) and `MountLeaseKeeper::claim`
  (`Pool/CasServerRoot.cpp:764-800`) branch on `server_uuid`, `writer_epoch`, `gc_fenced` and
  `min_active` read straight out of the object.
- Cross-member fencing is object state: `computeHeartbeatFloor`
  (`Pool/CasServerRoot.cpp:455-552`) fences a peer by writing `gc_fenced = true` into that
  peer's mount object; `MountLease.expires_at_ms` is a *stamped wall-clock value chosen by the
  writer*, and `mountDoubleStartMessage` (`Pool/CasServerRoot.cpp:368-386`) ships the clock-skew
  caveat as user-facing text.
- Pool identity (`pool_id`) is a `thread_local_rng()` draw (`Pool/CasPoolMeta.cpp:24-29`) used
  for matching, not for unguessability; it is also advertised in the clear on the interserver
  wire as `cas_pool_uuid` (`src/Storages/MergeTree/DataPartsExchange.cpp:99, 591`).

The only integrity mechanism between members is the content hash (see security-2) and
per-object CAS tokens/ETags, both of which a bucket writer controls end to end.

The ClickHouse-level boundary, by contrast, **is** enforced. Every CAS SQL verb has a dedicated
`GLOBAL`/`SYSTEM` access type (`src/Access/Common/AccessType.h:351-357`), checked both in
`InterpreterSystemQuery::execute` (`src/Interpreters/InterpreterSystemQuery.cpp:1012-1051`) and
in `getRequiredAccessForDDLOnCluster` (`ibid.:3161-3193`), with no verb missing a check and no
verb sharing another's type. `SYSTEM CAS DROP POOL MEMBER` additionally requires a
non-read-only CAS disk (`ibid.:1056-1057`).

Boundary summary: the *SQL* boundary holds; the *pool* boundary does not exist. Anything a
member can do to the pool, any bucket-credential holder can do, and the code has no way to
tell the difference.

## Findings

### security-1 -- Any bucket-credential peer can permanently disable, fence, or misdirect another member; no intra-pool authentication exists (High)

- **Attacker**: P (bucket-credential peer; includes a co-tenant IAM role scoped to the bucket,
  or one compromised pool member attacking the others).
- **Anchor**: `Pool/CasServerRoot.cpp:68-79` (`throwIfOwnerRetired`),
  `Pool/CasServerRoot.cpp:105-159` (`claimOwnerOrThrow`), `Pool/CasServerRoot.cpp:298-366`
  (`claimMount`), `Pool/CasServerRoot.cpp:325-333` (`FencedSelf`),
  `Pool/CasServerRoot.cpp:455-552` (`computeHeartbeatFloor` writes `gc_fenced` into a peer's
  slot), `Pool/CasServerRoot.cpp:764-800` (`MountLeaseKeeper::claim`),
  `Formats/CasServerRootFormats.cpp:44-68` (`decodeOwner` accepts `retired_at_ms` from the
  object).
- **Trigger**: one `PUT` to `gc/server-roots/<victim-srid>/owner` or
  `gc/server-roots/<victim-srid>/mount`. Three distinct effects, each from a single write:
  1. Write an owner object carrying `retired_at_ms`. On the victim's next mount,
     `throwIfOwnerRetired` throws `CORRUPTED_DATA` — the shipped message says the root "was
     explicitly decommissioned by an operator ... refusing to silently resume" and directs the
     operator to hand-edit the object. This is a **persistent, manual-recovery-only** denial of
     service, and it is indistinguishable in code from a genuine operator decommission.
  2. Write an owner object with a foreign `server_uuid`. `claimOwnerOrThrow:120-126` refuses to
     claim and emits a message blaming the *victim's* local UUID file ("this server's local
     uuid file was regenerated"), steering the operator toward the wrong recovery.
  3. Write the victim's mount object with `gc_fenced = true` (same `server_uuid` and
     `writer_epoch`). The victim's lease renewal loses its token, the mount fence trips
     (`Pool/CasMountRuntime.cpp:83-99`, `mayMutate`/`checkFenceOrThrow`), and `claimMount`
     returns `FencedSelf`, "terminal for this incarnation". Repeating the write on each remount
     is an unbounded write-availability DoS on the victim.
- **Evidence**: every branch above is a comparison against bytes fetched from the shared
  bucket. `grep` across the whole CAS tree finds no HMAC, signature, nonce, per-member key, or
  authorization check on any protocol object; the only "credential" is the S3/GCS credential
  that grants blanket prefix access. `describeUnresolvedReason`
  (`Backend/CasRequestControl.h:47-69`) enumerates fence-loss causes and includes no notion of a
  *foreign* writer. `CasEventType::ForeignInterference` exists
  (`Primitives/CasEvent.cpp:64`) — i.e. foreign writes are anticipated as an *observable*
  condition — but observation is not prevention.
- **Notes**: the same primitive extends to GC state, fold seals, run files, ref logs and
  checkpoints — all shared-bucket objects with the same zero-authentication property. The
  run-file whole-file seal (`Formats/CasRecordStreamFormat.cpp:303-310`) verifies a run against
  a checksum stored in the fold seal, which the same attacker also controls, so it detects
  corruption but not tampering. Sibling audits already report *no lease/mount interlock for GC
  REBUILD* and *partially reviewed SYSTEM CAS access checks* (gc-rebuild-feature); this finding
  is the underlying trust-model reason those matter — cite, not re-report.

### security-2 -- Content addressing defaults to a non-cryptographic hash and reads never re-verify, so a chosen-collision substitutes data (High)

- **Attacker**: P, and — for the collision-planting half — U (a ClickHouse user who can control
  the *bytes* of data written into the pool, e.g. INSERT into any table on a CAS disk, since
  dedup is pool-wide and not scoped to a table, database, or grant).
- **Anchor**: `ContentAddressedSettings.cpp:33` — `DECLARE(String, blob_hash, "cityhash128",
  "Pool blob content-hash function (cityhash128 | xxh3-128 | sha256); fixed at pool creation")`;
  `Primitives/CasBlobDigest.cpp:20-31` (`blobHashLenFor`: 16 bytes for both `ch128` and `xxh3`);
  `Primitives/CasXxh3Streamer.h:26-33`; `Formats/CasLayout.cpp:28-31` (`blobKey` = algo name +
  hex digest); `Formats/CasPartManifestFormat.cpp:272-279` (`computePayloadDigest` is also
  CityHash128).
- **Trigger**: find two byte strings with the same CityHash128 (or XXH3-128) digest; write the
  first into the pool; any later write of the second dedups to the first, and every reader of
  the second now reads the first. The algorithm is recorded per blob in the *object key path*
  (`blobs/<algo>/<shard>/<hex>`), parsed back by `Layout::parseBlobKey`
  (`Formats/CasLayout.cpp:38-85`), and per manifest entry as the `ha` field
  (`Formats/CasPartManifestFormat.cpp:203, 219-225`) — so the algorithm is faithfully recorded,
  but recording is not verification.
- **Evidence**: CityHash128 and XXH3-128 are non-cryptographic hashes with no collision
  resistance claim by their own authors; only `sha256` in the admitted set
  (`Primitives/CasBlobDigest.cpp:33-45`) offers one, and it is not the default.
  `validatePoolAlgosUsed` (`Formats/CasPoolMetaFormat.cpp:32-51`) admits all three equally, and
  `admitOrValidate` (`Pool/CasPoolMeta.cpp:57-85`) will silently add a weaker algo to an
  existing pool when `blob_hash_allow_new` is set. This composes with the sibling finding *read
  path never re-verifies payload against content hash* — cite, do not re-report: because no
  read recomputes the digest, a collision is not merely undetected at write time, it is never
  detected at all. `adoptEvidence` (`Pool/CasPartWriteTxn.cpp:478-486`) records an adopted blob
  with `token = nullopt` and the *sender-supplied* `blob_size`, performing no HEAD and no
  digest check, which widens the same gap on the relink path.
- **Notes**: severity is High on impact (silent data substitution across the whole pool, and
  across tenants since dedup is pool-global) and conditional on collision-finding cost for the
  chosen 128-bit non-cryptographic function. Choosing `sha256` at pool creation closes the
  planting half; it does not close the read half, which remains unverified for every algo.

### security-3 -- Unbounded in-memory materialization of any control object fetched from the bucket (High)

- **Attacker**: P.
- **Anchor**: `Backend/CasObjectStorageBackend.cpp:284-293` (`readObjectRanged`, whole-range
  path: `readStringUntilEOF(content, *buf)` with no cap),
  `Backend/CasObjectStorageBackend.cpp:468-489` (`ObjectStorageBackend::get` — HEAD for size,
  then read the whole body), `Backend/CasObjectStorageBackend.cpp:333-338`
  (`casSizedReadSettings` calls `base.adjustBufferSize(known_size + slack)` — the *read buffer*
  is sized to the attacker's object).
- **Trigger**: overwrite any control object the victim `get()`s unconditionally at mount or
  during GC — `_pool_meta`, `owner`, `mount`, `_ckpt`, a ref-log object — with a multi-gigabyte
  body. The victim HEADs it, sizes a read buffer to the declared size, and reads it entirely
  into a `String` before any format check runs.
- **Evidence**: the format-level `object_cap` in `FormatTraits`
  (`Formats/CasFormat.cpp:100-119`; e.g. `cas_pool_meta` = 1 MiB) is enforced only inside
  `openObject` (`Formats/CasTextFormat.cpp:373-401`), which is called on bytes that are
  *already fully in memory*. `Backend::get` has no size argument, no cap parameter, and no
  caller-side pre-check: `decodePoolMeta(existing->bytes)` at `Pool/CasPoolMeta.cpp:102` is
  reached only after the whole body is resident. The streaming path
  (`openObjectRangedStream`, `ibid.:314-331`, used by `Gc/CasBlobInDegree.cpp:249`) shows the
  bounded alternative exists and is simply not used for control objects.
- **Notes**: `openObject`'s zstd branch *is* correctly hardened — it rejects frames without a
  declared content size and checks the declared size against `object_cap` **before**
  `out.resize(content)` (`Formats/CasTextFormat.cpp:387-396`), so there is no zip-bomb. The
  gap is strictly one layer below, in the transport.

### security-4 -- Quadratic duplicate-key scan under a 64 MiB line cap gives cheap CPU exhaustion from one planted object (Medium)

- **Attacker**: P.
- **Anchor**: `Formats/CasTextFormat.cpp:164-166` — `std::find(seen_keys.begin(),
  seen_keys.end(), key)` over a `std::vector<String>` (`Formats/CasTextFormat.h:152`), executed
  once per key; `Formats/CasFormat.cpp:105-106` — `cas_ref_log` and `cas_ref_snap` carry
  `line_cap = 64 * kMiB`; `Formats/CasTextFormat.cpp:236-247` (`skipUnknown` accepts unlimited
  unknown keys in `KeyStrictness::Tolerant` formats, which both ref streams are).
- **Trigger**: plant a `cas_ref_log` object whose single JSON line holds a few million distinct
  short keys, all within the 64 MiB line cap. Decoding is Θ(k²) string comparisons — roughly
  10^13 comparisons for k ≈ 4·10^6 — pinning a GC or mount thread indefinitely.
- **Evidence**: the guard is a linear scan of a growing vector with no size ceiling on
  `seen_keys`; the only bound is `readLine`'s byte cap (`Formats/CasTextFormat.cpp:271-286`),
  which bounds *bytes*, not *key count*. `readLine` itself is correctly bounded (checks the cap
  after each `push_back`), so this is specifically the duplicate-key structure, not the reader.
- **Notes**: strict formats (`cas_ref_ckpt`, `cas_run`, `cas_ref_catalog`,
  `cas_gc_maintenance_state`) reject unknown keys but still pay the quadratic cost on known
  keys; their line caps (4 KiB–512 KiB) make the cost negligible there. The exposure is
  specific to the two 64 MiB tolerant ref-stream formats.

### security-5 -- `Layout::checkNamespace` accepts `.` and `..` segments, unlike every other CAS path validator (Medium)

- **Attacker**: P or O — anyone who can get a `..`-bearing namespace string into key
  construction; not demonstrated reachable from U in this tree.
- **Anchor**: `Formats/CasLayout.cpp:295-319` (`checkNamespace`: rejects only empty segments,
  `_files` and `_manifests`), against the three validators that *do* reject traversal —
  `Formats/CasLayout.h:25-30` (`isCleanRelativeNamespaceFileName`),
  `Primitives/CasCodecUtil.h:47-64` (`isCanonicalRefName`),
  `Formats/CasPartManifestFormat.cpp:184-193` (manifest entry paths). Consumers:
  `Formats/CasLayout.h:115` and `:141` (`manifestKey` concatenates the namespace directly into
  the object key).
- **Trigger**: a namespace containing a `..` segment produces object keys containing `..`. On
  S3/GCS that is a literal key component and harmless. Under the auto-selected
  `Mode::EmulatedSingleProcess` over local object storage, keys are joined onto a filesystem
  root by `ObjectStorageBackend::emuPath` (`Backend/CasObjectStorageBackend.cpp:367-374`, plain
  string concatenation with no normalization), so the same key escapes the disk root.
- **Evidence**: the asymmetry is the finding — the codebase demonstrably knows the check
  (three separate correct implementations) and omits it in exactly the validator that guards
  the namespace, which is the one segment concatenated into every manifest and namespace key.
  The parse side is defended (`Layout::parseNamespaceFileKey` throws `CORRUPTED_DATA` on an
  unclean relative name, `Formats/CasLayout.cpp:171-175`), so a planted key is rejected on read
  — but a `..` namespace on the *write* side is never rejected.
- **Notes**: rated Medium, not High, because I did not confirm a path by which an unprivileged
  ClickHouse user controls the namespace string end to end; namespaces observed in this tree
  derive from table paths (`Parts/PartPathParser.cpp:280-288`, `mirroredArchiveNamespace`).
  The missing check is confirmed and anchored regardless of that reachability question.

### security-6 -- Bucket layout, node hostnames, PIDs and server UUIDs are disclosed in errors reachable by unprivileged SQL users (Low)

- **Attacker**: U.
- **Anchor**: `Pool/CasServerRoot.cpp:368-386` (`mountDoubleStartMessage` embeds the peer's
  `server_uuid`, `hostname`, `pid`, `seq`, `expires_at_ms` and two literal object paths
  `gc/server-roots/<srid>/owner`, `.../mount`); `Pool/CasServerRoot.cpp:120-126`
  (`claimOwnerOrThrow` embeds both server UUIDs and the owner key);
  `Pool/CasServerRoot.cpp:592-595` (`probeNonTerminalMountSlots` renders holder host/pid);
  `Formats/CasLayout.cpp:172-175` and `:182-186` (`CORRUPTED_DATA` messages embed the full
  object key); `src/Storages/System/attachSystemTables.cpp:250` (`system.cas_mounts`).
- **Trigger**: any query that trips a CAS error path returns the message to the client;
  `SELECT * FROM system.cas_mounts` returns pool topology to any user with SELECT on `system`.
- **Evidence**: these are shipped strings, admissible per the code-only rule. No credential
  material is among them: `secret_access_key` and friends appear in CAS code only in the
  `non_cas_keys` ignore set (`ContentAddressedSettings.cpp:23-27`), never in a log, event, or
  exception. `Primitives/CasEvent.cpp` carries no credential-bearing field.
- **Notes**: Low. The disclosure is infrastructure topology (hostnames, PIDs, UUIDs,
  bucket-relative key layout), not secrets, and much of it is deliberate operator guidance.
  Worth noting only because the messages are verbose by design and reach unprivileged clients
  by default.

## By-design / info

- **SQL access control is complete and correct.** All seven CAS verbs have distinct access
  types (`src/Access/Common/AccessType.h:351-357`), each checked in both
  `InterpreterSystemQuery::execute` (`:1012-1051`) and the on-cluster required-access path
  (`:3161-3193`). No verb is unchecked, none aliases another, and the parser
  (`src/Parsers/ParserSystemQuery.cpp:460-489`) exposes no additional CAS verb lacking a type.
  This is the one boundary in the feature that is genuinely enforced.
- **`clickhouse-disks` CAS commands have no access control, and cannot.** `cas-drop-member`
  (`programs/disks/CommandCaDropMember.cpp:30-63`) performs a destructive pool-member erase with
  no authorization step; `CommandCaGcRebuild`, `CommandCaGcDryRun` and `CommandCaInspect` are
  the same shape. This is inherent to an offline tool driven by a local config that already
  holds the bucket credentials — attacker O already has everything. Noted so it is not mistaken
  for a missing check. The tool does enforce a *safety* precondition (refuses unless the disk is
  opened read-only, `:43-46`), which is not a security control.
- **Format decoders are otherwise well hardened.** `readFixedBytes`
  (`Primitives/CasCodecUtil.h:37-45`) checks `n > in.available()` *before* allocating, so the
  attacker-controlled `il` inline length in a manifest (`Formats/CasPartManifestFormat.cpp:206,
  253`) cannot drive an oversized allocation. `openObject`'s zstd path checks the declared
  content size against `object_cap` before resizing. `readLine` enforces its cap incrementally.
  Duplicate keys, trailing junk, non-canonical entry ordering, out-of-range ordinals and
  unknown critical (`!`-prefixed) keys are all rejected, and every parse error is normalized to
  `CORRUPTED_DATA` by `JsonObjectReader::guarded` (`Formats/CasTextFormat.cpp:110-130`) — a
  deliberate, correct error-type discipline. `cas_run`'s `object_cap = 0`
  (`Formats/CasFormat.cpp:111`) is safe because run files are read via `getStream`
  (`Gc/CasBlobInDegree.cpp:249`) and are line-capped at 4 KiB.
- **Path parsing has no traversal or injection defect** beyond security-5.
  `Parts/PartPathParser.cpp` splits on `/` and drops empty components
  (`splitNonEmpty`, `:10-30`), never rejoins with a user-controlled separator, and
  `Layout::parseBlobKey` / `parseRefObjectKey` / `parseManifestKey` / `parseBlobTargetRunKey`
  (`Formats/CasLayout.cpp:38-293`) all reject extra `/` in identity segments and require exact
  suffixes and canonical (no leading-zero) integers.
- **The interserver relink receiver discards the sender's namespace, which is the safe
  behaviour.** `prepareAdoptFromManifest`
  (`ContentAddressedMetadataStorage.cpp:1592-1636`) decodes the transferred manifest but uses
  only `decoded.entries`, re-staging under the *receiver's* `r->refKey()`
  (`Parts/PartFolderAccess.cpp:392-410`); the manifest's `ns` field is parsed and dropped. Note
  that `manifestNamespaceMatches` (`Formats/CasPartManifestFormat.cpp:286-289`) is called by six
  other consumers (`Pool/CasManifestReader.cpp:105`, `Pool/CasPartWriteTxn.cpp:650`,
  `Gc/CasGc.cpp:977`, `Tools/CasFsck.cpp:536`, `Gc/CasOrphanManifestSweep.cpp:700`) and *not*
  here — benign, because the field is never used for key construction on this path.
- **Relink does widen the impact of a compromised or spoofed sender**, without creating a new
  entry point. A sender that reaches the interserver endpoint supplies a manifest whose blob
  refs the receiver adopts on trust (`Pool/CasPartWriteTxn.cpp:478-486`, no HEAD, no digest
  check), so the receiver can be made to materialize a part out of *any* blob already in the
  shared pool rather than out of transmitted bytes. Attacker N reaching this requires the same
  position that already allows substituting the part bytes outright, so it is an impact
  amplification, not a new surface. The `cas_confirm` oracle
  (`src/Storages/MergeTree/DataPartsExchange.cpp:201-231`) answers yes/no about a ref in the
  endpoint's own table and is gated by `ownsNamespace`
  (`ContentAddressedMetadataStorage.cpp:1458-1463`); it discloses strictly less than the part
  fetch on the same endpoint.
- **`pool_id` is a uniqueness token, not a secret.** Minted from `thread_local_rng`
  (`Pool/CasPoolMeta.cpp:24-29`) and advertised in the clear on the wire
  (`DataPartsExchange.cpp:99, 591`). Correct for its purpose; flagged only so it is not later
  mistaken for a capability.

## Coverage

Read in full: `Formats/CasFormat.{h,cpp}`, `Formats/CasTextFormat.{h,cpp}`,
`Formats/CasByteBudget.h`, `Formats/CasLayout.{h,cpp}`, `Formats/CasPoolMetaFormat.cpp`,
`Formats/CasPartManifestFormat.cpp`, `Formats/CasBlobEnvelopeFormat.cpp`,
`Formats/CasRecordStreamFormat.cpp`, `Primitives/CasXxh3Streamer.h`,
`Primitives/CasBlobDigest.cpp`, `Primitives/CasCodecUtil.h`, `Primitives/CasEvent.cpp`,
`Parts/PartPathParser.cpp`, `Pool/CasPoolMeta.cpp`, `Pool/CasMountRuntime.cpp`,
`Pool/CasServerRoot.cpp` (through line 800), `Pool/CasBlobUploadPool.cpp`,
`Backend/CasRequestControl.h`, `ContentAddressedExchange.cpp`, `ContentAddressedSettings.cpp`
(settings block), `programs/disks/CommandCaDropMember.cpp`.

Read in part: `Backend/CasObjectStorageBackend.cpp` (transport read/get paths, 275-530),
`ContentAddressedMetadataStorage.cpp` (exchange surface, 1450-1638),
`Pool/CasPartWriteTxn.cpp` (adopt/observe paths), `Parts/PartFolderAccess.cpp`
(`prepareEntries` and neighbours), `src/Storages/MergeTree/DataPartsExchange.cpp` (CAS
branches), `src/Interpreters/InterpreterSystemQuery.cpp` (CAS verb handling and required
access), `src/Access/Common/AccessType.h`, `src/Parsers/ParserSystemQuery.cpp`.

Grepped exhaustively across `src/` for: all seven `SYSTEM_CAS_*` access types and their check
sites; credential identifiers (`access_key`, `secret_access_key`, `password`, `token`,
`credential`) inside the CAS tree; `manifestNamespaceMatches` call sites;
`decodeCasRelinkSourceToken` consumers; CAS system-table registrations.

Not covered (out of this audit's lane, or covered by siblings): `Gc/CasGc.cpp` GC-round
protocol logic beyond its manifest-namespace and run-stream checks (gc-protocol,
gc-rebuild-feature); `Tools/CasFsck.cpp` and `Tools/CasDecommission.cpp` internals; the read
path's verification behaviour (read-protocol — cited above, not re-derived); crash/interleaving
semantics (crash-consistency, interleaving); `Pool/CasServerRoot.cpp:800-1170`. No dynamic
analysis, fuzzing, or collision-cost measurement was performed; the CityHash128 collision
claim in security-2 rests on the published properties of a non-cryptographic hash, not on a
constructed collision.
