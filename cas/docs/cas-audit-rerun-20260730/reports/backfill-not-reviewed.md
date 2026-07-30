# backfill-not-reviewed — re-run 2026-07-30

## Scope
All 39 previously not-reviewed CAS-### ids.

CAS source: `/Volumes/workspace/ClickHouse` branch `cas-audit-20260730`.
CAS root: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`.
Cross-checked sibling reports (`ad2`, `ad3`, `ad4`, `ad7`, `encryption`, `upgrade-compat`,
`codeonly-line`, `bc5`, `tier4`, `coverage-map`, `datatype-agnosticism`, `performance`,
`write-protocol`) then re-anchored in current code.

## Findings still present

### HIGH

**CAS-018** — No bounded delete→physical-erase SLA · 🔴 still-present
- Anchor: `ContentAddressedTransaction.cpp:1034-1036` (`removeRecursive`: "pointer-unlink + deferred GC"); no SLA knob in `ContentAddressedSettings.cpp`.
- Trigger: DROP/TRUNCATE/DROP PARTITION/TTL on a CAS table.
- Notes: reclaim remains GC-deferred (`Gc/CasGc.cpp` condemn→delete_pending→deleteExact); stallable by leader, retention floor, `suppress_destructive`.

**CAS-019** — Dedup means one owner's delete may erase nothing · 🔴 still-present
- Anchor: `Gc/CasBlobInDegree.cpp:364-448` (in-degree→condemn); `Pool/CasRefLedger.cpp:2801,2890` (`dropRef`/`dropNamespace` drop edges, not blobs).
- Trigger: delete content that is byte-identical to any other live ref (table/partition/FREEZE/replica).
- Notes: no per-subject shred; reachability is pool-global by design of content addressing.

**CAS-046** — DiskEncrypted random-IV defeats content-addressed dedup · 🔴 still-present
- Anchor: absence of encryption-aware hashing in `Backend/CasObjectStorageBackend.cpp`; `DiskEncrypted` still uses per-file random IV (`src/Disks/DiskEncrypted.cpp` / `DiskEncryptedTransaction.h`).
- Trigger: wrap CAS disk with `type: encrypted` → identical plaintext → distinct ciphertext → no dedup.
- Notes: CAS is encryption-agnostic; S3 SSE remains the recommended path (CAS-204).

**CAS-009** — Rolling upgrade across format-generation bump · 🔴 still-present (worsened)
- Anchor: `Formats/CasFormat.cpp:57-62` (`currentCompatibilityVersion()` = `G_BUILD`); `G_BUILD = 3` (`CasFormat.h:28`); write-down-to-floor unimplemented.
- Trigger: peer at older `G_BUILD` reads a freshly-written object.
- Notes: no longer latent; mixed-generation cluster fails closed on every new object / pool open.

### MEDIUM

**CAS-031** — Relink/rename receiver trusts sender `blob_size`/`path` · 📐 by-design (hardened)
- Anchor: `Pool/CasPartWriteTxn.cpp:794` (`adoptEvidence` records sender `entry.blob_size`, `adopted=true`); trust documented at `ContentAddressedExchange.h:220-224`.
- Notes: `entry.path` hygiene closed (`CasPartManifestFormat.cpp:198-267`); `payload_digest` verified on decode (`CasPartManifestFormat.cpp:293-302`). Residual blob_size trust equals ordinary ReplicatedMergeTree interserver trust; silent-misread class closed.

**CAS-042** — BACKUP Atomic-DB-only; incremental/RESTORE untested · 🔴 still-present
- Anchor: `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp:417-427` (hard-link BACKUP refused on CA for non-Atomic); no BACKUP→RESTORE integration test under `test_cas_*` / `test_content_addressed_*`.
- Notes: Atomic pointer-holding BACKUP works; Ordinary rejected fail-closed; incremental dedup + RESTORE round-trip still untested.

**CAS-047** — Two "size" semantics (payload vs envelope+payload) · 🔴 still-present
- Anchor: `ContentAddressedMetadataStorage.cpp:1793` (`getStorageObjects` → payload length) vs `:1915-1917` (`getBlobViewPlan` → envelope+payload extent + FileView window).
- Trigger: any reader that uses `getStorageObjects` without `DiskObjectStorage::prepareRead` + FileView.
- Notes: in-manifest empty-key placeholder fails loud (`:1756-1757`); blob-backed bypass still serves envelope-as-data.

**CAS-056** — `root_shards` fixed create-time constant · 🟡 partial/changed-shape
- Anchor: write-path numeric `root_shards` removed (snapshot+log; `discoverUniverse` reports `(ns, 0)` at `Gc/CasGc.cpp:2393-2411`). Analogous create-time constant is now `gc_shards` — set once at first `gc/state` acquire (`Gc/CasGc.cpp:3022-3025`; `ContentAddressedSettings.cpp:80`).
- Notes: write-parallelism constraint from old root-shard model is gone; GC reducer shard count remains immutable.

**CAS-057** — GC discovery LIST O(namespaces × shards) · 🟡 mitigated/changed-shape
- Anchor: `Gc/CasGc.cpp:2393-2411` — single LIST of `cas/refs/`, parse namespaces; no per-(ns,shard) fan-out.
- Notes: cost is now O(ref keys under `cas/refs/`), not O(namespaces × shards). Still LIST-bound at scale; no parallel discovery.

**CAS-058** — Read-your-writes / strongly-consistent LIST hard assumption · 🔴 still-present
- Anchor: `Pool/CasPool.cpp:1326-1328` (`listNamespaces`); `Gc/CasGc.cpp:2397-2398` (`discoverUniverse`) — both document S3-strong / InMemory guarantee; RustFS "to confirm".
- Notes: assumed, not enforced per-backend.

**CAS-059** — MergeTree experimental transactions (MVCC) untested on CAS · 🟡 partial
- Anchor: `tests/queries/0_stateless/05004_content_addressed_transactions.sh` (BEGIN/COMMIT/ROLLBACK oracle); comment notes "transactional multi-part merges are not yet implemented on CA disks — B53".
- Notes: basic txn visibility tested; multi-part MVCC / merge-under-txn / CAS-021 interaction still untested.

**CAS-060** — Failed-build debris only reclaimed by sweeps · 🔴 still-present
- Anchor: `Pool/CasServerRoot.cpp:1239-1274` (`sweepOwnMountStaging` — best-effort, only reclaim path for staging); `Gc/CasOrphanManifestSweep.*` + stale-precommit sweep in `Pool/CasRefLedger.cpp:2586-2677`.
- Trigger: OOM/disk-full mid-build storm → debris accumulates faster than sweep cadence.

**CAS-061** — Full-text (GIN/Text) & vector-similarity indexes untested on CAS · 🔴 still-present
- Anchor: absence — zero `text`/`GIN`/`vector_similarity`/`MATERIALIZE INDEX` matches under `tests/integration/test_*content_addressed*` / `test_cas_*`.
- Notes: storage is type-agnostic (CAS-202); wide GIN/vector segment dedup + MATERIALIZE-during-merge uncovered.

**CAS-062** — No lease/owner introspection or force-release runbook · 🟡 partial / 🛠 will-fix
- Anchor (fixed surface): `StorageSystemContentAddressedMounts.cpp:40-59` (lease/uuid/epoch/state/gc_fenced); `ASTSystemQuery.h:152` `CONTENT_ADDRESSED_DROP_POOL_MEMBER`; `Tools/CasDecommission.cpp`.
- Residual: no single documented force-release runbook covering reused `server_root_id` / stuck-lease edge cases end-to-end.

**CAS-063** — No PoolMeta / control-plane backup-restore story · 🔴 still-present
- Anchor: absence — no PoolMeta restore/backup tool under `Pool/` or `Tools/`; corrupt `_pool_meta` fails mount closed (`Pool/CasPoolMeta.cpp:106-124`).

**CAS-064** — `server_root_id` uniqueness operator-owned · 🔴 still-present
- Anchor: `Pool/CasServerRoot.h:188-223` (`checkServerRootId` validates shape only); collision → mount-lease outage (`CasServerRoot.cpp:428-432` message: "configure a unique `<server_root_id>`").
- Notes: uniqueness is still a config contract, not a cluster-enforced registry.

**CAS-065** — Azure / non-S3 unsupported for Native CAS · 🔴 still-present
- Anchor: `Backend/CasObjectStorageBackend.cpp:94-108` (`checkConditionalWriteSingleAttemptSupport` — Native requires SingleAttempt / S3-like dialect; else refuse); Emulated fallback for Local/tests only.
- Notes: Azure/non-S3 still effectively unsupported for production Native CAS.

**CAS-066** — `createOrValidate` silently ignores `root_shards`/`blob_header_len` when pool exists · 🔴 still-present
- Anchor: `Pool/CasPoolMeta.cpp:118-124` ("Present => the pool is authoritative; ignore the passed config's blob_header_len"); `Formats/CasPoolMetaFormat.h:20-21,35-36`.
- Notes: `root_shards` no longer in PoolMeta (see CAS-056); silent-ignore for `blob_header_len` unchanged; no operator warning.

**CAS-067** — No read-side blob cache/pin · 🔴 still-present
- Anchor: `Pool/CasPool.h:68-78` — only `dedup_cache` (write-side HEAD hint) + `manifest_decode_cache`; no read-side blob body pin/cache in CAS.
- Notes: warm reads depend on FS-cache / decode caches above CAS; cold path re-GETs each blob.

**CAS-068** — FS-cache-over-CAS caches whole-blob ranges; envelope alignment untested · 🟡 partial
- Anchor: `DiskObjectStorage.cpp:876-922` (cache stage before `needFileView`); `tests/integration/test_cas_file_cache/test.py` (startup + roundtrip + hit metrics).
- Notes: composition now works and is hit-tested; envelope-offset alignment under partial cache hit still untested.

**CAS-069** — Migration onto/off CAS is always full data rewrite · 🔴 still-present
- Anchor: absence of in-place converter in CAS tree; `DataPartStorageOnDiskBase.cpp:748` (`copyDirectoryContentIntoTransaction` streams bytes); ALTER surface narrowed when any CAS volume present (`MergeTreeData.cpp:6718-6753`).
- Notes: no bulk relink/warm-start import; transient double-bill until GC (see ad4-migration).

**CAS-070** — FREEZE/detached/gc-snap retain deleted data · 🔴 still-present
- Anchor: `ContentAddressedTransaction.cpp:1044-1074` (table DROP drops live+detached namespace, not sibling shadow); `Parts/PartPathParser.h:17,25,44-48` (FREEZE shadow classification); `ContentAddressedSettings.cpp:79` (`gc_snap_generations_to_keep = 3`).
- Notes: detached folded into live namespace (partial mitigation); FREEZE shadows survive DROP until UNFREEZE.

**CAS-071** — No crypto-shred; erasure depends on backend DELETE · 🔴 still-present (narrow GCS mitigation)
- Anchor: `Backend/CasObjectStorageBackend.cpp:55-84` (`checkPoolPreconditions` — GCS versioning fail-closed; S3/object-lock/CRR/soft-delete unenforced); no crypto-shred primitive in tree.
- Notes: physical erase still backend-DELETE semantics.

**CAS-113** — DiskEncrypted-over-CAS control-plane plaintext / read-path untested · 🔴 still-present
- Anchor: `Backend/CasObjectStorageBackend.cpp` control-plane writes via `object_storage.*` (bypass wrapping IDisk); 0 `DiskEncrypted` refs in `ContentAddressed/**`; no CAS+encrypted gtest.
- Notes: composition ungated in `MetadataStorageFactory.cpp`.

### LOW

**CAS-073** — `looksLikePartDir` false-positives · 🔴 still-present
- Anchor: `Parts/PartPathParser.cpp:136-168` (three trailing numeric underscore groups ⇒ part dir).
- Trigger: non-Atomic table/dir names ending in `_N_N_N`.

**CAS-076** — `FormatId::Roster` / `traitsFor(Roster)` throws · 📐 by-design
- Anchor: `Formats/CasFormat.h:49,126` (Roster reserved); `Formats/CasFormat.cpp:35,112-118` (`traitsFor` throws for reserved id); `changePoints` still lists Roster in the baseline switch (`:35`).
- Notes: intentionally reserved for future write-down-to-floor roster; not a live codec path.

**CAS-080** — `allocateWriterEpoch` no overflow guard; fresh mount pins GC floor · 🔴 still-present
- Anchor: `Pool/CasServerRoot.cpp:249-251` (`next_writer_epoch = next + 1`, no overflow guard); fresh `MountLease` defaults `min_active=0` until first renew (`Formats/CasServerRootFormats.h:56`; renew stamps via `CasServerRoot.cpp:749-769`).
- Notes: wrap unreachable in practice (2⁶⁴); transient floor=0 until first heartbeat remains.

**CAS-094** — No proactive scrubbing of cold blobs · 🔴 still-present
- Anchor: absence — no scrub/walker in `Gc/` or `Tools/` that re-hashes cold blob payloads; read path does not re-verify payload vs content hash (pairs CAS-005).
- Notes: bit-rot waits for query / CHECK TABLE.

**CAS-112** — `chmod` / `generateObjectKeyForPath` NOT_IMPLEMENTED · 🔴 still-present
- Anchor: `ContentAddressedTransaction.cpp:531-533,1188-1191` (`notYet("generateObjectKeyForPath"/"chmod")`).
- Notes: latent; no MergeTree caller today.

## Findings fixed / no longer reproducible

**CAS-025** — `PartManifest.payload_digest` written but never re-verified · ✅ fixed
- Anchor: `Formats/CasPartManifestFormat.cpp:293-302` — decode recomputes digest and throws `CORRUPTED_DATA` on mismatch.

**CAS-036** — `blob_header_len` floor below mandatory provenance-TLV need · ✅ fixed
- Anchor: `Formats/CasPoolMetaFormat.cpp:36-46` — `kMinBlobHeaderLen = 240` (≥225-byte v3 mandatory content); create-time `BAD_ARGUMENTS`, decode-time `CORRUPTED_DATA`.

**CAS-054** — Relink cookie value not validated (only presence) · ✅ fixed
- Anchor: `ContentAddressedExchange.cpp:13,152-153` — `kTokenVersion = "car1"`; exact version-tag + field-count gate; mismatch → `nullopt` (byte-fetch fallback).

## By-design / N/A / info

**CAS-201** — B151 early publish rollback-window · 🟡 partial/mitigated
- Anchor (early-publish removed): `ContentAddressedTransaction.cpp:1349-1353` ("No early-published ref to compensate… publish happens only in … commit"); residual serial multi-part commit window at `:458-508` (= CAS-021).
- Verdict: early-publish half closed; residual is documented commit non-atomicity.

**CAS-202** — CAS fully data-type agnostic · ✅ verified
- Anchor: `Formats/CasPartManifestFormat.h:50-65` (opaque path/bytes); `Formats/CasLayout.cpp:34-37` (blob key = hash only); zero `#include DataTypes/**` in CAS tree.

**CAS-207** — Content-addressed keys make FS cache ideal · ⚪ info
- Anchor: `DiskObjectStorage.cpp:876-922` (cache below FileView; keys are physical blob keys); confirmed by `tests/integration/test_cas_file_cache/`.

**CAS-209** — Relink data-safe under version skew · ⚪ info / ✅ verified
- Anchor: `Formats/CasFormat.cpp:64-70` (`checkCompatibility` fail-closed); `ContentAddressedExchange.cpp:152-153` (cookie gate); receiver republishes local manifest (`ContentAddressedExchange.h:140-146`).

**CAS-210** — Onto-CAS migration dedups on landing · ⚪ info
- Anchor: `Pool/CasPartWriteTxn.cpp:178-212` (HEAD-first / dedup-cache adopt); content-addressed landing collapses duplicates (cost win; no body re-hash — see ad4 NEW-MIG-2).

**CAS-212** — Retired FormatId values / freeze enum at GA · ⚪ info (comment-only)
- Anchor: `Formats/CasFormat.h:38-67` (retired 2,3,4,6,7,10,15 kept unused via comments); no `static_assert`/negative test.

**CAS-213** — `manifestCleanupShard` hashes qualified ManifestId · ⚪ info / ✅ verified
- Anchor: `Gc/CasGcShardPlan.cpp:17-25` — `std::hash<ManifestId>{}(id) % gc_shards`; comment requires namespace-qualified id so same `ManifestRef` in two namespaces never merges.

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-018 | High | 🔴 still-present | `ContentAddressedTransaction.cpp:1034-1036`; no SLA in `ContentAddressedSettings.cpp` |
| CAS-019 | High | 🔴 still-present | `Gc/CasBlobInDegree.cpp:364-448`; `Pool/CasRefLedger.cpp:2801,2890` |
| CAS-046 | High | 🔴 still-present | absence in `Backend/CasObjectStorageBackend.cpp`; `DiskEncrypted` random IV |
| CAS-025 | Med | ✅ fixed | `Formats/CasPartManifestFormat.cpp:293-302` |
| CAS-031 | Med | 📐 by-design | `Pool/CasPartWriteTxn.cpp:794`; `ContentAddressedExchange.h:220-224` |
| CAS-036 | Med | ✅ fixed | `Formats/CasPoolMetaFormat.cpp:36-46` (`kMinBlobHeaderLen=240`) |
| CAS-042 | Med | 🔴 still-present | `DataPartStorageOnDiskBase.cpp:417-427`; no BACKUP/RESTORE CAS IT |
| CAS-047 | Med | 🔴 still-present | `ContentAddressedMetadataStorage.cpp:1793` vs `:1915-1917` |
| CAS-054 | Med | ✅ fixed | `ContentAddressedExchange.cpp:13,152-153` (`kTokenVersion=car1`) |
| CAS-056 | Med | 🟡 partial/changed-shape | `gc_shards` create-once `Gc/CasGc.cpp:3022-3025`; root shards gone |
| CAS-057 | Med | 🟡 mitigated/changed-shape | `Gc/CasGc.cpp:2393-2411` (single LIST, no ns×shard fan-out) |
| CAS-058 | Med | 🔴 still-present | `Pool/CasPool.cpp:1326-1328`; `Gc/CasGc.cpp:2397-2398` |
| CAS-059 | Med | 🟡 partial | `05004_content_addressed_transactions.sh`; multi-part merge B53 gap |
| CAS-060 | Med | 🔴 still-present | `Pool/CasServerRoot.cpp:1239-1274`; orphan/precommit sweeps |
| CAS-061 | Med | 🔴 still-present | absence of text/GIN/vector tests under `test_cas_*` / `test_content_addressed_*` |
| CAS-062 | Med | 🟡 partial / 🛠 will-fix | `StorageSystemContentAddressedMounts.cpp:40-59`; `DROP_POOL_MEMBER` |
| CAS-063 | Med | 🔴 still-present | absence of PoolMeta backup/restore under `Pool/`/`Tools/` |
| CAS-064 | Med | 🔴 still-present | `Pool/CasServerRoot.h:188-223`; `CasServerRoot.cpp:428-432` |
| CAS-065 | Med | 🔴 still-present | `Backend/CasObjectStorageBackend.cpp:94-108` |
| CAS-066 | Med | 🔴 still-present | `Pool/CasPoolMeta.cpp:118-124` |
| CAS-067 | Med | 🔴 still-present | `Pool/CasPool.h:68-78` (dedup+manifest caches only; no read blob pin) |
| CAS-068 | Med | 🟡 partial | `DiskObjectStorage.cpp:876-922`; `test_cas_file_cache` (no partial-hit envelope test) |
| CAS-069 | Med | 🔴 still-present | no in-place converter; `DataPartStorageOnDiskBase.cpp:748` |
| CAS-070 | Med | 🔴 still-present | `ContentAddressedTransaction.cpp:1044-1074`; `gc_snap_generations_to_keep` |
| CAS-071 | Med | 🔴 still-present | `Backend/CasObjectStorageBackend.cpp:55-84` (GCS-only versioning gate) |
| CAS-113 | Med | 🔴 still-present | control-plane via `CasObjectStorageBackend`; 0 DiskEncrypted refs in CAS tree |
| CAS-073 | Low | 🔴 still-present | `Parts/PartPathParser.cpp:136-168` |
| CAS-076 | Low | 📐 by-design | `Formats/CasFormat.h:49,126`; `CasFormat.cpp:112-118` |
| CAS-080 | Low | 🔴 still-present | `Pool/CasServerRoot.cpp:249-251`; MountLease `min_active` default 0 |
| CAS-094 | Low | 🔴 still-present | absence of cold-blob scrub/re-hash in `Gc/`/`Tools/` |
| CAS-112 | Low | 🔴 still-present | `ContentAddressedTransaction.cpp:531-533,1188-1191` |
| CAS-009 | High | 🔴 still-present | `Formats/CasFormat.cpp:57-62`; `CasFormat.h:28` (`G_BUILD=3`) |
| CAS-201 | Info | 🟡 partial/mitigated | early-publish gone `:1349-1353`; residual commit window `:458-508` |
| CAS-202 | Info | ✅ verified | `CasPartManifestFormat.h:50-65`; `CasLayout.cpp:34-37` |
| CAS-207 | Info | ⚪ info | `DiskObjectStorage.cpp:876-922`; `test_cas_file_cache` |
| CAS-209 | Info | ⚪ info / ✅ verified | `CasFormat.cpp:64-70`; `ContentAddressedExchange.cpp:152-153` |
| CAS-210 | Info | ⚪ info | `Pool/CasPartWriteTxn.cpp:178-212` |
| CAS-212 | Info | ⚪ info | `Formats/CasFormat.h:38-67` (comment-only retirement) |
| CAS-213 | Info | ⚪ info / ✅ verified | `Gc/CasGcShardPlan.cpp:17-25` |

### Counts (39 ids)

| Verdict | Count |
|---|---|
| 🔴 still-present | 22 |
| ✅ fixed / verified | 5 |
| 🟡 partial / mitigated / will-fix | 7 |
| 📐 by-design | 2 |
| ⚪ info | 3 |
| ❔ not-reviewed | **0** |
