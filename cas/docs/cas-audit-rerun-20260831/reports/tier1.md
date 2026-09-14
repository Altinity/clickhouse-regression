# tier1 -- fresh audit 2026-08-31

## Scope
Tier1 in this re-run is the **must-work happy path**: INSERT, SELECT, merge, replica relink, GC, FSCK. Only confirmed blockers (realistic trigger → the verb cannot complete correctly on a default CAS disk).

- Files/dirs examined: write path `ContentAddressedTransaction::writeFile` / `publishStaging` / `CasPartWriteTxn::ensureBlobPresent` / `promote`; read path `getView` / `getBlobViewPlan` / `tryGetInManifestBytes`; merge tmp→final in-transaction rename; `DataPartsExchange.cpp` relink (`ownsNamespace` + `confirmExactRef`); `Gc/CasGc.cpp` regular round + `CasOrphanManifestSweep` skip of undecodable manifests; `Tools/CasFsck.cpp`.
- Explicitly out of scope: admin verbs (tier2), failure-injection residuals (tier3), scale/cost (tier4/performance), encryption, unique-key (no production caller).

## Findings

No confirmed happy-path blockers on `ceee42c`.

Default INSERT/SELECT/merge of Wide or Compact parts complete: `.bin` streams as blobs; Compact `data.cmrk4` and `primary.cidx` take the inline path and stay under the 16 MiB cap for ordinary schemas. Relink is offered only inside one mounted pool and confirms an exact `ManifestRef`. GC no longer wedges the pool on an undecodable manifest (`2649bce42db`). FSCK enumerates reachable refs and reports `unaccounted` / dangling without being a write-path dependency.

Schema-dependent loud failures (16 MiB inline total, RAM buffer of a huge skip index) are not default-path blockers; they are recorded in `mergetree-part-support` / `datatype-agnosticism`.

## By-design / info / non-actionable
- Dedup HEAD after durable precommit, then adopt a present non-condemned body or publish under a fresh envelope (`CasPartWriteTxn.cpp:254-387`).
- Zero-copy replication stays off; relink is the intra-pool substitute.
- `part_folder_validate=always` adds a HEAD per ForceFresh view; SELECT of a warm `CachedForLoad` view does not rebuild the ref table.

## Closed-since-2026-08-12
- CAS-040 GC wedge on a `\n` projection name (`2649bce42db` + escaped banners).
- CAS-001 FREEZE isolation (not a tier1 verb; noted because UNFREEZE no longer deletes another replica's blobs that INSERT/merge still share).
- Worker renewals admitted only over an Active keeper (`ceee42c51a0`) — removes a class of "writes while the mount is not live" that could have blocked the happy path.

## Coverage
- Reviewed: INSERT write/commit, SELECT read plan, merge publish, relink confirm, GC round admission + orphan skip, FSCK entry points.
- N-A: admin verbs, encryption wrapper, unique-key bitmaps.
- Deferred: runtime INSERT/merge of a pathological JSON Compact part against the 16 MiB cap.
