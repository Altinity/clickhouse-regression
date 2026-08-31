# CAS (`metadata_type = content_addressed` MergeTree backend) — consolidated audit tracking

This is a **tracking issue** for a static-analysis audit of the Content-Addressed Storage (CAS) MergeTree
disk backend.

**2026-08-31 update.** All 39 audits plus a distributed-systems audit and a usability audit were
redone from scratch against **PR #2159 head** after Filimonov's 2026-08-21 triage and the post-triage
fix series that landed before merge. **`CAS-###` IDs are unchanged** from the 2026-08-12 catalogue
that Filimonov triaged — they are not renumbered. Items that the code no longer has, or that
Filimonov already closed as by-design / not-a-bug / duplicate, are checked off below and dropped
from the open work list.

> [!IMPORTANT]
> Static/logical review only. Filimonov's 2026-08-21 per-id residuals are treated as the
> authoritative narrowing: a real code shape with an invented consequence is not re-raised.
> Locate by symbol; 2026-08-12 `CA/...` line numbers are stale.

### 📎 Audit reports

* **Original (2026-07-09)**: https://gist.github.com/vzakaznikov/8b0506a495187ce3d634385544beebea
* **Re-run vs PR #2073 (2026-07-30)**: https://gist.github.com/alsugiliazova/7fb1441688ff428cc0e0a18918077c26
* **Re-run vs PR #2159 (2026-08-12, code-only)**: https://gist.github.com/alsugiliazova/6dce01834f93cdb7cdbb2fc70d1efc5f
* **Re-run vs PR #2159 head (2026-08-31)**: https://gist.github.com/alsugiliazova/f1b74c378277ef4b6842178d89333d2d — all 39 per-audit reports + `distributed-systems.md` + `usability.md` + `RECONCILIATION-2031.md`.
* **Code pin**: `ceee42c51a06cb05e2c9a2d811ef7e1726825552` (`cas: admit worker renewals only over an Active keeper`). Merge commit on `antalya-26.6`: `a49d9ed`. No further CAS product commits on `antalya-26.6` after the merge.
* **PR**: [#2159](https://github.com/Altinity/ClickHouse/pull/2159) (merged 2026-08-26).

### Finding the full detail for a `CAS-###`

The checklist line is a one-line residual. For the full write-up, open the 2026-08-31 gist and
search for the id or the audit name (e.g. CAS-007 → `interleaving.md` / `security.md` /
`distributed-systems.md`; CAS-020 → `read-protocol.md` / `idisk-contract.md`).
`RECONCILIATION-2031.md` maps buckets. Historical write-ups stay in the 2026-08-12 gist.
Filimonov's per-id reasoning is in [this comment](https://github.com/Altinity/ClickHouse/issues/2031#issuecomment-5375157383) (2026-08-21).

### How to triage

1. **Check the box** once it is triaged (resolved, dismissed, or filed as its own issue).
2. Replace `resolution:` inline with a verdict.
3. Add reasoning as a **comment** referencing the `CAS-###` id.

`carried from prev CAS-###` provenance is unreliable (Filimonov). Do not use it.

---

## Closed on #2159 after the 2026-08-12 catalogue (do not re-open)

These were the four P1s plus the write-protocol rewrite. Verified gone at `ceee42c`.

* [x] **CAS-001** Shadow/`FREEZE` namespace is now `serverPrefix()`-scoped · `DATA-LOSS` — resolution: ✅ fixed (`335802a`, closes [#2212](https://github.com/Altinity/ClickHouse/issues/2212))
* [x] **CAS-040** Manifest entry path is escaped in both the record line and the banner; orphan sweep skips an undecodable manifest instead of aborting the pool · `INTEGRITY` — resolution: ✅ fixed (`2649bce`)
* [x] **CAS-058** `freezeRemote` clones into a content-addressed disk in one transaction · `FEATURE-GAP` — resolution: ✅ fixed (`84b30f6`, closes [#2173](https://github.com/Altinity/ClickHouse/issues/2173))
* [x] **CAS-106** CAS settings live under the `cas_` config-key prefix; the `non_cas_keys` skip-list is gone · `CONFIG` — resolution: ✅ fixed (`917600b`, closes [#2243](https://github.com/Altinity/ClickHouse/issues/2243))
* [x] **CAS-010** Empty conditional token / `putOverwrite` on blob create — blob publish is no longer conditional · — resolution: ✅ obsolete (`940b168`)
* [x] **CAS-031** Multipart `If-None-Match` on blob CREATE — `putIfAbsentStream` / `promoteStaged` / `conditionalCreateControlled` / `copyObjectConditional` are gone · — resolution: ✅ obsolete (`940b168`)
* [x] **CAS-088** Unconditional `resurrect` returning a token it did not write — `resurrect` is gone; `publishBlob` is tokenless by design · — resolution: ✅ obsolete (`940b168`; Filimonov already had this as partly / comments-only)
* [x] **CAS-103** Dedup counters incremented before admit — counters now fire only on a successful adopt · — resolution: ✅ fixed (`940b168`)
* [x] **CAS-070** `remount_running` latch / lost wakeup — closed by the mount-lease rewrite (`7f932d3`, `ceee42c`, closes [#2244](https://github.com/Altinity/ClickHouse/issues/2244))
* [x] **CAS-093** Text-index temp ref leak — already ✅ fixed in the 2026-08-21 triage

Also landed in the same series (not originally P1, but they change the model): per-row catalog
proof for the *writer* path (`83c03e2` — **GC ref-cleanup still uses whole-catalog stillness,
CAS-079**), GCS generation isolated to CAS requests (`b69051a`), detached-work drain (`205af29`).

---

## Still open — Filimonov-accepted residuals that HEAD still has

Priority is Filimonov's 2026-08-21 P2/P3, not the original audit High. Headlines are his residual,
re-verified at `ceee42c`.

### P2

* [ ] **CAS-007** Nested `server_root_id` (`a/b`) passes `validateServerRootId` while decommission ownership is `srid` or `srid + "/"` prefix, so `SYSTEM CAS DROP POOL MEMBER` on `a` deletes live member `a/b`'s namespaces and objects · `DATA-LOSS` — resolution: 🔴 still-present (Filimonov confirmed, P2) · `CasServerRoot.h` `validateServerRootId`; `CasDecommission.cpp` `victim_srid + "/"`
* [ ] **CAS-020** `getStorageObjects` still returns `StoredObject(location.key, path, location.length)` and drops the envelope offset. Same-description server-side copy (CAS S3 → another S3 disk on the same endpoint, including same-host BACKUP-to-S3) copies envelope bytes as file content. Cross-type MOVE to local uses `readFile`/`prepareRead` and is safe. Inline files still fail loud (empty key) · `INTEGRITY` — resolution: 🔴 still-present (Filimonov confirmed, P2) · `ContentAddressedMetadataStorage.cpp` `getStorageObjects`
* [ ] **CAS-004** residual: server-side `SYSTEM CAS GC REBUILD` is safe (holds the live GC lease, condemns nothing). Offline `clickhouse-disks cas-gc-rebuild` still has no mount-lease interlock against a live writer · `INTEGRITY` — resolution: 🔴 still-present (Filimonov partly, P2)
* [ ] **CAS-014** Placement classifier is still a closed suffix allowlist and still misses `primary.cidx`, `.mrk4`/`.cmrk4`, and secondary-index files. Not corruption (1 MiB cap + blob spill); cost is whole-file RAM buffer + a double write · `CORRECTNESS` — resolution: 🔴 still-present (Filimonov partly, P2)
* [ ] **CAS-015** / **CAS-049** Single-flight / recovery / SQL `SYSTEM CAS FSCK` / `GC RUN` have no query cancellation. Each inner I/O is still budgeted; what remains is `KILL QUERY` / `max_execution_time` do not terminate the verb, and SQL FSCK holds `lifecycle_mutex` for the whole scan · `LIVENESS` — resolution: 🔴 still-present (Filimonov partly, P2)
* [ ] **CAS-022** Orphan-manifest sweep still nominates a manifest whose namespace has no catalog row (body is written before the catalog row). Window is narrow; outcome is loud, not silent data loss · `DATA-LOSS` — resolution: 🔴 still-present (Filimonov partly, P2)
* [ ] **CAS-032** Pool identity is still not bound to endpoint/bucket. Harm still requires writing into a CRR destination / bidirectional replication over the prefix · `INTEGRITY` — resolution: 🔴 still-present (Filimonov partly, P2) · docs residual
* [ ] **CAS-034** Per-round ref-cleanup / janitor budgets can sit below the creation rate. Consequence is deferred reclamation, not data loss · `LEAK` — resolution: 🔴 still-present (Filimonov partly, P2)
* [ ] **CAS-035** A GC round still fully lists `cas/ns/stream/` and retains every key in memory (also on rounds that then defer). Default `gc_shards=1` · `PERF/SCALE` — resolution: 🔴 still-present (Filimonov confirmed, P2)
* [ ] **CAS-044** Aggregate 16 MiB inline-data limit per manifest is still checked only in `stageManifest` with no reclassification to a blob. INSERT/merge fails loud and reproducibly · `FEATURE-GAP` — resolution: 🔴 still-present (Filimonov confirmed, P2)
* [ ] **CAS-045** Part-folder cache entry weight is still always 256 bytes (`Resolved::manifest_size` hardcoded 0). `part_folder_cache_bytes` and the oversized-bypass threshold are inoperative · `PERF/SCALE` — resolution: 🔴 still-present (Filimonov confirmed, P2)
* [ ] **CAS-046** Local scratch is still the part's full bytes, unreserved, unaccounted, deleted only at transaction end, no startup cleanup. Failures are loud (`ENOSPC`) · `PERF/SCALE` — resolution: 🔴 still-present (Filimonov confirmed, P2)
* [ ] **CAS-050** `CasGcScheduler::stop` still joins thread objects outside the mutex that guards them (reachable via `DROP POOL MEMBER` concurrent with GC STOP/shutdown) · `CONCURRENCY` — resolution: 🔴 still-present (Filimonov partly, P2)
* [ ] **CAS-055** Carry-forward `createHardLink` still ForceFresh-resolves the source per file. Default `part_folder_validate=always` ⇒ one manifest HEAD per file. Fix is still transaction-level memoization as in `unlinkFile` · `PERF/SCALE` — resolution: 🔴 still-present (Filimonov confirmed, P2)
* [ ] **CAS-061** Only `gc/state` has a rebuild path; catalog / `_ckpt` / `_pool_meta` fail closed. All CA tools still open via `_pool_meta` · `OBSERV/DAY2` — resolution: 🔴 still-present (Filimonov partly, P2)
* [ ] **CAS-065** Native `If-None-Match` runs in CAS-over-S3 CI; still missing a required GCS-generation lane and a Native row in the backend contract suite · `TEST-GAP` — resolution: 🔴 still-present (Filimonov partly, P2)
* [ ] **CAS-074** Generation prune still advances `snap_pruned_through` past a referenced generation; the compensating hand-off is one-shot and lost under `suppress_destructive`. `runFsck` still never lists `gc/`, so the promised fsck backstop does not exist · `LEAK` — resolution: 🔴 still-present (Filimonov partly, P2)
* [ ] **CAS-079** GC `cleanupRefObjects` still requires the pool-global catalog token to be unchanged for the whole remaining pass and bails out of the phase on any CREATE/DROP. `83c03e2` fixed this class only on the ref-*writer* path · `LEAK` — resolution: 🔴 still-present (Filimonov confirmed, P2) · `CasGc.cpp` `cleanupRefObjects`
* [ ] **CAS-081** S3 staging objects are still retained on abort (deliberate resurrect/promote source). Residuals: no periodic cleanup during a mount, no introspection. `DROP POOL MEMBER` still drains a dead member · `LEAK` — resolution: 🔴 still-present (Filimonov partly, P2)
* [ ] **CAS-085** `always_use_copy_instead_of_hardlinks=1` still makes mutations and same-disk clones throw `NOT_IMPLEMENTED`; the setting is never rejected. Fail-closed, no corruption · `FEATURE-GAP` — resolution: 🔴 still-present (Filimonov partly, P2)
* [ ] **CAS-092** residual: `CLOCK_BOOTTIME` still has no non-Linux fallback (Darwin). The "different clocks for fence and request" half stays refuted · `CORRECTNESS` — resolution: 🔴 still-present (Filimonov partly, P2)
* [ ] **CAS-098** `last_success_age_seconds=0` still means both "never led" and "succeeded just now"; `is_leader=0` does not separate a stopped GC from a follower · `OBSERV/DAY2` — resolution: 🔴 still-present (Filimonov partly, P2)
* [ ] **CAS-107** `ContentAddressedMetadataStorage` still does not override `applyNewSettings`. `SYSTEM RELOAD CONFIG` applies no `cas_*` setting and does not log that fact. A disk removed from config keeps renewing its mount lease until restart · `CONFIG` — resolution: 🔴 still-present (Filimonov confirmed, P2)
* [ ] **CAS-111** 64 MiB encoded snapshot / removal cap still hard-limits a table at ~0.6–0.9 M refs. Loud fail-closed before any object is created · `PERF/SCALE` — resolution: 🔴 still-present (Filimonov confirmed, P2)
* [ ] **CAS-112** Every committed positive ref chunk still does a fresh uncached GET + full decode + linear scan of the pool-global `cas/ref_catalog` · `PERF/SCALE` — resolution: 🔴 still-present (Filimonov partly, P2)
* [ ] **CAS-114** Recovery still closes every skipped writer epoch with its own durable pair. First touch of a long-idle table is O(mount count) sequential writes with no cap · `PERF/SCALE` — resolution: 🔴 still-present (Filimonov confirmed, P2)

### P3 residuals still confirmed (keep only the residual, not the original headline)

* [ ] **CAS-005** residual: no multi-ref atomicity; no rollback of a committed-ref repoint; `dropRefIfMatches` is still best-effort `noexcept`. Ordinary INSERT uses unique part names and does not take the repoint branch · `DATA-LOSS` — resolution: 🔴 still-present (Filimonov partly, P3)
* [ ] **CAS-006** residual: cross-namespace `RENAME`/`moveDirectory` is still a journal-less per-ref walk. Nothing is physically deleted; only non-Atomic (deprecated Ordinary) databases reach a true table rename · `DATA-LOSS` — resolution: 🔴 still-present (Filimonov partly, P3)
* [ ] **CAS-009** residual: upload still never re-hashes local scratch; a length-preserving scratch divergence can publish under the wrong digest. Presence-only admit of an already-stored body stays 📐 by-design (CAS-008) · `INTEGRITY` — resolution: 🔴 still-present (Filimonov partly, P2/P3)
* [ ] **CAS-017** residual: `dropNamespace` still latches admission closed before the durable work; a failed recovery empty-catch can leave the latch closed until remount. Not a permanently-broken table on every transient error · `LIVENESS` — resolution: 🔴 still-present (Filimonov partly, P3)
* [ ] **CAS-029** / **CAS-030** Versioning is still queried only on the GCS generation dialect; ETag mounts rely on the delete-marker probe. `skip_access_check` still skips the probe on ETag writable mounts · `CONFIG` — resolution: 🔴 still-present (Filimonov partly, P3)
* [ ] **CAS-037** residual: `location.offset + location.length` can still wrap and collapse the read window to EOF; GC generation listing still uses `std::stoull` (`-1` → `max_gen + 1 == 0`). Central "wrapping defeats every decoder gate" stays untenable · `DECODE/DoS` — resolution: 🔴 still-present (Filimonov partly, P3)
* [ ] **CAS-048** Empty covering-part publish still runs under `DataPartsLock` (DROP/REPLACE PARTITION). Same class as an ordinary object-storage disk writing a part under that lock · `LIVENESS` — resolution: 🔴 still-present (Filimonov partly, P3)
* [ ] **CAS-086** residual: a repeated `FREEZE WITH NAME` silently merges into the existing shadow ref instead of `DIRECTORY_ALREADY_EXISTS` · `CORRECTNESS` — resolution: 🔴 still-present (Filimonov partly, P3) · this is also the "audit-missed" item Filimonov named on 2026-08-21
* [ ] **CAS-090** residual: SSE-C + `staging_backend=s3` still uses server-side copy without copy-source customer-key headers. Fail-closed mount probe falls back to local staging; combination is optional · `SECURITY` — resolution: 🔴 still-present (Filimonov partly, P3)
* [ ] **CAS-094** A refused / CAS-losing rebuild still leaves run objects + a fold seal. Next-round-adopts-it and leaks-forever stay false · `INTEGRITY` — resolution: 🔴 still-present (Filimonov partly, P3)
* [ ] **CAS-095** `cas-gc-dryrun` is still silently `preview_deletes=0` on a missing `gc/state` · `OBSERV/DAY2` — resolution: 🔴 still-present (Filimonov partly, P3)
* [ ] **CAS-097** `cas-inspect` still cannot decode pool meta / catalog / owner / epoch / GC outcomes · `OBSERV/DAY2` — resolution: 🔴 still-present (Filimonov partly, P3)
* [ ] **CAS-124** Empty content under cityhash128 still aliases fsck's unparsable-key sentinel. Confined to one fsck classification line · `INTEGRITY` — resolution: 🔴 still-present (Filimonov partly, P3)
* [ ] **CAS-128** Staged-source inline `createHardLink`/`moveFile` into a dest with no build still fails closed at commit (`LOGICAL_ERROR`). `writeFile` itself now calls `buildFor` · `CORRECTNESS` — resolution: 🔴 still-present (Filimonov partly, P3)

---

## New this round (not in the 2026-08-12 catalogue)

* [ ] **CAS-136** `SYSTEM CAS GC RUN` with no disk name fans out to both the raw CAS disk and its `DiskObjectStorageCache` wrapper and runs two sequential rounds on the same metadata storage · `OBSERV/DAY2` — resolution: 🆕 new · `InterpreterSystemQuery.cpp` + `DiskObjectStorageCache.cpp`
* [ ] **CAS-137** Production UniqueKey (`MergeTreeBitmapStore` → `DeleteBitmapFileOps::writeBitmapToStorage`) and `SSTIndexWriter` still do `writeFile(.tmp)` + `replaceFile` on the part storage. On CAS that `replaceFile` opens a *new* transaction and throws `LOGICAL_ERROR` ("moveFile source not staged"). Filimonov marked **CAS-057** 🚫 not-a-bug on the claim that `writeBitmapToStorage` has no production caller — that caller exists (`MergeTreeBitmapStore.cpp`). UniqueKey-on-CAS is still fail-loud, not silent corruption · `FEATURE-GAP` — resolution: 🆕 / re-open residual of CAS-057

---

## Adjudicated — no action (Filimonov 2026-08-21, still true on HEAD)

Do not re-raise these as defects. Docs gaps (lifecycle / trust boundary / crypto-shred) stay documentation, not code work, unless called out above.

* [x] **CAS-002** `adoptEvidence` / §4 manifest-trust · 📐 by-design
* [x] **CAS-008** Default cityhash128, no re-hash on read · 📐 by-design
* [x] **CAS-012** Lifecycle / Object Lock / Glacier fail-open · 📐 by-design + docs (Glacier still has no restore-and-retry; keep as docs under CAS-029/032 if wanted)
* [x] **CAS-013** Algorithm admission raises `min_reader_generation` · 📐 latent; format floor already equals `G_BUILD` (now 10)
* [x] **CAS-024** Two CAS disks, one pool, one `server_root_id` · 🚫 not-a-bug (second mount `ABORTED`)
* [x] **CAS-025** REBUILD resets the condemn universe · 📐 by-design (R4 retention)
* [x] **CAS-026** Relink identity is not just `pool_uuid` · 📐 by-design
* [x] **CAS-027** Bucket credential is the trust boundary · 📐 by-design
* [x] **CAS-028** Unsalted content-hash keys · 📐 by-design (CAS dedup)
* [x] **CAS-033** Pool-wide `suppress_destructive` · 📐 by-design (fail-closed)
* [x] **CAS-042** / **CAS-122** One global generation; producerless `!` key · 📐 by-design / duplicate (recreate-only policy; pool format is now generation 10)
* [x] **CAS-047** Process-wide 16-thread upload pool, blocking enqueue · 📐 by-design (backpressure)
* [x] **CAS-052** `shared_from_this` on pool · 🚫 not-a-bug
* [x] **CAS-057** `moveFile`/`replaceFile` LOGICAL_ERROR on unstaged source · 🚫 not-a-bug (fail-loud stub) — see **CAS-137** if UniqueKey-on-CAS is in scope
* [x] **CAS-059** / **CAS-060** Encrypted disk over CAS · 📐 out-of-scope; fails loud at first blob write. Docs list it (`8779adc`, #2213). Missing fail-fast gate is the only residual
* [x] **CAS-064** No decoder fuzzer · 📐 by-design
* [x] **CAS-066** Emulated mode chosen by storage type · 📐 by-design
* [x] **CAS-068** `putIfAbsentControlled` swallows local failures as ambiguity · 📐 by-design
* [x] **CAS-071** Mount-keeper races · 📐 by-design
* [x] **CAS-073** Condemn marker not incarnation-scoped · 📐 by-design
* [x] **CAS-076** Seal-before-`gc/state` · 🚫 not-a-bug (prefix prune collects unaccepted seals)
* [x] **CAS-080** Snapshot publish only on write · 🚫 not-a-bug (also on read)
* [x] **CAS-083** LWD does not free surviving-entry blob bytes · 📐 by-design
* [x] **CAS-087** `detached`/`moving` parser order · 📐 by-design (Ordinary only)
* [x] **CAS-089** Envelope offset from pool meta · 📐 by-design
* [x] **CAS-110** `allow_stale` discarded · 📐 by-design (resolve is always fresh)
* [x] **CAS-125** `Xxh3Streamer` null deref · 🚫 not-a-bug
* [x] **CAS-126** Fence pre-check only on S3 staging · 📐 by-design
* [x] **CAS-129** Epoch check only at `promote` entry · 🚫 not-a-bug
* [x] **CAS-132** Path disclosure to unprivileged SQL · 🚫 not-a-bug (`GLOBAL` privileges)

P3 "partly" items whose only leftover is cosmetic (dead comments, always-zero ProfileEvents,
debug/sanitizer asserts, emulated-mode mutex, `readLine` allocation, cache-hit log volume,
`oc` optional default, write-side line-cap on `gc/state`) are **dropped from this body**.
They remain in the 2026-08-12 gist if anyone wants them. Re-raise only if the residual
grows a production consequence.

---

## Where to start (2026-08-31)

The four P1s are done. Next, in this order:

1. **CAS-007** — reject nested / prefix-overlapping `server_root_id` (operator-reachable data loss on `DROP POOL MEMBER`).
2. **CAS-020** — return a payload window from `getStorageObjects`, or refuse server-side copy on a CA source (silent wrong bytes on same-endpoint S3 copy / same-host BACKUP-to-S3).
3. **CAS-079** — revalidate the target catalog row in GC ref-cleanup, not the pool-global token (same class already removed from the writer).
4. **CAS-049** — give SQL FSCK a deadline and honor `KILL QUERY`.
5. **CAS-107** — `applyNewSettings` or a loud "restart required"; stop the keeper when the disk disappears from config.
6. **CAS-086** — repeated `FREEZE WITH NAME` should not silently merge.

Operator guardrails until those land: single-segment unique `cas_server_root_id`; never `DROP POOL MEMBER` on a prefix of a live id; do not BACKUP/MOVE CAS data onto another S3 disk with the same data-source description; use `clickhouse-disks cas-fsck --timeout` on large pools; restart after `cas_*` XML changes; do not wrap CAS in `DiskEncrypted`.

k-morozov (2026-08-18) on CAS-002 / CAS-003 / CAS-005 / CAS-006 is consistent with Filimonov's later verdicts (manifest-trust is architectural; GC dual-leader is extra work not split-brain; multi-ref / rename are known non-atomic). Those four stay in the residual list above, not as High.

---

## Coverage of this re-run

| Batch | Result |
|---|---|
| 39 named audits | re-run from scratch at `ceee42c`; reports in the 2026-08-31 gist |
| Distributed-systems | 1 High (CAS-007), 6 Medium, 3 Low |
| Usability (operator) | overall **ready with caveats (guardrails required)** |
| Tier-1 happy path (INSERT / SELECT / merge / relink / GC / FSCK) | no confirmed blockers |

Happy path is clear. Remaining work is admin-verb safety (decommission prefix, FSCK cancel, reload),
one silent copy-path integrity bug (CAS-020), and the scale/ops residuals Filimonov already accepted.
