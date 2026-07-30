# idisk-contract — re-run 2026-07-30

Re-verification of the original `cas-idisk-contract-audit.md` (adaptations
C-U1 … C-U7) against current PR HEAD
(`altinity/cas-gc-rebuild`, mirrored as branch `cas-audit-20260730` at
`/Volumes/workspace/ClickHouse`). Original per-audit ids map to consolidated
ids in `audit-summary.md` as:

| Original | Consolidated |
|---|---|
| C-U1 (moveDirectory non-atomic) | CAS-022 |
| C-U2 (mtime derived / epoch(0)) | CAS-048 |
| C-U3 (moveFile verbatim non-atomic) | (chains CAS-002 / J1 fence) — no dedicated consolidated id |
| C-U4 (unlink of committed content file = no-op) | CAS-111 |
| C-U5 (multi-part commit partial) | CAS-021 |
| C-U6 (`chmod` throws) | CAS-112 |
| C-U7 (`generateObjectKeyForPath` throws) | CAS-112 |

## Scope in current code

Files walked:

- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.{h,cpp}`
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.{h,cpp}`
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/PartFolderAccess.{h,cpp}`
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPartManifestFormat.{h,cpp}` (for `findEntry`/`entryRange` — the lookup implementation backing `existsFile`/`getFileSize`/`listDirectory`)

Cross-referenced (contract side): `src/Disks/IDisk.h`, `src/Disks/ObjectStorages/IMetadataStorage.h`
(no textual quoting required — the audit reasons over CAS's implementation
against the contract semantics already established in the original audit).

## Conformance matrix (current code)

| Surface method | CAS behavior in current PR | Change vs original audit | Anchor |
|---|---|---|---|
| `existsFile`/`existsDirectory` | Same shape as original (Probe-gated); classifies via `classifyDirectory`. | No change. | `ContentAddressedMetadataStorage.cpp:1317`, `:1448` |
| `existsFileOrDirectory` | Uses cached `PartFolderView`. | No change. | `ContentAddressedMetadataStorage.cpp:1517` |
| `getFileSize` | ContentRead-gated; verbatim/manifest/inline branches; falls through to view entry `size()`. | No change. | `ContentAddressedMetadataStorage.cpp:1536` |
| `listDirectory`/`iterateDirectory` | ContentRead/Probe-gated; `addFirstComponent`-collapsed via new `DirShape`-based dispatch. | Refactored (shape enum) but semantic equivalent. | `ContentAddressedMetadataStorage.cpp:1597`, `:1714` |
| `getStorageObjects` | ContentRead-gated; sized empty-key placeholder for in-manifest bytes; `poolAccess()` snapshot for locate. | Tightened (single mount-snapshot). | `ContentAddressedMetadataStorage.cpp:1748` |
| `getLastModified` | Returns `Poco::Timestamp::fromEpochTime(published_at_ms / 1000)`; **`Poco::Timestamp(0)` when `published_at_ms == 0`** for a resolved ref AND for table-level verbatim files. Throws `FILE_DOESNT_EXIST` for unknown paths. | Same semantics as original (C-U2 still present). | `ContentAddressedMetadataStorage.cpp:1565` |
| `setLastModified` | **Accept-and-ignore** (with a `Write` gate). | Still a silent no-op; gate added (rev.7 §1). | `ContentAddressedTransaction.cpp:1180` |
| `createHardLink` | Copies staged / adopts committed entry (`adoptEvidence`) — hardlink-as-copy. | Unchanged (dep tracking added). | `ContentAddressedTransaction.cpp:1119` |
| `moveFile` (part-file) | Re-key staged entry; delegates to `moveDirectory` for part-dir shapes. | Unchanged. | `ContentAddressedTransaction.cpp:1378` |
| `moveFile` (verbatim/mount) | **get → put → remove** (no atomic rename). Idempotent re-drive on absent-source-present-dest. | Unchanged (C-U3 still present). | `ContentAddressedTransaction.cpp:1384-1435` |
| `replaceFile` | Drops staged dst, delegates to `moveFile`. | Unchanged. | `ContentAddressedTransaction.cpp:1491` |
| `moveDirectory` (RENAME TABLE) | **Non-atomic**: republish-all-refs, put-all-namespace-files, then `dropNamespace`. Explicit "table SPLIT across namespaces" log on partial failure; idempotent re-drive. | Unchanged (C-U1 still present). | `ContentAddressedTransaction.cpp:1200-1249` |
| `moveDirectory` (part-dir) | Re-keys staged src into dst, then `republishRef` on committed source. | Unchanged. | `ContentAddressedTransaction.cpp:1280-1372` |
| `unlinkFile` (part file, staged) | Drops staged entry. | Unchanged. | `ContentAddressedTransaction.cpp:1546` |
| `unlinkFile` (part file, **committed content file, not staged in this txn**) | **Now stages a `content_removed` mark that resolves at publish to a repoint-remove.** Uses a per-txn ForceFresh memo (`force_fresh_validated_refs`) so the fast-removal file storm before `removeDirectory` costs one HEAD, and the marks are cleared by `removeDirectory` (whole-part drop supersedes). | **Fixed** — was fail-open no-op (C-U4 / CAS-111). Now performs a durable per-file remove when not immediately followed by a part drop. | `ContentAddressedTransaction.cpp:1509-1568` |
| `unlinkFile` (verbatim table file) | Immediate `removeNamespaceFile`. | Unchanged. | `ContentAddressedTransaction.cpp:1574` |
| `unlinkFile` (loose mountpoint) | Immediate `removeMountpointObject`. | Unchanged. | `ContentAddressedTransaction.cpp:1590` |
| `createDirectory` / `createDirectoryRecursive` | No-op (gated Write). | Unchanged (Write gate added). | `ContentAddressedTransaction.cpp:978`, `:986` |
| `removeDirectory` (part) | The real removal: `dropRefIfPresent` + clears any staged `content_removed`. | Refined ordering (clears staged marks). | `ContentAddressedTransaction.cpp:991-1029` |
| `removeRecursive` | Table-dir → `dropNamespace`; part-dir → `dropRefIfPresent`; detached/moving containers, shadow, subdirs handled explicitly. Remove gate. | Unchanged shape. | `ContentAddressedTransaction.cpp:1032-1116` |
| `truncateFile` | Throws `NOT_IMPLEMENTED`. | Unchanged. | `ContentAddressedTransaction.cpp:1603` |
| `commit` | Per-part publish loop with best-effort **precise rollback** via `part_outcomes`/`dropRefIfMatches` (only `created` refs; matches exact `manifest_ref`). Still no multi-ref atomic publish. | Rollback tightened but still non-atomic on crash (C-U5 still present). | `ContentAddressedTransaction.cpp:435-520` |
| `chmod` | `notYet("chmod")` — throws `NOT_IMPLEMENTED`. But `supportsChmod() = false` at the storage. | C-U6 still present; supportsChmod flag now false. | `ContentAddressedTransaction.cpp:1188`, `ContentAddressedMetadataStorage.h:228` |
| `generateObjectKeyForPath` | `notYet("generateObjectKeyForPath")` — throws. | C-U7 still present. | `ContentAddressedTransaction.cpp:531` |
| `setReadOnly` | Accept-and-ignore (Write gate). | Unchanged. | `ContentAddressedTransaction.cpp:1193` |
| `createMetadataFile` | `notYet("createMetadataFile")` — throws. | Unchanged (was `getSubmittedForRemovalBlobs` slot in original; this row is a new observation, no MergeTree path calls it on CAS). | `ContentAddressedTransaction.cpp:697` |
| `getSubmittedForRemovalBlobs` | Returns empty (GC owns reclamation). | Unchanged by-design divergence. | `ContentAddressedTransaction.cpp:536` |
| `getHardlinkCount` | Returns 0 (declared in header). | Unchanged. | `ContentAddressedMetadataStorage.h:260` |
| `clearOldTemporaryDirectories` | **Not overridden** at the CAS metadata storage. Base `IMetadataStorage` default is a no-op; CAS relies on `GC/dropRef` for reclamation of tmp part refs. | Unchanged — matches the original audit's note that this is a benign divergence for CAS. | (no CAS override) |

## Findings still present

### CAS-021 (C-U5) — Multi-part `commit()` non-atomic; partial commit on crash
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:435-520` — `ContentAddressedTransaction::commit`.
- Trigger: transaction stages ≥ 2 parts, first N publish, crash between publishes → durable refs exist for the N committed parts while the caller believes commit failed.
- Evidence quote: `"there is no multi-ref atomic publish, so a publish that throws after / earlier parts already published would leave a PARTIAL commit"` (in-source comment `:459-462`).
- Notes: Rollback is precise (`dropRefIfMatches` keyed on exact `manifest_ref`, `created=true` only) and correctly avoids clobbering a concurrent writer's repoint, but the **rollback is best-effort and not crash-durable**. Same semantics as original audit.

### CAS-022 (C-U1) — `moveDirectory` (RENAME TABLE) non-atomic; split-table on crash
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:1200-1249`.
- Trigger: crash mid-loop of `republishRef` / `putNamespaceFile` / `dropNamespace`.
- Evidence quote: `"leaves the table SPLIT across the two namespaces, but re-driving the SAME rename completes it. There is no in-call compensation"` (in-source comment `:1220-1224`).
- Notes: idempotent re-drivable but no durable move-journal. Same as original.

### C-U3 (chains CAS-002) — verbatim/mount `moveFile` is `get → put → remove`
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:1384-1435`.
- Trigger: any table-level verbatim file rename (mutation entry `tmp_mutation_N.txt → mutation_N.txt`) or loose mountpoint rename.
- Evidence quote: `"a verbatim rename is emulated as get(src) -> put(dst) -> remove(src) because object storage has no atomic rename. SINGLE-WRITER CONTRACT: only the owning server renames its own table-level verbatim files"` (`:1393-1396`).
- Notes: safe under the single-writer fence; **remains coupled to CAS-002 (fencing fix)** — the source line explicitly leans on the mount-lease single-writer contract. Unchanged.

### CAS-048 (C-U2) — `getLastModified` returns epoch(0) for unstamped / verbatim
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.cpp:1579-1594`.
- Trigger: `getLastModified` on (a) any table-level verbatim file, (b) any part published without `published_at_ms` (older writer, restored backup) → both return `Poco::Timestamp(0)`.
- Evidence quote: `"a part published without a stamp (published_at_ms == 0) reports the epoch"` (`:1571-1573`), and `"Table-level / generic verbatim files: no per-object mtime is kept — epoch."` (`:1591`).
- Notes: original severity Low; the mtime→TTL "is this temp dir old enough to reap?" hazard persists. Unchanged.

### CAS-112 (C-U6) — `chmod` throws `NOT_IMPLEMENTED`
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:1188-1191` (`notYet("chmod")`).
- Notes: `ContentAddressedMetadataStorage::supportsChmod() = false` (`ContentAddressedMetadataStorage.h:228`) now signals the capability up-front, so a well-behaved caller skips the transaction path. The **latent throw is still there** for any caller that ignores the capability probe.

### CAS-112 (C-U7) — `generateObjectKeyForPath` throws `NOT_IMPLEMENTED`
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:531-534` (`notYet(...)`).
- Notes: unchanged; no `areBlobPathsRandom` / equivalent capability probe protects it. `ContentAddressedMetadataStorage::areBlobPathsRandom() = false` (`ContentAddressedMetadataStorage.h:259`) is orthogonal — it does not gate this call. Callers on CA don't need it today.

## Findings fixed / no longer reproducible

### CAS-111 (C-U4) — unlink of committed single content file is no longer a no-op — ✅ **fixed**
- Fix anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:1509-1568`.
- Old behavior (per original audit §C-U4): committed-file unlink was a "deliberate NO-OP (fail-open)". Original text: `"per-file unlinks must be no-ops, and removeDirectory frees the part"`.
- New behavior: when the target file is a **committed content file NOT staged in this transaction**, unlink stages a `content_removed` mark that resolves at `publishStaging` to a **repoint-remove of the manifest minus the removed paths**. A per-txn memo `force_fresh_validated_refs` collapses the per-file ForceFresh proofs of the MergeTree fast-removal burst into ONE HEAD per (txn, ref), and `removeDirectory` clears staged `content_removed` before publish so the storm-then-drop shape still pays exactly one ref-drop and zero repoints.
- Evidence quote (source): `"A lone surgical unlink NOT followed by a ref-drop in the same transaction (ATTACH's removeVersionMetadata, a future backfill/repair delete) resolves to one repoint-remove — this closes the file's former fail-open"` (`:1527-1531`).
- This is the correctness bug the original audit called out as C-U4 / CAS-111; it is now closed.

## New findings (not in original audit)

### NEW-idisk-contract-1 — `Poco::Timestamp::fromEpochTime` truncates `published_at_ms` to seconds (Low)
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.cpp:1581-1582`.
- Trigger: `Poco::Timestamp::fromEpochTime(published_at_ms / 1000)`. `Poco::Timestamp` has microsecond precision, but the CAS code converts to `time_t` seconds and drops the sub-second component of `published_at_ms`. Two parts published in the same second report an identical mtime.
- Severity: Low; matters only for callers that break ties on mtime granularity (part sorting/dedup by mtime is not one of those). Amplifies CAS-048.

### NEW-idisk-contract-2 — `createDirectory` / `createDirectoryRecursive` return success without recording the path (Info/Low)
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:978-989`.
- Trigger: any caller that does `createDirectory(X)` then `existsDirectory(X)` on the same transaction/storage — the second call returns `false` (no verbatim file / ref under `X` exists yet).
- Severity: Info; this matches the plain-rewritable transaction and is intentional ("object storage has no real directories"). Called out because it is a **contract divergence from POSIX** that is not documented in the original audit's matrix — a MergeTree code path that assumes `mkdir → stat` visibility would silently misbehave.

### NEW-idisk-contract-3 — `truncateFile` throws (latent) (Info)
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:1603-1608`.
- Trigger: any caller that calls `IDiskTransaction::truncateFile` on CAS.
- Severity: Info/latent — MergeTree does not truncate parts; the `NOT_IMPLEMENTED` throw is a fail-loud guard, semantically same class as C-U6/C-U7 but not enumerated in the original audit's matrix.

### NEW-idisk-contract-4 — `createMetadataFile` throws (latent) (Info)
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:697-700` (`notYet("createMetadataFile")`).
- Trigger: any caller that reaches the legacy `IMetadataTransaction::createMetadataFile` on CAS.
- Severity: Info/latent — CAS writes go through `writeFile`/`stageBlobPartFile`; the direct-key-metadata API is unreachable today. Same latency-of-latent as C-U6/C-U7.

## By-design / N/A / info

- `createHardLink → copy-with-adopted-evidence` — verified still the cleanest CAS↔MergeTree impedance match (parts immutable + content addressing ⇒ hardlink-as-copy is semantically identical and dedup-free).
- `getSubmittedForRemovalBlobs → empty` — verified still by-design (disk layer must NOT free CA blobs; GC owns reclamation).
- `supportsAtomicFileWrites() = true`, `transactionIsStagingOverlay() = true`, `areBlobPathsRandom() = false`, `getHardlinkCount() = 0` — capability flags at `ContentAddressedMetadataStorage.h:256-260` accurately describe the adaptations to callers that consult them.
- `supportsChmod() = false` (`ContentAddressedMetadataStorage.h:228`) — new since the original audit; correctly signals C-U6.
- `CAS-116` (linear `lookupPath` scans → O(entries²)) — **verified fixed** in this audit's incidental scope: `findEntry`/`entryRange` now use `std::lower_bound` on the `path`-sorted `entries` vector (`Formats/CasPartManifestFormat.cpp:329-351`). The `PartFolderView` layer (`Parts/PartFolderAccess.cpp:85-134`) delegates all `hasFile`/`fileSize`/`listChildren`/`hasDirectory` calls to these O(log n) primitives. Recorded here for cross-audit reconciliation with `coverage-map` / `performance`; kept in this report because it directly affects `IDisk` per-file lookup contract cost.

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-021 (C-U5) | Low–Med | 🔴 still-present | `ContentAddressedTransaction.cpp:435-520` |
| CAS-022 (C-U1) | Med | 🔴 still-present | `ContentAddressedTransaction.cpp:1200-1249` |
| C-U3 (chains CAS-002) | Low | 🔴 still-present | `ContentAddressedTransaction.cpp:1384-1435` |
| CAS-048 (C-U2) | Low (rated Med under CAS-048) | 🔴 still-present | `ContentAddressedMetadataStorage.cpp:1565-1595` |
| CAS-111 (C-U4) | Low–Med | ✅ fixed | `ContentAddressedTransaction.cpp:1509-1568` |
| CAS-112 (C-U6, `chmod`) | Low (latent) | 🔴 still-present (capability probe added) | `ContentAddressedTransaction.cpp:1188`; `ContentAddressedMetadataStorage.h:228` |
| CAS-112 (C-U7, `generateObjectKeyForPath`) | Low (latent) | 🔴 still-present | `ContentAddressedTransaction.cpp:531-534` |
| NEW-idisk-contract-1 (`fromEpochTime` truncates ms → s) | — | ⚪ info / Low | `ContentAddressedMetadataStorage.cpp:1581-1582` |
| NEW-idisk-contract-2 (`createDirectory` no-op divergence) | — | ⚪ info | `ContentAddressedTransaction.cpp:978-989` |
| NEW-idisk-contract-3 (`truncateFile` throws) | — | ⚪ info (latent) | `ContentAddressedTransaction.cpp:1603-1608` |
| NEW-idisk-contract-4 (`createMetadataFile` throws) | — | ⚪ info (latent) | `ContentAddressedTransaction.cpp:697-700` |
| CAS-116 (linear `lookupPath`) — cross-audit | Low (Perf) | ✅ fixed | `Formats/CasPartManifestFormat.cpp:329-351`; `Parts/PartFolderAccess.cpp:85-134` |
