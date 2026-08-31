# test-coverage-fuzzing -- fresh audit 2026-08-31

## Scope
- Files/dirs examined at `ceee42c`: `src/Disks/tests/cas_format_test_battery.h`, every `runFormatBattery(` site, `gtest_cas_backend_contract.cpp`, `gtest_cas_settings.cpp`, `gtest_cas_backend_generation.cpp`, `tests/integration/test_cas_gcs/`, `tests/integration/test_gcs_live/`, `ci/` for those suite names, `Formats/CasFormat.h` `FormatId`, search for crash-at-step-N / `FaultAt` harnesses, search for CAS fuzz targets.
- Explicitly out of scope: treating fuzzer absence as a defect (by-design, CAS-064).

Tests exist in this worktree (unlike the 08-12 code-only strip). Inventory is from HEAD, not `842f2b37b8f`.

## Findings
### test-coverage-fuzzing-1 -- live formats `RunFile` and `GcMaintenanceState` are not registered in the shared decoder battery (Low)
- Anchor: `cas_format_test_battery.h:56-111` (`runFormatBattery`); call sites in `gtest_cas_{format_battery,pool_meta via format_battery,server_root_format,ref_snapshot_format,ref_log_format,ref_catalog,part_manifest_format,gc_state_format,gc_outcomes_format,fold_seal_format,blob_meta_format,blob_envelope_format}.cpp`. `FormatId` live values in `CasFormat.h:103-136` include `RunFile=13` and `GcMaintenanceState=25`. `gtest_cas_gc_maintenance_state_format.cpp` and `gtest_cas_text_format.cpp` mention those ids but do not call `runFormatBattery`. `FormatId::Roster` has no traits (`gtest_cas_text_format.cpp:74`).
- Trigger: a decode-of-encode / v+1 / truncation regression in `cas_run` or `cas_gc_maintenance_state` that the battery would have caught for the registered classes.
- Evidence: the battery is the shared contract for those failure modes. Two live classes rely on ad-hoc unit tests only. Drift risk, not a production hole. Same residual as CAS-064.
- Notes: CAS-064.

### test-coverage-fuzzing-2 -- no crash-at-step-N publish/commit harness (Low)
- Anchor: repo search under `src/Disks/tests` for `crash.?at.?step`, `crashAtStep`, `inject.?step`, `FaultAt` — no matches. Existing seams are named hooks (`shouldFailPromoteForTest`, `runAfterPromoteHookForTest`) not an ordered N-step schedule.
- Trigger: a reviewer asking "what if we die after precommit and before HEAD" as a single parameterized test.
- Evidence: recovery and abort paths are covered piecewise by dedicated gtests; there is still no one harness that walks the write protocol by step index. Already tracked. Not a missing production backstop.
- Notes: CAS-109 residual (the settings-uncovered half of CAS-109 is false on HEAD — `gtest_cas_settings.cpp` covers `cas_` prefix, unknown keys, ranges, scratch).

### test-coverage-fuzzing-3 -- backend contract suite still has no Native row (Low)
- Anchor: `gtest_cas_backend_contract.cpp:152-160` instantiates `CASInMemory` and `CASLocal` (`Mode::EmulatedSingleProcess`) only.
- Trigger: a Native/S3 conditional-write regression that emulated-mode tokens do not exercise.
- Evidence: Native behavior is covered elsewhere (`gtest_cas_backend_generation.cpp`, `gtest_cas_probe.cpp`, RustFS functional lanes). The *shared* contract table still does not pin Native. Same residual as CAS-065.
- Notes: CAS-065.

### test-coverage-fuzzing-4 -- live GCS is an opt-in integration suite, not a required CI lane (Low)
- Anchor: `tests/integration/test_gcs_live/test.py` (env-gated `GCS_LIVE_*`); `tests/integration/test_cas_gcs/test.py` (fake GCS XML). `ci/` has no `test_gcs_live` / `test_cas_gcs` job name.
- Trigger: a GCS generation-dialect change that the fake service does not model.
- Evidence: `test_cas_gcs` documents that a green fake run is not evidence for `ApiMode::GCS` against `storage.googleapis.com`. `test_gcs_live` is the real gate and requires operator credentials. Absence from default CI is a process gap, not a missing test file.
- Notes: CAS-065 residual.

## By-design / info / non-actionable
- **No CAS fuzzer.** Zero `*_cas*_fuzzer.cpp` / `src/Disks/**/fuzzers/`. Settled position (S3 trusted, decoders fail closed). Do not re-raise as a defect.
- Settings validation is covered in `gtest_cas_settings.cpp` (prefix required, unknown `cas_*` rejected, `server_root_id` / `gc_shards` / `blob_hash` / `staging_backend` / `part_folder_validate` / relative scratch).
- Functional CAS-over-S3 lanes (RustFS) and the unit estate remain the primary CI surface.

## Closed-since-2026-08-12
- `cas_` prefix / `non_cas_keys` (`917600b122b`, CAS-106): `gtest_cas_settings.cpp` pins the new prefix and rejects unprefixed keys.
- Settings "practically uncovered" half of CAS-109: contradicted by the settings gtest file on HEAD.

## Coverage
- Reviewed: battery registration vs `FormatId`; contract instantiations; settings tests; GCS fake vs live; crash-step search; fuzzer search; CI name search.
- N-A: fuzzer absence (by-design).
- Deferred: counting every gtest macro (not required to decide the residuals above).
