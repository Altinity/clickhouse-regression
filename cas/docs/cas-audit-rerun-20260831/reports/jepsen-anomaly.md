# jepsen-anomaly -- fresh audit 2026-08-31

## Scope

- Cross-node anomalies only (G1a / G1b / G-single / dirty read / lost update / split-brain)
  over refs, mount leases, GC leadership, FREEZE/shadow namespaces (now `server_root_id`
  scoped), and the relink confirm. Pin `ceee42c51a06cb05e2c9a2d811ef7e1726825552`.
- Files/dirs examined: `ContentAddressedMetadataStorage.cpp` (`liveNamespace` /
  `shadowNamespace` / `ownsNamespace` / `confirmExactRef` / `prepareAdoptFromManifest`),
  `ContentAddressedTransaction.cpp` (`commit` / `publishStaging`), `Pool/CasRefLedger.cpp`
  (`resolveRef` / `confirmExactRef` / `commitRefChunk`), `Pool/CasPartWriteTxn.cpp`
  (`precommitAdd` / `promote` / `ensureBlobPresent`), `Pool/CasServerRoot.cpp` (mount claim),
  `Pool/CasMountRuntime.cpp` (fence), `Pool/CasRefCkpt.cpp`, `Gc/CasGc.cpp`
  (`acquireOrRenewLease` / fold intake / `cleanupRefObjects`),
  `src/Storages/MergeTree/DataPartsExchange.cpp` (publish-then-confirm).
- Explicitly out of scope: in-process races (`concurrency`), two-actor operation pairs
  (`interleaving`), crash-atomicity of a single writer (`crash-consistency`).
  `Mode::EmulatedSingleProcess` is tests / local development only.

## Findings

### jepsen-anomaly-1 -- G1a / G1b / G-single: a multi-ref commit publishes one ref at a time (Medium)

- Anchor: `ContentAddressedTransaction.cpp:482-536` (`commit`) at ceee42c
- Trigger: one `ContentAddressedTransaction` stages two or more parts (reachable:
  `FREEZE` of several parts, `ATTACH`/`REPLACE PARTITION` cloning several parts through
  one disk transaction, a merge-plus-sidecar publish). `commit` calls `publishStaging`
  serially. After part *k* has promoted and before part *k+1* finishes:
  1. A peer fetch/relink, or a restart that recovers the namespace, can resolve and read
     the already-promoted refs (`CasRefLedger::resolveRef` returns only
     `state.getCommitted()`, `:322-324`). That is **G1b** (committed prefix of an
     in-flight multi-object txn) and **G-single** (a later read of the not-yet-published
     sibling misses it).
  2. If `publishStaging` then throws, the catch drops only outcomes with `created==true`
     via `dropRefIfMatches` (`:533-536`). A `kill -9` skips that catch. The prefix stays
     committed while the caller is told the transaction failed — **G1a**.
- Evidence: the function comments state the contract (`:482-490`): there is no multi-ref
  atomic publish; rollback is best-effort and in-process only. Each `promote` is its own
  ref-log append + `_ckpt` frontier (`CasRefLedger.cpp:3750-3771`). A remote replica does
  not participate in the in-process rollback. `dropRefIfMatches` is also not crash-safe:
  it is not a journaled compensation record.
- Notes: same residual as CAS-005 (no multi-ref atomicity). MergeTree's common INSERT is
  one part per transaction, so the realistic triggers are multi-part DDL/clone/freeze.
  Fail-closed on a single-part promote is unchanged (`PartWriteTxn::promote` `:740-745`,
  `:805-827`). Not High: no silent swap of committed bytes; the anomaly is a visible
  prefix / aborted-but-durable subset.

## By-design / info / non-actionable

- **FREEZE / shadow is no longer a shared register.** `shadowNamespace` is
  `serverPrefix() + "/" + canonicalDiskPath(...)` (`ContentAddressedMetadataStorage.cpp:1356-1361`),
  matching `liveNamespace` (`:1342-1347`). `ownsNamespace` requires
  `root_namespace.starts_with(server_root_id + "/")` (`:2096-2098`). Two mounts with
  distinct `server_root_id`s cannot dual-write one shadow ref table. The 2026-08-12
  High split-brain (pool-global `shadow/<backup>/…`) is gone.
- **Dirty read of a precommit is not admitted.** `resolveRef` and `confirmExactRef` both
  consult `getCommitted()` only (`CasRefLedger.cpp:322-324`, `:490-493`). A durable
  precommit is invisible to readers and to a `Yes`. `confirmExactRef` additionally
  refuses `Yes` unless the lane is quiescent (`pending.empty()`, `!leader_active`,
  `lane_state == Ready`, `:480-481`) and the mount fence still holds (`:503-506`).
- **Lost update on a ref is not admitted under distinct sriDs.** Append ids are
  `(writer_epoch, ref_sequence)` write-once keys. A live second mount of the *same*
  `server_root_id` is refused (`CasServerRoot.cpp:1011-1015`). A foreign occupant at
  the derived id faults the lane (`CasRefLedger.cpp:3720-3745`) rather than adopting
  foreign bytes.
- **Relink confirm does not authorize a dirty or fenced source.** Gate 1 is zero-I/O
  and fail-closed to `Unknown` (`CasRefLedger.cpp:408-508`). The receiver publishes
  its `+1` before asking (`ContentAddressedMetadataStorage.cpp:2303-2308`); a `Yes`
  is only the sender's assertion that *its* committed binding still names that
  `ManifestRef`. The documented LIST-as-journal hole (`DataPartsExchange.cpp` /
  `_sab_holeylist`) is a fold-visibility residual, not a confirm-primitive false
  `Yes`. It is not re-scored here.
- **Mount-lease split-brain is not admitted.** Claim is `NoWait` refuse of a live
  foreign/twin lease; steal of a slot requires a fenced/clean/token-stable certificate.
  Worker renewals require `MountLeaseKeeperState::Active` (`CasMountRuntime.cpp:339-340`).
- **GC dual-leader does not admit a lost update of the delete set.** Steal requires
  a frozen `(owner, seq)` *and* a frozen heartbeat pair across a full scheduler
  interval (`CasGc.cpp:4439-4464`). Destructive ref cleanup re-reads the catalog
  token and `gc/state` before each `deleteExact` (`:3275-3308`). A deposed leader's
  fold evaporates at the single `gc/state` CAS (`:3195-3198`). Heartbeat `casPut`
  remains advisory (`pulseHeartbeat` `:4357-4370`); that is liveness, not a second
  delete authority.

## Closed-since-2026-08-12

- **jepsen-anomaly-1 (High, FREEZE pool-global shadow namespace).** Closed by
  `335802a938f`: `shadowNamespace` / `shadowScope` now prefix `serverPrefix()`.
  `UNFREEZE` on server A cannot drop server B's frozen refs.
- **jepsen-anomaly-5 (Medium, GC lease not a fencing token on the delete path).**
  Not re-raised. HEAD revalidates catalog + `gc/state` before ref-object deletes;
  blob deletes are exact-token `delete_pending` from a prior adopted round. Residual
  is liveness of steal (no wall-clock TTL), which is design (CAS-003).

## Coverage

- Reviewed: G1a, G1b, G-single, dirty read, lost update, split-brain / dual writer
  on ref log + `_ckpt`, mount lease, writer epoch, GC lease/state + `gc/hb`,
  FREEZE/shadow namespaces, relink confirm + publish-then-confirm.
- N-A: emulated-backend cross-process linearizability (documented single-process).
- Deferred: TLA `_sab_holeylist` fold-miss of a receiver `+1` (named in
  `DataPartsExchange.cpp`; owned by gc-protocol / tla-fidelity).
