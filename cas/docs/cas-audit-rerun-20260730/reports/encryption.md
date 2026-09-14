# encryption — re-run 2026-07-30

Re-verification of the original `cas-encryption-audit.md` findings (E-1…E-4 → CAS-046, CAS-113, CAS-204) against current PR HEAD (`/Volumes/workspace/ClickHouse`, branch `cas-audit-20260730`, tracking `altinity/cas-gc-rebuild`).

## Scope in current code

- Files/dirs walked:
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/**` (full tree, 114 files)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.{h,cpp}` (backend PUT/GET/HEAD path — SSE surface)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.{h,cpp}` and `ContentAddressedTransaction.{h,cpp}` (read/write entry points, `getBlobViewPlan`, `readBlobPayload`)
  - `src/Disks/DiskObjectStorage/MetadataStorages/MetadataStorageFactory.cpp` (composition-point check for a CAS+`DiskEncrypted` guard)
  - `src/Disks/DiskEncrypted.{h,cpp}`, `src/Disks/DiskEncryptedTransaction.{h,cpp}` (composition-point check on the encrypted side)
  - `src/Disks/tests/**` (CAS-encryption test coverage check — `gtest_disk_encrypted.cpp`, `gtest_content_addressed_settings.cpp`, `gtest_cas_*`, `cas_test_helpers.h`)

## Search summary (all null)

- `rg -n 'DiskEncrypted|FileEncryption|InitVector|EncryptedTransaction' src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/` → **0 matches**.
- `rg -n 'SSE|ServerSideEncryption|server_side_encryption' src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/` → **0 matches**.
- `rg -n 'encrypt' src/Disks/DiskEncrypted.cpp | rg 'content_addressed|ContentAddressed'` → **0 matches** (DiskEncrypted has no CAS-composition awareness).
- `rg -n 'encrypted' src/Disks/DiskObjectStorage/MetadataStorages/MetadataStorageFactory.cpp` → **0 matches** (factory does not gate on wrap-by-DiskEncrypted).
- Every `encrypt`/`Encrypt`/`SSE` hit in the CAS tree is a false-positive substring match on the phrase `SYSTEM CONTENT ADDRESSED …` (verified line-by-line across `Gc/CasGc.cpp`, `Pool/CasPool.{h,cpp}`, `Pool/CasMountRuntime.{h,cpp}`, `ContentAddressedMetadataStorage.{h,cpp}`, `Backend/CasRequestControl.h`, `Formats/CasTextFormat.cpp`, `Formats/CasFormat.h`, `ContentAddressedSettings.{h,cpp}`, `Tools/CasFsck.cpp`, `Pool/CasServerRoot.cpp`, `Pool/CasRefLedger.h`, `Gc/CasGcScheduler.{h,cpp}`). Zero real encryption / SSE / IV / AES code in CAS.
- CAS-encryption test presence: `rg -l encrypt src/Disks/tests` → `gtest_disk_encrypted.cpp` (stand-alone `DiskEncrypted` unit test, does **not** wrap a CAS metadata storage) and `gtest_disk_object_storage.cpp` (comment-only). **No test composes `DiskEncrypted` over a CAS-backed disk.**

## Findings still present

### CAS-046 (E-1) — `DiskEncrypted` random-IV ciphertext defeats content-addressed dedup 🔴
- Anchor: **absence** of any encryption-aware hashing in `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.cpp` (backend receives whatever bytes the upper layer supplies via `object_storage.readObject`/`writeObject` and content-addresses them; see backend body around `readObject` calls at `CasObjectStorageBackend.cpp:363` and `:407`).
- Anchor: `src/Disks/DiskEncrypted.cpp` still generates a fresh random IV per `writeFile` via `FileEncryption::InitVector::random()` — verified by header (`src/Disks/DiskEncryptedTransaction.h`) and gtest fixture (`src/Disks/tests/gtest_disk_encrypted.cpp:25` — `constexpr auto kHeaderSize = FileEncryption::Header::kSize`, per-file random-IV header preserved). No PR change to make ciphertext deterministic.
- Trigger: two identical plaintext files (same-part re-materialization, cross-replica writes, deterministic merge/mutation output) → different random IV → different ciphertext → different content hash → **no dedup**.
- Notes: CAS is encryption-agnostic by design; the finding is a **feature-gap / anti-pattern warning**, not a CAS-side bug. Nothing in the PR closes the gap.

### CAS-113 (E-2) — CAS control-plane metadata plaintext under `DiskEncrypted`-only 🔴
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.cpp` — the CAS `Store` writes manifests, ref shards, `gc/state`, retired sets, mount lease, owner/epoch **directly** via `object_storage.readObject/writeObject/listObjects/…` (see calls at `:363`, `:407`, and analogous PUT paths); these bytes never pass through the wrapping `DiskEncrypted.writeFile`.
- Trigger: configure a disk `type: encrypted` wrapping `type: object_storage, metadata_type: content_addressed`, no S3 SSE. Column bytes are encrypted; every CAS manifest / ref shard / GC artifact / lease / seal object is written in cleartext to S3.
- Evidence: no code path in `ContentAddressed/**` routes control-plane objects through the encrypting wrapper. Confirmed by full absence of `writeFile`-through-`IDisk` semantics for control-plane writes (backend uses `object_storage.*` directly, bypassing any wrapping IDisk).
- Notes: still-present exactly as originally reported. Fix would be either (a) documented "SSE is mandatory for CAS metadata privacy", or (b) route control-plane writes through the wrapping disk (major architectural change).

### CAS-113 (E-3) — `DiskEncrypted`-over-CAS read-path composition untested, no guard 🔴
- Anchor (no guard): `src/Disks/DiskObjectStorage/MetadataStorages/MetadataStorageFactory.cpp` (CAS registration site) — 0 references to `DiskEncrypted`; no rejection or warning when the wrapping composition is configured.
- Anchor (untested composition): `src/Disks/tests/gtest_disk_encrypted.cpp` uses a plain non-encrypted `DiskLocal` under the encrypted wrapper; `src/Disks/tests/gtest_content_addressed_*.cpp` never instantiates `DiskEncrypted`. `rg -l 'DiskEncrypted' src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed` → 0 files. No gtest, no soak config, no integration test.
- Anchor (composition risk): CAS optimized read path — `getBlobViewPlan` and `readBlobPayload` in `ContentAddressedTransaction.cpp` / `ContentAddressedMetadataStorage.cpp` / `ContentAddressedExchange.h` — returns ciphertext sub-ranges via `ReadBufferFromFileView`; header/offset math and `getEncryptedFileSize` vs CAS `getFileSize` interaction remain un-audited under the wrapping stack.
- Trigger: read a part file that was written via `DiskEncrypted` on top of a CAS disk. Any MergeTree path that bypasses `disk->readFile` and reads storage objects directly (backup/fetch/direct-object read) returns ciphertext without decrypt; ranged reads over an offset-shifted header risk misalignment.
- Notes: unchanged from original audit — the composition is still permitted, still unguarded, still untested.

### CAS-113 (E-4) — Locally-written parts don't cross-replica-dedup under encryption 🔴
- Anchor: same as E-1 — per-node random-IV in `DiskEncrypted` → different ciphertext on each replica → no cross-replica dedup for locally-produced parts. Fetch-by-relink still ships the sender's ciphertext blobs by reference (relinked parts do share), so this manifests only for locally-materialized parts (INSERT, merge, mutation).
- Notes: derivative of E-1. Would resolve if E-1 resolved.

### CAS-204 — S3 SSE is fully supported and recommended ⚪ (info, unchanged)
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.cpp` — all backend I/O goes through `object_storage.readObject/writeObject/…`, i.e. the standard `IObjectStorage` interface. SSE headers (SSE-S3, SSE-KMS, SSE-C) are configured on the underlying `S3ObjectStorage` and applied transparently per request. CAS never sees ciphertext, so content-addressing is on plaintext and dedup is preserved.
- Verdict unchanged: **fully supported and recommended**; no code change needed.

## Findings fixed / no longer reproducible

None. Zero PR-side changes in the encryption dimension since the original audit — no CAS+DiskEncrypted guard added, no CAS-side encryption-aware hashing, no CAS+DiskEncrypted test, no SSE-mandating documentation lint.

## New findings (not in original audit)

None uncovered on re-scan. The original audit was complete for this dimension; the current PR does not introduce any new encryption surface (no new key management, no CAS-side envelope, no SSE-config plumbing) that would produce additional findings.

## By-design / N/A / info

- CAS-204 — by-design and correct. Recommended production configuration.
- CAS is deliberately encryption-agnostic (design contract in `docs/superpowers/cas/01-architecture.md` / `05-formats-and-backend.md`); E-1…E-4 are all consequences of that contract composed with client-side per-file random-IV encryption.

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-046 (E-1) | High (nullifies CAS dedup) | 🔴 still-present | `src/Disks/DiskEncrypted.cpp` (per-file random IV) + no CAS-side determinism / no guard in `MetadataStorages/MetadataStorageFactory.cpp` |
| CAS-113 (E-2) | Info–Med (metadata leakage) | 🔴 still-present | `ContentAddressed/Backend/CasObjectStorageBackend.cpp` control-plane writes bypass the wrapping IDisk |
| CAS-113 (E-3) | Med (untested composition, no guard) | 🔴 still-present | 0 hits for `DiskEncrypted` in `ContentAddressed/**`; 0 CAS+encryption tests in `src/Disks/tests/`; no guard in `MetadataStorages/MetadataStorageFactory.cpp` |
| CAS-113 (E-4) | Low (no cross-replica local-write dedup) | 🔴 still-present | Consequence of E-1; same anchor |
| CAS-204 | none (info, by-design) | ⚪ info / 📐 by-design | `ContentAddressed/Backend/CasObjectStorageBackend.cpp` uses `IObjectStorage` transparently; SSE is applied by the underlying `S3ObjectStorage` |

**Counts:** 🔴 still-present: **4** (CAS-046, CAS-113×3 sub-findings E-2/E-3/E-4)  ·  ✅ fixed: **0**  ·  📐 by-design / ⚪ info: **1** (CAS-204)  ·  🆕 new findings: **0**.
