# write-protocol -- fresh audit 2026-08-31

## Scope
- Durable publish path at `ceee42c51a06cb05e2c9a2d811ef7e1726825552` (worktree `/Volumes/workspace/altinity-clickhouse/cas-pr-2159-ceee42c`).
- Files/dirs examined (read in full or in the relevant regions):
  `Pool/CasPartWriteTxn.{h,cpp}`, `Backend/CasObjectStorageBackend.{h,cpp}`,
  `Backend/CasBackend.h`, `Backend/CasRequestControl.{h,cpp}`,
  `ContentAddressedTransaction.{h,cpp}`, `ContentAddressedMetadataStorage.{h,cpp}`
  (relink prepare/promote, admission), `ContentAddressedExchange.h`,
  `Parts/PartFolderAccess.{h,cpp}` (`promoteBuild`/`repointRef`/`dropRefIfMatches`/`prepareEntries`),
  `Pool/CasMountRuntime.{h,cpp}` (`checkFenceOrThrow`/`refAppendFenceOk`/`fenceGeneration`),
  `Pool/CasPool.{h,cpp}` (fence/append wiring), `Pool/CasRefLedger.cpp` (append/wedge, sampled),
  `Pool/CasRefProtocol.cpp` (owner-transition shapes, sampled),
  `Formats/CasPartManifestFormat.cpp` (caps/canonicalisation, sampled),
  `Storages/MergeTree/DataPartsExchange.cpp` (relink caller, sampled).
- Explicitly out of scope: GC in-degree/reclaim, checkpoint compaction, the read path,
  namespace lifecycle internals, fsck/inspect/decommission, wire formats beyond `PartManifest`.

Write path as implemented at HEAD (post-`940b168`):

1. `writeFile` classifies the path. Non-part paths are immediate namespace-file or
   mountpoint writes. Part files that `partFileMustStayBlob` (primary.idx, `*.bin`/`*.mrk*`/`*.cmrk*`)
   stream to S3 staging (`[envelope][payload]`) or a local temp file while hashing. Everything else
   is buffered and inlined if `<= 1 MiB`, else spilled as a local blob. Inline finalize now calls
   `buildFor` so a part of only inline files still has a `PartWriteTxn`.
2. Dedup key is the content hash (`BlobRef{algo, digest}` → `layout().blobKey(ref)`). Nothing is
   uploaded until `commit()` → `publishStaging`.
3. New-ref publish: `stageManifest` → `precommitAdd` → `uploadPendingBlobs`/`putBlob` → `promote`.
   Committed-ref standalone write/remove: scratch manifest + precommit (if this txn uploaded blobs)
   → upload → merge committed entries minus `content_removed` → `repointRef` → `abandon` the scratch.
4. Blob materialization (`ensureBlobPresent`, after a durable precommit): mandatory `HEAD`. A present
   body whose freshness meta is absent or `Clean` is adopted (no PUT). Absent or `Condemned` →
   unconditional `publishBlob` under a fresh envelope (or one verbatim server-side copy of the
   staging object on the first absent publication). Then `reconcileMetaClean`. No incarnation token
   is stored on the dep; proof is `Materialized` or `TrustedManifest`.
5. `putIfAbsentStream`, `promoteStaged`, `conditionalCreateControlled`, `copyObjectConditional`,
   and `resurrect` are absent from the CAS tree (confirmed by grep).
6. Relink write side: `prepareAdoptFromManifest` → `prepareEntries` (adopt + stage + precommit),
   sender confirm, then promote. Unresolved promote is "do not fetch bytes, retry".

## Findings
### write-protocol-1 -- a durable committed-ref repoint is not rolled back, and `abandon` after it can report commit failure (Medium)
- Anchor: `ContentAddressedTransaction.cpp:401-416` (`publishStaging` committed-ref branch), `:523-536` (`commit` rollback); `Parts/PartFolderAccess.cpp:326-360` (`promoteBuild`), `:536-572` (`repointRef`); `Pool/CasPartWriteTxn.cpp:756-780, 888-908` (`created = !state.getCommitted().contains(...)`).
- Trigger: a transaction that writes or unlinks a file on a part whose ref is already committed (the `getView(..., ForceFresh)` branch), where any step after the repoint throws. Minimal case: one part. `repointRef` publishes the merged manifest; the next durable step is `st.build->abandon()` of the scratch precommit. A retry-later append there (wedged lane, fence/lease loss, `Removing`) throws. `commit()` sets `failed = true` and rolls back only slots with `oc->created == true`. The committed-ref branch always stores `created=false`.
- Evidence: rollback is `if (oc && oc->created) dropRefIfMatches(...)`. `created` is computed inside the promote ops-builder as "no committed row", so it is false exactly when this commit *modified* pre-existing committed content. The merged list drops every `content_removed` path, so the durable effect can include removing files from a committed part. There is no compensating "repoint back" op. `dropRefIfMatches` is also `noexcept` and swallows errors (`PartFolderAccess.cpp:693-702`). The caller is told the commit failed after the intended mutation already landed.
- Notes: same residual as CAS-005 (no rollback of a committed-ref repoint). Not High: MergeTree inserts use unique part names, so the ordinary INSERT path never takes this branch; the trigger is standalone write/remove on a committed part (autocommit inline sidecar, unlink+repoint). Fail-loud, not silent corruption. `out_slot` is now captured before `abandon()`, which closes the old "outcome lost" half.

### write-protocol-2 -- multi-part `commit()` is N independent durable publishes with best-effort rollback (Medium)
- Anchor: `ContentAddressedTransaction.cpp:482-536`; `Parts/PartFolderAccess.cpp:646-707` (`dropRefIfMatches` swallows every exception).
- Trigger: one transaction staging two or more parts (`createHardLink` between two part directories, `moveFile` across part directories, or `writeFile` into two part folders). Part *i* publishes; part *i+1* fails on any retry-later condition.
- Evidence: each `publishStaging` is its own ref-log transaction. Compensation drops only first-time creates (`created==true`) and is never queued as a `WriterCleanupDuty`. A failed multi-part commit can leave an arbitrary prefix of newly created refs published. The code comments this as restoring the wiring-layer transaction contract, not a CAS invariant (`:482-490`).
- Notes: same CAS-005 residual (no multi-ref atomicity). Per-ref journals are individually consistent; the gap is the missing durable rollback intent.

### write-protocol-3 -- staged inline `createHardLink`/`moveFile` into a dest with no build still fails closed at commit (Low)
- Anchor: `ContentAddressedTransaction.cpp:1191-1205` (`createHardLink`, staged-source inline branch), `:1534-1549` (`moveFile`, cross-part blob-only `buildFor`); guard at `:420-422`.
- Trigger: in one transaction, write a small metadata file (not matched by `partFileMustStayBlob`) into part A, then `createHardLink` or cross-part `moveFile` it into part B that is not otherwise written and is not a committed ref. The inline branch appends to `dst_st.entries` without `buildFor`. At commit, `publishStaging` finds non-empty entries, `getView` is null, and throws `LOGICAL_ERROR: "staged entries or removal marks ... without a Build"`.
- Evidence: `writeFile`'s inline path now calls `buildFor` (`:956-965`) — that half of the 2026-08-12 finding is closed. The staged-source `createHardLink` inline arm does not. `moveFile` calls `buildFor` only when `entry.placement == Blob`. The committed-source hardlink arm (`:1221`) always calls `buildFor`. Fail-closed, no corruption; `LOGICAL_ERROR` is treated as a bug rather than retryable, and earlier parts in the same transaction may already be durable (finding 2).
- Notes: reachable for an all-inline dest (empty covering part cloned by metadata hardlinks only). A dest that also receives a blob file gets a build before commit.

### write-protocol-4 -- writer-epoch fence is checked at `requireAlive` entry, not at the durable append (Low)
- Anchor: `Pool/CasPartWriteTxn.cpp:165-184` (`requireAlive`), `:727` (only `requireAlive` in `promote`), `:769-923` (ops-builder never re-checks `epoch`); `Pool/CasPool.cpp` self-remount bumps `liveWriterEpoch`.
- Trigger: a build opened under writer epoch E1 enters `promote`, passes `requireAlive`, then blocks in `backend().get(manifest_key)` or the append queue (bounded by `operation_deadline_ms`, default 90 s). The mount loses its lease and self-remounts to E2. `appendRefOps` acquires a runtime under the new fence generation and the promote commits a `ManifestRef` that still carries E1.
- Evidence: the shipped text at `:181-183` ("belongs to a superseded mount incarnation … restart the build") states the intended invariant; nothing enforces it after the entry check. Append-side fences (`admitted_fence_generation`, catalog life) evaluate the *new* incarnation and do not reject the old build's epoch.
- Notes: outcome stays consistent — `active_build_seqs` survives remount, the newborn-blob watermark still protects deps, and a cross-node takeover is excluded (`mayMutate()` / live-twin refusal). The race is with the stale-precommit sweep: whichever of promote/sweep reaches the lane first wins.

## By-design / info / non-actionable
- **Blob publish after `940b168` is unconditional by design.** `ensureBlobPresent` HEADs, adopts a present non-condemned body, else `publishBlob` rewrites the key with a fresh envelope (`CasPartWriteTxn.cpp:327-468`; `CasObjectStorageBackend.cpp:862-957`). No `If-None-Match`, no request-controller budget on the body PUT, no token returned. Fence is checked before and after I/O (`checkFenceOrThrow(admitted_generation)`); a mid-stream fence loss completes the overwrite and then refuses the dep ("bytes are harmless debris", `:443-445`). Content-addressed keys make a concurrent overwrite the same payload. This replaces `resurrect`/`putIfAbsentStream`/`conditionalCreateControlled`; do not re-raise CAS-088's "unconditional overwrite" shape as a defect.
- **EDGE-BEFORE-OBSERVE holds.** `ensureBlobPresent` refuses unless `precommit_state == Durable` (`:257-261`). New-ref and scratch-repoint paths precommit before `uploadPendingBlobs`.
- **Lost-ACK on the ref-log append is still handled correctly.** `Unresolved` never forgets the id unless nothing was sent; other unresolved outcomes wedge the lane on the same key/bytes.
- **Repoint of the committed binding is atomic.** `RemoveCommitted(old)` + `Promote` + `SetPublishedAt` are one ref-log transaction (`CasPartWriteTxn.cpp:888-921`).
- **Relink write side is publish-then-confirm.** Receiver precommit is durable before the sender is asked to prove the exact `(ref, ManifestRef)` (`ContentAddressedMetadataStorage.cpp:2303-2308`). `PreparedPartWrite` records the commit in an allocation-free region before throwable post-work (`PartFolderAccess.cpp:332-350`).
- **Precommit cleanup is durable.** `~PartWriteTxn` enqueues `WriterCleanupDuty` when precommit is `Uncertain` or `Durable` (`CasPartWriteTxn.cpp:154-158`).
- **Dedup/HEAD-first counters are no longer emitted before admit.** `CASBlobBodyPutAvoided` increments only on the successful observe path after fence checks (`:372`).
- **Verbatim staged copy is first-publication-only.** `BlobSource::beginPublication` is shared across copies; later attempts stream under a new envelope (`CasPartWriteTxn.h:34-39`, `.cpp:393-413`).
- **`putMetaIfAbsent` on the observe-backfill path ignores its outcome** (`:363-370`). Absent meta is treated as Clean. A lost backfill is retried by the next observer; GC's in-degree still wins over `delete_pending`. Accounting/observability only — not raised.

## Closed-since-2026-08-12
- write-protocol-3 (resurrect is an unfenced overwrite that returns a token it did not write) — `resurrect` is gone; `publishBlob` is tokenless; `BlobDepRecord` has no token. Closed by `940b1685bf9`. The unconditional-publish shape is now the protocol (see by-design).
- write-protocol-4 (inline `writeFile` stages into a dest with no build) — `writeFile` inline finalize calls `buildFor` (`ContentAddressedTransaction.cpp:956-965`). Residual remains for staged-source hardlink/move (write-protocol-3 above).
- write-protocol-5 (HEAD-first ProfileEvents before `observeAndAdmit`) — optional HEAD-first / dedup-cache path is gone; counters fire only after a successful adopt. Closed by `940b1685bf9`.
- Symbols `putIfAbsentStream`, `promoteStaged`, `conditionalCreateControlled`, `copyObjectConditional` — absent from the CAS tree at this SHA.

## Coverage
- Reviewed: writeFile/staging (local + S3), hash/dedup key, mandatory HEAD then adopt-or-unconditional-publish, inline vs blob, manifest stage/caps, precommit, promote/repoint, ref-log append + fencing, rollback, relink write side, fan-out merge, abandon/cleanup.
- N-A: GC reclaim decisions; read-path caches (read-protocol audit).
- Deferred: `CasRefLedger` wedge/recovery internals beyond the append outcome classification used by promote/precommit/abandon.
