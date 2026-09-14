# cas-tier2-audit — re-run 2026-07-30

Re-verification of the Tier 2 findings (System tables, Filesystem cache, Storage-policy/TTL moves,
INSERT dedup) from `original-audit-gist.md` § `cas-tier2-audit.md` against the current PR HEAD
(`/Volumes/workspace/ClickHouse`, branch `cas-audit-20260730`, tracking `altinity/cas-gc-rebuild`).

## Scope in current code
- `src/Disks/DiskObjectStorage/DiskObjectStorage.cpp` — `prepareRead`, `reserve`.
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.cpp`
  — `getStorageObjects`, `getStorageObjectsIfExist`, `tryGetInManifestBytes`, `getRelinkOffer`.
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp`
  — `createHardLink`, `moveFile`, `moveDirectory`.
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/PartPathParser.{h,cpp}` —
  `kDeduplicationLogsDirName`, reserved table-level subdir handling.
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Tools/CasFsck.h` —
  `physical_bytes`, `referenced_logical_bytes`, `dedupRatio()`.

## Findings still present

### System tables

**SYS-1 (Med) — `bytes_on_disk` is logical; over-reports physical N× under dedup; no system view for physical/dedup.**
- Anchor: `src/Disks/.../ContentAddressed/ContentAddressedMetadataStorage.cpp:1748` (`getStorageObjects` returns
  `StoredObject(location.key, path, location.length)` where `length` is the per-file payload length, summed
  by MergeTree into `bytes_on_disk`).
- Physical/dedup counters exist only inside `CasFsck` — not exposed as a system table:
  `src/Disks/.../ContentAddressed/Tools/CasFsck.h:112-125` (`physical_bytes`, `referenced_logical_bytes`,
  `dedupRatio()`).
- Trigger: any query summing `system.parts.bytes_on_disk` on a CAS table with any dedup (merges, hardlinks,
  identical inserts) reports logical bytes ≥ physical.
- Evidence: no `System*Cas*` / `system.cas_pool` table registered in
  `src/Storages/System/*` — grep confirms only `CasFsck` internal struct carries these numbers.

**SYS-2 (Low) — in-manifest files render with empty `remote_path`.**
- Anchor: `src/Disks/.../ContentAddressed/ContentAddressedMetadataStorage.cpp:1756-1757`
  ```
  if (auto bytes = tryGetInManifestBytes(path))
      return {StoredObject("", path, bytes->size())};
  ```
- Also `getStorageObjectsIfExist` (:1827-1828): inline entries return `StoredObject("", …)`.
- `system.remote_data_paths` prints the empty `""` key for verbatim/mutable per-part files, unchanged from
  the original audit.

**SYS-3 (Info) — dedup makes `remote_data_paths` many-to-one.**
- Anchor: `src/Disks/.../ContentAddressed/ContentAddressedMetadataStorage.cpp:1789-1793`
  (`snap.pool->locate(*entry)` returns the content-hash blob key — the same key for any file whose entry
  matches).
- Behavior unchanged; accurate but non-unique. Info.

**SYS-4 (Low) — `system.disks` free/total space is object-storage placeholder.**
- Anchor: `src/Disks/DiskObjectStorage/DiskObjectStorage.cpp:544-634` (`reserve` / `getAvailableSpace`).
  CAS does not override reserve/free-space; ripgrep in
  `src/Disks/.../ContentAddressed/**` finds no `getAvailableSpace`/`freeSpace` override. Free space is
  whatever the backing object storage reports (S3 → effectively unbounded).

**SYS-5 (Low) — `system.mutations`/`part_log`/`replicated_fetches` CAS-specific fields unverified.**
- No CAS-specific code path was added to populate these tables; still purely MergeTree bookkeeping.
  `relink`-fetch byte accounting (would show `0` for relink) not exercised by tests. Status unchanged.

### Filesystem cache

**CACHE-1 (Info) — content-addressed keys make FS cache invalidation-free + cross-file dedup.**
- Anchor: `src/Disks/DiskObjectStorage/DiskObjectStorage.cpp:877-881` (cache stage added by
  `storage->prepareRead` — the underlying `CachedObjectStorage` is keyed by remote path, which for CAS is
  the content-hash blob key from `getStorageObjects`). Property still holds.

**CACHE-2 (Med) — FS cache is keyed on whole-blob ranges; `needFileView` is applied ABOVE the cache.**
- Anchor: `src/Disks/DiskObjectStorage/DiskObjectStorage.cpp:876-922`. Stage order in current code:
  ```
  pipeline.needGather();                                    // :877
  storage->prepareRead(...);                                // :881  (adds needFilesystemCache inside)
  ... needDistributedCache / needMemoryCache / async ...
  if (ca_blob_view)
      pipeline.needFileView(path, payload_offset, payload_end);  // :922 — LAST
  ```
  Confirmed: cache stores blob-coordinate ranges (envelope + payload); FileView is applied above the cache
  chain, shifting every logical read by `payload_offset`. Still present.

**CACHE-3 (Low) — cache observability by blob key, not part path.**
- Anchor: `src/Disks/.../ContentAddressed/ContentAddressedMetadataStorage.cpp:1789-1793` — blob key
  is what leaves `getStorageObjects`; `system.filesystem_cache` therefore sees keys, not part-file paths.
  Unchanged.

### Storage policy / TTL moves

**TIER-1 (Med) — cross-disk MOVE is a full byte copy; `createHardLink` requires two part-file paths on the SAME disk.**
- Anchor: `src/Disks/.../ContentAddressed/ContentAddressedTransaction.cpp:1119-1178`
  (`createHardLink`). Both `path_from` and `path_to` must resolve via `routeOf(path_*)` inside the same
  CAS metadata storage (:1123-1127); the source manifest is looked up via `partAccess()->getView(...)`
  on this disk only (:1165). No cross-disk relink hook exists.
- Consequence: cross-disk MOVE (including CAS→CAS same-pool between two CAS disks in a storage policy)
  falls back to the generic move-by-copy path in the storage-policy layer. Missed same-pool
  optimization confirmed.

**TIER-2 (Med) — TTL move off CAS double-bills storage until GC reclaims.**
- Anchor: `src/Disks/.../ContentAddressed/Gc/*` (deferred reclaim architecture — same LC-1 property
  from the original audit; ref-drop is decoupled from blob deletion). Move drops the CAS ref immediately
  but blobs persist until the GC sweep; source data therefore lives on both tiers transiently. Still
  present.

**TIER-3 (Low) — cross-disk MOVE vs concurrent GC untested (R1/X1 dangle class).**
- Anchor: `src/Disks/.../ContentAddressed/ContentAddressedMetadataStorage.cpp:1748-1796`
  (`getStorageObjects` used by the ranged GETs on the source). Fail-loud behavior is intended; no test
  exercise found. Unchanged.

**TIER-4 (Info) — `move_factor` free-space heuristics inert on CAS source.**
- Follows from SYS-4 (free space is placeholder). Info.

### INSERT block-deduplication

**DEDUP-1 (Info) — MergeTree block-dedup and CAS content-dedup compose cleanly.**
- Anchor: `src/Disks/.../ContentAddressed/Parts/PartPathParser.h:72-75` (`kDeduplicationLogsDirName =
  "deduplication_logs"`) — the log directory is a reserved table-level subdir stored as verbatim CAS
  namespace files. No conflict with content-dedup. Property unchanged.

**DEDUP-2 (Low) — non-replicated dedup-log durability rides mutable-file commit path.**
- Anchor: `src/Disks/.../ContentAddressed/ContentAddressedTransaction.cpp:1107` (removal path notes:
  "Table-level SUBDIRECTORY (deduplication_logs/): remove every verbatim file under it.") and
  `PartPathParser.cpp:194-361` (parser splits path at `deduplication_logs/`). Log entries are written as
  namespace files with last-writer-wins semantics; a crash between two window updates can lose the most
  recent block hashes. Bounded to a duplicate part (extra ref, same blobs). Unchanged.

**DEDUP-3 (Info) — replicated (ZK) dedup disk-agnostic.**
- No CAS code interacts with ZK dedup log. Unchanged.

## Findings fixed / no longer reproducible

None. Every Tier 2 finding is either an architectural property that remains true in the current code
or an observability/testing gap that would require new code (system table, cross-disk relink) to
close — none of which is present at this PR HEAD.

## New findings (not in original audit)

**NEW-tier2-1 (Low, cache/observability) — page memory cache key prefix disks-scopes CAS blob dedup.**
- Anchor: `src/Disks/DiskObjectStorage/DiskObjectStorage.cpp:893-902`.
  ```
  auto cache_path_prefix = fmt::format("{}:{}:", /*disk*/ name,
                                       magic_enum::enum_name(storage->getType()));
  ```
  The **memory page cache** key is prefixed by the disk `name`, so two CAS disks that share the same
  underlying pool and thus resolve to the **same blob key** do **not** share page-cache entries — the
  cross-file/cache dedup benefit from CACHE-1 applies only to the filesystem-cache stage (keyed on
  remote path). Minor observability/perf note; the filesystem cache dedup benefit (CACHE-1) is intact.
- Severity: Low (perf only; correctness unaffected).

**NEW-tier2-2 (Low, system-tables gap) — no CAS view of pool-level counters despite `CasFsck` numbers.**
- Anchor: `src/Disks/.../ContentAddressed/Tools/CasFsck.h:112-125` — `physical_bytes`,
  `referenced_logical_bytes`, `distinct_blobs`, `total_blob_refs`, `dedupRatio()` are all computed by
  fsck but there is no matching `StorageSystem*` entry in `src/Storages/System/`. Reinforces SYS-1 and
  makes the recommendation actionable: the numbers exist, they are simply not surfaced.
- Severity: Low (documentation/observability); would meaningfully improve operator sizing.

**NEW-tier2-3 (Low, TTL/tiering) — no move-path hook to short-circuit CAS→CAS same-pool moves.**
- Anchor: `src/Disks/.../ContentAddressed/ContentAddressedTransaction.cpp:1119-1128` (`createHardLink`
  gate requires two well-formed part-file paths in the same CAS metadata storage). Grep of
  `MetadataStorages/ContentAddressed/**` for `crossDisk|relinkAcross|cross_pool` returns no matches;
  the CAS-CAS same-pool fast path noted in the audit recommendations is still absent.
- Severity: Low (perf only; correctness is retained by the generic byte-copy path).

## By-design / N/A / info
- SYS-3, CACHE-1, TIER-4, DEDUP-1, DEDUP-3: informational properties (either accurate consequences of
  dedup or "no interaction" between subsystems). Unchanged.

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| SYS-1 | Med | 🔴 still-present | `ContentAddressedMetadataStorage.cpp:1748-1796`; `Tools/CasFsck.h:112-125` |
| SYS-2 | Low | 🔴 still-present | `ContentAddressedMetadataStorage.cpp:1756-1757, 1827-1828` |
| SYS-3 | Info | ⚪ info | `ContentAddressedMetadataStorage.cpp:1789-1793` |
| SYS-4 | Low | 🔴 still-present | `DiskObjectStorage.cpp:544-634` (no CAS override) |
| SYS-5 | Low | 🟡 needs-repro | no CAS-specific code populating these tables |
| CACHE-1 | Info | ⚪ info | `DiskObjectStorage.cpp:877-881` |
| CACHE-2 | Med | 🔴 still-present | `DiskObjectStorage.cpp:876-922` (needFileView applied last) |
| CACHE-3 | Low | 🔴 still-present | `ContentAddressedMetadataStorage.cpp:1789-1793` |
| TIER-1 | Med | 🔴 still-present | `ContentAddressedTransaction.cpp:1119-1178` (same-disk-only) |
| TIER-2 | Med | 🔴 still-present | Gc deferred-reclaim architecture (LC-1) |
| TIER-3 | Low | 🟡 needs-repro | `ContentAddressedMetadataStorage.cpp:1748-1796` |
| TIER-4 | Info | ⚪ info | follows from SYS-4 |
| DEDUP-1 | Info | ⚪ info | `PartPathParser.h:72-75` |
| DEDUP-2 | Low | 🔴 still-present | `ContentAddressedTransaction.cpp:1107`; `PartPathParser.cpp:194-361` |
| DEDUP-3 | Info | ⚪ info | no CAS code path |
| NEW-tier2-1 | — | 🔴 new | `DiskObjectStorage.cpp:893-902` (page cache key includes disk name) |
| NEW-tier2-2 | — | 🔴 new | `Tools/CasFsck.h:112-125` (no system-table exposure) |
| NEW-tier2-3 | — | 🔴 new | `ContentAddressedTransaction.cpp:1119-1128` (no cross-disk relink hook) |

## Counts
- Original Tier 2 findings reviewed: 15 (SYS-1..5, CACHE-1..3, TIER-1..4, DEDUP-1..3).
- Still-present: 8 (SYS-1, SYS-2, SYS-4, CACHE-2, CACHE-3, TIER-1, TIER-2, DEDUP-2).
- Needs-repro (unverified, no code change): 2 (SYS-5, TIER-3).
- Info / by-design (unchanged): 5 (SYS-3, CACHE-1, TIER-4, DEDUP-1, DEDUP-3).
- Fixed: 0.
- New findings: 3 (NEW-tier2-1..3).
