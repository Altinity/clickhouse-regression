# ad3-day2-dr-runbook — re-run 2026-07-30

Re-verification of AD-3 (Day-2 operability, DR, fsck, metrics) against the current
`cas-audit-20260730` branch (tracks `altinity/cas-gc-rebuild`, HEAD `834c9517f56`).

Scope of the re-run: CAS-013 (fsck not SQL-exposed), CAS-014 (no GC-liveness /
backlog / physical-bytes metrics), CAS-040 (`bytes_on_disk` logical only),
CAS-084 (orphan MPUs unreported), CAS-093 (fsck detects but doesn't repair),
CAS-101 (system-table quirks), CAS-102 (relink vs byte-fetch indistinguishable
in metrics), CAS-214 (66 ProfileEvents + `classifyCasNs` unanchored).

## Scope in current code

Files/dirs walked:

- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Tools/`
  - `CasFsck.{h,cpp}` (161 + 847 lines)
  - `CasInspect.{h,cpp}` (29 + 614 lines)
  - `CasDecommission.{h,cpp}` (52 + 376 lines) — NEW since original audit
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasInstrumentedBackend.{h,cpp}`
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGcScheduler.{h,cpp}`
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.cpp` (MPU search)
- `src/Interpreters/InterpreterSystemQuery.cpp` (CAS SQL surface, lines 1016-1090, 2414-2622)
- `src/Interpreters/ContentAddressedGarbageCollectionLog.cpp`
- `src/Parsers/ASTSystemQuery.{h,cpp}` (CAS command enum + formatter)
- `src/Parsers/ParserSystemQuery.cpp`
- `src/Storages/System/StorageSystemContentAddressedMounts.{h,cpp}` — NEW system table
- `src/Storages/System/attachSystemTables.cpp` (line 250)
- `src/Storages/System/StorageSystemParts.cpp` (bytes_on_disk column)
- `src/Storages/System/StorageSystemReplicatedFetches.cpp`
- `src/Common/ProfileEvents.cpp` (Cas* events, 142 total)

## Executive delta vs 2026-07-09 audit

Very substantial DR/observability progress on this PR:

- **SQL fsck exists** (`SYSTEM CONTENT ADDRESSED FSCK <disk>`), with an
  10-column result set including `physical_bytes` and
  `referenced_logical_bytes`. → CAS-013 largely fixed (summary-only, no
  `DETAIL`, no schedule).
- **`system.content_addressed_mounts`** is new. It carries lease
  introspection AND per-disk `is_leader`, `pending_reclaim`,
  `last_success_age_seconds`, `wedged_namespace_count`, plus a `lifecycle`
  column. → most of DR-2 (CAS-014) and DR-4 (CAS-062) satisfied at the
  introspection layer.
- **Operator verbs added**: `CONTENT_ADDRESSED_FSCK`,
  `CONTENT_ADDRESSED_FORGET`, `CONTENT_ADDRESSED_GC_STOP`,
  `CONTENT_ADDRESSED_GC_START`, `CONTENT_ADDRESSED_DROP_POOL_MEMBER`
  (`decommissionPoolMember` — the missing "kill this dead member" verb from
  DR-4).
- **Decommission tool** (`Tools/CasDecommission.{h,cpp}`) drains
  member-owned refs, manifest debris, staging, and mountpoint objects, and
  retires the mount slot — this is the pool-side reconciliation runbook
  DR-3 asked for, scoped to *one* dead member.

Still-present items are narrower and mostly operability polish (see
below).

## Findings still present

### CAS-013 — `fsck` (reachability / dangling / physical-vs-logical) is not operator-accessible via SQL

**Status: mostly fixed → residual `will-fix`.**

- Anchor (SQL surface): `src/Parsers/ASTSystemQuery.h:153` (`CONTENT_ADDRESSED_FSCK`);
  dispatch: `src/Interpreters/InterpreterSystemQuery.cpp:1034-1039`;
  implementation: `src/Interpreters/InterpreterSystemQuery.cpp:2524-2551`
  (`runContentAddressedFsck`).
- Result-set schema: `src/Interpreters/InterpreterSystemQuery.cpp:2414-2428`
  (`contentAddressedFsckColumns`) — includes `reachable`, `dangling`,
  `unreachable`, `pending_gc`, `awaiting_gc`, `unaccounted`, `physical_bytes`,
  `referenced_logical_bytes`, `distinct_blobs`, `total_blob_refs`.
- Residual gap: **summary-only.** The comment at
  `InterpreterSystemQuery.cpp:2537` — `runFsckNow(/* detail= */ false); // summary only (no DETAIL keyword yet)`
  — matches the header contract at `CasFsck.h:73-137`: `detail=true` is
  what populates the per-object list (offending keys, `reachable_from`
  labels, `stale_edge` names). Operators cannot ask "*which* refs are
  dangling / *which* run file is corrupted" from SQL. No `DETAIL` /
  `LIMIT` / `NAMESPACE` sub-syntax in `ParserSystemQuery.cpp` for this
  verb.
- Also missing from the surface (present in `runFsck`'s signature):
  no way to set a `deadline` / `partial_on_deadline` from SQL, and no
  `namespace_prefix`. A slow scan of a large pool has no operator lever
  short of pool quiesce.

### CAS-014 — No GC-liveness / reclaim-backlog / physical-bytes metric

**Status: mostly fixed → residual `will-fix` on the missing "bytes-pending-reclaim" signal and the aggregate/backend-native physical bytes.**

- The core liveness triple is now exposed per-disk via
  `system.content_addressed_mounts`:
  `StorageSystemContentAddressedMounts.cpp:52-55` — `is_leader`,
  `pending_reclaim`, `last_success_age_seconds`, `wedged_namespace_count`
  (all `Nullable` on peer rows — see the sensible comment at
  `.cpp:194-196`).
- Underlying source: `CasGcScheduler.h:118-125` — `struct GcHealth`.
- `physical_bytes` is now available on demand via `SYSTEM CONTENT ADDRESSED FSCK`
  (`InterpreterSystemQuery.cpp:2441`). That is a full-pool scan, not a
  continuously-updated gauge.
- Residual gaps:
  1. **No `bytes_pending_reclaim` / "backlog bytes"** anywhere. The
     `pending_reclaim` in `GcHealth`
     (`CasGcScheduler.h:122`: "cumulative condemned - executed deletes")
     is a **count** of ref-edges, not bytes. The AD-3 ask ("bytes pending
     reclaim") is unmet — an operator watching this column cannot answer
     "am I about to bill $N for backlog?".
  2. **No aggregate / continuous `physical_bytes` metric.** It is
     computable only by running fsck, which is a full LIST + reachability
     walk. There is no cheap gauge polled at scale (compare CAS-040 —
     same gap on the `system.parts` side).
  3. **No `rounds_since_last_reclaim`.** `last_success_age_seconds`
     (`CasGcScheduler.h:123`) counts age of the last *led* round, not
     the last round that actually *deleted* anything — a leader spinning
     empty rounds keeps this at 0 while backlog grows.

### CAS-040 — `system.parts.bytes_on_disk` is logical, over-reports physical N× under dedup; no physical/dedup-ratio system view

**Status: still present (unchanged).**

- Anchor: `src/Storages/System/StorageSystemParts.cpp:74` —
  `{"bytes_on_disk", ..., "Total size of all the data part files in bytes."}`.
- No new per-part or per-disk *physical* view. The only physical number
  is now inside `SYSTEM CONTENT ADDRESSED FSCK`'s single-row result
  (whole-pool aggregate), which is a full scan.
- Evidence quote (from fsck header, `CasFsck.h:125`):
  `double dedupRatio() const { return distinct_blobs ? double(total_blob_refs) / double(distinct_blobs) : 0.0; }`
  — the ratio is materialized inside the report struct and *not* joined
  back to `system.parts` / `system.disks`.

### CAS-084 — Orphaned multipart uploads neither aborted nor reported

**Status: still present (unchanged).**

- Anchors — negative evidence:
  - `grep -R "MultipartUpload\|abortMultipart\|listMultipart"` under
    `Tools/`, `Gc/`, `Pool/`, `Backend/` returns **only** call sites
    inside `Backend/CasObjectStorageBackend.cpp:813-828` (a comment
    explaining why CAS avoids MPU on conditional writes and the
    `WriteBufferFromS3::createMultipartUpload` call). No `listMultipartUpload*`
    inventory, no `abortMultipartUpload*` sweep, and no fsck class for MPU
    orphans (see `CasFsck.h:27-50` `enum FsckClass` — `Reachable`,
    `Dangling`, `Unreachable`, `PendingGc`, `AwaitingGc`, `Unaccounted`,
    `StaleEdge`, `SnapshotOracleMismatch`, `CorruptedRun` — no MPU class).
- Runbook mitigation is still bucket-lifecycle-rule-based; nothing in
  the SQL/system surface tells the operator whether abandoned MPUs
  exist.

### CAS-093 — `fsck` detects Dangling (=already-lost) but never repairs; no forced cadence

**Status: still present (unchanged).**

- Anchor: `Tools/CasFsck.cpp:1-60` — no `repair`/`heal`/`rewrite`/
  `refetch` code path. `runFsck` builds and returns `FsckReport`; the
  header at `CasFsck.h:139-150` documents this as strictly read-only.
- `SYSTEM CONTENT ADDRESSED FSCK` at
  `InterpreterSystemQuery.cpp:2524-2551` also has no repair verb / sibling
  `SYSTEM CONTENT ADDRESSED REPAIR` command. Cadence: neither
  `ContentAddressedSettings.{h,cpp}` nor the scheduler
  (`Gc/CasGcScheduler.{h,cpp}`) contain any periodic `fsck` invocation
  — the operator has to remember to run it.

### CAS-101 — System-table quirks (empty `remote_path` for in-manifest files, many-to-one remote paths, placeholder free space, unverified mutations / part_log / replicated_fetches fields)

**Status: still present. Nothing in the diff changes the semantics of
`remote_path`, part-level free-space reporting, or the fields listed in
the finding.** The new `system.content_addressed_mounts` adds
introspection but leaves the underlying quirks in `system.parts` /
`system.parts_columns` / `system.mutations` untouched.

### CAS-102 — Relink vs byte-fetch indistinguishable in `system.replicated_fetches`; cache observability by blob key not part path

**Status: still present.**

- Anchor: `src/Storages/System/StorageSystemReplicatedFetches.cpp:27-60` —
  no `is_relink` / `bytes_transferred_over_network` /
  `relink_source_blob` columns.
- ProfileEvents does count relink activity
  (`ProfileEvents.cpp:804` — `CasRefRepoint`) but a query-time
  correlation from a fetch row back to "was this a relink vs a byte
  fetch" is still not possible without the join described in the
  original finding.

### CAS-214 — 142 CAS ProfileEvents + `classifyCasNs` unanchored substring match

**Status: still present, and the ProfileEvents surface has more than doubled (66 → 142) — the fan-out is now larger.**

- Anchor for `classifyCasNs`:
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasInstrumentedBackend.cpp:113-130`.
  Still uses unanchored `key.find(...)` for `/blobs/`, `/cas/refs/`,
  `/cas/manifests/`, `/roots/`, `/gc/`. A user-provided path segment
  containing (for example) `/blobs/` would still misclassify — a
  metric-misattribution risk exactly as originally called out.
- Count: `grep -c '^\s*M(Cas' src/Common/ProfileEvents.cpp` → **142**
  events (vs 66 in the original audit). The doubling was necessary
  work (`CasRefApplyPoisoned`, `CasGcClampSuppressedPasses`,
  `CasGcDeadPrecommitSkipped`, etc. are all valid signal) but reinforces
  the point: this instrumentation is now the widest metric surface in
  the file and any prefix collision on `classifyCasNs` fans out across
  more counters than before.

## Findings fixed / no longer reproducible

- **DR-1 (largely fixed)** — `SYSTEM CONTENT ADDRESSED FSCK` exists;
  parser at `src/Parsers/ASTSystemQuery.h:153`; dispatch at
  `InterpreterSystemQuery.cpp:2524`. Residual is the missing `DETAIL /
  DEADLINE / NAMESPACE` sub-syntax (still-present entry above).
- **DR-4 (mostly fixed)** — `system.content_addressed_mounts` gives lease
  introspection (`StorageSystemContentAddressedMounts.cpp:40-59`
  includes `server_uuid`, `hostname`, `pid`, `writer_epoch`,
  `renewal_sequence`, `expires_at_ms`, `state`) and there is now a
  documented **force-recovery sequence**:
  `SYSTEM CONTENT ADDRESSED FORGET <disk>` (local, assertion-only —
  `InterpreterSystemQuery.cpp:2553-2576`) and
  `SYSTEM CONTENT ADDRESSED DROP POOL MEMBER '<srid>' FROM DISK '<disk>'`
  (pool-side, drives `decommissionPoolMember` at
  `Tools/CasDecommission.h:49-50`,
  `InterpreterSystemQuery.cpp:1058-1090`).
- **DR-3 (partial)** — `decommissionPoolMember` reconciles by dead
  *member*, not by ZK/catalog diff. Still no `SYSTEM CONTENT ADDRESSED
  RECONCILE` that compares live catalog/ZK part sets to CAS
  namespaces (the LC-2 / RPL-2 / phantom-part-at-startup ask), so
  CAS-044 remains the correct home for that gap.

## New findings (not in original audit)

- **NEW-ad3-1 (Low — SQL fsck cannot bound its runtime).**
  `Cas::runFsck` accepts a `deadline` and a `partial_on_deadline` flag
  (`CasFsck.h:148-150`), but `runContentAddressedFsck` in
  `InterpreterSystemQuery.cpp:2524-2551` never plumbs the query-level
  `max_execution_time` / an explicit `DEADLINE '...'` clause into it.
  Result: an operator running `SYSTEM CONTENT ADDRESSED FSCK` against a
  large / slow pool has no way to say "give me what you have after
  10 min"; the scan runs to completion or throws `TIMEOUT_EXCEEDED`
  from `checkDeadline` (`CasFsck.cpp:43-48`). Anchor:
  `InterpreterSystemQuery.cpp:2537` (`runFsckNow(false)` — no
  `deadline`).

- **NEW-ad3-2 (Low — `SYSTEM CONTENT ADDRESSED GC STOP` truthfully-but-misleadingly reports `is_leader`).**
  The comment at `InterpreterSystemQuery.cpp:1018-1023` explains that
  after GC is stopped, an explicit `GC RUN` can still transiently set
  `is_leader=1` on the disk — and `system.content_addressed_mounts.is_leader`
  will show that until a peer steals the lease. This is documented and
  intentional but is a Day-2 footgun: dashboards keyed on
  `is_leader AND NOT gc_running` will see a phantom leader window
  during operator-initiated GC RUNs after a STOP.

- **NEW-ad3-3 (Low — `SYSTEM CONTENT ADDRESSED FORGET` explicitly does not verify erasure).**
  `InterpreterSystemQuery.cpp:2570-2575` — the log line spells out
  "erasure NOT verified. The disk stays registered and answers store-class
  access with a typed error". Combined with CAS-093 (fsck cannot
  repair) and CAS-084 (MPU orphans), a `FORGET` on a disk with in-flight
  writes / orphaned MPUs leaves cleanup entirely to whatever bucket
  lifecycle rule the operator remembered to configure. Worth a runbook
  note that `FORGET` is an *assertion*, not a *reclamation*.

- **NEW-ad3-4 (Info — `Nullable` peer-row columns in `content_addressed_mounts` are a good pattern to keep).**
  `StorageSystemContentAddressedMounts.cpp:194-210` deliberately writes
  `NULL` for `is_leader` / `pending_reclaim` / `last_success_age_seconds` /
  `wedged_namespace_count` on rows describing *other servers*' mounts.
  This prevents the "peer B is GC leader" misread the comment calls out
  — worth codifying as a pattern for future per-disk/per-node CAS views
  (relates to CAS-101 quirks).

## By-design / N/A / info

- **DR-7 remains info-only.** `GC REBUILD` is still the excellent narrow
  DR tool; the AD-3 point ("it's the only rich one") is now less true
  because of `FSCK`, `FORGET`, `GC STOP/START`, and `DROP POOL MEMBER`
  additions.
- The `Tools/CasDecommission.cpp` decommission path is a *writer* operation
  that emits normal ref-edge deltas (`CasDecommission.h:44-45`), so it
  does not synchronously reclaim shared blob bytes — reliance on the
  regular GC to sweep the freed edges is documented and correct.

## Verdict summary table

| CAS-id  | Old severity | Status                                | Evidence anchor |
|---------|--------------|----------------------------------------|-----------------|
| CAS-013 | High         | 🛠 will-fix (largely fixed; missing `DETAIL`/`DEADLINE`/`NAMESPACE` in SQL) | `Parsers/ASTSystemQuery.h:153`, `InterpreterSystemQuery.cpp:2524-2551` |
| CAS-014 | High         | 🛠 will-fix (liveness triple exposed; no `bytes_pending_reclaim`, no continuous physical-bytes) | `StorageSystemContentAddressedMounts.cpp:52-55`, `Gc/CasGcScheduler.h:118-125` |
| CAS-040 | Med (OBSERV) | 🔴 still-present | `Storages/System/StorageSystemParts.cpp:74` |
| CAS-084 | Low (LEAK)   | 🔴 still-present | absence: no MPU calls under CAS `Tools/`,`Gc/`,`Pool/` (only `Backend/CasObjectStorageBackend.cpp:813-828`) |
| CAS-093 | Med (INT)    | 🔴 still-present | `Tools/CasFsck.cpp` (no repair path); `InterpreterSystemQuery.cpp:2524-2551` (no `REPAIR` verb) |
| CAS-101 | Low (OBSERV) | 🔴 still-present | `Storages/System/StorageSystemParts.cpp:74`; `StorageSystemReplicatedFetches.cpp` unchanged |
| CAS-102 | Low (OBSERV) | 🔴 still-present | `Storages/System/StorageSystemReplicatedFetches.cpp:27-60` (no relink flag) |
| CAS-214 | Info         | 🔴 still-present (surface grew: 66 → 142 events) | `Common/ProfileEvents.cpp` (`grep -c '^\s*M(Cas' → 142`); `Backend/CasInstrumentedBackend.cpp:113-130` |
| DR-1 (=CAS-013) | High | ✅ largely fixed | as CAS-013 |
| DR-2 (=CAS-014) | High | ✅ largely fixed | as CAS-014 |
| DR-3 (=CAS-044) | Med  | ↗ split-out (partial: per-member `DROP POOL MEMBER`; no cross-catalog RECONCILE) | `Tools/CasDecommission.h:49`, `InterpreterSystemQuery.cpp:1058-1090` |
| DR-4 (=CAS-062) | Med  | ✅ mostly fixed | `StorageSystemContentAddressedMounts.cpp:40-59`; `InterpreterSystemQuery.cpp:2553-2622` |
| DR-5 (=CAS-063) | Med  | 🔴 still-present (no `PoolMeta` backup/restore runbook or tool) | absence: no `PoolMeta` restore code under `Pool/` |
| DR-6 (=CAS-084) | Low  | 🔴 still-present | as CAS-084 |
| DR-7            | Info | ⚪ info (still true; toolbox is broader now) | — |
| NEW-ad3-1 | Low  | 🔴 still-present | `InterpreterSystemQuery.cpp:2537` |
| NEW-ad3-2 | Low  | 🔴 still-present | `InterpreterSystemQuery.cpp:1018-1023` |
| NEW-ad3-3 | Low  | 🔴 still-present | `InterpreterSystemQuery.cpp:2570-2575` |
| NEW-ad3-4 | Info | ⚪ info (good pattern) | `StorageSystemContentAddressedMounts.cpp:194-210` |
