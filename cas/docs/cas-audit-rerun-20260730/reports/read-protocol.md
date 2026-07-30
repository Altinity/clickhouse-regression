# read-protocol — re-run 2026-07-30

Static audit of the CAS read pipeline against the current PR
(`altinity/cas-gc-rebuild`, worktree at `/Volumes/workspace/ClickHouse`,
branch `cas-audit-20260730`). All anchors are current-HEAD file:line paths under
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`.

Scope (per user): CAS-001, CAS-005, CAS-024, CAS-049, CAS-086, CAS-087,
CAS-034, CAS-098, CAS-095, CAS-085.

## Scope in current code

- Files/dirs walked:
  - `ContentAddressedMetadataStorage.cpp` — `getStorageObjects`,
    `getBlobViewPlan`, `readBlobPayload`, `tryGetInManifestBytes`,
    `prepareInManifestRead`.
  - `Parts/PartFolderAccess.{h,cpp}` — `CachedPartFolderAccess::getView`,
    `buildView` (single-flight), `resolve`, `PartFolderView::findFile`,
    `inlineBytes`.
  - `Pool/CasManifestReader.{h,cpp}` — `readManifestShared`, `readManifest`,
    `locate`, manifest decode cache.
  - `Pool/CasRefLedger.{h,cpp}` — `resolveRef`, `ensureRefTableRecovered`.
  - `Pool/CasPool.{h,cpp}` — delegation of `resolveRef`/`readManifest*`/`locate`.
  - `Formats/CasBlobEnvelopeFormat.{h,cpp}` — envelope header + payload offset.
  - `Formats/CasPartManifestFormat.cpp` — `findEntry` (`std::lower_bound`).
  - `Formats/CasPoolMetaFormat.{h,cpp}` — `validatePoolBlobHeaderLen`
    (pool-wide fixed `blob_header_len`).
  - `Gc/CasGc.cpp` — two-phase graduation + `deleteExact` (context for CAS-001).

## Structural change vs original audit

The old per-shard TTL decode cache + `resolveRef(allow_stale)` fast-path is
**gone**. The ref layer is now an authoritative in-process `RefTableState` per
namespace (see `CasRefLedger::resolveRef`, `CasRefLedger.cpp:174` — the
`allow_stale` parameter is explicitly named `/*allow_stale*/` and the comment
states "no longer selects anything: this mounted writer is the ONLY writer of
`ns`'s ref state (no external CAS token to go stale against, unlike the old
per-shard decode cache), so the recovered-and-cached `RefTableState` is always
this process's authoritative view"). This retires several read-side hazards
architecturally rather than by fix: CAS-085 (`allow_stale` ↔ GC coupling) and
CAS-087 (force-fresh not fresh on eventually-consistent backends) no longer
have a code path to fire on the writer/owning mount. A read-only or cross-node
observer of another mount's namespace is out of scope for `CasRefLedger` — it
would have to recover the whole table via LIST-then-replay, so eventual
consistency of LIST is now the concern (compat item, tracked under CAS-058
in the summary, not in this audit's scope).

## Findings still present

### `CAS-001` — Reader holds no pin across the deferred blob GET

- Anchor: `ContentAddressedMetadataStorage.cpp:1886-1932`
  (`getBlobViewPlan` → `readBlobPayload`); `Pool/CasManifestReader.cpp:144-168`
  (`locate` returns `BlobLocation{key, offset, length}` and the manifest is
  discarded after plan); `Gc/CasGc.cpp:498-557` (GC's `deleteExact` graduation
  path is unchanged).
- Trigger: `resolveRef → readManifestShared → locate` runs at plan time; the
  actual ranged GET on the blob is issued later inside `readBlobPayload`
  against a raw `StoredObject(blob_key, …)`. Nothing between plan and GET
  registers a reader edge or holds a GC-honored token.
- Evidence quote (`getBlobViewPlan`, l.1909-1918):
  > `plan.object = StoredObject(physicalKey(location.key), path,
  > location.offset + location.length);` … the caller returns and the pipeline
  > issues the GET later.
- Notes: Same-mount readers are still incidentally fenced by MergeTree
  `DataPart` liveness (`old_parts_lifetime`) and by the fact that the ref
  ledger is the mounted writer (dropRef → ledger update is same-process). But
  a **cross-node** or **ref-less** reader (relink, another `server_root_id`
  reading a shared namespace, a diagnostic tool holding a plan) has no
  reader-side pin. GC's two-phase graduation (`delete_pending` → `deleteExact`)
  still only *bounds* the window; a slow GET can be raced by a full round.
  No `reader_pin` / `inflight_reads` construct exists anywhere in
  `MetadataStorages/ContentAddressed/` (grep negative). The finding is
  unchanged from the original R1/X1/MVCC-1 write-up.

### `CAS-005` — Payload never re-hashed against `logical_hash` on read

- Anchor: `ContentAddressedMetadataStorage.cpp:1923-1933` (`readBlobPayload`
  is a raw ranged GET wrapped in `ReadBufferFromFileView`, no hash);
  `Pool/CasPartWriteTxn.cpp:77` (comment: "The core otherwise never re-hashes
  payloads; any copy-forward…"); `Primitives/CasBlobHashingWriteBuffer.cpp:227`
  (write-side chained `HashingReadBuffer` — write only).
- Trigger: any read path — SELECT, CHECK TABLE flows through here.
- Evidence quote (`CasPartWriteTxn.cpp:77`):
  > "The core otherwise never re-hashes payloads; any copy-forward re-verifies…"
- Notes: Read path does no `logical_hash` re-verification and no
  content-hash re-derivation. Silent S3 bit-rot / truncation inside the payload
  region is undetected by CAS; integrity delegated to MergeTree's own
  checksums. Unchanged.

### `CAS-024` — `locate()` uses fixed `PoolMeta.blob_header_len`, not the blob's own envelope `header_len`

- Anchor: `Pool/CasManifestReader.cpp:151-160` (`locate` builds
  `BlobLocation{.offset = meta.blob_header_len, .length = entry.blob_size}`);
  `Formats/CasPoolMetaFormat.cpp:38-46` (`validatePoolBlobHeaderLen`);
  `Pool/CasPool.cpp:96-123` (pool-meta identity check on reopen refuses to
  mount if the observed pool's `blob_header_len` differs from the configured
  one).
- Trigger: Any read of a blob-backed entry uses `meta.blob_header_len` as the
  payload offset, never consults the on-object envelope `header_len`.
- Evidence quote (`CasManifestReader.cpp:146-149`):
  > "the pool's fixed `blob_header_len` — no per-object header read"
- Notes: The **structural** finding is unchanged: `locate` trusts a pool-wide
  scalar rather than parsing the envelope. It is **defused in practice** by
  `validatePoolBlobHeaderLen` (`CasPoolMetaFormat.cpp:38-46`) which fires on
  every pool-meta decode (mount + reopen) and rejects any `blob_header_len`
  that is not in `[kMinBlobHeaderLen, 16384]` and a multiple of 8, combined
  with the mount-time identity check (`CasPool.cpp:118-125`) that refuses to
  reopen a pool if the *observed* `blob_header_len` differs from what the
  process was configured with. A cross-version drift (writer with header_len
  A publishing into a pool the reader still thinks is B) is prevented at
  mount time. This makes CAS-024 **still-present as a structural trust, but
  unreachable under the current pool-meta contract**. Flag if the mount-time
  check is ever loosened, or if per-object envelopes ever diverge.

### `CAS-034` — Coalesced reader has no deadline (reader convoy)

- Anchor: `Parts/PartFolderAccess.cpp:264-303`
  (`CachedPartFolderAccess::buildView`).
- Trigger: On a cold `CachedForLoad` view build, concurrent readers of the
  same ref single-flight onto one leader via a `std::shared_future`; the
  leader's `store->readManifestShared(...)` (HEAD + GET + decode) has no
  bounded wait, and followers block on `future.get()` (`l.287`) with no
  timeout.
- Evidence quote (`PartFolderAccess.cpp:286-287`):
  > `if (!leader) return future.get();  /// Rethrows the leader's exception,
  > if any.`
- Notes: A hung leader HEAD or GET wedges every coalesced follower for the
  same `PartRefKey`. The scope moved from "shard read" (old design) to
  "part-folder view build," but the liveness cliff (unbounded shared-future
  wait) is identical. Only cold `CachedForLoad` is affected; `ForceFresh` /
  `StrictValidate` deliberately do not coalesce (`l.267-270`).

### `CAS-086` — `readManifest` HEAD+GET not coalesced at manifest layer, absence not negatively cached

- Anchor: `Pool/CasManifestReader.cpp:56-137` (`readManifestShared`).
- Trigger: Every call performs a mandatory `backend.head(key)` and, on
  cache-miss, `backend.get(key)`. No inflight-map at manifest granularity, no
  negative-cache entry on a `!head.exists` outcome.
- Evidence quote (`CasManifestReader.cpp:63-65`):
  > "`HEAD` is mandatory even on a cache hit. It proves that the live
  > reference still names an existing object…"
- Notes: `CachedPartFolderAccess::buildView` provides single-flight one layer
  up (see CAS-034), so *concurrent* callers of the same `PartRefKey` on the
  cold `CachedForLoad` path share one manifest HEAD+GET. `ForceFresh`
  bypasses that; two `ForceFresh` calls in flight both issue HEAD+GET.
  Absence never negatively-cached at any layer — an in-flight burst against a
  ref whose manifest is genuinely missing produces N HEAD storms.

### `CAS-095` — Envelope/manifest offset trust in the read-window arithmetic

- Anchor: `ContentAddressedMetadataStorage.cpp:1909-1918` (`getBlobViewPlan`
  computes `plan.payload_end = location.offset + location.length` and passes
  the object length as `location.offset + location.length` — no comparison to
  the real object size returned by any HEAD); `Pool/CasManifestReader.cpp:156-160`
  (locate stamps `.length = entry.blob_size` verbatim from the manifest).
- Trigger: A manifest whose `entry.blob_size` is larger than the real blob's
  payload region will produce a `ReadBufferFromFileView(_, path,
  location.offset, location.offset + location.length)` window that reads past
  the real object end.
- Evidence quote (`ContentAddressedMetadataStorage.cpp:1911-1914`):
  > "bytes_size is the readable extent of THIS file's window, NOT the whole
  > blob: a right-bounded read stops at payload_end…"
- Notes: The read path trusts (manifest offset, manifest length) with no
  cross-check against the actual object size. In practice the object side
  will surface EOF from the `readObject` layer as an EOF/short-read; the
  finding is a **structural trust**, not a proven exploit. It compounds with
  CAS-005 (no re-hash means length-wrong-but-bytes-there is invisible) and
  CAS-031 (relink receiver trusts sender-supplied `entry.blob_size`).

### `CAS-098` — Inline vs blob wide-part branch, correct-by-code but structurally coverage-relevant

- Anchor: `Parts/PartFolderAccess.cpp:85-108` (`findFile`, `inlineBytes`);
  `ContentAddressedMetadataStorage.cpp:1826-1830` (Inline placement returns
  `StoredObject("", path, entry->size())`, non-Inline calls
  `snap.pool->locate(*entry)`); `Pool/CasManifestReader.cpp:149-165`
  (`locate` throws `BAD_ARGUMENTS` for `EntryPlacement::Inline`).
- Trigger: Per-file resolve on a wide part chooses between an inline
  in-manifest read and a blob GET based on `entry.placement`. Both branches
  are exercised together in a wide part.
- Evidence quote (`CasManifestReader.cpp:162-164`):
  > `case EntryPlacement::Inline: throw Exception(BAD_ARGUMENTS, "entry
  > placement {} has no blob location"…)`
- Notes: **Code is correct** — each branch has a distinct return path and the
  invalid combination (Inline placement passed to `locate`) throws
  `BAD_ARGUMENTS`. The finding is retained as a **test-coverage** flag: no
  gtest exercises a wide part that mixes both branches with a mid-stream
  right-mark. Unchanged from original.

## Findings fixed / no longer reproducible

- `CAS-049` — Decode cache clear cliff at 16384 — **fixed**. The manifest
  decode cache is now a proper `CacheBase` LRU with `max_count = 16384`
  (`Pool/CasManifestReader.cpp:37-40`,
  `using ManifestDecodeCache = CacheBase<…>;` at `.h:92`). No wholesale-clear
  code path remains: eviction is per-entry LRU, keyed on
  `(ManifestId, Token)`. The shard-decode cache that the original R2/RES-3
  finding was written against has been removed entirely with the ref-ledger
  refactor.
- `CAS-085` — `allow_stale` ↔ GC condemn-latency coupling — **retired by
  design**. There is no TTL fast-path anymore. `CasRefLedger::resolveRef`
  ignores `allow_stale` (`CasRefLedger.cpp:174-181`); the mounted writer
  serves its own authoritative in-process ref table. The convention→invariant
  gap the original R3 named no longer has a code path.
- `CAS-087` — Force-fresh not fresh on eventually-consistent backends —
  **retired for the owning mount** by the same refactor. The read path no
  longer performs a HEAD-then-GET on the *ref* against the object store; ref
  state is in-process. The finding still lives on cross-node readers whose
  ref-table recovery depends on backend LIST semantics, but that folds into
  CAS-058 (read-your-writes LIST is a per-backend assumption) rather than
  CAS-087 as originally scoped.

## New findings (not in original audit)

- **NEW-read-1 (Med, liveness)** — `readManifestShared` HEAD-GET race window
  amplifies dangle. Anchor `Pool/CasManifestReader.cpp:65-90`: the HEAD at
  `l.65` and the GET at `l.87` are separate backend round-trips. A GC that
  deletes the manifest object between them surfaces as
  `"manifest at {} vanished between head and get — INV-NO-DANGLE"` (`l.89-90`,
  `FILE_DOESNT_EXIST`). Fail-loud, so this is a **liveness** issue, not a
  correctness one — but it is a same-manifest instance of the CAS-001 class
  applied to *manifests* (not just blobs), previously not called out for the
  manifest object itself.
- **NEW-read-2 (Low, coverage)** — Retained-view age policy uses wall-clock
  `now_ms_fn()` (`PartFolderAccess.cpp:203`) subtracted from
  `cached->validatedAtMs()`. On backward wall-clock movement (NTP step) the
  freshness gate can either extend indefinitely (past > now) or refuse every
  cached view. Same J3 clock-skew class as CAS-030 but on a purely
  read-serving cache; no correctness impact (a stale view has to re-prove
  against the fresh resolve), only a perf oscillation.
- **NEW-read-3 (Info)** — `CachedPartFolderAccess::buildView` single-flight
  drops leader exceptions onto every follower (`l.301: promise.set_exception`).
  This means one HEAD failure fans out to N `FILE_DOESNT_EXIST` errors for N
  coalesced readers. Correct semantically (they were asking the same
  question) but distinguishes coalesced from independent readers in error
  budgets / retry storms.

## By-design / N/A / info

- Manifest decode cache is keyed on `(ManifestId, Token)` and does not share
  across ids — original R2, retained as `CAS-205` (verified-safe /
  by-design). Confirmed unchanged at `Pool/CasManifestReader.cpp:43-54`.
- `findEntry` is `std::lower_bound` — O(log N), the CAS-116 wide-part
  slowness is fixed (`Formats/CasPartManifestFormat.cpp:329-336`). Outside
  the read-protocol audit scope but touched by every read.
- `readBlobPayload` gate: `checkOpAdmitted(CasOpClass::ContentRead)`
  (`ContentAddressedMetadataStorage.cpp:1928`) — a Vanished disk fails-loud
  rather than returning empty; consistent with INV-NO-DANGLE.
- In-manifest bytes served from memory (`tryGetInManifestBytes`,
  `prepareInManifestRead`) never touch the object store; force-fresh
  `txn_version` reads work through this path (bypasses the view cache) — no
  new hazard in the read protocol.

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-001 | Med-High | 🔴 still-present | `ContentAddressedMetadataStorage.cpp:1886-1932`; `Pool/CasManifestReader.cpp:144-168` |
| CAS-005 | High | 🔴 still-present | `ContentAddressedMetadataStorage.cpp:1923-1933`; `Pool/CasPartWriteTxn.cpp:77` |
| CAS-024 | Med | 🔴 still-present (📐 defused by mount-time pool-meta identity check) | `Pool/CasManifestReader.cpp:151-160`; `Formats/CasPoolMetaFormat.cpp:38-46`; `Pool/CasPool.cpp:118-125` |
| CAS-034 | Med | 🔴 still-present | `Parts/PartFolderAccess.cpp:264-303` |
| CAS-049 | Med (perf) | ✅ fixed | `Pool/CasManifestReader.cpp:37-40` (LRU `CacheBase`, `max_count=16384`, per-entry eviction) |
| CAS-085 | Low | ✅ fixed (retired by design) | `Pool/CasRefLedger.cpp:174-181` (`allow_stale` no-op) |
| CAS-086 | Low | 🔴 still-present (partly masked by CAS-034 single-flight on `CachedForLoad`) | `Pool/CasManifestReader.cpp:56-137` |
| CAS-087 | Low | ✅ fixed for owning mount (out-of-scope for cross-node under CAS-058) | `Pool/CasRefLedger.cpp:174-181` |
| CAS-095 | Med | 🔴 still-present (structural trust, EOF-guarded downstream) | `ContentAddressedMetadataStorage.cpp:1909-1918`; `Pool/CasManifestReader.cpp:156-160` |
| CAS-098 | Test-gap | ⚪ info (code correct; explicit coverage still absent) | `Parts/PartFolderAccess.cpp:85-108`; `ContentAddressedMetadataStorage.cpp:1826-1830`; `Pool/CasManifestReader.cpp:149-165` |
| NEW-read-1 | Med (liveness) | 🔴 still-present | `Pool/CasManifestReader.cpp:65-90` |
| NEW-read-2 | Low (perf) | 🔴 still-present | `Parts/PartFolderAccess.cpp:197-213` |
| NEW-read-3 | Info | 🔴 still-present | `Parts/PartFolderAccess.cpp:299-303` |
