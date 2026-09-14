# codeonly-line -- fresh audit 2026-08-31

## Scope
- Files/dirs examined:
  - `/Volumes/workspace/altinity-clickhouse/cas-pr-2159-ceee42c` @ `ceee42c51a06cb05e2c9a2d811ef7e1726825552`
  - All 133 `.cpp`/`.h` under `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/` (55,180 lines), plus `README.md` and `Formats/README.md`
  - Shipped docs under `docs/en/antalya/cas/**` (22 files) and `docs/en/operations/system-tables/cas_{log,gc_log,mounts}.md`
  - Targeted greps for retired write-protocol symbols (`putIfAbsentStream`, `promoteStaged`, `conditionalCreateControlled`, `copyObjectConditional`, `non_cas_keys`), `allow_stale`, `changePoints`, `G_BUILD`, `ShardReducer`, `tryFromDisk`, `parseStagingBackend`, and `TODO|FIXME|obsolete|legacy|no longer`
  - Protocol-change commits treated as current: `940b168` (unconditional blob publish), `917600b` (`cas_` settings), `7f932d3` (bounded lease / GC meta-job ownership)
- Explicitly out of scope:
  - Deep correctness of write/read/GC protocols (sibling audits)
  - Whether a comment that accurately describes current code is "too long"
  - Build/runtime

Baseline (HEAD, comments and tests restored; this is not the 2026-08-12 strip tree):

| area | files | lines |
|---|---|---|
| top level | 8 | 6,385 |
| `Backend/` | 13 | 4,756 |
| `Formats/` | 39 | 7,383 |
| `Gc/` | 19 | 9,461 |
| `Parts/` | 4 | 1,719 |
| `Pool/` | 33 | 20,782 |
| `Primitives/` | 10 | 1,476 |
| `Tools/` | 6 | 2,665 |
| `benchmarks/` | 1 | 553 |
| **total** | **133** | **55,180** |

Comment density: ~16,451 `//` / `///` lines (~30% of the tree). 134 `gtest_cas_*` / `gtest_ca_*` files are present. No `.tla` models. `docs/superpowers/` is absent from this worktree. Residual `TODO|FIXME|XXX|HACK` hits are ordinary prose ("no longer", "legacy", "temporarily"), not open defect markers.

Retired-symbol scan: `putIfAbsentStream`, `promoteStaged`, `conditionalCreateControlled`, `copyObjectConditional`, and `non_cas_keys` have **zero** hits in `src/` or `docs/`. The 940b168/917600b write-protocol names were deleted, not left as dangling comments.

## Findings

### codeonly-line-1 -- `Freshness::CachedForLoad` still advertises a stale-tolerant resolve that `resolveRef` discards (Medium)
- Anchor: `Parts/PartFolderAccess.h:62` (`Freshness::CachedForLoad`); `Parts/PartFolderAccess.cpp:318` and `:607`; `Pool/CasRefLedger.cpp:283-290` (`CasRefLedger::resolveRef`); `Pool/CasRefLedger.h:133`; `Pool/CasPool.h:549` / `Pool/CasPool.cpp:1851-1853` at ceee42c
- Trigger: any reader that takes `Freshness::CachedForLoad` (the default load-window policy) believing `allow_stale=true` will skip recovery/sweep, or any later edit that "honours" the flag because the enum comment says it is live
- Evidence: `PartFolderAccess.h:62` documents `CachedForLoad` as "stale-tolerant resolve (`allow_stale=true`)". The only two call sites pass that polarity (`PartFolderAccess.cpp:318` for `CachedForLoad`, `:607` unconditionally `true`). `CasPool::resolveRef` forwards `allow_stale` unchanged. The definition names the parameter `bool /*allow_stale*/` and the body never reads it; the adjacent comment states the knob "no longer selects anything" and is kept "so existing callers compile unchanged". The facade comment and the ledger comment contradict each other. The observable behaviour is always-fresh (fail-closed); the advertised API is not.
- Notes: Same root cause as 2026-08-12 codeonly-line-4, now with an explicit "intentional vestige" comment on the ledger side and a stale contract comment on the Parts side. Read-protocol / jepsen-anomaly must not treat `CachedForLoad` as a stale-read mode.

### codeonly-line-2 -- `moveFile` comments claim the unstaged-source throw has no live caller; UniqueKey still does that rename (Medium)
- Anchor: `ContentAddressedTransaction.cpp:1552-1557` (comment + `LOGICAL_ERROR`); production callers `src/Storages/MergeTree/UniqueKey/DeleteBitmapFileOps.cpp:58-71` (`writeBitmapToStorage` → `replaceFile`) and `UniqueKey/SSTIndexWriter.cpp:283` at ceee42c
- Trigger: a UniqueKey / SST-index write on a CAS part: write `<name>.tmp` through `IDataPartStorage::writeFile` (auto-commit when no part-storage transaction is open), then `replaceFile(tmp, final)`
- Evidence: The comment at `:1552-1556` says the unstaged branch "would cover a standalone one-shot rename of a committed `txn_version.txt`" and that "this branch therefore has no live caller and is retained only as a fail-loud guard". That is true for `txn_version.txt` (`supportsAtomicFileWrites` writes it directly). It is false for UniqueKey: `DeleteBitmapFileOps.cpp:62-71` writes `.tmp` then `storage.replaceFile`. `DataPartStorageOnDiskFull::replaceFile` (`DataPartStorageOnDiskFull.cpp:339-345`) falls through to `DiskObjectStorage::replaceFile`, which opens a **fresh** disk transaction, so `parts` is empty and `moveFile` throws `LOGICAL_ERROR` at `:1557`. `tryCreateWriteBuffer` (`:784-796`) *does* allow autocommit of inline-eligible part files (delete-bitmap / SST names are not in `partFileMustStayBlob`), so the `.tmp` can publish before `replaceFile` runs. The comment is a post-rewrite leftover that hides a live MergeTree caller.
- Notes: The behavioural defect is idisk-contract-2. This finding is the comment/code lie.

### codeonly-line-3 -- config-taking `parseStagingBackend` / `parsePartFolderValidate` still read unprefixed keys after `917600b` (Low)
- Anchor: `ContentAddressedMetadataStorage.cpp:325-328` (`parseStagingBackend(config, prefix)` reads `config_prefix + ".staging_backend"`); `:354-357` (`parsePartFolderValidate` reads `".part_folder_validate"`); contrast `ContentAddressedSettings.cpp:49,128-163` (`cas_` prefix) and the error strings at `:322` / `:351` (`cas_staging_backend`, `cas_part_folder_validate`) at ceee42c
- Trigger: any caller of the config overloads (today: `src/Disks/tests/gtest_cas_s3_staging.cpp:439-453`) against a disk block that only has `<cas_staging_backend>` / `<cas_part_folder_validate>`
- Evidence: Production load goes through `ContentAddressedSettings::loadFromConfig`, which only consumes `cas_*` (and temporarily the unprefixed spelling, with a warning). The two config overloads never look at `cas_staging_backend` / `cas_part_folder_validate`. A config that uses only the documented prefixed keys therefore parses as the **defaults** (`local`, `always`) through these helpers. Header comments at `ContentAddressedMetadataStorage.h:166-177` still describe "Reads `staging_backend` from `config`" / "Reads `part_folder_validate` from `config`" — accurate for the leftover helpers, stale relative to the 917600b public contract. The string overloads themselves are current (they mention `cas_*` in the exception text).
- Notes: Not a production mount bug while factory load uses `ContentAddressedSettings`. It is a 917600b leftover: a helper and its comment were not retargeted.

### codeonly-line-4 -- `tryFromDisk` comment still says InterpreterSystemQuery / system.cas_mounts were not migrated (Low)
- Anchor: `ContentAddressedMetadataStorage.h:179-185`; actual callers `src/Interpreters/InterpreterSystemQuery.cpp:1092,2544,2554,2581,2619,2652,2676,2699`, `src/Storages/System/StorageSystemContentAddressedMounts.cpp:124`, `src/Interpreters/ServerAsynchronousMetrics.cpp:372-381` at ceee42c
- Trigger: an auditor or a later cleanup that "migrates" those call sites again, or that treats the exception-probe behaviour described in the comment as current
- Evidence: The header says the helper "Centralizes the detection lambda duplicated across `InterpreterSystemQuery` and `StorageSystemContentAddressedMounts`; callers there have not yet been migrated to it." Every `SYSTEM CAS *` verb and `system.cas_mounts` already call `tryFromDisk`. The implementation (`ContentAddressedMetadataStorage.cpp:360-369`) was also rewritten to predicate on `disk->isContentAddressed()` first so it no longer constructs `NOT_IMPLEMENTED` on local disks — the comment still describes the old exception-as-control-flow design.
- Notes: Dead comment after the tryFromDisk / metrics rewrite. The code is the better of the two.

### codeonly-line-5 -- `Gc::fold` comments name `ShardReducer`; the fold calls `foldDeltasIntoGeneration` (Low)
- Anchor: `Gc/CasGc.cpp:3035-3043` (sharded-path comment: "Each bucket folds via its own `ShardReducer`"); `Gc/CasGc.cpp:3064-3071` (actual call); `Gc/CasGcShardPlan.h:58-86` (`ShardReducer`, `manifestCleanupShard`) at ceee42c
- Trigger: mapping the GC fold, or deleting `ShardReducer` as "unused" while trusting the fold comment that it is the production reducer
- Evidence: The sharded arm buckets deltas with `blobShard` and then calls `foldDeltasIntoGeneration(...)` per shard. A repo-wide search of `src/` + `programs/` for `ShardReducer::` / `manifestCleanupShard(` finds only `Gc/CasGcShardPlan.{h,cpp}` and `src/Disks/tests/gtest_cas_gc_shard_plan.cpp`. The class is real, tested, and not on the round path. The fold comment is a leftover of an earlier reducer shape.
- Notes: Coverage-map owns the dead-symbol inventory. This item is the comment/code drift.

### codeonly-line-6 -- shipped blob-protocol doc contradicts itself on token adoption (Low)
- Anchor: `docs/en/antalya/cas/architecture/blob-protocol.md:40` ("never adopt t1") and `:50` ("never retain a body token") versus `:137-138` (writer-vs-GC mermaid: "adopt t1 as dependency"); numbered steps at `:57-70` (HEAD, adopt present non-condemned body without retaining the observed token, else unconditional publish) at ceee42c
- Trigger: an operator or implementer using the second mermaid as the protocol
- Evidence: After 940b168 the code records a token-free `BlobDependencyProof::Materialized` and never keeps the HEAD token (`PartWriteTxn` / blob-protocol steps 3–4). The first mermaid and the numbered list match HEAD. The writer-vs-GC mermaid still draws the pre-rewrite "adopt t1" arrow on the Clean branch. Same file also links `/superpowers/cas/unconditional-blob-publication-performance` and `/superpowers/cas/unconditional-blob-publication-live-results` (`:85-92`); `docs/superpowers/` is not in this worktree, and those slugs are not under `docs/en/antalya/cas/`. `docs/en/antalya/cas/roadmap.md:46`, `bucket-requirements.md:60`, and `architecture/correctness.md:21-25` repeat the same broken `/superpowers/` links.
- Notes: Docs are claims, not evidence of behaviour. The code and the first half of the page agree; the second mermaid is a 940b168 leftover.

## By-design / info / non-actionable
- The 2026-08-12 strip baseline does not apply here. Comments, READMEs, shipped docs, and 134 gtests are present. Residual comment density is high (~30%) and is usable as a claim-to-verify surface, not as proof.
- `allow_stale` being ignored is **documented on the ledger** (`CasRefLedger.cpp:287-290`) as a vestigial parameter. The defect is the Parts-layer comment that still advertises the old knob (codeonly-line-1), not the discard itself.
- `changePoints()` is still unused by writers (`Formats/CasFormat.cpp:72`; callers only in `gtest_cas_format.cpp` / `gtest_cas_text_format.cpp` / `gtest_cas_gc_maintenance_state_format.cpp`). `CasFormat.h:138-144` now states that writers always stamp `G_BUILD` (currently 10) until a roster / write-down-to-floor policy exists. That is an upgrade-compat fact, not a silent comment/code lie.
- `putIfAbsent` remains a live Backend verb for metadata/control objects. Its survival is not a 940b168 leftover; blob bodies use `publishBlob`.
- Unprefixed disk keys are still accepted with a startup warning (`ContentAddressedSettings.cpp:210-217`; `docs/en/antalya/cas/configuration.md:124-127`). That matches 917600b's migration window. `non_cas_keys` is gone.
- `ContentAddressed/README.md:68-71` says a GC round "seal[s] the round with one CAS on `gc/state`". `Gc/CasGc.h:689-690` says the fold no longer CASes `gc/state` and "the SINGLE round CAS commits them". Those two sentences describe the same current protocol (fold in-memory, one round CAS). Not drift.
- Empty `catch (...)` sites that remain are generally accompanied by rationale comments; they are not the 2026-08-12 NOLINT-only empties.

## Closed-since-2026-08-12
- codeonly-line-1 (deleted test corpus) — 134 `gtest_cas_*` / `gtest_ca_*` files are in the tree; functional tests and `docs/en/antalya/cas/**` are present.
- codeonly-line-2 (stripped `/*param=*/` labels) — comments restored; no residual double-space label damage is the baseline.
- codeonly-line-3 (unnamed parameters as strip damage) — signatures and comments restored; remaining unnamed params (`allow_stale`) are explicit vestiges, not strip artifacts.
- codeonly-line-6 / -7 / -8 / -9 (empty-if / empty-catch / magic constants / `mount_renew_period_ms` as unrecoverable) — comments and setting `DECLARE` strings are back; those are no longer a code-only-line problem.
- codeonly-line-10 (untracked `docs/superpowers/CAS.md` + `tmp/` as the only narrative) — this worktree has no `docs/superpowers/`; shipped narrative is `docs/en/antalya/cas/**`. Broken `/superpowers/` *links* remain (codeonly-line-6).
- Retired write-protocol names (`putIfAbsentStream`, `promoteStaged`, `conditionalCreateControlled`, `copyObjectConditional`, `non_cas_keys`) — deleted from code and comments (`940b168` / `917600b`).

## Coverage
- Reviewed: tree inventory (133 files, 55,180 lines); comment density; presence of tests/docs/READMEs/TLA; retired-symbol grep; `allow_stale` end-to-end; settings prefix vs leftover config parsers; `tryFromDisk` comment vs callers; fold comment vs `ShardReducer`; blob-protocol.md vs `publishBlob` / HEAD-then-publish; UniqueKey vs `moveFile` comment; `changePoints` / `G_BUILD` comments vs writers.
- N/A: license-header / doxygen remnant analysis (ClickHouse style).
- Deferred: whitespace-level comment quality; whether every `DECLARE` setting description still matches the validator (settings/docs audit); full docs/en page-by-page vs every protocol (write-protocol / gc-protocol).
