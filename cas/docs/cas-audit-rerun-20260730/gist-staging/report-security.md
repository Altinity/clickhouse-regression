# cas-security-audit — re-run 2026-07-30

Static re-audit of the CAS **security** surface against PR
[Altinity/ClickHouse#2073](https://github.com/Altinity/ClickHouse/pull/2073)
(branch `altinity/cas-gc-rebuild`, working copy pinned at `cas-audit-20260730`).

Scope in this pass: trust model, auth, tamper surface. Findings re-verified from the original
report: **CAS-002** (fencing), **CAS-003** (CityHash128 collision poisoning), **CAS-004** (no
intra-pool authz), **CAS-026** (protobuf OOM), **CAS-030** (NTP-spoof amplification), **CAS-074**
(path traversal in `checkNamespace` / `mountpointObjectKey`), **CAS-108** (SYSTEM RBAC gating for
GC REBUILD), **CAS-211** (self-asserted provenance). Also focused on input validation, size caps,
and path validation across the trust boundary.

## Scope in current code

Files/dirs walked:

- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`
  - `Primitives/` — `CasBlobDigest.{h,cpp}`, `CasBlobHashingWriteBuffer.{h,cpp}`,
    `CasXxh3Streamer.h`, `CasEvent.h`
  - `Formats/` — `CasFormat.{h,cpp}` (registry + caps), `CasLayout.{h,cpp}`,
    `CasBlobEnvelopeFormat.h`, `CasRecordStreamFormat.h`, `CasPartManifestFormat.h`,
    `CasServerRootFormats.{h,cpp}`, `README.md`
  - `Pool/` — `CasPool.{h,cpp}`, `CasMountRuntime.{h,cpp}`, `CasPlainObjects.{h,cpp}`,
    `CasPartWriteTxn.{h,cpp}`, `CasRefLedger.{h,cpp}`, `CasServerRoot.{h,cpp}`, `CasRefProtocol.cpp`
  - `Gc/` — `CasGc.{h,cpp}` (rebuild)
- `src/Access/Common/AccessType.h` (CAS access types)
- `src/Interpreters/InterpreterSystemQuery.cpp` (SYSTEM RBAC checks + rebuild wiring)

Focused inspection on: hash-algorithm selection, envelope layout, decoder size caps, key
construction / traversal, mount-lease liveness protocol, `writer_epoch` fencing on durable writes,
`SYSTEM CONTENT ADDRESSED GC REBUILD` gating.

## Findings still present

### CAS-004 — No intra-pool authorization; identities are self-asserted 🔴
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasServerRoot.h:305-329`
  (`claimMount`); `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasBlobEnvelopeFormat.h:35-44`
  (`Provenance`); pool-wide use of a single S3 credential (all backends).
- Trigger: any peer that holds the bucket credential can forge a mount body (`server_uuid`,
  `writer_epoch`, `seq`, `expires_at_ms`), rewrite `gc/state`, poison/delete blobs, and overwrite
  `_pool_meta` — nothing on the object plane is signed.
- Evidence quote (from mount-lease claim doc):
  > "`different server_uuid` → `ForeignOwner` (do NOT write, regardless of expiry or prior state)."
  Enforcement is purely convention: the wire body is trusted at face value; any pool-write peer can
  set `server_uuid` to whatever it wants.
- Notes: Architectural / by-design. Unchanged since the original audit. The mount-lease
  observation-based reclaim (see CAS-030 below) hardens against **accidental** clock skew but does
  nothing against an adversarial peer that owns the credential.

### CAS-074 — `checkNamespace` and `mountpointObjectKey` do not reject `.` / `..` segments 🔴
- Anchor:
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasLayout.cpp:260-284`
  (`Layout::checkNamespace`) and
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasLayout.h:229-235`
  (`Layout::mountpointObjectKey`).
- Trigger: a namespace or mountpoint key containing a `..` or `.` segment reaches the key builder
  intact.
- Evidence quote (`checkNamespace`):
  > `if (segment.empty()) throw ...` and `if (segment == "_files")` / `if (segment == "_manifests")`
  > throw. Nothing rejects `..` or `.`.

  `mountpointObjectKey`:
  > `if (key.empty() || key.front() == '/' || key.back() == '/' || key.find("//") != String::npos)`
  > throw. No `..` check.
- Notes: `namespaceFileKey`
  (`CasLayout.h:179-189`) **does** now explicitly reject `..` in the file-name argument. The
  namespace itself, and `mountpointObjectKey`, remain safe **only** because production backends are
  object stores with literal, non-normalized keys (`srv1/../gc` is a distinct key, not traversal).
  A future filesystem-backed or normalizing backend, or a plain-`Local` backend that lowers keys
  through `std::filesystem::path`, would traverse into the control plane. Cheap defense-in-depth:
  reject `.` and `..` segments in `checkNamespace` and in `mountpointObjectKey`'s per-segment scan.

### CAS-211 — Provenance and CasEvent are self-asserted / forgeable ⚪ (info, unchanged)
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasBlobEnvelopeFormat.h:35-44`
  (`Provenance {created_at_ms, creator_server_id, ch_version, op}`);
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasEvent.h`
  (event sink is a diagnostic pipe, no signing).
- Trigger: any pool-write adversary can stamp arbitrary `creator_server_id` / timestamps into an
  envelope or into a `CasEvent`; a peer forensic reader has no way to distinguish forged bodies.
- Evidence quote (envelope-header doc):
  > "It is metadata for inspection and attribution only; readers do not use it to make storage or
  > compatibility decisions."
- Notes: By-design informational — provenance is a debugging aid, not an integrity control. Same
  posture as the original audit; no code path exposes it as an attribution primitive.

### CAS-108 (residual) — `GC REBUILD` DoS / amplification surface 🔴 (RBAC dedicated ✅, cost surface unchanged)
- Anchor: dedicated grant `AccessType::SYSTEM_CONTENT_ADDRESSED_GC_REBUILD`
  (`src/Access/Common/AccessType.h:352`); enforced at
  `src/Interpreters/InterpreterSystemQuery.cpp:1028-1033` and the runner at
  `src/Interpreters/InterpreterSystemQuery.cpp:2487-2503`; core loop
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGc.cpp:2488` (`rebuildBaseline`).
- Trigger: an operator holding the (now dedicated) grant can repeatedly issue
  `SYSTEM CONTENT ADDRESSED GC REBUILD <disk>` — each invocation triggers a full universe scan
  + fold across every shard and journal in the pool, and there is no rate-limit / single-flight on
  the command. Interrupted rebuilds leak `gc/gen/...` artifacts and ratchet the generation
  (§7 of the original audit).
- Evidence quote (interpreter):
  > `getContext()->checkAccess(AccessType::SYSTEM_CONTENT_ADDRESSED_GC_REBUILD);`
  > `result = runContentAddressedGcRebuild(query.disk, query.content_addressed_gc_rebuild_force);`
- Notes: The **RBAC narrowing** the original audit asked for is present and clean — separate access
  types exist for `GC_RUN`, `GC_REBUILD`, `DROP_POOL_MEMBER`, `FSCK`, `FORGET`, `GC_STOP`,
  `GC_START` (`AccessType.h:351-357`). The rebuild also now requires an EXPLICIT disk name (no
  node-wide fan-out — `runContentAddressedGcRebuild` throws `BAD_ARGUMENTS` on empty disk). The
  residual DoS / amplification surface (unbounded universe walk, no single-flight, per-round HEADs)
  remains — this maps to CAS-050 and CAS-108's operational-cost portion.

## Findings fixed / no longer reproducible

### CAS-003 — CityHash128 blob poisoning (via pool-global dedup) ✅ largely fixed
- Anchor for the fix:
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasBlobDigest.h:38-57`
  (`BlobHashAlgo {CityHash128, XXH3_128, Sha256}` + `parseBlobHashAlgo`);
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasBlobHashingWriteBuffer.cpp:201-218`
  (`makeBlobHashingWriteBuffer` returns `CityHash128BlobHashingWriteBuffer` /
  `Xxh3128BlobHashingWriteBuffer` / `Sha256BlobHashingWriteBuffer`);
  `CasBlobDigest.h:207-214` (`BlobRef {algo, digest}` — bare digest is *never* a blob identity);
  README (`Formats/README.md:39-40`) — blob digests are "algo-width hex ... rendered with their algo
  name (`sha256:ab12…`)". Blob object keys now carry the algo path segment (`blobs/<algo>/<shard>/<hex>`
  — `CasBlobDigest.h:45-47`).
- Why fixed: operators can pick a cryptographic hash (`sha256`) for pools that span trust domains;
  algo is pinned per-blob (in `BlobRef` and in the object key), so a future algorithm change or
  mixed-algo pool cannot silently fork or collide. The old "single unversioned CityHash128
  contract" of the original audit is gone; the algo is a first-class per-blob identity attribute.
- **Residual:** the *default* remains `CityHash128` (see `BlobRef` initializer at
  `CasBlobDigest.h:209` and `blobHashAlgoName`'s "ch128" mapping). Deployments that don't
  explicitly set `blob_hash = sha256` retain the poisoning-via-collision surface described in
  SEC-1. This is documentation / default-hardening, not a code bug. See NEW-security-1 below.
  Additionally, XXH3-128 is faster than CityHash128 but is **also not collision-resistant**, so
  selecting `xxh3-128` does not close SEC-1 either.

### CAS-030 — NTP-spoof amplification via wall-clock lease-expiry ✅ largely fixed
- Anchor for the fix:
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasServerRoot.h:305-421`
  (`claimMount` + `claimMountAwaitingExpiry`);
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasServerRoot.cpp:376-421`
  (heartbeat-gate observation).
- Why fixed: reclaim of a live-double-start mount now requires a **certificate of death** —
  `gc_fenced` on the predecessor, the graceful-farewell sentinel `min_active == UINT64_MAX`, or the
  observer proving token stability across `ttl_ms + ttl_ms/20 + poll_interval` on its own
  monotonic clock — not a comparison of the lease's stamped `expires_at_ms` against wall-time. The
  design explicitly documents:
  > "`expires_at_ms <= now_ms` ALONE is never sufficient — comparing a predecessor's stamp against
  > OUR wall clock is unsafe."
- **Residual:** wall-clock is still used to STAMP `expires_at_ms` on written bodies (diagnostics
  only) and to bound the mount-lease budget (`refAppendFenceOk`). An adversary who can skew the
  writer's clock forward can shorten the writer's own remaining budget (self-DoS, not an unfair
  reclaim by a peer). The security-critical amplification vector is closed.

### CAS-026 — Protobuf `ParseFromArray` OOM ✅ eliminated
- Anchor for the fix: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/README.md:9-13`:
  > "The object inventory is text end to end — there are no binary CAS formats and no protobuf
  > dependency."

  Format registry with fail-closed per-format decompressed size caps at
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasFormat.cpp:93-109`:
  ```
  {FormatId::Blob,         ...,  CompressionPolicy::Never,     256,        256}
  {FormatId::BlobMeta,     ...,  CompressionPolicy::Never,     1 * kMiB,   64 * kKiB}
  {FormatId::PoolMeta,     ...,  CompressionPolicy::Never,     1 * kMiB,   64 * kKiB}
  {FormatId::RefLog,       ...,  CompressionPolicy::Always,    64 * kMiB,  64 * kMiB}
  {FormatId::RefSnapshot,  ...,  CompressionPolicy::Always,    64 * kMiB,  64 * kMiB}
  {FormatId::PartManifest, ...,  CompressionPolicy::Always,    256 * kMiB, 64 * kKiB}
  {FormatId::RunFile,      ...,  CompressionPolicy::PinnedRaw, 0,          4 * kKiB}
  {FormatId::FoldSeal,     ...,  CompressionPolicy::Always,    256 * kMiB, 64 * kKiB}
  {FormatId::GcState,      ...,  CompressionPolicy::Never,     1 * kMiB,   64 * kKiB}
  {FormatId::GcHeartbeat,  ...,  CompressionPolicy::Never,     1 * kMiB,   64 * kKiB}
  {FormatId::GcOutcomes,   ...,  CompressionPolicy::Always,    256 * kMiB, 64 * kKiB}
  {FormatId::Owner,        ...,  CompressionPolicy::Never,     1 * kMiB,   64 * kKiB}
  {FormatId::ServerEpoch,  ...,  CompressionPolicy::Never,     1 * kMiB,   64 * kKiB}
  {FormatId::MountLease,   ...,  CompressionPolicy::Never,     1 * kMiB,   64 * kKiB}
  ```
  Comment above the table (`CasFormat.cpp:77`): "Caps are 100-1000x above realistic sizes; hitting
  one indicates a corrupt object or protocol bug." `RunFile` is `object_cap = 0` (never
  materialized whole — streamed one line at a time; `line_cap = 4 KiB`), which is exactly the
  "stream the fold" recommendation from SEC-4.
- Why fixed: no `ParseFromArray` call site exists anywhere in the CAS tree
  (`Grep ParseFromArray|ParseFromString` returns no matches under
  `ContentAddressed/`). Every decodable object has an absolute decompressed cap enforced
  before decode, independent of the write path. The declared-content-size vs cap check is
  documented in `Formats/README.md:5-7` ("`.zst` ... declared content size checked against the cap
  before allocation").

## Partially fixed

### CAS-002 — Shard `casPut` fenced by content token, not `writer_epoch` 🟡 mitigated (still not a store-enforced fence)
- Anchor:
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPlainObjects.cpp:21-57`
  (`CasPlainObjects::casPutObject`) — the sole conditional-CAS chokepoint for pool-meta / mount /
  namespace / mountpoint object writes.
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasMountRuntime.{h,cpp}`
  (`fenceGeneration()` / `checkFenceOrThrow`).
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPartWriteTxn.cpp:676-747`
  (part-write displacement re-checks the captured generation before every raw write).
- What's better: the fence is now **generation-tracked**, and every conditional-CAS site
  captures `fence_generation_fn()` at admission and calls `check_fence_or_throw_fn(admitted_generation)`
  **immediately before each backend write attempt** (line 43 for `putIfAbsent` / `putOverwrite`,
  line 82 for `deleteExact`). A lost-then-re-armed mount lease bumps `fence_generation`
  (`CasMountRuntime.cpp:92`: `fence_generation.fetch_add(1, ...)`), so a stale writer whose lease
  was reclaimed and reissued will fail closed with a typed transient before any durable write.
  The doc explicitly cites this as "rev.7 [C2]" — "the fence generation captured at admission is
  re-checked immediately before EVERY durable PUT below, not just the first attempt."
- What's still not fixed: the S3-side precondition on the CAS itself is still an **ETag / content
  token**, not a `writer_epoch` predicate on the object. Between `check_fence_or_throw_fn`
  (`CasPlainObjects.cpp:43`) and `backend.putOverwrite(..., head.token)` (line 51) a long STW
  pause on this process can still land a stale writer's PUT at the backend. The window is now
  small (in-process check → immediate PUT) but not zero, and — critically — no in-store predicate
  cross-checks that the writer's epoch is the current one. A malicious peer that owns the bucket
  credential (SEC-3 / CAS-004) can bypass the local fence entirely because the local generation
  counter is unauthenticated.
- Verdict: **mitigated for accidental faults** (pause-TOCTOU on the same process, clock-based
  reclaim from a peer), **not fixed for the adversary case**. Original recommendation still stands:
  carry `writer_epoch` into the CAS precondition (or sign the object body with an
  epoch-bound MAC) so the *store*, not a local check, enforces the fence.

## New findings (not in original audit)

- **NEW-security-1** — *`BlobHashAlgo` default is `CityHash128`.* Severity: **Med** (documentation
  + default-hardening). Anchor:
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasBlobDigest.h:207-214`
  (`BlobRef { BlobHashAlgo algo = BlobHashAlgo::CityHash128; ... }`);
  `parseBlobHashAlgo` (`CasBlobDigest.cpp:33-45`) allows `cityhash128 | xxh3-128 | sha256` but
  does not privilege `sha256`. Trigger: a pool created without an explicit `blob_hash = sha256`
  disk-config value inherits the non-crypto default. In a multi-trust-domain pool, this reverts
  CAS-003 to its original posture. Recommendation: when the pool spans trust domains, the
  disk-config parser should require an explicit `blob_hash` choice, warn on `cityhash128`, and
  document `sha256` as the recommended default; alternatively, flip the default to `xxh3-128` at
  minimum (which is at least not the audit's known-collidable target) and to `sha256` for shared
  pools.

- **NEW-security-2** — *`Xxh3128BlobHashingWriteBuffer::finalizeImpl` is not overridden;
  `getHashHex` calls `next()` but skips `finalize()`, and the class also lacks a `cancelImpl`.*
  Severity: **Low** (correctness / clean-shutdown). Anchor:
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasBlobHashingWriteBuffer.cpp:96-134`.
  Compare to `CityHash128BlobHashingWriteBuffer` (`:78-87`) which overrides both `finalizeImpl`
  and `cancelImpl` and forwards them to the nested `HashingWriteBuffer`. The XXH3 buffer relies on
  `BufferWithOwnMemory<IBlobHashingWriteBuffer>`'s inherited finalize path (which forwards to
  `sink` implicitly), but the sink is not finalized here explicitly on cancel — a mid-upload
  exception on the XXH3 path can leave the underlying sink dangling with data. Not a
  security-critical finding on its own but flagged because the write-buffer trio is a security
  chokepoint. Recommendation: mirror the `CityHash128BlobHashingWriteBuffer` finalize/cancel
  overrides across all three subclasses.

- **NEW-security-3** — *`_pool_meta` / `_manifests` / `_files` reserved-segment gate does not
  include the newer reserved prefixes in the `roots/` and `blobs/` trees.* Severity: **Low**
  (defense in depth). Anchor:
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasLayout.cpp:274-279`
  rejects `_files` and `_manifests` in a namespace, but the `roots/`, `blobs/`, `cas/refs/`,
  `cas/manifests/`, `gc/` and `gc/server-roots/` trees now also carry reserved subtrees
  (e.g. `blobs/<algo>` — see `CasBlobDigest.h:45-47`, and `cas/refs/<ns>/…_log|_snap` — see
  `Formats/README.md:22-24`). `checkNamespace` only rejects two literal segment names.
  Trigger: an admin-controlled namespace that happens to be named `refs` or `manifests` collides
  with the control-plane prefix inside its own `roots/<ns>/…` layout when the layout code paths
  concatenate (it doesn't today, because the split is at the prefix level, but the gate is not
  future-proof against a re-layout). Recommendation: enumerate the reserved namespace segments
  from a single registry in `Formats/README.md` and drive `checkNamespace` from it.

- **NEW-security-4** — *`mountpointObjectKey` and `checkNamespace` accept single-character
  segments `.` and `..`.* (Sub-finding of CAS-074, called out separately for the mountpoint path.)
  Severity: **Low**. Anchor: `CasLayout.h:229-235`. Trigger: caller passes a key such as
  `srv1/../gc/state` — the current key builder yields `<prefix>/roots/srv1/../gc/state`. On an
  object store this is a distinct literal key (safe); on `LocalObjectStorage`
  (`src/Disks/DiskObjectStorage/ObjectStorages/Local/LocalObjectStorage.cpp` exists as a real
  backend option and is exercised by tests) or on any future path-normalizing wrapper this
  traverses into the control plane. Recommendation: add the same `..` / `.` per-segment scan that
  `namespaceFileKey` (`CasLayout.h:182-184`) already does. Trivial patch.

## By-design / N/A / info

- **SEC-3 architectural framing** — CAS's whole security perimeter is the S3 bucket credential.
  The rebuild feature (`Gc::rebuildBaseline`, `CasGc.cpp:2488`) is a *recovery* tool for
  accidental `gc/state` loss, not a defense against an active in-pool adversary. Documented as
  such in the design doc (`Pool/CasServerRoot.h:305`ff). Unchanged.
- **SEC-6 rebuild RBAC** — dedicated grant present (`AccessType.h:352`), enforced
  (`InterpreterSystemQuery.cpp:1030`), and the disk argument is required (fail-closed on
  empty). The original audit's "confirm the grant is dedicated" recommendation is satisfied.
- **SEC-9 confidentiality** — blobs remain plaintext by design; CAS delegates encryption to S3
  SSE. Unchanged.

## Verdict summary table

| CAS-id  | Old severity  | Status                                              | Evidence anchor |
|---------|---------------|-----------------------------------------------------|-----------------|
| CAS-002 | High          | 🟡 mitigated (in-process fence-generation gate; store-side CAS still ETag-only) | `Pool/CasPlainObjects.cpp:21-57`, `Pool/CasMountRuntime.{h,cpp}`, `Pool/CasPartWriteTxn.cpp:676-747` |
| CAS-003 | High          | ✅ largely fixed (pluggable `sha256` / `xxh3-128` / `cityhash128`; algo pinned per-blob) | `Primitives/CasBlobDigest.{h,cpp}`, `Primitives/CasBlobHashingWriteBuffer.cpp:201-218` |
| CAS-004 | High          | 🔴 still-present · 📐 by-design (architectural)     | `Pool/CasServerRoot.h:305-329`; single-credential bucket assumption pool-wide |
| CAS-026 | Med           | ✅ fixed (protobuf removed; text formats with fail-closed per-format decompressed caps) | `Formats/README.md:9-13`, `Formats/CasFormat.cpp:93-109` |
| CAS-030 | Med           | ✅ largely fixed (wall-clock never trusted; observation-based reclaim on monotonic clock) | `Pool/CasServerRoot.h:305-421`, `Pool/CasServerRoot.cpp:376-421` |
| CAS-074 | Low           | 🔴 still-present (mountpoint + `checkNamespace` don't reject `..`/`.`) | `Formats/CasLayout.cpp:260-284`, `Formats/CasLayout.h:229-235` |
| CAS-108 | Low–Med       | 🟢 RBAC dedicated ✅ / 🔴 DoS-amplification surface still open (no single-flight / rate-limit) | `Access/Common/AccessType.h:352`, `Interpreters/InterpreterSystemQuery.cpp:1028-1033,2487-2503`, `Gc/CasGc.cpp:2488` |
| CAS-211 | Info          | ⚪ info · 📐 by-design (provenance is diagnostic)   | `Formats/CasBlobEnvelopeFormat.h:35-44` |

## Return summary

- **Path**: `cas/docs/cas-audit-rerun-20260730/reports/security.md`
- **Counts**: 8 original findings re-checked → 3 still-present (CAS-004, CAS-074, CAS-108-residual),
  1 partially fixed (CAS-002), 3 fixed / largely fixed (CAS-003, CAS-026, CAS-030), 1 unchanged
  by-design info (CAS-211). **4 new findings** added (NEW-security-1..4).
- **New findings**:
  - NEW-security-1 (**Med**): `BlobHashAlgo` default is `CityHash128`; a pool that spans trust
    domains without an explicit `blob_hash = sha256` inherits the CAS-003 posture.
    Anchor: `Primitives/CasBlobDigest.h:209`.
  - NEW-security-2 (**Low**): `Xxh3128BlobHashingWriteBuffer` (and by symmetry the SHA-256 variant)
    do not override `finalizeImpl`/`cancelImpl` like the CityHash variant does — mid-upload
    cancellation on the newer hash paths does not explicitly finalize the sink.
    Anchor: `Primitives/CasBlobHashingWriteBuffer.cpp:96-134`.
  - NEW-security-3 (**Low**): `checkNamespace` reserved-segment gate only covers `_files` and
    `_manifests`; other reserved subtrees (`refs`, `manifests`, `blobs/<algo>`, `gc/server-roots`)
    are outside the gate. Not exploitable today because the layout separates at the *prefix*, not
    the segment, but the gate is not future-proof.
    Anchor: `Formats/CasLayout.cpp:274-279`.
  - NEW-security-4 (**Low**): `mountpointObjectKey` doesn't reject `..` / `.` segments (sub-finding
    of CAS-074, called out separately because the mountpoint path is a distinct code path with a
    distinct fix). Anchor: `Formats/CasLayout.h:229-235`.
