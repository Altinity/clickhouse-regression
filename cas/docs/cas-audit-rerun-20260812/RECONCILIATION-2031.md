# Reconciliation against tracking issue #2031

This document reconciles the 135 product findings of the 2026-08-12 CAS re-run
([`NEW-FINDINGS.md`](NEW-FINDINGS.md), with detail in [`reports/`](reports/)) against the
131 triaged findings in tracking issue
[Altinity/ClickHouse#2031](https://github.com/Altinity/ClickHouse/issues/2031), using the live
body of that issue as fetched today.

Three facts govern how the comparison was done.

1. **#2031 has zero comments.** Every developer verdict is inline in the issue body, on the
   finding's own bullet, in the form `— resolution: <verdict> (Filimonov: <reasoning>)`, plus
   the four summary triage tables at the bottom of the body ("Closed by Filimonov",
   "Acknowledged real", "Minor / will-probably-fix", "Round 2 — Filimonov High-severity
   triage"). Where this document relies on an adjudication it quotes Filimonov verbatim from
   those lines rather than paraphrasing. Mikhail Filimonov is the CAS author and his reasoning
   is treated as authoritative.
2. **The two `CAS-###` numbering schemes are unrelated.** The 2026-08-12 round renumbered from
   scratch and carried nothing forward. Every id below is written `NEW-CAS-###` (2026-08-12
   round) or `OLD-CAS-###` (#2031 catalogue). Numeric coincidences are meaningless: e.g.
   NEW-CAS-033 (pool-wide `suppress_destructive`) happens to match OLD-CAS-033 in substance,
   while NEW-CAS-116 (quadratic staging vector) and OLD-CAS-116 (quadratic manifest lookup)
   are different defects that merely share a number.
3. **Matching was done on root cause and mechanism, not wording, class label or anchor.** The
   tree was refactored between rounds — protobuf and the binary formats were removed, the root
   shards and ref ledger were rebuilt, GC was reworked — so most matches have a completely
   different `file:line`. Several new findings are anchored in files that did not exist in the
   audited round.

#2031 also contains a second, untriaged section, "🆕 New findings from the 2026-07-30 re-run"
(`NEW-AD1-1` … `NEW-write-3`). Those items carry no verdict — every checkbox is unchecked and
no reasoning is attached — so they are **not** treated as adjudicated here. They are cited only
as corroboration where the 2026-08-12 round independently re-finds them, which matters for
bucket B: in several cases the contradiction was already visible in the prior round and was
never triaged.

Headline counts: **A = 15**, **B = 11**, **C = 51**, **D = 58** (total 135).

## Summary

| Bucket | Count | What it means for triage |
|---|---|---|
| **A** — already adjudicated, closed by the developer (📐 / 🚫 / ❌ / ↗) | 15 | Do not re-raise as defects. Carry into the new issue pre-marked with the inherited verdict, or drop. Includes 3 of the 24 new Highs, which should not be presented as High. |
| **B** — developer marked ✅ fixed, but the fresh audit still finds it | 11 | Highest-value bucket. These are the items that need the developer's attention first, because the fix is believed to be in place. Each is either an incomplete fix or a fix that addressed a different aspect of the same defect. |
| **C** — re-confirmed still-present (old verdict 🔴 / 🛠 / 🟡) | 51 | Already accepted as open. Merge the fresh anchor and evidence into the existing item instead of opening a new one; 12 of these strengthen or relocate the old evidence materially. |
| **D** — genuinely new | 58 | Real new work. Split roughly into refactor-introduced defects (new ref ledger, new GC, new request-control and event layers, new tools) and previously unexamined areas. |

## A -- already adjudicated by the developer (do not re-raise)

| NEW-CAS-### | Title (short) | OLD-CAS-### | Verdict | Filimonov's reasoning (quoted) |
|---|---|---|---|---|
| **NEW-CAS-008** (High) | non-cryptographic default hash, reads never re-verify | OLD-CAS-003, OLD-CAS-005 | 🟡 partial / 📐 by-design; 📐 by-design / YAGNI | "selectable hash landed — closes weak-collision concern; will **not** re-verify hash on read — incompatible with \"CH does not slow down\""; "S3 has many durability nines and hashes objects itself; CAS will not re-hash on read" |
| **NEW-CAS-012** (High) | lifecycle rules / Object Lock / storage-class transitions undetected, fail open | OLD-CAS-016, OLD-CAS-017 (+ OLD-CAS-052 🔴 for the Glacier half) | 📐 by-design / 🛠 docs; 📐 by-design | "lifecycle expiration must be off like versioning; add explicit user-facing bucket requirements; hard to detect without admin access"; "do not enable Object Lock/WORM/retention/lifecycle/versioning on the bucket — plain bucket only" |
| **NEW-CAS-013** (High) | one node's algorithm admission rewrites the pool-wide reader floor | OLD-CAS-009 | ↗ out-of-scope | "needs attention later; not a blocker; model may be wrong" |
| **NEW-CAS-027** | any bucket-credential peer can disable, fence or misdirect another member | OLD-CAS-004, OLD-CAS-211 | 📐 by-design | "bucket credential = whole trust boundary; all pool users same trust"; "bad actor with pool access is already doomed; provenance self-asserted / content-equality observable" |
| **NEW-CAS-028** | unsalted pool-global blob keys: no per-subject shred, residue, dedup oracle | OLD-CAS-019, OLD-CAS-211 (+ OLD-CAS-071 🔴 for crypto-shred) | 📐 by-design / ❌ wontfix | "this *is* the essence of CAS dedup — will not \"fix\"" |
| **NEW-CAS-033** | all reclamation gated on a whole-pool clean-pass predicate, no bound, no signal | OLD-CAS-033 | 📐 by-design | "prefer fail-closed safety under GC uncertainty; reclaim may stall" |
| **NEW-CAS-034** | per-round reclamation budgets sit below the steady-state creation rate | OLD-CAS-018, OLD-CAS-106 | 📐 by-design / ❌ wontfix; 📐 by-design | "erase SLA is not part of the disk contract; operator can `GC RUN` anytime; GC cadence ~5–10 min; GDPR faster-than-that unlikely" |
| **NEW-CAS-042** | one global build number is every object's minimum reader; change-point registry unused | OLD-CAS-009 (+ OLD-CAS-076 🔴 for the `Roster` throw) | ↗ out-of-scope | "needs attention later; not a blocker; model may be wrong" |
| **NEW-CAS-057** | `moveFile`/`replaceFile` on a committed part file always throws `LOGICAL_ERROR` | OLD-CAS-007 | 🚫 not-a-bug / 🟡 soft | "should be fine — tests catch nothing; glance someday — **not a blocker**" |
| **NEW-CAS-059** | encrypted disk layered over CAS with no capability check | OLD-CAS-046 (+ OLD-CAS-113 🔴 for the missing gate) | ↗ out-of-scope | "CAS+encryption needs design/dev/testing; should be workable later — not now" |
| **NEW-CAS-060** | per-file random IV makes every file a unique blob, destroying dedup | OLD-CAS-046 | ↗ out-of-scope | "CAS+encryption needs design/dev/testing; should be workable later — not now" |
| **NEW-CAS-064** | no CAS decoder is fuzzed, no property-based tests | OLD-CAS-010 | 📐 by-design / YAGNI | "same trust model as CAS-005 — trust S3; less trust ⇒ more perf loss; no decoder fuzz mandate as gate" |
| **NEW-CAS-071** | mount and pool state read and written outside the mutex that guards it | OLD-CAS-090 (+ OLD-CAS-091, whose own ✅ text records the residual) | 📐 by-design | (verdict recorded with anchors only: `Pool/CasMountRuntime.h:400`; `CasMountRuntime.cpp:156-163` `renewWatermarkOnce` unlocked; `:226-249` reassign under `Pool::remount_mutex` only) |
| **NEW-CAS-083** | lightweight `DELETE` and mutations free only rewritten files' bytes | OLD-CAS-019, OLD-CAS-018 | 📐 by-design / ❌ wontfix | "this *is* the essence of CAS dedup — will not \"fix\"" |
| **NEW-CAS-102** | 11 ProfileEvents can never fire; server-root I/O counted as GC I/O | OLD-CAS-214 | ⚪ info | "`classifyCasNs` uses unanchored substring match (metric misattribution only, no correctn[ess impact])" |

Several of the fresh round's loudest themes are, in fact, accepted design positions rather than
defects. **Integrity by delegation to S3** — content addressing is verified once, on the
producer side, and never again — is the position behind OLD-CAS-003, OLD-CAS-005 and
OLD-CAS-010; it disposes of NEW-CAS-008 and NEW-CAS-064 outright and covers half of
NEW-CAS-009. **The bucket credential is the entire trust boundary** (OLD-CAS-004,
OLD-CAS-211) disposes of NEW-CAS-027 and of the residue/oracle halves of NEW-CAS-028; note
that it does *not* extend to unprivileged SQL users, so NEW-CAS-132 is not covered by it.
**A plain bucket is a hard prerequisite** (OLD-CAS-016, OLD-CAS-017): lifecycle, versioning,
Object Lock and retention must simply be off, so NEW-CAS-012's core is documentation, not
code. **Deletion is not erasure and there is no erase SLA** (OLD-CAS-018, OLD-CAS-019)
disposes of NEW-CAS-083 and most of NEW-CAS-028 and NEW-CAS-034. **Fail-closed reclamation is
preferred to uncertain reclamation** (OLD-CAS-033) disposes of NEW-CAS-033. **Encryption over
CAS is out of scope** (OLD-CAS-046) disposes of NEW-CAS-059 and NEW-CAS-060.

Four honesty notes on this bucket:

- **NEW-CAS-057 is the one A item whose premise the fresh evidence contradicts.** OLD-CAS-007
  was dismissed on the strength of "should be fine — tests catch nothing; glance someday". The
  fresh audit anchors an unconditional `LOGICAL_ERROR` in `moveFile` for any source not staged
  in the same transaction, with `DeleteBitmapFileOps::writeBitmapToStorage` as a real caller
  (`CA/ContentAddressedTransaction.cpp:1030-1055`). The dismissal was explicitly soft
  ("glance someday"), so this should be re-opened rather than carried as closed.
- **NEW-CAS-013 and NEW-CAS-042 inherit ↗ out-of-scope, which is deferral, not dismissal.**
  Filimonov's words were "needs attention later; not a blocker; model may be wrong". They
  should be carried as deferred compatibility work, not deleted.
- **NEW-CAS-034 is only partly covered.** OLD-CAS-018 and OLD-CAS-106 adjudicate reclaim
  *latency* as a by-design function of cadence and budgets. NEW-CAS-034's stronger claim — that
  the shipped `gc_round_ref_cleanup_budget = 5000` per 60 s round and the 1,000-key/round
  janitor page sit *below* the steady-state creation rate, so debris accumulates without bound
  — is a different assertion and is not disposed of by either verdict. Carry the
  budget-versus-rate arithmetic as an open question even though the latency complaint is closed.
- **NEW-CAS-012 and NEW-CAS-028 and NEW-CAS-059 each have an open sub-aspect** tracked by a
  🔴 old id (OLD-CAS-052 archive-tier reads with no restore-and-retry; OLD-CAS-071 no
  crypto-shred; OLD-CAS-113 the missing DiskEncrypted-over-CAS guard). Those halves belong in
  bucket C's disposition even though the finding as a whole lands in A.

## B -- marked fixed, but still found

Eleven contradictions. In each case the developer's ✅ (or, in two cases, an adjudicated
verified-safe 📐/⚪ assertion) is cited with the anchor the fix claimed, followed by the fresh
anchor and mechanism. Where the match is arguable it is stated as such.

### NEW-CAS-048 vs OLD-CAS-006 -- CAS part publish still runs object-store I/O under `DataPartsLock`
- **Old verdict and claimed fix:** ✅ fixed. Filimonov: "durable publish **no longer** runs
  under `DataPartsLock`" (also in the Round-2 High triage table: "Durable publish **no longer**
  under `DataPartsLock`").
- **What the fresh audit finds now:** `src/Storages/MergeTree/MergeTreeData.cpp:5918-5922`
  performs the rename plus `commitTransaction()` *inside the caller's* `DataPartsLock`, and the
  path `:5545-5546` → `DataPartStorageOnDiskBase.cpp:780-789` →
  `CA/ContentAddressedTransaction.cpp:961` reaches remote publish from there. A throttling or
  5xx bucket therefore stalls the table's parts lock, blocking every SELECT, merge scheduling
  and part-set mutation on that table (`bc7-1`).
- **Assessment: incomplete fix.** The off-lock publish exists — the fresh round confirms it on
  the replicated `renameParts()` path — but it was not applied to the covering-part path used by
  `DROP PARTITION`/`REPLACE PARTITION`. This was already visible in the prior round as the
  untriaged `NEW-BC7-1`, which named the remaining call sites (`MergeTreeSink.cpp:379`,
  `MutatePlainMergeTreeTask.cpp:134`, `MergePlainMergeTreeTask.cpp:160`). Two independent rounds
  now find the same asymmetry. This is the highest-confidence contradiction in the set.

### NEW-CAS-098 vs OLD-CAS-014 -- the "GC stopped reclaiming" signal still cannot answer the question it exists for
- **Old verdict and claimed fix:** ✅ fixed / 🛠 recheck. Filimonov: "should be OK now; worth
  re-verify — **not a blocker**".
- **What the fresh audit finds now:** the surfaces landed but are not usable for the failure they
  were added for. `CA/Gc/CasGcScheduler.cpp:312-327` computes health process-locally and
  ephemerally; `.h:74` computes `ever_succeeded` and never exposes it, so
  `last_success_age_seconds = 0` means both "never led" and "succeeded just now"
  (`StorageSystemContentAddressedMounts.cpp:52-55`, `:177-191`); `is_leader = 0` conflates
  stopped, follower and crashed; `GC STOP` is node-local, does not survive restart and is
  invisible to peers (`CasGcScheduler.cpp:67-79`); `pending_reclaim` is monotone (`:170-172`) so
  it never sheds spared or replaced entries; there are no `CurrentMetrics` gauges
  (`src/Common/CurrentMetrics.cpp:239-241`); and `CASGCClampSuppressedPasses`
  (`ProfileEvents.cpp:803`) fires every round by construction, so the one counter that would
  flag a shut destructive gate is noise.
- **Assessment: incomplete fix.** The metric surface exists; the specific silent failure named
  in OLD-CAS-014 ("GC stopped reclaiming" is invisible) is still invisible. Filimonov himself
  asked for a re-verify; this is that re-verify, and it fails.

### NEW-CAS-110 vs OLD-CAS-085 -- `allow_stale` was not retired; it is still plumbed and now silently ignored
- **Old verdict and claimed fix:** ✅ fixed. Filimonov classed R3 cosmetic and the resolution
  records "`allow_stale` retired in code", anchored at `Pool/CasRefLedger.cpp:174-179`.
- **What the fresh audit finds now:** the parameter is still declared
  (`CA/Pool/CasRefLedger.h:62-63`), still forwarded through `CA/Pool/CasPool.cpp:1135-1137`, and
  in the definition at `CA/Pool/CasRefLedger.cpp:214-215` it is unnamed and never read. Two
  callers explicitly request stale tolerance and silently get the strict path:
  `CA/Parts/PartFolderAccess.cpp:283` and the literal `true` at `:483`. They can block on
  namespace recovery and can throw where they expect a cheap best-effort answer
  (`codeonly-line-4`, `tier1-4`).
- **Assessment: incomplete fix / worse than before.** "Retired" was implemented as "ignored"
  rather than "removed", so the callers that relied on the semantics lost them without a
  compile error. The original coupling concern is indeed gone; a new correctness defect on the
  same symbol replaced it.

### NEW-CAS-092 vs OLD-CAS-030 -- a cross-node wall-clock liveness gate survives
- **Old verdict and claimed fix:** ✅ fixed / 🟡 residual tradeoff. Filimonov (2026-07-17):
  "lease liveness via token stability on observer clock, **no cross-node wall-clock trust**;
  remaining mount-wait tradeoff accepted".
- **What the fresh audit finds now:** the token-stability lease is present, but
  `CA/Pool/CasServerRoot.cpp:196-209` still decides another node's liveness by comparing
  `expires_at_ms > now_ms` where `now_ms` comes from this node's `system_clock`
  (`CA/Pool/CasPool.cpp:386-396`) — the decommission epoch mint. Separately the fence and the
  request it admits are on different clocks: `CLOCK_BOOTTIME` at
  `CA/Pool/CasMountRuntime.cpp:57-62`, `:101-111`, `:212-213` versus `steadyClockNowMs` at
  `CA/Backend/CasRequestControl.cpp:80-83`, so a host suspend or live-migration between fence
  admission and the conditional PUT is invisible to the deadline that admitted it. Both
  `CLOCK_BOOTTIME` reads are also unguarded on non-Linux targets
  (`CasMountRuntime.cpp:60`, `CasServerRoot.cpp:54`) (`bc6-5`, `bc6-6`, `bc6-9`).
- **Assessment: incomplete fix.** The fix removed cross-node wall-clock trust from the *lease
  renewal* path. One cross-node wall-clock decision remains, on the destructive
  `SYSTEM CAS DROP MEMBER` path, which is the worst place for it.

### NEW-CAS-036 vs OLD-CAS-026 -- the decode size cap did not survive the format replacement
- **Old verdict and claimed fix:** ✅ fixed. Filimonov (2026-07-17): "protobuf/binary formats
  removed → self-describing text", anchored at `Formats/CasTextFormat.cpp:389,401`.
- **What the fresh audit finds now:** the OOM-on-planted-oversized-object mechanism is intact in
  the replacement path. `CA/Backend/CasObjectStorageBackend.cpp:284-293` reads control objects
  with `readStringUntilEOF` and no cap; `:333-338` sizes the read buffer to the attacker's
  declared size; and `CA/Formats/CasTextFormat.cpp:387-399` still does
  `out.resize(declared zstd frame size)` before decompressing — the same shape as the original
  complaint, at one of the two exact lines the fix cited. Overwriting `_pool_meta`, `owner`,
  `mount`, `_ckpt` or a ref-log object with a multi-gigabyte body OOMs the victim before any
  format check runs; and `CasTextFormat.cpp:164-166` adds Θ(k²) key comparisons on a single
  64 MiB line (`security-3`, `security-4`, `bc4-6`).
- **Assessment: fix addressed a different aspect.** Removing protobuf removed the
  `ParseFromArray` / `static_cast` specifics. The root cause — bucket-sourced bytes are
  materialized and sized from attacker-declared values with no cap — was not addressed and is
  now anchored in the replacement format.

### NEW-CAS-037 vs OLD-CAS-039 -- the numeric-overflow class was fixed by deleting one field
- **Old verdict and claimed fix:** ✅ fixed —
  "`CasBlobEnvelopeFormat.cpp:162,240-248` — `logical_size` removed from envelope; `header_len`
  derived from `'\n'`; the size-consistency invariant it tried to enf[orce]".
- **What the fresh audit finds now:** unchecked `uint64` wrap is systemic in the text codec, and
  it still defeats read-window gating. `CA/Formats/CasTextFormat.cpp:193-223`
  (`readU64Number`/`readU64String`/`readU32Number` over `readIntText`) wraps mod 2^64; a planted
  manifest `sz` produces a wrapped read window at `CA/Pool/CasManifestReader.cpp:139-143` and
  `CA/ContentAddressedMetadataStorage.cpp:1439-1454`; `std::stoull` accepts `-1` for a GC
  generation key and `max_gen + 1` overflows; `published_at_ms` overflows the Poco timestamp
  multiplication; `blob_header_len - 1` and the fsck byte accumulator share the class
  (`bc1-1`, `bc1-2`, `bc1-4` … `bc1-8`, `bc4-9`).
- **Assessment: fix addressed a different aspect.** Deleting `logical_size` removed the one
  documented exploit of the wrap; the arithmetic itself was never hardened, and the fresh round
  finds the same wrap now reachable on the read path (`offset + length`) rather than on the
  envelope invariant.

### NEW-CAS-122 vs OLD-CAS-075 -- the critical-extension gate the fix relied on has no producer
- **Old verdict and claimed fix:** ✅ fixed — "`Formats/CasBlobEnvelopeFormat.h:53–58`
  (`header_hash` removed); `!`-key gate `CasTextFormat.cpp:249–251`". The fix therefore rests on
  the `!`-prefixed critical-key mechanism replacing writer-honesty enforcement.
- **What the fresh audit finds now:** the mechanism cannot be used. At
  `CA/Formats/CasTextFormat.cpp:240-242` a `!` key throws `UNKNOWN_FORMAT_VERSION`, and its only
  writer is guarded by `EnvelopeHeader::emit_unknown_critical_key`, which is never set true
  anywhere in the tree. Its error code is also on the non-recoverable path. Meanwhile strict
  formats (`CasFormat.cpp:107-112`) raise `CORRUPTED_DATA` at `CasTextFormat.cpp:243-244` for
  any additive field in `RefCkpt`, `RefCatalog`, `GcMaintenanceState`, `RunFile` or `FoldSeal`
  (`upgrade-compat-7`, `upgrade-compat-8`).
- **Assessment: incomplete fix.** The removal half of the fix landed; the enforcement half it
  was traded against is dead code, so "critical extension" enforcement still relies on writer
  honesty — the exact residue OLD-CAS-075 named.

### NEW-CAS-029 vs OLD-CAS-011 -- the startup versioning check runs only for GCS-typed clients and fails open
- **Old verdict and claimed fix:** ✅ fixed / 📐 by-design. Filimonov: "CAS checks at startup
  that versioning is off; versioned buckets unsupported".
- **What the fresh audit finds now:** the provider dialect is declared by configuration and
  never detected (`CA/Backend/CasObjectStorageBackend.cpp:53-67`), so on AWS S3 and every
  S3-compatible store the versioning precondition is skipped entirely; on GCS it is downgraded
  to a warning whenever `GetBucketVersioning` fails or is not permitted
  (`src/IO/S3/Client.cpp:1301-1307`, `S3ObjectStorage.cpp:514-529`). A versioned bucket then
  either wedges all reclamation or aborts a GC round with `LOGICAL_ERROR` *after* the delete,
  with prior deletes silently recoverable as versions (`ad6-1`, `ad6-2`, `ad6-5`, `ad2-10`,
  `ad6-8`, `tla-fidelity-9`).
- **Assessment: incomplete fix.** OLD-CAS-011's own text already said the guard existed only
  "when the versioning API is queryable, else fails open"; the ✅ was granted for the startup
  check without closing the fail-open and provider-coverage gaps. The prior round said the same
  thing in the untriaged `NEW-ad2-1` and `NEW-ad2-2`. Given "versioned buckets unsupported" is
  also a 📐 position, the residue here is specifically *detection*, not support.

### NEW-CAS-062 vs OLD-CAS-013 -- SQL fsck landed, but the SQL surface cannot say what is wrong
- **Old verdict and claimed fix:** ✅ fixed. Filimonov: "SQL fsck landed; still slow vs GC —
  backlog to speed up".
- **What the fresh audit finds now:** the verb exists but is counts-only:
  `src/Interpreters/InterpreterSystemQuery.cpp:2534` calls `runFsckNow(/*detail=*/false)`, so
  from SQL an operator learns that the pool is corrupt but never which keys; no deadline and no
  scoping are plumbed (`CA/ContentAddressedMetadataStorage.cpp:739-745`); `CA/Tools/CasFsck.h:114`
  returns a report and `Tools/` contains no repair function; and the `clean()` verdict excludes
  the two crash-residue counters, so a pool with body-without-meta residue reports clean
  (`ad3-2`, `crash-consistency-9`).
- **Assessment: incomplete fix.** OLD-CAS-013's premise was that "the most valuable health
  diagnostic is internal-only"; making it callable without making it informative does not
  deliver that. The prior round's untriaged `NEW-ad3-1` already reported the missing deadline
  plumbing. Note that the *repair* half is separately open as OLD-CAS-093 (🔴), re-confirmed
  here as NEW-CAS-100.

### NEW-CAS-065 vs OLD-CAS-012 -- the conditional-write guarantee is not pinned by any CI lane
- **Old verdict and claimed fix:** ✅ fixed. Filimonov: "e2e tested on real S3 and GCS; Azure
  still not".
- **What the fresh audit finds now:** the only automated coverage of conditional writes is the
  emulated in-process backend — `src/Disks/tests/gtest_cas_backend_contract.cpp:250-258` and
  `gtest_cas_backend_generation.cpp:12-120` — and `ci/defs/altinity_jobs.py` has no GCS
  parameter set, with CAS-over-local as one unsanitized lane (`:116-120`). The native
  `If-None-Match`/`If-Match` path and the GCS generation-token path have no end-to-end lane
  (`test-coverage-fuzzing-2`, `-3`, `-8`).
- **Assessment: incomplete fix, with a caveat.** A static audit cannot see a manual e2e run, and
  Filimonov's statement may be entirely accurate about what was executed. What still stands is
  the durable part of OLD-CAS-012's complaint: the single most safety-critical path has no
  repeatable, regression-protecting lane, so the guarantee is verified once rather than
  continuously. Classified B on that basis; if the ✅ was meant only as "we ran it once", this is
  better read as a C.

### NEW-CAS-043 vs OLD-CAS-209 -- the relink version-skew fallback does not catch the generation error
- **Old verdict and claimed adjudication:** 📐 by-design, recorded as verified-safe:
  "Relink is data-safe under version skew (fail-closed publish-nothing → byte-fetch fallback;
  format bumps caught by the manifest's own comp[atibility check])", anchored at
  `ContentAddressedExchange.h:140-146`, `Formats/CasFormat.cpp:64-70`.
- **What the fresh audit finds now:** the fallback's `catch` filters on `CORRUPTED_DATA` only
  (`CA/ContentAddressedMetadataStorage.cpp:1610-1619`) while the generation check throws
  `UNKNOWN_FORMAT_VERSION` (`CA/Formats/CasFormat.cpp:90`), so a fetch between two nodes on
  different `G_BUILD` fails outright instead of degrading to a byte fetch
  (`src/Storages/MergeTree/DataPartsExchange.cpp:1182-1184`, `:793-799`) (`upgrade-compat-3`).
- **Assessment: contradiction of an adjudicated verified-safe assertion**, not of a ✅ fix. The
  fail-closed part holds (nothing wrong is published); the "byte-fetch fallback" that made it
  safe *and* available does not engage for the one error the skew actually produces. Listed in B
  because the position it contradicts is an adjudicated one; the consequence is availability,
  not data loss.

Two candidates were deliberately **not** put in this bucket:

- **NEW-CAS-116** (staging is O(F²)) is not a contradiction of OLD-CAS-116's ✅. That fix
  genuinely indexed manifest lookups (`Formats/CasPartManifestFormat.cpp:329-351`,
  `Parts/PartFolderAccess.cpp:85-134`); the quadratic that remains is in a different container,
  the transaction's staged-entry vector (`CA/ContentAddressedTransaction.cpp:510`, `:652`, `:810`
  …). Filed D.
- **NEW-CAS-111** (64 MiB ref-table admission cap fails writes at ~610k refs) is *not* filed as
  a contradiction of OLD-CAS-008's ✅ ("journals should be fine now"), because the fix addressed
  journal growth and trimming, whereas the new ceiling is hit by *live* ref volume where
  trimming cannot help. It is filed C against OLD-CAS-100, which is still open and describes
  exactly the "hard-limit wedge" mechanism. The nuance worth reporting to the developer is that
  write availability is still coupled to a 64 MiB encoded-object ceiling.

## C -- re-confirmed still-present

| NEW-CAS-### | OLD-CAS-### | Old verdict | Change in evidence |
|---|---|---|---|
| NEW-CAS-001 | OLD-CAS-070 | 🔴 still-present | **Strengthened + explained.** Old: shadow/detached refs silently retain deleted data. New: the cause is that `shadowNamespace()` (`:897-900`) omits the `serverPrefix()` that `liveNamespace()` (`:886-889`) applies, so shadow refs are pool-global — adding a cross-server hazard (UNFREEZE on either server deletes the other's frozen parts) and removing the watermark floor for those namespaces. |
| NEW-CAS-002 | OLD-CAS-031 | 🔴 still-present | **Strengthened + relocated.** Old: receiver trusts sender-supplied `blob_size`/`path`, only blob *presence* revalidated (`CasPartWriteTxn.cpp:781-796`). New: `adoptEvidence` (`:478-486`, accepted at `:675-695`) consults neither the object nor the durable `Condemned` marker, so a committed manifest can name a deleted blob with no source to re-upload from. Note: OLD-CAS-001's 🚫 ("reader cannot keep reading after part removed") does **not** cover this — it is a writer-side adopt path, not a reader. |
| NEW-CAS-003 | OLD-CAS-032 | 🔴 still-present | **Strengthened.** Old: zombie leader's unconditional `pulseHeartbeat` clobbers `gc/hb.owner` (`CasGc.cpp:2989-3003`). New anchor `:3089-3103` (`pulseHeartbeat` discards its `casPut` result) plus a steal predicate at `:3155-3186` and destructive phases (`:611-665`, `:865-884`, `:906-930`) that never revalidate — so two actors can run destructive phases concurrently, and a rebuild never renews across an unbounded scan. |
| NEW-CAS-004 | OLD-CAS-015 | 🟡 partial | **Contradicts the partial's premise.** Filimonov: "GC REBUILD still poorly tested / may have issues; mount-lease should take correctly now". New: `CasGc.cpp:2725` is the only exclusion taken, the mount census result is *discarded* at `:2968-2971`, and the two entry points require opposite read-only postures (`ContentAddressedMetadataStorage.cpp:491` vs `CommandCaGcRebuild.cpp:26,43-47`). |
| NEW-CAS-005 | OLD-CAS-021, OLD-CAS-097 | 🔴 still-present | **Same + strengthened.** Old: multi-part `commit()` not atomic, best-effort rollback; `updateRefPayload` one-shots not rolled back. New: repoint of an already-committed ref is unrevertible (`ContentAddressedTransaction.cpp:280-289`, `:327-348`) and the compensator `dropRefIfMatches` is `noexcept` and swallows every error (`PartFolderAccess.cpp:518-562`). OLD-CAS-020's ✅ (leak on `promote`-overwrite) is *not* contradicted — this is the revertibility aspect. |
| NEW-CAS-006 | OLD-CAS-022, OLD-CAS-044 | 🔴 still-present | **Strengthened.** New anchor `ContentAddressedTransaction.cpp:846-874`: the ref set is a snapshot taken once, so refs added during the walk are dropped with the source, and the terminal `dropNamespace(from_ns)` at `:874` is unconditional. Ordinary part removal takes the same path. |
| NEW-CAS-007 | OLD-CAS-064 | 🔴 still-present | **Escalated; match uncertain.** OLD-CAS-064 covers `server_root_id` *collision* (equality). NEW-CAS-007 is *nesting* (prefix), where `SYSTEM CAS DROP POOL MEMBER` on `srid=a` prefix-deletes a live `srid=a/b` (`CasServerRoot.h:104-134`, `CasDecommission.cpp:124-135`, `:186-202`). Same missing-validation root cause, new destructive consequence; a reader could reasonably file this as D. |
| NEW-CAS-009 | OLD-CAS-038 | 🔴 still-present | **Strengthened; partly A.** Old: scratch temp file never verified against its key between hash and upload. New: the same absence of digest re-verification on *every* admission path — dedup hit, retry, `resurrect`, `promoteStaged` (`CasPartWriteTxn.cpp:250-305`, `:387-420`, `:463-471`; `ContentAddressedTransaction.cpp:1276-1295`), all size-checked only. The "do not re-verify an existing object" half is arguably covered by OLD-CAS-005's 📐; the scratch/staged-body half is not. |
| NEW-CAS-015 | OLD-CAS-034, OLD-CAS-083 | 🔴 still-present (OLD-083 "will probably fix") | **Strengthened, much wider.** Old: one coalesced shard read with no deadline. New: no deadline and no cancellation on ref-append followers (`CasRefLedger.cpp:1457-1492`), namespace recovery blocking every reader (`:956-1106`), `DROP TABLE` waiting for the publish leader (`:3451-3458`), `future.get()` on part load (`PartFolderAccess.cpp:240-252`), and `remount_mutex` held across two quiescence waits (`CasPool.cpp:635`, `:702-733`, `:828-896`). |
| NEW-CAS-020 | OLD-CAS-047 (+ OLD-CAS-041) | 🔴 still-present | **Strengthened with a concrete corrupting consumer.** Old: two "size" semantics, correctness depends on all reads going through the CAS plan. New: `getStorageObjects` drops the envelope offset (`ContentAddressedMetadataStorage.cpp:1336-1340`, `:1368-1371`), so the generic object-storage copy path used by `MOVE PART/PARTITION TO DISK` and TTL moves copies the 256-byte envelope as file content and produces a corrupt destination part with no error. |
| NEW-CAS-021 | OLD-CAS-035 | 🔴 still-present ("minor") | **Strengthened, now bidirectional.** Old: presence-asserting closures misreport a lost-ACK success as failure. New: `CasRequestControl.cpp:427-435`, `:498-506` treat content equality as proof of our own authorship (a loser of a race is told it committed); `:357-368`, `:543-562` report ambiguity as foreign occupancy; and `NoSuchKey` is mapped to `PreconditionFailed` (`CasObjectStorageBackend.cpp:109-124`). |
| NEW-CAS-023 | OLD-CAS-043 | 🔴 still-present | **Strengthened.** Old: DROP/TRUNCATE free zero bytes synchronously, leak forever if GC disabled. New: with `gc_enabled=false` the scheduler never starts (`:611`) while the remove paths never consult the flag (`ContentAddressedTransaction.cpp:683`, `:705`, `:1069`) *and* every manual reclamation verb is refused with `BAD_ARGUMENTS` (`:461-464`, `:492-494`, `:715-717`); on a settled-vanished pool a drop returns success having done nothing (`:809-812`). |
| NEW-CAS-024 | OLD-CAS-064 (+ OLD-CAS-041) | 🔴 still-present | **Escalated to silent data loss.** Two CAS disks on one pool with the same `server_root_id` resolve to the same `(namespace, ref)` (`:886-889`, `:903-934`), so a `MOVE PARTITION TO DISK` between them publishes then drops the same ref; validation does not detect the collision (`ContentAddressedSettings.cpp:119-137`). |
| NEW-CAS-025 | OLD-CAS-015 (+ OLD-CAS-108) | 🟡 partial | **Relocated.** Old: rebuild's non-atomic scans can bless a baseline missing a blob. New: the rebuilt generation starts from an empty `prior_runs` and folds only `+1` deltas (`CasGc.cpp:2809-2824`, `:2876-2951`), so every blob unreferenced at rebuild time is permanently unreclaimable, and the graduation guard is vacuous because the rebuild call site omits the confirm callback. |
| NEW-CAS-026 | OLD-CAS-031 | 🔴 still-present | **Strengthened.** Old: only blob *presence* revalidated. New: both gates are `pool_uuid` equality (`DataPartsExchange.cpp:313-330`, `:780-787`), the adopted manifest gets no presence check on any dependency (`ContentAddressedMetadataStorage.cpp:1592-1636`), and the publish uses `check_consistency=false` (`DataPartsExchange.cpp:1262`). OLD-CAS-054's ✅ (cookie *value* validated) holds; the objection is now that the validated value is insufficient. |
| NEW-CAS-032 | OLD-CAS-051 | 🔴 still-present | **Same, relocated.** Nothing binds pool identity to an endpoint or region (`CasPoolMeta.cpp:100-104`, `:111-119`), so endpoint failover onto a CRR destination is indistinguishable from the primary. |
| NEW-CAS-035 | OLD-CAS-057, OLD-CAS-050 | 🟡 partial/mitigated; 🔴 | **Contradicts the "mitigated" claim.** OLD-CAS-057 was mitigated to "single LIST, no ns×shard fan-out"; the fresh audit finds the single LIST is retained whole in memory with no cursor (`CasGc.cpp:2561-2593`) and is called unconditionally including on deferred rounds (`:2597`), while the fold is over all edges (`CasBlobInDegree.cpp:484-555`) with an unbudgeted delta vector (`:1379`). OLD-CAS-089's ❌ ("huge single-round delta is a known limit") covers the peak-memory half. |
| NEW-CAS-038 | OLD-CAS-077 | 🔴 still-present | **Strengthened, now systemic.** Old: `decodeFoldSeal` casts enums without validation (`CasFoldSealFormat.cpp:189`). New: safety-critical fields are *optional* with least-safe defaults across `decodeMountLease` (`CasServerRootFormats.cpp:147-169` — a truncated lease decodes to "expired, unfenced"), `CasGcStateFormat.cpp:50-63`, `CasBlobMetaFormat.cpp:66-81`, and two of four fold-seal entry points skip structural validation (`:294-305`, `:286`). |
| NEW-CAS-039 | OLD-CAS-066 | 🔴 still-present | **Relocated + strengthened.** Old: `createOrValidate` silently ignores passed `root_shards`/`blob_header_len` when a pool exists. New: root shards are gone, but `gc_shards` is adopted from bucket bytes with only a `>= 1` check (`CasPoolMetaFormat.cpp:116`, `:142`; `CasPoolMeta.cpp:94-95`) and silently overwrites the node's configured value (`CasPool.cpp:351-354`, `:547-550`) while sizing vectors and loop bounds. |
| NEW-CAS-041 | OLD-CAS-027 | 🔴 still-present | **Same root cause, harder consequence.** Old: additive fields dropped on re-encode by an older build (`skipUnknown` + decode-to-struct). New: because OLD-CAS-025's ✅ fix recomputes `payload_digest` by canonical re-encode of the decoded model (`CasPartManifestFormat.cpp:263-267`, `:272-279`), a tolerated or foreign field now reads as `CORRUPTED_DATA` rather than being silently dropped — the fix converted a silent-loss failure into a hard-fail one without addressing decode-to-struct. Not filed B: OLD-CAS-025's own claim (the digest *is* re-verified) holds. |
| NEW-CAS-044 | OLD-CAS-100 | 🔴 still-present | **Relocated.** Old: manifest soft-limit backpressure cannot prevent the hard-limit wedge. New: the 16 MiB per-part inline budget (`CasPartWriteTxn.cpp:54`) is enforced only after everything is staged (`:514-528`) with no re-classification to blob placement, so a legitimately wide part fails its INSERT permanently and reproducibly. |
| NEW-CAS-045 | OLD-CAS-049 | 🟡 partial/mitigated | **Contradicts the mitigation.** The bytes-based LRU credited in the old resolution is inoperative: `estimatedBytes() = 256 + manifest_size` (`PartFolderAccess.cpp:128-131`) while both producers hardwire `.manifest_size = 0` (`CasRefLedger.cpp:254-258`, `:273-276`), so `part_folder_cache_bytes` does nothing and the oversized-entry bypass guard never fires. |
| NEW-CAS-046 | OLD-CAS-096 | 🔴 still-present | **Strengthened.** Old: scratch FS-full fails the insert late, no pre-flight check. New: additionally unreserved and unaccounted (`DiskObjectStorage.h:65-67` returns `{}` for all three space queries), held for the whole transaction, defaults onto the server data volume (`MetadataStorageFactory.cpp:233-238`), and never swept at startup because only the in-process cleaner enumerates scratch (`ContentAddressedTransaction.cpp:148-172`). |
| NEW-CAS-055 | OLD-CAS-086 | 🔴 still-present ("minor/cosmetic") | **Relocated + strengthened.** Old: `readManifest` HEAD+GET not coalesced, absence not negatively cached. New: the shipped default `part_folder_validate=always` (`ContentAddressedSettings.cpp:55`) disables the cache short-circuit (`PartFolderAccess.cpp:172`), so `createHardLink` re-reads the source manifest per file (`ContentAddressedTransaction.cpp:816`) — hundreds to thousands of round trips per mutation, clone or FREEZE of a wide part. |
| NEW-CAS-061 | OLD-CAS-063 | 🔴 still-present | **Strengthened.** Old: no `PoolMeta`/control-plane backup-restore story. New: only `gc/state` has a rebuild path, and because every tool opens the pool through `_pool_meta` first (`CasPool.cpp:293-368`, esp. `:351-353`), damage to that one object disables the instruments needed to diagnose it; the shipped message states "there is no in-place migration" (`CasPoolMetaFormat.cpp:89-95`). |
| NEW-CAS-063 | OLD-CAS-062 | 🛠 will-fix | **Relocated.** The verb asked for now exists, but the only way to clear a dead member's mount slot is `SYSTEM CAS DROP POOL MEMBER`, which erases that member's namespaces first (`CasDecommission.cpp:137-183` before `:236-363`), and a crash between control-object deletion and the owner tombstone leaves a member `cas_mounts` cannot show and a re-run cannot repair. |
| NEW-CAS-066 | OLD-CAS-065 | 🔴 still-present | **Strengthened; partly new.** Old: Azure/non-S3 effectively unsupported for Native CAS. New: `checkConditionalWriteSingleAttemptSupport` returns early for non-Native mode and is only reached on the writable path (`CasObjectStorageBackend.cpp:78-91`), so read-only mounts never check; and the emulated single-process mode is chosen by storage type alone with no override (`ContentAddressedMetadataStorage.cpp:509-520`), which is a new sub-finding. |
| NEW-CAS-074 | OLD-CAS-072 | 🔴 still-present | **Strengthened.** Old: a crash between the round CAS and the hand-off strands a `gc/gen` prefix. New: the prune cursor advances even when it skips (`CasGc.cpp:2479-2484`, returning early on `suppress_destructive` at `:2460`, committing at `:2496`) and the compensating hand-off (`:829-856`) is one-shot, so nothing ever revisits `snap_pruned_through`. |
| NEW-CAS-075 | OLD-CAS-060 | 🔴 still-present | **Strengthened.** Old: failed-build debris reclaimed only by sweeps. New: `streamIfAbsent` makes the body durable before `writeFreshMetaClean` (`CasPartWriteTxn.cpp:423-429`, `:463-465`, `:471-474`), and the only lister of `blobsPrefix()` is fsck — so a body with no meta is reclaimed by no sweep at all and is excluded from the `clean()` verdict. |
| NEW-CAS-076 | OLD-CAS-072, OLD-CAS-108 | 🔴 still-present | **Same shape, new anchor.** GC writes the fold seal (`CasGc.cpp:2254`) before committing `gc/state` (`:804`), and the rebuild repeats it (`:2980`/`:2987`), so each crash in the window leaves a complete-looking seal for a generation no state references and nothing prunes. |
| NEW-CAS-081 | OLD-CAS-060 | 🔴 still-present | **Strengthened materially.** New: S3 staging objects are removed only in the `else if (committed)` branch while tracking is cleared unconditionally (`ContentAddressedTransaction.cpp:148-172`), and the residual sweep is `noexcept`, best-effort, own-`server_root_id`-only with no age filter (`CasServerRoot.cpp:1140-1168`) and runs once (`ContentAddressedMetadataStorage.cpp:596-607`). Whole part-file plaintext persists after any killed INSERT; a pod re-creation orphans it forever; two disks sharing an srid sweep each other's live staging. |
| NEW-CAS-082 | OLD-CAS-084 | 🔴 still-present ("minor") | **Contradicts the dismissal's premise.** Filimonov: "MPU leftovers typical for S3, GC cleans eventually". The fresh audit finds an exhaustive search of the CAS tree for `multipart` matches nothing — no abort, no reconciliation anywhere — so nothing in CAS ever cleans them; they are billed and invisible to fsck's `physical_bytes`. Probe debris is additionally excluded from the residual scan (`CasProbe.cpp:20-32`, `CasSentinelProbe.cpp:17-20`). |
| NEW-CAS-085 | OLD-CAS-112 | 🔴 still-present | **No longer latent.** OLD-CAS-112 called `generateObjectKeyForPath`'s `NOT_IMPLEMENTED` latent because "no MergeTree path calls them today". With `always_use_copy_instead_of_hardlinks=1` — accepted silently on a CAS table — `MutateTask.cpp:2490-2494`, `:2513-2517`, `:3306-3311` reach it (`ContentAddressedTransaction.cpp:363-366`, `:492-495`), permanently breaking every mutation, FREEZE, ATTACH/REPLACE PARTITION and backup-restore clone. |
| NEW-CAS-086 | OLD-CAS-048, OLD-CAS-099 | 🔴 still-present | **Strengthened, now a contract-level cluster.** Old: `getLastModified` semantics; `setLastModified` no-op. New adds `isDirectoryEmpty` returning true for every part dir (so `removeDirectory`'s non-empty guard never fires), `getHardlinkCount` constant 0 while `supportsHardLinks()` is true, and silent no-op removes on unclassified paths (`ContentAddressedMetadataStorage.cpp:1293-1305`, `:1172-1194`, `.h:121`; `ContentAddressedTransaction.cpp:683-780`, `:831-834`). |
| NEW-CAS-087 | OLD-CAS-073 | 🔴 still-present | **Same file, both directions.** Old: `looksLikePartDir` false-positives on names ending in three numeric groups. New: a component named `detached`/`moving` outranks part-dir detection entirely (`PartPathParser.cpp:140-162`), and any part dir failing the heuristic silently becomes a table-level file via the catch-all (`:274-277`). |
| NEW-CAS-089 | OLD-CAS-024 | 🔴 still-present | **Strengthened.** Old: `locate()` uses the fixed `PoolMeta.blob_header_len`, not the blob's own `header_len`. New: same (`CasManifestReader.cpp:137-144`), plus the envelope identity field is silently truncated on write (`CasBlobEnvelopeFormat.cpp:74-87`), the stamped version (`:102`) is never enforced on a production read path, and the decoder's only caller is `CasInspect.cpp:571`. The prior round's untriaged `NEW-ad7-3` said the same. |
| NEW-CAS-090 | OLD-CAS-113 | 🔴 still-present | **Strengthened.** Old: DiskEncrypted-over-CAS leaves control-plane metadata plaintext, composition untested, dedup lost. New adds concrete mechanisms: SSE-C breaks staging promotion because no copy-source SSE-C headers exist (`src/IO/S3/Client.cpp:1273-1287`), the manifest carries names, sizes and ≤1 MiB bodies in the clear (`CasPartManifestFormat.h:20-39`), AES-CTR carries no MAC (`FileEncryptionCommon.h:21-30`, `:114-139`), and immutable shared blobs make re-keying impossible. OLD-CAS-204's 📐 (SSE-S3/KMS transparent and recommended) is unaffected; SSE-**C** is the case that breaks. |
| NEW-CAS-091 | OLD-CAS-074 | 🔴 still-present | **Strengthened from theoretical to real.** Old: `checkNamespace`/`mountpointObjectKey` don't reject `.`/`..`, "safe only for" object keys. New: same acceptance (`CasLayout.cpp:295-319`, unlike every sibling validator), but the emulated-over-local mode is *auto-selected* by storage type, and those keys are then joined onto a filesystem root — so the traversal is real, not hypothetical. The prior round's untriaged `NEW-security-4` also flagged the mountpoint path. |
| NEW-CAS-093 | OLD-CAS-061 | 🔴 still-present | **From test-gap to defect.** Old: full-text/GIN and vector index build on CAS untested. New: the temp text-index directory takes its own `beginTransaction()` on a sibling dir *inside* the part (`TextIndexUtils.cpp:601-609`), publishing a ref under the part before the part exists, and its `removeRecursive` cleanup is one of NEW-CAS-086's silent no-ops, so the temp ref and its blobs survive. |
| NEW-CAS-094 | OLD-CAS-108 | 🔴 still-present | **Same root cause, new anchors.** A refused rebuild reports `performed=0` while leaving complete-looking run objects (`CasGc.cpp:2811-2824`, `:2832`) and a fold seal (`:2980` before the state CAS at `:2987`) behind, which a later round can adopt or reject as an "impossible" state; attempt numbering diverges from the normal round's `attempt = lease.seq`. |
| NEW-CAS-097 | OLD-CAS-062 | 🛠 will-fix | **Relocated.** Introspection landed but cannot localize: `system.cas_mounts` exposes `wedged_namespace_count` only (`:55`), `cas-inspect` has no branch for 8 of the 18 formats and mis-decodes `_files/` names ending in `mount`/`fold_seal` (`CasInspect.cpp:517-576`, `:532-562`), drops `RefCoverage::hold` (`:329-335`), and requires a raw key no shipped command can enumerate (`CommandCaInspect.cpp:26-27`). |
| NEW-CAS-100 | OLD-CAS-093 | 🔴 still-present | **Strengthened: the verdict is unsound, not just unrepaired.** Old: fsck detects Dangling but never repairs. New: run-checksum verification is gated on `!unref_hashes.empty()` (`CasFsck.cpp:654`), the stale-edge check is gated on `detail` which the SQL path never sets (`:707`), a namespace-scoped run reports the same "clean" as a full run (`:831-866`), `partial` is set only on timeout (`:903-920`), and two crash-residue counters are computed then discarded (`:824-829`). |
| NEW-CAS-111 | OLD-CAS-100 | 🔴 still-present | **Strengthened + quantified.** Old: soft-limit backpressure cannot prevent the hard-limit wedge. New: the per-namespace 64 MiB ceiling (`CasRefLogFormat.h:50`, `CasRefSnapshotFormat.h:40`) fails writes permanently and non-retryably at roughly 610k refs via `admits()` → `LIMIT_EXCEEDED` (`CasRefLedger.cpp:859-861`, `:2161-2169`). Also qualifies OLD-CAS-008's ✅: write availability is still coupled to a 64 MiB encoded-object ceiling, now on live state where trimming cannot help. |
| NEW-CAS-115 | OLD-CAS-049 | 🟡 partial/mitigated | **Contradicts the mitigation quantitatively.** `PartManifestWeight` misses ~2x of the real per-entry footprint (`CasManifestReader.h:49-58`) and `DedupWeight` returns a constant 64, ~3.1x under actual cost (`CasPool.h:464-471`), constructed with `NO_MAX_COUNT` so there is no entry-count backstop (`CasPool.cpp:165-168`). |
| NEW-CAS-118 | OLD-CAS-086, OLD-CAS-067 | 🔴 still-present | **Strengthened.** Old: HEAD+GET not coalesced; no read-side blob cache/pin. New: `backend.head(key)` runs at `CasManifestReader.cpp:58` *before* the cache probe at `:76-78` and the cache key includes the freshness token; `resolve()` runs before the view-cache probe (`PartFolderAccess.cpp:152`); and four independent routing/resolve sites mean one logical read resolves the ref several times, with no read snapshot. |
| NEW-CAS-119 | OLD-CAS-053 | 🔴 still-present | **Strengthened.** Old: throttle/429 storms compound with CAS-conflict retries, no adaptive backoff (`CasRequestControl.cpp:46-56` lumps 429/5xx with `PreconditionFailed`). New: conditional writes use a single-attempt client (`CasObjectStorageBackend.cpp:628-639`), so retry moves from the jittered SDK to CAS's un-jittered fixed backoff, up to 16 attempts, each adding a resolution GET. |
| NEW-CAS-120 | OLD-CAS-041 | 🔴 still-present | **Same, confirmed twice.** Every CAS destination goes through `copyDirectoryContentIntoTransaction`, a plain recursive `readFile`/`writeFile` loop (`DataPartStorageOnDiskBase.cpp:702-718`, `:652-679`), even CAS→CAS same-pool, while the relink optimization already exists on the interserver path. Identical to the prior round's untriaged `NEW-MIG-1`. |
| NEW-CAS-121 | OLD-CAS-042 | 🔴 still-present | **Strengthened.** Old: BACKUP is Atomic-DB-only; incremental dedup untested. New: same refusal (`DataPartStorageOnDiskBase.cpp:417-422`), plus `areBlobPathsRandom()` returning `false` (`ContentAddressedMetadataStorage.h:120`) forces checksums `FromReading` (`BackupEntryWithChecksumCalculation.cpp:124-127`), so even an incremental backup re-reads the whole dataset. |
| NEW-CAS-123 | OLD-CAS-040 (+ OLD-CAS-101) | 🔴 still-present | **Relocated.** Old: `bytes_on_disk` is logical, no physical/dedup view. New: fsck's byte accounting covers only `blobs/` (`CasFsck.cpp:578-596`), so a bucket-versus-table gap cannot be attributed to manifests, ref logs, snapshots, staging or generations, and "how much would dropping table X reclaim" has no surface; `previewDeletes` mixes physical and logical sizes. |
| NEW-CAS-129 | OLD-CAS-002 | 🚫 not-a-bug / 🟡 needs-repro | **The requested recheck, with a bounded window.** Filimonov: "looks overstated / \"высосана из пальца\"; maybe recheck carefully — **not a blocker**". Fresh: `requireAlive` is called once at entry to `promote` (`CasPartWriteTxn.cpp:125-128`, `:635`) and the ops builder never re-checks (`:657-729`), so a build admitted under epoch E1 can append on a fresh runtime after a self-remount to E2 up to `operation_deadline_ms` (default 90 s) later. Graded Low by the fresh round, consistent with "not a blocker". |
| NEW-CAS-130 | OLD-CAS-080 (+ OLD-CAS-029) | 🔴 still-present | **Same defect, extra facets.** Old: `allocateWriterEpoch` has no overflow guard and `MountLease min_active` defaults to 0. New: `allocateWriterEpoch` can still return 0 on the object-present path (`CasServerRoot.cpp:226-236`), `doStart` writes a literal `seq = 1` over the slot `claimMount` just bumped (`:1021` vs `:334`, `:347`), and `server_uuid`/`writer_epoch` are assigned but never consulted by `mayMutate`/`checkFenceOrThrow` — which is also the mechanism behind OLD-CAS-029's dual-mount concern. |

## D -- genuinely new in this round

| NEW-CAS-### | Title (short) | Severity | Why it has no old counterpart |
|---|---|---|---|
| NEW-CAS-010 | empty conditional token turns a fenced write into an unconditional clobber | High | Refactor-introduced: token minting in `CasObjectStorageBackend.cpp:165-173` and type-only validation at `:677-678` are new code. Adjacent to OLD-CAS-002, but Filimonov's dismissal there was about `writer_epoch` versus content-token fencing, not about a *missing* precondition. |
| NEW-CAS-011 | plain-object writes bypass the request controller and the margin-checked fence | High | `CA/Pool/CasPlainObjects.cpp` is new. Adjacent to OLD-CAS-053 (no adaptive backoff) and OLD-CAS-035, neither of which covers an entire write lane with no controller, no margin subtraction and 100 retries with zero backoff. |
| NEW-CAS-014 | file-placement classifier is a closed suffix allowlist missing shipped names | High | Previously unexamined as a defect. The prior round saw the same function and recorded it as benign (untriaged `NEW-datatype-agnosticism-3`), and OLD-CAS-202's ✅ asserted type-agnosticism — which remains literally true, since placement keys on file *names*, not data types. That is why this is D and not a contradiction of OLD-CAS-202. |
| NEW-CAS-016 | `attempt_timeout_ms` never reaches the wire; payload read bypasses the CAS backend | High | The request-control layer (`CasRequestControl`) is new; the payload-read bypass to `DiskObjectStorage.cpp:903-904` was not examined before. |
| NEW-CAS-017 | namespace removal latches admission closed before durability; terminal states with no exit | High | The ref-lane state machine (`RefLaneState`, `beginRemoving`) is new. |
| NEW-CAS-018 | latches and leadership set/released outside RAII; `noexcept` paths allocate | High | Exception-safety of the reworked ref ledger and pool teardown. OLD-CAS-023's ✅ covered a different teardown race in `CasMountRuntime`. |
| NEW-CAS-019 | part-folder single flight keyed by ref only, collapsing manifest ids | High | `Parts/PartFolderAccess` single-flight is new. |
| NEW-CAS-022 | orphan-manifest sweep applies no protection when the namespace has no catalog row | High | `Gc/CasOrphanManifestSweep.cpp` is new; the first-write window between `stageManifest` and `precommitAdd` did not exist in the audited shape. |
| NEW-CAS-030 | `skip_access_check` removes every bucket-configuration defense; decommission hard-codes it | Medium | New setting plus a new hard-coded call site (`CasPool.cpp:528`). OLD-CAS-012's ✅ was about e2e coverage, not about an opt-out that is unrecorded in the pool. |
| NEW-CAS-031 | conditional-write contract validated only for single-PUT, then assumed for multipart | Medium | The probe (`CasProbe.cpp:42`) is new. Deliberately not filed against OLD-CAS-012: the gap is in what the probe validates, not in whether real providers were exercised. |
| NEW-CAS-040 | part-manifest payload-zone banner written raw, validated only on decode | Medium | Encode-side/decode-side asymmetry in the new text manifest format; an entry path containing LF produces a permanently undecodable committed part. OLD-CAS-115's ✅ covered duplicate-path detection, a different check. |
| NEW-CAS-047 | blob upload pool is process-global, 16 threads, 16-slot queue, blocking enqueue | Medium | `CasBlobUploadPool` sizing and the blocking `scheduleImpl` were not examined; OLD-CAS-100 touched the same header for a different reason. |
| NEW-CAS-049 | `GC STOP`, shutdown and `FSCK` serialize behind whole in-flight unbounded scans | Medium | `gc_round_mutex`/`lifecycle_mutex` scoping is new. OLD-CAS-013's "still slow vs GC" acknowledged fsck cost, not mutual exclusion with every other lifecycle statement. |
| NEW-CAS-050 | GC scheduler joins thread objects outside the mutex; threads self-exit | Medium | `Gc/CasGcScheduler.cpp` is new. Same bug class as OLD-CAS-023 (✅ fixed) in a different component, so not a contradiction. |
| NEW-CAS-051 | snapshot-publish dispatch can leak its pending count and hang two unbounded waits | Medium | Snapshot publisher dispatch is new. |
| NEW-CAS-052 | anomaly reporting calls `shared_from_this()` on a possibly expiring pool | Medium | The anomaly-report path is new. |
| NEW-CAS-053 | ref-table cache budget enforced only at recovery; cannot evict a table being written; underflows | Medium | New subsystem. The prior round raised it as the untriaged `NEW-ad5-2`, which was never adjudicated. |
| NEW-CAS-054 | ref publication re-encodes the whole namespace every 256 transactions | Medium | Refactor-introduced: the snapshot threshold and `debugAssertBodyCounters` are new; the audited round's journals worked differently. |
| NEW-CAS-056 | a single-file write/unlink republishes the whole manifest twice per operation | Medium | This is the *cost* of OLD-CAS-111's ✅ fix (committed single-file unlink implemented via republish/repoint), i.e. a different defect near the fixed code, not a contradiction of it. |
| NEW-CAS-058 | cross-disk `ATTACH`/`REPLACE PARTITION FROM` into CAS is unimplemented and fails part-way | Medium | The `freezeRemote` transaction-less branch (`DataPartStorageOnDiskBase.cpp:593-621`) was not examined; OLD-CAS-041 covered MOVE, not ATTACH FROM. |
| NEW-CAS-067 | emulated conditional-write token is a filesystem mtime; pruning stalls on clock skew | Medium | Emulated-mode token machinery is new. |
| NEW-CAS-068 | `putIfAbsentControlled` swallows deterministic local failures as ambiguity | Medium | Asymmetry among five new sibling helpers; same family as OLD-CAS-035 but the opposite direction and a different mechanism. |
| NEW-CAS-069 | empty catches reclassify transient read failures as corruption | Medium | OLD-CAS-088's 📐 ("corrupt GC state ⇒ GC stop; recover via GC REBUILD") adjudicates *genuine* corruption. It does not cover a `MEMORY_LIMIT_EXCEEDED` being *misclassified* as corruption and driving a rebuild that (per NEW-CAS-025) permanently orphans blobs. |
| NEW-CAS-070 | remount self-healing permanently disabled by a lost wakeup, a latched flag, or one throw | Medium | Same latch machinery OLD-CAS-023's ✅ touched, but a different failure (permanent fence-closed, not UAF) introduced by the remount worker's structure. Filed D per the conservatism rule. |
| NEW-CAS-072 | staged-manifest debris cleanup tracks only one precommit binding | Medium | Different defect in the `abandon` machinery OLD-CAS-081's ✅ reordered; the ordering fix holds. |
| NEW-CAS-073 | condemn marker is not incarnation-scoped, is its own proof, and is never cleared | Medium | The blob-meta condemn marker is new (the audited round's equivalent coupling was OLD-CAS-085, since retired). |
| NEW-CAS-077 | a permanently lost node pins its own manifest debris as unreclaimable | Medium | The watermark-floor-from-mount-lease dependency in the orphan sweep is new; adjacent to OLD-CAS-062 but a distinct mechanism. |
| NEW-CAS-078 | namespace janitor rewinds its durable cursor on a transient LIST failure | Medium | `Gc/CasNamespaceJanitor.cpp` is new. |
| NEW-CAS-079 | ref trimming is starved by any concurrent catalog mutation anywhere in the pool | Medium | The single pool-global ref catalog is new. |
| NEW-CAS-080 | a snapshot published without a checkpoint advance is not re-driven on a quiescent namespace | Medium | New checkpoint protocol. |
| NEW-CAS-084 | reclaimed blobs are never evicted from the node-local filesystem cache | Medium | OLD-CAS-207's ⚪ recorded content-addressed keys as *correctness*-ideal for the FS cache, which remains true; capacity retention and local readability of erased content were never examined. |
| NEW-CAS-088 | `resurrect` is an unconditional, fence-unchecked overwrite returning a token it did not write | Medium | `resurrect` is new. Token-coherence family with OLD-CAS-079, but a different call and a different failure. |
| NEW-CAS-095 | `cas-gc-dryrun` is not a preview and is silently empty in the disaster state it exists for | Medium | New tool. |
| NEW-CAS-096 | the rebuild reports almost nothing about the quality of the baseline it blesses | Medium | `RebuildReport` is new. |
| NEW-CAS-099 | rolling restart and planned node removal have no quiesce, drain or handoff verb | Medium | Day-2 lifecycle verbs are new; OLD-CAS-062 asked for lease introspection, not an ordered drain. |
| NEW-CAS-101 | GC round counters derived from budget-truncated logs; phase rows carry round 0 | Medium | `system.cas_gc_log` and the phase timer are new. |
| NEW-CAS-103 | savings and outcome counters incremented before the outcome they claim is decided | Medium | New instrumentation on the HEAD-first dedup path. |
| NEW-CAS-104 | audit-event dispatch funnels read and write hot paths through one mutex, on by default | Medium | `CasEventDispatcher` and the `CasEvent` struct are new. |
| NEW-CAS-105 | the mount/lease/request budget and seven pool caps are unreachable from configuration | Medium | The shipped settings list is new; OLD-CAS-066 was about ignored *pool-creation* parameters, not about unreachable ones. |
| NEW-CAS-106 | the non-CAS config key allowlist is a fixed 18-entry set, so ordinary S3 keys abort disk load | Medium | New settings plumbing. |
| NEW-CAS-107 | no CAS setting can be changed by config reload; a removed CAS disk keeps its mount | Medium | Previously unexamined; the prior round raised it as the untriaged `NEW-ad7-3`. |
| NEW-CAS-108 | dead code and test-only seams compiled into the production binary | Medium | `CasInMemoryBackend`, the `ForTest` seams and the file-scope hook are new. |
| NEW-CAS-109 | no deterministic crash-at-step-N harness; settings validation has 6 tests | Medium | Coverage shape of the reworked tree; the audited round had no equivalent claim. |
| NEW-CAS-112 | every ref append re-reads and linearly rescans the pool-global ref catalog | Medium | The ref catalog is new. |
| NEW-CAS-113 | encoded-size caps are validated only after the oversized buffer has been built | Medium | New cap sites. |
| NEW-CAS-114 | recovery seals every skipped writer epoch one at a time, uncapped | Medium | New per-epoch seal chain. |
| NEW-CAS-116 | staging is quadratic in the number of files in a part | Medium | Deliberately not filed B against OLD-CAS-116's ✅: that fix genuinely indexed manifest lookups; the remaining quadratic is in the transaction's staged-entry vector, a different container. |
| NEW-CAS-117 | one object plus one meta object plus a 256-byte envelope per part file | Medium | Per-object overhead of the current layout was never quantified; OLD-CAS-067 was about the absence of a read cache. |
| NEW-CAS-124 | empty content hashes to the all-zero digest, which is also fsck's unparsable-key sentinel | Low | Fsck sentinel is new. |
| NEW-CAS-125 | `Xxh3Streamer` dereferences a null state, making the allocation-failure guard dead | Low | XXH3-128 arrived with OLD-CAS-037's ✅ fix (selectable hash); this is a new defect in new code, not a failure of that fix. |
| NEW-CAS-126 | the write-fence pre-check exists only on the S3 staging path | Low | Both staging backends are new. |
| NEW-CAS-127 | avoidable per-byte and per-line copying and allocation on hot paths | Low | Constant-factor review of the new text codec and write path. |
| NEW-CAS-128 | inline entries staged into a destination part that never gets a build fail the whole commit | Low | New inline-staging model. |
| NEW-CAS-131 | audit-event and cache-counter attribution defects | Low | New event log and view cache. |
| NEW-CAS-132 | bucket layout, hostnames, PIDs and server UUIDs disclosed to unprivileged SQL users | Low | Not covered by OLD-CAS-004/OLD-CAS-211: those adjudicate a *pool-credential* adversary ("bad actor with pool access is already doomed"); this is disclosure to a SQL user with no bucket access at all. |
| NEW-CAS-133 | `cas_mounts` renders a transient LIST failure identically to a non-existent pool | Low | `system.cas_mounts` is new. |
| NEW-CAS-134 | a receiver with two CAS pools in one policy advertises only the first | Low | Multi-pool relink advertisement was never examined. |
| NEW-CAS-135 | emulated mode holds one mutex across round trips and a process-wide mutex across a blob body | Low | Emulated backend internals are new. |

## Old findings with no counterpart in this round

Of the 131 old ids, 100 have at least one 2026-08-12 counterpart (as a match, a sub-aspect or an
explicit non-match note above). The remaining 31 are listed here. "Area not re-examined" is
grounded in the fresh round's own coverage map and in `NOTE-2`, which records that
`CasPartWriteTxn.cpp` was excluded by both tier sweeps by name and that four items on
`coverage-map`'s blind-spot list have no owner.

| OLD-CAS-### | Old verdict | Likely reason there is no counterpart |
|---|---|---|
| OLD-CAS-001 | 🚫 not-a-bug | Dismissed and not re-raised. The fresh `jepsen-anomaly` and `read-protocol` reports examined the read path and produced no reader-pin item, which is consistent with the dismissal. (Its writer-side sibling *is* re-raised as NEW-CAS-002.) |
| OLD-CAS-008 | ✅ fixed | Fix confirmed structurally: the audited journal is gone, replaced by the ref log/snapshot protocol. The residual 64 MiB coupling is reported under NEW-CAS-111. |
| OLD-CAS-020 | ✅ fixed | No re-find. `OwnerTransition`/`allow_repoint` is present in the fresh anchors (`repointRef`), and the fresh round's objections to that code are cost (NEW-CAS-056) and revertibility (NEW-CAS-005), not the manifest leak. |
| OLD-CAS-023 | ✅ fixed | Fix confirmed gone as a UAF; the fresh round's remount findings (NEW-CAS-070) are a different failure mode in the same machinery. |
| OLD-CAS-025 | ✅ fixed | Fix confirmed present — `payload_digest` *is* re-verified on decode. Its unintended forward-compatibility cost is NEW-CAS-041. |
| OLD-CAS-036 | ✅ fixed | `blob_header_len` floor re-examined by `read-protocol`/`bc4` (NEW-CAS-089 anchors the same field) with no re-find of the floor bug. |
| OLD-CAS-037 | ✅ fixed | Fix confirmed present: the algorithm is selectable and recorded in `PoolMeta` (`ContentAddressedSettings.cpp:33`, `CasPoolMeta.cpp:72`). Its side effects are NEW-CAS-013 and NEW-CAS-125. |
| OLD-CAS-045 | 🚫 not CAS | Dismissed as general ReplicatedMergeTree behaviour; the fresh round did not audit ZK↔storage divergence. |
| OLD-CAS-054 | ✅ fixed | Cookie-value validation is present. NEW-CAS-026 argues the validated value (`pool_uuid`) is insufficient, which is a sufficiency objection rather than a re-find. |
| OLD-CAS-055 | 🔴 still-present | Area not re-examined: no fresh report covers non-MergeTree engines, `tmp` disks, SSD-cache dictionaries or Distributed spool on a CAS disk. |
| OLD-CAS-056 | 🟡 partial | Superseded by the refactor — root shards are gone. The surviving create-once concern is re-raised for `gc_shards` as NEW-CAS-039. |
| OLD-CAS-058 | 🔴 still-present | Area not re-examined as its own item: `ad6` covered provider behaviour but no fresh finding targets the read-your-writes / strongly-consistent-LIST assumption. The prior round's untriaged `NEW-AD6-2` still stands. |
| OLD-CAS-059 | 🟡 partial | Area not re-examined: no MergeTree-experimental-transactions/MVCC audit in this round. |
| OLD-CAS-068 | 🟡 partial | Area only partially re-examined: NEW-CAS-020 covers the envelope offset and NEW-CAS-084 the FS cache, but no fresh finding targets partial-hit envelope alignment. |
| OLD-CAS-078 | 🔴 still-present | Probe concurrency not re-examined; the fresh probe findings are NEW-CAS-031 (multipart) and NEW-CAS-082 (probe debris). |
| OLD-CAS-079 | 🔴 still-present | Non-atomic HEAD-then-GET not re-raised directly; the closest fresh items are NEW-CAS-088 and NEW-CAS-118. |
| OLD-CAS-082 | 🔴 still-present, "will probably fix" | Journal double-append on idempotent retry not re-found — plausibly fixed with the ref-log rework, but the fresh round makes no claim either way. |
| OLD-CAS-083 | 🔴 still-present, "will probably fix" | Subsumed rather than dropped: NEW-CAS-015 covers undeadlined leader waits generally, but no fresh item targets batch-wide failure amplification specifically. |
| OLD-CAS-087 | 🔴 still-present | Force-fresh semantics on eventually-consistent backends not re-raised as such; NEW-CAS-055 and NEW-CAS-118 examine the freshness plumbing from a cost angle only. |
| OLD-CAS-092 | ✅ fixed | No re-find; `shard_write_seq` pruning on `dropNamespace` was not contradicted. |
| OLD-CAS-094 | 🔴 still-present | No proactive cold-blob scrub is still absent, but the fresh round folded integrity-verification concerns into NEW-CAS-008/009 rather than raising scrub separately — and OLD-CAS-005's 📐 governs it. |
| OLD-CAS-098 | 🔴 still-present | Partially covered: `bc5-wide-part-read` ran this round and produced NEW-CAS-014/045/055/116/117, but no item restates the wide/compact/packed read-branch test gap. |
| OLD-CAS-102 | 🔴 still-present | Relink-versus-byte-fetch observability in `system.replicated_fetches` not re-raised; NEW-CAS-134 mentions the missing diagnostic only in passing. |
| OLD-CAS-103 | 🔴 still-present | Move-versus-concurrent-GC remains untested; the fresh round's move findings are functional (NEW-CAS-020/058/120) and it did not restate the test gap. |
| OLD-CAS-104 | 🔴 still-present | Non-replicated dedup-log durability not re-examined. |
| OLD-CAS-105 | 🔴 still-present | RESTORE round-trip and Packed-part support not re-examined; NEW-CAS-121 covers BACKUP only. |
| OLD-CAS-107 | 🔴 still-present | No big-endian item this round (the prior round's untriaged `NEW-upgrade-compat-5` still stands); `upgrade-compat` spent its findings on generations and digests. |
| OLD-CAS-109 | 🔴 still-present | System-log-tables-on-CAS storm, `clickhouse-disks` and `EXCHANGE TABLES` not re-examined. |
| OLD-CAS-110 | 🟡 partial | FETCH-to-detached relink coverage not restated; NEW-CAS-134 covers a different relink gap. |
| OLD-CAS-117 | 🔴 still-present | `FINAL`, parallel-replica reads and patch-apply-on-read not re-examined. |
| OLD-CAS-201, 203, 205, 206, 208, 210, 212, 213 | ⚪ info / 📐 / ✅ | Informational records with no fresh counterpart. Two are worth qualifying rather than deleting: OLD-CAS-203 ("all mainstream MergeTree part types supported") is qualified by NEW-CAS-057 and NEW-CAS-087, and OLD-CAS-205 ("fail-closed everywhere on the safety core") is qualified by the fresh round's fail-open cluster (NEW-CAS-010, NEW-CAS-021, NEW-CAS-029, NEW-CAS-068, NEW-CAS-069). Neither is filed as a contradiction because both are aggregate claims rather than specific fixes. |

## Recommended disposition for the new tracking issue

**Carry 120 of the 135 as open items; pre-mark 15 with the inherited verdict.**

1. **Do not re-raise the 15 bucket-A items as defects.** Record them in a collapsed
   "already adjudicated" section with the old id, the verdict and Filimonov's quoted reasoning,
   so the next round does not re-litigate them either. Three exceptions to "closed and done":
   NEW-CAS-057 should be re-opened (its dismissal was explicitly soft and the fresh evidence
   contradicts its premise); NEW-CAS-013 and NEW-CAS-042 inherit ↗ *out-of-scope*, i.e.
   deferred, and should be carried as deferred compatibility work; and the budget-versus-rate
   arithmetic inside NEW-CAS-034 should be carried as an open question even though the
   reclaim-latency complaint is closed.
2. **Lead the new issue with the 11 bucket-B contradictions.** These are the only items where
   the developer's current mental model is wrong, so they have the highest information value per
   line. Present each with the old ✅ and the quoted claim, then the fresh anchor. Rank them
   NEW-CAS-048, NEW-CAS-092, NEW-CAS-110, NEW-CAS-036, NEW-CAS-122, NEW-CAS-029, NEW-CAS-098
   first: those are the ones where the residual defect is safety- or availability-relevant
   rather than coverage-relevant.
3. **Merge the 51 bucket-C items into the existing ids rather than opening new ones**, carrying
   the new anchor and noting the direction of the evidence change. Twelve deserve an explicit
   "evidence changed" flag because they contradict a 🟡 *mitigated/partial* claim or refute a
   dismissal's premise: NEW-CAS-004 (vs OLD-CAS-015), NEW-CAS-035 and NEW-CAS-045 and
   NEW-CAS-115 (vs OLD-CAS-049/057 "mitigated"), NEW-CAS-082 (vs "GC cleans eventually"),
   NEW-CAS-085 (vs "latent"), NEW-CAS-091 (vs "safe only for object keys"), NEW-CAS-002 and
   NEW-CAS-026 (vs "presence revalidated"), NEW-CAS-093 (test-gap → defect), NEW-CAS-100
   (unrepaired → unsound verdict), NEW-CAS-129 (the requested recheck, now with a bounded
   window).
4. **File the 58 bucket-D items as new.** Note in the issue preamble that most cluster in code
   the refactor introduced — the ref ledger and catalog, the GC scheduler and sweeps, the
   request-control layer, the event dispatcher, the emulated backend and the day-2 tools — which
   is expected and is where review effort should concentrate.
5. **Re-grade the High list from 24 to 21 before publishing.** Three of the 24 new Highs are
   already-accepted design positions and must not be presented as High:
   - **NEW-CAS-008** — non-cryptographic default hash, reads never re-verify → OLD-CAS-003 +
     OLD-CAS-005, 📐/YAGNI: "S3 has many durability nines and hashes objects itself; CAS will
     not re-hash on read", and "selectable hash landed — closes weak-collision concern; will
     **not** re-verify hash on read".
   - **NEW-CAS-012** — lifecycle / Object Lock / storage-class undetected → OLD-CAS-016 +
     OLD-CAS-017, 📐: "do not enable Object Lock/WORM/retention/lifecycle/versioning on the
     bucket — plain bucket only". Re-file the residue as a *documentation* item plus the
     already-open OLD-CAS-052 (Glacier restore-and-retry).
   - **NEW-CAS-013** — pool-wide reader-floor ratchet → OLD-CAS-009, ↗ out-of-scope: "needs
     attention later; not a blocker; model may be wrong". Carry as deferred, not High.

   Two further Highs should be *partially* de-escalated rather than dropped: **NEW-CAS-009**
   (the "never re-verify an existing object" half is OLD-CAS-005's 📐; only the
   scratch/staged-body half, OLD-CAS-038, is open) and **NEW-CAS-023** (the GC-deferred-reclaim
   half is OLD-CAS-018's 📐/❌; the `gc_enabled=false` accept-and-do-nothing and the
   vanished-pool silent-success halves are genuinely open). After de-escalation the High list is
   21 items, of which 13 are re-confirmations of already-open ids and 8 are new.
6. **Keep `NOTE-1`..`NOTE-3` as confidence qualifiers**, not defects, and state plainly that
   the audited tree had the CAS test corpus deleted — which is why every TEST-GAP finding in
   this round (NEW-CAS-064, NEW-CAS-065, NEW-CAS-108, NEW-CAS-109) should be re-verified against
   the real tree before it is presented to the developer as a gap.
