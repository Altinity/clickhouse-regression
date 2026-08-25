# test-coverage-fuzzing -- fresh audit 2026-08-12

## Scope (incl. why tests are read from the base commit)

Static, read-only audit of the CAS test estate in `/Volumes/workspace/altinity-clickhouse/ClickHouse`,
branch `cas-code-only-strip`, base commit `842f2b37b8f`. No edits, no checkout, no execution.

**Tests are read from the base commit, not the working tree.** The `cas-code-only-strip` working tree
has every CAS test *deleted* — 128 `src/Disks/tests/gtest_cas_*.cpp` files (including
`gtest_cas_backend_contract.cpp`), the CAS stateless cases in the `04278`–`05023` range, and all ten
`tests/integration/test_cas_*` suites. That deletion is an artifact of the code-only strip used to
produce the review branch; it is **not** the PR's state. Every inventory number and file path below
was obtained via `git ls-tree -r --name-only 842f2b37b8f` and `git show 842f2b37b8f:<path>`, so the
audit reflects what the PR actually ships.

Method: enumerate names exhaustively, read a representative subset in full
(`gtest_cas_backend_contract.cpp`, `cas_format_test_battery.h`, `cas_sweep_test_support.h`,
`gtest_cas_backend_generation.cpp`, `gtest_cas_fsck.cpp`, `gtest_cas_gc_rebuild.cpp`,
`gtest_cas_mount.cpp`, `gtest_cas_settings.cpp`, `ci/defs/altinity_jobs.py`,
`ci/jobs/functional_tests.py`, `ci/jobs/unit_tests_job.py`, three integration `storage_conf.xml`),
and grep the rest by test-name and symbol. No claim below rests on a file I did not open or on a
grep I did not run.

## Test inventory at 842f2b37b8f

| Layer | Count | Location / notes |
| --- | --- | --- |
| Unit (gtest) | 128 files, 1941 `TEST*` macros | `src/Disks/tests/gtest_cas_*.cpp`; plus `gtest_ca_wiring.cpp` and three shared headers (`cas_test_helpers.h`, `cas_format_test_battery.h`, `cas_sweep_test_support.h`) |
| Stateless / functional | 44 `.sql`/`.sh` scripts | `tests/queries/0_stateless/04278_cas_disk` … `05023_cas_dropns_leaked_namespace`; all tagged `no-fasttest` |
| Integration | 10 suites, ~28 test functions | `tests/integration/test_cas_{s3,gc_s3,gc_sharded,shared_pool,replicated_relink,drop_pool_member,ref_snaplog,file_cache,insert_fault_recovery,lazy_load_recovery}` |
| Benchmark | 1 | `.../ContentAddressed/benchmarks/benchmark_cas_ref_protocol.cpp` |
| CAS fuzz targets | **0** | no `src/Disks/**/fuzzers/`, no `*_cas*_fuzzer.cpp`, no `tests/fuzz/*cas*.options` |

CI wiring:

| Job | Definition | What it runs |
| --- | --- | --- |
| Unit tests | `ci/defs/job_configs.py:145` → `ci/jobs/unit_tests_job.py` | whole `unit_tests_dbms` binary, filter `-FunctionsStress.*:SilkFiberSocketTest*` — all 1941 CAS gtests ride the generic lane; there is no CAS-specific unit job or sanitizer matrix beyond the generic one |
| CAS-over-S3 functional | `ci/defs/altinity_jobs.py:74-115` (`cas_functional_tests_jobs`) | `amd_binary`, `arm_binary`, `amd_asan_ubsan` (2 shards), `amd_tsan` (2 shards), `amd_msan` (3 shards); option `cas s3 storage` → `--cas-s3-storage` |
| CAS-over-local functional | `ci/defs/altinity_jobs.py:116-120` | `amd_binary` only, option `cas storage` → `--cas-storage` |
| Object store used by the S3 lane | `ci/jobs/functional_tests.py:652` | **RustFS**, started in place of / alongside MinIO because MinIO OSS does not enforce conditional DELETE and the fail-closed probe rejects it |
| Integration object store | `tests/integration/test_cas_*/configs/storage_conf.xml` | also **RustFS** (`http://rustfs1:11121/test/...`); no `with_minio` anywhere under `test_cas_*` |

Notable: the S3 sanitizer lanes are sharded specifically because an unsharded lane exceeds the 6h
GitHub timeout — a standing signal that the CAS functional estate is already at the edge of its CI
budget.

## Coverage map by subsystem

| Subsystem | Verdict | Evidence / absence |
| --- | --- | --- |
| Write path (part write txn, blob upload, dedup) | Covered | `gtest_cas_part_write.cpp`, `gtest_cas_writer_duties.cpp`, `gtest_cas_blob_upload_pool{,_env}.cpp`, `gtest_cas_upload_fanout.cpp`, `gtest_cas_parallel_commit.cpp`, `gtest_cas_inline_placement.cpp`; `04285_cas_deduplication_window_inline_disk.sql`, `05006_cas_deduplication_blob_insert.sql` |
| Read path (manifest reader, part folder view, ns file) | Covered | `gtest_cas_part_folder_{access,view}.cpp`, `gtest_cas_ns_file_read_contract.cpp`, `gtest_cas_namespace_file_request_profile.cpp`, `gtest_cas_ref_read_contract.cpp`, `gtest_cas_recovery_streaming.cpp` |
| GC normal round (fold, sweep, source edges, shards) | Covered | 20 `gtest_cas_gc_*.cpp` (`_round`, `_fold`, `_attempt`, `_bounded_walk`, `_frontier_gate`, `_ack_floor`, `_shard_plan`, `_shard_incarnation`, `_source_edge`, `_leak`, `_undercount_repro`, …); `test_cas_gc_s3`, `test_cas_gc_sharded`, `04279_cas_gc.sql` |
| GC rebuild / fsck | Covered | `gtest_cas_gc_rebuild.cpp` (15 tests incl. `LeaseConflictRefuses`, `CheckpointSnapshotAtOlderEpochSealFailsClosed`), `gtest_cas_fsck.cpp` (~42 tests incl. a `CASFsckAuthority` family); `05019_cas_fsck_access.sh`, `05020_cas_fsck.sh`, `05011_cas_gc_rebuild_access.sh` |
| Mount lease / epoch fencing | Covered | `gtest_cas_mount.cpp` (61 tests: lease renew, double-start, await-expiry incl. `SkewedFarFutureExpiryHasNoEffectOnObservationThreshold`, writer-epoch monotonicity), `gtest_cas_fence_generation.cpp` (9 tests), `gtest_cas_heartbeat.cpp`; `test_cas_shared_pool` for the two-server case |
| Ref ledger / checkpoint | Covered | `gtest_cas_ref_{ledger-adjacent}` family: `_ckpt`, `_ckpt_join`, `_catalog`, `_cow_map`, `_cow_manifest_set`, `_intake`, `_statemachine`, `_install_safety`, `_snapshot_publish_ordering`, `_recovery_cas_walk`; `test_cas_ref_snaplog` |
| Formats / decoders | **Thin** | 14 of the 18 live `FormatId`s register with `runFormatBattery`; **`RunFile` (13), `RefCkpt` (23), `GcMaintenanceState` (25) do not** — they only get bespoke trait/cap assertions (`gtest_cas_ref_ckpt.cpp:407`, `gtest_cas_gc_maintenance_state_format.cpp:29`). The battery itself only mutates by line-boundary truncation, in-header truncation, `v+1`, wrong-type, and leading garbage — no bit flips, no random payloads |
| Backend conditional-write dialects | **Thin** | `gtest_cas_backend_contract.cpp` parameterizes 19 contract tests over exactly two backends: `InMemoryBackend` and `ObjectStorageBackend` in `Mode::EmulatedSingleProcess` over `LocalObjectStorage` (lines 250-258). `Mode::Native` appears only in `gtest_cas_backend_generation.cpp`, still over `LocalObjectStorage`, with the dialect faked via `setNativeTokenTypeForTest(TokenType::Generation)` |
| Relink / fetch | Covered | `test_cas_replicated_relink` (10 tests: relink happy path, cross-pool byte fallback, legacy-peer mix, recursion brake, source-dropped window, stalled publish), `gtest_cas_confirm_exact_ref.cpp`, `gtest_cas_repoint.cpp`; `05002_cas_fetch_partition.sql` |
| Decommission | Covered | `gtest_cas_decommission.cpp`, `gtest_cas_decommission_catalog_duties.cpp`, `gtest_cas_retirement_sweep.cpp`; `test_cas_drop_pool_member` (incl. SIGKILL of node2 and lease expiry); `05013_system_cas_drop_pool_member.sql`, `05016_cas_drop_pool_member_access.sh` |
| Settings validation | **Thin** | `gtest_cas_settings.cpp` has 6 tests (defaults, unknown-key rejection, object-storage key skip, `ValidateFailsClosed`, scratch-path anchoring). One fail-closed test for the whole settings surface; no per-setting boundary matrix. `gtest_cas_mount.cpp:896` adds one cross-setting consistency case (`RefusesWritableOpenWithInconsistentCasRequestBudget`) |
| System tables | Covered | `gtest_cas_event_log.cpp`, `gtest_cas_gc_log.cpp`, `gtest_cas_observability.cpp`; `05009_cas_event_log.sql`, `05010_cas_mounts_gc_health.sh`, `05012_cas_mounts_typed_columns.sql`, `05007_cas_gc_introspection.sh` |
| Real GCS (generation-token) dialect | **Absent** | no GCS CI lane in `ci/defs/altinity_jobs.py`; no `gcs` fixture under `tests/integration/test_cas_*`; every generation-token test is `Mode::Native` over `LocalObjectStorage` + `setNativeTokenTypeForTest` |
| Fuzzing of any CAS decoder | **Absent** | see below |
| Property-based / invariant testing | **Absent** | see below |

## Structurally untestable seams

These are seams the current harness *cannot* reach, not merely ones nobody wrote a test for. Listing
them separately keeps them out of the findings, except where a cheap proxy exists and is missing.

| Seam | Why the harness cannot reach it | Closest proxy that exists |
| --- | --- | --- |
| Real S3/GCS conditional-write semantics | `ContentAddressedMetadataStorage.cpp:690` auto-selects `Mode::EmulatedSingleProcess` whenever `object_storage->getType() == ObjectStorageType::Local`. Every gtest builds on `LocalObjectStorage`, so a unit test physically cannot enter the native `If-Match`/`If-None-Match`/generation path unless it fakes the token type | RustFS in the functional and integration lanes — a real S3 dialect, but one implementation, and neither AWS S3 nor GCS |
| Multi-node races | gtests are single-process; the emulated backend's token state is per-process by construction (the code comments this explicitly at `ContentAddressedMetadataStorage.cpp:706`) | two-node `test_cas_shared_pool`, `test_cas_gc_sharded`, `test_cas_replicated_relink`, `test_cas_drop_pool_member` — real but coarse, ~a handful of interleavings |
| Crash-at-step-N durability | No deterministic crash injection: nothing kills the process between a chosen pair of object-store calls. Integration crashes are whole-process SIGKILL at hand-picked points (`test_cas_shared_pool/test.py:265`, `test_cas_drop_pool_member/test.py:146`, `test_cas_gc_sharded/test.py:255`) | in-process `*_for_test` hooks (e.g. `gc_verb_admit_window_hook_for_test`) simulate the *window* but not the durability boundary |
| Clock skew | No global fake clock; lease tests advance a local clock only | `gtest_cas_mount.cpp` `CASMountAwaitExpiry` family, incl. `SkewedFarFutureExpiryHasNoEffectOnObservationThreshold` — good for leases, absent for GC grace windows and `BlobMeta` freshness |
| Mixed-version pools | No harness runs two different CAS builds against one bucket | `test_cas_replicated_relink::test_version_mix_legacy_peer_gets_bytes` (protocol-level only), the `v+1` gate in `runFormatBattery`, and `changePoints()` assertions in `gtest_cas_format.cpp` |
| Throttling / 503 storms | No fault proxy in-tree on this side; RustFS is not made to throttle | `gtest_cas_request_control.cpp`, `gtest_cas_operation_gate.cpp` at the budget layer only |

## Fuzzing posture

The repository has 20 fuzz targets (`src/{AggregateFunctions,Compression,Core,DataTypes,Formats,
Interpreters,Parsers,Storages}/fuzzers/`, `programs/{local,server}/fuzzers/`) with matching
`tests/fuzz/*.options`, plus `ci/jobs/fuzzers_job.py`, `ci/jobs/libfuzzer_test_check.py`, and
`ci/workflows/nightly_fuzzers.py`.

**Not one of them targets CAS.** There is no `src/Disks/**/fuzzers/` directory at all
(`git ls-tree -r --name-only 842f2b37b8f | rg '^src/Disks/.*fuzz'` returns nothing), no
`tests/fuzz/*cas*` options file, and no CAS entry in the nightly fuzzer workflow. Stated plainly:
**zero CAS decoders are fuzzed**, even though every `Formats/` decoder — `CasPartManifestFormat`,
`CasRefLogFormat`, `CasRefSnapshotFormat`, `CasRefCkptFormat`, `CasRefCatalogFormat`,
`CasBlobMetaFormat`, `CasBlobEnvelopeFormat`, `CasFoldSealFormat`, `CasGcStateFormat`,
`CasGcOutcomesFormat`, `CasGcMaintenanceStateFormat`, `CasServerRootFormats`,
`CasRecordStreamFormat` — parses attacker-or-corruption-reachable bytes pulled from a bucket that is
shared across servers and, in the shared-pool deployment, across trust boundaries.

The nearest thing to fuzzing is `runFormatBattery`, and it is a *structured negative-example* suite,
not a fuzzer: it cuts the encoded text at every `\n` and at every third byte of line 1, bumps the
version, swaps the type string, and prepends garbage. It never flips bits inside a body, never
generates oversized or adversarially nested payloads, and never explores the compressed (`zstd`) arm
beyond re-sealing the golden text.

## Property/invariant testing

No property-based framework is vendored or used: `rapidcheck` and `RC_GTEST` appear nowhere in `src`.
Every CAS assertion is an example, hand-constructed and hand-checked.

The safety invariants the design documents name are asserted example-wise:

| Invariant | Asserted as | Where |
| --- | --- | --- |
| In-degree correctness | examples | `gtest_cas_blob_indegree.cpp`, `gtest_cas_gc_undercount_repro.cpp`, `gtest_cas_gc_arithmetic_intake.cpp` |
| No delete while referenced | examples | `gtest_cas_sweep_deletion_premise.cpp`, `gtest_cas_gc_leak.cpp`, `gtest_cas_ref_gc.cpp`, `gtest_cas_gc_rebuild.cpp::BatchedRebuildProtectsAllRefs`, `LandedEdgeBehindClampNeverDeleted` |
| Encode/decode round-trip | one example per format | `runFormatBattery` line `c.decode(stored)` — a single round-trip on a single hand-built value |
| Golden-text stability | pinned strings | `runFormatBattery` golden comparison |

Only 20 of 128 CAS gtest files spawn a `std::thread`, so even the concurrency-sensitive invariants are
predominantly checked on a single interleaving.

## Findings

### test-coverage-fuzzing-1 -- No CAS decoder is fuzzed despite bucket-sourced input (High)

- **Anchor**: absence of `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/fuzzers/`;
  `ci/workflows/nightly_fuzzers.py` and `tests/fuzz/` contain no CAS target.
- **Gap**: 13 decoders under `.../ContentAddressed/Formats/` parse bytes read from the object store.
  The repo already has the full libFuzzer scaffold (20 targets, `.options` files, nightly job), so the
  gap is not tooling cost — it is that CAS was never added.
- **Consequence**: a corrupted, truncated, or hostile object in a shared bucket reaches
  hand-written parsers (varint/offset arithmetic in `CasCodecUtil.h`, `CasRecordStreamFormat`,
  `CasRefWireVocab`) whose only negative testing is truncation at line boundaries. Under ASan/MSan
  this is exactly the class of defect the existing fuzzers were built to catch elsewhere in the tree.
- **Evidence**: `git ls-tree -r --name-only 842f2b37b8f | rg '^src/Disks/.*fuzz'` → empty;
  `rg 'cas' tests/fuzz/` → empty; `cas_format_test_battery.h` mutation set as quoted above.

### test-coverage-fuzzing-2 -- Backend contract suite never runs against a native conditional-write dialect (High)

- **Anchor**: `src/Disks/tests/gtest_cas_backend_contract.cpp:250-258`.
- **Gap**: the 19 `CASBackendContract` cases — the *definition* of the Backend seam, covering
  `putIfAbsent`, token-exact overwrite, `casPut` create/swap, `deleteExact` exactness, range get,
  head, list pagination, read-after-write, and the whole `StreamPut` lifecycle — are instantiated
  over `InMemoryBackend` and `ObjectStorageBackend{Mode::EmulatedSingleProcess}` only. There is no
  `INSTANTIATE_TEST_SUITE_P` against a real S3 endpoint, nor a recorded/replayed S3 transcript.
- **Consequence**: the contract that all of CAS safety rests on is validated only against two
  implementations that CAS itself wrote, one of which is explicitly documented as unsafe for
  production. Any divergence between the emulation and a real store's `If-Match` / `If-None-Match` /
  `x-amz-meta-*` / multipart-ETag behavior is invisible until a functional lane fails end-to-end,
  where the failure surfaces as a corrupted pool rather than a contract violation.
- **Evidence**: `ContentAddressedMetadataStorage.cpp:690` auto-selects `EmulatedSingleProcess` for
  `ObjectStorageType::Local`, so every gtest-constructed disk is emulated by construction;
  `cas_test_helpers.h:123` documents the same.

### test-coverage-fuzzing-3 -- The GCS generation-token dialect has no lane anywhere (High)

- **Anchor**: `src/Disks/tests/gtest_cas_backend_generation.cpp:12-120`; `ci/defs/altinity_jobs.py`
  (no GCS parameter set).
- **Gap**: every generation-token behavior — `TokenType::Generation` stamping, `listTokensDisabled`,
  `checkPoolPreconditions` versioning probe, the forced-single-PUT cap
  (`gcs_max_conditional_put_bytes`), and the `resurrect` exemption from that cap — is tested by
  constructing `Mode::Native` over a `LocalObjectStorage` and then calling
  `setNativeTokenTypeForTest(TokenType::Generation)`. That exercises CAS's own branching on a flag it
  set itself; it never touches a store that mints generations.
- **Consequence**: GCS is a documented target (`CasObjectStorageBackend.h:79` describes the XML LIST
  omission of generations), yet no test — unit, functional, or integration — runs against it or any
  emulator of it. The `x-goog-if-generation-match` path could be wrong in a way no lane can observe.
- **Evidence**: `rg -il gcs src/Disks/tests` matches only files that *mention* the dialect in
  comments or use the test setter; the functional matrix has `cas s3 storage` (RustFS) and
  `cas storage` (local) and nothing else.

### test-coverage-fuzzing-4 -- Three live format classes skip the shared failure-mode battery (Medium)

- **Anchor**: `src/Disks/tests/cas_format_test_battery.h` registrations; `FormatId::RunFile` (13),
  `FormatId::RefCkpt` (23), `FormatId::GcMaintenanceState` (25).
- **Gap**: 14 of 18 live `FormatId`s call `runFormatBattery`. `RunFile` (the GC source-edge NDJSON
  stream), `RefCkpt` (the per-namespace checkpoint, INV-4), and `GcMaintenanceState` (the janitor
  cursor) get only trait/cap/change-point assertions — `gtest_cas_ref_ckpt.cpp:407`,
  `gtest_cas_ref_ckpt_join.cpp:547`, `gtest_cas_gc_maintenance_state_format.cpp:29-84`. None of the
  three is checked for truncation-at-line-boundary, truncation-inside-header, the `v+1` gate, or
  leading garbage.
- **Consequence**: `RefCkpt` is the object fsck treats as the authority root
  (`gtest_cas_fsck.cpp::MissingCheckpointBaseSnapshotIsChainBroken`), and `RunFile` is what a GC round
  replays. A partially-written or version-skewed instance of either is precisely the input the battery
  exists to fail closed on, and precisely the input these two never see.
- **Evidence**: `git grep -c 'runFormatBattery(' 842f2b37b8f -- src/Disks/tests` across 13 files;
  `FormatId::` extraction per file as tabulated in the coverage map.

### test-coverage-fuzzing-5 -- No property-based testing of the safety invariants (Medium)

- **Anchor**: absence of `rapidcheck`/`RC_GTEST` anywhere under `src`.
- **Gap**: in-degree correctness, no-delete-while-referenced, and encode/decode round-trip are the
  three invariants the design calls load-bearing, and all three are asserted only on hand-built
  examples. Round-trip in particular gets exactly one value per format (`c.decode(c.encode())`), so
  fields that are empty, maximal, duplicated, or unicode-hostile in the golden fixture are never
  round-tripped at all.
- **Consequence**: the accounting bugs this subsystem has historically produced —
  `gtest_cas_gc_undercount_repro.cpp` and `gtest_cas_b140_dangle.cpp` are named after specific past
  escapes — are exactly the shape that randomized generation over ref/blob graphs finds cheaply and
  that example tests find only after a customer does.
- **Evidence**: the invariant table above; `gtest_cas_sweep_deletion_premise.cpp` and
  `gtest_cas_gc_leak.cpp` are scenario tests, not generators.

### test-coverage-fuzzing-6 -- No deterministic crash-at-step-N harness (Medium)

- **Anchor**: `tests/integration/test_cas_shared_pool/test.py:265`,
  `test_cas_drop_pool_member/test.py:146`, `test_cas_gc_sharded/test.py:255`.
- **Gap**: durability is tested by SIGKILL at three hand-chosen moments plus a handful of graceful
  `restart_clickhouse()` calls. The codebase already carries in-process test seams
  (`gc_verb_admit_window_hook_for_test`, `setNativeTokenTypeForTest`, the fence-trip hooks driving
  `gtest_cas_fence_generation.cpp`), so the machinery for "abort before the Nth durable call" is
  half-built — it is used to simulate windows, never to cut power.
- **Consequence**: multi-object commit sequences (part-write txn → manifest publish → ref intake →
  catalog update) have no test that stops after each individual object lands. A torn commit at an
  untested boundary is discovered by fsck in production rather than by CI.
- **Evidence**: `git grep 'SIGKILL\|stop_clickhouse\|restart_clickhouse' -- 'tests/integration/test_cas_*'`
  returns 15 lines total across 10 suites.

### test-coverage-fuzzing-7 -- Settings validation has one fail-closed test for the whole surface (Low)

- **Anchor**: `src/Disks/tests/gtest_cas_settings.cpp` (6 tests).
- **Gap**: `ValidateFailsClosed` is a single case; there is no per-setting boundary matrix (zero,
  negative, overflow, mutually-inconsistent pairs). The one cross-setting consistency check that
  exists lives elsewhere, in `gtest_cas_mount.cpp:896`.
- **Consequence**: a misconfigured CAS disk is the operator's most likely first encounter with the
  feature, and the failure mode is a server that either refuses to start or starts unsafe. The gap is
  Low because `openPoolView` and `CasProbe` are themselves fail-closed, which bounds the blast radius.
- **Evidence**: test list quoted in the coverage map.

### test-coverage-fuzzing-8 -- CAS-over-local functional coverage is one unsanitized lane (Low)

- **Anchor**: `ci/defs/altinity_jobs.py:116-120`.
- **Gap**: the `cas storage` (local object storage, `EmulatedSingleProcess`) variant runs only under
  `amd_binary`. The S3 variant gets ASan/UBSan, TSan, and MSan; the local variant gets none.
- **Consequence**: the emulated backend — the one every gtest depends on and therefore the one whose
  correctness props up finding 2 — is the code path with the *least* sanitizer coverage in the
  functional matrix. A data race in `emuMintToken`'s per-key token map would be invisible to CI.
- **Evidence**: the `cas_functional_tests_jobs` parameter sets, quoted in the inventory table.

## Coverage

Reviewed statically at `842f2b37b8f`: the full CAS test name inventory (128 gtest files / 1941 test
macros, 44 stateless scripts, 10 integration suites); read in full
`gtest_cas_backend_contract.cpp`, `cas_format_test_battery.h`, `cas_sweep_test_support.h`,
`gtest_cas_backend_generation.cpp`, `ci/defs/altinity_jobs.py`, `ci/jobs/unit_tests_job.py`, and three
integration `storage_conf.xml` files; read the test-name listings and selected bodies of
`gtest_cas_fsck.cpp`, `gtest_cas_gc_rebuild.cpp`, `gtest_cas_mount.cpp`, `gtest_cas_fence_generation.cpp`,
`gtest_cas_settings.cpp`, `gtest_cas_ref_decode_bounds.cpp`; read the CAS-relevant regions of
`ci/jobs/functional_tests.py`, `ContentAddressedMetadataStorage.cpp` (`openPoolView`), and
`CasFormat.h` (`FormatId`).

Not covered by this audit: whether the tests that exist actually *pass*, their runtime/flakiness,
assertion strength inside bodies I only listed by name, coverage of non-CAS code touched by the PR,
and anything requiring execution. Findings 2, 3, and 6 are gaps in *what the harness can reach*;
findings 1, 4, 5, 7, and 8 are gaps in *what was written* and are each closable with existing
in-tree scaffolding.
