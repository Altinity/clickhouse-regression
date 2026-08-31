# bc2-writebuffer-spill -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `ContentAddressedTransaction.{h,cpp}` (`CaContentWriteBuffer`, `CaInlineWriteBuffer`, `writeFile`, `cleanupPendingTempFiles`, `fanOutBlobUploads`), `Primitives/CasBlobHashingWriteBuffer.cpp`, `Pool/CasPartWriteTxn.cpp` (`ensureBlobPresent`, `stageManifest` caps), `ContentAddressedSettings.cpp` (`scratch_path`), `Pool/CasBlobUploadPool.cpp`.
- Explicitly out of scope: S3 staging sweeper prefix scoping; hash-algorithm choice (ad1); DataPartsLock hold during publish (bc7).

## Findings
### bc2-1 -- Local scratch is still unreserved, unaccounted, and held until transaction end (Medium)
- Anchor: `ContentAddressedTransaction.cpp:929-939` (local `CaContentWriteBuffer`), `:1835,1840` (create scratch file), `:167-210` (`cleanupPendingTempFiles`), `ContentAddressedSettings.cpp:56` (`scratch_path` only) at ceee42c
- Trigger: default `staging_backend=local`. Any INSERT/merge whose part bytes exceed free space on the filesystem that holds `<data path>/disks/<name>/cas_scratch/`.
- Evidence: no `IDisk::reserve`, no `TemporaryDataOnDisk`, no `statvfs`, no scratch-byte quota setting. Scratch is created with `WriteBufferFromFile` and unlinked only in `cleanupPendingTempFiles` after *all* parts publish, or in the buffer dtor on cancel. `DiskObjectStorage` still reports unlimited space, so MergeTree `reserve()` on a CAS disk cannot back-pressure. Failure is loud (`ENOSPC`). Peak local use is the full part size per in-flight transaction, times concurrency. Crash mid-transaction leaves the files until a later cleanup (no startup sweep of `cas_scratch/`).
- Notes: same root as CAS-046. Operability, not silent corruption.

### bc2-2 -- Upload never re-hashes the scratch file; `finalizeImpl` does not `sync()` (Medium)
- Anchor: `ContentAddressedTransaction.cpp:1905-1932` (`CaContentWriteBuffer::finalizeImpl`), `:1955-1959` (`sync`, not called from finalize); `Pool/CasPartWriteTxn.cpp:345-351,411-412` (publish compares `source.size` only) at ceee42c
- Trigger: a length-preserving divergence of the local scratch between the in-memory hash and the commit-time upload — page-cache/disk bit rot, or another writer hitting the same random-named temp path (no `O_EXCL` in the local ctor).
- Evidence: the digest is taken from the streaming hasher (`getHashHex` then `hashing->finalize()`) *before* `sink->finalize()`. `finalizeImpl` never calls `sink->sync()`. At commit the file is re-opened and streamed; `ensureBlobPresent` checks `logical_size != source.size` and `declared_size != source.size` (`fanOutBlobUploads` at `:1724-1728`) and nothing else. A same-length rewrite of the scratch body is published under the original content-hash key. That is the remaining CAS-009 window (presence-only admit + no re-hash of a re-upload).
- Notes: same residual as CAS-009. Silent integrity loss, but the trigger is local-scratch corruption of exact length, not a remote race.

### bc2-3 -- Aggregate inline cap is 16 MiB and has no spill/reclassification path (Medium)
- Anchor: `Pool/CasPartWriteTxn.cpp:55,533-535` (`kMaxManifestInlineBytesTotal`); `ContentAddressedTransaction.cpp:100` (`INLINE_CAP = 1 MiB` per file), `:954-998` (per-file spill only) at ceee42c
- Trigger: a part whose *sum* of inline-candidate files exceeds 16 MiB while each file is `<= 1 MiB` (wide part with many skip-index / `primary.cidx` / metadata files — see bc5-1). Per-file overflow already spills to a blob; the aggregate check does not.
- Evidence: `stageManifest` sums `inline_bytes` and throws `LIMIT_EXCEEDED` with no rewrite-as-blob path. The cap is a compile-time constant, not a setting. The failure is after blob uploads for that part have already been issued (`publishStaging` uploads then stages the manifest), so the attempt leaves GC-reclaimable debris. Every retry of the same part shape fails the same way.
- Notes: same root as CAS-044. Loud, reproducible, no silent corruption.

## By-design / info / non-actionable
- S3 staging objects of an aborted transaction are left in place on purpose (`cleanupPendingTempFiles` `:188-208`) for `sweepOwnMountStaging` to reclaim. Not a finalize/sync defect.
- `CaInlineWriteBuffer::sync` only flushes the in-memory buffer (`:1992-1995`). There is no durable sink until the 1 MiB spill writes a local file (which also does `finalize` without `sync` at `:986-988`).
- Blob-upload fan-out now rejects `declared_size != source.size` before scheduling (`:1724-1728`). That closes a wiring bug; it is not a content-hash check.

## Closed-since-2026-08-12
- Local-path fence skip: S3 staging still re-checks the fence immediately before `sink->finalize()` (`:1916-1923`); local staging still has no such callback. Local scratch has no durable backend effect until commit, so this is the accepted CAS-126 posture, not a new hole.
- Buffer-size clamp to 256 MiB is now at the allocation site (`:1700-1705`). The previous unbounded `buf_size` abort is closed.

## Coverage
- Reviewed: placement → inline vs blob buffers; local and S3 spill; finalize/sync/cancel; scratch lifecycle; upload size-only checks; 1 MiB / 16 MiB caps.
- N-A: protobuf (gone).
- Deferred: startup scratch sweep (sibling day-2 / resource audits).
