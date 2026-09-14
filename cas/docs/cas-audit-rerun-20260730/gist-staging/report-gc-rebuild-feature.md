# gc-rebuild-feature — re-run 2026-07-30

Re-audit of the `cas-gc-rebuild` feature against the current PR head
(branch `cas-audit-20260730`, tracking `altinity/cas-gc-rebuild`, PR
[#2073](https://github.com/Altinity/ClickHouse/pull/2073)). The original findings
CAS-015 (mount-lease interlock), CAS-050 (O(all blobs) sync HEAD scan), CAS-108
(DoS / FORCE blast radius / interrupted-rebuild debris), and CAS-206 (--force
narrowness) are all traced through the current code.

Since the original audit, the feature has gained a **SYSTEM SQL surface**
(`SYSTEM CONTENT ADDRESSED GC REBUILD [FORCE] <disk>`) that runs the rebuild
in-process on a live server. This inverts the framing of CAS-015 and creates a
new failure mode captured below as NEW-GCR-A.

## Scope in current code

- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGc.cpp` — `Gc::rebuildBaseline` (2488–2903); baseline guard in `Gc::runRegularRound` (1434–1449); adopted-seal `CORRUPTED_DATA` guard (1225–1231).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.cpp` — `runGcRebuildNow` (621–656).
- `programs/disks/CommandCaGcRebuild.cpp` — `clickhouse-disks ca-gc-rebuild` (85 lines, `isReadOnly()` gate at :54).
- `src/Interpreters/InterpreterSystemQuery.cpp` — `runContentAddressedGcRebuild` (2487–2510) + dispatch/access (1028–1032, 3187–3190).
- `src/Parsers/ParserSystemQuery.cpp` — `CONTENT_ADDRESSED_GC_REBUILD` case (477–488).
- `src/Parsers/ASTSystemQuery.{h,cpp}` — `CONTENT_ADDRESSED_GC_REBUILD` + `content_addressed_gc_rebuild_force`.
- `src/Access/Common/AccessType.h` — `SYSTEM_CONTENT_ADDRESSED_GC_REBUILD` (:352).
- `src/Disks/tests/gtest_cas_gc_rebuild.cpp` — 14 tests (grown from 11 in the original audit).

## Findings still present

### CAS-015 — `GC REBUILD` has no mount-lease interlock (🔴 still-present, *scope broadened*)

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGc.cpp:2488–2568` (`Gc::rebuildBaseline`).
- Trigger: any pool whose GC lease is currently free (or stealable) — `rebuildBaseline` acquires the GC lease (:2564) and, if healthy check fails or `force`, folds the universe (:2648) and blob scan (:2756–2769). It **never reads any `mount/*` key** to check whether another server is actively writing. `grep -n "mount|Mount" CasGc.cpp` at the rebuild function returns nothing beyond the `mount_obs`-driven *fence-out-dead-mounts* pass (:2836–2841), which is a **liveness cleanup of dead mounts**, not a refusal on a *live* one.
- Evidence quote (CasGc.cpp:2499–2501):
  > Health check BEFORE the lease (the lease acquire on an absent state CREATES a bootstrap body, which must not make scenario (а) look healthy). Healthy = decodes AND, when a baseline is claimed, the seal + every referenced run + every retired list are HEAD-present.
- Notes:
  - `ca-gc-rebuild` CLI still uses only `isReadOnly()` (`programs/disks/CommandCaGcRebuild.cpp:54`) — cannot see a remote writer on another host, exactly as GCR-1 stated.
  - The **new** `SYSTEM CONTENT ADDRESSED GC REBUILD` path (`ContentAddressedMetadataStorage.cpp:621–656`) is *inverted*: it calls `checkNotReadOnly("GC rebuild")` (:623), meaning the disk **must be writable on this server** — so *this* server necessarily holds a live mount lease when the SYSTEM command runs. See NEW-GCR-A for the new hazard this introduces.
  - No test in `gtest_cas_gc_rebuild.cpp` exercises a concurrent writer during rebuild — the two GCR-1 proof tests from the original audit are **not present**. `grep -n Mount` in that file returns nothing.

### CAS-050 — Zero-condemn scan is O(total blobs) with a synchronous HEAD per candidate, unbudgeted (🔴 still-present)

- Anchor: `Gc::rebuildBaseline` blob-scan block, `CasGc.cpp:2749–2770`.
- Trigger: any pool at rebuild time — the `forEachListedKey(backend, layout.blobsPrefix(), …)` walks the entire `blobs/` prefix; for every listed key not in `edge_bearing` the code issues a `backend.head(k.key)` synchronously.
- Evidence (CasGc.cpp:2762–2768):
  ```cpp
  if (edge_bearing.contains(ref))
      return;
  const HeadResult hr = backend.head(k.key);
  if (!hr.exists)
      return;
  zero_condemned[blobShard(ref, gc_shards)].push_back(RetiredEntry{...});
  ```
- Notes: The edge fold above has a real budget (`rebuild_edge_budget`, :2593–2594) and paginates via `route_deltas` / `flush_shard`. The blob LIST/HEAD sweep has **no budget knob, no HEAD concurrency, no rate limit** and no "phase 2 / optional" gate. `forEachListedKey` paginates at 1000 keys per LIST but every returned non-edge key becomes a HEAD round-trip. This is exactly GCR-2/GCR-4 with no mitigations added.
- The universe scan still repeats: `discoverUniverse()` at :2517 (health-check gen-0 branch) and again at :2648 for the fold. GCR-4 fully still present.

### CAS-108 — DoS / FORCE blast radius / interrupted-rebuild leaks gen artifacts (🟡 partly-improved, most of it still-present)

- **DoS / SYSTEM-gate side** — improved:
  - New privilege `SYSTEM_CONTENT_ADDRESSED_GC_REBUILD` is a distinct grant (`AccessType.h:352`) and is checked before dispatch (`InterpreterSystemQuery.cpp:1030, 3187–3190`).
  - Parser requires an explicit disk (no fan-out) (`ParserSystemQuery.cpp:479–486`) with a fail-closed backstop in the interpreter (`InterpreterSystemQuery.cpp:2489–2494`: *"REBUILD requires an EXPLICIT disk (E1): the destructive baseline rebuild must never fan out …"*).
  - `runGcRebuildNow` also serializes under `gc_scheduler_mutex` (`ContentAddressedMetadataStorage.cpp:638`) and re-runs the admission gate under the lock.
- **Interrupted-rebuild debris** — still-present:
  - Anchor: `CasGc.cpp:2570–2592` — generation numbering scans surviving `gc/gen/*` prefixes to pick `max_gen + 1`.
  - Trigger: a rebuild that crashes after `putDeterministicArtifact(foldSealKey)` (:2861) or the marker/run writes (:2789, :2861) but **before** the final `casPut(gcStateKey, …)` (:2874) leaves `gc/gen/<seal>/**`, `gc/gen/<run>/**`, and any published `meta/…` markers (:2789) as ownerless debris.
  - Evidence (CasGc.cpp:2588):
    > `Foreign key shape under gc/gen is debris, not a numbering input.`
    Debris is *skipped by numbering* — never reclaimed. The rebuild's own orphan sweep (:2712) targets manifests, and the regular round's orphan sweep does not target `gc/gen`.
  - Each interrupted attempt monotonically bumps `generation`; the swallowed condemn-marker path (`writeCondemnedMeta`, :2789) also leaves `.meta` objects on failure ("the entry enters the retired set unconfirmed" — :2796).
- **FORCE blast radius** — narrowness preserved (see CAS-206 below); but a **new** privileged in-server surface exists (see NEW-GCR-A).

### CAS-206 — `FORCE` is correctly narrow (⚪ info, still-safe / preserved)

- Anchor: `CasGc.cpp:2549` (`if (healthy && !force)`); post-lease unconditional refusals still fire regardless of `force`.
- Evidence:
  - `force` gates only the healthy-state refusal at :2549–2554.
  - Lease refusal (:2565–2568) is **unconditional** — `LeaseConflictRefuses` gtest still covers it.
  - Missing-committed-manifest refusal (:2681–2685) is **unconditional** — `MissingCommittedManifestRefuses` gtest still covers it.
  - CAS-collision refusal on the final `gc/state` write (:2874–2879) is **unconditional**.
- Verdict unchanged: `FORCE` cannot bless data loss. GCR-6 stays a design strength.

## Findings fixed / no longer reproducible

- **The old journal-based guard (`journal.front().transition_version > 1`) referenced in the original audit at CasGc.cpp:706–725 has been replaced** by a snapshot/log-based baseline guard in `runRegularRound` (`CasGc.cpp:1434–1449`) and an adopted-seal-absent `CORRUPTED_DATA` guard (`CasGc.cpp:1225–1231`). Both fail closed with a message pointing operators to `SYSTEM CONTENT ADDRESSED GC REBUILD`. The **GCR-7 guarantee** (guard fires before any destructive step) is preserved and covered by `CasGcBaselineGuard.AbsentAdoptedSealFailsClosed` (gtest_cas_gc_rebuild.cpp:54).
- **DoS/fan-out** portion of CAS-108: SYSTEM path now requires an explicit disk (parser + interpreter backstop), a distinct grant, and serializes with local GC verbs — the "operator typos SYSTEM CAS GC REBUILD → whole-cluster nuke" hazard is closed at the parser level.

## New findings (not in original audit)

### NEW-GCR-A — SYSTEM path calls `checkNotReadOnly` → **this server is a live mount** while rebuild runs (High)

- Anchor: `ContentAddressedMetadataStorage.cpp:621–655` (`runGcRebuildNow`), esp. :623 `checkNotReadOnly("GC rebuild")` and :651–655 constructs a `Cas::Gc` on `store()` and calls `rebuildBaseline(force)` directly.
- Trigger: any grantee of `SYSTEM CONTENT ADDRESSED GC REBUILD` executes `SYSTEM CONTENT ADDRESSED GC REBUILD FORCE '<disk>'` (or without FORCE, on an already-unhealthy state) on a running server. The invoking server itself owns the mount lease and, unless GC is stopped, may be publishing writes concurrently.
- Consequence: worse than the clickhouse-disks path — the CLI is at least gated on `isReadOnly()` so the *invoking* process cannot write, but the SYSTEM path *requires* that the invoking process holds a writable mount. Local writer serialization is only against `gc_scheduler_mutex` (round vs rebuild vs FORGET), which does **not** cover MergeTree publish/drop closures against `refs/…` shards — they run on user query threads and never take that mutex. The rebuild's universe scan (:2648) and blob scan (:2756–2770) are thus racing an active in-process writer as well as any remote one.
- Evidence quote (`ContentAddressedMetadataStorage.cpp:621–624`):
  ```cpp
  Cas::RebuildReport ContentAddressedMetadataStorage::runGcRebuildNow(bool force) const
  {
      checkNotReadOnly("GC rebuild");
      if (!gc_enabled)
  ```
- Suggested fix: (a) require `SYSTEM CAS GC STOP <disk>` (via `gcStop`) as a precondition, and (b) refuse if any mount lease other than a fenced-out one is fresh — the code already reads `mount_obs` right below the fold (:2841), so the data is on hand.
- Cross-ref: this is the same class as CAS-015 (mount-lease interlock missing) but the *new* SYSTEM surface makes running it in production far more likely, because the CLI's `<readonly>true</readonly>` friction is gone.

### NEW-GCR-B — Zero-condemn scan traverses **all admitted algos**, further widening CAS-050 (Low)

- Anchor: `CasGc.cpp:2756–2769`, comment at 2751–2755.
- Trigger: mixed-algo pool (hash algo migration).
- Notes: `parseBlobKey` now recognizes every admitted algo; the scan intentionally sweeps *all* of them ("across EVERY admitted algo, not just the pool's node-local write algo"). Correct for coverage, but multiplies the O(all blobs) HEAD cost by the number of admitted algos — no separate budget.

### NEW-GCR-C — Command-layer still uncovered by gtests (Test-gap, unchanged)

- Anchor: `programs/disks/CommandCaGcRebuild.cpp` (85 lines).
- Trigger: `isReadOnly()` gate at :54, the `dynamic_cast` rejections at :46–52, the non-zero exit on refusal at :74–76 — none of these have any test.
- SQL surface (`SYSTEM CONTENT ADDRESSED GC REBUILD`) has `tests/queries/0_stateless/05011_cas_gc_rebuild_access.sh` covering the *access grant* only; no functional refusal/perform test at the stateless-SQL layer for the new SYSTEM path.

### NEW-GCR-D — Marker write failure is a **silent per-entry retry**, not accounted for (Low)

- Anchor: `CasGc.cpp:2783–2800`.
- Trigger: any transient S3 error while publishing zero-condemn markers.
- Evidence (CasGc.cpp:2794–2797):
  > `ProfileEvents::increment(ProfileEvents::CasGcMetaWriteAnomaly);`
  > `tryLogCurrentException(logger, "CAS gc rebuild: condemn-marker write failed; the entry enters the retired set unconfirmed (carried at graduation, never fail-open deleted)");`
- Notes: correct in the fail-safe direction (never fail-open deletes), but the `RebuildReport` returned to the operator has no field surfacing "N markers failed" — the `SYSTEM` client sees `performed=1` and the follow-up graduation lag becomes an invisible operational issue.

## By-design / N/A / info

- Guard fires before any destructive step (GCR-7): still covered by `AbsentAdoptedSealFailsClosed`, `FreshStateOverTrimmedJournalsFailsClosed` re-cast as `CasGcBaselineGuard.GenuinelyFreshPoolIsUnaffected` + the `runRegularRound` guard at CasGc.cpp:1444.
- Test suite grew from 11 to 14 tests; new tests visible: `OrphanBlobCondemnedInRebuiltRun`, `PublishesCondemnMarkersForZeroEdgeBlobs`, `SwallowedRebuildMarkerWriteCarriesEntryInsteadOfDeleting`. Still no concurrent-writer test (per NEW-GCR-A / CAS-015).
- GCR-5 (LIST consistency assumption) is unchanged; still all `InMemoryBackend`-tested.

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-015 | High (DATA-LOSS) | 🔴 still-present; **worsened** by new SYSTEM path → see NEW-GCR-A | `CasGc.cpp:2488–2568`; `ContentAddressedMetadataStorage.cpp:621–655`; `CommandCaGcRebuild.cpp:54` |
| CAS-050 | Med (PERF/SCALE) | 🔴 still-present, unmitigated | `CasGc.cpp:2749–2770`; `discoverUniverse()` duplicated at `:2517` and `:2648` |
| CAS-108 | DAY2 / LEAK | 🟡 mixed: DoS/fan-out ✅ closed at SYSTEM parser; interrupted-rebuild `gc/gen` debris 🔴 still-present | Parser: `ParserSystemQuery.cpp:479–486`; interpreter backstop `InterpreterSystemQuery.cpp:2489–2494`; debris path: `CasGc.cpp:2570–2592, 2789, 2861, 2874` |
| CAS-206 | Info (safe) | ⚪ still-safe, force still narrowly scoped | `CasGc.cpp:2549` (only healthy gate); refusals at `:2565, :2681, :2874` unconditional |
| NEW-GCR-A | — | 🔴 new (High) — SYSTEM path requires writable disk ⇒ live mount interlock now bypassable via SQL grant | `ContentAddressedMetadataStorage.cpp:621–624, 651–655` |
| NEW-GCR-B | — | 🟡 new (Low) — blob scan sweeps all admitted algos, multiplying CAS-050 | `CasGc.cpp:2751–2769` |
| NEW-GCR-C | — | ⚪ new (test-gap) — CLI + SYSTEM refusal paths untested at functional layer | `CommandCaGcRebuild.cpp` (no gtest); `05011_cas_gc_rebuild_access.sh` covers access only |
| NEW-GCR-D | — | ⚪ new (Low) — silent marker-write anomaly not exposed in `RebuildReport` | `CasGc.cpp:2789–2800` |

**Counts:**
- Findings re-checked: **4** (CAS-015, CAS-050, CAS-108, CAS-206).
- Still-present unchanged: **2** (CAS-015, CAS-050).
- Still-present partly-mitigated: **1** (CAS-108 — DoS side closed; debris side open).
- Still-safe / by-design confirmed: **1** (CAS-206).
- New findings: **4** (NEW-GCR-A High, NEW-GCR-B Low, NEW-GCR-C test-gap, NEW-GCR-D Low).
