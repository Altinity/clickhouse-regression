# bc3-exception-safety — re-run 2026-07-30

Static re-verification of the BC-3 exception-safety / partial-commit-rollback / one-shot-ref-update-rollback audit against current PR HEAD (`/Volumes/workspace/ClickHouse`, branch `cas-audit-20260730`). Only CAS code inspected.

## Scope in current code

- Files/dirs walked:
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.h`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp` (dtor, `cleanupPendingTempFiles`, `uploadPendingBlobs`, `publishStaging`, `commit`, `tryCommit`, `writeFile`, `tryCreateWriteBuffer`)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/PartFolderAccess.h` / `.cpp` (`dropRefIfMatches`, `CommitOutcome`)
  - Cross-checked references: `Pool/CasPartWriteTxn.{h,cpp}`, `Pool/CasRefLedger.{h,cpp}`, `Primitives/CasBlobHashingWriteBuffer.*`

## Findings still present

### BC3-1 (Med) — Multi-part `commit()` is not atomic; mid-loop throw yields a durable partial commit (=CAS-021)
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:458-513` (`commit()`; publish loop + compensating rollback).
- Trigger: transaction stages parts A, B, C; `publishStaging(B)` throws after A already published; rollback drops A only if `oc.created` and the ref still matches `manifest_ref`. Under a compounded backend outage, the conditional `dropRefIfMatches` can still be a no-op (returns `false`, logs, increments `CasRefRollbackBestEffortDropFailed`) → A remains durably live while `commit()` reports failure.
- Evidence quote:

```458:466:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
    /// Publish each staged part. [TXN-ONE-PIPELINE] This is the ONLY place a ref becomes durable — the
    /// tmp->final rename is a pure overlay re-key. Commit
    /// atomicity: there is no multi-ref atomic publish, so a publish that throws after
    /// earlier parts already published would leave a PARTIAL commit — some refs durably visible while
    /// the transaction reports failure, diverging the durable pool from the disk layer's all-or-nothing
    /// expectation.
```

- Notes: The rollback is now precise per outcome (`dropRefIfMatches` on the exact `manifest_ref` — Task 3 in the PR), preventing the earlier "unconditional `dropRef` clobbers a concurrent repoint" hazard. But the underlying multi-ref atomicity gap is unchanged and explicitly documented. Still-present, same severity.

### BC3-3 (Low) — Rollback ordering unspecified vs partial visibility (folded into CAS-097)
- Anchor: `ContentAddressedTransaction.cpp:494-513` (rollback loop runs AFTER the throw, refs A already durable+visible).
- Trigger: concurrent reader / GC observes an already-published earlier part between its `publishStaging` completion and the compensating `dropRefIfMatches`. No correctness violation (each ref is independently valid), but the transaction's aborted state is transiently observable.
- Evidence quote:

```509:511:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
        for (const auto & oc : part_outcomes)
            if (oc && oc->created)
                metadata_storage.partAccess()->dropRefIfMatches({oc->ns, oc->ref}, oc->manifest_ref);
        throw;
```

- Notes: Unchanged.

### BC3-2 (Low, re-scoped) — Repoint of an already-committed ref is intentionally NOT rolled back → "commit failed" ≠ "no durable effect" (=CAS-097)
- Anchor: `ContentAddressedTransaction.cpp:468-472` and `468-472` rollback comment; `publishStaging` repoint branch at `:338-393` returns `CommitOutcome` with `created=false`.
- Trigger: A transaction stages a new part AND a standalone write to an already-committed part (e.g. `metadata_version.txt`, `txn_version.txt`, or any inline metadata file on a committed part). Both go through `publishStaging`; the mutable-per-part branch was removed and these files now flow through the repoint path. The new-part promote yields `created=true` (rolled back). The repoint on the committed ref yields `created=false` and is deliberately NOT dropped on failure:

```468:472:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
    /// Fail-closed (CLAUDE.md): only refs that were ABSENT before we published them are rolled back. A
    /// ref that already existed is pre-existing data this commit must never destroy on its error path.
    /// Publishing over a live ref does not occur in the MergeTree write path (unique part names), but
    /// the rollback must not assume it. updateRefPublishedAt mutations (autocommit one-shots on a
    /// COMMITTED part) are individually durable by design and are deliberately NOT rolled back.
```

- Notes: Mechanism changed (no more separate mutable-file `updateRefPayload` path — deleted per `writeFile` comments at `:844-850`) but the observable contract is identical: if the transaction contains BOTH a new-part publish and a repoint of a pre-existing part, and the second throws, the first is committed durably while `commit()` reports failure. The comment still names `updateRefPublishedAt`; that operation itself is not surfaced in code — the concern now generalizes to any inline write that lands as a repoint. Still-present.

### BC3-4 (Info ✅) — Precommit-first / publish-last ordering keeps mid-states debris, not dangling refs
- Anchor: `ContentAddressedTransaction.cpp:400-413` (write path: `stageManifest → precommitAdd → uploadPendingBlobs → promoteBuild`); repoint path `:344-359` (scratch manifest + `precommitAdd` before `uploadPendingBlobs`, `repointRef` last).
- Evidence quote:

```404:410:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
    /// ORDERING IS LOAD-BEARING (EDGE-BEFORE-OBSERVE):
    /// precommitAdd's durable closure names EVERY blob hash BEFORE putBlob makes the first backend
    /// observation. This is what lets promote skip re-validating tokened leaves (a condemnation in the
    /// putBlob→promote window cannot graduate — the next fold sees the edge).
```

- Notes: still holds; a throw before promote leaves uploads as unreferenced (GC-reclaimable) debris, never a dangling live ref.

### BC3-5 (Info ✅) — Temp-file & buffer RAII is complete
- Anchor: dtor `ContentAddressedTransaction.cpp:107-140` (unconditional `cleanupPendingTempFiles` + best-effort `abandon` per build with `tryLogCurrentException`); `cleanupPendingTempFiles` `noexcept` at `:165-210`; `CaContentWriteBuffer`'s `cancelImpl`/`removeTempFile` are `noexcept` (header `:368-370`).
- Evidence quote:

```109:112:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
    /// Always clean up pending staging (whether committed or not). On the success path
    /// cleanupPendingTempFiles was already called at the end of commit(); this call is the defensive
    /// backstop for aborted/exception-unwound transactions whose publishStaging never ran.
    cleanupPendingTempFiles();
```

- Notes: Additionally, uncommitted S3 staging objects are deliberately kept for the mount-lease sweeper (`Cas::sweepOwnMountStaging`); still not a leak (§at `:186-206`).

## Findings fixed / no longer reproducible

### BC3-6 (fixed) — Failed-rollback is no longer silent; a metric + log now fire
- Fix anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/PartFolderAccess.cpp:646-707` (`dropRefIfMatches` is `noexcept` and, on catch, increments `ProfileEvents::CasRefRollbackBestEffortDropFailed` and `tryLogCurrentException`s a distinctive `ns=/ref=/expected=` message).
- Evidence:

```693:702:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/PartFolderAccess.cpp
    catch (...)
    {
        /// Best-effort rollback cleanup, like dropRefBestEffort: debris is GC-reclaimed, but swallowing
        /// without a diagnostic could leave a live phantom ref after a backend outage.
        removed = false;
        ProfileEvents::increment(ProfileEvents::CasRefRollbackBestEffortDropFailed);
        tryLogCurrentException(getLogger("CachedPartFolderAccess"),
            fmt::format("CA conditional rollback dropRefIfMatches failed (ns={} ref={} expected={}); "
                        "the ref may remain live", key.ns.string(), key.ref, Cas::manifestRefDebugString(expected)));
    }
```

- Notes: Operator-observable metric + WARN log directly addresses the "no signal on divergence" concern that made BC3-1 dangerous. The compounded partial-commit remains possible (BC3-1) but is no longer silent.

### Structural cleanups relative to the original audit
- The empty `catch(...) {}` (NOLINT bugprone-empty-catch) inside the rollback loop is gone; rollback safety is now enforced by `dropRefIfMatches`' `noexcept` contract, so no throw can propagate from the compensating loop → the original "never mask original failure" comment (`ContentAddressedTransaction.cpp:502-503`) is now actually enforced by the callee, not by an in-line swallow.
- `dropRefIfMatches` (Task 3) replaces the earlier unconditional `dropRef`, so the rollback now leaves an unrelated concurrent repoint of the same ref intact.
- Outcome slots (`part_outcomes[i]`) are captured immediately after each `promoteBuild` / `repointRef` return, BEFORE any further throwable work in `publishStaging` (`:377-382`, `:421-427`). This closes the "later throw loses the outcome and skips rollback of that ref" window.

## New findings (not in original audit)

### NEW-bc3-1 (Low) — Comment references a deleted API (`updateRefPublishedAt`) — stale, mildly misleading
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:471-472`
- Trigger: The `commit()` header comment justifies the "not rolled back" rule using `updateRefPublishedAt` (autocommit one-shots on a committed part) as the motivating case, but the mutable-per-part path this comment referenced was deleted from `writeFile` (`:844-850` explicitly notes "the former mutable-per-part-file branch ... is DELETED"). The invariant is still correct, but the reader is directed to look for a code path that no longer exists.
- Severity: Low (doc/comment drift, not behavior).

### NEW-bc3-2 (Low, hardening) — Repoint-only failure mid-transaction has no rollback and no distinct log/metric
- Anchor: `ContentAddressedTransaction.cpp:381-393` (repoint branch — `oc.created` is always `false` here per line 382 comment).
- Trigger: A transaction that ONLY repoints already-committed refs (e.g. same-transaction inline metadata updates on multiple committed parts) can commit part A's repoint durably, throw on part B's repoint, and — because both outcomes are `created=false` — the compensating loop drops nothing. This is the deliberate contract, but there is no distinct signal (metric, log) that a partial repoint has become durable; operators only see the top-level exception. BC3-6's new metric fires only when a `created=true` rollback fails, not when a `created=false` repoint partial-commits.
- Notes: Adjacent to CAS-097 rather than a new class; consider emitting a diagnostic when `commit()` fails with ≥1 successful `created=false` outcome already in `part_outcomes`.

## By-design / N/A / info

- Multi-ref atomicity remains a documented wiring-layer compromise (`:459-466`), not an invariant violation of the CAS pool. Widening to a durable move-journal / auto-re-drive is orthogonal to this audit and tracked under CAS-022.
- S3 staging objects belonging to an aborted transaction intentionally survive to the mount-lease sweeper (`:186-206`) — not a leak.
- Destructor's `abandon()` throw is caught and `tryLogCurrentException`'d (`:130-138`); a failed abandon can leave a live-epoch precommit binding until remount, but this is diagnosable, matching BC3-5 semantics.

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-021 (BC3-1) | Med | 🔴 still-present | `ContentAddressedTransaction.cpp:458-513` |
| CAS-097 (BC3-2) | Low | 🔴 still-present (re-scoped: mechanism changed, contract unchanged) | `ContentAddressedTransaction.cpp:468-472`, `:338-393` |
| CAS-097 (BC3-3) | Low | 🔴 still-present | `ContentAddressedTransaction.cpp:494-513` |
| BC3-4 | Info | ⚪ info (still holds ✅) | `ContentAddressedTransaction.cpp:400-413`, `:344-359` |
| BC3-5 | Info | ⚪ info (still holds ✅) | `ContentAddressedTransaction.cpp:107-140`, `:165-210` |
| CAS-021 (BC3-6) | Low | ✅ fixed | `Parts/PartFolderAccess.cpp:646-707` |
| NEW-bc3-1 | — | 🔴 new (Low, doc drift) | `ContentAddressedTransaction.cpp:471-472` |
| NEW-bc3-2 | — | 🔴 new (Low, hardening) | `ContentAddressedTransaction.cpp:381-393` |

**Counts:** still-present = 3 (BC3-1 / BC3-2 / BC3-3, all folded into CAS-021 / CAS-097); fixed = 1 (BC3-6); info-holds = 2 (BC3-4, BC3-5); new = 2 (NEW-bc3-1 doc drift, NEW-bc3-2 partial-repoint diagnostic gap).

**Verdict:** the exception-safety story is now materially stronger. The two structural improvements — `dropRefIfMatches` (precise, no-clobber, `noexcept`) and immediate outcome capture in `publishStaging` — jointly close BC3-6 and the "later throw loses the outcome" seam that was implicit in the original write-up. The multi-ref non-atomicity (BC3-1) remains a documented compromise; the residual "commit failed ≠ no durable effect" (BC3-2) survives because repoint of a pre-existing ref is fail-closed-preserved by design. Actionable follow-ups are minor: fix stale `updateRefPublishedAt` comment; emit a signal when a mixed new-ref/repoint commit partial-commits on the repoint side.
