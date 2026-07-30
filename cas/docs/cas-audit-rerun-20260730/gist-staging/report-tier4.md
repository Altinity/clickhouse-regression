# cas-tier4-audit — re-run 2026-07-30

Original section: `cas-tier4-audit.md` (Object-Store compat / Error / Observability).
Per user directive, this re-run ALSO covers the BACKUP/RESTORE/ATTACH/FETCH-to-detached /
EXCHANGE / `clickhouse-disks` tooling findings the user explicitly listed
(CAS-042 = BAK-1/B-1, CAS-105 = BAK-4/B-3, CAS-109 = tooling/EXCHANGE test-gap,
CAS-110 = B-5/RPL-4/RPL-5 relink to detached).

## Scope in current code

- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.{h,cpp}`
- `.../Backend/CasProbe.{h,cpp}`, `CasRequestControl.{h,cpp}`
- `.../ContentAddressedMetadataStorage.{h,cpp}`
- `.../ContentAddressedTransaction.{h,cpp}` (RENAME/ATTACH/DETACH/move paths)
- `.../ContentAddressedExchange.{h,cpp}` (relink wire)
- `.../Parts/PartPathParser.{cpp}` (`looksLikePartDir`)
- `.../Tools/CasFsck.{cpp,h}`, `CasInspect.{cpp,h}`, `CasDecommission.{cpp,h}`
- `.../Gc/CasGc*.{cpp,h}`
- Adjacent CAS integration hooks:
  - `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp` (BACKUP hardlink gate + freeze)
  - `src/Storages/MergeTree/DataPartsExchange.{cpp,h}` (relink + `to_detached` gate)
  - `src/Storages/MergeTree/MergeTreeData.cpp` (`choosePartFormat`)
  - `src/Common/ProfileEvents.cpp`, `src/Common/CurrentMetrics.cpp` (CAS metrics)
- `tests/integration/test_cas_*`, `test_content_addressed_*` (test coverage inventory)

Static reasoning only.

---

## Findings still present

### OSC-1 (High) — Native conditional-write path NOT end-to-end tested on real S3/GCS
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.cpp:143-146`
- Trigger: production run against AWS S3 / GCS exercises a code path validated only against RustFS+emulation.
- Evidence quote (still present in current code):
  > "Native conditional writes require an S3-compatible integration environment for end-to-end
  > coverage. Unit tests cover the emulated semantics, the typed exception path, and this classifier
  > through the test-only `detail` declaration."
- Notes: The classifier is fail-safe (misread → PreconditionFailed, never false success — see
  `finalizeConditionalWrite` at line 147, which now matches both `PreconditionFailed`, the
  `NoSuchKey` error name, and `S3Errors::NO_SUCH_KEY` enum). Still the single most safety-critical
  seam without a real-S3/GCS integration test. Original finding stands verbatim.

### OSC-2 (High) — GCS bucket versioning breaks GC reclaim; guarded only when the versioning API is queryable
- Anchor: `.../Backend/CasObjectStorageBackend.cpp:55-84` (`checkPoolPreconditions`)
- Trigger: mount CAS on a GCS bucket where `GetBucketVersioning` fails (permissions / unsupported)
  while versioning is actually ON.
- Evidence quote (lines 69-74):
  > "could not VERIFY the bucket-versioning precondition ... proceeding on the assumption that
  > bucket versioning is OFF. If versioning is actually enabled, token-exact DELETEs will
  > archive noncurrent generations instead of reclaiming storage and GC will silently stop
  > reclaiming space."
- Notes: The Enabled branch fails-closed (`NOT_IMPLEMENTED`, line 79). Inconclusive still
  proceeds → unbounded silent leak with only a startup WARNING. No config knob to force
  fail-closed on inconclusive. Recommendation unchanged.

### OSC-3 (Med) — Azure / non-S3 object storages effectively unsupported for Native CAS
- Anchor: `.../Backend/CasObjectStorageBackend.cpp:93-109` (`checkConditionalWriteSingleAttemptSupport`)
- Trigger: attempt to mount CAS Native on any `IObjectStorage` that does not implement the
  `SingleAttempt` retry profile (only `S3ObjectStorage` does today).
- Evidence quote (lines 103-108):
  > "CAS Native-mode conditional writes require an object storage that supports the SingleAttempt
  > retry profile ... refusing to mount writable. Native mode is designed for an S3-like
  > conditional dialect only; a non-S3 object storage should use EmulatedSingleProcess."
- Notes: Fail-closed is correct, but the S3-family-only supported universe is asserted in-code,
  not in user-facing docs. Multi-writer CAS on Azure remains unavailable.

### OSC-4 (Med) — Read-your-writes LIST is a hard per-backend assumption
- Anchor: `.../Pool/CasPool.cpp:1327-1329` ("RustFS: to confirm in soak.")
- Trigger: startup part discovery / `dropNamespace` enumeration on any backend whose LIST is
  not strongly consistent read-your-writes.
- Notes: On S3 this is guaranteed since 2021; on GCS/others unstated. Ties to BOOT-1
  (Tier 3). No new mitigation in current code.

### ERR-1 (Med) — Throttle/429 storms compound with CAS-conflict retries
- Anchor: retry surfaces at
  `.../Backend/CasObjectStorageBackend.cpp` (nativeConditionalPut) +
  `.../Pool/CasPool.cpp` mutate/casPut loops.
- Trigger: sustained 429/SlowDown on a hot shard.
- Notes: No CAS-level adaptive backoff on throttle; relies on the underlying S3 client's
  retry/backoff. Not exercised by tests. Original finding stands.

### ERR-2 (Med) — Failed-build debris reclaimed only by sweeps
- Anchor: `.../ContentAddressedTransaction.cpp` (transaction abort path) + orphan sweep in
  `.../Gc/CasGc.cpp` and `CasGcScheduler.cpp` + reference to "reclaimable/in-flight" debris.
- Trigger: repeated write failures after `putBlob`/precommit but before promote (e.g.
  disk-full, OOM storm).
- Notes: No failure-rate backpressure; debris storms cause transient bloat. Unchanged.

### ERR-3 (Low) — Crash mid multipart upload leaves incomplete MPU
- Anchor: not a CAS-specific code path; CAS relies on the S3 client's MPU + bucket lifecycle
  rules for MPU abort.
- Notes: Unchanged; standard hygiene item.

### OBS-1 (Med) — No continuously-exported physical/logical/dedup/pending-reclaim metric
- Anchor: `src/Common/ProfileEvents.cpp:759-843` (CAS metrics inventory), `.../CurrentMetrics.cpp:233-241`.
- Trigger: operator wants to answer "how much am I actually storing?" / "is GC keeping up?"
  without paying for a full `CasFsck` pool scan.
- Notes: The current CAS ProfileEvents/CurrentMetrics are all **request counters** and
  **cache-footprint gauges** — none exposes physical bytes, referenced-logical bytes,
  dedup ratio, or pending-reclaim bytes. `CasFsck` is still the only source
  (`.../Tools/CasFsck.cpp`, on-demand full scan). Verified absent:
  `CasPhysicalBytes / CasLogicalBytes / CasDedupRatio / CasPendingReclaim` (grep = no matches).
  Original finding stands.

### OBS-2 (Med) — GC health is per-round log rows, not an alertable metric
- Anchor: `.../Gc/CasGc.{cpp,h}` + `.../Gc/CasGcScheduler.h` (round accounting) +
  `system.content_addressed_garbage_collection_log` writer.
- Trigger: silently stalled GC (OSC-2 GCS versioning, lease starvation, wedged mount).
- Notes: No "rounds since last successful reclaim" / "reclaim backlog" / "GC leader present"
  gauge exported (grep for `CasGcRoundsCompleted`, `CasGcLastRound`, `CasReclaim*` returned
  zero hits). Given how many earlier findings terminate in "GC silently stops reclaiming",
  this remains the highest-leverage observability gap. Unchanged.

### ERR-4 / OBS-4 (Info) — Fail-closed direction correct; per-decision event log high-volume but gated
- Anchor: fail-closed comment stance still uniform (see `finalizeConditionalWrite` at line
  147-162, `checkPoolPreconditions` at line 55, `checkConditionalWriteSingleAttemptSupport`
  at line 93). Event sink still context-gated (`CasInstrumentedBackend.cpp` + `CasEvent.{h,cpp}`).
- Notes: Verified unchanged; both are correct-by-posture. ✅

---

## Findings from the user's expanded scope (BACKUP/RESTORE/ATTACH/FETCH/EXCHANGE/tooling)

### CAS-042 / BAK-1 / B-1 (Med) — Still present: BACKUP via temp hard links refused on non-Atomic (Ordinary) DBs
- Anchor: `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp:417-427`
- Trigger: `BACKUP TABLE t` on an Ordinary database whose disk is content-addressed.
- Evidence quote (line 422-427):
  > "if (make_temporary_hard_links && disk->isContentAddressed()) throw Exception(
  > ErrorCodes::SUPPORT_IS_DISABLED,
  > \"BACKUP via temporary hard links is not supported on a content_addressed disk yet
  > (B16/B34); use an Atomic database (which backs up via pointer-holding) instead ...\");"
- Notes: Atomic-DB pointer-holding BACKUP works (unchanged), Ordinary DBs still rejected fail-closed.
  Message explicitly names the audit codes B16/B34. Freeze on CAS is still wrapped by an
  owned transaction (`DataPartStorageOnDiskBase.cpp:535-544`) to avoid the B21 corruption mode.
  No CAS-specific BACKUP integration test in `tests/integration/` (grep of `test_cas_*` /
  `test_content_addressed_*` for BACKUP/RESTORE → no matches). Coverage gap persists.

### CAS-105 / BAK-4 / B-3 (Low–Med) — Still present: Packed storage-type parts unsupported; RESTORE round-trip untested on CAS
- Anchor: `src/Storages/MergeTree/MergeTreeData.cpp:5147-5168` (`choosePartFormat`).
- Trigger: RESTORE / ATTACH a Packed part written on a non-CAS disk onto a CAS disk.
- Evidence: current `choosePartFormat` returns `{PartType::(Wide|Compact), PartStorageType::Full}`
  unconditionally — no Packed path (grep for `Packed` in the CAS tree: no matches). CAS's per-file
  manifest model has no code for a single-file packed container.
- Notes: Also confirmed no `test_cas_*` / `test_content_addressed_*` integration test doing
  BACKUP→drop→RESTORE→CHECK TABLE on CAS. Both the incremental-backup dedup path (BAK-3) and
  the RESTORE round-trip (BAK-4) remain untested. Unchanged.

### CAS-109 (Med) — Still present in part: EXCHANGE TABLES, `clickhouse-disks` verbs, disk-layering untested on CAS
- Anchor:
  - EXCHANGE / RENAME TABLE: `.../ContentAddressedTransaction.cpp:1200-1249` (`moveDirectory`
    cross-namespace rename is best-effort, multi-op, non-atomic, idempotent on retry;
    partial failure logs "the table is SPLIT across namespaces" and rethrows).
  - `clickhouse-disks` tooling: `.../Tools/CasInspect.h:9` ("Read-only decode-to-JSON dispatch
    for `clickhouse-disks ca-inspect`"), `.../Tools/CasFsck.cpp`, `.../Tools/CasDecommission.cpp`;
    exposed verbs listed in `.../README.md:157` ("`clickhouse-disks` verbs (all require the
    disk opened read-only): `fsck` ...").
- Trigger:
  - `EXCHANGE TABLES a AND b` where both are on the same CAS pool → two consecutive
    cross-namespace `moveDirectory` calls, neither atomic w.r.t. the other; a crash between
    them leaves both tables partially split (idempotent on re-drive).
  - Any `clickhouse-disks` write verb against a CAS disk (deliberately gated to read-only —
    see README line 157).
- Notes: The `moveDirectory` RENAME path is explicit about the non-atomicity trade-off (line
  1216-1224): "There is no native cross-namespace atomicity ... true atomicity would need a
  durable move-journal (deliberately out of scope — it would touch the tested GC/journal
  layer)." EXCHANGE TABLES has no dedicated wrapper; it composes two rename halves via the
  same primitive. No integration test in `test_cas_*` / `test_content_addressed_*` exercises
  EXCHANGE TABLES on CAS or `clickhouse-disks` verbs end-to-end. Test-gap unchanged.
  The "tiny-part storm on system-log tables" perf shape is a Tier 2 SYS-1 issue; not
  re-verified here.

### CAS-110 / RPL-4 / RPL-5 / B-5 (Fixed → new residual) — FETCH-to-detached now DOES relink
- Original claim: "A `to_detached` fetch content-addresses the downloaded bytes into the
  `detached/` namespace instead of relinking to blobs already in the shared pool" (byte
  transfer, no dedup on that path).
- **Status in current code: ✅ fixed.**
- Anchor of fix:
  - Relink gate: `src/Storages/MergeTree/DataPartsExchange.cpp:697-704`:
    > "Gated on `allow_ca_relink` alone (B66b). ... The gate used to be
    > `try_zero_copy && !to_detached`, and BOTH halves were accidents of that same brake ...
    > `!to_detached` because the relink path staged at the ACTIVE part path and ignored
    > `to_detached`. `to_detached` is now a parameter of `relinkPartToDisk` (it stages under
    > the `detached/` parent) ..."
  - Relink call passes `to_detached`: `DataPartsExchange.cpp:944` — `relinkPartToDisk(part_name,
    tmp_prefix, disk, to_detached, sender_manifest_bytes, ...)`.
  - Receiver seam explicitly acknowledges the detached-namespace ref: `.../ContentAddressedExchange.h:50`
    (`ref_name; /// the ref the sender published the part under ("detached/<name>" for B66b)`),
    line 206-208 ("a relink into `TABLE/detached/DIR` (B66b) lands on the `detached/<dir>` ref
    for free, through the one router every other read and write of that part uses").
  - Fallback path continues to `downloadPartToDisk(... to_detached ...)` at
    `DataPartsExchange.cpp:971` and target-dir composition at line 1149 (
    `getRelativeDataPath() + (to_detached ? DETACHED_DIR_NAME : "")`).
- Residual (NEW): the ONLY integration test exercising CAS relink is
  `tests/integration/test_cas_replicated_relink/` — search for `to_detached` there is
  useful next work; grep didn't surface a dedicated `FETCH PART ... TO DETACHED` or
  `ALTER TABLE FETCH PARTITION ... FROM ...` test on CAS. **See NEW-tier4-1 below.**

---

## Findings fixed / no longer reproducible

- **CAS-110 / B-5 / RPL-4** — FETCH-to-detached now takes the relink path. See anchors above.

---

## New findings (not in original audit)

- **NEW-tier4-1 (Low, test-coverage)** — FETCH-to-detached relink correctness has code but
  no dedicated integration test. `ALTER TABLE ... FETCH PARTITION ... FROM ...` on CAS
  (which routes through `to_detached=true`) needs an integration test asserting that the
  received part lands as a relinked `detached/<name>` ref, not as a byte re-upload.
  Anchor for fix: `src/Storages/MergeTree/DataPartsExchange.cpp:697-704, 944` +
  `.../ContentAddressedExchange.h:50, 206-208`. Coverage gap: no test in
  `tests/integration/test_cas_*` currently pins B66b.

- **NEW-tier4-2 (Low, test-coverage)** — RENAME TABLE / cross-engine table move on CAS is
  best-effort non-atomic (documented at `ContentAddressedTransaction.cpp:1212-1248`), and
  the "SPLIT across namespaces" recovery path is idempotent by construction, but there is
  no integration test that injects a fault between the `republishRef` loop and
  `dropNamespace` and asserts idempotent re-drive. Given how many downstream properties
  hinge on this window (EXCHANGE TABLES composes two such halves), a dedicated fault-injection
  test would catch a future refactor that accidentally loses idempotency.

- **NEW-tier4-3 (Low, observability)** — A `CasBlobAdoptTrusted` ProfileEvent
  (`src/Common/ProfileEvents.cpp:900`) partially closes the original OBS-3 gap (relink
  hit-rate is now measurable at the "adoption" level), but there is still no counter
  distinguishing a **relink fetch** from a **byte fetch** in the replication log
  (`system.replicated_fetches` bytes-transferred remains the only signal). Not a regression;
  narrows OBS-3 from "no visibility" to "no per-fetch flag."

---

## By-design / N/A / info

- FREEZE on CAS via `DataPartStorageOnDiskBase.cpp:525-544` uses an owned transaction on a
  CAS disk to keep the whole clone in one part-ref (fixes the historical B21 corruption
  mode when caller passes no external transaction). BAK-2 "FREEZE is essentially free on CAS"
  remains ✅.
- The fail-closed refusal to mount a Native CAS on a non-S3 IObjectStorage
  (`checkConditionalWriteSingleAttemptSupport`) is by-design and correct.
- `clickhouse-disks` verbs against CAS are deliberately read-only-only
  (`README.md:157`) — a write verb would need its own transaction semantics; this is
  documented, not a bug.

---

## Verdict summary table

| ID | Old severity | Status | Evidence anchor |
|---|---|---|---|
| OSC-1 | High | 🔴 still-present | `Backend/CasObjectStorageBackend.cpp:143-146` |
| OSC-2 | High | 🔴 still-present | `Backend/CasObjectStorageBackend.cpp:55-84` |
| OSC-3 | Med  | 🔴 still-present (by-design fail-closed) | `Backend/CasObjectStorageBackend.cpp:93-109` |
| OSC-4 | Med  | 🔴 still-present | `Pool/CasPool.cpp:1327-1329` |
| ERR-1 | Med  | 🔴 still-present | `Backend/CasObjectStorageBackend.cpp` nativeConditionalPut + `Pool/CasPool.cpp` mutate loops |
| ERR-2 | Med  | 🔴 still-present | `ContentAddressedTransaction.cpp` abort + `Gc/CasGc*.cpp` sweeps |
| ERR-3 | Low  | 🔴 still-present (lifecycle-rule dependency) | (S3 client MPU path; not CAS-owned) |
| ERR-4 | Info | ⚪ info (verified correct) | `Backend/CasObjectStorageBackend.cpp:141` (fail-safe direction comment) |
| OBS-1 | Med  | 🔴 still-present | `Common/ProfileEvents.cpp:759-843` (no phys/logical/dedup gauges) |
| OBS-2 | Med  | 🔴 still-present | `Gc/CasGc*.cpp` (log-only; no liveness gauge) |
| OBS-3 | Low  | 🟡 partially addressed | `ProfileEvents.cpp:900` (`CasBlobAdoptTrusted`) narrows but doesn't close |
| OBS-4 | Info | ⚪ info (gated as claimed) | `Backend/CasInstrumentedBackend.cpp` + `CasEvent.{h,cpp}` |
| CAS-042 (BAK-1/B-1) | Med | 🔴 still-present | `MergeTree/DataPartStorageOnDiskBase.cpp:417-427` |
| CAS-105 (BAK-4/B-3) | Low–Med | 🔴 still-present | `MergeTree/MergeTreeData.cpp:5147-5168` + no CAS BACKUP/RESTORE test |
| CAS-109 (EXCHANGE/tooling test-gap) | Med | 🔴 still-present | `ContentAddressedTransaction.cpp:1200-1249` + `Tools/*` + no integration test |
| CAS-110 (B-5 / RPL-4/5) | Low | ✅ fixed | `DataPartsExchange.cpp:697-704, 944` + `ContentAddressedExchange.h:50, 206-208` |
| NEW-tier4-1 | Low | 🆕 test-gap | `DataPartsExchange.cpp:697-704` — no `FETCH … TO DETACHED` CAS test |
| NEW-tier4-2 | Low | 🆕 test-gap | `ContentAddressedTransaction.cpp:1212-1248` — no RENAME-fault idempotence test |
| NEW-tier4-3 | Low | 🆕 observability | `ProfileEvents.cpp:900` — narrows OBS-3, doesn't close it |
