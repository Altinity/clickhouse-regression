# tier3 -- fresh audit 2026-08-31

## Scope
Tier3 in this re-run is **failure-injection surfaces that remain unhandled**: ambiguous writes, fence loss, catalog churn.

- Files/dirs examined: `Pool/CasPartWriteTxn.cpp` (`ensureBlobPresent` HEAD → adopt / publish loop, 8 publication attempts, fence checks), `Backend/CasObjectStorageBackend.cpp` (`publishBlob` streaming vs `copyObject`), `Backend/CasRequestControl.cpp`, `Pool/CasMountRuntime.cpp` (`scheduleRemount`, `checkFenceOrThrow`, Active-keeper admission at HEAD `ceee42c`), `Pool/CasRefCatalog.cpp` (`casUpdateImpl` retry), `Tools/CasDecommission.cpp` (incarnation change refuse), `ContentAddressedTransaction.cpp` (`cleanupPendingTempFiles`), `Pool/CasEventDispatcher.cpp` (not a protocol surface).
- Explicitly out of scope: inventing consequences for the new unconditional-publish-after-HEAD design; GC fold internals.

## Findings
### tier3-1 -- an aborted S3-staging write is invisible to GC and unreclaimed until the next mount of the same srid (Medium)
- Anchor: `ContentAddressedTransaction.cpp:167-196` (S3 pending blobs deleted only `if (committed)`; abort leaves them for `sweepOwnMountStaging`); sweeper is mount/decommission scoped, not a GC phase.
- Trigger: `cas_staging_backend=s3` and `KILL MUTATION` / cancelled merge after blobs reached staging and before `commit()`.
- Evidence: local scratch is removed on abort; S3 staging is intentionally kept as a re-readable publication source. There is still no in-mount periodic sweeper and no `system` row that lists stranded staging keys. Repeated kills accumulate bucket cost. Fail-closed (no data loss). Same residual as CAS-081.
- Notes: CAS-081.

## By-design / info / non-actionable
- **Ambiguous blob publish is handled.** `ensureBlobPresent` HEADs, adopts a present non-condemned body, else publishes (copy or stream) under a fresh envelope, retries up to 8 times, then `throwCasWriteRetryLater` (`CasPartWriteTxn.cpp:327-436`). Remaining-ambiguous is loud, not silent success.
- **Unconditional publish after HEAD-absent is the written protocol** (`940b1685bf9`). A concurrent winner at the same content key is adopted on the next HEAD or overwritten with an equivalent payload + new envelope. Not an unhandled hole.
- **Fence loss is checked** after the mandatory HEAD and before durable meta/publish (`checkFenceOrThrow(admitted_generation)`). Worker renewals require an Active keeper (`ceee42c51a0`). `scheduleRemount` is a driver-state machine (`CasMountRuntime.cpp:1072-1084`), not the old "latch before spawn" disable-forever path.
- **Catalog churn on decommission is handled.** Selection is an immutable catalog cut; a later incarnation change throws `CORRUPTED_DATA` and refuses destructive work (`CasDecommission.cpp:164-175`). `casUpdateImpl` re-GETs on conflict (`CasRefCatalog.cpp:120-131`).
- Empty conditional tokens: no production call site constructs one (CAS-010). Not re-raised.

## Closed-since-2026-08-12
- `promoteStaged` / `conditionalCreateControlled` / `copyObjectConditional` gone; ambiguous create is no longer a separate primitive.
- CAS-070 remount-spawn latch: remount is now a parked driver, not "set remount_running then createThread".
- Detached work drained at shutdown (`205af29c7f2`) — released Context no longer races injected failures on teardown.

## Coverage
- Reviewed: blob publish retry/ambiguity, fence checks, remount driver, catalog CAS retry, decommission incarnation guard, S3 staging abort residue.
- N-A: inventing a split-brain from unconditional publish of identical content.
- Deferred: runtime fault injection of HEAD-then-loss-then-copy.
