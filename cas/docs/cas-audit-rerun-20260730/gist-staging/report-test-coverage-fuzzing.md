# test-coverage-fuzzing — re-run 2026-07-30

Static re-audit of CAS decoder fuzz coverage and specific CAS-side test gaps
against current PR HEAD (`altinity/cas-gc-rebuild`, worktree at
`/Volumes/workspace/ClickHouse`, branch `cas-audit-20260730`,
HEAD `834c9517f56`).

Scope (per user): CAS-010, CAS-012, CAS-098, CAS-103, CAS-105, CAS-110, CAS-117.

## Scope in current code

- Files/dirs walked:
  - `src/Disks/fuzzers/` — **does not exist**
    (verified: `ls: /Volumes/workspace/ClickHouse/src/Disks/fuzzers/: No such
    file or directory`). Only these `src/*/fuzzers/` trees exist:
    `AggregateFunctions`, `Compression`, `Core`, `DataTypes`, `Formats`,
    `Interpreters`, `Parsers`, `Storages`. No CAS decoder fuzzer under any of
    them (checked `Storages/fuzzers/` — only `columns_description_fuzzer.cpp`,
    `mergetree_checksum_fuzzer.cpp`).
  - `src/Disks/tests/` — **115 files** total, **100 CAS/CA gtests**
    (`gtest_cas_*` / `gtest_ca_*`). Every finding-adjacent codec has a *unit*
    test but none are libFuzzer / coverage-guided harnesses (assert-only,
    example-based inputs). Notable: `gtest_cas_envelope.cpp`,
    `gtest_cas_blob_envelope_format.cpp`, `gtest_cas_manifest_id.cpp`,
    `gtest_cas_part_manifest_format.cpp`,
    `gtest_cas_gc_state_format.cpp`, `gtest_cas_gc_outcomes_format.cpp`,
    `gtest_cas_fold_seal_format.cpp`, `gtest_cas_record_stream_format.cpp`,
    `gtest_cas_ref_snapshot_format.cpp`, `gtest_cas_ref_log_format.cpp`,
    `gtest_cas_server_root_format.cpp`, `gtest_cas_text_format.cpp`,
    `gtest_cas_ref_decode_bounds.cpp` (an explicit *bounds* unit test — still
    example-based). Search for anything named `_fuzz*` returns **zero** files
    inside `src/Disks/`.
  - `tests/queries/0_stateless/` — **66** `content_addressed`/`cas` scripts
    (numeric range 04278–05022). Enumerated in full during audit.
  - `tests/integration/` — 8 CAS-scoped integration suites:
    `test_cas_file_cache`, `test_cas_gc_sharded`,
    `test_cas_insert_fault_recovery`, `test_cas_lazy_load_recovery`,
    `test_cas_replicated_relink`, `test_content_addressed_drop_pool_member`,
    `test_content_addressed_gc_s3`, `test_content_addressed_ref_snaplog`,
    `test_content_addressed_s3`, `test_content_addressed_shared_pool`.
  - `utils/ca-soak/` — multi-backend docker-compose harness intact
    (`docker-compose-awss3.yml`, `docker-compose-gcs.yml`,
    `docker-compose-10replicas.yml`, `docker-compose-gc_shards{2,8}.yml`,
    `docker-compose-s3faultproxy.yml`, `docker-compose-small_dedup_cache.yml`).
    31 `tests/test_*.py` scenario/model files.

## Findings still present

### CAS-010 — no fuzzers for CAS decoders (envelope / run-file / manifest / root-shard / gc-formats / pool-meta) 🔴 still-present

- Anchor: **absence** — `src/Disks/fuzzers/` does not exist; no
  `LLVMFuzzerTestOneInput` target references any CAS decoder anywhere in
  `src/`. Verified by directory listing and by enumerating every
  `src/*/fuzzers/` sibling.
- Trigger: `git ls-files src/Disks/fuzzers/` → empty; `rg 'LLVMFuzzerTestOneInput' src/Disks/` → no matches.
- Evidence: only unit-test parity exists (e.g.
  `src/Disks/tests/gtest_cas_envelope.cpp`,
  `gtest_cas_blob_envelope_format.cpp`,
  `gtest_cas_part_manifest_format.cpp`,
  `gtest_cas_gc_state_format.cpp`,
  `gtest_cas_gc_outcomes_format.cpp`,
  `gtest_cas_fold_seal_format.cpp`,
  `gtest_cas_record_stream_format.cpp` (nearest RunFile analogue),
  `gtest_cas_server_root_format.cpp` — all assert-based, no fuzz harness).
  The reference harness the original audit called out
  (`src/Storages/fuzzers/mergetree_checksum_fuzzer.cpp`) still exists and is
  still not mirrored for CAS.
- Notes: The bounds-focused unit `gtest_cas_ref_decode_bounds.cpp` shows the
  team is aware of decoder-bounds risk but chose an example-based test rather
  than a fuzz target. Header-hash and size-arithmetic checks in
  `Formats/CasBlobEnvelopeFormat.cpp` reduce (but do not eliminate) OOB
  surface; `blob_header_len` is validated pool-wide by `validatePoolBlobHeaderLen`
  in `Formats/CasPoolMetaFormat.cpp` — those checks are only exercised on
  hand-picked inputs. All six decoders called out in the original FZ1 remain
  un-fuzzed.

### CAS-012 — native conditional-write untested on real S3/GCS 🔴 still-present

- Anchor: `src/Disks/tests/gtest_cas_backend_generation.cpp`,
  `gtest_cas_backend_contract.cpp` (in-process/mock backend only); no
  integration test drives conditional-PUT against a real endpoint.
- Trigger: `rg -i 'conditional|IfNoneMatch|If-None-Match|native' tests/integration/test_cas*/*.py` and `test_content_addressed_*/*.py` → **no matches**.
- Evidence: `test_content_addressed_s3` and `test_content_addressed_gc_s3`
  run against MinIO only; no GCS-backed integration test file exists.
  `utils/ca-soak/docker-compose-gcs.yml` is present but nothing in
  `utils/ca-soak/tests/` asserts *conditional* PUT semantics (the closest are
  `test_s3_transient_retry.py`, `test_transport_retry.py`, which model
  transport faults, not the If-None-Match / preconditions branch).
- Notes: The CAS write path's correctness against real S3 (IfNoneMatch → 412)
  and GCS (`x-goog-if-generation-match: 0` → 412) rests on unit-level mocks
  that do not fail-loud when a backend silently accepts overwrites. This is
  the exact "substrate everything relies on" the original audit flagged.

### CAS-098 — wide-part read branches untested 🔴 still-present

- Anchor: `src/Disks/tests/gtest_cas_part_write.cpp` is the only file whose
  contents reference `wide_part`; no dedicated read-side gtest covers the
  wide vs compact vs packed read branches on CAS
  (no `gtest_cas_read*`, no `gtest_cas_wide_part*`).
- Trigger: `rg 'wide_part|packed_part|MergeTreeReaderWide|MergeTreeReaderCompact' src/Disks/tests/` → only `gtest_cas_part_write.cpp`.
- Evidence: stateless coverage is functional-level
  (`04278_content_addressed_disk.sql`, `04299_/04300_/05000_*projection*`)
  and does not force part format across the branch matrix
  (`min_bytes_for_wide_part=0/1/threshold`, packed placement mixed with
  streamed blobs, projections wide + patch parts). The read pipeline in
  `ContentAddressedMetadataStorage::getStorageObjects` / `readBlobPayload` /
  `tryGetInManifestBytes` is exercised implicitly by high-level SELECTs but
  has **no branch-directed test** (see also `reports/read-protocol.md`).

### CAS-103 — MOVE vs GC untested 🔴 still-present

- Anchor: **absence** — `rg -i 'MOVE PART|MOVE PARTITION|move_part' tests/queries/0_stateless/*content_addressed*` finds only
  `04280_content_addressed_clone_partition_works.sql` (that test exercises
  `CLONE PARTITION`, not `MOVE ... TO DISK/VOLUME`); the same grep across
  `tests/integration/test_cas*/**` and `test_content_addressed_*/**` returns
  **no matches**.
- Trigger: No integration or stateless test issues `ALTER TABLE ... MOVE
  PART/PARTITION TO DISK|VOLUME` against a CAS disk while GC is active.
- Evidence: `ContentAddressedTransaction.cpp` supports `moveDirectory`
  (exercised by DROP / mutation flow via `gtest_cas_protocol_scenarios`) but
  the storage-policy MOVE path — which is the race window between the source
  ref removal and destination ref promotion under a shared-pool GC — has
  neither a stateless SQL test nor an integration test nor a ca-soak
  scenario (`utils/ca-soak/scenarios/` has no MOVE card).
- Notes: DUR2 / C-U1 face is present in `test_cas_insert_fault_recovery` /
  `test_cas_lazy_load_recovery` for INSERT and open/close, not for MOVE.

### CAS-105 — RESTORE + Packed untested 🔴 still-present

- Anchor: `tests/queries/0_stateless/05005_content_addressed_backup_restore.sh`
  covers BACKUP/RESTORE round-trip but `rg -i 'packed|Packed'` inside that
  file returns **no matches**. `gtest_cas_inline_placement.cpp` exercises
  inline (packed) placement at the storage layer, but no RESTORE test
  forces packed placement on restore or crosses RESTORE with packed
  detached parts.
- Trigger: `rg -i 'RESTORE|Packed' tests/queries/0_stateless/*content_addressed*` → only the two backup/restore scripts (`05005_*`, `04284_*`), neither of which touches the packed / inline-placement branch.
- Evidence: `04284_content_addressed_backup_pointer_holding.sh` asserts
  pointer-holding semantics, not packed-restore correctness. `ca-soak`
  scenarios lack a RESTORE card.

### CAS-110 — FETCH quorum / SYNC REPLICA untested on CAS 🔴 still-present (SYNC covered, quorum not)

- Anchor: `tests/integration/test_cas_replicated_relink/test.py` — uses
  `SYSTEM SYNC REPLICA` extensively (17 call sites at lines 284, 309, 313,
  318, 355, 519, 551, 557, 616, 684, 798, 868…) so *SYNC REPLICA is
  covered*. **`insert_quorum` is not**: `rg -i 'quorum|InsertQuorum'` across
  the entire suite returns **no matches**. No `cloneReplica` /
  lost-replica-recovery scenario either.
- Trigger: no integration test creates a `ReplicatedMergeTree` on CAS with
  `insert_quorum >= 2` and forces a fetch under quorum-lag.
- Evidence: matches original RPL-5 — "quorum inserts, SYSTEM SYNC REPLICA,
  lost-replica recovery (`cloneReplica`), and `REPLACE_RANGE`/`DROP_RANGE`
  log entries … no integration test exercising them against a CA disk."
  SYNC REPLICA is now covered; quorum + cloneReplica remain gaps.
- Notes: Downgrade severity vs original RPL-5 for SYNC portion; quorum
  branch is still the untested corner.

### CAS-117 — FINAL / patch-apply-on-read untested for CAS-specific concurrency 🔴 still-present (partial)

- Anchor: `tests/queries/0_stateless/04294_content_addressed_patch_parts.sh`
  — issues `OPTIMIZE TABLE t_ca FINAL` (line 75) to apply patch parts and
  asserts `final_rows_match` / `final_data_match` on a *single-server*
  table. `04293_content_addressed_lightweight_delete.sh` similarly uses
  `FINAL` on one node. `test_cas_replicated_relink/test.py:312, 758`
  exercises `OPTIMIZE TABLE ... FINAL` on replicated tables. What is
  **missing**: FINAL under **concurrent merge** + **parallel-replica
  reads**, plus patch-apply-on-read across a shared-pool GC condemn
  window.
- Trigger: no test drives `FINAL` while a background merge and a
  concurrent GC round race for the same ref set on a CAS disk; nothing
  enables `parallel_replicas` on a CAS table.
- Evidence: `rg -i 'parallel_replicas|allow_experimental_parallel_reading'
  tests/queries/0_stateless/*content_addressed*` → no matches. The
  correctness question posed by MVCC-3 (FINAL + patch-apply + parallel
  replicas → wide fan-in on manifest/shard decode caches, unverified
  under concurrent merge) is still un-answered by any test.

## Findings fixed / no longer reproducible

- **CAS-110 (SYNC REPLICA portion)** — the original T-G / RPL-5 blanket
  claim "SYNC REPLICA … no integration test exercising them against a CA
  disk" is *partly* fixed by `test_cas_replicated_relink/test.py` (17 SYNC
  REPLICA sites). Full finding remains open for the quorum + cloneReplica
  branch.
- **T-G / regression repro discipline** (from original section 1) — still
  strong: dedicated repros like `gtest_cas_b140_dangle.cpp`,
  `gtest_cas_gc_undercount_repro.cpp`,
  `gtest_cas_part_write_root_dangle.cpp` remain in tree; new additions
  since the original audit visible in the listing include
  `gtest_cas_ref_decode_bounds.cpp`, `gtest_cas_ref_install_safety.cpp`,
  `gtest_cas_ref_lane_exception_safety.cpp`,
  `gtest_cas_orphan_manifest_sweep.cpp`, `gtest_cas_bootstrap_ordering.cpp`,
  `gtest_cas_fence_generation.cpp`, `gtest_cas_confirm_exact_ref.cpp`. So
  the *unit* coverage is broader than in the original audit, but the fuzz
  gap is unchanged.

## New findings (not in original audit)

- **NEW-TCF-1 (Med)** — no GCS-backed integration test despite
  `utils/ca-soak/docker-compose-gcs.yml` being present. All `tests/integration/test_cas*`
  and `test_content_addressed_*` suites are MinIO/S3-only. GCS
  precondition semantics (`x-goog-if-generation-match: 0`) live entirely in
  the ca-soak surface, without an integration-tests-level assertion.
  Anchor: absence across `tests/integration/test_c*a*s*/test.py`.
- **NEW-TCF-2 (Low)** — `ca-soak/scenarios/` is model/checker-oriented
  (see `cards`, `framework`) but has no explicit **MOVE / RESTORE /
  quorum** cards even though it has the multi-replica infra
  (`docker-compose-10replicas.yml`) that would make them cheap. The
  scenarios listed (`test_aborted_retry`, `test_chaos_schedule`,
  `test_mount_fence_retry`, `test_stale_edge_verdict`, etc.) target
  fence/retry surfaces, not lifecycle/replication.
- **NEW-TCF-3 (Info)** — `gtest_cas_ref_decode_bounds.cpp` exists and is a
  natural seed corpus for a `cas_ref_decode_fuzzer`: converting its
  hand-crafted malformed inputs into a libFuzzer corpus is the
  lowest-friction path to shipping the first CAS fuzz target. Same
  observation for `gtest_cas_envelope.cpp` and the format-battery
  (`cas_format_test_battery.h`, `gtest_cas_format_battery.cpp`).

## By-design / N/A / info

- The multi-backend `ca-soak` harness genuinely covers write/GC/mount/codec
  core against real MinIO / GCS / rustfs at up to 10 replicas — the
  original audit's "excellent" characterization of core functional coverage
  still holds.
- CAS envelope reads validate header hash + size arithmetic
  (`Formats/CasBlobEnvelopeFormat.cpp`) and pool-wide `blob_header_len`
  (`validatePoolBlobHeaderLen`, `Formats/CasPoolMetaFormat.cpp`) — this is
  meaningful defense-in-depth but does **not** substitute for
  coverage-guided fuzzing of the six decoders.
- `SYSTEM SYNC REPLICA` coverage in `test_cas_replicated_relink` is now
  broad enough to consider SYNC REPLICA "covered" for the base fetch case.

## Verdict summary table

| CAS-id  | Old severity | Status                | Evidence anchor |
|---------|--------------|-----------------------|-----------------|
| CAS-010 | High         | 🔴 still-present      | `src/Disks/fuzzers/` absent; no `LLVMFuzzerTestOneInput` for envelope / run-file / manifest / root-shard / gc-formats / pool-meta in `src/`. Only unit tests: `src/Disks/tests/gtest_cas_envelope.cpp`, `gtest_cas_blob_envelope_format.cpp`, `gtest_cas_part_manifest_format.cpp`, `gtest_cas_gc_state_format.cpp`, `gtest_cas_gc_outcomes_format.cpp`, `gtest_cas_fold_seal_format.cpp`, `gtest_cas_record_stream_format.cpp`, `gtest_cas_server_root_format.cpp`, `gtest_cas_ref_decode_bounds.cpp`. |
| CAS-012 | High         | 🔴 still-present      | Only mock: `src/Disks/tests/gtest_cas_backend_generation.cpp`, `gtest_cas_backend_contract.cpp`. No `conditional`/`IfNoneMatch` string in `tests/integration/test_cas*/*.py` or `test_content_addressed_*/*.py`. No GCS integration test file. |
| CAS-098 | Med          | 🔴 still-present      | `src/Disks/tests/gtest_cas_part_write.cpp` is the only file mentioning `wide_part`; no dedicated wide/compact/packed read-branch gtest; stateless tests do not toggle `min_bytes_for_wide_part`. |
| CAS-103 | Med          | 🔴 still-present      | No `MOVE PART`/`MOVE PARTITION` grep hits in `tests/integration/test_c*a*s*/**` or `tests/queries/0_stateless/*content_addressed*` (only `04280_content_addressed_clone_partition_works.sql`, which does CLONE, not MOVE). No `ca-soak` MOVE scenario. |
| CAS-105 | Med          | 🔴 still-present      | `tests/queries/0_stateless/05005_content_addressed_backup_restore.sh` — no `Packed`/`packed` inside. `04284_content_addressed_backup_pointer_holding.sh` — pointer-holding only. No RESTORE + packed-placement crossover test. |
| CAS-110 | Med          | 🟡 partial-fix        | SYNC REPLICA covered (`tests/integration/test_cas_replicated_relink/test.py` lines 284, 309, 313, 318, 355, 519, 551, 557, 616, 684, 798, 868). Quorum + cloneReplica still uncovered (`rg 'quorum\|InsertQuorum' tests/integration/test_cas*/*.py` → 0 hits). |
| CAS-117 | Med          | 🔴 still-present      | `04294_content_addressed_patch_parts.sh:75` and `04293_content_addressed_lightweight_delete.sh` use FINAL single-node; `test_cas_replicated_relink/test.py:312, 758` uses FINAL replicated. No FINAL-under-concurrent-merge, no `parallel_replicas` on CAS, no patch-apply-vs-GC race test. |
| NEW-TCF-1 | Med (new)  | 🔴 still-present      | Absence across `tests/integration/test_c*a*s*/test.py` — no GCS integration despite `utils/ca-soak/docker-compose-gcs.yml`. |
| NEW-TCF-2 | Low (new)  | 🔴 still-present      | `utils/ca-soak/scenarios/` — no MOVE / RESTORE / quorum card. |
| NEW-TCF-3 | Info (new) | ⚪ info               | `gtest_cas_ref_decode_bounds.cpp`, `gtest_cas_envelope.cpp`, `cas_format_test_battery.h` are ready-made fuzz seed corpora. |

## Counts

- Files/dirs walked: `src/Disks/fuzzers/` (absent), `src/Disks/tests/` (115 files; 100 CAS gtests), `tests/queries/0_stateless/` (66 CAS scripts), `tests/integration/` (10 CAS suites), `utils/ca-soak/` (31 scenario tests + 7 docker-compose backends).
- Findings still-present: **6** (CAS-010, CAS-012, CAS-098, CAS-103, CAS-105, CAS-117).
- Findings partial-fix: **1** (CAS-110 — SYNC REPLICA covered, quorum + cloneReplica not).
- Findings fully fixed: **0**.
- New findings: **3** (NEW-TCF-1 GCS integration; NEW-TCF-2 ca-soak MOVE/RESTORE/quorum cards; NEW-TCF-3 fuzz seed corpora info).
