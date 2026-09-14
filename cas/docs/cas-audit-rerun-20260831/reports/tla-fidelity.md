# tla-fidelity -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `Pool/CasPartWriteTxn.{h,cpp}` (`requireAlive`, `ensureBlobPresent`, `precommitAdd`, `promote`, `adoptEvidence`, `abandon`), `ContentAddressedTransaction.cpp` (EDGE-BEFORE-OBSERVE comments + fan-out), `Pool/CasMountRuntime.cpp` (Active-keeper admit), `Pool/CasServerRoot.cpp` / `Formats/CasServerRootFormats.cpp` (mount lease + `write_attempt_id`), `Pool/CasRefLedger.cpp` / `Pool/CasRefProtocol.{h,cpp}` (ref-log CAS, confirmExactRef), `Gc/CasGc.cpp` (lease acquire, fold, pending_deletes, ref cleanup, janitor, rebuild), `Gc/CasBlobInDegree.cpp` (graduation / confirm-before-delete_pending), `src/Storages/MergeTree/DataPartsExchange.cpp` (publish-then-confirm), `ContentAddressedMetadataStorage.cpp` (`prepareAdoptFromManifest`).
- Explicitly out of scope: inventing a TLA+ spec; `docs/en/antalya/cas/**` as proof of enforcement. The left-hand side is only invariants the code names in shipped exception/log strings or in the predicate that implements them.

Named invariants checked: `requireAlive`; EDGE-BEFORE-OBSERVE; `WPromote owner==bld`; unique-ref; confirm-before-promote (relink); confirm-before-graduate (`confirm_condemned_marker`); GC lease revalidate before ref/janitor delete; worker renewals only over an Active keeper.

## Findings

None. On the production call sites that claim these predicates, the guard is present and fail-closed. Residuals that the 2026-08-12 report treated as bypasses are either by-design (CAS-002/003/008) or closed by later commits.

## By-design / info / non-actionable
- **`requireAlive` is the write-txn fence.** `PartWriteTxn.cpp:165-184` fails closed if abandoned, if `dropNamespace` cancelled the build, or if `epoch != liveWriterEpoch()`. Production mutators call it: `ensureBlobPresent` (`:256`, again in the publish loop `:330`), `adoptEvidence` (`:476`), `stageManifest` (`:513`), `precommitAdd` (`:614`), `promote` (`:727`), `abandon` (`:1016`). The cancelled-`abandon` arm (`:979-1013`) skips it on purpose: the removal txn already dropped every precommit. `mergeBlobUploadResults` does not call it; it only folds results whose `ensureBlobPresent` already did. CAS-129's "called from one site" claim is false on this pin.
- **EDGE-BEFORE-OBSERVE is a hard gate on the new publish protocol.** `ensureBlobPresent` (`:257-261`) throws `LOGICAL_ERROR` unless `precommit_state == Durable`. Blob work is: durable precommit → HEAD → adopt present non-condemned body, else unconditional publish under a fresh envelope (`:327-468`). Promote (`:810-813`) then treats `Materialized` leaves as edge-protected and does not re-HEAD them. That is the invariant the string names, not a second observe.
- **`WPromote owner==bld` and unique-ref are enforced inside the ref-log CAS closure.** Promote (`:803-808`) refuses if the precommit binding is gone; (`:874-880`) refuses a different committed manifest unless `allow_repoint`. Idempotent same-manifest re-promote is a no-op (`:787-789`).
- **Confirm-before-promote is the relink handshake.** Sender offers relink only if the client advertised `REPLICATION_PROTOCOL_VERSION_WITH_CA_CONFIRM` (`DataPartsExchange.cpp:404`). Receiver: T1 `prepareAdoptFromManifest` (durable +1) → T2 confirm → T3 `promote` (`:1457-1556`). Empty source token, unproven cookie, or confirm transport failure all refuse promote. The file's own comment (`:1383-1387`) states that a `yes` is **not** a dangle-free proof (holey LIST); that is a documented limit of what the invariant claims, not a failed enforcement of confirm-before-promote.
- **`adoptEvidence` still skips HEAD/meta.** `PartWriteTxn.cpp:474-488` records `TrustedManifest` with no backend call. Filimonov CAS-002: §4 manifest-trust, fsck backstop. `requireAlive` is now on this path; that is the only change. Not a new bypass.
- **GC lease is revalidated on catalog/ref/janitor deletes, not on prior-round blob `delete_pending`.** Janitor (`CasGc.cpp:327-334`) and `cleanupRefObjects` (`:3301-3316`) re-GET `gc/state` and stop if owner/seq moved. `pending_deletes` (`:666-668`) is exact-token delete of rows a **previous** committed pass published as `delete_pending`; the file claims that is safe at any leader staleness. Filimonov CAS-003: "destructive phases are never revalidated" is false; liveness-only residual. Still the design.
- **Confirm-before-graduate is live on the regular fold.** `confirm_condemned_marker` (`CasGc.cpp:1751-1778`) requires in-process or durable `Condemned` meta; missing evidence carries and retries the marker, never graduates. `foldDeltasIntoGeneration` (`CasBlobInDegree.cpp:489`) still treats an empty callback as "confirmed" (`!confirm_condemned_marker || …`). Regular fold always passes the lambda (`CasGc.cpp:3026`, `:3068`). Rebuild (`:3987-3991`) passes `{}` **and** `current_round=0`, so it graduates nothing (edge-only, stated in-file). No production graduation site omits the callback. Missing fail-closed default only — same class as CAS-010, not a proven path.
- **Mount-lease workers require an Active keeper.** `CasMountRuntime.cpp:599-600` (this pin: `ceee42c`). `decodeMountLease` (`CasServerRootFormats.cpp:178-179`) requires a non-zero `write_attempt_id`. Renew/release refuse non-Active state (`CasServerRoot.cpp:1642`, `:1861`).
- **Ref-log append is fenced.** Durable append uses the request controller plus `admitted_fence_generation` / `checkFenceOrThrow` (CAS-129). Empty-token `If-Match` has no production mint (CAS-010).
- **No-rehash on adopt/publish is CAS-008, not an EDGE-BEFORE-OBSERVE hole.** Size is checked; digest is not recomputed. By design.

## Closed-since-2026-08-12
- **tla-fidelity-1** (vacuous graduation when callback omitted): regular fold always supplies `confirm_condemned_marker`; rebuild is edge-only with `current_round=0`. The fail-open default remains but has no graduating caller.
- **tla-fidelity-2** (no lease revalidate on destructive GC): ref cleanup and namespace janitor now revalidate owner+seq before `deleteExact`. Blob `delete_pending` deletes stay prior-round / exact-token by stated design (CAS-003), not a remaining bypass of a claimed revalidate-every-delete invariant.
- **tla-fidelity-6** (staged-manifest cleanup can delete a live precommit body): `cleanupStagedManifestDebrisBestEffort` (`PartWriteTxn.cpp:1117-1145`) skips the manifest once `precommit_state != NotAttempted`, including `Uncertain`.
- **requireAlive / epoch** (CAS-129): seven production call sites; superseded-epoch fails closed.
- **Unconfirmed relink promote:** closed by protocol 11 + token cookie + `CA_CONFIRM_ANSWER_PROVEN` only.
- **Worker renewal on a non-Active keeper:** closed by `ceee42c51a0`.
- Previous tla-fidelity-3 (REBUILD drops condemn universe) is still the rebuild contract (CAS-025, by design), not an enforcement miss.
- Previous tla-fidelity-7 (no re-hash) is CAS-008, by design.

## Coverage
- Reviewed: mount-lease claim/renew/release + `write_attempt_id` + Active-keeper admit; ref-log promote/precommit/abandon CAS closures; blob admit (HEAD → adopt or unconditional publish) vs EDGE-BEFORE-OBSERVE / `requireAlive`; GC lease acquire, fold graduation gate, pending_deletes, ref-cleanup revalidate, janitor revalidate, rebuild edge-only fold; relink T1/T2/T3.
- N-A: a standalone `.tla` model (none outside `contrib/`; the holey-LIST comment cites `CaRelinkConfirmCore.tla` as a limit, not as a spec this audit diffs against).
- Deferred: full ref recovery walk (`runRecoveryWalkOnce` / `_ckpt` join) beyond the `requireAlive` / fence sites already named.
