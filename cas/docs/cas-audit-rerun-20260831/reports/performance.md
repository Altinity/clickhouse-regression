# performance -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `Pool/CasRefLedger.cpp` (recovery epoch seals, catalog GETs on removal/reconcile), `Pool/CasRefCatalog.cpp` (`casUpdateImpl` full-catalog GET+rewrite), `Parts/PartFolderAccess.cpp` (`estimatedBytes`, `manifest_size`), `Pool/CasRefLedger.cpp:349-351` / `:383` (`Resolved.manifest_size = 0`), `ContentAddressedTransaction.cpp` (`createHardLink` ForceFresh, `CaInlineWriteBuffer`, scratch overflow, `fanOutBlobUploads`), `Pool/CasBlobUploadPool.cpp`, `ContentAddressedSettings.cpp` (cache budgets, `scratch_path`), `DataPartStorageOnDiskBase.cpp` / `clonePart` (no local-move relink), `Pool/CasManifestReader.cpp`.
- Explicitly out of scope: lock-hold times (bc7); inventing request-count arithmetic; treating the 16-thread blocking upload pool as a defect.

Question: remaining *real* scale costs after the post-08-12 protocol changes. Do not re-raise by-design backpressure.

## Findings
### performance-1 -- part-folder view-cache weight is always 256 bytes because `Resolved.manifest_size` is hardcoded 0 (Medium)
- Anchor: `CasRefLedger.cpp:349-351` and `:383` (`manifest_size = 0`); `PartFolderAccess.cpp:69` (copied into the view); `:136-140` (`estimatedBytes() = 256 + manifest_size`); settings `part_folder_cache_bytes` / `part_folder_cache_max_entry_bytes` (`ContentAddressedSettings.cpp:74-76`).
- Trigger: any production load that relies on `cas_part_folder_cache_bytes` or the 16 MiB oversized-bypass.
- Evidence: both `Resolved` producers write 0. The byte budget and oversized-bypass threshold cannot see real manifest size. The cache is an entry-count LRU with a fake weight. Same root cause as CAS-045.
- Notes: CAS-045.

### performance-2 -- recovery still writes one durable epoch-seal pair per skipped writer epoch (Medium)
- Anchor: `CasRefLedger.cpp:1097-1116` (`makeEpochSealTxn` + `sealObject` + conditional create per dead unclosed epoch); epoch is pool-wide (minted per mount), seal chain is per namespace.
- Trigger: first touch of a long-idle table after many remounts/restarts (writer epoch has advanced while the namespace was quiet).
- Evidence: each skipped epoch is closed with its own seal PUT + `_ckpt` work. There is no batch close. First read/write of that table pays O(elapsed mount count) sequential durable pairs with no upper bound other than "how many epochs were minted". Fail-closed and correct; the cost is user-visible stall. Same class as CAS-114.
- Notes: CAS-114.

### performance-3 -- mutation/FREEZE/ATTACH still pay one ForceFresh manifest HEAD per hardlinked file (Medium)
- Anchor: `ContentAddressedTransaction.cpp:1213`; default `cas_part_folder_validate=always`.
- Trigger: wide-part mutation or FREEZE PARTITION.
- Evidence: `unlinkFile` memoizes the proof; `createHardLink` does not. Network-bound, serialized on the mutate thread. Same as CAS-055 / alter-merge-mutation-1.
- Notes: CAS-055.

### performance-4 -- same-pool local MOVE/clone has no relink; dest restages from a full source GET (Medium)
- Anchor: `DataPartStorageOnDiskBase.cpp:790-813` (`clonePart` on a CA dest always `copyDirectoryContentIntoTransaction`); `ContentAddressedTransaction.cpp` write path hashes and `ensureBlobPresent`s every blob. Dedup HEAD absorbs the PUT when the hash exists (`CasPartWriteTxn.cpp:357-387`).
- Trigger: `MOVE PARTITION TO DISK|VOLUME` inside one pool, or `clonePart` onto another CA disk of the same pool.
- Evidence: there is no "copy the ManifestRef / adopt the source view" fast path for a local move. Cost is a full source read plus restage; blob PUTs are skipped on hit. Same class as CAS-120.
- Notes: CAS-120.

### performance-5 -- local scratch for blob writes has no reservation, quota, or startup cleanup (Low)
- Anchor: `ContentAddressedTransaction.cpp:929-939`, `:982-988`; `ContentAddressedSettings.cpp:56,187-194` (`cas_scratch_path`).
- Trigger: concurrent large INSERTs/merges with `staging_backend=local` (the default) on a small local volume.
- Evidence: scratch is the part's full bytes, created on demand, removed at transaction end, not reserved against a disk quota. Failure is loud ENOSPC. Already tracked as a desirable limit, not a correctness hole. Same class as CAS-046.
- Notes: CAS-046.

## By-design / info / non-actionable
- Process-wide blob upload pool (`CasBlobUploadPool.cpp`, `cas_blob_upload_pool_size`) with blocking enqueue is ordinary backpressure (CAS-047). Not a defect.
- `fanOutBlobUploads` (`ContentAddressedTransaction.cpp:1708-1778`) is one task per unique blob, drain-on-every-path, cannot self-deadlock on a size-1 pool.
- Catalog GET+full rewrite remains on namespace *lifecycle* (`CasRefCatalog.cpp:114-131`) and on terminal removal (`CasRefLedger.cpp:3290`). It is **not** on every part publish (the 08-12 "GET per ref chunk" claim does not hold on this path at HEAD).
- Manifest decode-cache still HEADs before a cache probe when `part_folder_validate=always`. That is the configured fail-closed policy.
- 16-thread / queue==threads is a setting, not a hang.

## Closed-since-2026-08-12
- `putIfAbsentStream` / `promoteStaged` / `copyObjectConditional` hot path (4C+11 PUT shape including those primitives) replaced by precommit → HEAD → adopt-or-unconditional-publish (`940b1685bf9`). Do not reuse the old request-count table.
- `admits()` O(R) re-encode on the release path was already closed before 08-12; not re-raised.

## Coverage
- Reviewed: view-cache weighting, recovery epoch seals, hardlink HEAD amplification, clone/move relink absence, scratch accounting, upload fan-out, catalog GET call sites.
- N-A: by-design upload-pool backpressure.
- Deferred: measured commit RTT and GC fold memory (owned by ad5/gc).
