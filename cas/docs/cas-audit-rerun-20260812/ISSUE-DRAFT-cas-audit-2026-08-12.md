# CAS — consolidated static audit findings, 2026-08-12 re-run (tracking)

> Draft to replace [#2031](https://github.com/Altinity/ClickHouse/issues/2031).
> Suggested title: **CAS — consolidated static audit findings, 2026-08-12 re-run (tracking)**
> Suggested labels: `cas`, `audit`, `tracking`
> Once opened, close #2031 with a pointer here and do not triage against its numbering.

## Why this supersedes #2031

The CAS PR was reopened and substantially refactored: protobuf wire formats were replaced by
self-describing text/NDJSON, the ref ledger and GC were reworked, and the pool/mount/backend layer
changed shape. Enough moved that per-finding re-verification against the old list stopped being
meaningful.

So all **39 audits were re-run from scratch**. No prior finding was carried forward, re-verified, or
used as a checklist. **The `CAS-###` IDs here are freshly numbered and do not correspond to the
numbering in #2031** — please do not cross-reference the two lists.

The audits were run against a **code-only branch** (`cas-code-only-strip`), with comments and design
docs stripped, precisely because the previous round found prose that no longer described what the
code did. Intended behaviour was inferred from types, control flow, error classification, and
fail-open versus fail-closed branches. Shipped strings (exception messages, setting descriptions)
were treated as admissible evidence; comments and `docs/**` were not.

## Audit target

| | |
|---|---|
| Repo / branch | `Altinity/ClickHouse`, `cas-code-only-strip` |
| Base commit | `842f2b37b8f` |
| Tree audited | base plus the uncommitted comment/doc strip, as of 2026-08-12T09:40Z |
| Code root | `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/` — 129 files, 36,603 lines |
| Method | static reasoning only; no build, no runtime, no fault injection |

## Results

**349 raw findings** across the 39 reports, merged by root cause into **135 product findings**:

| Severity | Count |
|---|---|
| High | 21 (24 before applying the #2031 verdicts, see below) |
| Medium | 98 |
| Low | 13 |

Three further items are properties of the audit round or of the strip itself rather than product
defects, and are kept separately as `NOTE-1`..`NOTE-3`.

### Reconciled against #2031's existing triage

#2031 has no comments; all of the developer's verdicts are inline in its body. Every one of the 135
new findings was matched against that triaged list by root cause, so nothing already ruled on gets
re-litigated. Full mapping in `RECONCILIATION-2031.md`.

| Bucket | Count | Disposition |
|---|---|---|
| **A** — already adjudicated (by-design / not-a-bug / wontfix / out-of-scope) | 15 | Not re-raised as defects; carried with the inherited verdict |
| **B** — marked fixed, but still found | 11 | Highest priority: the fix is believed to be in place |
| **C** — re-confirmed still-present | 51 | Merge the new anchor into the existing item |
| **D** — genuinely new | 58 | New work, mostly in refactor-introduced code |

Three of the 24 Highs are accepted design positions and are **not** presented as High here:
reads never re-verifying the content hash (#2031 CAS-003/005, *"S3 has many durability nines and
hashes objects itself; CAS will not re-hash on read"*), bucket lifecycle/Object Lock/storage-class
not being detected (CAS-016/017, *"plain bucket only"*), and the pool-wide reader-floor ratchet
(CAS-009, out-of-scope). Two more are partially inherited: CAS-009's staged-body half and CAS-023's
`gc_enabled=false` half remain open, the rest is closed. That leaves **21 High** — 13
re-confirmations of already-open items and 8 new.

### Marked fixed in #2031, but still present (read this first)

These are the items where the tracking issue and the code disagree, so they carry the most
information. Each cites the old id, the claimed fix, and the current anchor.

| New | Old | Claimed fixed | What still stands |
|---|---|---|---|
| CAS-048 | CAS-006 | "durable publish no longer runs under `DataPartsLock`" | `MergeTreeData.cpp:5918-5922` still commits a CAS transaction under the held lock on the covering/empty-part path |
| CAS-092 | CAS-030 | "no cross-node wall-clock trust" | `CasServerRoot.cpp:196-209` still judges another node's liveness against this node's `system_clock`, on the destructive decommission path |
| CAS-110 | CAS-085 | "`allow_stale` retired in code" | still declared and forwarded through two layers, then silently discarded at `CasRefLedger.cpp:214-215`, with callers relying on the semantics |
| CAS-036 | CAS-026 | protobuf removed, so the uncapped decode is gone | the text codec still reads to EOF uncapped and sizes a buffer from the declared zstd frame size |
| CAS-122 | CAS-075 | `header_hash` replaced by the `!`-critical-key gate | that gate has no producer (`emit_unknown_critical_key` never set), so writer-honesty enforcement is unchanged |
| CAS-029 | CAS-011 | "CAS checks at startup that versioning is off" | the check runs only for config-declared GCS clients, and is a warning when it fails |
| CAS-098 | CAS-014 | GC liveness metrics landed | still cannot answer "has GC stopped reclaiming": `last_success_age_seconds=0` conflates never-led with just-succeeded |
| CAS-062 | CAS-013 | "SQL fsck landed" | runs `detail=false` with no scoping, and `clean()` excludes crash-residue counters, so it cannot say what is wrong |
| CAS-037 | CAS-039 | `logical_size` removed from the envelope | unchecked `uint64` wrap is systemic in the text codec and now reaches `offset + length` on the read path |
| CAS-043 | CAS-209 | version-skew relink degrades to a byte fetch | the fallback catches `CORRUPTED_DATA` only, while the generation check throws `UNKNOWN_FORMAT_VERSION`, so relink fails outright |
| CAS-065 | CAS-012 | "e2e tested on real S3 and GCS" | no CI lane exercises the native or GCS dialect, so it is not regression-protected (a static audit cannot see a manual run) |

One item goes the other way: CAS-057 inherits a soft dismissal (#2031 CAS-007, *"should be fine —
tests catch nothing"*), but the fresh audit anchors an unconditional `LOGICAL_ERROR` with a real
caller, so its premise no longer holds and it should be re-opened.

### Severity rubric

Graded on realistic impact under a plausible trigger, not worst-case theory. Two rules did most of
the work, and both differ from the previous round, so counts are not directly comparable:

1. **A fail-closed loud failure grades below silent corruption.** A visible error is normally
   Medium — the operator learns immediately and nothing is silently wrong. It is High only when the
   refusal is unbounded or unrecoverable.
2. **Operability, observability, cost and scale gaps are not High on their own.** They are promoted
   only when they directly cause an unbounded outage.

Applied symmetrically: anything whose impact is silent loss or silent wrong results was promoted out
of Medium regardless of how narrow the anchor looked.

## High severity (24)

| ID | Class | Finding |
|---|---|---|
| CAS-001 | DATA-LOSS | shadow/FREEZE and backup namespaces are pool-global while every exclusion primitive is per-server-root |
| CAS-002 | DATA-LOSS | manifest-trust `adoptEvidence` bypasses the condemn marker and edge-before-observe |
| CAS-003 | CONCURRENCY | the GC lease has no TTL, is stealable on differential observation, and destructive phases are never revalidated |
| CAS-004 | INTEGRITY | `GC REBUILD` has no writer/mount interlock and "read-only" does not gate writes |
| CAS-005 | DATA-LOSS | a repointed committed ref is unrevertible; durable mutations happen before `commit()` with a silent best-effort rollback |
| CAS-006 | DATA-LOSS | cross-namespace `RENAME` is a per-ref non-atomic migration ending in an unconditional source drop, with no reconciler |
| CAS-007 | DATA-LOSS | nested `server_root_id` is accepted, and decommissioning the ancestor destroys a live descendant member |
| CAS-008 | SECURITY | content addressing defaults to a non-cryptographic 128-bit hash and reads never re-verify |
| CAS-009 | INTEGRITY | an occupied content address is admitted on existence alone; no re-upload or staged body is ever re-hashed |
| CAS-010 | INTEGRITY | an empty conditional token turns a fenced write into an unconditional clobber |
| CAS-011 | INTEGRITY | plain-object writes bypass the request controller and the margin-checked fence; indeterminate outcomes are never resolved |
| CAS-012 | DATA-LOSS | lifecycle rules, Object Lock and storage-class transitions are undetected and fail open; Glacier reads have no restore-and-retry |
| CAS-013 | COMPAT | one node admitting a hash algorithm rewrites the pool-wide reader floor to its own build number |
| CAS-014 | CORRECTNESS | the file-placement classifier is a closed suffix allowlist that misses shipped MergeTree file names, routing them fully in memory |
| CAS-015 | LIVENESS | waits on single-flight, leader and recovery paths have no deadline and no cancellation |
| CAS-016 | LIVENESS | `attempt_timeout_ms` never reaches the wire, and the blob payload read bypasses the CAS backend entirely |
| CAS-017 | LIVENESS | namespace removal latches admission closed before anything is durable; the lane has terminal states with no exit |
| CAS-018 | LIVENESS | latches and leadership are set or released outside RAII; `noexcept` and destructor paths allocate |
| CAS-019 | CORRECTNESS | part-folder single flight is keyed by ref only, collapsing different manifest ids onto one key |
| CAS-020 | INTEGRITY | `getStorageObjects` returns objects that are not the file's bytes, because the envelope offset is dropped |
| CAS-021 | INTEGRITY | ambiguous conditional-write outcomes are reported as definite ones |
| CAS-022 | DATA-LOSS | the orphan-manifest sweep applies no protection to a manifest whose namespace has no catalog row |
| CAS-023 | DATA-LOSS | deletes are accepted and silently do nothing when GC is disabled or the pool has settled as vanished |
| CAS-024 | DATA-LOSS | two CAS disks sharing a pool and a `server_root_id` share one namespace; a MOVE between them deletes the moved part |

Full entries — class, code anchor, impact, minimal trigger, and the contributing audits — are in
`NEW-FINDINGS.md`. The 98 Medium and 13 Low findings are listed there in the same shape.

## Structural themes

Individual findings cluster into a smaller number of design-level causes. These are the ones worth
fixing as patterns rather than one anchor at a time:

1. **Namespace scoping is inconsistent.** `server_root_id` prefixes live namespaces and nothing
   else, and namespace identity has no per-disk component — so shadow, FREEZE and backup namespaces
   are pool-global, unowned by every exclusion primitive, and invisible to sweeps that need a mount
   lease. Nesting is not rejected. (CAS-001, CAS-007, CAS-024, CAS-077)
2. **Fail-open on ambiguous or unverifiable backend results.** Bucket-configuration preconditions
   are skipped or downgraded to warnings when they cannot be evaluated, and indeterminate write
   outcomes are reported as definite in both directions. (CAS-012, CAS-021, CAS-029 – CAS-032)
3. **Durability is claimed before it is achieved, and cannot be undone.** Repoints, multi-part
   commits, cross-namespace renames, generation seals and blob bodies all become durable before the
   step that would make them consistent; rollbacks are `noexcept` and silent, with no reconciler.
   (CAS-005, CAS-006, CAS-072, CAS-075, CAS-076, CAS-080)
4. **Content addressing is never re-verified.** Admission is by existence alone; re-uploads and
   resurrects are size-checked only; staged bodies are re-read but not re-hashed; reads never
   verify. Every integrity guarantee rests on one producer-side hashing pass over a
   non-cryptographic default digest. (CAS-008, CAS-009, CAS-088, CAS-089)
5. **Exclusive access rests on tokens and leases that are not fencing tokens.** An empty ETag
   becomes an unconditional clobber, the GC lease has no TTL and is not revalidated before
   destructive phases, plain-object writes skip the controller, and the mount fence carries an
   identity it never checks. (CAS-003, CAS-010, CAS-011, CAS-129, CAS-130)
6. **Cost is O(total pool) where it should be O(churn).** Every GC round re-folds all edges and
   re-lists the whole ref prefix; every 256 commits re-encodes a namespace; every hardlink re-reads
   the source manifest. (CAS-035, CAS-054, CAS-055, CAS-112, CAS-114, CAS-116, CAS-120)
7. **Budgets and caps are checked after materialization, or unreachable.** Size caps validate an
   already-built buffer, the inline budget fires only at commit, and several pool caps have no
   configuration path at all, making their validators dead code. (CAS-044, CAS-046, CAS-105,
   CAS-113, CAS-115)
8. **Cache accounting is fictional.** The view cache weighs every manifest as 256 bytes; the
   manifest and dedup caches under-weigh by ~2x and ~3.1x. Every configured memory budget is
   advisory, and one of them also defeats an oversized-entry guard. (CAS-045, CAS-115, CAS-118)
9. **Day-2 tooling can detect but not localize or repair.** fsck is counts-only and report-only,
   only `gc/state` has a rebuild path, `cas-inspect` cannot decode eight formats, and the only verb
   that clears a dead member's slot erases its data first. (CAS-061 – CAS-063, CAS-097, CAS-100,
   CAS-123)
10. **The safety-critical surfaces have no executable specification.** No decoder is fuzzed, no
    property-based tests exist, no CI lane exercises a real conditional-write dialect, and there is
    no crash-at-step-N harness — exactly the coverage that would pin the crash-consistency and
    conditional-write findings. (CAS-064, CAS-065, CAS-109)

## Suggested triage order

1. The 11 "marked fixed but still present" items above, since the fix is currently believed to be
   done. Within them, the safety- and availability-relevant ones first: CAS-048, CAS-092, CAS-110,
   CAS-036, CAS-122, CAS-029, CAS-098.
2. The silent data-loss set: CAS-001, CAS-002, CAS-005, CAS-006, CAS-022, CAS-023, CAS-024.
3. The fencing and integrity set, where a fix changes protocol shape: CAS-003, CAS-004, CAS-010,
   CAS-011, CAS-021.
4. The availability cliffs: CAS-015, CAS-016, CAS-017, CAS-018.
5. Treat theme 10 as a precondition for trusting any fix in themes 2–5: without a real
   conditional-write CI lane and decoder fuzzing, these classes cannot be regression-tested. Note
   the developer's standing position that decoder fuzzing is not a merge gate (#2031 CAS-010) — the
   point here is regression protection for the fixes above, not a new mandate.

## Method, scope and limits

- **Static only.** No build, no execution, no fault injection, no multi-node chaos. Findings state a
  trigger; none has a runtime reproduction.
- **Code-only evidence.** Comments and `docs/**` were excluded by construction. Where a contract
  genuinely cannot be recovered from code, that is recorded rather than guessed (see `NOTE-3`).
- **Tests.** The audited working tree has the CAS test corpus deleted by the strip; the
  test-coverage audit therefore read tests from the base commit. That deletion is an artifact of the
  audit branch, not of the PR (`NOTE-1`).
- **What this round cannot tell you.** Real S3/GCS conditional-write behaviour, sanitizer results,
  fuzzing results, actual performance, and true multi-node race outcomes. `Mode::EmulatedSingleProcess`
  is auto-selected for local object storage, so local runs do not exercise the real dialect.
- **Inherited verdicts.** Bucket-A items are carried with the developer's original reasoning quoted
  rather than re-argued. Where the fresh evidence contradicts the premise of a dismissal, that is
  stated explicitly instead of silently re-raising the item.

## Reports

All 39 per-audit reports, the consolidated list, and this draft live in the regression repo under
`cas/docs/cas-audit-rerun-20260812/`:

`codeonly-line` · `coverage-map` · `idisk-contract` · `write-protocol` · `read-protocol` ·
`gc-protocol` · `gc-rebuild-feature` · `jepsen-anomaly` · `security` · `concurrency` ·
`interleaving` · `crash-consistency` · `upgrade-compat` · `tla-fidelity` · `bc1-offset-overflow` ·
`bc2-writebuffer-spill` · `bc3-exception-safety` · `bc4-protobuf-decode` (reframed as structured
decode hardening) · `bc5-wide-part-read` · `bc6-mtime-semantics` · `bc7-blocking-io-locks` ·
`ad1-hash-determinism` · `ad2-deletion-erasure` · `ad3-day2-dr-runbook` · `ad4-migration` ·
`ad5-resource-exhaustion` · `ad6-s3-lifecycle-cross-region` · `ad7-protocol-skew` ·
`mergetree-part-support` · `datatype-agnosticism` · `alter-merge-mutation` · `encryption` ·
`performance` · `test-coverage-fuzzing` · `tier1` (ref ledger/catalog core) · `tier2` (pool runtime,
mount, backend) · `tier3` (GC internals, tools) · `tier4` (residual surfaces) ·
`backfill-not-reviewed`

Every finding carries a `file:line` anchor in the audited tree and names the audits that reported
it, so each one can be triaged independently.

---

*This audit round was produced with AI assistance. Every finding is anchored to code in the audited
tree; severities and merges were re-graded in a dedicated pass.*
