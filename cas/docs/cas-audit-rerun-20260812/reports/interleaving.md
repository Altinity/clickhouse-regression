# interleaving -- fresh audit 2026-08-12

## Scope

Static, code-only audit of **operation pairs across concurrent actors** in
`/Volumes/workspace/altinity-clickhouse/ClickHouse` (branch `cas-code-only-strip`, base `842f2b37b8f`,
working tree as-is), CAS root `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`.
All paths below are relative to that root unless prefixed otherwise.

In scope: interleavings between *separate* actors that each perform durable state transitions on the
shared object store -- a second server in the same pool, the GC leader, the namespace janitor, DDL, the
relink/fetch receiver, mount claim/renew/reclaim. Out of scope: races between threads inside one
process (that is the `concurrency` audit), and pure crash-atomicity (that is `crash-consistency`).

Code-only rule observed: `docs/**` and comments are not treated as evidence of intent; shipped log /
exception strings are treated as admissible statements of shipped behaviour.

Already found by sibling audits, cited but not re-reported: `adoptEvidence` bypasses the condemn
marker; no pin is held across the blob GET; `repointRef` is unrevertible; the GC lease has no TTL.

## Actors and durable transitions

**writer A / writer B (INSERT, merge, FREEZE, ATTACH publish)** -- one mount per `server_root_id`.
- `allocateBuildSeq()` bumps the per-mount build watermark (`Pool/CasMountRuntime.cpp:148`), which is
  published into the mount lease's `min_active`.
- blob PUT: `PartWriteTxn::putBlob` / `uploadFromSource` (`Pool/CasPartWriteTxn.cpp:131`, `:307`),
  admission of an already-present blob via `observeAndAdmit` (`:240`, `:250`), tokenless adoption via
  `adoptEvidence` (`:478`, sibling finding).
- manifest body PUT at `cas/manifests/<ns>/<epoch>-<build_seq>/<ordinal>`:
  `PartWriteTxn::stageManifest` (`:507`), key derivation `Formats/CasLayout.h:139-145`.
- ref-log append (the only ref-visible durable transition): `precommitAdd` (`:576`) then
  `promote` (`:633`), each landing an immutable `cas/ns/stream/<life>/_log/<epoch>-<seq>` object
  through `commitRefChunk` (`Pool/CasRefLedger.cpp:2245`).
- checkpoint / snapshot publication: `publishCkptContribution` (`Pool/CasRefLedger.cpp:2916`),
  `tryPublishSnapshotAndAdvanceCheckpointOnce` (`:2930`).
- namespace catalog transitions `absent -> Creating -> Live`: `resolveNamespaceLife`
  (`Pool/CasRefLedger.cpp:866-954`).

**DDL (DROP / RENAME / DETACH / ATTACH / TRUNCATE)** -- runs on the writer's process but is a distinct
actor with respect to GC and to the janitor.
- `removeRecursive` / `removeDirectory` -> `dropNamespace` -> catalog `Live -> Removing`, terminal
  removal ref-log record, then catalog removal (`Pool/CasRefLedger.cpp:3391`, `:3396`, `:3601`).
- RENAME across table UUIDs: per-ref `republishRef` + namespace-file copy + `dropNamespace(from_ns)`
  (`ContentAddressedTransaction.cpp:846-885`).
- single-file mutations on committed parts: `repointRef` (`Parts/PartFolderAccess.cpp:442`),
  `unlinkFile` (`ContentAddressedTransaction.cpp:1069`), `replaceFile` (`:1058`).

**GC leader** -- `Gc::runRegularRound` (`Gc/CasGc.cpp:415`).
- heartbeat floor: fences dead server roots (`Gc/CasGc.cpp:466-503`).
- fold: ref-log intake bounded by the checkpoint-committed frontier, emitting blob in-degree deltas
  (`Gc/CasGc.cpp:1229`, intake loop `:1640-1825`).
- fold seal write (durable round artifact) `putDeterministicArtifact(... foldSealKey ...)`
  (`Gc/CasGc.cpp:2245-2254`).
- condemn marker write / graduation to real deletion (`Gc/CasGc.cpp:352`, `:362`, `:368`, `:374`,
  graduation predicate `:2534-2559`).
- ref-object cleanup (superseded logs/snaps) `Gc::cleanupRefObjects` (`Gc/CasGc.cpp:2288`).
- catalog reconcile of completed removals `Gc::drainCompletedRemoving` (`Gc/CasGc.cpp:3195`).

**GC rebuild / fsck** -- `Gc::rebuildBaseline` (`Gc/CasGc.cpp:2623`), `Tools/CasFsck.cpp` (read-mostly,
plus `prefixEligible`-gated decisions at `Tools/CasFsck.cpp:890`).

**namespace janitor** -- `NamespaceJanitor::runOnePage` (`Gc/CasNamespaceJanitor.cpp:9-132`): lists
`cas/ns/`, reads the catalog cut, `deleteExact`s every object whose life id is not resolvable, then
CASes the janitor cursor.

**orphan manifest sweep** -- `Gc/CasOrphanManifestSweep.cpp:479-620`: lists `cas/manifests/`, then
per-prefix watermark eligibility `prefixEligible` (`:373-387`) which resolves the owning mount lease by
namespace-path prefix (`floorForNamespace`, `:37-57`).

**relink / fetch receiver** -- `getRelinkOffer` / `prepareAdoptFromManifest` /
`confirmExactRef` (`ContentAddressedMetadataStorage.cpp`, `Pool/CasRefLedger.cpp:298`), driven from
`src/Storages/MergeTree/DataPartsExchange.cpp`.

**mount claim / renew / reclaim** -- `MountLeaseKeeper::claim` (`Pool/CasServerRoot.cpp:764`), renew and
fence-out paths (`:844-920`), `armMountFence` / `checkFenceOrThrow` / `mayMutate`
(`Pool/CasMountRuntime.cpp:118`, `:90`, `:77`).

**reader** -- `resolveRef` + manifest read + blob GET; no durable transition, so it appears only as a
victim in the matrix.

## Interleaving matrix

| pair | hazard at the interleaving point | prevented by / admitted | anchor |
| --- | --- | --- | --- |
| writer publish vs GC condemn | blob uploaded, manifest staged, ref-log append not yet landed -> in-degree 0 -> condemned | **prevented**: the sweep/skip decisions require `prefixEligible`, and the writer registers `build_seq` in the mount lease `min_active` *before* staging; GC also lists manifests before reading the lease, so anything listed pre-dates the lease read | `Pool/CasMountRuntime.cpp:148`; `Gc/CasOrphanManifestSweep.cpp:373-387`, `:489` vs `:554` |
| writer publish vs GC delete | a ref-log record naming a manifest lands after the fold cut -> blob deleted while newly referenced | **prevented**: fold intake stops at the checkpoint-committed frontier and clamps (`hold`) on any manifest body it cannot read; deletion graduates only in a strictly later round than the condemn | `Gc/CasGc.cpp:1662-1703`, `:1757-1778`, `:2534-2559` |
| writer publish vs GC delete, adopt path | adopted blob was already condemned | **admitted** -- sibling finding (`adoptEvidence` bypasses the condemn marker); not re-reported here | `Pool/CasPartWriteTxn.cpp:478` |
| writer A vs writer B, same live namespace | two mounts appending to one ref-log | **prevented**: live namespaces are `server_root_id`-prefixed, and the per-srid mount slot admits one writer | `ContentAddressedMetadataStorage.cpp:886-889`; `Formats/CasLayout.h:228-231` |
| writer A vs writer B, same **shadow** namespace | shadow namespaces are *not* srid-prefixed -> two mounts share one ref-log id space and one manifest key space | **admitted** -- interleaving-1 | `ContentAddressedMetadataStorage.cpp:897-900`; `Pool/CasRefProtocol.cpp:418-423`; `Formats/CasLayout.h:139-145` |
| writer vs writer, namespace creation | both create the same catalog entry | **prevented**: catalog `Creating` reconcile requires the foreign creator fence to be provably dead, else refuse-and-retry | `Pool/CasRefLedger.cpp:880-948` |
| two writers on the same ref name (same srid) | lost update / divergent binding | **prevented**: ref ops are serialized per-namespace through the append lane and each append carries the exact `old_binding`; a foreign occupant at the derived id faults the lane | `Pool/CasRefLedger.cpp:2380-2448`, `:2472-2530` |
| stale writer (fenced-out) vs new writer | zombie append after lease loss | **prevented**: `putIfAbsentControlled` re-checks `fence_ok` and a successor's epoch seal conclusively rejects the transaction | `Pool/CasRefLedger.cpp:2259-2264`, `:2455`, `:2501-2516` |
| DDL drop vs writer publish | publish into a namespace being removed | **prevented**: a positive append re-reads the catalog and requires the *exact* life to be `Live`, else `retry later` + close the positive lane | `Pool/CasRefLedger.cpp:2313-2342` |
| DDL drop vs DDL drop / terminal append | two terminal removals, or a terminal append into a live lane | **prevented**: the terminal chunk requires exact removal ownership, a closed positive lane, and catalog state `Removing` | `Pool/CasRefLedger.cpp:2273-2311` |
| DDL drop vs adopt / relink receive | source ref dropped between offer and receiver commit | **prevented**: the receiver's precommit is durable before the source is confirmed, and `confirmExactRef` only answers on a quiet lane under the correct fence; adoption is refused across a namespace the mount does not own | `Pool/CasRefLedger.cpp:298`; `ContentAddressedMetadataStorage.cpp:1462` |
| DDL rename vs concurrent publish into the source ns | a ref published after `listRefs` is destroyed by `dropNamespace(from_ns)` instead of migrated | **admitted** -- interleaving-3 (only server-local DDL exclusion prevents it; CAS re-validates nothing) | `ContentAddressedTransaction.cpp:862`, `:874`, shipped string `:878-882` |
| DDL rename vs GC | source manifest `-1` folds before the destination `+1` (two different ref-logs, no cross-namespace atomicity) | **prevented**: `republishRef` publishes the destination *before* dropping the source, so blob in-degree never dips; a transiently condemned manifest is re-grounded before graduation | `Parts/PartFolderAccess.cpp:437-438`; `Gc/CasGc.cpp:2534-2559` |
| DDL vs GC round in progress | GC folds a namespace that DDL moves to `Removing` mid-round | **prevented**: the fold reads a catalog cut and `drainCompletedRemoving` only retires a life whose durable cursor covers its terminal record | `Gc/CasGc.cpp:2369-2371`, `:3195` |
| same-UUID table recreation | new life reuses the old namespace string -> ABA on ref-log / ckpt / files keys | **prevented**: every namespace object key is scoped by `incarnation`, and creation is refused while the old life is `Removing` | `Formats/CasLayout.h:75-83`; `Pool/CasRefLedger.cpp:895-902` |
| janitor vs namespace re-creation | janitor deletes objects of a life that has just been re-created | **prevented**: the listing is taken *before* the catalog cut, so a life born after the listing is not in the page and a life in the page is in the (fresher) catalog; `Creating` entries are catalog-named and therefore resolvable; deletes are `deleteExact` with the listed token | `Gc/CasNamespaceJanitor.cpp:25` vs `:35`, `:77`, `:105` |
| janitor vs janitor (two GC leaders; the lease has no TTL) | double delete, cursor skip | **prevented**: `deleteExact` is token-exact and the cursor is published with a CAS on the token read at page start | `Gc/CasNamespaceJanitor.cpp:105`, `:13` vs `:124` |
| checkpoint / snapshot publish vs concurrent append | a checkpoint advances past a record that the appender has not landed, or an append lands under a superseded runtime | **prevented**: both the ckpt contribution and the commit-frontier publication re-verify `admitted_fence_generation` and the runtime-retirement flags | `Pool/CasRefLedger.cpp:2407-2426`, `:2536-2543` |
| checkpoint vs GC ref-object cleanup | GC deletes a log/snap that the checkpoint still needs | **prevented**: cleanup is driven from the adopted fold seal's per-life durable cursor | `Gc/CasGc.cpp:2288`, `:2369-2371` |
| mount reclaim vs in-flight write | the reclaiming process sweeps the previous incarnation's staging while it is still writing | **prevented**: staging sweep runs only after `claim` succeeds, and `claim` requires token stability of a dead lease; the old incarnation trips `mount lost` and `mayMutate` refuses | `Pool/CasServerRoot.cpp:764`; `Pool/CasMountRuntime.cpp:77`, `:83`, `:90` |
| mount renew failure vs GC heartbeat floor | GC fences a srid that is actually alive | **prevented**: the floor is computed from durable heartbeats and the fenced writer's own renew path fails closed | `Gc/CasGc.cpp:466-503`; `Pool/CasServerRoot.cpp:732`, `:864` |
| orphan manifest sweep vs shadow-namespace writer | no mount lease resolves for a non-srid-prefixed namespace | **admitted** -- interleaving-2 (fails *closed* for deletion, but permanently) | `Gc/CasOrphanManifestSweep.cpp:37-57`, `:373-387` |
| reader vs GC delete | blob deleted between resolve and GET | **admitted** -- sibling finding (no pin across the blob GET); not re-reported here | -- |
| reader vs janitor | log/snap deleted under a recovery walk | **prevented**: only unresolvable (dead) lives are touched, and a live recovery walk resolves through the catalog | `Gc/CasNamespaceJanitor.cpp:77` |

## Findings

### interleaving-1 -- shadow/backup namespaces are pool-global, so two servers in one pool are unfenced concurrent writers on one ref table (High)

- **Anchor**
  - `ContentAddressedMetadataStorage.cpp:897-900` -- `shadowNamespace()` returns
    `RootNamespace{canonicalDiskPath(shadow_table_dir)}` with **no** `serverPrefix()`.
  - `ContentAddressedMetadataStorage.cpp:886-889` -- `liveNamespace()` *does* prepend `serverPrefix()`.
  - `ContentAddressedMetadataStorage.cpp:858-861` -- `serverPrefix()` is `server_root_id`.
  - Write exclusivity is scoped to one srid only: `Formats/CasLayout.h:218-231`
    (`ownerKey` / `epochKey` / `mountKey` are all `serverRootPrefix(server_root_id) + ...`).
  - The one namespace-ownership predicate that exists, `ownsNamespace()`
    (`ContentAddressedMetadataStorage.cpp:1458-1463`, `return root_namespace.starts_with(server_root_id + "/")`),
    is used only on the relink/adopt path; no mutation path in `CasRefLedger` consults it.
  - Id derivation is per-mount: `nextRefTxnId` = `{live_epoch, greatest_applied.ref_sequence + 1}`
    (`Pool/CasRefProtocol.cpp:418-423`), with `live_epoch` allocated from the *per-srid* `epochKey`.
  - Manifest keys are derived from the same per-mount counters:
    `cas/manifests/<ns>/<writer_epoch>-<build_sequence>/<ordinal>` (`Formats/CasLayout.h:139-145`).
  - The catalog explicitly contemplates a foreign `server_root_id` as the creator of a namespace and
    hands the entry over once the foreign creator fence is provably dead
    (`Pool/CasRefLedger.cpp:904-948`), and once the entry is `Live` **any** srid adopts the same life
    and starts appending (`:892-893`).

- **Trigger (minimal)**
  1. Two servers, distinct `server_root_id`s, one CAS pool (same endpoint + prefix) -- the supported
     multi-mount configuration that `serverRootsPrefix()` and the heartbeat floor exist for.
  2. Both hold the same table UUID `U` (a `CREATE ... ON CLUSTER` replicated table propagates one UUID),
     and both run `ALTER TABLE t FREEZE WITH NAME 'b'` (or any shadow-directory write).
  3. Both derive the identical namespace string `shadow/b/store/<xx>/<U>`
     (`ContentAddressedMetadataStorage.cpp:897-900`).
  4. `resolveNamespaceLife` on each: one creates the entry, the other observes it `Live` and adopts the
     same `NamespaceLifeId` (`Pool/CasRefLedger.cpp:892-893`).
  5. Both mounts now append into `cas/ns/stream/<same life>/_log/`, each numbering from its own
     `live_epoch` and its own in-memory `greatest_applied`.
     - **Equal epochs** (the common case: each srid's epoch counter starts independently, so two
       freshly claimed mounts are both at epoch 1): both derive the same key, the loser's
       `putIfAbsent` finds a foreign body, `classifyRefLogOccupant` returns `Occupant::Foreign`, and
       the lane is set `Faulted` with `on_impossible_interference` raised -- the namespace is wedged
       until remount (`Pool/CasRefLedger.cpp:2472-2530`).
     - **Unequal epochs**: the two id ranges are disjoint, so *both* `putIfAbsent`es commit. Each
       mount's committed state contains only its own ops; neither sees the other's rows. A later
       recovery walk replays the union in `(writer_epoch, ref_sequence)` order across an epoch
       boundary that no epoch seal justifies -- the intake either holds the namespace
       (`HoldReason::UnconsumedSealCrossing`, `Gc/CasGc.cpp:1683-1698`) or applies owner transitions
       whose `old_binding` was never observed.
  6. Independently of the ref-log, step 5 also collides in the manifest key space: both mounts stage
     `cas/manifests/shadow/b/store/<xx>/<U>/1-1/0` with *different* bodies
     (`Formats/CasLayout.h:139-145`, `Pool/CasPartWriteTxn.cpp:507`), i.e. two distinct manifests
     contend for one immutable manifest identity.

- **Evidence** The asymmetry between `liveNamespace` (srid-prefixed) and `shadowNamespace`
  (not prefixed) is in the same file, twelve lines apart. Every write-exclusion mechanism in the pool
  is keyed by `server_root_id` (`Formats/CasLayout.h:208-241`), so a namespace outside that prefix has
  no single-writer property at all. `ownsNamespace` proves the codebase has the predicate needed to
  reject such a namespace on the mutation path but does not apply it there.

- **Notes** Severity High because the failure is not confined to the FREEZE: the wedge is on the ref
  lane of a shared namespace, and the divergent-chain branch produces a ref-log whose replay is not
  well-defined for any future reader of that namespace. `floorForNamespace` cannot resolve an owner for
  these namespaces either, which is interleaving-2. Fail-loudness is partial: the equal-epoch branch is
  loud (`CORRUPTED_DATA` + faulted lane), the unequal-epoch branch is silent at append time.

### interleaving-2 -- non-srid-prefixed namespaces have no watermark floor, permanently disabling both the orphan-manifest sweep and the fold's clamp release (Medium)

- **Anchor**
  - `Gc/CasOrphanManifestSweep.cpp:37-57` -- `floorForNamespace()` recovers the owning mount lease by
    walking `/`-separated prefixes of the *namespace string* right-to-left and GETting
    `layout.mountKey(prefix)`; it returns `std::nullopt` if no prefix has a mount object.
  - `Gc/CasOrphanManifestSweep.cpp:373-377` -- `prefixEligible()` returns `false` whenever the floor is
    absent.
  - Consumers: the orphan manifest sweep (`:392`, `:554`), the fold's dead-precommit skip
    (`Gc/CasGc.cpp:1736-1755`), the GC manifest-cleanup gate (`Gc/CasGc.cpp:2943`), and fsck
    (`Tools/CasFsck.cpp:890`).

- **Trigger (minimal)**
  1. Any `FREEZE` / shadow write creates namespace `shadow/<name>/store/<xx>/<uuid>`
     (`ContentAddressedMetadataStorage.cpp:897-900`), which shares no prefix with any
     `gc/server-roots/<srid>/mount` key.
  2. GC round: the orphan manifest sweep lists `cas/manifests/shadow/...`, computes
     `prefixEligible(...) == false` for every build prefix, and skips every object forever
     (`Gc/CasOrphanManifestSweep.cpp:552-560`). Manifest bodies left behind by an abandoned or
     crashed shadow build are never reclaimed, and neither are the blobs they hold in-degree on.
  3. In the same code path, the fold's "provably dead precommit" release is also gated on
     `prefixEligible` (`Gc/CasGc.cpp:1736-1739`); with the floor absent, the alternative branch is the
     clamp at `:1757-1778`, which fires `HoldReason::ManifestBodyMissing` and holds the namespace at
     that position. Because eligibility can never become true for such a namespace, that hold can
     never be released by this mechanism -- the namespace's fold frontier stops permanently, and by
     `Gc/CasOrphanManifestSweep.cpp:343-347` every object at or above that position is retained.

- **Evidence** `floorForNamespace` is a purely lexical srid recovery from a namespace path; it is
  correct exactly for namespaces built by `liveNamespace` and wrong-by-construction for anything built
  by `shadowNamespace`. Direction of failure is safe (retain, never delete), but the retention is
  unbounded and the clamp branch converts a single missing precommit body into a permanent per-namespace
  GC stall.

- **Notes** Step 3's precondition (a live precommit whose manifest body is absent) is reachable only if
  a staged body is removed after its precommit record is durable -- the abandon path
  (`Pool/CasPartWriteTxn.cpp:778`, `:866`) is the candidate, which I did not fully confirm; step 2 (the
  unbounded manifest/blob leak) needs no extra precondition. Severity Medium on that basis.

### interleaving-3 -- cross-UUID RENAME migrates a snapshot of refs and then drops the source namespace unconditionally (Medium)

- **Anchor** `ContentAddressedTransaction.cpp:846-885`:
  - `:862` -- `for (const auto & [ref, _] : metadata_storage.store()->listRefs(from_ns))` -- the set of
    refs to migrate is a snapshot taken once.
  - `:863` -- `republishRef({from_ns, ref}, {to_ns, ref})` per ref, one non-atomic step each.
  - `:864-873` -- namespace files copied afterwards, also per name.
  - `:874` -- `metadata_storage.partAccess()->dropNamespace(from_ns)` -- an unconditional terminal
    removal of the source namespace; nothing re-lists it or asserts it is empty.
  - `:878-882` -- shipped `LOG_ERROR` string: *"RENAME TABLE move was only partially applied: the table
    is SPLIT across namespaces '{}' and '{}'"*.

- **Trigger (minimal)**
  1. `RENAME`/`EXCHANGE`-style move where source and destination table UUIDs differ, so the CAS branch
     at `:854-886` is taken.
  2. `listRefs(from_ns)` returns refs `{p1}` at time T0.
  3. Any actor publishes `p2` into `from_ns` after T0 -- a background merge, a fetch/relink receiver,
     or a retry of an in-flight publish that was already past its admission check.
  4. `dropNamespace(from_ns)` at `:874` issues the terminal removal for the whole namespace; `p2` is
     removed rather than migrated, and no diagnostic names it (the shipped `SPLIT` string only covers
     the exception path, and this path throws nothing).

- **Evidence** The migration is a read-modify-write over a namespace with no revalidation before the
  destructive final step, and the destructive step is namespace-scoped rather than
  migrated-ref-scoped. The shipped string at `:878-882` establishes that partial application is a
  known, tolerated outcome of this sequence, i.e. the sequence is not atomic by design.

- **Notes** What actually prevents step 3 today is ClickHouse-level DDL exclusion on the table, which
  is outside CAS and outside anything CAS asserts; the CAS layer contributes no fence. Severity Medium
  rather than High for that reason. Note also that `republishRef` correctly orders
  publish-destination-before-drop-source (`Parts/PartFolderAccess.cpp:437-438`), so the *blob* level of
  this operation is safe; the exposure is entirely the unconditional `dropNamespace`.

## By-design / info

- **Two-phase graduation is the load-bearing publish/delete fence.** Condemnation and deletion are
  separated by at least one round (`Gc/CasGc.cpp:2534-2559`, `oldest_nonpending_condemn_round <
  current_round`), which is what makes the transient in-degree dips of multi-namespace operations
  (rename, relink) survivable.
- **The fold is frontier-bounded and clamp-on-doubt.** Ref intake never walks past
  `committed_through`, and any unreadable manifest body or unproven epoch crossing converts into a
  namespace `hold` rather than a deletion (`Gc/CasGc.cpp:1662-1703`, `:1757-1778`). This is why
  "publish lands after the fold cut" is not exploitable.
- **Listing-before-lease ordering is what makes the watermark sound.** The orphan sweep lists
  `cas/manifests/` at `Gc/CasOrphanManifestSweep.cpp:489` and reads the mount lease only later at
  `:554`; combined with `allocateBuildSeq` registering `min_active` before any manifest body is staged
  (`Pool/CasMountRuntime.cpp:148`), a listed manifest of an in-flight build is always ineligible. The
  opposite order would be a live-delete race.
- **Listing-before-catalog ordering is what makes the janitor sound.** `Gc/CasNamespaceJanitor.cpp:25`
  (list) precedes `:35` (catalog cut), so the catalog is never staler than the listing; plus
  `deleteExact` with the listed token (`:105`).
- **Cross-srid namespace *creation* is explicitly reconciled** (`Pool/CasRefLedger.cpp:904-948`,
  including a `CreatorFenceStillLive` refusal). The gap in interleaving-1 is that this reconciliation
  covers only the `Creating` state; after `Live` there is no cross-srid mutual exclusion on appends.
- **Same-UUID recreation is fenced by incarnation, not by namespace string.** All namespace object keys
  embed the incarnation (`Formats/CasLayout.h:75-83`), and `resolveNamespaceLife` refuses creation while
  the prior life is `Removing` (`Pool/CasRefLedger.cpp:895-902`), so DROP-then-CREATE-with-same-UUID
  cannot ABA onto the old life's logs, snapshots, ckpt or namespace files.
- **The GC lease having no TTL (sibling finding) is largely absorbed at this layer**: the janitor,
  the sweep and the condemn/delete artifacts are all token-exact or content-deterministic
  (`putDeterministicArtifact`, `Gc/CasGc.cpp:2254`), so two concurrent leaders duplicate work rather
  than corrupt state. Interleaving consequences of that finding are not re-reported.
- **Fenced-out writers are rejected at three independent points**: `mayMutate`
  (`Pool/CasMountRuntime.cpp:77`), the `fence_ok` predicate re-evaluated inside the conditional PUT
  (`Pool/CasRefLedger.cpp:2259-2264`, `:2455`), and a successor's epoch seal occupying the derived id
  (`:2501-2516`). This is the strongest fence in the subsystem.

## Coverage

Walked pairs: all ten pairs named in the brief, plus writer/writer namespace creation, stale-writer vs
new-writer appends, janitor vs janitor, checkpoint vs GC ref-object cleanup, mount renew vs heartbeat
floor, and reader vs janitor -- 25 rows in the matrix.

Confirmed admitted interleavings: 3 (one High, two Medium). Two of the three share one root cause --
namespaces that are not `server_root_id`-scoped -- and each has an independent anchor and consequence.
Two matrix rows are attributed to sibling findings and deliberately not re-reported.

Not established, deliberately left out: whether the abandon path can delete a manifest body whose
precommit record is already durable (needed to make interleaving-2 step 3 unconditional); whether a
divergent two-epoch ref-log chain resolves to a hold or to a silent last-writer-wins in the recovery
walk (both branches are bad, but I could not pin which without executing the walk); any claim about
what an operator observes, since all CAS tests are deleted in this working tree
(`git show 842f2b37b8f:tests/...`) and no test asserts these orderings.

Method limits: static reading only, no build, no execution; local `EmulatedSingleProcess` backend means
the multi-mount interleavings above are not locally reproducible by construction.
