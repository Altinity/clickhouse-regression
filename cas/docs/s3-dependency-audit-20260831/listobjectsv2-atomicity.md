# ListObjectsV2: non-atomic (multi-request) usage

**Tree:** `antalya-26.6` @ `6e10e116421`  
**Question:** which CAS listings are split into two or more S3 `ListObjectsV2` requests, and what that implies.

## What S3 actually provides

A single `ListObjectsV2` response is one page (`MaxKeys`, default ClickHouse `list_object_keys_size = 1000`). If `IsTruncated` is true, the next page uses `ContinuationToken` (and, on the first `iterate` request, `StartAfter`).

**A multi-page listing is not a point-in-time snapshot.** Between pages:

- a key can be created and appear on a later page, or never appear if it sorts before the cursor
- a key can be deleted after it was listed
- a key that sorts between two pages can be missed (holey list) or appear twice if the store's cursor is sloppy

AWS S3 has been strongly consistent for individual objects since December 2020. That does **not** make a paginated prefix walk atomic.

CAS encodes this as `Backend::list(prefix, cursor, limit)` → `IObjectStorage::iterate(..., start_after=cursor)`. `forEachListedKey` loops until `next_cursor` is empty. Comments at `CasBackend.h:367–370` call this a cursor-resume walk: “each returned key is delivered once”; they do **not** claim a snapshot.

`ObjectStorageBackend::list` (`CasObjectStorageBackend.cpp:1088–1176`) on Native S3:

- one `Backend::list(limit=N)` may itself issue **multiple** HTTP `ListObjectsV2` calls (`iterate` with `max_keys=0` uses the S3 page size) while returning ≤ N keys
- so even a “single page” CAS call can be multi-request if the store page is smaller than `limit`, or if `start_after` filtering skips keys

## Verdict

| Class | Multi-request? | Treated as snapshot? | Safety posture |
|-------|----------------|----------------------|----------------|
| `prefixHasAnyKey` (`limit=1`) | Usually one HTTP page | N/A (existence hint) | Probe only |
| Capability probe (`limit=100`, one key) | One page | N/A | Fail-closed if probe key missing |
| Janitor / orphan planner (one page per tick/round) | One CAS page; may be multiple HTTP if page size &lt; budget | No | Cursor does not advance without authority |
| Every `forEachListedKey` / cursor `while` walk | **Yes** | **No** | Hint + follow-up HEAD/GET/probe, or fail-closed on holes |
| `sweepOwnMountStaging` (`listObjects(max_keys=0)`) | **Yes** (full prefix) | No | Fail-open; best-effort delete |

**No production caller treats a multi-page LIST as an atomic snapshot.**

---

## Per-site inventory

### Single-page / single-key (not a multi-page snapshot problem)

| Site | File:line | Prefix | Limit | Notes |
|------|-----------|--------|------:|-------|
| `prefixHasAnyKey` | `Pool/CasServerRoot.cpp:61` | caller | 1 | Emptiness hint for decommission subtree |
| `runCapabilityProbe` | `Backend/CasProbe.cpp:194,231` | `_probe/<id>` | 100 | List-after-write / list-after-delete of one key |
| `planManifestCursorPage` | `Gc/CasOrphanManifestSweep.cpp:616` | manifests | budget | One page **per GC round**; cursor advances across rounds |
| `NamespaceJanitor::runOnePage` | `Gc/CasNamespaceJanitor.cpp:25` | `cas/ns/` | budget | One page per tick; cursor frozen if delete authority missing |

These can still be **internally** multi-HTTP if `list_object_keys_size` is smaller than the CAS limit, but they do not assemble a “whole prefix” view in one logical operation.

### Multi-page walks (`forEachListedKey` or explicit cursor loop)

| # | Function | File:line | Typical prefix | Why listing | If pages disagree with store |
|---|----------|-----------|----------------|-------------|------------------------------|
| 1 | `computeHeartbeatFloor` | `CasServerRoot.cpp:1137` | `gc/server-roots/` | Live-mount floor | Conservative `++live` on LIST+GET race |
| 2 | `probeNonTerminalMountSlots` | `CasServerRoot.cpp:1252` | same | Recreate safety | Skip if GET misses; fail-closed on undecodable lease |
| 3 | `listMounts` | `CasServerRoot.cpp:1306` | same | `system.content_addressed_mounts` | Skip row if GET misses (observability) |
| 4 | `listNamespaceFiles` | `CasPlainObjects.cpp:103` | namespace files | Directory listing | May miss/include files; sorted for determinism |
| 5 | `deletePrefixWholesale` | `CasGc.cpp:3410` | `gc/gen/<g>/` | Prune GC-internal prefix | Fail-open on 404 / TokenMismatch |
| 6 | `probePoolBootstrapResidual` | `CasSentinelProbe.cpp:47` | pool prefix | Residual before minting `_pool_meta` | **Fail-closed** → `Indeterminate`; “LIST is only a discovery hint” |
| 7 | `sweepNamespace` | `CasOrphanManifestSweep.cpp:557` | manifest build prefix | Exact-token delete unowned bodies | HEAD + `deleteExact`; 404/mismatch tolerated |
| 8 | `newestFoldSealRef` | `CasGc.cpp:1344` | `gc/gen/` | Newest fold seal | **Wide list is a hint**; probes generations above listed max; **throws** if listing lied |
| 9 | `probeGenerationForSeal` | `CasGc.cpp:1467` | one generation | Narrow seal probe | Complements (8) |
| 10 | `enumerateRefPrefix` | `CasGc.cpp:3651` | `cas/ns/stream/` | GC hot scan once per round | Hint; fold walks by exact key |
| 11 | `rebuildBaseline` (×3) | `CasGc.cpp:3915,3952,4148` | streams / `gc/gen/` / manifests | Rebuild health + next gen + over-protect | Completeness checks; blob-prefix listing **removed** (listing-driven hide) |
| 12 | `CasFsck::listAll` | `CasFsck.cpp:60` used at 728, 914, 1099 | blobs / manifests | Physical inventory | Explicitly not a snapshot; HEAD re-check for LIST lag |
| 13 | `runFsckImpl` residue | `CasFsck.cpp:528` | `cas/ns/` | Lifeless ns keys | Observe-then-cut catalog after listing |
| 14 | `deleteListedPrefix` | `CasDecommission.cpp:50` | staging / server-root data | Drain | Fail-open per object |
| 15 | decommission manifests | `CasDecommission.cpp:222` | server manifests | Group then sweep | Warnings block slot retirement |

### Direct `IObjectStorage::listObjects` (bypasses `Backend::list`)

| Function | File:line | Prefix | Pagination | Failure |
|----------|-----------|--------|------------|---------|
| `sweepOwnMountStaging` | `CasServerRoot.cpp:1867` | `staging/<server_root_id>/` | `max_keys=0` = full walk | **Fail-open**: LIST error swallowed; mount proceeds |

Implementation layer (not a caller): `ObjectStorageBackend::list` Native path uses `iterate` (`CasObjectStorageBackend.cpp:1148`); Emulated path uses `listObjects(max_keys=0)` then client-side slice (`:1104`).

### Not list-based (for contrast)

- `recoverRefTableDetailedFromAuthority` — point `get` only
- `Gc::discoverUniverse` — catalog GET, not LIST
- `ContentAddressedMetadataStorage` directory APIs — catalog-backed

---

## Side effects of a non-atomic / holey list

| Effect | Where it matters | Mitigated? |
|--------|------------------|------------|
| Missed key (hole) | GC rebuild newest-seal; fsck blob inventory | **Yes, fail-closed** in `newestFoldSealRef` (probe above listed max). Fsck HEAD-rechecks. |
| Missed key | GC hot `enumerateRefPrefix` | Fold is exact-key; missed ref delays reclaim (leak), does not delete live data |
| Missed key | orphan / janitor / decommission | Next page/round / next mount; leak not loss |
| Extra key (created mid-walk) | wholesale delete / staging sweep | Token-exact delete or unconditional staging delete of **temp** prefixes only |
| Extra key | heartbeat / mounts table | Conservative live / skip on GET miss |
| False empty (`limit=1` miss) | decommission subtree empty | Combined with other prefixes; slot retirement still gated |
| LIST error | bootstrap | Indeterminate, do not mint identity |
| LIST error | staging sweep | Mount continues with leaked staging objects |

**Safety split (intended):**

- **Must not lose data:** holey list must not produce a “newest seal” that is too old (`newestFoldSealRef`), must not make GC delete a live blob (reclaim is `deleteExact`, not “listed ⇒ delete”), must not mint a pool identity over residuals.
- **May leak:** missed orphans, missed staging keys, delayed janitor.

---

## Confirmed finding (by design, still an operator hazard)

**LIST-1 — Multi-page `ListObjectsV2` is never an atomic snapshot**

- **Impact:** Any algorithm that assumed “we listed the whole prefix as it was at T0” is wrong. CAS mostly does not assume that; rebuild/fsck/bootstrap document the hint.
- **Anchor:** `CasBackend.h:367–370`, `CasGc.cpp:1337–1340`, `S3ObjectStorage.cpp:159–216`
- **Trigger:** prefix larger than one S3 page **or** concurrent create/delete during the walk
- **Why defect-class:** not a code bug in the pagination helper; it **is** a correctness boundary. Residual risk is any future caller that treats `forEachListedKey` as a snapshot.
- **Fix direction:** keep list-as-hint; never add a “prefix empty ⇒ safe to destroy” decision that is only a multi-page list.
- **Regression test direction:** existing holey-list / rebuild probes; add a test that inserts a key in the lexicographic gap between two pages if one is not already present.

---

## Coverage

| Call-graph node | Reviewed |
|-----------------|----------|
| All production `Backend::list` sites listed above | yes |
| `forEachListedKey` callers | yes |
| `listObjects` staging sweep | yes |
| Test-only `src/Disks/tests/` list sites | skipped (not production) |
| Azure `iterate` (start_after ignored) | noted; CAS-on-Azure listing resume is weaker than S3 |
