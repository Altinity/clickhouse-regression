# backfill-not-reviewed -- fresh audit 2026-08-12

## Scope and purpose

This is the closing accountability audit of the fresh re-run at
`/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base commit
`842f2b37b8f`, working tree as-is. Its subject is not the CAS code but **the audit round itself**:
what was walked, what was named but not walked, what each report explicitly deferred, and what
residual risk that leaves. It re-audits nothing.

Code surface under accountability: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`
— 130 files (129 `.cpp`/`.h` totalling 36,603 lines, plus `benchmarks/CMakeLists.txt`).

**Method.** For every file in the tree I searched all peer reports for the file's basename, then
read the `Scope` / `Region walked` / `Coverage` sections of each report to separate three states:
(a) walked line-by-line, (b) read in the region relevant to that audit's question, (c) named in an
inventory only. Peer reports were read, not re-derived.

**Method limits, stated up front.** Basename search is a proxy for review, and it is imperfect in
both directions. It *undercounts*, because the tier reports and several thematic reports use
`{h,cpp}` shorthand in their region tables — `Pool/CasRefCatalog.h` is never spelled out in prose
but tier1's line arithmetic (`552 + 139`) proves it was read. It *overcounts*, because a file can be
cited once as evidence for someone else's finding without anyone having read it. Where the two
disagree I resolved it by reading the owning report's Coverage section, and I flag the residual
uncertainty inline. Nothing in this report was verified by execution.

**First and largest accountability fact: this was a 37-audit round, not a 39-audit round.**
The reports directory contains 36 files. Two of the 38 named peers, **`tier3` (GC internals +
tools)** and **`tier4` (residual surfaces / blind spots)**, were never produced — they exist only in
the earlier `cas-audit-rerun-20260730/reports/` round. Those two were precisely the audits whose job
was exhaustive coverage of `Gc/` and `Tools/` and closure of the blind-spot list. Their absence is
the root cause of most of the findings below, because other reports deferred work *to* them.

## Per-file accountability

Three-state classification. "Deep sweep" means a report claims a complete, ordered, line-by-line
read of the file. "Region-read" means one or more reports read the parts relevant to their own
question and anchored findings there. "Enumerated only" means the file appears in `coverage-map`'s
inventory (which classifies all 130 files by role) and/or `codeonly-line`'s strip scan, but no audit
walked it.

| Directory | Files | Lines | Deep sweep | Region-read only | Enumerated only |
|---|---|---|---|---|---|
| `(root)` | 8 | 4,010 | 2 (`ContentAddressedSettings.{h,cpp}`, tier2) | 6 | 0 |
| `Backend/` | 13 | 3,207 | **13 (100%, tier2)** | 0 | 0 |
| `Formats/` | 39 | 5,677 | 26 (bc1, bc4, security, upgrade-compat, tier1, bc5) | 7 | 6 |
| `Gc/` | 17 | 6,352 | 5 (`CasBlobInDegree.{h,cpp}`, `CasNamespaceJanitor.cpp`, `CasGcShardPlan.{h,cpp}`) | 8 | 4 |
| `Parts/` | 4 | 1,179 | **4 (100%, bc5 + bc6 + mergetree-part-support)** | 0 | 0 |
| `Pool/` | 31 | 12,604 | **29 (tier1 + tier2 + concurrency)** | 2 | 0 |
| `Primitives/` | 10 | 1,123 | 7 (bc1, security, performance, ad1) | 1 | 2 |
| `Tools/` | 6 | 2,082 | **0** | 4 | 2 |
| `benchmarks/` | 2 | 373 | 2 (performance) | 0 | 0 |
| **Total** | **130** | **36,607** | **88** | **28** | **14** |

**Walked by at least one audit: 116 of 130 files (~97% of lines).** Every file in the tree is named
by at least one report except one (below), so the round's *breadth* is genuine. The gaps are in
*depth*, and they concentrate in `Gc/` and `Tools/`.

### Files never named by any of the 36 reports

| File | Lines | Status |
|---|---|---|
| `Gc/CasGcMaintenanceState.cpp` | 40 | **Zero mentions.** Only its class name appears, in `coverage-map`'s role inventory. |

### Files named in an inventory only, never walked

Corrected for `{h,cpp}` shorthand, i.e. these survive the correction and are genuinely unwalked:

| File | Lines | Sole mention | Note |
|---|---|---|---|
| `Gc/CasOrphanManifestSweep.h` | 91 | `coverage-map` | The `.cpp` (731 lines) is region-read only; the pair has no owner |
| `Primitives/CasNamespaceLifeId.h` | 77 | `coverage-map` | Header-only implementation, no `.cpp` — so nothing else covers it |
| `Formats/CasRecordStreamFormat.h` | 80 | `coverage-map` | `.cpp` deep-swept by bc1 and bc4 |
| `Gc/CatalogLifecycleReconciler.h` | 58 | `coverage-map` | gc-protocol read `.cpp:32-118` |
| `Formats/CasRefWireVocab.cpp` | 47 | bc4 (passing) | See backfill-6 |
| `Formats/CasGcStateFormat.h` | 42 | `coverage-map` | `.cpp` deep-swept |
| `Gc/CasGcMaintenanceState.h` | 29 | `coverage-map` | See backfill-7 |
| `Formats/CasRefWireVocab.h` | 35 | `coverage-map` | See backfill-6 |
| `Gc/CasNamespaceJanitor.h` | 33 | `coverage-map` | `.cpp` deep-swept by tla-fidelity |
| `Tools/CasDecommission.h` | 33 | `coverage-map` | See backfill-3 |
| `Formats/CasWireVocab.h` | 32 | `codeonly-line` | `.cpp` deep-swept |
| `Formats/CasRefCkptFormat.h` | 28 | `coverage-map` | `.cpp` deep-swept by tier1 |
| `Primitives/CasBlobHashingWriteBuffer.h` | 25 | `coverage-map` | `.cpp` region-read by bc2, ad1, performance |
| `Tools/CasInspect.h` | 12 | `coverage-map` | See backfill-3 |

Ten of these fourteen are headers whose `.cpp` was deep-swept; treating the declaration as covered by
the definition's review is reasonable, and I do so. The four that matter are called out as findings.

### Large files with no exhaustive owner

These are heavily *cited* but never walked end to end. The mention count is high enough to look like
coverage and is not.

| File | Lines | Reports naming it | Who declined it, and why |
|---|---|---|---|
| `Gc/CasGc.cpp` | 3,236 | 24 | No full read anywhere. gc-protocol and gc-rebuild-feature read large ranges; bc7 states it "treats the round as one uninterruptible unit… not a per-phase attribution"; bc1 read 4 ranges; tier3 (owner) absent |
| `Tools/CasFsck.cpp` | 950 | 17 | Five explicit refusals (bc3, security, tla-fidelity, gc-protocol, performance); ad3 covers its *output surface*, not its internals |
| `Pool/CasPartWriteTxn.cpp` | 902 | 27 | tier2 excludes it "except the epoch check at line 125"; tier1 excludes it; no tier owns it |
| `Gc/CasOrphanManifestSweep.cpp` | 731 | 11 | tla-fidelity defers "retention classification"; bc1 lists it as pattern-swept only |
| `Tools/CasInspect.cpp` | 579 | 13 | `coverage-map` blind spot #2 states no angle owns its decoder completeness; bc4 read it as the envelope decoder only |
| `Gc/CasGc.h` | 472 | 8 | Region-read; no full read |
| `Tools/CasDecommission.cpp` | 388 | 12 | `coverage-map` blind spot #3 states no listed angle owns it; ad3 covers the verb end to end, tla-fidelity the delete paths |

`ContentAddressedMetadataStorage.cpp` (1,638) and `ContentAddressedTransaction.cpp` (1,360) are also
without a single full read, but they are the two most-cited files in the round (29 and 27 reports),
and `idisk-contract` walked their entire override surface method by method against the base
declarations. I judge them adequately covered and do not raise them as findings.

## Deferred items collected from the 38 reports

Every item below is quoted or paraphrased from a peer report's own Coverage / Deferred / "Not
covered" section. Grouped by theme.

### A. Deferrals to audits that do not exist

| Item | Owning report | Risk |
|---|---|---|
| Exhaustive sweep of `Gc/` (17 files, 6,352 lines) | tier3 — **never written** | High |
| Exhaustive sweep of `Tools/` (6 files, 2,082 lines) | tier3 — **never written** | High |
| Closure of `coverage-map`'s 11 named blind spots | tier4 — **never written** | Medium |
| "mount-lease acquisition and fencing semantics in depth (`mounts-and-leases`)" | gc-rebuild-feature → nonexistent audit | Medium (largely absorbed by tier2's full read of `CasServerRoot.cpp`/`CasMountRuntime.cpp`) |
| "`checkOpAdmitted` / `TruthAbsent` correctness belongs to the mounts/leases audit" | idisk-contract → nonexistent audit | Medium |
| "`Tools/CasDecommission` end-to-end (decommission audit)" | gc-rebuild-feature → nonexistent audit | Medium |
| "Envelope header format and blob hashing (write-protocol / formats audits)" | idisk-contract → no "formats" audit; bc4 partially absorbs | Low |
| bc1's arithmetic residue left to "the 39-audit siblings that cover the read protocol, GC protocol and fsck paths in depth" | bc1-offset-overflow → the fsck depth audit is tier3 | Medium |

### B. Prerequisite checks that were deferred and never performed by anyone

| Item | Owning report | Risk |
|---|---|---|
| "Verifying that the 775 machine-added lines in the CAS tree are behaviour-preserving… should be done **before any audit in this re-run reports a behavioural conclusion** as attributable to the base commit" | codeonly-line (Deferred) | **High** — see backfill-2 |
| Whether the 119 deleted functional cases / 134 deleted gtests resolve code-only-line items 1, 3, 9; "left for the coverage-map audit to decide" | codeonly-line → coverage-map did not read tests; test-coverage-fuzzing read the test *inventory* at base but did not resolve those three items | Medium |
| Per-audit search scoping (`src/`, `programs/`, `ci/`) "not enforced by anything in this repo" | codeonly-line | Low |

### C. Tool and GC internals

| Item | Owning report | Risk |
|---|---|---|
| `Tools/CasFsck.cpp` beyond its `catch (...)` sites | bc3-exception-safety | Medium |
| `Tools/CasFsck.cpp` and `Tools/CasDecommission.cpp` internals | security | Medium |
| `Tools/CasFsck.cpp`, `Tools/CasInspect.cpp` | tla-fidelity | Medium |
| `CasFsck`/`CasInspect`; `rebuildBaseline` and its enumeration helpers; `previewDeletes` | gc-protocol ("Not examined (deliberately)") | Low (rebuild is gc-rebuild-feature's; the tools are not) |
| `Tools/CasFsck.cpp` — "offline tool, not a hot path" | performance | Low |
| `Tools/**` | tier1, tier2 (both explicitly exclude) | Medium |
| `Gc::runRegularRound` interior, phase by phase | bc7-blocking-io-locks | Medium |
| `Gc/CasOrphanManifestSweep.cpp` retention classification, `Gc/CatalogLifecycleReconciler.cpp`, `Gc/CasGcShardPlan.cpp` | tla-fidelity ("out of budget") | Medium |
| `CasOrphanManifestSweep`/`CasBlobInDegree` internals inside the `gc_round_mutex` region | bc7-blocking-io-locks | Low |
| `Gc/**` except two `computeHeartbeatFloor` call sites | tier2 | Medium |
| Fsck's full-listing path performance at scale | ad2-deletion-erasure | Low |

### D. Format encode halves, headers and vocabularies

| Item | Owning report | Risk |
|---|---|---|
| "Encode halves of the large ref/fold formats beyond what was needed for encode/decode asymmetry"; `CasLayout.h` key builders; `Tools/` renderers | bc4 | Low (security deep-swept `CasLayout.{h,cpp}`) |
| Ref-log / ref-snapshot **body grammars** beyond header handling — "outside a static skew analysis without fixtures" | upgrade-compat | Medium (tier1 read the codecs, but for ledger correctness, not skew) |
| `Formats/**`, `Primitives/**` | tier2 (explicit exclusion) | Low (bc1/bc4/security cover) |
| Three live `FormatId`s (`RunFile`, `RefCkpt`, `GcMaintenanceState`) skip the shared decode battery | test-coverage-fuzzing-4 (a finding, not just a deferral) | Medium |

### E. Runtime, backend and infrastructure boundaries

| Item | Owning report | Risk |
|---|---|---|
| S3/GCS server-side lifecycle, versioning, replication configuration | ad2, ad6, crash-consistency | High (ad6 raises 7 High findings *about* this and cannot verify any) |
| Object-storage client internals (S3 connection pool, keep-alive, multipart thresholds) | ad5 | Medium |
| `Mode::EmulatedSingleProcess` — "the single most consequential blind spot" | coverage-map blind spot #8; interleaving and gc-rebuild-feature both note multi-mount cases are not locally reproducible | High |
| Azure/GCS server-side encryption specifics; `CLICKHOUSE_CLOUD` KMS paths (compiled out) | encryption | Low |
| Keeper/ZooKeeper-side divergence; SQL-created (`custom`) CAS disks; proxy/endpoint dialect differences | ad7 | Medium |
| `Cache/` metadata storage semantics; `MetadataStorageFromCacheObjectStorage` | ad2, upgrade-compat, idisk-contract | Low |
| `benchmarks/` subtree | ad5, upgrade-compat, bc1, bc3, tier1 (performance does cover it) | Low |

### F. Cross-cutting ClickHouse-side surfaces

| Item | Owning report | Risk |
|---|---|---|
| Backup/`RESTORE` engine internals beyond the shadow-namespace boundary; backup/restore of an encrypted CAS disk end to end | ad2, encryption | Medium |
| Crash behaviour of the ClickHouse metadata/replication layers calling into CAS | crash-consistency | Medium |
| FETCH PARTITION and the interserver relink protocol; cross-pool / cross-disk ATTACH | alter-merge-mutation, mergetree-part-support, ad4 | Medium (ad4-1 and ad7-2 anchor the risk; no audit owns the full protocol) |
| Non-MergeTree writers on a CAS disk | datatype-agnosticism | Low |
| `system.cas_log` / `cas_gc_log` / `cas_mounts` column sets, not audited column by column | upgrade-compat | Low |
| Per-query memory-tracker attribution for CAS allocations | ad5 | Low |

### G. Named-unresolved questions (a report tried and could not settle it)

| Item | Owning report | Risk |
|---|---|---|
| Whether the abandon path can delete a manifest body whose precommit record is already durable — needed to make `interleaving-2` step 3 unconditional | interleaving | Medium |
| Whether a divergent two-epoch ref-log chain resolves to a hold or to silent last-writer-wins — "both branches are bad, but I could not pin which without executing the walk" | interleaving | **High** |
| Which of two readings of the dead `ShardReducer` is correct; gc-protocol accepted the dead-code reading "without re-derivation" rather than deriving how `CasGc.cpp` computes per-shard ownership | coverage-map-1 → gc-protocol | Medium |
| `getLastModifiedIfExists` non-atomicity — "no in-tree caller feeds it a CAS path today… it becomes a finding the moment a caller appears" | bc6 | Low |
| `ALTER TABLE FREEZE` re-freezing an existing backup name, and the resulting stamp — not traced end to end | bc6 | Low |
| Mtimes under `deduplication_logs/` — no reader of their mtime was found | bc6 | Low |
| The 12-item "code-only line": contracts unrecoverable from code and to be treated as **unknown** by all other audits | codeonly-line | High (a permanent property of the stripped tree, not a work gap) |

## Analysis categories not performed this round

Every one of the 36 reports states that it is static-only. Aggregated, the round performed **no
execution of any kind** — and, notably, **nothing was compiled**, so not even the compiler's opinion
of the tree was obtained. The following categories were not attempted and cannot be closed by more
static review.

1. **Runtime / dynamic testing.** No build, no test run; all CAS tests are deleted in the working
   tree. Would find: whether the reported triggers are actually reachable. A large fraction of this
   round's findings are stated as code paths with a named trigger, not as observed failures — for
   example `interleaving`'s two-epoch divergence question and `tla-fidelity`'s two-GC-actor
   reachability are explicitly unresolvable without running the walk.
2. **Real S3 / GCS behavioural verification.** Would find: whether the conditional-write contract
   CAS depends on actually holds on each vendor — `If-None-Match` / `If-Match` semantics, multipart
   ETag behaviour, generation tokens, `ListObjectVersions`, delete-marker reporting, throttling
   shape. `ad6` raises seven High findings entirely about this contract and can verify none of them;
   `test-coverage-fuzzing-2` and `-3` establish that the base commit's own tests never touch a real
   dialect either. This is the largest single evidence gap in the round.
3. **Sanitizer runs (ASan/TSan/MSan/UBSan).** Would find: the concurrency and lifetime defects that
   static reasoning can only nominate. `concurrency` names 14 findings and withdrew several
   candidates as "unconfirmed"; TSan would settle both lists. `bc1`'s eight overflow findings and
   `security-3`'s unbounded materialization are exactly UBSan/ASan territory.
   `test-coverage-fuzzing-8` notes the emulated backend — the one everything else rests on — is the
   least sanitized lane in CI.
4. **Fuzzing.** Would find: crashes and hangs in the 13 hand-written decoders that parse
   bucket-sourced bytes. `test-coverage-fuzzing-1` establishes the scaffold already exists in-repo
   and CAS was simply never added. `bc4`'s ten decode findings are the hypotheses a fuzzer would
   confirm or refute in hours.
5. **Formal model checking.** No `.tla` model exists on this tree (`tla-fidelity` recovered state
   machines from code instead). Would find: the interleavings a human matrix misses.
   `interleaving` walked 25 hand-chosen pairs; TLC would explore the product space and would settle
   the two-epoch divergence question directly.
6. **Performance measurement.** `performance` states its magnitudes are "arithmetic from shipped
   defaults", high confidence on complexity classes, medium on absolute numbers, and explicitly not
   assessed: real cache hit rates, actual GC round wall time, and whether any cost is visible above
   object-store latency. `ad5`'s resident-byte estimates assume a glibc-style allocator. Would find:
   which of the ~12 quantified hot paths matters in a real deployment.
7. **Multi-node chaos.** Would find: whether the split-brain, fencing and lease findings
   (`jepsen-anomaly-1`, `interleaving-1`, `gc-protocol-3`, `ad7-1`) manifest under real partitions
   and clock skew. Structurally impossible to approach locally: `Mode::EmulatedSingleProcess` is
   auto-selected for local object storage, so the multi-mount paths are out of contract by
   construction on any local setup.
8. **Diff review against the base commit.** Not performed by anyone — see backfill-2. This one is
   *not* a different method: it is a static task that was scheduled and dropped.

## Findings

### backfill-1 -- tier3 and tier4 were never produced, leaving `Gc/` and `Tools/` (8,434 lines, 23 files) with no exhaustive sweep and the blind-spot list unclosed (High)

- **Anchor / Gap**: `cas/docs/cas-audit-rerun-20260812/reports/` contains 36 `.md` files; `tier3.md`
  and `tier4.md` exist only under `cas-audit-rerun-20260730/reports/`. tier3's scope was "GC
  internals + tools" and tier4's was "residual surfaces / blind spots". `Gc/` has 0 of 6,352 lines
  under a deep sweep; `Tools/` has 0 of 2,082. By contrast tier1 delivered 8,095 lines at "100% of
  the named region" and tier2 delivered all of `Backend/` plus 90% of `Pool/` line-by-line — so the
  tier method demonstrably works and two of its four instances are simply missing.
- **Residual risk**: High, and compounding rather than isolated. Five reports (bc3, security,
  tla-fidelity, gc-protocol, performance) each explicitly declined the `Tools/` internals in the
  expectation that a sibling owned them; bc1 routed its arithmetic residue to "the siblings that
  cover the fsck paths in depth"; tier1 and tier2 both list `Tools/**` as out of tier. The
  deferrals form a cycle that terminates at two reports that do not exist, so the gap is invisible
  from inside any single report — which is precisely the failure mode this audit exists to catch.

### backfill-2 -- the strip-fidelity check that codeonly-line made a precondition for the whole round was deferred and never performed, so every behavioural conclusion rests on an unverified tree (High)

- **Anchor / Gap**: `codeonly-line.md`, Deferred: "Verifying that the 775 machine-added lines in the
  CAS tree are behaviour-preserving. codeonly-line-2 establishes that the stripper rewrote code
  lines, not only deleted comment lines. A whitespace-insensitive diff of the CAS tree against
  `842f2b37b8f` would settle it, but that is a diff-review task rather than a static read of the
  working tree, and **it should be done before any audit in this re-run reports a behavioural
  conclusion as attributable to the base commit**." No report performed it. Searching the 36 reports
  for a diff of the CAS tree against the base returns nothing; every report instead states its
  claims are anchored "at the cited lines in the working tree at `842f2b37b8f`".
- **Residual risk**: High. This does not mean the findings are wrong — `codeonly-line-2` describes
  the stripper as removing `/*param=*/` labels, which is behaviour-preserving at the language level.
  But the round produced roughly 200 findings attributed to a base commit whose equivalence to the
  audited tree was flagged as unestablished by the one audit whose job was to establish it, and the
  check is cheap: one whitespace-insensitive diff. Until it is run, any finding anchored on a line
  the stripper rewrote is attributed on trust.

### backfill-3 -- `Tools/` (2,082 lines) has no owner, and it is the instrument set that every disaster-recovery finding depends on (Medium)

- **Anchor / Gap**: `Tools/CasFsck.cpp` (950), `Tools/CasInspect.cpp` (579),
  `Tools/CasDecommission.cpp` (388), plus `CasFsck.h` (120), `CasDecommission.h` (33),
  `CasInspect.h` (12). Five reports refuse the internals by name; `coverage-map` blind spots #2 and
  #3 state outright that no listed angle owns `CasInspect.cpp`'s decoder completeness or
  `CasDecommission.cpp`'s blast radius. What *is* covered is the output surface: `ad3` walked
  `runFsck`'s byte accounting and namespace scoping, `caInspectToJson`'s key coverage, and
  `decommissionPoolMember` end to end; `gc-rebuild-feature` searched all three for write operations
  and refusals; `crash-consistency-4` anchors a decommission crash window.
- **Residual risk**: Medium. `fsck` and `inspect` are read-only, so a defect degrades diagnosis
  rather than corrupting data — but that is exactly the risk that matters here, because `ad3` raises
  four High findings (`ad3-1` through `ad3-4`) whose whole subject is that the DR surface cannot
  localize or attribute damage. A decoder gap in `CasInspect.cpp`, or a misclassification in
  `CasFsck.cpp`'s five leak classes, would make the operator's position worse than `ad3` already
  reports, and nothing in this round would have seen it. `CasDecommission.cpp` is the one
  genuinely destructive tool in the set, and `ad7-1` already reports that a nested `server_root_id`
  lets it destroy a live descendant member.

### backfill-4 -- `Gc/CasGc.cpp` (3,236 lines, the largest file in the tree) has no phase-by-phase owner (Medium)

- **Anchor / Gap**: named by 24 of 36 reports, walked in full by none. `gc-protocol` and
  `gc-rebuild-feature` read large ranges and between them cover the round structure, fold, lease and
  rebuild; `tla-fidelity` recovered the GC round state machine; `bc1` read four arithmetic ranges.
  But `bc7-blocking-io-locks` states plainly: "Not fully traced: the interior of
  `Gc::runRegularRound` phase by phase — the round is treated here as one uninterruptible unit under
  `gc_round_mutex`, which is sufficient for the stall bound but not a per-phase attribution."
  `tier2` excludes `Gc/**` apart from two call sites. `tla-fidelity` additionally defers the
  `CasOrphanManifestSweep` retention classification and `CatalogLifecycleReconciler` as "out of
  budget".
- **Residual risk**: Medium rather than High, because GC is the *most* audited subsystem in the round
  by finding count (gc-protocol, gc-rebuild-feature, ad2, tla-fidelity, crash-consistency and ad5 all
  produce anchored GC findings), and `gc-protocol`'s Coverage section contains a genuinely tight
  three-legged proof that the live-blob-deletion fence holds. The residual is the interior of the one
  destructive loop in CAS, reviewed by question rather than by line, in a file large enough that a
  defect between the reviewed ranges would be seen by nobody.

### backfill-5 -- `Pool/CasPartWriteTxn.cpp` (902 lines) is excluded by both tier sweeps by name, while hosting three of the round's protocol findings (Medium)

- **Anchor / Gap**: `tier2` Coverage: "Explicitly not covered by tier2: … `CasPartWriteTxn.*`
  (except the epoch check at line 125)". `tier1` Coverage: "Not covered by this tier … blob and
  manifest paths". It is named by 27 reports — the third-highest in the tree — but every one of them
  read a section: `write-protocol` the commit ordering, `gc-protocol` the adopt guards,
  `bc5` `stageManifest`/`promote`/`uploadFromSource`, `ad1` the hashing producers, `bc2` the staging
  path.
- **Residual risk**: Medium. This is the blob adopt / dedup / promote core, and it is where
  `gc-protocol-1` (High: manifest-trust adopt bypasses the condemn marker), `tla-fidelity-6` and
  `tla-fidelity-8` are anchored. High mention density is not coverage: a file that 27 audits each
  read a fifth of has no reader who saw the interactions between the fifths, which is exactly the
  shape of the defect `gc-protocol-1` turned out to be.

### backfill-6 -- `Formats/CasRefWireVocab.{h,cpp}` (82 lines), the shared token vocabulary of all four ref formats, was walked by no audit (Low)

- **Anchor / Gap**: `CasRefWireVocab.cpp` is named once, in passing, by `bc4` (and once by
  `test-coverage-fuzzing-1` as an example of an unfuzzed parser); `CasRefWireVocab.h` is named only
  in `coverage-map`'s inventory. It is absent from `bc4`'s 14-file full-read list, from
  `upgrade-compat`'s 11-file list, from `security`'s list, and from `tier1`'s region table — tier1
  read `CasRefLogFormat`, `CasRefCatalogFormat`, `CasRefCkptFormat` and `CasRefSnapshotFormat` but
  not the vocabulary those four share.
- **Residual risk**: Low, sized by the file: 82 lines of key/enum spelling with no arithmetic and no
  I/O. It is raised because the miss is systematic rather than random — the file fell between a
  format audit organized by codec and a tier audit organized by subsystem — and because a wrong or
  ambiguous token spelling in a shared vocabulary is a silent cross-version compatibility bug of
  exactly the class `upgrade-compat` reports elsewhere (`upgrade-compat-5`, `-8`).

### backfill-7 -- `Gc/CasGcMaintenanceState.cpp` is the only CAS file named by zero audits, and the consumer of its `Corrupt` verdict was never traced (Low)

- **Anchor / Gap**: `Gc/CasGcMaintenanceState.{h,cpp}` (69 lines). The `.cpp` appears in no report;
  the `.h` only in `coverage-map`'s inventory. `bc4` deep-swept the *format*
  (`CasGcMaintenanceStateFormat.cpp`) and `ad5` names the header, so the encoding is covered and the
  access layer is not. Reading it for this audit: two functions, `readGcMaintenanceState` and
  `casGcMaintenanceState`, wrapping `backend.get` and `backend.casPut`. It rethrows anything that is
  not `CORRUPTED_DATA` and otherwise returns `status = Corrupt` **together with the token**.
- **Residual risk**: Low. The file is small, has no arithmetic, and fails closed on unexpected
  errors. The one nameable residual is that returning a live token alongside a `Corrupt` verdict
  makes a corrupt janitor cursor CAS-overwritable, and no audit traced who consumes `Corrupt` or
  what cursor value they substitute — a wrong substitution would silently reset the namespace
  janitor's paging position, which `ad2-12` already identifies as a slow path (1,000 objects per
  round). I did not trace the consumer; I am reporting the gap, not a defect.

### backfill-8 -- `Primitives/CasNamespaceLifeId.h` (77 lines) is a header-only implementation that only the enumerating audit named (Low)

- **Anchor / Gap**: named solely by `coverage-map`; `interleaving` mentions the type name in prose.
  There is no `.cpp`, so unlike the other unwalked headers, nothing else covers it by proxy. It
  contains the live implementations of `renderIncarnation` and `parseIncarnation` — the rendering and
  parsing of the 128-bit namespace-life incarnation, with a `LOGICAL_ERROR` on a zero incarnation and
  a strict 32-hex-character canonical-form check on parse.
- **Residual risk**: Low. Namespace-life identity is load-bearing for the namespace lifecycle
  findings (`crash-consistency-8`, `interleaving-2`, `gc-protocol-2`, `ad3-7`), and this is where its
  wire spelling is decided; a parse that accepted a non-canonical spelling would be the exact
  `bc4-9` defect class ("bodies accept non-canonical numeric spellings that the key parser rejects").
  Reading it here, the parser looks strict in the right direction — reject rather than normalize —
  which is why this is Low and not Medium.

### backfill-9 -- the interleaving audit's two explicitly unresolved questions have no owner, and one of them is a "both branches are bad" fork (Medium)

- **Anchor / Gap**: `interleaving.md` Coverage: "Not established, deliberately left out: whether the
  abandon path can delete a manifest body whose precommit record is already durable (needed to make
  interleaving-2 step 3 unconditional); whether a divergent two-epoch ref-log chain resolves to a
  hold or to a silent last-writer-wins in the recovery walk (**both branches are bad, but I could not
  pin which without executing the walk**)." Nothing in the round picks either up. tier1 deep-swept
  the recovery walk (`CasRefLedger.cpp`, 100% of the region) and refuted eleven candidate defects in
  it, but does not address the two-epoch divergence question, and `tla-fidelity` lists
  `runRecoveryWalkOnce` and `commitRefChunk` (~1,400 lines) as out of budget.
- **Residual risk**: Medium, and it is the round's clearest example of a known-unknown rather than an
  unknown-unknown. A silent last-writer-wins on a divergent ref-log chain is data loss; a hold is an
  availability wedge. The audit that found the fork could not resolve it statically and said so, the
  audit that read the region exhaustively was not asked the question, and the audit that owns state
  machines ran out of budget on the same function. It should be assigned explicitly, not left to
  whoever next reads `CasRefLedger.cpp`.

### backfill-10 -- `coverage-map`'s blind-spot list was published for tier4 to close and four items remain named by nobody else (Low)

- **Anchor / Gap**: `coverage-map.md`, "Blind spots not covered by the 39 audit angles", 11 items.
  Tracing each across the other 35 reports: #8 (`EmulatedSingleProcess`, called "the single most
  consequential blind spot") is picked up by 13 reports and is now well covered; #1 (`non_cas_keys`)
  by security and tier2, which produced `tier2-8`; #10 (`forgetDisk`) by five; #6
  (`CasByteBudget` sizing chain) by tier1 and ad5; #2, #3, #5 and #11 by ad3/bc4/performance in part.
  Still named by `coverage-map` alone: **#4** (`skew_margin_ms` and the
  `mountObservationThresholdMs` / `HeartbeatFloor` arithmetic relationship), **#7** (the
  `PartPathParser` split cache), and #9 (the read-only / `TruthAbsent` admission matrix) has only
  `mergetree-part-support` beside it, with `idisk-contract` explicitly deferring its correctness to
  the nonexistent mounts/leases audit.
- **Residual risk**: Low, and two of the three are reduced by direct inspection performed for this
  audit. #4 is largely closed in substance: tier2 read `CasServerRoot.cpp` in full including
  `mountObservationThresholdMs` and `computeHeartbeatFloor`, so the residual is only the
  `skew_margin_ms` value supplied by a caller outside the CAS root. #7 is **not a risk**: I read the
  cache rather than inheriting the concern, and it is a fixed 8-slot thread-local ring
  (`Parts/PartPathParser.cpp:35-59`, `kCapacity = 8`), so the unbounded-growth worry is unfounded,
  and every caller copies out of the returned reference within a single function without re-entering
  `splitCached`, so there is no dangling-reference hazard either. #9 is the one worth assigning: the
  admission matrix decides whether a refused operation fails closed or returns silent success, and
  `ad2-8` already reports a settled-vanished pool turning deletes into successful no-ops.

## Recommended next round (prioritized)

1. **Run the strip-fidelity diff first** (backfill-2). One whitespace-insensitive diff of the CAS
   tree against `842f2b37b8f`. It is hours of work, it was already scheduled and dropped once, and
   until it is done every finding in this round is attributed on trust. Nothing else should be
   started before it.
2. **Write tier3** (backfill-1, -3, -4): an exhaustive line-by-line sweep of `Gc/` (6,352 lines) and
   `Tools/` (2,082), in the tier1/tier2 style that demonstrably worked. Start with
   `Gc::runRegularRound` phase by phase and `Tools/CasFsck.cpp`, which between them carry the most
   deferrals.
3. **Add `Pool/CasPartWriteTxn.cpp` to a tier** (backfill-5). 902 lines, disowned by both tiers,
   host to `gc-protocol-1`. Cheapest high-value addition in the list.
4. **Assign the two interleaving forks** (backfill-9), specifically the divergent two-epoch ref-log
   chain. This needs the recovery walk executed, not read — so it is the natural first item for a
   dynamic round rather than a static one.
5. **Then stop auditing statically and start executing.** The static method is close to exhausted:
   116 of 130 files walked, ~200 findings, and the four categories that would move the needle all
   need a running system. In order of evidence-per-hour:
   (a) **fuzz the 13 decoders** — the libFuzzer scaffold is already in-repo per
   `test-coverage-fuzzing-1`, and it directly tests `bc1`'s eight overflow findings and `bc4`'s ten
   decode findings; (b) **restore the deleted tests from `842f2b37b8f` and run them under
   TSan/ASan** — settles `concurrency`'s 14 findings and its withdrawn candidates; (c) **stand up a
   real S3 and a real GCS lane** — `ad6`'s seven High findings and `test-coverage-fuzzing-2`/`-3` all
   say the conditional-write contract has never been validated against a store CAS did not write
   itself; (d) **a crash-at-step-N harness**, which `test-coverage-fuzzing-6` notes is half-built
   from existing in-process test seams.
6. **Retire the deferral-to-sibling convention, or enforce it.** Eight deferrals in this round point
   at audits that do not exist (`tier3`, `tier4`, `mounts-and-leases`, `decommission`, `formats`).
   A round should publish its audit list and reject a Coverage section that defers to a name not on
   it; otherwise the gap is structurally invisible until an audit like this one goes looking.

## Coverage

**Reviewed.** All 36 report files in `cas/docs/cas-audit-rerun-20260812/reports/` (9,257 lines
total): the `Scope`, `Region walked`, `Coverage`, `Deferred`, `Not covered`, `Blind spots` and
`By-design` sections of each, read in full; finding titles and severities of all 36 enumerated. The
CAS tree enumerated exhaustively: 130 files, per-file line counts, per-file basename search against
every report, cross-checked against tier1's and tier2's region tables and against the explicit
"Read in full" lists in bc1, bc2, bc3, bc4, bc5, bc6, bc7, security, upgrade-compat, encryption,
performance, tla-fidelity, concurrency, ad1-ad7, mergetree-part-support and datatype-agnosticism.
Directory-level and round-level coverage percentages computed from that mapping. Cross-round check
for `tier3`/`tier4` across all three `cas-audit-rerun-*` directories.

**Read from the CAS tree directly** (only to size a residual risk honestly rather than repeat a
peer's concern): `Gc/CasGcMaintenanceState.cpp` in full (40 lines),
`Primitives/CasNamespaceLifeId.h` (parse/render), `Parts/PartPathParser.cpp:30-64` and its six
`splitCached` call sites. This inspection **downgraded** backfill-10's item #7 from a suspected
unbounded-cache risk to no risk, and produced the one nameable residual in backfill-7.

**Not covered / boundaries.** I did not re-audit any code and claim no defect in CAS itself: every
finding here is about the audit round. Basename search is a proxy for review and is imperfect in
both directions — the `{h,cpp}` shorthand correction is applied by hand from the tier region tables,
so a header covered only by a shorthand I missed would appear one row too pessimistic in the
"enumerated only" table; conversely a file cited once as another audit's evidence counts as
"region-read" here even though nobody read it. The "deep sweep" column reflects what reports
*claim*; I did not verify any claim by re-reading the file. I did not read the earlier
`cas-audit-rerun-20260730` or `-20260811` rounds except to establish where `tier3.md` and `tier4.md`
do exist. Per the code-only rule, no `docs/**` narrative was used as evidence about CAS behaviour;
the peer reports are used as evidence about *the audit round*, which is this audit's subject.

**No dynamic analysis of any kind was performed** — nothing was built, run, checked out or modified,
consistent with every peer report and with the read-only constraint on the target tree.
