# write-protocol — re-run 2026-07-30

Audit scope: end-to-end CAS write path — `precommit → blob PUT (envelope + payload) → promote (ref CAS) → journal (ref-log) append`. Verifies the 9 CAS-### findings the original `cas-write-protocol-audit.md` cluster maps into (W1, W2, W-N1..N4 → CAS-020, CAS-081, CAS-035, CAS-082, CAS-083, CAS-084) plus the write-adjacent CAS-002 / CAS-008 / CAS-021 / CAS-038 / CAS-097 called out in the task brief.

## Scope in current code

Files walked (write-side, line-by-line for the load-bearing sections):

- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp` (1916 lines) — commit loop, `publishStaging`, `writeFile`, `stageBlobPartFile`, `moveDirectory`, `replaceFile`, `unlinkFile`, `CaContentWriteBuffer`.
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPartWriteTxn.cpp` (~1490 lines) — `stageManifest`, `precommitAdd`, `promote`, `abandon`, `putBlob`/`observeAndAdmit`/`uploadFromSource`, `adoptEvidence`.
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/PartFolderAccess.cpp` — `promoteBuild`, `publishEntries`, `republishRef`, `repointRef`, `dropRef`.
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasRefLedger.cpp` (~2990 lines) — `appendRefOps` batching/carving, `dropRef`, `updateRefPublishedAt`, snapshot publisher, stale-precommit sweep.
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPlainObjects.cpp` — `casPutObject` (namespace/mountpoint file writes).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasBlobEnvelopeFormat.cpp` (253 lines) — v3 blob envelope encode/decode.
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPartManifestFormat.cpp` — manifest encode/decode (skimmed).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasRefLogFormat.h` — 20 MiB / 64 MiB txn caps.
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasBlobHashingWriteBuffer.cpp` (260 lines) — hash-through streaming write buffer.

## Findings still present

### CAS-002 — Shard `casPut` fenced by content token, not `writer_epoch`

- Anchor: `Pool/CasPlainObjects.cpp:51` — `putOverwrite(full_key, bytes, head.token)`.
- Trigger: any concurrent writer (or a stale-fence writer that later admits itself) mutating the same namespace/mountpoint object between the fence-generation check (line 43) and the durable `putOverwrite` (line 51). The atomic precondition is the content ETag (`head.token`), not `writer_epoch`.
- Evidence quote (`CasPlainObjects.cpp:34–37`, `43`, `51`):
  > "rev.7 [C2]: the fence generation captured at admission is re-checked immediately before EVERY durable PUT below, not just the first attempt."
  > `check_fence_or_throw_fn(admitted_generation);`
  > `if (backend.putOverwrite(full_key, bytes, head.token).outcome == PutOutcome::Done)`
- Notes: The fix-in-progress is the *hoisted* fence check outside the atomic PUT — TOCTOU-close but not a single atomic epoch-fenced conditional. RefLog appends are epoch-fenced separately by embedding `writer_epoch` in `RefTxnId` (`CasRefLedger.cpp:1673`), so this residual applies to **plain-object writes** (namespace files, mountpoint objects) and the "single-appender" mutation-entry CSN append (line 27–32 documents the reliance on external single-appender contract, not the CAS itself). The write-audit's split-brain path lives here.

### CAS-021 — Multi-part `commit()` is not atomic; best-effort rollback is not durable

- Anchor: `ContentAddressedTransaction.cpp:494–513` — serial `publishStaging` loop, catch-and-`dropRefIfMatches` compensating rollback.
- Trigger: crash / OOM / non-idempotent second-part failure after the first part's `promoteBuild` returned successfully. The already-durable first part remains committed; the reported outcome is failure.
- Evidence quote (`ContentAddressedTransaction.cpp:458–466`):
  > "Commit atomicity: there is no multi-ref atomic publish, so a publish that throws after earlier parts already published would leave a PARTIAL commit — some refs durably visible while the transaction reports failure … Track the refs THIS commit creates and, on any exception, best-effort unpublish them before rethrowing."
  > `for (const auto & oc : part_outcomes) if (oc && oc->created) metadata_storage.partAccess()->dropRefIfMatches({oc->ns, oc->ref}, oc->manifest_ref);`
- Notes: The rollback keys on `Cas::CommitOutcome::manifest_ref` (`ContentAddressedTransaction.cpp:474–508`) — a real improvement over "drop by name" (a concurrent repoint survives). Still **best-effort** (`dropRefIfMatches` runs in-process; a crash between two `publishStaging` calls leaves the earlier commit durable with no compensating drop). Correctness caveat unchanged: crash-mid-commit → durable partial commit is possible; the promise is fail-loud on the failing part while earlier parts survive the mid-commit crash as CAS refs. The audit's `INV_COMMIT_FAILCLOSED` is preserved per-part, not per-transaction. This is a **wiring-layer** guarantee, not a CAS invariant (as the comment notes at line 466).

### CAS-035 — Presence-asserting closures throw on lost-ACK replay

- Anchor: `Pool/CasRefLedger.cpp:2807–2822` (`dropRef` closure), `2842–2874` (`updateRefPublishedAt` closure).
- Trigger: append-lane retry after a lost ACK re-runs the closure against the fresh live state. If the *first* run already committed the drop / update, the *second* run's closure now sees "committed row is absent" and throws `FILE_DOESNT_EXIST` — a spurious failure surfaced for an operation that in fact succeeded.
- Evidence quote (`CasRefLedger.cpp:2810–2814`):
  > `const auto it = state.getCommitted().find(ref_name);`
  > `if (it == state.getCommitted().end())`
  > `throw Exception(ErrorCodes::FILE_DOESNT_EXIST, "dropRef: no such ref {} in namespace {}", ref_name, ns.string());`
  > Comment on the throw: "Fail-closed (no silent no-op): this item's own exception, the batch survives."
- Notes: `PartWriteTxn::abandon` (`CasPartWriteTxn.cpp:1354–1379`) explicitly *does* tolerate an already-absent precommit under `PrecommitState::Uncertain` (comment lines 1355–1364), so the pattern is *known and applied surgically* — but only for abandon. `dropRef` and `updateRefPublishedAt` remain strict. Same class as the original W-N1 finding. Contrast with `dropRefIfPresent` in `PartFolderAccess.cpp:600–610`, which the transaction-level rollback and `moveDirectory` use — but user-driven drops still route through the strict `CasRefLedger::dropRef`.

### CAS-038 — Scratch temp file un-fsynced and never re-verified against its key between hash and upload

- Anchor: `ContentAddressedTransaction.cpp:1749–1765` (`CaContentWriteBuffer` local-scratch ctor), `1819–1846` (`finalizeImpl`), `1869–1874` (`sync`).
- Trigger: any scratch-FS bit-flip / partial-page cache eviction / OS crash between `sink->finalize()` (line 1837, `WriteBufferFromFile::finalize`) and the later re-read at `ContentAddressedTransaction.cpp:295` (`ReadBufferFromFile(staging_key)` inside `uploadPendingBlobs → write_payload`). The hash was computed in-memory on the stream; the on-disk bytes are never re-hashed and never fsynced.
- Evidence quote (`ContentAddressedTransaction.cpp:1819–1846`):
  > `void CaContentWriteBuffer::finalizeImpl()`
  > `{ next(); const size_t size = count(); const std::string hash_hex = hashing->getHashHex(); hashing->finalize(); ... sink->finalize(); if (on_finalized) { on_finalized(hash_hex, size, temp_path); ... } }`
  > No `sink->sync()` before `on_finalized`; `sync()` (line 1869) exists but is not called on the finalize path.
- Notes: `sink` is a plain `WriteBufferFromFile` (line 1754); `finalize()` only flushes the write buffer, not `fsync()`. The S3 staging-object mode is fine (the payload streams straight to the object store and is validated via the pool CAS token). This finding is strictly the **Local scratch** path.

### CAS-097 — `updateRefPayload` one-shots are intentionally not rolled back

- Anchor: `ContentAddressedTransaction.cpp:466–472` (rollback comment scope), `Pool/CasRefLedger.cpp:2842–2874` (`updateRefPublishedAt`).
- Trigger: an autocommit-on-committed-part write triggers a `repointRef`/`updateRefPublishedAt` one-shot; a later failure in the same commit path leaves the one-shot durable while the surrounding transaction reports failure.
- Evidence quote (`ContentAddressedTransaction.cpp:470–472`):
  > "updateRefPublishedAt mutations (autocommit one-shots on a COMMITTED part) are individually durable by design and are deliberately NOT rolled back."
- Notes: Documented rollback-window observability gap — same as the original BC3-2/BC3-3 folded into CAS-097. `📐 by-design` per the original consolidated summary; the current code makes the design explicit in the commit-rollback comment. No new evidence flip; kept as still-present for tracking parity.

### CAS-008 — 64 MiB write-side hard cap on the ref-log txn (removal class)

- Anchor: `Formats/CasRefLogFormat.h:74` — `inline constexpr size_t ref_removal_max_bytes = 64 * 1024 * 1024;`. Also `ref_txn_max_bytes = 20 MiB` (line 73), `ref_txn_max_ops = 5000` (line 68).
- Trigger: an admin-driven `RemoveNamespace` (whole-namespace drop) whose per-op removal ops for *every committed ref + precommit* in the namespace exceed 64 MiB of encoded JSON — writes are rejected by the codec.
- Evidence quote (`CasRefLogFormat.h:63–74`):
  > "A transaction containing `RemoveNamespace` is 'removal-class': it shares the larger complete-table byte budget and has neither a separate operation-count cap nor a per-op cap, because that byte budget alone bounds it."
- Notes: This is architecturally different from the original CAS-008 shape (a single monolithic root-shard journal hitting 64 MiB under churn). Under the current design each namespace publishes its own ref-log txns bounded by 20 MiB / 5000 ops and periodically snapshotted (`CasRefLedger::maybeScheduleSnapshotPublish`, `trySnapshotPublishOnce`). Ordinary write availability is therefore *decoupled* from GC folding — an important improvement over the pre-refactor shape. The residual is only the removal-class 64 MiB cap on a **single** whole-namespace drop txn, which is a load-shedding gate, not a churn-availability wedge. Left `🟡 still-present` at reduced severity because the exact hard limit still exists and can reject a giant-namespace drop; the *churn* aspect is arguably fixed. Reasonable re-classification target: `↗ split-out` (write-availability piece fixed, drop-size piece remains).

### CAS-084 — Orphan multipart uploads on interrupted / lost-ACK blob upload

- Anchor: `Backend/CasObjectStorageBackend.cpp:812` (documented single-PUT constraint for generation-token stores), `Backend/CasProbe.cpp:274` (probe-cleanup path uses `removeObjectIfExists`, not `abortMultipartUpload`).
- Trigger: a payload-streaming upload of a large-enough blob or staging object that internally becomes a multipart upload; connection interrupt / lost ACK between `Initiate` and `Complete` leaves an unaborted multipart on S3.
- Evidence: no `abortMultipartUpload` call anywhere in the CAS tree (`grep abortMultipart` returns zero matches under the CAS root); the only cleanup is `removeObjectIfExists` (final-object DELETE) and the mount-lease-scoped staging sweeper (`ContentAddressedTransaction.cpp:189–194` / `Cas::sweepOwnMountStaging`).
- Notes: Reclaimed by S3 lifecycle policy only. `📐` by-design per the original summary, kept as `🔴 still-present` (no code change) with `LEAK / DAY2` severity.

## Findings fixed / no longer reproducible

### CAS-020 — `promote`-overwrite manifest leak (RENAME / lost-ACK)

- Fix anchor: `Pool/CasPartWriteTxn.cpp:1184–1229` — `promote`'s "BUG 1a" branch.
- What changed: `promote` now refuses to overwrite a live committed ref that already names a *different* manifest unless the caller opts in via `allow_repoint`. When `allow_repoint=true`, the closure emits an explicit `OwnerTransition` op that RETIRES the old committed binding (line 1223–1229), in the same ref-log record as the new promote — so GC folds the `-1` on the displaced manifest's blobs. The unconditional `refs[R] = …` pattern is gone.
- Evidence:
  > `CasPartWriteTxn.cpp:1195–1203`: `if (const auto it = state.getCommitted().find(final_ref_name); it != state.getCommitted().end() && !(it->second.manifest_ref == id.ref)) { if (!allow_repoint) throwCasWriteRetryLater(...); repoint_old = it->second.manifest_ref; }`
  > Lines 1223–1229: emits `RefOp{OwnerTransition, old_binding=Committed(final_ref_name, *repoint_old), (no new_binding)}` in the same ref-log txn.
- RENAME path (`ContentAddressedTransaction.cpp:1232–1249` → `PartFolderAccess.cpp:506–534` `republishRef`): `republishRef` no longer overwrites a same-content destination silently (it drops the source in that case) and REJECTS a different-content destination with `ABORTED` (line 524). The RENAME lost-ACK amplifier flagged by W1 is closed.

### CAS-081 — `abandon` retires `build_seq` before appending the precommit-removal event

- Fix anchor: `Pool/CasPartWriteTxn.cpp:1337–1413` — reordered `abandon`.
- What changed: `abandon()` first appends the precommit-removal `RefOp` (line 1354–1379), then flips `alive = false` (line 1405), then calls `store->retireBuildSeq(build_seq)` (line 1413). The ordering is explicitly documented at lines 1407–1412 ("mirrors `PartWriteTxn::promote`, which retires after its commit"). The old "retire seq, then append event" fragile shape is gone.
- Evidence quote: `CasPartWriteTxn.cpp:1408–1412`:
  > "This runs AFTER the precommit removal above (mirrors `PartWriteTxn::promote`, which retires after its commit) so the build stays active until its precommit binding's removal is durable: retiring first would advance `min_active` past a build whose precommit binding is still live in the ref log …"

### CAS-039 — Envelope size-consistency check bypassable via `logical_size` uint64 overflow wrap

- Fix anchor: `Formats/CasBlobEnvelopeFormat.cpp` entire file.
- What changed: the v3 envelope no longer encodes a `logical_size` / `logical_hash` / `header_len == object_size - logical_size` structural relation. The envelope is now a fixed-length JSON header (`type`, `v`, `tag`, `bld`, optional `ts`/`by`/`op`/`ch`, optional `ref`) space-padded to `blob_header_len` with an `'\n'` terminator (lines 99–160 encode, 162–251 decode). Payload length is the object size minus the derived `header_len` (from the `'\n'` position, `decodeEnvelopeHeader:242`). No overflow-wrap surface remains.
- Evidence: no `logical_size` field in either encode or decode; `header_len` derived post-decode from `'\n'` position, not from arithmetic against `object_size`.

## Findings covered by W-N# in the original write-protocol audit

Kept for parity with the mapping table. All four are ≤ Low severity in the consolidated summary.

- **CAS-082** (W-N2, lost-ACK replay double-appends journal events): still-present class. The append-lane commit path (`CasRefLedger.cpp:1873+` `commitRefChunk`, and the item-fail arm at line 1839) tolerates an already-applied idempotent replay (see lines 1842–1861: "every survivor of the LAST chunk contributed ZERO ops — an idempotent no-op"), so the fix here is *set-idempotency* not *append-idempotency*. Journal (ref-log) bloat under lost-ACK replay is unchanged. `LEAK`, low severity.
- **CAS-083** (W-N3, flat-combining leader convoy under S3 stall): still-present class. `CasRefLedger::flushRefBatch` / `commitRefChunk` remain the single-leader-per-namespace serialize-then-carve pattern; a slow object store still stalls the whole batch. Liveness, not correctness.
- **CAS-084** (W-N4, orphan multipart uploads / manifest bodies): documented above under "still present".

## New findings (not in original audit)

- **NEW-write-1** — `CaContentWriteBuffer::finalizeImpl` sets `temp_ownership_transferred = true` (line 1845) even after `on_finalized` throws in the tail of that lambda, because the flag is set *after* the callback. On S3-staging mode a callback throw (e.g. from `stageBlobPartFile` when the route parse throws under the `writeFile` closure) would leave `temp_ownership_transferred = false`; `~CaContentWriteBuffer()` then calls `cancel()` → `cancelImpl` (line 1849) — and for `is_s3_staging=true` the destructor deliberately *does not* delete the remote staging object (comment at line 1855–1858). So a fresh mount's staging-key becomes an orphan sweep target rather than being reclaimed on the failing txn, even though `cleanupPendingTempFiles` was never given the key. Severity `Low`, `LEAK / OBSERV`, anchor `ContentAddressedTransaction.cpp:1842–1846` combined with `165–207`. Reachable only if `on_finalized` itself throws after the sink is durable — narrow, but noted.

- **NEW-write-2** — `CaContentWriteBuffer::finalizeImpl` reports the payload size via `count()` (line 1822), which is the byte count of what THIS buffer forwarded to `hashing`. In S3-staging mode the envelope header is written directly to `sink` (line 1794) *bypassing* `hashing` and this outer buffer. Correct by design, but the reported `size` returned via `on_finalized(hash_hex, size, temp_path)` is the **payload-only** size — which `stageBlobPartFile` then persists as `entry.blob_size`. Downstream `tryReadFileInFlight` for S3 staging then builds a `ReadBufferFromFileView` windowed to `[header_len, header_len+size)` (line 617–622), which requires `header_len` to come from `poolMeta().blob_header_len` and not from a decoded envelope. If a mid-stream mount rotates `blob_header_len` (currently a pool-wide constant, `CasPoolMeta` guarded), the in-flight read of a pending blob would read from the wrong offset. Not currently exploitable (pool-meta `blob_header_len` is create-time constant per CAS-066), but a mixed-version writer scenario (`CAS-024`, `PoolMeta` drift) chains here. Severity `Low`, `CORRECTNESS / COMPAT`, anchor `ContentAddressedTransaction.cpp:617–622`. Flag for future defence: window on the decoded envelope's own `header_len`, not `PoolMeta`.

- **NEW-write-3** — `ContentAddressedTransaction::moveDirectory`'s RENAME-TABLE branch (`ContentAddressedTransaction.cpp:1231–1249`) does `for (const auto & [ref, _] : store->listRefs(from_ns))` and calls `republishRef(...)` per ref, then `putNamespaceFile` per verbatim file, then `dropNamespace(from_ns)`. There is no bounded budget on this loop and no chunking: a table with millions of parts stalls the entire user query for the whole loop, holding the disk transaction open (the containing `ContentAddressedTransaction` is not concurrent-safe). Comment at 1215–1223 openly notes the re-drivability but does not budget the loop. Severity `Low` (`LIVENESS / PERF`), anchor `ContentAddressedTransaction.cpp:1233–1238`. Chain with CAS-006 (S3 latency under DataPartsLock) and CAS-057 (LIST cost) for a full outage shape on RENAME TABLE of a very large table.

## By-design / N/A / info

- **CAS-201 / rollback-window observability** — `publishStaging` publishes each part serially; a partial commit is documented (lines 458–466) and the rollback keys on `Cas::CommitOutcome::manifest_ref` (line 474–508). This is the wiring-layer transaction contract, not a CAS invariant. Info.
- **`CasEvent` audit emission** — every promote/abandon path emits a best-effort `EventEmitter` event guarded by `try/catch` (e.g. `CasPartWriteTxn.cpp:1253–1268`, `1319–1333`, `1382–1397`, `1420–1435`). Observability signal, not a defect.
- **CAS-002 mutation-entry single-appender** — `CasPlainObjects::casPutObject:27–32` acknowledges the `bytes`-frozen-before-loop single-appender contract; the mutation-entry CSN append is the only production user. Info (documented contract).

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-020 | Med-High | ✅ fixed | `Pool/CasPartWriteTxn.cpp:1184–1229` (BUG-1a `allow_repoint` retires old binding); `Parts/PartFolderAccess.cpp:506–534` (`republishRef` rejects different-content dst) |
| CAS-002 | High | 🔴 still-present | `Pool/CasPlainObjects.cpp:43,51` (fence-check outside atomic PUT; token=content ETag, not `writer_epoch`) |
| CAS-008 | High | ↗ split-out | `Formats/CasRefLogFormat.h:74` (64 MiB removal-class cap still exists; churn-availability piece decoupled via per-ns ref-log + snapshot publish) |
| CAS-021 | Med | 🔴 still-present | `ContentAddressedTransaction.cpp:494–513` (serial `publishStaging` + best-effort `dropRefIfMatches`) |
| CAS-035 | Med | 🔴 still-present | `Pool/CasRefLedger.cpp:2810–2814` (`dropRef` throws `FILE_DOESNT_EXIST` on absent committed ref); `:2853–2856` (same in `updateRefPublishedAt`) |
| CAS-038 | Med | 🔴 still-present | `ContentAddressedTransaction.cpp:1819–1846` (no `fsync`; no re-hash of on-disk bytes before upload) |
| CAS-039 | Med | ✅ fixed | `Formats/CasBlobEnvelopeFormat.cpp` (v3 drops `logical_size`; `header_len` derived from `'\n'` position, no overflow surface) |
| CAS-081 | Low | ✅ fixed | `Pool/CasPartWriteTxn.cpp:1354–1413` (`abandon` appends precommit-removal, THEN flips `alive`, THEN retires seq; ordering documented at 1407–1412) |
| CAS-082 | Low | 🔴 still-present | `Pool/CasRefLedger.cpp:1842–1861` (idempotent no-op tolerated but retried ops still appended to journal) |
| CAS-083 | Med | 🔴 still-present | `Pool/CasRefLedger.cpp` `flushRefBatch`/`commitRefChunk` (single-leader per-ns batch model unchanged) |
| CAS-084 | Low | 🔴 still-present | zero `abortMultipartUpload` calls under `MetadataStorages/ContentAddressed/**` |
| CAS-097 | Low | 📐 by-design | `ContentAddressedTransaction.cpp:466–472` (comment explicitly documents no-rollback for one-shots) |
| NEW-write-1 | Low | ⚪ info | `ContentAddressedTransaction.cpp:1842–1846` combined with `165–207` (S3 staging orphan on late `on_finalized` throw) |
| NEW-write-2 | Low | ⚪ info | `ContentAddressedTransaction.cpp:617–622` (in-flight read uses `PoolMeta.blob_header_len`, not decoded envelope) |
| NEW-write-3 | Low | ⚪ info | `ContentAddressedTransaction.cpp:1233–1238` (unbounded RENAME-TABLE loop) |

## Counts

- Still present: **7** (CAS-002, CAS-021, CAS-035, CAS-038, CAS-082, CAS-083, CAS-084).
- Fixed: **3** (CAS-020, CAS-039, CAS-081).
- Split-out / partially fixed: **1** (CAS-008 — churn axis fixed, removal-class 64 MiB cap remains).
- By-design: **1** (CAS-097).
- New findings: **3** (all Low / info).

## Headline

The write-side spine has genuinely closed the two write-protocol defects the original audit called correctness-load-bearing: **CAS-020** (promote-overwrite manifest leak) is fixed by the `allow_repoint` two-op ref-log record that emits the retiring `OwnerTransition` for the displaced manifest in the same txn, and **CAS-081** (`abandon` ordering) is fixed by appending the precommit-removal *before* `alive`/`retireBuildSeq`. **CAS-039** (envelope size-consistency overflow) is architecturally gone with the v3 JSON envelope. The still-present items are the ones the consolidated summary already tagged as unchanged classes (**CAS-002** epoch-vs-token fencing on plain-object writes; **CAS-021** best-effort multi-part-commit rollback; **CAS-035** presence-asserting-closure `FILE_DOESNT_EXIST` on lost-ACK replay of `dropRef`/`updateRefPublishedAt`; **CAS-038** un-fsynced un-re-hashed local scratch; **CAS-082/083/084** journal-bloat/leader-convoy/orphan-MPU) — none newly regressed, none escalated in severity. Three new low-severity observations noted around the write buffer's S3-staging orphan path, envelope-header offset trust, and unbounded RENAME-TABLE loop.
