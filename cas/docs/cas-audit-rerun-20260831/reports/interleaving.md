# interleaving -- fresh audit 2026-08-31

## Scope

- Operation pairs across concurrent actors that each perform durable transitions
  on a shared pool: two servers, one pool; `SYSTEM CAS DROP POOL MEMBER` vs a
  live nested `server_root_id`; `UNFREEZE`; `MOVE PARTITION`; concurrent
  INSERT + GC. Pin `ceee42c51a06cb05e2c9a2d811ef7e1726825552`.
- Files/dirs examined: `Tools/CasDecommission.cpp`, `Pool/CasServerRoot.h`
  (`validateServerRootId`), `Pool/CasPool.cpp` (`openForDecommission`),
  `Formats/CasLayout.h` (`casManifestsServerPrefix` / `serverRootDataPrefix`),
  `ContentAddressedMetadataStorage.cpp` (`shadowNamespace` / `ownsNamespace`),
  `ContentAddressedTransaction.cpp` (`removeDirectory` UNFREEZE /
  `moveDirectory`), `Gc/CasOrphanManifestSweep.cpp` (`floorForNamespace`),
  `Gc/CasGc.cpp` (fold intake, two-phase graduation, `cleanupRefObjects`),
  `Pool/CasPartWriteTxn.cpp` (EDGE-BEFORE-OBSERVE),
  `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp` (`freezeRemote`),
  `src/Storages/MergeTree/MergeTreeData.cpp` (MOVE / FREEZE / UNFREEZE
  admission).
- Explicitly out of scope: in-process thread races (`concurrency`);
  crash-atomicity of one actor (`crash-consistency`); linearizability of a
  single register (`jepsen-anomaly`).

## Findings

### interleaving-1 -- DROP POOL MEMBER on `a` destroys live member `a/b` (Medium)

- Anchor: `Tools/CasDecommission.cpp:143-157,219-242,253-258`;
  `Pool/CasServerRoot.h:76-106` (`validateServerRootId`);
  `Formats/CasLayout.h:429-431` (`casManifestsServerPrefix`), `:422-424`
  (`serverRootDataPrefix`) at ceee42c
- Trigger: two writable mounts in one pool, `cas_server_root_id` `a` and
  `a/b`. Both pass `validateServerRootId` (slashes are allowed; the check
  rejects only empty / `.` / `..` / `_files` / `_manifests` segments). An
  operator runs `SYSTEM CAS DROP POOL MEMBER` for `a` while `a/b` is live.
  `openForDecommission` succeeds because `a` has an owner/mount
  (`CasPool.cpp:842-851`).
- Evidence: catalog selection keeps every row whose namespace equals `a` *or
  starts with* `a/` (`:146-151`). That includes `a/b/store/…` and
  `a/b/shadow/…`. Each selected life is `dropNamespace`d (`:194`). Physical
  drains use string prefixes that also contain the child:
  - `casManifestsServerPrefix("a")` = `…/cas/manifests/a/` lists
    `…/cas/manifests/a/b/…`
  - `staging/a/` lists `staging/a/b/`
  - `serverRootDataPrefix("a")` = `…/roots/a/` lists `…/roots/a/b/`
  The `victim` vs `victim2` slash fix (`:143-145`) does not separate a
  nested path component. `floorForNamespace` already walks longest prefix
  (`CasOrphanManifestSweep.cpp:39-64`) and would treat `a` and `a/b` as
  distinct mounts — decommission does not.
- Notes: same root cause as CAS-007. Consequence is deletion of a live
  member's namespaces, manifests, staging, and mountpoint objects. Scored
  Medium (not High): the validator advertises nested ids, but the trigger
  requires an operator to configure a parent *and* a child srid and then
  decommission the parent. `a` vs `a2` is already excluded.

## By-design / info / non-actionable

- **Two servers, one pool, disjoint sriDs are fenced.** Live and shadow
  namespaces are `server_root_id + "/" + …`
  (`ContentAddressedMetadataStorage.cpp:1342-1361`). Mount claim refuses a
  live twin of the same srid. GC fold is checkpoint-bounded per life and
  two-phase on blobs (condemn → `delete_pending` → exact-token delete).
- **UNFREEZE is now server-root scoped.** `removeDirectory` of a shadow
  path calls `dropNamespace(shadowNamespace(path))`
  (`ContentAddressedTransaction.cpp:1080`). That namespace includes
  `serverPrefix()`, so `UNFREEZE` on A cannot drop B's `shadow/<name>/…`
  refs. Repeated `FREEZE WITH NAME` merging two snapshots into one ref is
  a same-server POSIX-rename residual (CAS-086), not a cross-node
  interleaving.
- **MOVE PARTITION TO TABLE / cross-disk clone has a CA transaction.**
  `freezeRemote` wraps the clone in one `DiskTransaction` when the
  destination is content-addressed (`DataPartStorageOnDiskBase.cpp:687-744`).
  Same-pool publish is absorbed by the post-precommit HEAD adopt
  (`PartWriteTxn::ensureBlobPresent`). Two CA disks with the *same* srid
  cannot both mount (CAS-024). Cross-disk `MOVE … TO DISK` is still a
  sequential byte copy plus dest publish; a crash mid-partition leaves a
  prefix of parts on the dest — ordinary MergeTree move semantics, not a
  CAS-specific dual-write.
- **INSERT + GC: EDGE-BEFORE-OBSERVE plus two-phase graduation.**
  `ensureBlobPresent` refuses to materialize before
  `PrecommitState::Durable` (`CasPartWriteTxn.cpp:257-261`). Fold intake
  stops at `_ckpt.committed_through` (`CasGc.cpp:2284-2298`), so an
  uncheckpointed precommit is not folded — and is also not treated as
  absent-of-hold in a way that licenses deletion of a blob the previous
  coverage still names. Graduation publishes `delete_pending` one round
  and exact-deletes the next (`:633-649`, `:783-797`). A concurrent
  INSERT that HEADs a condemned blob republishes (`:389-468`). No
  confirmed window in which GC deletes a blob a live precommit or
  committed ref still names.

## Closed-since-2026-08-12

- **interleaving-1 (High, pool-global shadow / FREEZE dual writers).**
  Closed by `335802a938f` (same close as jepsen-anomaly-1 / CAS-001).
- **interleaving-2 (Medium, non-srid-prefixed namespaces have no watermark
  floor).** Closed for FREEZE/shadow: those namespaces now carry
  `server_root_id`, so `floorForNamespace` longest-prefix match finds the
  mount lease. Residual nested-srid *decommission* prefix is
  interleaving-1 above, a different actor.

## Coverage

- Reviewed: two servers / one pool (live + shadow + mount + GC);
  `DROP POOL MEMBER` vs nested srid (catalog + LIST prefixes + staging +
  roots); UNFREEZE; MOVE PARTITION / `freezeRemote`; INSERT + GC
  (precommit-before-observe, ckpt-bounded fold, condemn/graduate).
- N-A: `EmulatedSingleProcess` two-process sharing (documented unsafe).
- Deferred: TLA `_sab_holeylist` relink+GC fold miss (named in
  `DataPartsExchange.cpp`; gc-protocol / tla-fidelity).
